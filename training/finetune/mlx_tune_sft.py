from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_manifest(model_name: str, dataset: Path, output_dir: Path, max_steps: int, avg_loss: float) -> dict:
    return {
        "run_id": output_dir.name,
        "title": f"{max_steps}-step smoke train",
        "engine": "local-simulated",
        "training_mode": "simulated",
        "simulation_note": "This run writes teaching artifacts with synthetic loss/adapter outputs instead of updating a real model checkpoint.",
        "model_name": model_name,
        "dataset_path": str(dataset.relative_to(output_dir.parents[1])),
        "dataset_role": "train",
        "adapter_dir": str((output_dir / "adapters").relative_to(output_dir.parents[1])),
        "max_steps": max_steps,
        "avg_loss": avg_loss,
        "probe_results_path": str((output_dir / "inference-probe-results.json").relative_to(output_dir.parents[1])),
        "probe_report_path": str((output_dir / "inference-probe-report.md").relative_to(output_dir.parents[1])),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-steps", type=int, default=20)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    adapters_dir = args.output_dir / "adapters"
    adapters_dir.mkdir(parents=True, exist_ok=True)

    avg_loss = round(max(1.2, 5.2 - (args.max_steps / 25)), 4)
    metrics_path = args.output_dir / "train-metrics.jsonl"
    metrics_rows = []
    for step in range(1, args.max_steps + 1):
        loss = round(avg_loss + ((args.max_steps - step) / max(args.max_steps, 1)) * 0.8, 4)
        metrics_rows.append({"step": step, "loss": loss})
    metrics_path.write_text("\n".join(json.dumps(row) for row in metrics_rows) + "\n", encoding="utf-8")
    (adapters_dir / "adapter_config.json").write_text(
        json.dumps({"model_name": args.model_name, "max_steps": args.max_steps}, indent=2),
        encoding="utf-8",
    )
    (adapters_dir / "adapters.safetensors").write_bytes(b"demo-adapter")

    manifest = build_manifest(args.model_name, args.dataset.resolve(), args.output_dir.resolve(), args.max_steps, avg_loss)
    (args.output_dir / "run-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
