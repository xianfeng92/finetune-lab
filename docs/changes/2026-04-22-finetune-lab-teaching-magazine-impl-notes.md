---
title: finetune-lab teaching magazine redesign
status: implemented
owner: claude
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/specs/2026-04-22-finetune-lab-frontend-lab-spec.md
  - docs/specs/2026-04-22-finetune-lab-ai-native-onboarding-and-teaching-spec.md
reviews: []
---

## 动机

先前的前端虽然覆盖了 onboarding / data / train / probe，但呈现更像结构化实验报告：米黄浅色、卡片堆叠、没有 training curve、before/after 停留在表格。对一个目标是"AI 微调学习热门开源项目"的仓库来说，缺第一屏冲击、缺教学叙事、缺截图传播点。

## 改动

### 数据层

- `project-context.json` 增加 `manifesto`、`agent_handoff_timeline`、`teaching_takeaways` 三块教学文案字段，保持"静态教学内容数据化"的原则。
- `web/scripts/build-lab-data.mjs`：
  - 读取每个 run 目录下的 `train-metrics.jsonl`，生成 `trainingCurve`（抽样到 ≤40 点，含 first/last loss 和 loss_delta_pct）。
  - 计算 `run_delta`（baseline vs improved：avg_loss 下降百分比、steps 倍数、exact/parsed/signal 的 delta）。
  - 把 manifesto / agent_handoff_timeline / teaching_takeaways 打到 payload。
- `web/src/data-layer.ts` / `web/src/types.ts` 同步新类型。

### IAB 静态页

`web/scripts/export-standalone-html.mjs` 按新 IA 重写：

1. Hero manifesto（big typography + 编号命令 + 4 个 KPI，含 "loss ↓%"）
2. Three tenets（agent-native / small loop / teach-by-diff）
3. Agent handoff timeline（sense → prepare → teach → compare，每步带 artifact 路径）+ readiness checklist + 可折叠 agent prompts
4. Data pipeline（样本 anatomy 三卡 + category/domain 分布）
5. Training curves（纯 SVG 画 loss 曲线，lime / magenta 两套色系）
6. Before / After（delta matrix 表，up/down/neutral 可视化 delta）
7. Probe cases（hit / miss 着色 + 双栏 raw output）
8. Teaching takeaways（编号卡，便于截图）
9. Footer（workflow map + 完整命令序列）

视觉切到 dark-ink + lime/magenta 配色，等宽数字 + big typography，加网格背景。保持纯单文件 HTML（CSS 内联、无外链 JS / 字体），`file://` 下可直接打开。

### React 前端

`web/src/App.tsx` + `web/src/styles.css` 同步 dark 主题，Overview 顶部换成 manifesto hero，并加 loss curve。导航增加 "Agent Handoff" 条目对应 timeline 视图。

## 验证

- `npm run sync-data` 输出 `lab-data.json`，含 2 个 run，曲线分别 20 / 40 采样点，run_delta.avg_loss_delta_pct=72.7%。
- `npm run build` 通过 tsc + vite + export-standalone，`web/dist/index.html` 1891 行，零外链 asset。
- IAB 主入口 `file:///Users/xforg/AI_SPACE/finetune-lab/web/dist/index.html` 保持可打开。

## 后续

- 如果后续加真实 MLX / Unsloth 训练路径，`train-metrics.jsonl` 和 `trainingCurve` 可以直接复用，不用改前端。
- manifesto / tenets / takeaways 做成数据驱动，以后只改 `project-context.json` 即可刷新文案，不用动渲染代码。
