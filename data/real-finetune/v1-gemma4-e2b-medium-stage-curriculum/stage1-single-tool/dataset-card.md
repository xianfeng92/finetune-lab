---
name: v1-gemma4-e2b-medium-stage-curriculum/stage1-single-tool
version: 1.0
generated_at: "2026-04-26T16:42:16+08:00"
generator: synthetic-unknown
total_samples: 150
splits:
  train: 120
  valid: 15
  test: 15
license: internal-research-only
sensitivity: low
pii_scanned: true
pii_redacted_count: 0
policy_version_at_generation: 1.0
schema_ref: training/data_pipeline/types or web/src/types.ts
---

## 描述

real-finetune 数据集 `v1-gemma4-e2b-medium-stage-curriculum/stage1-single-tool`：以 openai-chat-with-tools 格式存放的训练 / valid / test split。由 SFT 数据经 build_real_finetune_dataset 转换生成，承接 mlx-lm.lora 真实训练。

## 来源 / Provenance

- 来源：training/finetune/build_real_finetune_dataset.py
- 上游：data/sft/<对应 SFT 数据集>
- 数据目录：real-finetune/v1-gemma4-e2b-medium-stage-curriculum/stage1-single-tool

## Schema

参见 `training/data_pipeline/types or web/src/types.ts`，本卡片不重复字段定义。

## 已知限制

- 合成数据无法覆盖真实方言、口语化、跨说法
- 上线前必须用真实样本回归

## 治理

- 脱敏策略：见 [redaction-report.md](./redaction-report.md)
- schema 校验：见 [validation_report.md](./validation_report.md)
- 统计描述：见 [dataset_summary.md](./dataset_summary.md)
