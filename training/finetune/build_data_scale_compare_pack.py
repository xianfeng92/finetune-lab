from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_ready(run_dir: Path) -> bool:
    return (run_dir / "run-manifest.json").exists() and (run_dir / "inference-probe-results.json").exists()


def infer_data_scale(run_dir: Path) -> str:
    text = str(run_dir)
    if "large" in text:
        return "large"
    if "medium" in text:
        return "medium"
    return "small"


def infer_dataset_variant(run_dir: Path) -> tuple[str, str]:
    text = str(run_dir)
    if "public-augmented" in text:
        return "public_augmented", "Public-augmented"
    return "core", "Core"


def infer_strategy(run_dir: Path) -> tuple[str, str]:
    text = str(run_dir)
    if "stage-curriculum-consolidation" in text:
        return "curriculum_consolidation", "Curriculum + consolidation"
    return "direct_mixed", "Direct mixed"


def summarize_results(rows: list[dict]) -> dict:
    total = max(len(rows), 1)
    exact = sum(1 for row in rows if row.get("exact_name_match"))
    structured = sum(1 for row in rows if row.get("structured_output_valid"))
    args = sum(1 for row in rows if row.get("arguments_match"))
    behavior = sum(1 for row in rows if row.get("behavior_match"))
    unsafe = sum(1 for row in rows if row.get("unsafe_direct_call"))
    confirm_total = sum(1 for row in rows if row.get("behavior") == "confirm")
    confirm_hit = sum(1 for row in rows if row.get("confirmation_contract_hit"))
    reject_total = sum(1 for row in rows if row.get("behavior") == "reject")
    reject_hit = sum(1 for row in rows if row.get("refusal_contract_hit"))
    return {
        "total_cases": len(rows),
        "exact_name_match": {"hit": exact, "total": len(rows), "rate": round(exact / total, 3)},
        "structured_output_valid": {"hit": structured, "total": len(rows), "rate": round(structured / total, 3)},
        "arguments_match": {"hit": args, "total": len(rows), "rate": round(args / total, 3)},
        "behavior_accuracy": {"hit": behavior, "total": len(rows), "rate": round(behavior / total, 3)},
        "unsafe_direct_call_rate": {"count": unsafe, "total": len(rows), "rate": round(unsafe / total, 3)},
        "confirmation_contract_hit": {
            "hit": confirm_hit,
            "total": confirm_total,
            "rate": round(confirm_hit / max(confirm_total, 1), 3),
        },
        "refusal_contract_hit": {
            "hit": reject_hit,
            "total": reject_total,
            "rate": round(reject_hit / max(reject_total, 1), 3),
        },
    }


def dataset_snapshot(pack: dict) -> dict:
    counts = pack.get("counts", {})
    behaviors = pack.get("behaviors", {})
    risks = pack.get("risks", {})
    actions = pack.get("expected_system_actions", {})
    return {
        "counts": counts,
        "train_behaviors": behaviors.get("train", {}),
        "test_behaviors": behaviors.get("test", {}),
        "train_risks": risks.get("train", {}),
        "test_risks": risks.get("test", {}),
        "train_expected_system_actions": actions.get("train", {}),
        "test_expected_system_actions": actions.get("test", {}),
    }


def load_scenario(run_dir: Path, dataset_pack: dict) -> dict:
    manifest = load_json(run_dir / "run-manifest.json")
    rows = load_json(run_dir / "inference-probe-results.json")
    strategy_id, strategy_label = infer_strategy(run_dir)
    scale = infer_data_scale(run_dir)
    dataset_variant, dataset_variant_label = infer_dataset_variant(run_dir)
    if scale == "medium" and dataset_variant != "core":
        scenario_id = f"{scale}-{dataset_variant}-{strategy_id}"
        label = f"{scale.capitalize()} · {dataset_variant_label} · {strategy_label}"
    else:
        scenario_id = f"{scale}-{strategy_id}"
        label = f"{scale.capitalize()} · {strategy_label}"
    return {
        "scenario_id": scenario_id,
        "label": label,
        "data_scale": scale,
        "dataset_variant": dataset_variant,
        "dataset_variant_label": dataset_variant_label,
        "strategy": strategy_id,
        "strategy_label": strategy_label,
        "run_dir": str(run_dir.resolve().relative_to(ROOT)),
        "run_id": manifest["run_id"],
        "title": manifest["title"],
        "max_steps": manifest["max_steps"],
        "avg_loss": manifest["avg_loss"],
        "dataset": dataset_snapshot(dataset_pack),
        "metrics": summarize_results(rows),
    }


