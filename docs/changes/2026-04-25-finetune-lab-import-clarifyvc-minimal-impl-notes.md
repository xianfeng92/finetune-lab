# 2026-04-25 finetune-lab import ClarifyVC minimal impl notes

## 本次改动

- 新增 `training/data_pipeline/import_clarifyvc.py`
- 新增 `training/data_pipeline/tests/test_import_clarifyvc.py`
- 在 `Makefile` 中新增 `make import-clarifyvc`
- 更新 `training/data_pipeline/README.md`
- 更新 `docs/ai/public-datasets-for-car-tool-finetuning.md`

## 实现策略

这次没有把 `ClarifyVC` 当成“可直接镜像的公开原始数据集”处理，而是明确实现成：

- `OpenReview artifacts mirror`
- `paper_protocol_seed importer`

原因是：

- 论文正文公开了 `tier / task / ambiguity` 协议与代表性示例
- 论文里给出的匿名代码和数据地址是 `https://anonymous.4open.science/r/ClarifyVC`
- 当前本机环境访问该地址返回 `HTTP 403`

因此这版实现选择先把可公开验证的部分接进仓库：

- 论坛页 HTML
- 论文 PDF
- 基于论文表格和示例整理出的最小 protocol seed

## 当前导入内容

最小 protocol seed 覆盖：

- Tier 1: single-turn structured parsing
- Tier 2: ambiguity detection and clarification
- Tier 3: multi-turn dialogue grounding

当前能映射到仓库现有 tool schema 的域：

- `hvac`
- `window`
- `seat`

当前仍然只作为 raw protocol preview 保存的域：

- `lighting`
- `navigation`
- `media`

## 输出目录

原始协议镜像：

- `data/public-source/clarifyvc/`

规范化 preview：

- `data/public-normalized/clarifyvc-v1/`

## 验证

已验证：

- `bash training/data_pipeline/scripts/test.sh`
- `python training/data_pipeline/import_clarifyvc.py --raw-output-dir <tmp> --normalized-output-dir <tmp>`

## 已知边界

- 当前不是 `ClarifyVC` 完整原始数据导入
- 当前 preview 只验证“论文协议能否映射到 finetune-lab schema”
- 若后续匿名数据地址恢复可访问，应再补一版 raw dataset mirror importer
