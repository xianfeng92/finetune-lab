---
title: finetune-lab Gemma 4 E2B learning roadmap
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/specs/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-spec.md
reviews: []
---

## 动机

Claude 刚把前端从“实验报告页”推进成了更有产品感的教学页，但它还没有真正接上 `Gemma 4 E2B` 六阶段学习主线。页面能展示当前 run，却还不能清楚回答：

- 为什么默认从 `google/gemma-4-E2B-it` 开始
- 当前项目已经覆盖到哪个 level
- 下一阶段最值得补的是哪条学习路径
- 可以从热门微调开源项目学什么结构经验

这轮改动的目标，就是把这些问题做成前端和 IAB 都能直接读取的统一元数据。

## 改动

### 1. `project-context.json` 新增学习路线图元数据

新增三块数据：

- `gemma_track`
  - 默认教学基座、对照模型、专题化重点、升级路径
- `learning_roadmap`
  - 六个 level 的状态、目标、意义、命令、产物、关注指标、常见误区
- `reference_projects`
  - LLaMA-Factory / Unsloth / LitGPT / Alignment Handbook 的结构化借鉴点

这样仓库的“教学叙事”不再散落在文档和代码里，而是可以被前端和 agent 统一消费。

### 2. 统一数据层把路线图打进 `lab-data.json`

`web/scripts/build-lab-data.mjs` 现在除了 dataset、runs、probe、run_delta，还会同步：

- `gemma_track`
- `learning_roadmap`
- `reference_projects`

`web/src/data-layer.ts` 也补了相应类型，React 和 IAB 都可以直接读。

### 3. React Overview 变成“路线图首页”

`web/src/App.tsx` 的 Overview 新增三块：

- `Gemma 4 E2B six-level learning roadmap`
  - 6 张 level 卡片，显示 `live / partial / next / planned`
- `Gemma 4 E2B is the default teaching spine`
  - 解释为什么默认从 `google/gemma-4-E2B-it` 开始，再对照 `google/gemma-4-E2B`
- `What to steal from hot open-source labs`
  - 把热门项目抽象成定位和结构经验，而不是简单列名字

`web/src/styles.css` 同步增加了 roadmap / track / reference 的暗色主题样式。

### 4. IAB 静态页同步接上路线图

`web/scripts/export-standalone-html.mjs` 新增了 `renderRoadmapBlock(data)`，并插入到 Hero / Tenets 之后。

IAB 现在也能直接展示：

- Gemma 4 E2B 路线图
- 默认教学基座与对照模型
- structured outputs / tool calling 专题化方向
- 热门开源项目的经验抽取

这样 `file://` 主展示页和 React 开发版不再出现叙事割裂。

## 验证

- `make web-build`
  - 通过 `sync-data + tsc + vite build + export-standalone`
- `web/public/lab-data.json`
  - 已包含 `gemma_track`、`learning_roadmap`、`reference_projects`
- `web/dist/index.html`
  - 已包含 Gemma 4 路线图区块，且继续兼容 `file://`

## 当前结论

这轮之后，前端已经不只是“当前实验结果展示”，而是开始承担：

- 解释项目为什么以 Gemma 4 E2B 为主线
- 告诉用户当前已经覆盖到哪几个学习 level
- 告诉用户后续最值得补的是 structured outputs / tool calling 与 preference tuning

下一步最自然的延伸，就是把 Level 5 的专题数据包和 probe 视图真正做出来，让页面里的路线图和仓库里的实验入口完全对齐。
