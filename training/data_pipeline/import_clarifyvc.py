from __future__ import annotations

import argparse
import json
import urllib.request
from collections import Counter
from pathlib import Path

from formatter import build_sft_text


OPENREVIEW_FORUM_URL = "https://openreview.net/forum?id=afO3vnSNsS"
OPENREVIEW_PDF_URL = "https://openreview.net/pdf?id=afO3vnSNsS"

SUPPORTED_DOMAINS = {"hvac", "window", "seat", "lighting", "navigation", "media"}
WINDOW_POSITION_MAP = {
    "front-left": "front_left",
    "front-right": "front_right",
    "rear-left": "rear_left",
    "rear-right": "rear_right",
}

PROTOCOL_SEED_EXAMPLES = [
    {
        "id": "clarifyvc-tier1-hvac-direct",
        "tier": "tier1_single_turn_structured_parsing",
        "task_type": "single_turn_structured_parsing",
        "domain": "hvac",
        "variation_category": "direct_commands",
        "instruction": "Set AC to 22°.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "low",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "hvac_set_temperature",
                "arguments": {"zone": "driver", "celsius": 22},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 3 Tier 1 + Table 4 direct commands",
    },
    {
        "id": "clarifyvc-tier1-window-spatial",
        "tier": "tier1_single_turn_structured_parsing",
        "task_type": "single_turn_structured_parsing",
        "domain": "window",
        "variation_category": "spatial_references",
        "instruction": "Open the rear-right window.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "medium",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "window_set_open_percent",
                "arguments": {"position": "rear_right", "percent": 100},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 4 spatial references + Table 9 windows example",
    },
    {
        "id": "clarifyvc-tier2-hvac-intensity",
        "tier": "tier2_ambiguity_detection_and_clarification",
        "task_type": "ambiguity_detection_and_clarification",
        "domain": "hvac",
        "variation_category": "subjective_modifiers",
        "ambiguity_type": "intensity_ambiguity",
        "instruction": "Make it a bit cooler.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 18, "power_state": "driving"},
        "risk": "medium",
        "behavior": "clarify",
        "tool_calls": [],
        "assistant_content": "你想调到多少度？",
        "paper_anchor": "Table 5 intensity ambiguity",
    },
    {
        "id": "clarifyvc-tier2-window-entity",
        "tier": "tier2_ambiguity_detection_and_clarification",
        "task_type": "ambiguity_detection_and_clarification",
        "domain": "window",
        "variation_category": "referential_ambiguity",
        "ambiguity_type": "entity_ambiguity",
        "instruction": "Open it.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "medium",
        "behavior": "clarify",
        "tool_calls": [],
        "assistant_content": "你想打开哪一扇窗？",
        "paper_anchor": "Table 5 entity ambiguity",
    },
    {
        "id": "clarifyvc-tier2-seat-mode",
        "tier": "tier2_ambiguity_detection_and_clarification",
        "task_type": "ambiguity_detection_and_clarification",
        "domain": "seat",
        "variation_category": "mode_ambiguity",
        "ambiguity_type": "mode_ambiguity",
        "instruction": "Heat my seat.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "low",
        "behavior": "clarify",
        "tool_calls": [],
        "assistant_content": "你想加热哪一个座椅，开到几档？",
        "paper_anchor": "Table 9 seat example + Table 5 mode ambiguity",
    },
    {
        "id": "clarifyvc-tier3-hvac-multi-turn",
        "tier": "tier3_multi_turn_dialogue_grounding",
        "task_type": "multi_turn_dialogue_grounding",
        "domain": "hvac",
        "variation_category": "context_dependent_follow_up",
        "instruction": "It's too hot in here.",
        "dialogue_history": [
            {"role": "user", "content": "It's too hot in here."},
            {"role": "assistant", "content": "What exact temperature would you like?"},
            {"role": "user", "content": "Set AC to 22°."},
        ],
        "vehicle_state": {"speed_kph": 24, "power_state": "driving"},
        "risk": "low",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "hvac_set_temperature",
                "arguments": {"zone": "driver", "celsius": 22},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 3 Tier 3 + Appendix B MEA prompt",
    },
    {
        "id": "clarifyvc-tier1-lighting-direct",
        "tier": "tier1_single_turn_structured_parsing",
        "task_type": "single_turn_structured_parsing",
        "domain": "lighting",
        "variation_category": "direct_commands",
        "instruction": "Turn on ambient lights.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "low",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "lighting_set_ambient",
                "arguments": {"on": True, "color": "purple"},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 9 lighting example",
    },
    {
        "id": "clarifyvc-tier1-navigation-direct",
        "tier": "tier1_single_turn_structured_parsing",
        "task_type": "single_turn_structured_parsing",
        "domain": "navigation",
        "variation_category": "direct_commands",
        "instruction": "Take me to the nearest station.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "low",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "navigation_set_destination",
                "arguments": {"destination_query": "nearest station"},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 9 navigation example",
    },
    {
        "id": "clarifyvc-tier1-media-direct",
        "tier": "tier1_single_turn_structured_parsing",
        "task_type": "single_turn_structured_parsing",
        "domain": "media",
        "variation_category": "direct_commands",
        "instruction": "Play my jazz playlist.",
        "dialogue_history": [],
        "vehicle_state": {"speed_kph": 0, "power_state": "parked"},
        "risk": "low",
        "behavior": "tool_call",
        "tool_calls": [
            {
                "name": "media_play_content",
                "arguments": {"query": "jazz playlist", "source": "playlist"},
            }
        ],
        "assistant_content": "",
        "paper_anchor": "Table 9 media example",
    },
]


