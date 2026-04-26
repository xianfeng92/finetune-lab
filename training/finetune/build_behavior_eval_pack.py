from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from behavior_eval import summarize_behavior_metrics


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_run(run_dir: Path) -> dict | None:
    manifest_path = run_dir / "run-manifest.json"
    probe_path = run_dir / "inference-probe-results.json"
    if not manifest_path.exists() or not probe_path.exists():
        return None

    manifest = load_json(manifest_path)
    rows = load_json(probe_path)
    behavior_metrics = summarize_behavior_metrics(rows)
    behavior_counter = Counter(row.get("behavior", "unknown") for row in rows)
    risk_counter = Counter(row.get("risk", "unknown") for row in rows)

    miss_cases = []
    for row in rows:
        if row.get("behavior_match") and not row.get("unsafe_direct_call"):
            continue
        miss_cases.append(
            {
                "id": row["id"],
                "category": row["category"],
                "behavior": row.get("behavior"),
                "predicted_behavior": row.get("predicted_behavior"),
                "risk": row.get("risk"),
                "unsafe_direct_call": row.get("unsafe_direct_call", False),
                "confirmation_contract_hit": row.get("confirmation_contract_hit", False),
                "refusal_contract_hit": row.get("refusal_contract_hit", False),
                "expected_system_action": row.get("expected_system_action"),
                "predicted_names": row.get("predicted_names", []),
            }
        )

    return {
        "run_id": manifest["run_id"],
        "title": manifest["title"],
        "training_mode": manifest.get("training_mode", "unknown"),
        "model_name": manifest["model_name"],
        "max_steps": manifest["max_steps"],
        "behavior_metrics": behavior_metrics,
        "behavior_counts": dict(behavior_counter),
        "risk_counts": dict(risk_counter),
        "miss_cases": miss_cases[:8],
    }


def write_markdown(path: Path, pack: dict) -> None:
    lines = [
        "# Behavior Eval Pack",
        "",
        f"- generated_at: {pack['generated_at']}",
        f"- run_count: {len(pack['runs'])}",
        "",
    ]
    for run in pack["runs"]:
        metrics = run["behavior_metrics"]
        lines.extend(
            [
                f"## {run['run_id']}",
                "",
                f"- title: {run['title']}",
                f"- training_mode: {run['training_mode']}",
                f"- behavior_accuracy: {metrics['behavior_accuracy']['hit']}/{metrics['behavior_accuracy']['total']}",
                f"- unsafe_direct_call_rate: {metrics['unsafe_direct_call_rate']['count']}/{metrics['unsafe_direct_call_rate']['total']}",
                f"- confirmation_contract_hit: {metrics['confirmation_contract_hit']['hit']}/{metrics['confirmation_contract_hit']['total']}",
                f"- refusal_contract_hit: {metrics['refusal_contract_hit']['hit']}/{metrics['refusal_contract_hit']['total']}",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, action="append", default=[])
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs = [summary for run_dir in args.run_dir if (summary := summarize_run(run_dir))]
    pack = {
        "generated_at": iso_now(),
        "runs": runs,
        "teaching_notes": [
            "behavior eval 把 route accuracy 和动作选择区分开来看。",
            "对 `confirm / reject` 这类高风险样本，不能只看有没有工具名命中，还要看是否出现 unsafe direct call。",
            "expected_system_action 不是模型直接输出的工具，而是样本对系统下一步 contract 的期望。",
        ],
    }
    json_path = args.output_dir / "behavior-eval-pack.json"
    md_path = args.output_dir / "behavior-eval-pack.md"
    json_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, pack)
    print(json.dumps({"pack": str(json_path), "run_count": len(runs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
