"""Data governance: PII redaction + dataset card / redaction report generation.

Per docs/specs/2026-04-26-data-governance-artifacts-spec.md.

No external deps beyond stdlib. Keeps the pipeline itself fast.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

POLICY_VERSION = "1.0"

# ---------- Policy / Rule ----------


@dataclass(frozen=True)
class RedactionRule:
    name: str
    pattern: re.Pattern
    replacement: str


@dataclass(frozen=True)
class RedactionPolicy:
    version: str
    rules: tuple[RedactionRule, ...]
    fields: tuple[str, ...]


# Chinese mainland mobile: 11 digits, starts with 1[3-9], not adjacent to other digits.
# Will incidentally match strings like "13800138000" but NOT "我有 13 个苹果" (only 2 digits).
_PHONE_CN_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")

# Chinese national ID: 18 digits with valid date segment + check digit (digit or X/x).
_ID_CN_RE = re.compile(
    r"(?<!\d)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)",
)

# Chinese plate: traditional blue + 2024 green (8 char). Province char + letter + 5-6 alnum.
_PLATE_PROVINCES = "京津沪渝冀晋蒙辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川贵云藏陕甘青宁新"
_PLATE_CN_RE = re.compile(
    rf"(?<![A-Za-z0-9])[{_PLATE_PROVINCES}][A-HJ-NP-Z][A-HJ-NP-Z0-9]{{5,6}}(?![A-Za-z0-9])"
)

_EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w.+-])")


def default_policy() -> RedactionPolicy:
    return RedactionPolicy(
        version=POLICY_VERSION,
        rules=(
            RedactionRule("phone_cn", _PHONE_CN_RE, "[PHONE_REDACTED]"),
            RedactionRule("id_cn", _ID_CN_RE, "[ID_REDACTED]"),
            RedactionRule("plate_cn", _PLATE_CN_RE, "[PLATE_REDACTED]"),
            RedactionRule("email", _EMAIL_RE, "[EMAIL_REDACTED]"),
        ),
        fields=(
            "prompt_user",
            "expected_assistant_content",
            "system_prompt",
            "messages[*].content",
        ),
    )


# ---------- Field access ----------


def _walk_field(record: dict, path: str):
    """Yield (setter, value) pairs for a field path supporting `messages[*].content`.

    setter is a callable(new_value) that writes the new value back into the record.
    """
    if "[*]." in path:
        head, tail = path.split("[*].", 1)
        arr = record.get(head)
        if not isinstance(arr, list):
            return
        for item in arr:
            if isinstance(item, dict):
                value = item.get(tail)
                if isinstance(value, str):
                    yield (lambda v, _it=item, _k=tail: _it.__setitem__(_k, v)), value
        return
    value = record.get(path)
    if isinstance(value, str):
        yield (lambda v, _r=record, _k=path: _r.__setitem__(_k, v)), value


# ---------- Redaction ----------


@dataclass
class RedactionResult:
    redacted_record: dict
    match_counts: dict[str, int]
    redacted_fields: list[str]

    @property
    def total_matches(self) -> int:
        return sum(self.match_counts.values())


def redact_record(record: dict, policy: RedactionPolicy | None = None) -> RedactionResult:
    policy = policy or default_policy()
    redacted = json.loads(json.dumps(record))  # deep copy
    counts: dict[str, int] = {rule.name: 0 for rule in policy.rules}
    redacted_fields: list[str] = []
    for field_path in policy.fields:
        for setter, value in _walk_field(redacted, field_path):
            new_value = value
            field_hit = False
            for rule in policy.rules:
                new_value, n = rule.pattern.subn(rule.replacement, new_value)
                if n:
                    counts[rule.name] += n
                    field_hit = True
            if field_hit:
                setter(new_value)
                if field_path not in redacted_fields:
                    redacted_fields.append(field_path)
    return RedactionResult(redacted, counts, redacted_fields)


# ---------- Bulk over a JSONL ----------


@dataclass
class AggregateRedactionStats:
    records_scanned: int = 0
    records_redacted: int = 0
    match_counts: dict[str, int] = field(default_factory=dict)
    fields_scanned: list[str] = field(default_factory=list)
    spot_check: list[dict] = field(default_factory=list)

    def merge(self, result: RedactionResult, original_record: dict) -> None:
        self.records_scanned += 1
        if result.total_matches > 0:
            self.records_redacted += 1
            self.spot_check.append(
                {
                    "record_id": original_record.get("id"),
                    "original_excerpts": _excerpts(original_record, result.redacted_fields),
                    "redacted_excerpts": _excerpts(result.redacted_record, result.redacted_fields),
                    "matches": dict(result.match_counts),
                }
            )
        for name, n in result.match_counts.items():
            self.match_counts[name] = self.match_counts.get(name, 0) + n


def _excerpts(record: dict, field_paths: list[str], max_chars: int = 160) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in field_paths:
        for _, value in _walk_field(record, path):
            text = value if len(value) <= max_chars else value[:max_chars] + "…"
            out.setdefault(path, text)
            break
    return out


def redact_jsonl(
    input_path: Path,
    output_path: Path,
    policy: RedactionPolicy | None = None,
) -> AggregateRedactionStats:
    """Stream-redact a JSONL file. Safe for large datasets — reads/writes line by line."""
    policy = policy or default_policy()
    stats = AggregateRedactionStats()
    stats.fields_scanned = list(policy.fields)
    with input_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.rstrip("\n")
            if not line:
                continue
            record = json.loads(line)
            result = redact_record(record, policy)
            stats.merge(result, record)
            dst.write(json.dumps(result.redacted_record, ensure_ascii=False) + "\n")
    return stats


def scan_jsonl(input_path: Path, policy: RedactionPolicy | None = None) -> AggregateRedactionStats:
    """Scan-only: count matches but don't write a redacted output. Useful for spot-check on synthetic data."""
    policy = policy or default_policy()
    stats = AggregateRedactionStats()
    stats.fields_scanned = list(policy.fields)
    if not input_path.exists():
        return stats
    with input_path.open("r", encoding="utf-8") as src:
        for line in src:
            line = line.rstrip("\n")
            if not line:
                continue
            record = json.loads(line)
            result = redact_record(record, policy)
            stats.merge(result, record)
    return stats