def build_system_prompt(loaded_tool_names: list[str], vehicle_state: dict, tier: str) -> str:
    return "\n".join(
        [
            "你是车机工具调用助手，只能从已加载工具中选择。",
            f"clarifyvc_tier={tier}",
            f"loaded_tool_names={','.join(loaded_tool_names)}",
            "vehicle_state:",
            json.dumps(vehicle_state, ensure_ascii=False),
        ]
    )


def default_loaded_tool_names(domain: str) -> list[str]:
    if domain == "hvac":
        return ["hvac_set_temperature"]
    if domain == "window":
        return ["window_set_open_percent"]
    if domain == "seat":
        return ["seat_set_heating"]
    if domain == "lighting":
        return ["lighting_set_ambient"]
    if domain == "navigation":
        return ["navigation_set_destination"]
    if domain == "media":
        return ["media_play_content"]
    return []


def infer_category(record: dict) -> str:
    tier = record["tier"]
    if tier == "tier1_single_turn_structured_parsing":
        return "clarifyvc_tier1_single_turn_structured_parsing"
    if tier == "tier2_ambiguity_detection_and_clarification":
        return "clarifyvc_tier2_ambiguity_detection_and_clarification"
    return "clarifyvc_tier3_multi_turn_dialogue_grounding"


def normalize_protocol_record(record: dict) -> tuple[dict | None, str | None]:
    if record["domain"] not in SUPPORTED_DOMAINS:
        return None, f"unsupported_domain:{record['domain']}"

    behavior = record["behavior"]
    if record.get("tool_calls"):
        loaded_tool_names = list(dict.fromkeys(call["name"] for call in record["tool_calls"]))
    else:
        loaded_tool_names = default_loaded_tool_names(record["domain"])
    if not loaded_tool_names:
        return None, f"missing_loaded_tools:{record['domain']}"

    system_prompt = build_system_prompt(loaded_tool_names, record["vehicle_state"], record["tier"])
    messages = list(record.get("dialogue_history", []))
    if not messages:
        messages.append({"role": "user", "content": record["instruction"]})
    assistant_message = {"role": "assistant", "content": record.get("assistant_content", "")}
    if record.get("tool_calls"):
        assistant_message["tool_calls"] = record["tool_calls"]
    messages.append(assistant_message)

    sample = {
        "id": record["id"],
        "category": infer_category(record),
        "behavior": behavior,
        "risk": record["risk"],
        "vehicle_state": record["vehicle_state"],
        "domains_loaded": [record["domain"]],
        "loaded_tool_names": loaded_tool_names,
        "system_prompt": system_prompt,
        "messages": messages,
        "meta": {
            "prompt_token_count": len(system_prompt),
            "generator_model": "clarifyvc/protocol-import-v1",
            "adversarial": False,
            "seed_anchor_id": record["id"],
        },
        "sft_text": build_sft_text(system_prompt, messages),
        "source": {
            "dataset": "clarifyvc",
            "source_type": "paper_protocol_seed",
            "forum_url": OPENREVIEW_FORUM_URL,
            "paper_pdf_url": OPENREVIEW_PDF_URL,
            "tier": record["tier"],
            "task_type": record["task_type"],
            "variation_category": record.get("variation_category"),
            "ambiguity_type": record.get("ambiguity_type"),
            "paper_anchor": record["paper_anchor"],
        },
    }
    return sample, None


