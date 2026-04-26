from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from adversarial import mark_adversarial
from formatter import build_sft_text
from generator import RuleBasedProvider
from schema_sampler import load_schema, sample_loaded_tools
from validator import validate_samples


CATEGORY_TARGETS = [
    ("single_domain_single_tool", 30),
    ("single_domain_multi_tool_chain", 15),
    ("cross_domain_multi_tool", 15),
    ("reroute_to_meta", 10),
    ("full_tool_fallback", 10),
    ("proactive_event_driven", 10),
    ("confirm_required_action", 5),
    ("reject_unsafe_action", 5),
]

CATEGORY_BEHAVIOR = {
    "single_domain_single_tool": "tool_call",
    "single_domain_multi_tool_chain": "tool_call",
    "cross_domain_multi_tool": "tool_call",
    "reroute_to_meta": "handoff",
    "full_tool_fallback": "clarify",
    "proactive_event_driven": "tool_call",
    "confirm_required_action": "confirm",
    "reject_unsafe_action": "reject",
}

RISK_LEVELS = {
    "low": 0,
    "medium": 1,
    "high": 2,
}

DOMAIN_RISK = {
    "hvac": "low",
    "seat": "low",
    "window": "medium",
    "door": "high",
}


DOMAIN_PROMPTS = {
    "hvac": ("冷死了，主驾调到24度", {"name": "hvac_set_temperature", "arguments": {"zone": "driver", "celsius": 24}}),
    "window": ("开点窗，前排留条缝", {"name": "window_set_open_percent", "arguments": {"position": "all", "percent": 15}}),
    "seat": ("副驾座椅加热开2档", {"name": "seat_set_heating", "arguments": {"position": "passenger", "level": 2}}),
    "door": ("把车门都锁上", {"name": "door_set_lock", "arguments": {"position": "all", "locked": True}}),
}

REROUTE_PROMPTS = [
    ("车里太闷了，想透透气", "window"),
    ("车里太冷了，想把空调调暖一点", "hvac"),
    ("我想把门都锁上", "door"),
]

SINGLE_DOMAIN_MULTI_TOOL_CHAIN_VARIANTS = [
    (
        "主驾空调调到24度，风速开3档",
        [
            {"name": "hvac_set_temperature", "arguments": {"zone": "driver", "celsius": 24}},
            {"name": "hvac_set_fan_speed", "arguments": {"zone": "driver", "level": 3}},
        ],
    ),
    (
        "副驾温度降到20度，风速调到4档",
        [
            {"name": "hvac_set_temperature", "arguments": {"zone": "passenger", "celsius": 20}},
            {"name": "hvac_set_fan_speed", "arguments": {"zone": "passenger", "level": 4}},
        ],
    ),
    (
        "后排空调设到22度，风量开2档",
        [
            {"name": "hvac_set_temperature", "arguments": {"zone": "rear", "celsius": 22}},
            {"name": "hvac_set_fan_speed", "arguments": {"zone": "rear", "level": 2}},
        ],
    ),
]

CONFIRM_ACTION_VARIANTS = [
    {
        "prompt_user": "把所有车窗都打开",
        "domains": ["window"],
        "tool_calls": [],
        "assistant_content": "当前车辆可能在行驶中。打开所有车窗前需要你确认。",
        "expected_system_action": {
            "type": "create_pending_confirmation",
            "tool": "window_set_open_percent",
            "arguments": {"position": "all", "percent": 100},
            "expires_in_seconds": 60,
        },
        "vehicle_state": {"speed_kph": 30, "power_state": "driving"},
        "risk": "high",
    },
    {
        "prompt_user": "把车门都解锁",
        "domains": ["door"],
        "tool_calls": [],
        "assistant_content": "当前车辆状态下，执行车门解锁前需要你确认。",
        "expected_system_action": {
            "type": "create_pending_confirmation",
            "tool": "door_set_lock",
            "arguments": {"position": "all", "locked": False},
            "expires_in_seconds": 60,
        },
        "vehicle_state": {"speed_kph": 12, "power_state": "driving"},
        "risk": "high",
    },
]

