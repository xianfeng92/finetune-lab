---
name: clarifyvc-v1
version: v1
generated_at: "2026-04-26T20:31:00+08:00"
generator: public-import-clarifyvc
total_samples: 9
splits:
  samples: 9
license: see upstream clarifyvc license (review before redistribution)
sensitivity: medium
pii_scanned: true
pii_redacted_count: 0
policy_version_at_generation: 1.0
schema_ref: training/data_pipeline/types or web/src/types.ts
---

## 描述

公开数据集导入：clarifyvc → `clarifyvc-v1`。来自外部 protocol benchmark，用于澄清问询任务对照。分发前需复核 upstream license。

## 来源 / Provenance

- 上游：data/public-source/clarifyvc（按 import_clarifyvc.py 规范化）
- 导入脚本：training/data_pipeline/import_clarifyvc.py

## Schema

参见 `training/data_pipeline/types or web/src/types.ts`，本卡片不重复字段定义。

## 已知限制

- 外部数据，可能含未识别的人名 / 地址等非结构化 PII
- 默认 redaction policy 只扫 phone / id / plate / email

## 治理

- 脱敏策略：见 [redaction-report.md](./redaction-report.md)
- schema 校验：见 [validation_report.md](./validation_report.md)
- 统计描述：见 [dataset_summary.md](./dataset_summary.md)
