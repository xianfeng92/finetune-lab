# 2026-04-22 finetune-lab Gemma 4 E2B Learning Roadmap Review

## 结论

本轮对 `finetune-lab` 的 Gemma 4 E2B 学习路线图实现做了文档级验收。

结论：通过，无阻塞问题，路线图、Level 5 和 Level 6 的最小教学闭环已经成立。

## 核对范围

- Gemma 4 E2B 是否已成为默认教学基座
- 六阶段学习路线是否已经进入统一项目上下文和前端展示
- Level 5 的 structured outputs / tool calling 专题是否已形成可读产物
- Level 6 的 preference demo 和 scale-up compare 是否已形成最小闭环

## 核对结果

### 1. Gemma 主线已经明确

项目上下文已经把 `google/gemma-4-E2B-it` 固定为默认教学基座，并保留 `google/gemma-4-E2B` 与 `google/gemma-4-E4B-it` 的升级路径，符合 spec 的模型策略。

参考：

- `project-context.json`
- `README.md`

### 2. 六阶段路线图已进入前端教学视图

学习路线图、Gemma track 和参考项目区块已经进入 React 前端和 IAB 静态页，说明 roadmap 已从文档概念进入用户可见界面。

参考：

- `web/src/App.tsx`
- `web/scripts/export-standalone-html.mjs`
- `web/public/lab-data.json`

### 3. Level 5 专题产物已落地

仓库已经提供 tool-routing dataset pack 和 structured-output probe pack，能够支持 route selection、JSON validity 和 tool choice accuracy 的教学展示。

参考：

- `outputs/level5/tool-routing-dataset-pack.json`
- `outputs/level5/structured-output-probe-pack.json`
- `training/finetune/post_train_probe.py`

### 4. Level 6 已形成最小 post-training 教学闭环

仓库已经具备 preference pairs、policy compare 和 Gemma scale-up compare，能够解释 `chosen / rejected`、行为偏好差异以及何时继续留在 `E2B-it`、何时考虑升级到 `E4B-it`。

参考：

- `data/preferences/v1-gemma4-e2b-demo/pairs.jsonl`
- `outputs/level6/preference-dataset-pack.json`
- `outputs/level6/policy-compare-report.json`
- `outputs/level6/gemma-scale-up-compare.json`

## 剩余风险

- `Level 6` 目前在路线图里仍是 `partial`，说明真实 scale-up 实验还没有完全收口。
- 当前 Level 6 已经有更明确的 compare rubric 和成本视角，但还缺真正的 `E4B-it` 确认性实验记录。
