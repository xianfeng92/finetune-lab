---
title: Edge Bench W5 docs implementation notes
status: implemented
owner: codex
created: 2026-04-28
updated: 2026-04-28
implements:
  - /Users/xforg/AI_SPACE/DecisionF/docs/changes/2026-04-28-finetune-edge-bench-w2-impl-notes.md
---

# Edge Bench W5 Docs Implementation Notes

## Summary

按照 W2 交接里的推荐路径，优先完成 W5 的文档化输出，而不是进入可选 W3 Android NDK：

- 新增 `edge-bench/README.md` 作为子项目入口。
- 新增 `edge-bench/docs/05-benchmark-results.md`，汇总 W2 五组 baseline 数据、产物路径和 4 维雷达图。
- 新增 `edge-bench/docs/06-policygateway-cross-engine.md`，写清楚 PolicyGateway 跨引擎差异、非量化根因和 KV-sharing 推理失效链路。
- 新增 `edge-bench/docs/07-pitfalls-and-decisions.md`，沉淀 W2 避坑表和当前 path (b) 决策。
- 新增 `edge-bench/docs/08-blog-draft.md`，作为 W5 技术博客主稿草稿。
- 更新主 `README.md`，把 Edge Inference Bench 加入项目首屏和 workflow 表。
- 更新 AI 平台版简历草稿，补入 N=2 完整 LoRA 对照 + LiteRT base-only fallback 的真实措辞。

## Data Used

本次没有重跑 144-case 推理，直接读取本地 W2 产物：

- `outputs/edge-bench/baselines/mlx-stage4-strict/inference-probe-report.md`
- `outputs/edge-bench/baselines/llama_cpp-stage4-fp16-strict/inference-probe-report.md`
- `outputs/edge-bench/baselines/llama_cpp-stage4-Q4_K_M-strict/inference-probe-report.md`
- `outputs/edge-bench/baselines/litert_lm-base-strict/inference-probe-report.md`

关键结论保持 W2 口径：

- MLX LoRA：`144/144 behavior`、`0/144 unsafe`、`12/12 confirm`、`12/12 refusal`。
- llama.cpp fp16：`87/144 behavior`、`24/144 unsafe`、`0/12 confirm`、`0/12 refusal`。
- llama.cpp Q4_K_M：`86/144 behavior`、`24/144 unsafe`、`0/12 confirm`、`0/12 refusal`。
- LiteRT-LM：base-only fallback，不计入同一 LoRA 三引擎一致性结论。

## Remaining

- 如果要真正完成 W5-1 的“发表”，还需要把 `edge-bench/docs/08-blog-draft.md` 按目标平台格式做最后润色并发布。
- W5-3 已先更新 AI 平台版简历草稿；Edge 版简历是否也同步，留给下一轮按投递方向决定。
- W3 Android NDK 仍是可选项，不阻塞当前博客主线。