REJECT_ACTION_VARIANTS = [
    {
        "prompt_user": "行驶中把车门都解锁",
        "domains": ["door"],
        "tool_calls": [],
        "assistant_content": "车辆行驶中不能执行车门解锁操作。",
        "expected_system_action": {
            "type": "refuse_execution",
            "reason_code": "unsafe_vehicle_state",
        },
        "vehicle_state": {"speed_kph": 45, "power_state": "driving"},
        "risk": "high",
    },
    {
        "prompt_user": "高速上把所有车窗全打开",
        "domains": ["window"],
        "tool_calls": [],
        "assistant_content": "当前车速过高，不能直接执行全开车窗操作。",
        "expected_system_action": {
            "type": "refuse_execution",
            "reason_code": "unsafe_vehicle_state",
        },
        "vehicle_state": {"speed_kph": 96, "power_state": "driving"},
        "risk": "high",
    },
]

DEFAULT_VEHICLE_STATE = {
    "speed_kph": 0,
    "power_state": "parked",
}


def risk_for_domains(domains: list[str]) -> str:
    highest = "low"
    for domain in domains:
        candidate = DOMAIN_RISK.get(domain, "low")
        if RISK_LEVELS[candidate] > RISK_LEVELS[highest]:
            highest = candidate
    return highest


def infer_vehicle_state(category: str, domains: list[str], offset: int, event: dict | None = None) -> dict:
    primary_domain = domains[0] if domains else "hvac"
    if category == "proactive_event_driven" and event:
        event_profiles = {
            "evt-cabin-cold": {"speed_kph": 42, "power_state": "driving"},
            "evt-window-rain": {"speed_kph": 48, "power_state": "driving"},
            "evt-seat-cold": {"speed_kph": 26, "power_state": "driving"},
            "evt-door-open": {"speed_kph": 0, "power_state": "parked"},
        }
        return event_profiles.get(event["id"], {"speed_kph": 18, "power_state": "driving"})
    if category == "full_tool_fallback":
        return {"speed_kph": 0, "power_state": "parked"}
    if primary_domain == "door":
        return {"speed_kph": 0, "power_state": "parked"}
    if primary_domain == "window":
        return {"speed_kph": 0 if offset % 2 == 0 else 6, "power_state": "parked"}
    if primary_domain == "seat":
        return {"speed_kph": 0 if offset % 2 == 0 else 22, "power_state": "parked" if offset % 2 == 0 else "driving"}
    if primary_domain == "hvac":
        return {"speed_kph": 0 if offset % 3 == 0 else 38, "power_state": "parked" if offset % 3 == 0 else "driving"}
    return DEFAULT_VEHICLE_STATE


def build_system_prompt(loaded_tools: list[dict], vehicle_state: dict, event: dict | None = None) -> str:
    lines = [
        "你是车机工具调用助手，只能从已加载工具中选择。",
        f"loaded_tool_names={','.join(tool['name'] for tool in loaded_tools)}",
        "vehicle_state:",
        json.dumps(vehicle_state, ensure_ascii=False),
    ]
    if event:
        lines.append("event_context:")
        lines.append(json.dumps(event, ensure_ascii=False))
    return "\n".join(lines)


def build_sample(sample_id: int, category: str, loaded_tools: list[dict], user_prompt: str, tool_calls: list[dict], provider_name: str, vehicle_state: dict, risk: str, event: dict | None = None, assistant_content: str | None = None, expected_system_action: dict | None = None) -> dict:
    behavior = CATEGORY_BEHAVIOR[category]
    messages = []
    if category != "proactive_event_driven":
        messages.append({"role": "user", "content": user_prompt})
    assistant_message = {"role": "assistant", "content": assistant_content or ""}
    if tool_calls:
        assistant_message["tool_calls"] = tool_calls
    messages.append(assistant_message)
    system_prompt = build_system_prompt(loaded_tools, vehicle_state, event=event)
    sample = {
        "id": f"sft-v1-{sample_id:04d}",
        "category": category,
        "behavior": behavior,
        "risk": risk,
        "vehicle_state": vehicle_state,
        "domains_loaded": sorted({name.split("_", 1)[0].replace("window", "window") for name in [tool["name"] for tool in loaded_tools] if not name.startswith("_meta")}),
        "loaded_tool_names": [tool["name"] for tool in loaded_tools],
        "system_prompt": system_prompt,
        "messages": messages,
        "meta": {
            "prompt_token_count": len(system_prompt),
            "generator_model": provider_name,
            "adversarial": False,
            "seed_anchor_id": None,
        },
        "sft_text": build_sft_text(system_prompt, messages),
    }
    if event:
        sample["event"] = event
    if expected_system_action:
        sample["expected_system_action"] = expected_system_action
    return sample


def scaled_category_targets(multiplier: int) -> list[tuple[str, int]]:
    return [(category, target * multiplier) for category, target in CATEGORY_TARGETS]


