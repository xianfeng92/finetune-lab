from __future__ import annotations

from schema_sampler import load_schema, sample_loaded_tools
from pipeline import generate_samples, split_samples
from validator import validate_samples


def test_schema_sampler_returns_tools() -> None:
    schema = load_schema()
    tools = sample_loaded_tools(schema, ["hvac"], include_meta=True, seed=7)
    names = [tool["name"] for tool in tools]
    assert "hvac_set_temperature" in names or "hvac_set_fan_speed" in names
    assert "_meta_reroute" in names


def test_generated_samples_validate() -> None:
    samples = generate_samples()
    errors = validate_samples(samples)
    assert len(samples) == 100
    assert errors == []
    assert {sample["behavior"] for sample in samples} == {"tool_call", "clarify", "handoff", "confirm", "reject"}
    assert all("behavior" in sample for sample in samples)
    assert all("template_id" in sample for sample in samples)
    assert all("split_group" in sample for sample in samples)
    assert all(sample["eval_split"] == "unassigned" for sample in samples)
    assert {sample["risk"] for sample in samples} == {"low", "medium", "high"}
    assert all("vehicle_state" in sample for sample in samples)
    assert all(set(sample["vehicle_state"].keys()) == {"speed_kph", "power_state"} for sample in samples)
    assert sum(1 for sample in samples if sample.get("expected_system_action", {}).get("type") == "create_pending_confirmation") == 5
    assert sum(1 for sample in samples if sample.get("expected_system_action", {}).get("type") == "refuse_execution") == 5


def test_split_samples_produces_category_held_out_set() -> None:
    samples = generate_samples()
    train_samples, held_out_samples = split_samples(samples)

    assert len(train_samples) == 80
    assert len(held_out_samples) == 20
    assert {sample["id"] for sample in train_samples}.isdisjoint({sample["id"] for sample in held_out_samples})

    held_out_by_category = {}
    for sample in held_out_samples:
        held_out_by_category[sample["category"]] = held_out_by_category.get(sample["category"], 0) + 1

    assert held_out_by_category == {
        "single_domain_single_tool": 6,
        "single_domain_multi_tool_chain": 3,
        "cross_domain_multi_tool": 3,
        "reroute_to_meta": 2,
        "full_tool_fallback": 2,
        "proactive_event_driven": 2,
        "confirm_required_action": 1,
        "reject_unsafe_action": 1,
    }


def test_group_split_keeps_templates_out_of_train() -> None:
    samples = generate_samples(multiplier=5)
    train_samples, held_out_samples = split_samples(samples, split_strategy="group")

    train_groups = {sample["split_group"] for sample in train_samples}
    held_out_groups = {sample["split_group"] for sample in held_out_samples}

    assert train_groups.isdisjoint(held_out_groups)
    assert {sample["eval_split"] for sample in train_samples} == {"train"}
    assert {sample["eval_split"] for sample in held_out_samples} == {"unseen_template"}
