# 2026-04-22 finetune-lab AI-native Onboarding and Teaching Impl Notes

## 背景

`finetune-lab/` 已经具备最小可跑闭环，但还不够 AI-native：

- agent 缺少明确的 onboarding 协议
- 用户下载仓库后，还不能自然地把 setup 和实验执行交给 Codex / Claude
- 前端虽然能展示数据、run 和 probe，但没有把 agent handoff 和教学链路讲完整

## 本轮改动

- 新增 `docs/specs/2026-04-22-finetune-lab-ai-native-onboarding-and-teaching-spec.md`
- 新增 `scripts/ai_onboarding_report.py`
  生成：
  - `outputs/agent/onboarding-report.json`
  - `outputs/agent/onboarding-report.md`
- 扩展 `Makefile`
  新增：
  - `make ai-onboarding`
  - `make ai-setup`
  - `make ai-lab`
- 更新 `README.md`、`AGENTS.md`、`project-context.json`、`docs/ai/setup.md`、`docs/ai/workflows.md`
  把 agent-first 的接手协议、推荐 prompt 和标准学习路径写清楚
- 扩展前端统一数据层
  把 onboarding report、agent prompts、workflow stages 同步进 `lab-data.json`
- 更新 React 前端
  新增 `AI Onboarding` 视图
- 更新 IAB 静态页
  新增 onboarding / readiness / agent prompts / workflow teaching sections

## 实际验证

本轮实际跑过：

```bash
make ai-lab
npm run build
```

验证结果：

- `make ai-onboarding` 可以生成机器可读和人类可读的 onboarding 报告
- `make ai-lab` 能跑通最小教学闭环
- `web/public/lab-data.json` 已包含 onboarding、agent prompts、workflow stages
- `web/dist/index.html` 已包含 onboarding 教学区块

## 结果

当前仓库已经更接近真正的 AI-native 学习项目：

- 用户可以先让 agent 判断 readiness
- agent 可以按统一 target 接手 setup 和最小闭环
- 前端能把 `onboarding -> data -> train -> probe -> compare` 讲成一条教学链路
