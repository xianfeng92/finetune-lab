from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.finetune.live_status import (
    build_initial_live_status,
    live_status_slug,
    now_iso,
    sample_process_metrics,
    sample_system_metrics,
    tail_points,
    write_live_index,
    write_live_status,
)


MLX_COMPAT_DIR = ROOT / "training" / "finetune" / "mlx_compat"
MLX_LORA_ENTRYPOINT = ROOT / "training" / "finetune" / "mlx_lora_entry.py"

TRAIN_RE = re.compile(
    r"Iter (?P<iteration>\d+): Train loss (?P<train_loss>[0-9.]+), "
    r"Learning Rate (?P<learning_rate>[0-9.eE+-]+), "
    r"It/sec (?P<iterations_per_second>[0-9.]+), "
    r"Tokens/sec (?P<tokens_per_second>[0-9.]+), "
    r"Trained Tokens (?P<trained_tokens>\d+), "
    r"Peak mem (?P<peak_memory>[0-9.]+) GB"
)
VAL_RE = re.compile(
    r"Iter (?P<iteration>\d+): Val loss (?P<val_loss>[0-9.]+), Val took (?P<val_time>[0-9.]+)s"
)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ensure_dataset(data_dir: Path) -> None:
    required = [data_dir / f"{name}.jsonl" for name in ("train", "valid", "test")]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing real fine-tune dataset files: {missing}")


def resolve_iters(data_dir: Path, batch_size: int, requested_iters: int | None, requested_epochs: float | None) -> tuple[int, int, float]:
    train_row_count = len(load_jsonl(data_dir / "train.jsonl"))
    if train_row_count <= 0:
        raise SystemExit("real fine-tune dataset has no train rows")
    if requested_iters is not None and requested_epochs is not None:
        raise SystemExit("Specify either --iters or --epochs, not both.")

    if requested_epochs is not None:
        iters = max(1, math.ceil(train_row_count * requested_epochs / batch_size))
    else:
        iters = requested_iters if requested_iters is not None else 12
    effective_epochs = round((iters * batch_size) / train_row_count, 3)
    return iters, train_row_count, effective_epochs


def parse_metric_line(line: str) -> tuple[str, dict] | None:
    if match := TRAIN_RE.search(line):
        payload = {
            "step": int(match.group("iteration")),
            "loss": float(match.group("train_loss")),
            "learning_rate": float(match.group("learning_rate")),
            "iterations_per_second": float(match.group("iterations_per_second")),
            "tokens_per_second": float(match.group("tokens_per_second")),
            "trained_tokens": int(match.group("trained_tokens")),
            "peak_memory_gb": float(match.group("peak_memory")),
        }
        return ("train", payload)
    if match := VAL_RE.search(line):
        payload = {
            "step": int(match.group("iteration")),
            "val_loss": float(match.group("val_loss")),
            "val_time_s": float(match.group("val_time")),
        }
        return ("eval", payload)
    return None


def parse_metrics_from_log(log_path: Path) -> tuple[list[dict], list[dict]]:
    train_metrics: list[dict] = []
    eval_metrics: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        parsed = parse_metric_line(line.strip())
        if parsed is None:
            continue
        kind, payload = parsed
        if kind == "train":
            train_metrics.append(payload)
        else:
            eval_metrics.append(payload)
    return train_metrics, eval_metrics


def build_progress(train_metrics: list[dict], eval_metrics: list[dict], effective_epochs: float, train_row_count: int, batch_size: int) -> dict:
    last_train = train_metrics[-1] if train_metrics else None
    last_eval = eval_metrics[-1] if eval_metrics else None
    current_step = last_train["step"] if last_train else (last_eval["step"] if last_eval else 0)
    current_epoch = round((current_step * batch_size) / train_row_count, 3) if train_row_count else 0
    return {
        "current_step": current_step,
        "current_epoch": current_epoch,
        "target_epochs": effective_epochs,
        "last_train_loss": last_train["loss"] if last_train else None,
        "last_val_loss": last_eval["val_loss"] if last_eval else None,
        "last_learning_rate": last_train["learning_rate"] if last_train else None,
        "last_trained_tokens": last_train["trained_tokens"] if last_train else None,
        "last_peak_memory_gb": last_train["peak_memory_gb"] if last_train else None,
    }


