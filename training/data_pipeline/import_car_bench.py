from __future__ import annotations

import argparse
import json
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from formatter import build_sft_text


RAW_BASE_URL = "https://huggingface.co/datasets/johanneskirmayr/car-bench-dataset/raw/main"

TASK_CONFIGS = {
    "tasks_base": {
        "train": "tasks/base_train.jsonl",
        "test": "tasks/base_test.jsonl",
    },
    "tasks_disambiguation": {
        "train": "tasks/disambiguation_train.jsonl",
        "test": "tasks/disambiguation_test.jsonl",
    },
    "tasks_hallucination": {
        "train": "tasks/hallucination_train.jsonl",
        "test": "tasks/hallucination_test.jsonl",
    },
}

DOMAIN_RISK = {
    "hvac": "low",
    "seat": "low",
    "window": "medium",
    "door": "high",
}

RISK_LEVELS = {
    "low": 0,
    "medium": 1,
    "high": 2,
}

WINDOW_POSITION_MAP = {
    "ALL": "all",
    "DRIVER": "front_left",
    "PASSENGER": "front_right",
    "DRIVER_REAR": "rear_left",
    "PASSENGER_REAR": "rear_right",
}

SEAT_ZONE_MAP = {
    "DRIVER": ["driver"],
    "ALL_ZONES": ["driver", "passenger", "rear_left", "rear_right"],
}

DIRECT_TASK_TYPES = {"base", "disambiguation_internal"}


def clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, int(value)))


def infer_vehicle_state(instruction: str, context: dict) -> dict:
    lowered = instruction.lower()
    driving_markers = (
        "while driving",
        "you are driving",
        "you're driving",
        "during your drive",
        "on your drive",
        "as you drive",
    )
    parked_markers = (
        "before you start driving",
        "before setting off",
        "while parked",
        "parked car",
    )
    if any(marker in lowered for marker in parked_markers):
        return {"speed_kph": 0, "power_state": "parked"}
    if context.get("navigation_active") or any(marker in lowered for marker in driving_markers):
        return {"speed_kph": 35, "power_state": "driving"}
    return {"speed_kph": 0, "power_state": "parked"}


def build_system_prompt(loaded_tool_names: list[str], vehicle_state: dict) -> str:
    return "\n".join(
        [
            "你是车机工具调用助手，只能从已加载工具中选择。",
            f"loaded_tool_names={','.join(loaded_tool_names)}",
            "vehicle_state:",
            json.dumps(vehicle_state, ensure_ascii=False),
        ]
    )


def infer_risk(domains: list[str], vehicle_state: dict) -> str:
    highest = "low"
    for domain in domains:
        candidate = DOMAIN_RISK.get(domain, "low")
        if RISK_LEVELS[candidate] > RISK_LEVELS[highest]:
            highest = candidate
    if vehicle_state["power_state"] == "driving" and highest == "medium":
        return "high"
    return highest


def infer_category(tool_calls: list[dict]) -> str:
    domains = {tool_call["name"].split("_", 1)[0] for tool_call in tool_calls}
    if len(domains) == 1 and len(tool_calls) == 1:
        return "single_domain_single_tool"
    if len(domains) == 1:
        return "single_domain_multi_tool_chain"
    return "cross_domain_multi_tool"


def occupied_positions_for_zone(zone: str, seats_occupied: dict) -> list[str]:
    if zone == "DRIVER":
        return ["driver"]
    if zone != "ALL_ZONES":
        return []

    resolved: list[str] = []
    if seats_occupied.get("driver", True):
        resolved.append("driver")
    if seats_occupied.get("passenger", True):
        resolved.append("passenger")
    if seats_occupied.get("driver_rear"):
        resolved.append("rear_left")
    if seats_occupied.get("passenger_rear"):
        resolved.append("rear_right")
    return resolved or ["driver", "passenger"]


