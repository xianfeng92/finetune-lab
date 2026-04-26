from __future__ import annotations

from build_public_augmented_dataset import build_augmentation_summary, sanitize_sample


def test_sanitize_sample_drops_import_only_fields() -> None:
    sample = {
        "id": "car-bench-demo",
        "category": "single_domain_single_tool",
        "behavior": "tool_call",
        "risk": "low",
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "domains_loaded": ["lighting"],
        "loaded_tool_names": ["lighting_set_ambient"],
        "system_prompt": "demo",
        "messages": [{"role": "user", "content": "x"}, {"role": "assistant", "content": "", "tool_calls": []}],
        "meta": {"prompt_token_count": 12, "generator_model": "car-bench/import-v1", "adversarial": False, "seed_anchor_id": "a"},
        "sft_text": "demo",
        "source": {"dataset": "car-bench"},
        "source_actions": [{"name": "set_ambient_lights"}],
    }

    sanitized = sanitize_sample(sample)

    assert "source" not in sanitized
    assert "source_actions" not in sanitized
    assert sanitized["loaded_tool_names"] == ["lighting_set_ambient"]


def test_build_augmentation_summary_counts_sources_and_domains() -> None:
    car_bench_rows = [
        {"behavior": "tool_call", "domains_loaded": ["lighting"], "category": "single_domain_single_tool"},
        {"behavior": "tool_call", "domains_loaded": ["navigation"], "category": "single_domain_single_tool"},
    ]
    clarifyvc_rows = [
        {"behavior": "clarify", "domains_loaded": ["hvac"], "category": "clarifyvc_tier2_ambiguity_detection_and_clarification"},
    ]

    summary = build_augmentation_summary(car_bench_rows, clarifyvc_rows)

    assert summary["public_sample_count"] == 3
    assert summary["public_source_counts"] == {"car_bench": 2, "clarifyvc": 1}
    assert summary["public_behavior_counts"] == {"clarify": 1, "tool_call": 2}
    assert summary["public_domain_counts"] == {"hvac": 1, "lighting": 1, "navigation": 1}
