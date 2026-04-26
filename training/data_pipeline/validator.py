from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator

from schema_sampler import DEFAULT_SCHEMA_PATH, flatten_tools, load_schema


SAMPLE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
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
    ],
    "properties": {
        "id": {"type": "string"},
        "category": {"type": "string"},
        "behavior": {
            "type": "string",
            "enum": ["answer_only", "tool_call", "clarify", "confirm", "reject", "handoff"],
        },
        "risk": {"type": "string", "enum": ["low", "medium", "high"]},
        "vehicle_state": {
            "type": "object",
            "additionalProperties": False,
            "required": ["speed_kph", "power_state"],
            "properties": {
                "speed_kph": {"type": "integer", "minimum": 0},
                "power_state": {"type": "string", "enum": ["parked", "driving"]},
            },
        },
        "expected_system_action": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["create_pending_confirmation", "refuse_execution"],
                },
                "tool": {"type": "string"},
                "arguments": {"type": "object"},
                "expires_in_seconds": {"type": "integer", "minimum": 1},
                "reason_code": {"type": "string"},
            },
        },
        "domains_loaded": {"type": "array", "items": {"type": "string"}},
        "loaded_tool_names": {"type": "array", "items": {"type": "string"}},
        "system_prompt": {"type": "string"},
        "messages": {"type": "array"},
        "event": {"type": "object"},
        "meta": {
            "type": "object",
            "additionalProperties": False,
            "required": ["prompt_token_count", "generator_model", "adversarial", "seed_anchor_id"],
            "properties": {
                "prompt_token_count": {"type": "integer", "minimum": 0},
                "generator_model": {"type": "string"},
                "adversarial": {"type": "boolean"},
                "seed_anchor_id": {"type": ["string", "null"]},
            },
        },
        "sft_text": {"type": "string"},
    },
}


def validate_tool_call(tool_call: dict, tool_schemas: dict) -> None:
    if tool_call["name"] not in tool_schemas:
        raise ValueError(f"unknown tool: {tool_call['name']}")
    schema = tool_schemas[tool_call["name"]]["parameters"]
    Draft202012Validator(schema).validate(tool_call["arguments"])


def validate_sample(sample: dict, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    Draft202012Validator(SAMPLE_SCHEMA).validate(sample)
    schema = load_schema(schema_path)
    tool_schemas = flatten_tools(schema)
    for message in sample["messages"]:
        for tool_call in message.get("tool_calls", []):
            validate_tool_call(tool_call, tool_schemas)


def validate_jsonl(samples_path: Path) -> list[str]:
    errors: list[str] = []
    for line_no, line in enumerate(samples_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        sample = json.loads(line)
        try:
            validate_sample(sample)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"line {line_no}: {exc}")
    return errors


def validate_samples(samples: Iterable[dict]) -> list[str]:
    errors: list[str] = []
    for index, sample in enumerate(samples, start=1):
        try:
            validate_sample(sample)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"sample {index}: {exc}")
    return errors
