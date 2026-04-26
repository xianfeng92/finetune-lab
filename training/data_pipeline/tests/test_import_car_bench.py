from __future__ import annotations

from import_car_bench import READ_ONLY_HELPER_ACTIONS, infer_vehicle_state, map_action, normalize_task_record


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


def test_map_action_supports_lighting_and_navigation() -> None:
    lighting_action = {"name": "set_fog_lights", "kwargs": {"on": True}}
    navigation_action = {"name": "set_new_navigation", "kwargs": {"route_ids": ["route_1", "route_2"]}}

    lighting_mapped = map_action(lighting_action, {})
    navigation_mapped = map_action(navigation_action, {})

    assert lighting_mapped == [{"name": "lighting_set_fog_lights", "arguments": {"on": True}}]
    assert navigation_mapped == [{"name": "navigation_set_route", "arguments": {"route_ids": ["route_1", "route_2"]}}]


def test_normalize_task_record_ignores_read_only_helpers_when_supported_action_exists() -> None:
    record = {
        "task_id": "base_nav_1",
        "calendar_id": None,
        "persona": "Planner persona.",
        "instruction": "Navigate to Munich and start the route.",
        "task_type": "base",
        "actions": json_actions(
            [
                {"name": "get_location_id_by_location_name", "kwargs": {"location": "Munich"}},
                {"name": "get_routes_from_start_to_destination", "kwargs": {"start_id": "loc_a", "destination_id": "loc_b"}},
                {"name": "set_new_navigation", "kwargs": {"route_ids": ["rll_demo_1"]}},
            ]
        ),
        "context_init_config": '{"navigation_active": false, "seats_occupied": {"driver": true}}',
    }

    sample, skip_reason = normalize_task_record(record, "tasks_base", "train")

    assert skip_reason is None
    assert sample is not None
    assert sample["loaded_tool_names"] == ["navigation_set_route"]
    assert sample["domains_loaded"] == ["navigation"]
    assert sample["messages"][-1]["tool_calls"] == [{"name": "navigation_set_route", "arguments": {"route_ids": ["rll_demo_1"]}}]
    assert "get_location_id_by_location_name" in READ_ONLY_HELPER_ACTIONS


def json_actions(actions: list[dict]) -> str:
    import json

    return json.dumps(
        [
            {
                "name": action["name"],
                "kwargs": action["kwargs"],
                "index": index,
                "dependent_on_action_index": None,
            }
            for index, action in enumerate(actions)
        ]
    )
