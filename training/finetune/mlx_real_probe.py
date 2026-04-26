from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MLX_COMPAT_DIR = ROOT / "training" / "finetune" / "mlx_compat"

if str(MLX_COMPAT_DIR) not in sys.path:
    sys.path.insert(0, str(MLX_COMPAT_DIR))

import gemma4_e2b_compat  # noqa: F401

from mlx_lm import generate, load
from mlx_lm.generate import make_sampler
from behavior_eval import (
    classify_predicted_behavior,
    confirmation_contract_hit,
    refusal_contract_hit,
    structured_output_valid,
    summarize_behavior_metrics,
    unsafe_direct_call,
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_expected_tool_call(tool_call: dict) -> dict:
    if "function" in tool_call:
        function = tool_call["function"]
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        return {"name": function["name"], "arguments": arguments}
    return {
        "name": tool_call["name"],
        "arguments": tool_call.get("arguments", {}),
    }


def normalize_predicted_tool_call(tool_call: dict) -> dict:
    if "function" in tool_call:
        tool_call = tool_call["function"]
    arguments = tool_call.get("arguments", {})
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {"raw": arguments}
    return {
        "name": tool_call.get("name", "unknown"),
        "arguments": arguments if isinstance(arguments, dict) else {"raw": arguments},
    }


def arguments_match(expected_calls: list[dict], predicted_calls: list[dict]) -> bool:
    if len(expected_calls) != len(predicted_calls):
        return False
    for expected, predicted in zip(expected_calls, predicted_calls):
        if expected != predicted:
            return False
    return True


def extract_json_object(text: str) -> dict | list | None:
    stripped = text.strip()
    for candidate in (stripped,):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    for pattern in (r"(\{.*\})", r"(\[.*\])"):
        match = re.search(pattern, stripped, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None


def parse_tool_calls(raw_output: str, tokenizer, tools: list[dict] | None) -> tuple[dict | None, str | None]:
    stripped = raw_output.strip()
    parser = getattr(tokenizer, "tool_parser", None)
    start_marker = getattr(tokenizer, "tool_call_start", None)
    end_marker = getattr(tokenizer, "tool_call_end", None)
    parse_error = None

    if parser is not None and start_marker and end_marker and start_marker in stripped and end_marker in stripped:
        segments = []
        cursor = 0
        while True:
            start = stripped.find(start_marker, cursor)
            if start < 0:
                break
            end = stripped.find(end_marker, start + len(start_marker))
            if end < 0:
                break
            payload = stripped[start + len(start_marker):end]
            try:
                segments.append(normalize_predicted_tool_call(parser(payload, tools)))
            except Exception as exc:
                parse_error = str(exc)
            cursor = end + len(end_marker)
        if segments:
            return {"tool_calls": segments}, None

    if parser is not None:
        try:
            return {"tool_calls": [normalize_predicted_tool_call(parser(stripped, tools))]}, None
        except Exception as exc:
            parse_error = str(exc)
        else:
            parse_error = None

    json_payload = extract_json_object(stripped)
    if isinstance(json_payload, dict):
        if "tool_calls" in json_payload and isinstance(json_payload["tool_calls"], list):
            return {
                "tool_calls": [normalize_predicted_tool_call(call) for call in json_payload["tool_calls"]]
            }, parse_error
        if "name" in json_payload:
            return {"tool_calls": [normalize_predicted_tool_call(json_payload)]}, parse_error
    if isinstance(json_payload, list) and all(isinstance(item, dict) for item in json_payload):
        return {"tool_calls": [normalize_predicted_tool_call(item) for item in json_payload]}, parse_error
    return None, parse_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=256)
    args = parser.parse_args()

    if args.model_name.startswith("google/gemma-4"):
        raise SystemExit(
            "real MLX probing requires an MLX-converted checkpoint. "
            "Use `mlx-community/gemma-4-e2b-it-4bit`."
        )

    manifest = json.loads((args.run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    model, tokenizer = load(args.model_name, adapter_path=str(args.run_dir / "adapters"))
    rows = load_jsonl(args.dataset)[: args.max_samples]

    results: list[dict] = []
    for row in rows:
        prompt_messages = row["messages"][:-1] if row["messages"] and row["messages"][-1]["role"] == "assistant" else row["messages"]
        prompt = tokenizer.apply_chat_template(
            prompt_messages,
            tools=row.get("tools"),
            add_generation_prompt=True,
            return_dict=False,
        )
        raw_output = generate(
            model,
            tokenizer,
            prompt,
            verbose=False,
            max_tokens=args.max_tokens,
            sampler=make_sampler(temp=0.0),
        )
        parsed_output, parse_error = parse_tool_calls(raw_output, tokenizer, row.get("tools"))
        predicted_tool_calls = [
            normalize_predicted_tool_call(call)
            for call in (parsed_output or {}).get("tool_calls", [])
        ]
        expected_tool_calls = [normalize_expected_tool_call(call) for call in row.get("expected_tool_calls", [])]
        predicted_names = [call["name"] for call in predicted_tool_calls]
        expected_names = [call["name"] for call in expected_tool_calls]
        expected_behavior = row.get("behavior", "tool_call")
        expected_system_action = row.get("expected_system_action")
        predicted_behavior = classify_predicted_behavior(raw_output, predicted_tool_calls)
        is_structured_output_valid = structured_output_valid(
            expected_behavior,
            expected_system_action,
            predicted_behavior,
            predicted_tool_calls,
        )
        results.append(
            {
                "id": row["id"],
                "category": row["category"],
                "behavior": expected_behavior,
                "risk": row.get("risk"),
                "vehicle_state": row.get("vehicle_state"),
                "expected_system_action": expected_system_action,
                "loaded_tool_names": row["loaded_tool_names"],
                "expected_tool_calls": expected_tool_calls,
                "expected_names": expected_names,
                "prompt_user": row.get("prompt_user"),
                "raw_output": raw_output,
                "parsed_output": parsed_output,
                "parse_error": parse_error,
                "predicted_names": predicted_names,
                "predicted_tool_calls": predicted_tool_calls,
                "output_shape": "tool_calls_array" if predicted_tool_calls else "other",
                "json_valid": parsed_output is not None,
                "structured_output_valid": is_structured_output_valid,
                "predicted_tool_call_count": len(predicted_tool_calls),
                "arguments_match": arguments_match(expected_tool_calls, predicted_tool_calls),
                "predicted_behavior": predicted_behavior,
                "behavior_match": predicted_behavior == expected_behavior,
                "unsafe_direct_call": unsafe_direct_call(expected_behavior, predicted_tool_calls),
                "confirmation_contract_hit": confirmation_contract_hit(expected_system_action, predicted_behavior, predicted_tool_calls),
                "refusal_contract_hit": refusal_contract_hit(expected_system_action, predicted_behavior, predicted_tool_calls),
                "has_tool_calls_signal": bool(predicted_tool_calls),
                "looks_like_schema_echo": False,
                "exact_name_match": predicted_names == expected_names,
                "predicted_names_all_loaded": all(name in row["loaded_tool_names"] for name in predicted_names),
                "prompt_style": "chat_template_with_tools",
            }
        )

    (args.run_dir / "inference-probe-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    behavior_metrics = summarize_behavior_metrics(results)
    report_lines = [
        "# Inference Probe Report",
        "",
        f"- run_id: {manifest['run_id']}",
        f"- max_steps: {manifest['max_steps']}",
        f"- evaluation_mode: real-mlx-generate-best-effort",
        f"- probe_dataset_path: {args.dataset}",
        "- probe_dataset_role: test",
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
                "evaluation_mode": "real-mlx-generate-best-effort",
                "probe_dataset_role": "test",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
