from __future__ import annotations

from import_clarifyvc import PROTOCOL_SEED_EXAMPLES, normalize_protocol_record


def test_normalize_protocol_record_maps_tier2_to_clarify() -> None:
    record = next(seed for seed in PROTOCOL_SEED_EXAMPLES if seed["id"] == "clarifyvc-tier2-hvac-intensity")

    sample, skip_reason = normalize_protocol_record(record)

    assert skip_reason is None
    assert sample is not None
    assert sample["behavior"] == "clarify"
    assert sample["category"] == "clarifyvc_tier2_ambiguity_detection_and_clarification"
    assert sample["messages"][0]["role"] == "user"
    assert sample["messages"][-1]["role"] == "assistant"
    assert "多少度" in sample["messages"][-1]["content"]


def test_normalize_protocol_record_preserves_multi_turn_history() -> None:
    record = next(seed for seed in PROTOCOL_SEED_EXAMPLES if seed["id"] == "clarifyvc-tier3-hvac-multi-turn")

    sample, skip_reason = normalize_protocol_record(record)

    assert skip_reason is None
    assert sample is not None
    assert sample["behavior"] == "tool_call"
    assert len(sample["messages"]) == 4
    assert sample["messages"][0]["content"] == "It's too hot in here."
    assert sample["messages"][-1]["tool_calls"][0]["name"] == "hvac_set_temperature"


def test_normalize_protocol_record_maps_lighting_domain() -> None:
    record = next(seed for seed in PROTOCOL_SEED_EXAMPLES if seed["id"] == "clarifyvc-tier1-lighting-direct")

    sample, skip_reason = normalize_protocol_record(record)

    assert skip_reason is None
    assert sample is not None
    assert sample["loaded_tool_names"] == ["lighting_set_ambient"]
    assert sample["messages"][-1]["tool_calls"][0]["arguments"]["color"] == "purple"


def test_normalize_protocol_record_maps_navigation_and_media_domains() -> None:
    navigation_record = next(seed for seed in PROTOCOL_SEED_EXAMPLES if seed["id"] == "clarifyvc-tier1-navigation-direct")
    media_record = next(seed for seed in PROTOCOL_SEED_EXAMPLES if seed["id"] == "clarifyvc-tier1-media-direct")

    navigation_sample, navigation_skip_reason = normalize_protocol_record(navigation_record)
    media_sample, media_skip_reason = normalize_protocol_record(media_record)

    assert navigation_skip_reason is None
    assert navigation_sample is not None
    assert navigation_sample["loaded_tool_names"] == ["navigation_set_destination"]
    assert navigation_sample["messages"][-1]["tool_calls"][0]["arguments"]["destination_query"] == "nearest station"

    assert media_skip_reason is None
    assert media_sample is not None
    assert media_sample["loaded_tool_names"] == ["media_play_content"]
    assert media_sample["messages"][-1]["tool_calls"][0]["arguments"]["query"] == "jazz playlist"
