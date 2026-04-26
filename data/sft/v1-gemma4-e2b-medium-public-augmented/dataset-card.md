---
name: v1-gemma4-e2b-medium-public-augmented
version: v1
generated_at: "2026-04-26T20:45:08+08:00"
generator: synthetic-car-bench/import-v1
total_samples: 539
splits:
  train: 439
  held-out: 100
license: internal-research-only
sensitivity: low
pii_scanned: true
pii_redacted_count: 0
policy_version_at_generation: 1.0
schema_ref: training/data_pipeline/types or web/src/types.ts
---

## 描述

SFT 数据集 `v1-gemma4-e2b-medium-public-augmented`：合成的车控 tool-call 样本，用于 LoRA 微调教学，不可作为真实车机训练集。

## 来源 / Provenance

- 生成器：training/data_pipeline/pipeline.py + schema_sampler + generator
- 种子：seed-anchor schema v1（合成数据，不含真实用户对话）
- 数据目录：/Users/xforg/AI_SPACE/finetune-lab/data/sft/v1-gemma4-e2b-medium-public-augmented

## Schema

参见 `training/data_pipeline/types or web/src/types.ts`，本卡片不重复字段定义。

## 已知限制

- 合成数据无法覆盖真实方言、口语化、跨说法
- 上线前必须用真实样本回归

## 治理

- 脱敏策略：见 [redaction-report.md](./redaction-report.md)
- schema 校验：见 [validation_report.md](./validation_report.md)
- 统计描述：见 [dataset_summary.md](./dataset_summary.md)
