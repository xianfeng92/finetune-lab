from __future__ import annotations

from import_car_bench import infer_vehicle_state, map_action, normalize_task_record


def test_map_action_set_seat_heating_all_zones_uses_occupied_seats() -> None:
    action = {
        "name": "set_seat_heating",
        "kwargs": {
            "level": 2,
            "seat_zone": "ALL_ZONES",
        },
    }
    context = {
        "seats_occupied": {
            "driver": True,
            "passenger": True,
            "driver_rear": False,
            "passenger_rear": True,
        }
    }

    mapped = map_action(action, context)

    assert mapped == [
        {"name": "seat_set_heating", "arguments": {"position": "driver", "level": 2}},
        {"name": "seat_set_heating", "arguments": {"position": "passenger", "level": 2}},
        {"name": "seat_set_heating", "arguments": {"position": "rear_right", "level": 2}},
    ]


def test_infer_vehicle_state_detects_driving_language() -> None:
    vehicle_state = infer_vehicle_state("You are driving and want to open the windows.", {"navigation_active": False})
    assert vehicle_state == {"speed_kph": 35, "power_state": "driving"}


def test_normalize_task_record_builds_preview_sample() -> None:
    record = {
        "task_id": "base_14",
        "calendar_id": "cal_8382",
        "persona": "Commanding persona.",
        "instruction": "You're driving with a passenger and want to turn down the seat heating for both seats to level 1.",
        "task_type": "base",
        "actions": '[{"name": "set_seat_heating", "kwargs": {"level": 1, "seat_zone": "ALL_ZONES"}, "index": 0, "dependent_on_action_index": null}]',
        "context_init_config": '{"navigation_active": true, "seats_occupied": {"driver": true, "passenger": true, "driver_rear": false, "passenger_rear": false}}',
    }

    sample, skip_reason = normalize_task_record(record, "tasks_base", "train")

    assert skip_reason is None
    assert sample is not None
    assert sample["id"] == "car-bench-base_14"
    assert sample["category"] == "single_domain_multi_tool_chain"
    assert sample["behavior"] == "tool_call"
    assert sample["risk"] == "low"
    assert sample["vehicle_state"] == {"speed_kph": 35, "power_state": "driving"}
    assert sample["loaded_tool_names"] == ["seat_set_heating"]
    assert len(sample["messages"][1]["tool_calls"]) == 2
