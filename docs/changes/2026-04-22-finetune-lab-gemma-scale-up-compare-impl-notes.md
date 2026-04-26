---
title: finetune-lab Gemma scale-up compare
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/specs/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-spec.md
reviews: []
---

## 动机

此前 Level 6 虽然已经有 preference pair 和 policy compare，但 scale-up 部分还更像“经验性建议”，不够像一个真正的决策报告。

用户提的目标是“更真实一点的 Gemma scale-up compare”，所以这轮补的是：

- 明确的 gating 条件
- E2B-it vs E4B-it 的对照画像
- 当前状态下为什么建议继续 stay small

## 改动

### 1. Level 6 生成脚本新增 scale-up compare

[training/finetune/build_level6_demo.py](/Users/xforg/AI_SPACE/finetune-lab/training/finetune/build_level6_demo.py:1) 现在除了生成：

- `preference-dataset-pack.json`
- `policy-compare-report.json`

还会额外生成：

- `outputs/level6/gemma-scale-up-compare.json`
- `outputs/level6/gemma-scale-up-compare.md`

### 2. Scale-up compare 的结构

这份报告不再只是 3 条建议，而是包含：

- `current_state`
  - pair 数量
  - rejection type 数量
  - baseline / preference 的 chosen win rate
  - win gap
- `gates`
  - pair volume
  - rejection diversity
  - policy gap
  - evaluation rubric
- `model_profiles`
  - `google/gemma-4-E2B-it`
  - `google/gemma-4-E4B-it`
- `decision_matrix`
  - 当前状态、E2B-it 适配点、E4B-it 适配点
- `recommendation`
  - 当前推荐模型
  - 当前阶段 `stay-small / scale-up`
  - next actions

### 3. 前端和 IAB 接入

统一数据层现在包含：

- `level6.scale_up_compare`

React 前端：

- [web/src/App.tsx](/Users/xforg/AI_SPACE/finetune-lab/web/src/App.tsx:1)
  - Level 6 卡片新增 `Gemma scale-up compare`
  - 展示 gates、fit score、recommended model、next actions

IAB 静态页：

- [web/scripts/export-standalone-html.mjs](/Users/xforg/AI_SPACE/finetune-lab/web/scripts/export-standalone-html.mjs:1)
  - 同步展示 `Gemma scale-up compare`
  - 让 `file://` 下也能直接看到“为什么现在建议继续留在 E2B-it”

### 4. 路线图元数据去掉过期占位

`project-context.json` 里 Level 6 的 commands 已经从：

- `planned: Gemma scale-up compare`

更新为：

- `review outputs/level6/gemma-scale-up-compare.json`

这样路线图不再和实际实现状态打架。

## 验证

本轮实际跑过：

- `make level6-demo`
- `make web-build`

当前报告结论：

- recommended model: `google/gemma-4-E2B-it`
- stage: `stay-small`

原因是：

- 当前 pairs 只有 8 条
- 虽然 preference direction 已经很明显，但 pair volume 和 eval rubric 还不够支撑 E4B-it 的确认性实验

## 当前结论

Level 6 现在不只是“偏好数据 demo”，而是已经有一个能回答现实问题的 scale-up compare：

- 现在为什么不该急着上更大模型
- 升级前还差哪些 gate
- 下一步应该先扩哪里
