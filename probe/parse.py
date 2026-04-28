"""Engine-agnostic tool-call parsing helpers.

Extracted from training/finetune/mlx_real_probe.py so that downstream consumers
(edge-bench llama.cpp / LiteRT-LM probes) can share the exact same parse path
that produced the MLX baseline ground truth — apples-to-apples 4-dim metrics.

The MLX-specific tokenizer wrapper exposes `tool_parser` / `tool_call_start` /
`tool_call_end` attributes; HF AutoTokenizer doesn't. This module accepts those
three values explicitly so any engine can plug in.
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Optional


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


def parse_tool_calls(
    raw_output: str,
    tools: list[dict] | None,
    *,
    parser: Optional[Callable[[str, Any], Any]] = None,
    start_marker: Optional[str] = None,
    end_marker: Optional[str] = None,
) -> tuple[dict | None, str | None]:
    """Parse model raw output into {tool_calls: [...]} or None.

    parser/start_marker/end_marker mirror the MLX TokenizerWrapper interface,
    but are explicit args here so any engine can supply them.
    """
    stripped = raw_output.strip()
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