def map_action(action: dict, context: dict) -> list[dict] | None:
    name = action["name"]
    kwargs = action.get("kwargs", {})
    seats_occupied = context.get("seats_occupied", {})

    if name == "set_climate_temperature":
        temperature = clamp_int(kwargs["temperature"], 16, 30)
        seat_zone = kwargs.get("seat_zone", "DRIVER")
        return [
            {
                "name": "hvac_set_temperature",
                "arguments": {
                    "zone": "driver" if position == "driver" else "passenger" if position == "passenger" else "rear",
                    "celsius": temperature,
                },
            }
            for position in occupied_positions_for_zone(seat_zone, seats_occupied)
        ]

    if name == "set_fan_speed":
        level = clamp_int(kwargs["level"], 1, 7)
        return [
            {"name": "hvac_set_fan_speed", "arguments": {"zone": zone, "level": level}}
            for zone in ["driver", "passenger"]
        ]

    if name == "open_close_window":
        position = WINDOW_POSITION_MAP.get(kwargs.get("window"))
        if not position:
            return None
        return [
            {
                "name": "window_set_open_percent",
                "arguments": {
                    "position": position,
                    "percent": clamp_int(kwargs["percentage"], 0, 100),
                },
            }
        ]

    if name == "set_seat_heating":
        level = clamp_int(kwargs["level"], 0, 3)
        seat_zone = kwargs.get("seat_zone", "DRIVER")
        positions = occupied_positions_for_zone(seat_zone, seats_occupied)
        return [
            {
                "name": "seat_set_heating",
                "arguments": {
                    "position": position,
                    "level": level,
                },
            }
            for position in positions
        ]

    return None


def normalize_task_record(record: dict, source_config: str, source_split: str) -> tuple[dict | None, str | None]:
    actions = json.loads(record["actions"])
    context = json.loads(record["context_init_config"])
    task_type = record["task_type"]

    if task_type not in DIRECT_TASK_TYPES:
        return None, f"task_type:{task_type}"

    mapped_tool_calls: list[dict] = []
    unsupported_actions: list[str] = []
    for action in actions:
        mapped = map_action(action, context)
        if not mapped:
            unsupported_actions.append(action["name"])
            continue
        mapped_tool_calls.extend(mapped)

    if unsupported_actions:
        return None, f"unsupported_actions:{','.join(sorted(set(unsupported_actions)))}"
    if not mapped_tool_calls:
        return None, "no_supported_actions"

    category = infer_category(mapped_tool_calls)
    behavior = "tool_call"
    domains_loaded = sorted({tool_call["name"].split("_", 1)[0] for tool_call in mapped_tool_calls})
    loaded_tool_names = []
    for tool_call in mapped_tool_calls:
        if tool_call["name"] not in loaded_tool_names:
            loaded_tool_names.append(tool_call["name"])
    vehicle_state = infer_vehicle_state(record["instruction"], context)
    risk = infer_risk(domains_loaded, vehicle_state)
    system_prompt = build_system_prompt(loaded_tool_names, vehicle_state)
    messages = [
        {"role": "user", "content": record["instruction"]},
        {"role": "assistant", "content": "", "tool_calls": mapped_tool_calls},
    ]

    sample = {
        "id": f"car-bench-{record['task_id']}",
        "category": category,
        "behavior": behavior,
        "risk": risk,
        "vehicle_state": vehicle_state,
        "domains_loaded": domains_loaded,
        "loaded_tool_names": loaded_tool_names,
        "system_prompt": system_prompt,
        "messages": messages,
        "meta": {
            "prompt_token_count": len(system_prompt),
            "generator_model": "car-bench/import-v1",
            "adversarial": task_type.startswith("hallucination"),
            "seed_anchor_id": record["task_id"],
        },
        "sft_text": build_sft_text(system_prompt, messages),
        "source": {
            "dataset": "car-bench",
            "config": source_config,
            "split": source_split,
            "task_id": record["task_id"],
            "task_type": task_type,
            "persona": record.get("persona", ""),
            "calendar_id": record.get("calendar_id"),
        },
        "source_actions": actions,
        "source_context_init_config": context,
    }
    return sample, None


def download_raw_file(relative_path: str, destination: Path, refresh: bool) -> None:
    if destination.exists() and not refresh:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    url = f"{RAW_BASE_URL}/{relative_path}"
    with urllib.request.urlopen(url, timeout=60) as response:
        destination.write_bytes(response.read())


def load_records(path: Path, max_rows: int | None) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if max_rows is not None and index >= max_rows:
                break
            if not line.strip():
                continue
            records.append(json.loads(line))
    return records


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def build_summary(
    total_records: int,
    normalized_samples: list[dict],
    source_config_counts: Counter,
    task_type_counts: Counter,
    mapped_action_counts: Counter,
    skip_reasons: Counter,
) -> dict:
    return {
        "total_records": total_records,
        "normalized_sample_count": len(normalized_samples),
        "source_config_counts": dict(sorted(source_config_counts.items())),
        "source_task_type_counts": dict(sorted(task_type_counts.items())),
        "mapped_action_counts": dict(sorted(mapped_action_counts.items())),
        "skip_reason_counts": dict(sorted(skip_reasons.items())),
        "category_counts": dict(sorted(Counter(sample["category"] for sample in normalized_samples).items())),
        "domain_counts": dict(
            sorted(Counter(domain for sample in normalized_samples for domain in sample["domains_loaded"]).items())
        ),
        "risk_counts": dict(sorted(Counter(sample["risk"] for sample in normalized_samples).items())),
        "behavior_counts": dict(sorted(Counter(sample["behavior"] for sample in normalized_samples).items())),
    }


