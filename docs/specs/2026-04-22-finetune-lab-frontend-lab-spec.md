---
title: finetune-lab Frontend Lab Spec
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/changes/2026-04-22-finetune-lab-rebuild-on-main-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-rename-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-file-iab-build-fix-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-static-lab-polish-impl-notes.md
reviews:
  - docs/reviews/2026-04-22-finetune-lab-frontend-lab-review.md
---

## 目标

做一个教学型前端实验台，展示：

1. 数据如何生成
2. 训练 run 有哪些输出
3. probe 如何对比

## 页面

- `Overview`
- `Data Pipeline`
- `Training Runs`
- `Probe Compare`

## 数据边界

前端组件不直接扫描仓库。

统一读取：

- `web/public/lab-data.json`

该文件由构建脚本从下列产物生成：

- `data/sft/**/samples.jsonl`
- `outputs/**/run-manifest.json`
- `outputs/**/inference-probe-results.json`
