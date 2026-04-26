---
title: finetune-lab Level 5 tool routing and structured output pack
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/specs/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-spec.md
reviews: []
---

## 动机

此前 Level 5 只停留在路线图文案里，还没有真正的专题产物。页面虽然写了 `Structured Outputs and Tool Calling`，但仓库里还没有：

- tool-routing dataset pack
- structured-output probe pack
- 对应的标准入口

这会让 Level 5 看起来像“下一步想法”，而不是当前仓库已经能学的内容。

## 改动

### 1. 新增标准入口

`Makefile` 新增：

- `make level5-pack`

并把它接入 `make ai-lab`，这样最小闭环跑完 probe 后，会顺手生成 Level 5 专题包。

### 2. probe 结果补充结构化输出字段

`training/finetune/post_train_probe.py` 现在会额外写出：

- `output_shape`
- `json_valid`
- `structured_output_valid`
- `predicted_tool_calls`
- `predicted_tool_call_count`
- `arguments_match`

这样同一份 probe 结果就能区分：

- 只是挑对了工具名
- 还是已经学会输出 `tool_calls` 数组
- 连 arguments 结构也一起学会了没有

本轮模拟结果里：

- 20-step run：`tool_name_only`
- 100-step run：`tool_calls_array`

这正好形成了一个很适合教学的 Level 5 对照。

### 3. 新增 Level 5 pack 生成脚本

新增 [training/finetune/build_level5_pack.py](/Users/xforg/AI_SPACE/finetune-lab/training/finetune/build_level5_pack.py:1)，生成：

- `outputs/level5/tool-routing-dataset-pack.json`
- `outputs/level5/tool-routing-dataset-pack.md`
- `outputs/level5/structured-output-probe-pack.json`
- `outputs/level5/structured-output-probe-pack.md`

其中：

- `tool-routing dataset pack`
  - 聚合 route counts、candidate histogram、focus samples
- `structured-output probe pack`
  - 聚合各 run 的 `tool_name_only` / `tool_calls_array` / `arguments_match`
  - 对齐 case-level compare

### 4. 统一数据层和前端接入

`web/scripts/build-lab-data.mjs` 现在会把 Level 5 packs 打进 `lab-data.json`。

React 前端：

- [web/src/App.tsx](/Users/xforg/AI_SPACE/finetune-lab/web/src/App.tsx:1)
  - Overview 新增 `Level 5: Structured Outputs and Tool Calling`
- [web/src/styles.css](/Users/xforg/AI_SPACE/finetune-lab/web/src/styles.css:1)
  - 增加 Level 5 专题卡片样式

IAB 静态页：

- [web/scripts/export-standalone-html.mjs](/Users/xforg/AI_SPACE/finetune-lab/web/scripts/export-standalone-html.mjs:1)
  - 新增 `Level 5 pack` 区块
  - 直接展示 `tool_calls 0/5 -> 5/5`、`tool_name_only -> tool_calls_array`

### 5. 项目元数据同步

更新了：

- `project-context.json`
- `docs/ai/workflows.md`
- `README.md`
- `web/README.md`

现在 Level 5 在仓库元数据里已经从 `next` 切到 `live`，并且 commands / artifacts 都是实际可跑、可读的路径。

## 验证

本轮实际跑过：

- `make probe-mac`
- `make probe-mac-100`
- `make level5-pack`
- `make web-build`

关键结果：

- 20-step probe summary：
  - `tool_name_only = 5/5`
  - `tool_calls_array = 0/5`
- 100-step probe summary：
  - `tool_name_only = 0/5`
  - `tool_calls_array = 5/5`
- `web/dist/index.html`
  - 已包含 `06 · Level 5 pack`

## 当前结论

Level 5 现在已经不再只是路线图文案，而是有：

- 标准入口
- 专题产物
- 前端展示
- IAB 展示

下一步如果要继续往前走，最自然的是：

- 把 Level 5 的 dataset/probe 从当前 demo 进一步扩到更像真实 agent 的 tool-routing 场景
- 再往 Level 6 的 preference tuning demo 推进
