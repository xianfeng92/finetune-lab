from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_tool_routing_pack(samples: list[dict]) -> dict:
    routed_samples = [sample for sample in samples if sample.get("behavior", "tool_call") == "tool_call"]
    route_counter: Counter[str] = Counter()
    domain_counter: Counter[str] = Counter()
    candidate_histogram: Counter[int] = Counter()
    route_candidate_counts: defaultdict[str, list[int]] = defaultdict(list)
    focus_samples = []

    for sample in routed_samples:
        expected_calls = sample["messages"][-1].get("tool_calls", [])
        expected_name = expected_calls[0]["name"] if expected_calls else "none"
        candidate_count = len(sample["loaded_tool_names"])
        route_counter[expected_name] += 1
        candidate_histogram[candidate_count] += 1
        route_candidate_counts[expected_name].append(candidate_count)
        for domain in sample.get("domains_loaded", []):
            domain_counter[domain] += 1

        if candidate_count > 1 and len(focus_samples) < 6:
            focus_samples.append(
                {
                    "id": sample["id"],
                    "category": sample["category"],
                    "prompt_user": next((msg["content"] for msg in sample["messages"] if msg["role"] == "user"), None),
                    "loaded_tool_names": sample["loaded_tool_names"],
                    "expected_name": expected_name,
                    "expected_arguments": expected_calls[0].get("arguments", {}) if expected_calls else {},
                    "route_type": "multi-choice" if candidate_count > 1 else "single-choice",
                }
            )

    if not focus_samples:
        for sample in samples[:3]:
            expected_calls = sample["messages"][-1].get("tool_calls", [])
            expected_name = expected_calls[0]["name"] if expected_calls else "none"
            focus_samples.append(
                {
                    "id": sample["id"],
                    "category": sample["category"],
                    "prompt_user": next((msg["content"] for msg in sample["messages"] if msg["role"] == "user"), None),
                    "loaded_tool_names": sample["loaded_tool_names"],
                    "expected_name": expected_name,
                    "expected_arguments": expected_calls[0].get("arguments", {}) if expected_calls else {},
                    "route_type": "single-choice",
                }
            )

    routes = []
    for tool_name, count in route_counter.most_common():
        candidate_counts = route_candidate_counts[tool_name]
        routes.append(
            {
                "tool_name": tool_name,
                "count": count,
                "avg_candidate_count": round(sum(candidate_counts) / len(candidate_counts), 2),
            }
        )

    return {
        "generated_at": iso_now(),
        "summary": {
            "total_samples": len(routed_samples),
            "ignored_non_tool_call_samples": len(samples) - len(routed_samples),
            "single_tool_samples": sum(1 for sample in routed_samples if len(sample["loaded_tool_names"]) == 1),
            "multi_tool_samples": sum(1 for sample in routed_samples if len(sample["loaded_tool_names"]) > 1),
            "distinct_tools": len(route_counter),
            "avg_candidate_count": round(
                sum(len(sample["loaded_tool_names"]) for sample in routed_samples) / max(len(routed_samples), 1),
                2,
            ),
            "candidate_histogram": [
                {"candidate_count": count, "samples": total}
                for count, total in sorted(candidate_histogram.items())
            ],
            "domain_counts": [
                {"domain": domain, "count": count}
                for domain, count in domain_counter.most_common()
            ],
            "route_counts": routes,
        },
        "focus_samples": focus_samples,
        "teaching_notes": [
            "tool routing 不是生成一段自然语言，而是在 loaded_tool_names 候选集合里挑对名字。",
            "multi-choice case 比 single-choice case 更能体现微调是否真的学会 route selection。",
            "如果只评估文本流畅度，会漏掉最关键的 tool choice accuracy。",
            "confirm / reject / clarify 这类非直接工具调用样本会从 Level 5 route pack 里排除，避免把行为决策和 route accuracy 混在一起。",
        ],
    }


def summarize_probe_rows(rows: list[dict]) -> dict:
    return {
        "total_cases": len(rows),
        "exact_name_match": sum(1 for row in rows if row["exact_name_match"]),
        "json_valid": sum(1 for row in rows if row.get("json_valid")),
        "structured_output_valid": sum(1 for row in rows if row.get("structured_output_valid")),
        "arguments_match": sum(1 for row in rows if row.get("arguments_match")),
        "tool_signal": sum(1 for row in rows if row["has_tool_calls_signal"]),
        "tool_name_only": sum(1 for row in rows if row.get("output_shape") == "tool_name_only"),
        "tool_calls_array": sum(1 for row in rows if row.get("output_shape") == "tool_calls_array"),
        "schema_echo": sum(1 for row in rows if row["looks_like_schema_echo"]),
    }


