---
title: finetune-lab Level 6 preference data demo
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/specs/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-spec.md
reviews: []
---

## 动机

在 Level 5 之后，仓库已经能讲清楚：

- tool routing
- structured outputs
- case-level probe

但还缺一层关键升级：用户还不知道 `preference data` 和 `SFT data` 到底差在哪，也不知道 `policy compare` 这种视角为什么重要。

所以这轮不直接上真实 DPO，而是先做一个最小的 Level 6 demo，把心智模型立住。

## 改动

### 1. 新增标准入口

`Makefile` 新增：

- `make level6-demo`

这个 target 会生成：

- `data/preferences/v1-gemma4-e2b-demo/pairs.jsonl`
- `outputs/level6/preference-dataset-pack.json`
- `outputs/level6/policy-compare-report.json`

### 2. 新增 Level 6 demo 脚本

新增 [training/finetune/build_level6_demo.py](/Users/xforg/AI_SPACE/finetune-lab/training/finetune/build_level6_demo.py:1)。

它会基于现有 SFT sample 生成一组最小 preference pairs：

- `chosen`
  - 完整 `tool_calls` 数组
- `rejected`
  - `tool_name_only`
  - `wrong_tool_loaded`
  - `wrong_arguments`
  - `natural_language_only`
  - `schema_echo`

这样用户可以直接看懂：偏好数据不是再问一次“正确答案是什么”，而是在问“两个候选答案里哪个更好”。

### 3. 新增 policy compare report

Level 6 demo 还会生成一个轻量的 `policy compare report`，用来对比：

- `SFT-only policy`
- `Preference-aware policy`

报告会输出：

- `chosen_win_rate`
- `structured_output_preference`
- case-level compare
- `scale_up_guidance`

目的不是模拟真实训练效果，而是帮助用户理解 preference tuning 想要优化的行为是什么。

### 4. 前端与 IAB 接入

统一数据层新增：

- `level6.preference_dataset_pack`
- `level6.policy_compare_report`

React 前端：

- [web/src/App.tsx](/Users/xforg/AI_SPACE/finetune-lab/web/src/App.tsx:1)
  - Overview 新增 `Level 6: Preference Data Demo`

IAB 静态页：

- [web/scripts/export-standalone-html.mjs](/Users/xforg/AI_SPACE/finetune-lab/web/scripts/export-standalone-html.mjs:1)
  - 新增 `07 · Level 6 demo`
  - 展示 preference pairs、policy compare、scale-up guidance

### 5. 项目元数据同步

更新了：

- `project-context.json`
- `README.md`
- `docs/ai/workflows.md`
- `training/finetune/README.md`
- `web/README.md`

现在 Level 6 在路线图里的状态从 `planned` 变成了 `partial`，表示：

- preference data demo 已经可跑、可看
- 更真实的 scale-up compare 还没有完全做完

## 验证

本轮实际跑过：

- `make level6-demo`
- `make web-build`

关键结果：

- `pairs.jsonl` 生成 8 条 preference pairs
- `policy compare` 中：
  - `SFT-only policy`: `1/6 chosen wins`
  - `Preference-aware policy`: `6/6 chosen wins`
- IAB 页面已新增 Level 6 demo 区块

## 当前结论

Level 6 现在已经有一条最小但完整的教学链路：

- preference pairs
- dataset pack
- policy compare
- scale-up guidance
- React / IAB 展示

下一步如果继续做 Level 6，更自然的方向是：

- 把 synthetic pair 扩展成更丰富的 preference rubric
- 引入更真实的 judge / reward 口径
- 再考虑更大 Gemma checkpoint 的 scale-up compare
