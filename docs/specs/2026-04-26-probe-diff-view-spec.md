---
title: Probe Diff View Spec
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26 (implemented)
implements:
  - docs/changes/2026-04-26-probe-diff-view-impl-notes.md
reviews:
  - docs/reviews/2026-04-26-web-beginner-ux-questions-review.md
  - docs/reviews/2026-04-26-web-data-fidelity-review.md
---

## 目标

把当前 Probe Compare tab 里只显示 `raw_output` 的"每个 case 一条"视图，升级为 **input / expected / per-run actual** 三段对比视图，让小白能在一个屏幕里回答："**这一条期望模型做什么？哪些 run 做对了，哪些没做对？错在哪？**"

对应需求来自 [UX review F4](../reviews/2026-04-26-web-beginner-ux-questions-review.md)：

> Probe cases 区在右侧（被遮挡，需要继续滚），列出 case id（sft-v1-0xxx）。点进去能看具体的 input / expected / actual 对比吗？没明显的引导。

## 不在范围

- 不做字符级 diff（不引入 `diff` / `diff-match-patch` 等库）。
- 不改 probe 数据结构 / 不改 `inference-probe-results.json` 字段。
- 不做导出 / 分享单个 case 的功能。
- 不做按 category / behavior / risk 筛选 case（只做"分歧最大 / 全失败 / 单 run 通过"三个 saved-view，不做自由 filter）。
- 不替换现有的 9 张"Run comparison"汇总卡，那是横向口径；本 spec 只重做下半部分（case 详情）。

## 数据来源

从已有 `RunSummary.probeResults: ProbeResult[]` 取（[types.ts](../../web/src/types.ts)），每条 `ProbeResult` 至少含：

- 输入端：`prompt_user`、`loaded_tool_names`、`vehicle_state`、`expected_system_action`
- 期望端：`expected_names`、`expected_tool_calls`、`expected_assistant_content`、`behavior`、`risk`
- 实际端：`raw_output`、`parsed_output`、`predicted_names`、`predicted_tool_calls`、`predicted_behavior`、`output_shape`
- 命中标记：`exact_name_match`、`behavior_match`、`arguments_match`、`structured_output_valid`、`unsafe_direct_call`、`confirmation_contract_hit`、`refusal_contract_hit`

不需要新数据。同一 case_id 在多个 run 里出现，按 run 聚合。

## UI 结构