def download(url: str, destination: Path, refresh: bool) -> None:
    if destination.exists() and not refresh:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 Codex ClarifyVC Importer"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def build_summary(total_records: int, normalized_samples: list[dict], skip_reasons: Counter, protocol_seeds: list[dict]) -> dict:
    return {
        "total_records": total_records,
        "normalized_sample_count": len(normalized_samples),
        "tier_counts": dict(sorted(Counter(seed["tier"] for seed in protocol_seeds).items())),
        "raw_domain_counts": dict(sorted(Counter(seed["domain"] for seed in protocol_seeds).items())),
        "raw_behavior_counts": dict(sorted(Counter(seed["behavior"] for seed in protocol_seeds).items())),
        "skip_reason_counts": dict(sorted(skip_reasons.items())),
        "normalized_category_counts": dict(sorted(Counter(sample["category"] for sample in normalized_samples).items())),
        "normalized_domain_counts": dict(
            sorted(Counter(domain for sample in normalized_samples for domain in sample["domains_loaded"]).items())
        ),
        "normalized_behavior_counts": dict(sorted(Counter(sample["behavior"] for sample in normalized_samples).items())),
        "normalized_risk_counts": dict(sorted(Counter(sample["risk"] for sample in normalized_samples).items())),
    }


def write_summary_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# ClarifyVC Import Summary",
        "",
        "- source_type: `paper_protocol_seed`",
        "- raw_dataset_availability: `public paper + protocol only; raw dataset mirror unavailable from current public endpoints`",
        f"- total_records: `{summary['total_records']}`",
        f"- normalized_sample_count: `{summary['normalized_sample_count']}`",
        "",
        "## Raw Tier Counts",
        "",
    ]
    for key, value in summary["tier_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Normalized Behavior Counts", ""])
    for key, value in summary["normalized_behavior_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Skip Reasons", ""])
    for key, value in summary["skip_reason_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a minimal ClarifyVC paper-protocol seed preview into finetune-lab."
    )
    parser.add_argument(
        "--raw-output-dir",
        default="data/public-source/clarifyvc",
        help="Directory to store OpenReview artifacts and protocol seed examples.",
    )
    parser.add_argument(
        "--normalized-output-dir",
        default="data/public-normalized/clarifyvc-v1",
        help="Directory to store normalized ClarifyVC preview files.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download OpenReview artifacts even if they already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_output_dir = Path(args.raw_output_dir)
    normalized_output_dir = Path(args.normalized_output_dir)

    download(OPENREVIEW_FORUM_URL, raw_output_dir / "openreview-forum.html", refresh=args.refresh)
    download(OPENREVIEW_PDF_URL, raw_output_dir / "clarifyvc-paper.pdf", refresh=args.refresh)

    metadata = {
        "dataset": "clarifyvc",
        "source_type": "paper_protocol_seed",
        "forum_url": OPENREVIEW_FORUM_URL,
        "paper_pdf_url": OPENREVIEW_PDF_URL,
        "notes": [
            "The OpenReview paper advertises code+dataset availability at anonymous.4open.science/r/ClarifyVC.",
            "Current public requests to anonymous.4open.science return HTTP 403 from this environment, so this importer mirrors the paper artifacts and builds a minimal protocol-seed preview instead of a raw dataset clone.",
        ],
    }
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    (raw_output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_jsonl(raw_output_dir / "protocol-seed-examples.jsonl", PROTOCOL_SEED_EXAMPLES)

    normalized_samples: list[dict] = []
    skip_reasons: Counter = Counter()
    for record in PROTOCOL_SEED_EXAMPLES:
        normalized_sample, skip_reason = normalize_protocol_record(record)
        if normalized_sample is None:
            skip_reasons[skip_reason or "unknown"] += 1
            continue
        normalized_samples.append(normalized_sample)

    normalized_output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(normalized_output_dir / "samples.jsonl", normalized_samples)
    summary = build_summary(
        total_records=len(PROTOCOL_SEED_EXAMPLES),
        normalized_samples=normalized_samples,
        skip_reasons=skip_reasons,
        protocol_seeds=PROTOCOL_SEED_EXAMPLES,
    )
    (normalized_output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_summary_markdown(normalized_output_dir / "summary.md", summary)
    _write_governance_artifacts(normalized_output_dir)


def _write_governance_artifacts(output_dir: Path) -> None:
    try:
        import governance as g
    except ImportError:  # pragma: no cover
        from . import governance as g  # type: ignore
    name = output_dir.name
    manifest = g.DatasetCardManifest(
        name=name,
        version=name.split("-")[-1] if "-" in name else "1.0",
        generator="public-import-clarifyvc",
        license="see upstream clarifyvc license (review before redistribution)",
        sensitivity="medium",
        description=(
            f"公开数据集导入：clarifyvc → `{name}`。来自外部 protocol benchmark，"
            "用于澄清问询任务对照。分发前需复核 upstream license。"
        ),
        provenance=[
            "上游：data/public-source/clarifyvc（按 import_clarifyvc.py 规范化）",
            "导入脚本：training/data_pipeline/import_clarifyvc.py",
        ],
        known_limitations=[
            "外部数据，可能含未识别的人名 / 地址等非结构化 PII",
            "默认 redaction policy 只扫 phone / id / plate / email",
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
