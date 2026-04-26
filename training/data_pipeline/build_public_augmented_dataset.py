from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from pipeline import _write_governance_artifacts, build_summary_payload, write_summary
from validator import validate_samples


CANONICAL_SAMPLE_KEYS = {
    "id",
    "category",
    "behavior",
    "risk",
    "vehicle_state",
    "domains_loaded",
    "loaded_tool_names",
    "system_prompt",
    "messages",
    "meta",
    "sft_text",
    "template_id",
    "split_group",
    "eval_split",
    "split_strategy",
    "expected_system_action",
    "event",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def sanitize_sample(sample: dict) -> dict:
    sanitized = {key: sample[key] for key in CANONICAL_SAMPLE_KEYS if key in sample}
    sanitized.setdefault("meta", {})
    sanitized.setdefault("eval_split", "public_external")
    sanitized.setdefault("split_strategy", "external")
    sanitized["meta"] = {
        "prompt_token_count": sanitized["meta"].get("prompt_token_count", 0),
        "generator_model": sanitized["meta"].get("generator_model", "unknown"),
        "adversarial": sanitized["meta"].get("adversarial", False),
        "seed_anchor_id": sanitized["meta"].get("seed_anchor_id"),
    }
    return sanitized


def build_augmentation_summary(car_bench_rows: list[dict], clarifyvc_rows: list[dict]) -> dict:
    all_rows = car_bench_rows + clarifyvc_rows
    return {
        "public_sample_count": len(all_rows),
        "public_source_counts": {
            "car_bench": len(car_bench_rows),
            "clarifyvc": len(clarifyvc_rows),
        },
        "public_behavior_counts": dict(sorted(Counter(row["behavior"] for row in all_rows).items())),
        "public_domain_counts": dict(
            sorted(Counter(domain for row in all_rows for domain in row.get("domains_loaded", [])).items())
        ),
        "public_category_counts": dict(sorted(Counter(row["category"] for row in all_rows).items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a medium public-augmented dataset from internal + public sources.")
    parser.add_argument("--base-train", type=Path, required=True)
    parser.add_argument("--base-held-out", type=Path, required=True)
    parser.add_argument("--car-bench", type=Path, required=True)
    parser.add_argument("--clarifyvc", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-summary", type=Path, help="Optional base dataset_summary.json to inherit multiplier metadata.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    base_train = [sanitize_sample(sample) for sample in load_jsonl(args.base_train)]
    held_out = [sanitize_sample(sample) for sample in load_jsonl(args.base_held_out)]
    car_bench_rows = [sanitize_sample(sample) for sample in load_jsonl(args.car_bench)]
    clarifyvc_rows = [sanitize_sample(sample) for sample in load_jsonl(args.clarifyvc)]
    public_rows = car_bench_rows + clarifyvc_rows

    train_rows = base_train + public_rows
    samples = train_rows + held_out

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "samples.jsonl", samples)
    write_jsonl(args.output_dir / "train.jsonl", train_rows)
    write_jsonl(args.output_dir / "held-out.jsonl", held_out)

    errors = validate_samples(samples)
    base_multiplier = 1
    if args.base_summary and args.base_summary.exists():
        base_summary = json.loads(args.base_summary.read_text(encoding="utf-8"))
        base_multiplier = int(base_summary.get("multiplier", 1))
    held_out_ratio = round(len(held_out) / max(len(samples), 1), 3)
    summary = build_summary_payload(
        samples,
        train_rows,
        held_out,
        args.output_dir,
        base_multiplier,
        held_out_ratio,
        "public_augmented_train_only",
        errors,
    )
    summary["augmentation"] = build_augmentation_summary(car_bench_rows, clarifyvc_rows)
    write_summary(args.output_dir / "dataset_summary", summary)
    (args.output_dir / "validation_report.md").write_text(
        (args.output_dir / "dataset_summary.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _write_governance_artifacts(args.output_dir, samples, train_rows, held_out)

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "train_count": len(train_rows),
                "held_out_count": len(held_out),
                "public_sample_count": len(public_rows),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
