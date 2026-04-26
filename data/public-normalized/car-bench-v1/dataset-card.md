---
name: car-bench-v1
version: v1
generated_at: "2026-04-26T20:31:59+08:00"
generator: public-import-car-bench
total_samples: 30
splits:
  samples: 30
license: see upstream car-bench license (review before redistribution)
sensitivity: medium
pii_scanned: true
pii_redacted_count: 0
policy_version_at_generation: 1.0
schema_ref: training/data_pipeline/types or web/src/types.ts
---

## 描述

公开数据集导入：car-bench → `car-bench-v1`。来自外部公开 benchmark，尽管已脱敏正则扫描，分发前需复核 upstream license。

## 来源 / Provenance

- 上游：data/public-source/car-bench（按 import_car_bench.py 规范化）
- 导入脚本：training/data_pipeline/import_car_bench.py

## Schema

参见 `training/data_pipeline/types or web/src/types.ts`，本卡片不重复字段定义。

## 已知限制

- 外部数据，可能含未识别的人名 / 地址等非结构化 PII
- 默认 redaction policy 只扫 phone / id / plate / email
- 如果上游升级，需要重跑 dataset-governance 刷新报告

## 治理

- 脱敏策略：见 [redaction-report.md](./redaction-report.md)
- schema 校验：见 [validation_report.md](./validation_report.md)
- 统计描述：见 [dataset_summary.md](./dataset_summary.md)