def build_manifest(args: argparse.Namespace, train_metrics: list[dict], eval_metrics: list[dict]) -> dict:
    avg_loss = round(sum(row["loss"] for row in train_metrics) / len(train_metrics), 4) if train_metrics else None
    return {
        "run_id": args.output_dir.name,
        "title": f"{args.iters}-iter real MLX LoRA run",
        "engine": "mlx-lm.lora",
        "training_mode": "real-mlx-lora",
        "model_name": args.model_name,
        "dataset_path": rel(args.data_dir / "train.jsonl"),
        "dataset_role": "train",
        "train_row_count": args.train_row_count,
        "effective_epochs": args.effective_epochs,
        "adapter_dir": rel(args.output_dir / "adapters"),
        "max_steps": args.iters,
        "avg_loss": avg_loss,
        "probe_results_path": rel(args.output_dir / "inference-probe-results.json"),
        "probe_report_path": rel(args.output_dir / "inference-probe-report.md"),
        "train_metrics_path": rel(args.output_dir / "train-metrics.jsonl"),
        "eval_metrics_path": rel(args.output_dir / "eval-metrics.jsonl"),
        "log_path": rel(args.output_dir / "mlx-lora.log"),
        "config_path": rel(args.output_dir / "run-plan.json"),
        "live_status_path": rel(args.output_dir / "run-live-status.json"),
        "public_live_status_path": f"run-live/{live_status_slug(args.output_dir)}",
        "workflow_note": "This run uses Apple MLX LoRA with real optimizer updates and model weights instead of synthetic smoke-train artifacts.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mlx-lora-cmd", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resume-adapter-file", type=Path)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--iters", type=int)
    parser.add_argument("--epochs", type=float)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--steps-per-report", type=int, default=1)
    parser.add_argument("--steps-per-eval", type=int, default=4)
    parser.add_argument("--save-every", type=int, default=6)
    parser.add_argument("--val-batches", type=int, default=-1)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--num-layers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    if args.model_name.startswith("google/gemma-4"):
        raise SystemExit(
            "real MLX LoRA requires an MLX-converted checkpoint. "
            "Use `mlx-community/gemma-4-e2b-it-4bit` instead of raw google/* weights."
        )

    ensure_dataset(args.data_dir)
    args.iters, args.train_row_count, args.effective_epochs = resolve_iters(
        args.data_dir,
        args.batch_size,
        args.iters,
        args.epochs,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    adapters_dir = args.output_dir / "adapters"
    adapters_dir.mkdir(parents=True, exist_ok=True)
    mlx_python = args.mlx_lora_cmd.resolve().parent / "python"

    command = [
        str(mlx_python),
        str(MLX_LORA_ENTRYPOINT),
        "--model",
        args.model_name,
        "--train",
        "--data",
        str(args.data_dir),
        "--fine-tune-type",
        "lora",
        "--optimizer",
        "adamw",
        "--mask-prompt",
        "--batch-size",
        str(args.batch_size),
        "--iters",
        str(args.iters),
        "--learning-rate",
        str(args.learning_rate),
        "--steps-per-report",
        str(args.steps_per_report),
        "--steps-per-eval",
        str(args.steps_per_eval),
        "--save-every",
        str(args.save_every),
        "--val-batches",
        str(args.val_batches),
        "--max-seq-length",
        str(args.max_seq_length),
        "--num-layers",
        str(args.num_layers),
        "--adapter-path",
        str(adapters_dir),
        "--seed",
        str(args.seed),
        "--test",
    ]
    if args.resume_adapter_file:
        command.extend(["--resume-adapter-file", str(args.resume_adapter_file)])

    run_plan = {
        "command": command,
        "model_name": args.model_name,
        "data_dir": rel(args.data_dir),
        "output_dir": rel(args.output_dir),
        "mlx_python": str(mlx_python),
        "mlx_lora_entrypoint": rel(MLX_LORA_ENTRYPOINT),
        "mlx_compat_dir": rel(MLX_COMPAT_DIR),
        "compat_patch": "gemma4-e2b-disable-kv-sharing-only",
        "resume_adapter_file": rel(args.resume_adapter_file) if args.resume_adapter_file else None,
        "iters": args.iters,
        "requested_epochs": args.epochs,
        "train_row_count": args.train_row_count,
        "effective_epochs": args.effective_epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "num_layers": args.num_layers,
        "max_seq_length": args.max_seq_length,
    }
    (args.output_dir / "run-plan.json").write_text(json.dumps(run_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    log_path = args.output_dir / "mlx-lora.log"
    train_metrics: list[dict] = []
    eval_metrics: list[dict] = []
    live_status = build_initial_live_status(
        run_id=args.output_dir.name,
        title=f"{args.iters}-iter real MLX LoRA run",
        model_name=args.model_name,
        dataset_path=rel(args.data_dir / "train.jsonl"),
        output_dir=args.output_dir,
        total_steps=args.iters,
        effective_epochs=args.effective_epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        run_plan_path=args.output_dir / "run-plan.json",
    )
    state_lock = threading.Lock()
    stop_event = threading.Event()

    def flush_live_status() -> None:
        with state_lock:
            payload = json.loads(json.dumps(live_status))
        write_live_status(args.output_dir, payload)
        write_live_index(args.output_dir, payload)

    def refresh_resources(pid: int) -> None:
        process_metrics = sample_process_metrics(pid)
        system_metrics = sample_system_metrics()
        sample = {
            "sampled_at": now_iso(),
            **process_metrics,
            **system_metrics,
        }
        with state_lock:
            live_status["updated_at"] = sample["sampled_at"]
            live_status["resources"].update(process_metrics)
            live_status["resources"].update(system_metrics)
            live_status["recent_resource_samples"] = tail_points(
                live_status["recent_resource_samples"] + [sample],
                keep=30,
            )
        flush_live_status()

    def sampler(pid: int) -> None:
        while not stop_event.is_set():
            refresh_resources(pid)
            if stop_event.wait(2.0):
                break

    flush_live_status()
    returncode = 1
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        with state_lock:
            live_status["status"] = "running"
            live_status["updated_at"] = now_iso()
        flush_live_status()
        sampler_thread = threading.Thread(target=sampler, args=(process.pid,), daemon=True)
        sampler_thread.start()
        assert process.stdout is not None
        for raw_line in process.stdout:
            log_file.write(raw_line)
            log_file.flush()
            parsed = parse_metric_line(raw_line.strip())
            if parsed is None:
                continue
            kind, payload = parsed
            if kind == "train":
                train_metrics.append(payload)
            else:
                eval_metrics.append(payload)
            with state_lock:
                live_status["progress"] = build_progress(
                    train_metrics,
                    eval_metrics,
                    args.effective_epochs,
                    args.train_row_count,
                    args.batch_size,
                )
                if kind == "train":
                    live_status["recent_train_points"] = tail_points(
                        live_status["recent_train_points"] + [payload],
                        keep=60,
                    )
                else:
                    live_status["recent_eval_points"] = tail_points(
                        live_status["recent_eval_points"] + [payload],
                        keep=30,
                    )
                live_status["updated_at"] = now_iso()
            flush_live_status()
        returncode = process.wait()
        stop_event.set()
        sampler_thread.join(timeout=5)
        refresh_resources(process.pid)

    if returncode != 0:
        with state_lock:
            live_status["status"] = "failed"
            live_status["completed_at"] = now_iso()
            live_status["updated_at"] = live_status["completed_at"]
        flush_live_status()
        raise SystemExit(returncode)

    (args.output_dir / "train-metrics.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in train_metrics) + ("\n" if train_metrics else ""),
        encoding="utf-8",
    )
    (args.output_dir / "eval-metrics.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in eval_metrics) + ("\n" if eval_metrics else ""),
        encoding="utf-8",
    )

    manifest = build_manifest(args, train_metrics, eval_metrics)
    (args.output_dir / "run-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with state_lock:
        live_status["status"] = "completed"
        live_status["completed_at"] = now_iso()
        live_status["updated_at"] = live_status["completed_at"]
        live_status["progress"] = build_progress(
            train_metrics,
            eval_metrics,
            args.effective_epochs,
            args.train_row_count,
            args.batch_size,
        )
        live_status["manifest_path"] = rel(args.output_dir / "run-manifest.json")
    flush_live_status()
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
