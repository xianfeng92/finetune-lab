"""4-dim PolicyGateway probe for llama.cpp Gemma 4 GGUF.

Mirrors training/finetune/mlx_real_probe.py I/O contract — same
inference-probe-results.json + inference-probe-report.md schema — so the W4
EdgeBenchRunner can compare engines apples-to-apples.

Inference path: subprocess `llama-completion` with chat-template-applied
prompt; -no-cnv is REQUIRED to bypass auto-conversation mode that crashes on
the embedded Gemma 4 minja-incompatible template (see
edge-bench/deploy/llama_cpp/convert.sh trap notes).

Tool parser: reuses mlx_lm.tool_parsers.gemma4 — pure regex, no MLX runtime,
guarantees byte-identical parse path with mlx_real_probe.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from probe.behavior_eval import (  # noqa: E402
    classify_predicted_behavior,
    confirmation_contract_hit,
    refusal_contract_hit,
    structured_output_valid,
    summarize_behavior_metrics,
    unsafe_direct_call,
)
from probe.parse import (  # noqa: E402
    arguments_match,
    normalize_expected_tool_call,
    normalize_predicted_tool_call,
    parse_tool_calls,
)

from transformers import AutoTokenizer  # noqa: E402
from mlx_lm.tool_parsers.gemma4 import (  # noqa: E402
    parse_tool_call as gemma4_parser,
    tool_call_start as GEMMA4_START,
    tool_call_end as GEMMA4_END,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gguf", type=Path, required=True, help="Path to .gguf model")
    parser.add_argument("--tokenizer-dir", type=Path, required=True, help="HF model dir for AutoTokenizer + chat template")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--llama-completion", default="llama-completion", help="llama-completion binary")
    args = parser.parse_args()

    args.run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": args.run_dir.name,
        "max_steps": 0,
        "training_mode": "fused-into-base",
        "model_name": str(args.gguf),
        "engine": "llama_cpp",
        "tokenizer_dir": str(args.tokenizer_dir),
    }
    (args.run_dir / "run-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer_dir))
    rows = [
        json.loads(line)
        for line in args.dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.max_samples]

    prompt_path = args.run_dir / "_tmp_prompt.txt"
    results: list[dict] = []
    started = time.time()
    for i, row in enumerate(rows):
        prompt_messages = (
            row["messages"][:-1]
            if row["messages"] and row["messages"][-1]["role"] == "assistant"
            else row["messages"]
        )
        prompt = tokenizer.apply_chat_template(
            prompt_messages,
            tools=row.get("tools"),
            add_generation_prompt=True,
            tokenize=False,
        )
        prompt_path.write_text(prompt, encoding="utf-8")

        proc = subprocess.run(
            [
                args.llama_completion,
                "-m", str(args.gguf),
                "-f", str(prompt_path),
                "-n", str(args.max_tokens),
                "--no-display-prompt",
                "-no-cnv",
                "--temp", "0",
            ],
            capture_output=True, text=True, timeout=180,
        )
        raw_output = proc.stdout.replace(" [end of text]", "").rstrip()

        parsed_output, parse_error = parse_tool_calls(
            raw_output,
            row.get("tools"),
            parser=gemma4_parser,
            start_marker=GEMMA4_START,
            end_marker=GEMMA4_END,
        )
        predicted_tool_calls = [
            normalize_predicted_tool_call(call)
            for call in (parsed_output or {}).get("tool_calls", [])
        ]
        expected_tool_calls = [
            normalize_expected_tool_call(call) for call in row.get("expected_tool_calls", [])
        ]
        predicted_names = [c["name"] for c in predicted_tool_calls]
        expected_names = [c["name"] for c in expected_tool_calls]
        expected_behavior = row.get("behavior", "tool_call")
        expected_system_action = row.get("expected_system_action")
        predicted_behavior = classify_predicted_behavior(raw_output, predicted_tool_calls)
        is_structured_output_valid = structured_output_valid(
            expected_behavior, expected_system_action, predicted_behavior, predicted_tool_calls
        )

        results.append({
            "id": row["id"],
            "category": row["category"],
            "behavior": expected_behavior,
            "risk": row.get("risk"),
            "vehicle_state": row.get("vehicle_state"),
            "expected_system_action": expected_system_action,
            "template_id": row.get("template_id"),
            "split_group": row.get("split_group"),
            "eval_split": row.get("eval_split"),
            "split_strategy": row.get("split_strategy"),
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
            "confirmation_contract_hit": confirmation_contract_hit(
                expected_system_action, predicted_behavior, predicted_tool_calls
            ),
            "refusal_contract_hit": refusal_contract_hit(
                expected_system_action, predicted_behavior, predicted_tool_calls
            ),
            "has_tool_calls_signal": bool(predicted_tool_calls),
            "looks_like_schema_echo": False,
            "exact_name_match": predicted_names == expected_names,
            "predicted_names_all_loaded": all(n in row["loaded_tool_names"] for n in predicted_names),
            "prompt_style": "chat_template_with_tools",
        })

        if (i + 1) % 16 == 0:
            print(f"  ... {i + 1}/{len(rows)} cases done", file=sys.stderr)

    if prompt_path.exists():
        prompt_path.unlink()

    (args.run_dir / "inference-probe-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    behavior_metrics = summarize_behavior_metrics(results)
    report_lines = [
        "# Inference Probe Report",
        "",
        f"- run_id: {manifest['run_id']}",
        f"- max_steps: {manifest['max_steps']}",
        "- evaluation_mode: llama-cpp-completion-temp0",
        f"- probe_dataset_path: {args.dataset}",
        "- probe_dataset_role: test",
        f"- exact_name_match: {sum(1 for r in results if r['exact_name_match'])}/{len(results)}",
        f"- parsed_json: {sum(1 for r in results if r['parsed_output'] is not None)}/{len(results)}",
        f"- structured_output_valid: {sum(1 for r in results if r['structured_output_valid'])}/{len(results)}",
        f"- arguments_match: {sum(1 for r in results if r['arguments_match'])}/{len(results)}",
        f"- behavior_accuracy: {behavior_metrics['behavior_accuracy']['hit']}/{behavior_metrics['behavior_accuracy']['total']}",
        f"- unsafe_direct_call_rate: {behavior_metrics['unsafe_direct_call_rate']['count']}/{behavior_metrics['unsafe_direct_call_rate']['total']}",
        f"- confirmation_contract_hit: {behavior_metrics['confirmation_contract_hit']['hit']}/{behavior_metrics['confirmation_contract_hit']['total']}",
        f"- refusal_contract_hit: {behavior_metrics['refusal_contract_hit']['hit']}/{behavior_metrics['refusal_contract_hit']['total']}",
        f"- wall_seconds: {round(time.time() - started, 1)}",
    ]
    (args.run_dir / "inference-probe-report.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "run_id": manifest["run_id"],
        "probe_count": len(results),
        "evaluation_mode": "llama-cpp-completion-temp0",
        "probe_dataset_role": "test",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
