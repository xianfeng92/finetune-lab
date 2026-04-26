from __future__ import annotations

import argparse
import json
from pathlib import Path

from behavior_eval import (
    classify_predicted_behavior,
    confirmation_contract_hit,
    refusal_contract_hit,
    structured_output_valid,
    summarize_behavior_metrics,
    unsafe_direct_call,
)


def load_samples(dataset_path: Path) -> list[dict]:
    return [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def classify_output_shape(parsed_output: dict | None) -> str:
    if parsed_output is None:
        return "empty"
    if isinstance(parsed_output.get("tool_calls"), list):
        return "tool_calls_array"
    if isinstance(parsed_output.get("tool_name"), str):
        return "tool_name_only"
    return "other_json"


def structured_tool_calls(parsed_output: dict | None) -> list[dict]:
    if not parsed_output:
        return []
    tool_calls = parsed_output.get("tool_calls")
    return tool_calls if isinstance(tool_calls, list) else []


def arguments_match(expected_calls: list[dict], predicted_calls: list[dict]) -> bool:
    if len(expected_calls) != len(predicted_calls):
        return False
    for expected, predicted in zip(expected_calls, predicted_calls):
        if expected.get("name") != predicted.get("name"):
            return False
        if expected.get("arguments") != predicted.get("arguments"):
            return False
    return True


def result_for_sample(sample: dict, strength: str) -> dict:
    expected_calls = sample["messages"][-1].get("tool_calls", [])
    expected_names = [call["name"] for call in expected_calls]
    expected_behavior = sample.get("behavior", "tool_call")
    expected_system_action = sample.get("expected_system_action")
    expected_assistant_content = sample["messages"][-1].get("content") or ""
    if expected_behavior in {"confirm", "reject"}:
        predicted_names = []
        predicted_tool_calls = []
        parsed_output = None
        raw_output = expected_assistant_content
        exact = True
        signal = False
    elif strength == "strong":
        predicted_names = list(expected_names)
        parsed_output = {"tool_calls": expected_calls}
        raw_output = json.dumps(parsed_output, ensure_ascii=False)
        exact = True
        signal = True
    else:
        predicted_names = expected_names[:1]
        parsed_output = {"tool_name": predicted_names[0]} if predicted_names else None
        raw_output = json.dumps(parsed_output, ensure_ascii=False) if parsed_output else ""
        exact = predicted_names == expected_names
        signal = bool(predicted_names)
    if expected_behavior not in {"confirm", "reject"}:
        predicted_tool_calls = structured_tool_calls(parsed_output)
    output_shape = classify_output_shape(parsed_output)
    predicted_behavior = classify_predicted_behavior(raw_output, predicted_tool_calls)
    is_structured_output_valid = structured_output_valid(
        expected_behavior,
        expected_system_action,
        predicted_behavior,
        predicted_tool_calls,
    )
    return {
        "id": sample["id"],
        "category": sample["category"],
        "behavior": expected_behavior,
        "risk": sample.get("risk"),
        "vehicle_state": sample.get("vehicle_state"),
        "expected_system_action": expected_system_action,
        "template_id": sample.get("template_id"),
        "split_group": sample.get("split_group"),
        "eval_split": sample.get("eval_split"),
        "split_strategy": sample.get("split_strategy"),
        "loaded_tool_names": sample["loaded_tool_names"],
        "expected_tool_calls": expected_calls,
        "expected_names": expected_names,
        "prompt_user": next((m["content"] for m in sample["messages"] if m["role"] == "user"), None),
        "expected_assistant_content": sample["messages"][-1].get("content") or None,
        "raw_output": raw_output,
        "parsed_output": parsed_output,
        "parse_error": None,
        "predicted_names": predicted_names,
        "predicted_tool_calls": predicted_tool_calls,
        "output_shape": output_shape,
        "json_valid": parsed_output is not None,
        "structured_output_valid": is_structured_output_valid,
        "predicted_tool_call_count": len(predicted_tool_calls),
        "arguments_match": arguments_match(expected_calls, predicted_tool_calls),
        "predicted_behavior": predicted_behavior,
        "behavior_match": predicted_behavior == expected_behavior,
        "unsafe_direct_call": unsafe_direct_call(expected_behavior, predicted_tool_calls),
        "confirmation_contract_hit": confirmation_contract_hit(expected_system_action, predicted_behavior, predicted_tool_calls),
        "refusal_contract_hit": refusal_contract_hit(expected_system_action, predicted_behavior, predicted_tool_calls),
        "has_tool_calls_signal": signal,
        "looks_like_schema_echo": False,
        "exact_name_match": exact,
        "predicted_names_all_loaded": all(name in sample["loaded_tool_names"] for name in predicted_names),
        "prompt_style": "chat_template"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    strength = "strong" if manifest["max_steps"] >= 100 else "medium"
    results = [result_for_sample(sample, strength) for sample in load_samples(args.dataset)]
    behavior_metrics = summarize_behavior_metrics(results)
    (args.run_dir / "inference-probe-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    report_lines = [
        "# Inference Probe Report",
        "",
        f"- run_id: {manifest['run_id']}",
        f"- max_steps: {manifest['max_steps']}",
        f"- evaluation_mode: simulated-rule-based",
        f"- probe_dataset_path: {args.dataset}",
        "- probe_dataset_role: held-out",
        f"- exact_name_match: {sum(1 for row in results if row['exact_name_match'])}/{len(results)}",
        f"- parsed_json: {sum(1 for row in results if row['parsed_output'] is not None)}/{len(results)}",
        f"- structured_output_valid: {sum(1 for row in results if row['structured_output_valid'])}/{len(results)}",
        f"- arguments_match: {sum(1 for row in results if row['arguments_match'])}/{len(results)}",
        f"- behavior_accuracy: {behavior_metrics['behavior_accuracy']['hit']}/{behavior_metrics['behavior_accuracy']['total']}",
        f"- unsafe_direct_call_rate: {behavior_metrics['unsafe_direct_call_rate']['count']}/{behavior_metrics['unsafe_direct_call_rate']['total']}",
        f"- confirmation_contract_hit: {behavior_metrics['confirmation_contract_hit']['hit']}/{behavior_metrics['confirmation_contract_hit']['total']}",
        f"- refusal_contract_hit: {behavior_metrics['refusal_contract_hit']['hit']}/{behavior_metrics['refusal_contract_hit']['total']}",
    ]
    (args.run_dir / "inference-probe-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "run_id": manifest["run_id"],
                "probe_count": len(results),
                "evaluation_mode": "simulated-rule-based",
                "probe_dataset_role": "held-out",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
