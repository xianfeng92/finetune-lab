# finetune-lab web

AI-native 微调教学实验台。所有视图都从一次构建时聚合的 `web/public/lab-data.json` 读数据，页面本身不扫描仓库。

## 两种形态

- **React 前端**（`web/src/*`）：通过 `make web-dev` / `make web-build` 运行，开发时用。
- **IAB 静态页**（`web/dist/index.html`）：零依赖单文件，兼容 `file://`，是当前主要展示入口。由 `scripts/export-standalone-html.mjs` 导出。

## 信息架构

IAB 静态页按下列顺序讲一条完整故事：

1. Hero manifesto — "Clone it / Hand it to an agent / Watch a model learn"
2. Three tenets — agent-native / small loop / teach-by-diff
3. Agent handoff timeline — sense → prepare → teach → compare
4. Data pipeline — 样本 anatomy + category / domain 分布
5. Training curves — 每个 run 的 loss 曲线（直接读 `train-metrics.jsonl`）
6. Before / After — baseline 和 improved run 的 delta matrix
7. Level 5 pack — tool-routing dataset pack + structured-output probe pack
8. Level 6 demo — preference pair dataset + policy compare + scale-up guidance
9. Probe cases — case 级 exact / miss 对比
10. Teaching takeaways — 跑完一轮应当能解释的四条结论

## 数据层入口

```bash
npm run sync-data     # 生成 web/public/lab-data.json 和 src/generated/lab-data.generated.ts
npm run build         # tsc + vite build + 导出 IAB 单文件
```

`build-lab-data.mjs` 会自动聚合：

- dataset samples + summary
- run manifest + probe + artifacts
- `train-metrics.jsonl` → training curve（自动抽样到 ≤40 个点）
- run delta（baseline vs improved）
- Level 5 packs（tool-routing / structured-output）
- Level 6 demo（preference dataset / policy compare）
- onboarding report
- manifesto / agent handoff timeline / teaching takeaways（来自 `project-context.json`）