替换 [App.tsx#CompareView](../../web/src/App.tsx) 当前的"Probe cases 列表 + 每个 run 一段 raw_output"块，改为：

```
┌─ Run comparison（保留不动）──────────────────┐
│  20 张 compare-card（已实现）                 │
└──────────────────────────────────────────────┘
┌─ Probe cases ─────────┬─ Case detail ───────┐
│  saved views（新）     │  [Input] [Expected] │
│   • all-fail（N）     │  [Run actuals]      │
│   • split（N）         │                     │
│   • highest-divergence│                     │
│  case list（已有）    │                     │
└───────────────────────┴─────────────────────┘
```

### 区块 1：Saved views（新）

Case 列表上方加 3 个快捷视图按钮，每个显示数量徽章：

| view | 定义 | 教学价值 |
|---|---|---|
| `all-fail` | 所有 real run 都 `exact_name_match = false` 的 case | 最难的样本，模型集体没学会 |
| `split` | 至少一个 real run 通过、至少一个失败 | 区分能力：哪些 run 学到了 |
| `highest-divergence` | predicted_names 集合在不同 run 间差异最大的 case（用 Jaccard 距离平均值排序，取 top 5） | 最能体现 strategy / scale 影响 |

点 view 把 case 列表按这个集合筛一遍，再展示。

实现：在 `CompareView` 内 `useMemo` 算这三组的 caseId 列表。

### 区块 2：Case detail（替换现有 raw output 段）

选中一个 caseId 后，渲染三个并排 panel：

#### Panel 2.1 — Input（一份就够，case 级数据所有 run 共享）

来自任意一个 run 的 ProbeResult（取 runs[0].probeResults.find(id)）。展示：

- `prompt_user` —— 突出显示，用户级问题
- `loaded_tool_names` —— pill row，告诉小白模型"看到的"工具
- `vehicle_state` —— 简短一行（`speed_kph` / `power_state`）
- `expected_system_action` —— 如果非空，单独一栏

#### Panel 2.2 — Expected（同上，case 级）

- `behavior` —— 单 pill：`tool_call` / `clarify` / `confirm` / `reject` / `answer_only` / `handoff`
- `risk` —— 单 pill：`low` / `medium` / `high`
- `expected_names` —— 期望工具集合（pill 列表）
- `expected_tool_calls` —— 折叠 JSON
- `expected_assistant_content` —— 如果非空，markdown 展示
- 如果有 `expected_system_action`：显示 type + reason_code

#### Panel 2.3 — Per-run actuals（核心）

每个有这条 case 的 run 占一行（用现有 RunModeBadge 区分 SIM/REAL），按 5 列展示：

| 列 | 内容 | 视觉 |
|---|---|---|
| Run | run 标题 + RunModeBadge | 一行 |
| Pass pills | exact / behavior / args / parsed / signal 五个 chip | 命中 = 实色 lime；未命中 = 灰底 |
| Predicted names | predicted_names 集合 | pill 列表，**和 expected_names 做集合 diff**：匹配 = lime 边框；多余 = magenta 边框；缺失 = 在末尾用 strikethrough 灰色 pill 表示 |
| Predicted behavior | 一个 chip | behavior_match = lime；不一致 = red |
| Raw output | `<details>` 折叠，max-height 200px | 默认收起；展开后可滚 |

如果 `unsafe_direct_call` / `confirmation_contract_hit` / `refusal_contract_hit` 命中关键 contract，在 Run 列加一个红色或绿色徽章（`unsafe!` / `confirm ok` / `reject ok`），让 contract 类问题第一眼可见。

### 默认选中

`useState<selectedCaseId>` 初始值改为：优先 `highest-divergence` 第一个；如果没有 split / divergence，回退到 `caseIds[0]`。这样新手第一眼就能看到"不同 run 在同一题上判得不一样"的现象。

## 实现拆步

| # | 步骤 | 验证 |
|---|---|---|
| 1 | 在 `CompareView` 内提取 `casesByView`：`{ allFail, split, highestDivergence }` 三组 caseId 列表 | console 打印三组数量；split 应 ≥ 1 |
| 2 | 案例列表上方渲染 3 个 saved-view 按钮（带徽章），点击切换 `viewFilter` state | 切换后 `caseIds` 变化 |
| 3 | 抽出 `<CaseInputPanel>` / `<CaseExpectedPanel>` 组件，从 runs[0] 的命中实例取数据 | 选 case 后渲染 |
| 4 | 抽出 `<CaseRunRow>` 组件：5 列 + diff pills | 集合 diff 渲染正确 |
| 5 | 删除现有 "raw output 与命中情况" 一节，用新 detail 替换 | 视觉验收 |
| 6 | 默认选中 `highestDivergence[0] ?? splitFirst ?? caseIds[0]` | 首屏即看到分歧 case |
| 7 | 加 CSS：`case-detail-grid` / `case-runrow` / `pill-match` / `pill-extra` / `pill-missing` 等 | hover / 颜色对照清晰 |
| 8 | preview 验证：选一个 split case 看 actuals 行；选一个 all-fail case 看是否大面积红 / 灰 | 截图存档 |

## 成功标准

新手在不读代码、不查文档的前提下，看一条 case 能够回答以下问题：

1. "这条 case 让模型做什么？"（Input + Expected 两栏直接答）
2. "我看的这个 run 做对了没？"（Pass pills 一眼）
3. "做错的话，错在工具名 / 行为类型 / 参数 / JSON 结构哪一类？"（diff pill 颜色 + Pass pills）
4. "其它 run 在同一条 case 上的表现如何？"（per-run rows 横向对比）
5. "哪些 case 是'谁都不会'，哪些是'有人会有人不会'？"（saved views 的 `all-fail` / `split`）

## 风险

- **per-run rows 在 28 个 run 下会很长**。用 `max-height: 60vh + overflow: auto` 限制；且默认按 `metrics.total > 0` 过滤，只显示真正测过这条 case 的 run（沿用 J 段空 run 折叠的语义）。
- **Jaccard divergence 在 case 数 ≥ 96 的大 run 上 O(N²) run 对比**。可接受 —— 28 个 run × 96 case ≈ 2700 个，浏览器侧可即时算。如果未来 run 数 > 50，再考虑 worker 化。
- **default-select 高分歧 case** 可能反而让首次访客困惑（因为还没看汇总数字就先看到反例）。在 panel 顶部加一行小字提示："默认显示分歧最大的 case，便于看出不同 run 的判别差异"。

## 参考

- 当前实现：[web/src/App.tsx#CompareView](../../web/src/App.tsx)
- 数据 schema：[web/src/types.ts#ProbeResult](../../web/src/types.ts)
- 来源 review F4：[2026-04-26-web-beginner-ux-questions-review.md](../reviews/2026-04-26-web-beginner-ux-questions-review.md)
