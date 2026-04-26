from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.run(
            command,
            cwd=ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if process.returncode != 0:
        raise SystemExit(process.returncode)

    train_metrics, eval_metrics = parse_metrics_from_log(log_path)

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
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
