---
title: finetune-lab AI-native Onboarding and Teaching Spec
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/changes/2026-04-22-finetune-lab-ai-native-onboarding-and-teaching-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-learning-coverage-and-ai-native-hardening-impl-notes.md
reviews:
  - docs/reviews/2026-04-22-finetune-lab-ai-native-onboarding-and-teaching-review.md
  - docs/reviews/2026-04-22-finetune-lab-learning-coverage-and-ai-native-review.md
---

## 目标

把 `finetune-lab/` 补成一个真正 AI-native 的微调学习仓库：

1. 用户下载仓库后，可以直接让 Codex 或 Claude 接手环境 setup
2. agent 可以继续跑通最小微调闭环，而不是只停留在依赖安装
3. 前端要把 `onboarding -> data -> train -> probe -> compare` 这条链路讲清楚

## 非目标

- 不追求真实重型训练环境的完整兼容
- 不在本轮引入额外后端服务
- 不要求把所有实验变成一键生产级流水线

## 设计原则

- 单一入口：优先通过 `Makefile` 提供稳定 target
- agent-first：命令、产物路径、下一步都必须可被 agent 判断
- teaching-first：前端优先解释链路，不只显示结果
- lightweight-first：重依赖步骤默认允许轻量 smoke fallback

## 实现范围

### 1. AI-native onboarding

新增一组 agent 友好的标准入口：

- `make ai-onboarding`
  生成当前仓库的 onboarding 状态报告
- `make ai-setup`
  准备 Python 和前端依赖，并刷新 onboarding 状态
- `make ai-lab`
  跑通最小教学闭环，并刷新前端可读数据

onboarding 报告至少包含：

- 当前机器与依赖状态
- 关键产物是否已经存在
- 下一步推荐命令
- 可直接给 Codex / Claude 的提示词

### 2. 项目上下文协议

更新 `README.md`、`AGENTS.md`、`project-context.json`、`docs/ai/setup.md`、`docs/ai/workflows.md`，明确：

- agent 应先读什么
- agent 第一条建议执行什么命令
- 用户可以直接复制给 agent 的 prompt
- 仓库的标准学习路径和产物路径

### 3. 前端教学链路

统一数据层除了 dataset 和 runs，还要包含：

- onboarding 报告
- workflow stages
- recommended agent prompts

前端至少要能展示：

- AI-native onboarding
- 当前仓库 readiness
- 用户可以如何让 agent 接手
- 微调学习路径上的每个阶段在看什么

### 4. 文档收口

实现完成后：

- 在 `docs/changes/` 写实现说明
- 把本 spec 更新为 `implemented`

## 验收标准

- 新 clone 的用户可以通过 agent 和 `Makefile` 明确完成 setup
- `make ai-onboarding` 能产出机器可读和人类可读的状态报告
- `make ai-lab` 能跑通最小教学闭环
- 前端构建后的页面能展示 onboarding 和教学链路
- README 和 AI 文档能直接指导 Codex / Claude 接手仓库