def generate_samples(multiplier: int = 1) -> list[dict]:
    schema = load_schema()
    provider = RuleBasedProvider()
    samples: list[dict] = []
    sample_id = 1
    domains = ["hvac", "window", "seat", "door"]

    for category, target in scaled_category_targets(multiplier):
        for offset in range(target):
            domain = domains[offset % len(domains)]
            loaded_tools = sample_loaded_tools(schema, [domain], include_meta=category in {"reroute_to_meta", "full_tool_fallback"})
            prompt, tool_call = DOMAIN_PROMPTS[domain]

            if category == "single_domain_single_tool":
                tool_calls = [tool_call]
                target_domains = [domain]
            elif category == "single_domain_multi_tool_chain":
                loaded_tools = sample_loaded_tools(schema, ["hvac"], include_meta=False)
                prompt, tool_calls = SINGLE_DOMAIN_MULTI_TOOL_CHAIN_VARIANTS[offset % len(SINGLE_DOMAIN_MULTI_TOOL_CHAIN_VARIANTS)]
                target_domains = ["hvac"]
            elif category == "cross_domain_multi_tool":
                other_domain = domains[(offset + 1) % len(domains)]
                loaded_tools = sample_loaded_tools(schema, [domain, other_domain], include_meta=True)
                prompt = f"{prompt}，顺便把{other_domain}也处理一下"
                tool_calls = [tool_call, DOMAIN_PROMPTS[other_domain][1]]
                target_domains = [domain, other_domain]
            elif category == "reroute_to_meta":
                wrong_domain = domains[(offset + 1) % len(domains)]
                loaded_tools = sample_loaded_tools(schema, [wrong_domain], include_meta=True)
                prompt, suggested = REROUTE_PROMPTS[offset % len(REROUTE_PROMPTS)]
                tool_calls = [{"name": "_meta_reroute", "arguments": {"suggested_domains": [suggested], "reason": "loaded tools do not match intent"}}]
                target_domains = [suggested]
            elif category == "full_tool_fallback":
                loaded_tools = sample_loaded_tools(schema, domains, include_meta=True)
                prompt = "把车里弄舒服一点"
                tool_calls = [{"name": "_meta_reroute", "arguments": {"suggested_domains": ["hvac", "window"], "reason": "request is too broad for a single deterministic tool path"}}]
                target_domains = ["hvac", "window"]
            elif category == "confirm_required_action":
                variant = CONFIRM_ACTION_VARIANTS[offset % len(CONFIRM_ACTION_VARIANTS)]
                loaded_tools = sample_loaded_tools(schema, variant["domains"], include_meta=True)
                prompt = variant["prompt_user"]
                tool_calls = variant["tool_calls"]
                target_domains = variant["domains"]
                vehicle_state = variant["vehicle_state"]
                risk = variant["risk"]
                sample = build_sample(
                    sample_id,
                    category,
                    loaded_tools,
                    prompt,
                    tool_calls,
                    provider.provider_name,
                    vehicle_state,
                    risk,
                    assistant_content=variant["assistant_content"],
                    expected_system_action=variant["expected_system_action"],
                )
                samples.append(mark_adversarial(sample, adversarial=False))
                sample_id += 1
                continue
            elif category == "reject_unsafe_action":
                variant = REJECT_ACTION_VARIANTS[offset % len(REJECT_ACTION_VARIANTS)]
                loaded_tools = sample_loaded_tools(schema, variant["domains"], include_meta=True)
                prompt = variant["prompt_user"]
                tool_calls = variant["tool_calls"]
                target_domains = variant["domains"]
                vehicle_state = variant["vehicle_state"]
                risk = variant["risk"]
                sample = build_sample(
                    sample_id,
                    category,
                    loaded_tools,
                    prompt,
                    tool_calls,
                    provider.provider_name,
                    vehicle_state,
                    risk,
                    assistant_content=variant["assistant_content"],
                    expected_system_action=variant["expected_system_action"],
                )
                samples.append(mark_adversarial(sample, adversarial=False))
                sample_id += 1
                continue
            else:
                event = schema["events"][offset % len(schema["events"])]
                event_domain = event["domain"]
                loaded_tools = sample_loaded_tools(schema, [event_domain], include_meta=True)
                event_prompt, event_tool = DOMAIN_PROMPTS[event_domain]
                vehicle_state = infer_vehicle_state(category, [event_domain], offset, event=event)
                risk = risk_for_domains([event_domain])
                sample = build_sample(
                    sample_id,
                    category,
                    loaded_tools,
                    event_prompt,
                    [event_tool],
                    provider.provider_name,
                    vehicle_state,
                    risk,
                    event=event,
                    assistant_content=f"检测到事件：{event['description']}，我先帮你处理。",
                )
                samples.append(sample)
                sample_id += 1
                continue

            vehicle_state = infer_vehicle_state(category, target_domains, offset)
            risk = risk_for_domains(target_domains)
            sample = build_sample(sample_id, category, loaded_tools, prompt, tool_calls, provider.provider_name, vehicle_state, risk)
            samples.append(mark_adversarial(sample, adversarial=False))
            sample_id += 1
    return samples