# ---------- Spot-check supplement ----------


def add_clean_spot_check(stats: AggregateRedactionStats, jsonl_path: Path, count: int = 10, seed: int = 42) -> None:
    """When records_redacted == 0, still attach `count` random samples to the spot_check list.
    This makes redaction-report.md a concrete "zero-PII proof" rather than an empty page."""
    if stats.records_redacted > 0 or not jsonl_path.exists():
        return
    rng = random.Random(seed)
    pool: list[dict] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                pool.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    sampled = rng.sample(pool, k=min(count, len(pool)))
    for record in sampled:
        stats.spot_check.append(
            {
                "record_id": record.get("id"),
                "original_excerpts": _excerpts(record, list(stats.fields_scanned)),
                "redacted_excerpts": {},
                "matches": {},
                "note": "no PII match — included as zero-PII evidence sample",
            }
        )


# ---------- Markdown rendering ----------


def _yaml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, dict):
        return "\n" + "\n".join(f"  {k}: {_yaml_value(val)}" for k, val in v.items())
    if isinstance(v, list):
        return "\n" + "\n".join(f"  - {_yaml_value(item).lstrip()}" for item in v)
    s = str(v)
    if any(ch in s for ch in ":#"):
        return json.dumps(s, ensure_ascii=False)
    return s


def _yaml_frontmatter(data: dict) -> str:
    lines = ["---"]
    for k, v in data.items():
        rendered = _yaml_value(v)
        if rendered.startswith("\n"):
            lines.append(f"{k}:{rendered}")
        else:
            lines.append(f"{k}: {rendered}")
    lines.append("---")
    return "\n".join(lines)


@dataclass
class DatasetCardManifest:
    name: str
    version: str
    generator: str
    license: str = "internal-research-only"
    sensitivity: str = "low"
    description: str = "（请填写：这份数据是干什么用的、教学目标是什么、不能拿去做什么）"
    provenance: list[str] = field(default_factory=list)
    schema_ref: str = "training/data_pipeline/types or web/src/types.ts"
    known_limitations: list[str] = field(default_factory=list)


def write_dataset_card(
    dataset_dir: Path,
    manifest: DatasetCardManifest,
    splits: dict[str, int],
    redaction_stats: AggregateRedactionStats,
) -> Path:
    # The pipeline emits both samples.jsonl and its train/held-out subdivisions.
    # When all three are present, samples is a superset (= train + held-out) so we
    # take the primary count and report sub-splits separately.
    if "samples" in splits and {"train", "held-out"}.issubset(splits):
        total = splits["samples"]
        sub_splits = {k: v for k, v in splits.items() if k != "samples"}
    elif "samples" in splits:
        total = splits["samples"]
        sub_splits = {k: v for k, v in splits.items() if k != "samples"}
    else:
        total = sum(splits.values())
        sub_splits = splits
    front = {
        "name": manifest.name,
        "version": manifest.version,
        "generated_at": _now_iso(),
        "generator": manifest.generator,
        "total_samples": total,
        "splits": sub_splits if sub_splits else splits,
        "license": manifest.license,
        "sensitivity": manifest.sensitivity,
        "pii_scanned": True,
        "pii_redacted_count": redaction_stats.records_redacted,
        "policy_version_at_generation": POLICY_VERSION,
        "schema_ref": manifest.schema_ref,
    }
    body_lines = [
        "",
        "## 描述",
        "",
        manifest.description,
        "",
        "## 来源 / Provenance",
        "",
    ]
    if manifest.provenance:
        body_lines.extend(f"- {item}" for item in manifest.provenance)
    else:
        body_lines.append("- （请补充）")
    body_lines.extend(
        [
            "",
            "## Schema",
            "",
            f"参见 `{manifest.schema_ref}`，本卡片不重复字段定义。",
            "",
            "## 已知限制",
            "",
        ]
    )
    if manifest.known_limitations:
        body_lines.extend(f"- {item}" for item in manifest.known_limitations)
    else:
        body_lines.append("- （请补充）")
    body_lines.extend(
        [
            "",
            "## 治理",
            "",
            "- 脱敏策略：见 [redaction-report.md](./redaction-report.md)",
            "- schema 校验：见 [validation_report.md](./validation_report.md)",
            "- 统计描述：见 [dataset_summary.md](./dataset_summary.md)",
            "",
        ]
    )
    out_path = dataset_dir / "dataset-card.md"
    out_path.write_text(_yaml_frontmatter(front) + "\n" + "\n".join(body_lines), encoding="utf-8")
    return out_path


