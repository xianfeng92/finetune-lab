from __future__ import annotations

from training.finetune.behavior_eval import (
    classify_predicted_behavior,
    structured_output_valid,
)


def test_meta_reroute_with_broad_reason_maps_to_clarify() -> None:
    predicted = [
        {
            "name": "_meta_reroute",
            "arguments": {
                "reason": "request is too broad for a single deterministic tool path",
                "suggested_domains": ["hvac", "window"],
            },
        }
    ]
    assert classify_predicted_behavior("", predicted) == "clarify"


def test_meta_reroute_with_tool_mismatch_maps_to_handoff() -> None:
    predicted = [
        {
            "name": "_meta_reroute",
            "arguments": {
                "reason": "loaded tools do not match intent",
                "suggested_domains": ["window"],
            },
        }
    ]
    assert classify_predicted_behavior("", predicted) == "handoff"


def test_confirm_text_without_tool_calls_is_valid_structured_behavior() -> None:
    assert structured_output_valid(
        expected_behavior="confirm",
        expected_system_action={"type": "create_pending_confirmation"},
        predicted_behavior="confirm",
        predicted_tool_calls=[],
    )


def test_reject_text_without_tool_calls_is_valid_structured_behavior() -> None:
    assert structured_output_valid(
        expected_behavior="reject",
        expected_system_action={"type": "refuse_execution"},
        predicted_behavior="reject",
        predicted_tool_calls=[],
    )


def test_answer_only_without_contract_is_not_structured_output() -> None:
    assert not structured_output_valid(
        expected_behavior="answer_only",
        expected_system_action=None,
        predicted_behavior="answer_only",
        predicted_tool_calls=[],
    )