def split_samples(samples: list[dict], held_out_ratio: float = 0.2) -> tuple[list[dict], list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for sample in samples:
        grouped.setdefault(sample["category"], []).append(sample)

    train_samples: list[dict] = []
    held_out_samples: list[dict] = []
    for category, category_samples in grouped.items():
        _ = category
        held_out_count = max(1, round(len(category_samples) * held_out_ratio))
        split_index = len(category_samples) - held_out_count
        train_samples.extend(category_samples[:split_index])
        held_out_samples.extend(category_samples[split_index:])

    return train_samples, held_out_samples


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def build_summary_payload(
    samples: list[dict],
    train_samples: list[dict],
    held_out_samples: list[dict],
    output_dir: Path,
    multiplier: int,
    held_out_ratio: float,
    errors: list[str],
) -> dict:
    category_counts = Counter(sample["category"] for sample in samples)
    behavior_counts = Counter(sample["behavior"] for sample in samples)
    risk_counts = Counter(sample["risk"] for sample in samples)
    system_action_counts = Counter(
        sample["expected_system_action"]["type"]
        for sample in samples
        if sample.get("expected_system_action")
    )
    train_counts = Counter(sample["category"] for sample in train_samples)
    held_out_counts = Counter(sample["category"] for sample in held_out_samples)
    loaded_tool_count_total = sum(len(sample["loaded_tool_names"]) for sample in samples)
    expected_tool_call_total = sum(len(sample["messages"][-1].get("tool_calls", [])) for sample in samples)
    multi_tool_count = sum(1 for sample in samples if len(sample["messages"][-1].get("tool_calls", [])) > 1)
    event_driven_count = sum(1 for sample in samples if sample["category"] == "proactive_event_driven")
    return {
        "title": "SFT dataset summary",
        "output_dir": str(output_dir),
        "multiplier": multiplier,
        "held_out_ratio": held_out_ratio,
        "counts": {
            "total": len(samples),
            "train": len(train_samples),
            "held_out": len(held_out_samples),
        },
        "shape": {
            "avg_loaded_tool_count": round(loaded_tool_count_total / max(len(samples), 1), 2),
            "avg_expected_tool_call_count": round(expected_tool_call_total / max(len(samples), 1), 2),
            "multi_tool_sample_count": multi_tool_count,
            "event_driven_sample_count": event_driven_count,
        },
        "categories": {
            category: {
                "total": category_counts.get(category, 0),
                "train": train_counts.get(category, 0),
                "held_out": held_out_counts.get(category, 0),
            }
            for category, _ in CATEGORY_TARGETS
        },
        "behaviors": {
            behavior: count
            for behavior, count in behavior_counts.items()
        },
        "risks": {
            risk: count
            for risk, count in risk_counts.items()
        },
        "expected_system_actions": {
            action_type: count
            for action_type, count in system_action_counts.items()
        },
        "validation": {
            "valid_count": len(samples) - len(errors),
            "error_count": len(errors),
            "errors": errors,
        },
    }


def write_summary(summary_path_base: Path, summary: dict) -> None:
    (summary_path_base.with_suffix(".json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_lines = [
        "# Dataset Summary",
        "",
        f"- total_samples: {summary['counts']['total']}",
        f"- train_samples: {summary['counts']['train']}",
        f"- held_out_samples: {summary['counts']['held_out']}",
        f"- multiplier: {summary['multiplier']}",
        f"- held_out_ratio: {summary['held_out_ratio']}",
        f"- avg_loaded_tool_count: {summary['shape']['avg_loaded_tool_count']}",
        f"- avg_expected_tool_call_count: {summary['shape']['avg_expected_tool_call_count']}",
        f"- multi_tool_sample_count: {summary['shape']['multi_tool_sample_count']}",
        f"- event_driven_sample_count: {summary['shape']['event_driven_sample_count']}",
        f"- schema_valid_rate: {summary['validation']['valid_count']}/{summary['counts']['total']}",
        "",
        "## Category Counts",
        "",
    ]
    for category, counts in summary["categories"].items():
        report_lines.append(f"- {category}: total={counts['total']} train={counts['train']} held_out={counts['held_out']}")
    report_lines.extend(["", "## Train / Held-out Split", ""])
    for category, counts in summary["categories"].items():
        report_lines.append(f"- {category}: train={counts['train']} held_out={counts['held_out']}")
    report_lines.extend(["", "## Behavior Counts", ""])
    for behavior, count in summary["behaviors"].items():
        report_lines.append(f"- {behavior}: {count}")
    report_lines.extend(["", "## Risk Counts", ""])
    for risk, count in summary["risks"].items():
        report_lines.append(f"- {risk}: {count}")
    report_lines.extend(["", "## Expected System Actions", ""])
    if summary["expected_system_actions"]:
        for action_type, count in summary["expected_system_actions"].items():
            report_lines.append(f"- {action_type}: {count}")
    else:
        report_lines.append("- none")
    report_lines.extend(["", "## Validation Errors", ""])
    if summary["validation"]["errors"]:
        report_lines.extend(f"- {error}" for error in summary["validation"]["errors"])
    else:
        report_lines.append("- none")
    (summary_path_base.with_suffix(".md")).write_text("\n".join(report_lines) + "\n", encoding="utf-8")


def write_outputs(samples: list[dict], output_dir: Path, multiplier: int = 1, held_out_ratio: float = 0.2) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    train_samples, held_out_samples = split_samples(samples, held_out_ratio=held_out_ratio)
    samples_path = output_dir / "samples.jsonl"
    train_path = output_dir / "train.jsonl"
    held_out_path = output_dir / "held-out.jsonl"
    write_jsonl(samples_path, samples)
    write_jsonl(train_path, train_samples)
    write_jsonl(held_out_path, held_out_samples)
    errors = validate_samples(samples)
    summary = build_summary_payload(
        samples,
        train_samples,
        held_out_samples,
        output_dir,
        multiplier,
        held_out_ratio,
        errors,
    )
    write_summary(output_dir / "dataset_summary", summary)
    # Keep the old report path so existing workflows and docs continue to work.
    (output_dir / "validation_report.md").write_text((output_dir / "dataset_summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    _write_governance_artifacts(output_dir, samples, train_samples, held_out_samples)


def _write_governance_artifacts(output_dir: Path, samples: list[dict], train: list[dict], held_out: list[dict]) -> None:
    """Emit dataset-card.md + redaction-report.md alongside the existing artifacts."""
    try:
        import governance as g
    except ImportError:  # pragma: no cover — relative path edge case in some test runners
        from . import governance as g  # type: ignore
    name = output_dir.name
    generators = sorted({(s.get("meta") or {}).get("generator_model", "unknown") for s in samples})
    generator = f"synthetic-{generators[0]}" if generators else "synthetic-unknown"
    manifest = g.DatasetCardManifest(
        name=name,
        version=name.split("-")[0] if name.startswith("v") else "1.0",
        generator=generator,
        license="internal-research-only",
        sensitivity="low",
        description=(
            f"SFT 数据集 `{name}`：合成的车控 tool-call 样本，用于 LoRA 微调教学，"
            "不可作为真实车机训练集。"
        ),
        provenance=[
            "生成器：training/data_pipeline/pipeline.py + schema_sampler + generator",
            "种子：seed-anchor schema v1（合成数据，不含真实用户对话）",
            f"数据目录：{output_dir}",
        ],
        known_limitations=[
            "合成数据无法覆盖真实方言、口语化、跨说法",
            "上线前必须用真实样本回归",
        ],
    )
    g.governance_pass(
        output_dir,
        manifest,
        primary_jsonl="samples.jsonl",
        splits_jsonl={
            "samples": "samples.jsonl",
            "train": "train.jsonl",
            "held-out": "held-out.jsonl",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/sft/v1-seed-anchor-demo"))
    parser.add_argument("--multiplier", type=int, default=1)
    parser.add_argument("--held-out-ratio", type=float, default=0.2)
    args = parser.parse_args()
    if args.multiplier < 1:
        raise SystemExit("--multiplier must be >= 1")
    if not 0 < args.held_out_ratio < 1:
        raise SystemExit("--held-out-ratio must be between 0 and 1")
    samples = generate_samples(multiplier=args.multiplier)
    write_outputs(samples, args.output_dir, multiplier=args.multiplier, held_out_ratio=args.held_out_ratio)


if __name__ == "__main__":
    main()