def write_redaction_report(
    dataset_dir: Path,
    policy: RedactionPolicy,
    stats: AggregateRedactionStats,
    dataset_name: str,
) -> Path:
    front = {
        "dataset": dataset_name,
        "generated_at": _now_iso(),
        "policy_version": policy.version,
        "records_scanned": stats.records_scanned,
        "records_redacted": stats.records_redacted,
        "match_counts": stats.match_counts,
        "fields_scanned": list(stats.fields_scanned),
        "spot_check_count": len(stats.spot_check),
    }
    lines = ["", "## 应用的策略", ""]
    rule_descriptions = {
        "phone_cn": "中国大陆手机号（11 位，1[3-9]xxxxxxxxx，前后非数字）",
        "id_cn": "中国大陆身份证（18 位，含日期段 + 校验位 X/x）",
        "plate_cn": "中国机动车牌（蓝/绿牌，省份字 + 字母 + 5-6 位 alnum）",
        "email": "标准 email",
    }
    for rule in policy.rules:
        lines.append(f"### `{rule.name}`")
        lines.append("")
        lines.append(rule_descriptions.get(rule.name, "—"))
        lines.append(f"替换为 `{rule.replacement}`。")
        lines.append("")

    lines.extend(["## 命中明细", ""])
    if stats.records_redacted > 0:
        for entry in stats.spot_check:
            lines.append(f"### `{entry.get('record_id')}`")
            lines.append("")
            for field_name, excerpt in (entry.get("original_excerpts") or {}).items():
                lines.append(f"- 字段 `{field_name}` 原文片段：`{excerpt}`")
            for field_name, excerpt in (entry.get("redacted_excerpts") or {}).items():
                lines.append(f"- 字段 `{field_name}` 脱敏后：`{excerpt}`")
            matches = entry.get("matches") or {}
            hit_summary = ", ".join(f"{k}×{v}" for k, v in matches.items() if v) or "—"
            lines.append(f"- 命中：{hit_summary}")
            lines.append("")
    else:
        lines.append("本批无命中（`records_redacted = 0`）。")
        lines.append("")

    lines.extend(["## Spot-check（10 例）", ""])
    if stats.spot_check:
        cap = 10
        for entry in stats.spot_check[:cap]:
            note = entry.get("note") or ""
            lines.append(f"### `{entry.get('record_id')}`{(' — ' + note) if note else ''}")
            lines.append("")
            for field_name, excerpt in (entry.get("original_excerpts") or {}).items():
                lines.append(f"- `{field_name}`: `{excerpt}`")
            lines.append("")
    else:
        lines.append("（无可抽查样本，可能 dataset 为空）")
        lines.append("")

    lines.extend(
        [
            "## 残留风险",
            "",
            "- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。",
            "- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。",
            "- 不做 NER，不识别非结构化人名。",
            "- IP / MAC / 银行卡号不在策略覆盖范围。",
            "",
        ]
    )

    out_path = dataset_dir / "redaction-report.md"
    out_path.write_text(_yaml_frontmatter(front) + "\n" + "\n".join(lines), encoding="utf-8")
    return out_path


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


# ---------- Convenience: governance pass over a dataset directory ----------


def governance_pass(
    dataset_dir: Path,
    manifest: DatasetCardManifest,
    *,
    primary_jsonl: str = "samples.jsonl",
    splits_jsonl: dict[str, str] | None = None,
    policy: RedactionPolicy | None = None,
) -> dict:
    """Run scan over the dataset's primary jsonl and write both governance artifacts.

    For synthetic datasets we default to scan-only (no rewriting). When real-log paths are
    introduced later, swap `scan_jsonl` for `redact_jsonl` and route writes accordingly.
    """
    policy = policy or default_policy()
    primary_path = dataset_dir / primary_jsonl
    stats = scan_jsonl(primary_path, policy)
    add_clean_spot_check(stats, primary_path)

    splits = {}
    for label, filename in (splits_jsonl or {"samples": primary_jsonl}).items():
        path = dataset_dir / filename
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                splits[label] = sum(1 for line in f if line.strip())

    card_path = write_dataset_card(dataset_dir, manifest, splits, stats)
    report_path = write_redaction_report(dataset_dir, policy, stats, manifest.name)
    return {
        "dataset": manifest.name,
        "dataset_card": str(card_path),
        "redaction_report": str(report_path),
        "records_scanned": stats.records_scanned,
        "records_redacted": stats.records_redacted,
        "match_counts": stats.match_counts,
    }
