# 2026-04-22 finetune-lab AI-native Onboarding and Teaching Review

## 结论

本轮对 `finetune-lab` 的 AI-native onboarding 和教学链路实现做了文档级验收。

结论：通过，无阻塞问题，可作为 `implemented` 状态继续维护。

## 核对范围

- `make ai-onboarding`、`make ai-setup`、`make ai-lab` 是否形成稳定入口
- onboarding 报告是否同时提供机器可读和人类可读产物
- 仓库上下文协议是否足以让 Codex / Claude 接手
- 前端是否已展示 onboarding、workflow stages 和 agent handoff 信息

## 核对结果

### 1. AI-native 标准入口已落地

仓库已经提供 `ai-onboarding`、`ai-setup`、`ai-lab` 三个标准 target，符合 spec 中“单一入口 + agent-first”的要求。

参考：

- `Makefile`
- `README.md`
- `AGENTS.md`

### 2. onboarding 报告协议已形成

onboarding 报告已同时输出 `.json` 和 `.md`，满足 agent 可读和用户可读两条路径。

参考：

- `scripts/ai_onboarding_report.py`
- `outputs/agent/onboarding-report.json`
- `outputs/agent/onboarding-report.md`

### 3. agent handoff 文档已补齐

`project-context.json`、`docs/ai/setup.md`、`docs/ai/workflows.md` 已明确写出仓库入口、标准命令、工作流阶段和产物路径，足以作为 Codex / Claude 的接手上下文。

参考：

- `project-context.json`
- `docs/ai/setup.md`
- `docs/ai/workflows.md`

### 4. 前端教学链路已接通

前端和 IAB 静态页已经展示 onboarding、workflow stages 和 agent prompts，说明 spec 中的教学链路要求已经落地。

参考：

- `web/src/App.tsx`
- `web/scripts/build-lab-data.mjs`
- `web/scripts/export-standalone-html.mjs`
- `web/public/lab-data.json`

## 剩余风险

- 当前 onboarding 仍以本地轻量路径和 demo 产物为主，跨机器依赖差异较大时还需要继续补环境兼容说明。
- 本 review 主要验证入口、协议和展示链路是否闭环，不代替后续脚本级或跨平台运行验证。
