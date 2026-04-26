"""Tests for governance.py — PII redaction + report rendering."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import governance as g


# ---------- phone_cn ----------


def test_phone_cn_matches_standard_mobile():
    res = g.redact_record({"prompt_user": "联系我 13800138000 谢谢"})
    assert res.match_counts["phone_cn"] == 1
    assert "[PHONE_REDACTED]" in res.redacted_record["prompt_user"]


def test_phone_cn_matches_multiple():
    res = g.redact_record({"prompt_user": "13912345678 或 15999998888"})
    assert res.match_counts["phone_cn"] == 2


def test_phone_cn_does_not_match_short_digit_runs():
    # "13 个苹果，800 块" — 13 and 800 are not adjacent, neither is 11 digits
    res = g.redact_record({"prompt_user": "我有 13 个苹果，800 块买的"})
    assert res.match_counts["phone_cn"] == 0


def test_phone_cn_does_not_match_inside_longer_digit_run():
    # 13 digits — not exactly 11 — must NOT match.
    res = g.redact_record({"prompt_user": "ID=1380013800012"})
    assert res.match_counts["phone_cn"] == 0


# ---------- id_cn ----------


def test_id_cn_matches_18_digit_with_check_X():
    res = g.redact_record({"prompt_user": "身份证 11010519491231002X 已记录"})
    assert res.match_counts["id_cn"] == 1
    assert "[ID_REDACTED]" in res.redacted_record["prompt_user"]


def test_id_cn_does_not_match_invalid_date():
    # month 13 invalid
    res = g.redact_record({"prompt_user": "11010519491331002X"})
    assert res.match_counts["id_cn"] == 0


# ---------- plate_cn ----------


def test_plate_cn_matches_blue_plate():
    res = g.redact_record({"prompt_user": "车牌京A12345"})
    assert res.match_counts["plate_cn"] == 1


def test_plate_cn_matches_green_plate_8char():
    res = g.redact_record({"prompt_user": "苏A123456 是新能源"})
    assert res.match_counts["plate_cn"] == 1


def test_plate_cn_does_not_match_plain_letters():
    res = g.redact_record({"prompt_user": "ABC123456"})
    assert res.match_counts["plate_cn"] == 0


# ---------- email ----------


def test_email_matches_standard():
    res = g.redact_record({"prompt_user": "foo.bar+test@example.com 联系我"})
    assert res.match_counts["email"] == 1
    assert "[EMAIL_REDACTED]" in res.redacted_record["prompt_user"]


def test_email_does_not_match_at_alone():
    res = g.redact_record({"prompt_user": "@ 是个符号"})
    assert res.match_counts["email"] == 0


# ---------- field traversal ----------


def test_walks_messages_array():
    record = {
        "messages": [
            {"role": "user", "content": "我手机号是 13800138000"},
            {"role": "assistant", "content": "好的"},
        ]
    }
    res = g.redact_record(record)
    assert res.match_counts["phone_cn"] == 1
    assert "[PHONE_REDACTED]" in res.redacted_record["messages"][0]["content"]
    assert res.redacted_record["messages"][1]["content"] == "好的"


def test_walks_system_prompt():
    record = {"system_prompt": "vehicle_state: ... contact 13800138000"}
    res = g.redact_record(record)
    assert res.match_counts["phone_cn"] == 1


def test_does_not_modify_original_record():
    record = {"prompt_user": "电话 13800138000"}
    res = g.redact_record(record)
    # original untouched
    assert record["prompt_user"] == "电话 13800138000"
    assert res.redacted_record["prompt_user"] != record["prompt_user"]


# ---------- bulk + report ----------


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")


def test_scan_jsonl_aggregates_counts(tmp_path: Path):
    p = tmp_path / "samples.jsonl"
    _write_jsonl(
        p,
        [
            {"id": "a", "prompt_user": "我手机号 13800138000"},
            {"id": "b", "prompt_user": "干净样本"},
            {"id": "c", "prompt_user": "邮箱 a@b.com 电话 15999998888"},
        ],
    )
    stats = g.scan_jsonl(p)
    assert stats.records_scanned == 3
    assert stats.records_redacted == 2
    assert stats.match_counts["phone_cn"] == 2
    assert stats.match_counts["email"] == 1
    assert len(stats.spot_check) == 2


def test_redact_jsonl_writes_redacted_output(tmp_path: Path):
    src = tmp_path / "in.jsonl"
    dst = tmp_path / "out.jsonl"
    _write_jsonl(src, [{"id": "a", "prompt_user": "电话 13800138000"}])
    g.redact_jsonl(src, dst)
    out = json.loads(dst.read_text(encoding="utf-8").strip())
    assert "[PHONE_REDACTED]" in out["prompt_user"]


def test_clean_spot_check_supplements_zero_pii(tmp_path: Path):
    p = tmp_path / "samples.jsonl"
    _write_jsonl(p, [{"id": f"id-{i}", "prompt_user": f"clean prompt {i}"} for i in range(20)])
    stats = g.scan_jsonl(p)
    assert stats.records_redacted == 0
    assert stats.spot_check == []
    g.add_clean_spot_check(stats, p, count=5, seed=1)
    assert len(stats.spot_check) == 5
    assert all(item.get("note") for item in stats.spot_check)


def test_governance_pass_writes_both_artifacts(tmp_path: Path):
    p = tmp_path / "samples.jsonl"
    _write_jsonl(
        p,
        [
            {"id": "ok-1", "prompt_user": "把空调调到 22 度"},
            {"id": "leak", "prompt_user": "我手机 13800138000"},
        ],
    )
    manifest = g.DatasetCardManifest(
        name="test-dataset",
        version="0.1",
        generator="test-fixture",
    )
    summary = g.governance_pass(tmp_path, manifest)
    assert summary["records_scanned"] == 2
    assert summary["records_redacted"] == 1
    card = (tmp_path / "dataset-card.md").read_text(encoding="utf-8")
    report = (tmp_path / "redaction-report.md").read_text(encoding="utf-8")
    assert "test-dataset" in card
    assert "policy_version: 1.0" in report
    assert "[PHONE_REDACTED]" in report  # excerpt of redacted shows the marker
    assert "phone_cn:" in report or "phone_cn: 1" in report


@pytest.mark.parametrize(
    "text,expected",
    [
        ("13700137000", 1),
        ("12345", 0),  # too short
        ("119999999999", 0),  # 12 digits — phone_cn requires exactly 11 with no adjacent digit
        ("call 13800138000.", 1),
    ],
)
def test_phone_cn_boundary_cases(text, expected):
    res = g.redact_record({"prompt_user": text})
    assert res.match_counts["phone_cn"] == expected