def build_structured_output_pack(run_dirs: list[Path]) -> dict:
    runs = []
    compare_cases: dict[str, dict] = {}

    for run_dir in run_dirs:
        manifest_path = run_dir / "run-manifest.json"
        probe_path = run_dir / "inference-probe-results.json"
        if not manifest_path.exists() or not probe_path.exists():
            continue
        manifest = load_json(manifest_path)
        rows = load_json(probe_path)
        summary = summarize_probe_rows(rows)
        run_payload = {
            "run_id": manifest["run_id"],
            "title": manifest["title"],
            "max_steps": manifest["max_steps"],
            "model_name": manifest["model_name"],
            "summary": summary,
            "cases": [],
        }
        for row in rows[:5]:
            case = {
                "id": row["id"],
                "prompt_user": row["prompt_user"],
                "loaded_tool_names": row["loaded_tool_names"],
                "expected_names": row["expected_names"],
                "predicted_names": row["predicted_names"],
                "output_shape": row.get("output_shape", "unknown"),
                "structured_output_valid": row.get("structured_output_valid", False),
                "arguments_match": row.get("arguments_match", False),
                "exact_name_match": row["exact_name_match"],
                "raw_output": row["raw_output"],
            }
            run_payload["cases"].append(case)
            compare_cases.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "prompt_user": row["prompt_user"],
                    "expected_names": row["expected_names"],
                    "loaded_tool_names": row["loaded_tool_names"],
                    "runs": [],
                },
            )["runs"].append(
                {
                    "run_id": manifest["run_id"],
                    "title": manifest["title"],
                    "max_steps": manifest["max_steps"],
                    "predicted_names": row["predicted_names"],
                    "output_shape": row.get("output_shape", "unknown"),
                    "structured_output_valid": row.get("structured_output_valid", False),
                    "arguments_match": row.get("arguments_match", False),
                    "exact_name_match": row["exact_name_match"],
                }
            )
        runs.append(run_payload)

    compare_list = list(compare_cases.values())
    compare_list.sort(key=lambda item: item["id"])

    notes = []
    if runs:
        weakest = runs[0]
        strongest = runs[-1]
        notes.append(
            f"{weakest['title']} 主要验证 tool routing 是否出现信号；{strongest['title']} 更适合看 structured output 是否已经稳定成 tool_calls 数组。"
        )
        if weakest["summary"]["tool_name_only"] and strongest["summary"]["tool_calls_array"]:
            notes.append("这是一个典型的 Level 5 教学差异：早期 run 可能只输出 tool_name，后期 run 才稳定学会结构化 tool_calls。")
        if strongest["summary"]["arguments_match"] >= weakest["summary"]["arguments_match"]:
            notes.append("arguments_match 能帮助区分“挑对工具名”与“连参数结构也一起学会”这两层能力。")

    return {
        "generated_at": iso_now(),
        "runs": runs,
        "compare_cases": compare_list,
        "teaching_notes": notes,
    }


def write_markdown(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, action="append", default=[])
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    samples = load_jsonl(args.dataset)
    tool_pack = build_tool_routing_pack(samples)
    tool_json_path = args.output_dir / "tool-routing-dataset-pack.json"
    tool_md_path = args.output_dir / "tool-routing-dataset-pack.md"
    tool_json_path.write_text(json.dumps(tool_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(
        tool_md_path,
        [
            "# Tool Routing Dataset Pack",
            "",
            f"- total_samples: {tool_pack['summary']['total_samples']}",
            f"- multi_tool_samples: {tool_pack['summary']['multi_tool_samples']}",
            f"- avg_candidate_count: {tool_pack['summary']['avg_candidate_count']}",
            "",
            "## Teaching Notes",
            "",
            *[f"- {note}" for note in tool_pack["teaching_notes"]],
        ],
    )

    structured_pack = build_structured_output_pack(args.run_dir)
    structured_json_path = args.output_dir / "structured-output-probe-pack.json"
    structured_md_path = args.output_dir / "structured-output-probe-pack.md"
    structured_json_path.write_text(json.dumps(structured_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = ["# Structured Output Probe Pack", ""]
    for run in structured_pack["runs"]:
        md_lines.extend(
            [
                f"## {run['title']}",
                "",
                f"- exact_name_match: {run['summary']['exact_name_match']}/{run['summary']['total_cases']}",
                f"- structured_output_valid: {run['summary']['structured_output_valid']}/{run['summary']['total_cases']}",
                f"- arguments_match: {run['summary']['arguments_match']}/{run['summary']['total_cases']}",
                "",
            ]
        )
    if structured_pack["teaching_notes"]:
        md_lines.extend(["## Teaching Notes", ""])
        md_lines.extend(f"- {note}" for note in structured_pack["teaching_notes"])
    write_markdown(structured_md_path, md_lines)

    print(
        json.dumps(
            {
                "tool_pack": str(tool_json_path),
                "structured_pack": str(structured_json_path),
                "run_count": len(structured_pack["runs"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