def build_matrix(scenarios: list[dict]) -> list[dict]:
    metric_specs = [
        ("exact_name_match", "Exact name match"),
        ("structured_output_valid", "Structured output valid"),
        ("arguments_match", "Arguments match"),
        ("behavior_accuracy", "Behavior accuracy"),
        ("unsafe_direct_call_rate", "Unsafe direct call"),
        ("confirmation_contract_hit", "Confirm contract"),
        ("refusal_contract_hit", "Reject contract"),
    ]
    rows = []
    for metric_id, label in metric_specs:
        row = {"metric": metric_id, "label": label, "scenarios": []}
        for scenario in scenarios:
            metric = scenario["metrics"][metric_id]
            value = metric.get("count", metric.get("hit"))
            row["scenarios"].append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "label": scenario["label"],
                    "value": value,
                    "total": metric["total"],
                    "rate": metric["rate"],
                }
            )
        rows.append(row)
    return rows


def write_markdown(path: Path, pack: dict) -> None:
    lines = [
        "# Data Scale Compare Pack",
        "",
        f"- generated_at: {pack['generated_at']}",
        "",
    ]
    for scenario in pack["scenarios"]:
        metrics = scenario["metrics"]
        counts = scenario["dataset"]["counts"]
        lines.extend(
            [
                f"## {scenario['label']}",
                "",
                f"- train/valid/test: {counts['train']}/{counts['valid']}/{counts['test']}",
                f"- dataset_variant: {scenario['dataset_variant_label']}",
                f"- avg_loss: {scenario['avg_loss']}",
                f"- exact_name_match: {metrics['exact_name_match']['hit']}/{metrics['exact_name_match']['total']}",
                f"- structured_output_valid: {metrics['structured_output_valid']['hit']}/{metrics['structured_output_valid']['total']}",
                f"- arguments_match: {metrics['arguments_match']['hit']}/{metrics['arguments_match']['total']}",
                f"- behavior_accuracy: {metrics['behavior_accuracy']['hit']}/{metrics['behavior_accuracy']['total']}",
                f"- unsafe_direct_call_rate: {metrics['unsafe_direct_call_rate']['count']}/{metrics['unsafe_direct_call_rate']['total']}",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--small-pack", type=Path, required=True)
    parser.add_argument("--medium-pack", type=Path, required=True)
    parser.add_argument("--medium-public-augmented-pack", type=Path)
    parser.add_argument("--large-pack", type=Path)
    parser.add_argument("--run-dir", type=Path, action="append", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    small_pack = load_json(args.small_pack)
    medium_pack = load_json(args.medium_pack)
    medium_public_augmented_pack = load_json(args.medium_public_augmented_pack) if args.medium_public_augmented_pack else medium_pack
    large_pack = load_json(args.large_pack) if args.large_pack else None
    scenarios = []
    for run_dir in args.run_dir:
        if not scenario_ready(run_dir):
            continue
        scale = infer_data_scale(run_dir)
        if scale == "large":
            dataset_pack = large_pack or medium_pack
        elif scale == "medium":
            dataset_variant, _ = infer_dataset_variant(run_dir)
            dataset_pack = medium_public_augmented_pack if dataset_variant == "public_augmented" else medium_pack
        else:
            dataset_pack = small_pack
        scenarios.append(load_scenario(run_dir, dataset_pack))
    scenarios.sort(key=lambda item: (item["data_scale"], item["dataset_variant"], item["strategy"]))

    pack = {
        "generated_at": iso_now(),
        "scenarios": scenarios,
        "matrix": build_matrix(scenarios),
        "teaching_notes": [
            "公平比较数据量时，要先确保 small / medium / large 走的是同一份 schema，而不是一边带 confirm/reject、一边还是老版 tool-call-only。",
            "direct mixed 用来回答'更多数据直接硬训会怎样'，curriculum + consolidation 用来回答'更多数据配合阶段化教学能不能更稳'。",
            "public-augmented 场景回答的是'把公开来源样本直接并进主训练集，会不会立刻带来 mixed-task 提升'。如果 held-out 不变而指标没有提升，说明外部样本还没有和当前任务契合到足以形成直接收益。",
            "如果数据量变大后 exact/args 提升，但 structured/behavior 没跟上，说明问题不只是样本量，而是 task mixture、行为标签和课程设计。",
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "data-scale-compare-pack.json"
    md_path = args.output_dir / "data-scale-compare-pack.md"
    json_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, pack)
    print(json.dumps({"pack": str(json_path), "scenario_count": len(scenarios)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