def write_summary_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# CAR-Bench Import Summary",
        "",
        f"- total_records: `{summary['total_records']}`",
        f"- normalized_sample_count: `{summary['normalized_sample_count']}`",
        "",
        "## Category Counts",
        "",
    ]
    for key, value in summary["category_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Risk Counts", ""])
    for key, value in summary["risk_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Skip Reasons", ""])
    for key, value in summary["skip_reason_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a minimal CAR-Bench preview into finetune-lab.")
    parser.add_argument(
        "--raw-output-dir",
        default="data/public-source/car-bench",
        help="Directory to store raw CAR-Bench task files.",
    )
    parser.add_argument(
        "--normalized-output-dir",
        default="data/public-normalized/car-bench-v1",
        help="Directory to store normalized mapping-preview files.",
    )
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["tasks_base", "tasks_disambiguation", "tasks_hallucination"],
        choices=sorted(TASK_CONFIGS),
        help="CAR-Bench task configs to download.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train"],
        choices=["train", "test"],
        help="Splits to download and normalize.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional per-file row cap for smoke importing.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download raw source files even if they already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_output_dir = Path(args.raw_output_dir)
    normalized_output_dir = Path(args.normalized_output_dir)
    normalized_samples: list[dict] = []
    total_records = 0
    source_config_counts: Counter = Counter()
    task_type_counts: Counter = Counter()
    mapped_action_counts: Counter = Counter()
    skip_reasons: Counter = Counter()

    for config in args.configs:
        for split in args.splits:
            relative_path = TASK_CONFIGS[config][split]
            raw_path = raw_output_dir / config / f"{split}.jsonl"
            download_raw_file(relative_path, raw_path, refresh=args.refresh)
            records = load_records(raw_path, args.max_rows)
            total_records += len(records)
            source_config_counts[f"{config}:{split}"] += len(records)
            for record in records:
                task_type_counts[record["task_type"]] += 1
                normalized_sample, skip_reason = normalize_task_record(record, config, split)
                if normalized_sample is None:
                    skip_reasons[skip_reason or "unknown"] += 1
                    continue
                normalized_samples.append(normalized_sample)
                for action in normalized_sample["source_actions"]:
                    mapped_action_counts[action["name"]] += 1

    normalized_output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(normalized_output_dir / "samples.jsonl", normalized_samples)
    summary = build_summary(
        total_records=total_records,
        normalized_samples=normalized_samples,
        source_config_counts=source_config_counts,
        task_type_counts=task_type_counts,
        mapped_action_counts=mapped_action_counts,
        skip_reasons=skip_reasons,
    )
    (normalized_output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_markdown(normalized_output_dir / "summary.md", summary)
    _write_governance_artifacts(normalized_output_dir, len(normalized_samples))


def _write_governance_artifacts(output_dir: Path, total: int) -> None:
    try:
        import governance as g
    except ImportError:  # pragma: no cover
        from . import governance as g  # type: ignore
    name = output_dir.name
    manifest = g.DatasetCardManifest(
        name=name,
        version=name.split("-")[-1] if "-" in name else "1.0",
        generator="public-import-car-bench",
        license="see upstream car-bench license (review before redistribution)",
        sensitivity="medium",
        description=(
            f"公开数据集导入：car-bench → `{name}`。来自外部公开 benchmark，"
            "尽管已脱敏正则扫描，分发前需复核 upstream license。"
        ),
        provenance=[
            "上游：data/public-source/car-bench（按 import_car_bench.py 规范化）",
            "导入脚本：training/data_pipeline/import_car_bench.py",
        ],
        known_limitations=[
            "外部数据，可能含未识别的人名 / 地址等非结构化 PII",
            "默认 redaction policy 只扫 phone / id / plate / email",
            "如果上游升级，需要重跑 dataset-governance 刷新报告",
        ],
    )
    g.governance_pass(
        output_dir,
        manifest,
        primary_jsonl="samples.jsonl",
        splits_jsonl={"samples": "samples.jsonl"},
    )


if __name__ == "__main__":
    main()
