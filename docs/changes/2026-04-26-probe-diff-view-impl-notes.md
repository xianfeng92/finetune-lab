---
title: Probe Diff View Implementation Notes
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26
implements:
  - docs/specs/2026-04-26-probe-diff-view-spec.md
---

## 范围

按 [docs/specs/2026-04-26-probe-diff-view-spec.md](../specs/2026-04-26-probe-diff-view-spec.md) 实现，把 Probe Compare tab 下半部分（原"raw output 与命中情况"）替换成完整的 Input / Expected / Per-run actuals 三段对比视图。

## 改动

| 区块 | 内容 | 文件 |
| --- | --- | --- |
| Case 聚合 | `aggregateCases(runs)` 把所有 run × probe 摊开成 `Map<caseId, { caseId, perRun }>`；不依赖 runs[0] 的口径，多 run 都有的 case 会自动合并。 | [web/src/App.tsx:1289-1306](../../web/src/App.tsx) |
| 三组 saved view | `casesByView` memo 计算 `allFail`（所有 real run 都未通过 exact）、`split`（部分通过）、`highestDivergence`（real run 间 predicted_names Jaccard 距离平均值 top 5）。 | [web/src/App.tsx:1450-1470](../../web/src/App.tsx) |
| Case 列表筛选 | `viewFilter` state + 4 个按钮（all / highest-divergence / split / all-fail），每个按钮显示数量徽章。 | [web/src/App.tsx:1499-1519](../../web/src/App.tsx) |
| Input panel | `<CaseInputPanel>`：prompt_user 突出渲染、loaded_tool_names pill 列表、vehicle_state 行内代码。 | [web/src/App.tsx:1340-1366](../../web/src/App.tsx) |
| Expected panel | `<CaseExpectedPanel>`：behavior + risk pill、expected_names pill、expected_assistant_content、expected_system_action、expected_tool_calls JSON 折叠。 | [web/src/App.tsx:1368-1402](../../web/src/App.tsx) |
| Per-run row | `<CaseRunRow>`：5 个状态 pill（exact / behavior / args / parsed / signal）+ contract pill（unsafe / confirm / reject）+ 集合 diff（match / extra / missing）+ predicted_behavior + raw_output 折叠。 | [web/src/App.tsx:1404-1444](../../web/src/App.tsx) |
| 集合 diff | `<CasePillRow>` 组件：`match` lime 实色 / `+extra` magenta / `−missing` 灰底 + 删除线。 | [web/src/App.tsx:1322-1338](../../web/src/App.tsx) |
| 默认选中 | `selectedCaseId` 初始值优先 `highestDivergence[0]`，回退到 `split[0]`，再到 `caseIds[0]`。 | [web/src/App.tsx:1486-1497](../../web/src/App.tsx) |
| CSS | 新增 `.case-savedview / .case-detail-card / .case-pill / .case-runrow / .case-status-pill` 等约 100 行；`@media` 断点把网格折成 1 列。 | [web/src/styles.css:763-916](../../web/src/styles.css) |

## 决策与偏离

- spec 里写 saved view 默认 grid 1 列，实现里改成 2×2 grid（1100px 以下回退 1 列）。理由：4 个 view 一行排不下，2×2 视觉更紧凑。
- spec 里"per-run row 默认按 metrics.total > 0 过滤"实际没单独再过滤 —— `aggregateCases` 已经只把 case 出现过的 run 收进 `perRun`，等价于过滤。
- `arguments_match` 字段在 `ProbeResult` 类型里没声明，用 `(r as ProbeResult & { arguments_match?: boolean }).arguments_match` 拿；后续可以补类型。

## 验证

- `make web-build` 通过。
- preview 实测：默认进入 Probe Compare tab，下方自动选中 `sft-v1-0029`（highest-divergence top 1）。展示 4 个 run row：`80-iter real lora-small-direct` 显示红色 strikethrough `−hvac_set_temperature`（漏调用）+ 5 个 fail pill；同尺寸的 `lora-stage-curriculum-consolidation/stage4` 显示绿色 match + 5 个 ok pill。F4 review 关心的 input/expected/actual 三段对比已经一屏可见。
- 切到 `all-fail` view：visibleCases 从 163 → 1（sft-v1-0060），点进去 18 个 fail pill / 7 个 ok pill。
- 全 5 tab 切换 0 个 React 错误。

## 没做（spec 里也排除了）

- 字符级 diff（spec 明确不做）。
- expected_assistant_content 的 markdown 渲染（spec 没要求 markdown，纯文本足够）。
- per-case 单独导出 / 分享链接（spec 排除）。

## 参考

- spec：[docs/specs/2026-04-26-probe-diff-view-spec.md](../specs/2026-04-26-probe-diff-view-spec.md)
- review F4：[docs/reviews/2026-04-26-web-beginner-ux-questions-review.md](../reviews/2026-04-26-web-beginner-ux-questions-review.md)
