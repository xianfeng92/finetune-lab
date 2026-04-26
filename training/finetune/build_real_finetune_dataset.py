from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = ROOT / "data" / "tool-schemas" / "automotive-v1.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_category_filter(values: list[str] | None) -> list[str]:
    categories: list[str] = []
    for value in values or []:
        for item in value.split(","):
            category = item.strip()
            if category:
                categories.append(category)
    return categories


def flatten_tool_lookup(schema_payload: dict) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    domains = schema_payload.get("domains", {})
    for _, tools in domains.items():
        for tool in tools:
            lookup[tool["name"]] = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {"type": "object", "properties": {}}),
                },
            }
    return lookup


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


def to_chat_tool_call(tool_call: dict) -> dict:
    normalized = normalize_expected_tool_call(tool_call)
    return {
        "type": "function",
        "function": {
            "name": normalized["name"],
            # Gemma 4's chat template expects a structured object here and will
            # serialize it into `call:name{...}` form itself. Passing a JSON
            # string produces `{{...}}` payloads that the downstream parser
            # cannot read back during probing.
            "arguments": normalized["arguments"],
        },
    }


def build_messages(sample: dict) -> list[dict]:
    messages: list[dict] = []
    if sample.get("system_prompt"):
        messages.append({"role": "system", "content": sample["system_prompt"]})
    for message in sample["messages"]:
        payload = {
            "role": message["role"],
            "content": message.get("content") or "",
        }
        if message.get("tool_calls"):
            payload["tool_calls"] = [to_chat_tool_call(call) for call in message["tool_calls"]]
        messages.append(payload)
    return messages


def filter_samples(samples: list[dict], categories: list[str]) -> list[dict]:
    if not categories:
        return samples
    category_set = set(categories)
    return [sample for sample in samples if sample["category"] in category_set]


def build_record(sample: dict, tool_lookup: dict[str, dict]) -> dict:
    missing_tools = [name for name in sample["loaded_tool_names"] if name not in tool_lookup]
    if missing_tools:
        raise KeyError(f"Missing schema for tools: {missing_tools}")

    expected_tool_calls = [
        normalize_expected_tool_call(call)
        for call in sample["messages"][-1].get("tool_calls", [])
    ]
    return {
        "id": sample["id"],
        "category": sample["category"],
        "behavior": sample["behavior"],
        "risk": sample["risk"],
        "vehicle_state": sample["vehicle_state"],
        "expected_system_action": sample.get("expected_system_action"),
        "messages": build_messages(sample),
        "tools": [tool_lookup[name] for name in sample["loaded_tool_names"]],
        "loaded_tool_names": sample["loaded_tool_names"],
        "expected_tool_calls": expected_tool_calls,
        "prompt_user": next((msg["content"] for msg in sample["messages"] if msg["role"] == "user"), ""),
        "source_dataset_path": sample.get("source_dataset_path", "data/sft/v1-seed-anchor-demo"),
    }


def split_eval_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in sorted(records, key=lambda row: row["id"]):
        grouped[record["category"]].append(record)

    valid: list[dict] = []
    test: list[dict] = []
    for category in sorted(grouped):
        bucket = grouped[category]
        split_index = max(1, math.ceil(len(bucket) / 2))
        valid.extend(bucket[:split_index])
        test.extend(bucket[split_index:])
        if not bucket[split_index:]:
            test.append(bucket[-1])
            valid.pop()
    return valid, test


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def build_pack(
    train_rows: list[dict],
    valid_rows: list[dict],
    test_rows: list[dict],
    schema_path: Path,
    output_dir: Path,
    category_filter: list[str],
) -> dict:
    counts = {
        "train": len(train_rows),
        "valid": len(valid_rows),
        "test": len(test_rows),
    }
    category_counts = {
        split: Counter(row["category"] for row in rows)
        for split, rows in [("train", train_rows), ("valid", valid_rows), ("test", test_rows)]
    }
    behavior_counts = {
        split: Counter(row["behavior"] for row in rows)
        for split, rows in [("train", train_rows), ("valid", valid_rows), ("test", test_rows)]
    }
    risk_counts = {
        split: Counter(row["risk"] for row in rows)
        for split, rows in [("train", train_rows), ("valid", valid_rows), ("test", test_rows)]
    }
    system_action_counts = {
        split: Counter(
            row["expected_system_action"]["type"]
            for row in rows
            if row.get("expected_system_action")
        )
        for split, rows in [("train", train_rows), ("valid", valid_rows), ("test", test_rows)]
    }
    return {
        "title": "Gemma real mini fine-tune dataset pack",
        "training_format": "openai-chat-with-tools",
        "schema_path": str(schema_path.relative_to(ROOT)),
        "output_dir": str(output_dir.relative_to(ROOT)),
        "category_filter": category_filter,
        "counts": counts,
        "categories": {
            split: dict(counter)
            for split, counter in category_counts.items()
        },
        "behaviors": {
            split: dict(counter)
            for split, counter in behavior_counts.items()
        },
        "risks": {
            split: dict(counter)
            for split, counter in risk_counts.items()
        },
        "expected_system_actions": {
            split: dict(counter)
            for split, counter in system_action_counts.items()
        },
        "notes": [
            "train split keeps the original SFT teaching samples.",
            "held-out split is re-sliced into valid/test so MLX LoRA can report validation loss and keep a separate probe set.",
            "assistant tool calls are rewritten into OpenAI-style function calls for tokenizer.apply_chat_template(..., tools=...).",
            "behavior labels are preserved so later eval layers can distinguish tool_call / clarify / handoff style decisions.",
            "risk and vehicle_state are preserved so later eval layers can reason about safety context instead of only tool names.",
            "category_filter limits the dataset to a narrower teaching slice when you want a simpler controlled run.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-dataset", type=Path, required=True)
    parser.add_argument("--held-out-dataset", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pack-output", type=Path, required=True)
    parser.add_argument(
        "--category-filter",
        action="append",
        help="Optional category name(s) to keep. Can be repeated or comma-separated.",
    )
    args = parser.parse_args()

    schema_payload = json.loads(args.schema.read_text(encoding="utf-8"))
    tool_lookup = flatten_tool_lookup(schema_payload)
    category_filter = parse_category_filter(args.category_filter)

    train_samples = filter_samples(load_jsonl(args.train_dataset), category_filter)
    held_out_samples = filter_samples(load_jsonl(args.held_out_dataset), category_filter)
    if not train_samples:
        raise SystemExit(f"No train samples remain after category_filter={category_filter}")
    if len(held_out_samples) < 2:
        raise SystemExit(
            "Need at least 2 held-out samples after filtering so valid/test can both exist. "
            f"category_filter={category_filter}"
        )

    train_rows = [build_record(sample, tool_lookup) for sample in train_samples]
    held_out_rows = [build_record(sample, tool_lookup) for sample in held_out_samples]
    valid_rows, test_rows = split_eval_records(held_out_rows)

    write_jsonl(args.output_dir / "train.jsonl", train_rows)
    write_jsonl(args.output_dir / "valid.jsonl", valid_rows)
    write_jsonl(args.output_dir / "test.jsonl", test_rows)

    pack = build_pack(
        train_rows,
        valid_rows,
        test_rows,
        args.schema.resolve(),
        args.output_dir.resolve(),
        category_filter,
    )
    args.pack_output.parent.mkdir(parents=True, exist_ok=True)
    args.pack_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pack, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
