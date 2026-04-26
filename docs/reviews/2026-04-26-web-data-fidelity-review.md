---
title: Web Data Fidelity Review
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26 (F1~F7 全部修复)
implements: []
reviews: []
---

# 2026-04-26 Web Data Fidelity Review

## 结论

对 `finetune-lab` 前端实验台展示数据相对于磁盘真实 artifact 的保真度做了一轮核对。

**结论：底层 artifact 没造假，但 `build-lab-data.mjs` 的采集口径和 `App.tsx` 的指标选取，使"页面看到的微调结果"与"磁盘上真实跑出来的微调结果"出现显著偏差。**
共发现 6 处问题，其中 2 处定级 P0（结构性失真）、3 处 P1（可解读性误导）、1 处 P2（计算 bug）。

> 2026-04-26 更新：F1~F7 已全部修复，详见文末"已修复"段。原"本次只做发现记录"段保留作为发现状态的存档。

## 核对范围

- 页面入口：`http://127.0.0.1:4173`（`npm run dev` 起的实时 dev server）
- 数据装配脚本：[web/scripts/build-lab-data.mjs](../../web/scripts/build-lab-data.mjs)
- 渲染入口：[web/src/App.tsx](../../web/src/App.tsx)
- 真实磁盘 artifact：`outputs/**/run-manifest.json`、`outputs/**/train-metrics.jsonl`、`outputs/**/inference-probe-results.json`、`data/sft/v1-seed-anchor-demo/samples.jsonl`

## 真实反映的部分（保持不变）

| 页面元素 | 数据来源 | 验证 |
| --- | --- | --- |
| `SAMPLES 100` | `data/sft/v1-seed-anchor-demo/samples.jsonl` | `wc -l = 100` |
| 数据集 category / behavior / risk 分布 | 同上，`countBy` 实时统计 | 计算逻辑正确 |
| 单 run 的 loss 曲线采样点 | `outputs/<run>/train-metrics.jsonl` | `sampleCurve` 等距抽样，无偏 |
| 单 run 的 `avg_loss / max_steps / training_mode` | `outputs/<run>/run-manifest.json` 原值透传 | 一致 |
| 单 run 的 probe 指标（exact / parsedJson / toolSignal） | `inference-probe-results.json` 实时 reduce | 计算逻辑正确 |
| Roadmap / Agent Handoff / Hero 文案 | `project-context.json` | 一致 |

## 发现

### F1（P0）页面只显示 9 个 run，磁盘上其实有 27 个

**现象**

`outputs/` 下按 `run-manifest.json` 计数共有 27 份。页面 `runs.length = 9`。

**机制**

[build-lab-data.mjs:84-125](../../web/scripts/build-lab-data.mjs) 的 `getRuns()` 只对 `outputs/<dir>/run-manifest.json` 一层做匹配，**不递归子目录**。所有分阶段 run 落在 `outputs/<run>/<stage>/run-manifest.json`，因此被静默忽略：

```
被漏掉（18 个）：
  stage-curriculum/{stage1-single-tool, stage2-reroute-meta, stage3-multi-tool}
  stage-curriculum-consolidation/stage4-consolidation         ← project-context 标记的 SOTA
  stage-curriculum-replay/{stage1, stage2, stage3}
  medium-stage-curriculum/{stage1, stage2, stage3}
  medium-stage-curriculum-consolidation/stage4-consolidation
  large-stage-curriculum/{stage1, stage2, stage3}
  large-stage-curriculum-consolidation/stage4-consolidation
  medium-cross-domain-focus/stage5-cross-domain
  medium-cross-domain-focus-refresh/stage6-micro-refresh
  tail-polish/stage5-focus
  tail-polish-refresh/stage6-micro-refresh
```

**后果**

`project-context.json#workflow_stages.real_train.current_findings` 中明确写着：

> curriculum + consolidation 目前是最好的真实 mixed-task 路径：7/8 exact_name_match、8/8 structured_output_valid、6/8 arguments_match。

这条仓库自我宣称的 SOTA 结论，**在前端任何位置都看不到**。data-scale-compare、curriculum vs replay、stage 间遗忘观察这些教学专题，全部失踪。

### F2（P0）Hero KPI 把训练 loss 当成模型质量指标

**现象**

Hero 显示 `LOSS ↓ 99.8%`，hint = "800-iter real MLX LoRA run"。该值取自 `latest.trainingCurve.loss_delta_pct`，定义为单条 run 内 train-metrics 首末两点的相对降幅（[build-lab-data.mjs:60-62](../../web/scripts/build-lab-data.mjs)），`latest` = 按 `max_steps` 升序排序后的最后一个 run。

**反例（同样在页面 9 个 run 范围内）**

| run | steps | loss drop | probe exact |
| --- | ---: | ---: | ---: |
| `gemma4-e2b-real-mlx-lora-medium` | 400 | 99.3% | **1/8 = 12.5%** |
| `gemma4-e2b-real-mlx-lora-medium-direct` | 400 | 99.6% | 43/48 = 89.6% |
| `gemma4-e2b-real-mlx-lora-mixed-3epoch` | 240 | 100% | 4/8 = 50% |
| `gemma4-e2b-real-mlx-lora-large-direct` | 800 | 99.8% | 80/96 = 83.3% |
| `gemma4-e2b-real-mlx-lora-small-direct` | 80 | 96.9% | 4/10 = 40% |

`medium` 是教科书级过拟合：训练 loss 几乎归零，held-out probe 只命中 1/8。Hero 选 `loss_delta_pct` 当门面，恰好和 [docs/ai/beginner-guide.md §5.3 / §5.5](../ai/beginner-guide.md) 要传达的"loss 下降 ≠ 学到了"完全相反。

**后果**

新手第一眼看到 99.8% 会得出"微调非常成功"的结论；但仓库内同时存在过拟合反例，且 hero 完全没有暴露这一点。

### F3（P1）simulated 与 real run 在同一列表里没有视觉区分

**现象**

`outputs/gemma4-e2b-mlx-demo-unsloth-vlm` 与 `outputs/gemma4-e2b-mlx-demo-unsloth-vlm-100step` 的 `training_mode = "simulated"`，不真正更新权重；其余 7 个为 `real-mlx-lora`。

页面 RUNS 计数把它们一并算入 `9`，Training Runs tab 里两类 run 卡片样式一致。100-step simulated run 显示 `exact 20/20` 完美 probe 结果。

**后果**

新手无法分辨"模型真的学会了"和"模拟链路在演戏"。这一点对教学型仓库尤其致命——`docs/ai/beginner-guide.md §3.1` 已经把"simulated vs real 是两条并行路径"作为概念重点，但页面没承接这条概念。

### F4（P1）跨 run 直接比较 probe 数字，未归一化测试集大小

**现象**

各 run 的 `inference-probe-results.json` 测试样本数差异显著：4 / 8 / 10 / 20 / 48 / 96。Run cards 直接展示 `exact 4/4`、`exact 1/8`、`exact 80/96`，没有强调样本量差距。

**后果**

`single-tool-control` 的 `4/4` 视觉上看起来比 `large-direct` 的 `80/96` 更"完美"。但前者只测了 4 个 case 且为窄域控制实验，后者测了 96 个 mixed-task case，二者不在同一口径下。

### F5（P1）Run 排序使用 `max_steps`，会和"时间最新"语义冲突

**现象**

[build-lab-data.mjs:121](../../web/scripts/build-lab-data.mjs) 用 `runs.sort((a, b) => a.manifest.max_steps - b.manifest.max_steps)`。Hero 的 `latest = runs[runs.length - 1]` 因此恒等于 step 最多的 run，不一定是时间上最新跑的 run。

**后果**

随着仓库继续跑实验，`latest` 永远会被 `large-direct`（800 步）这种长 run 锁住，新跑的更小但更优的 run（比如 stage-curriculum-consolidation，假设它将来被纳入展示后总步数仍小于 800）将始终排在它前面，Hero KPI 将不再随实验推进而更新。这条问题目前还没有被外部表象暴露，但属于潜伏的语义错误。

### F7（P1）Probe Compare 卡片副标题"held-out probe over N cases"硬编码取第一个 run 的样本数

**现象**

Probe Compare tab 上 9 张 run 卡每张副标题都写 `held-out probe over 8 cases`，但卡内分子/分母分别是 `4/4`、`14/20`、`4/10`、`20/20`、`1/8`、`43/48`、`80/96` 等等——分母明显不是 8。

**机制**

[App.tsx:1125](../../web/src/App.tsx)：

```tsx
<p className="mini-note">held-out probe over {props.runs[0]?.probeResults.length ?? 0} cases</p>
```

副标题取的是 `props.runs[0]?.probeResults.length`（首个 run，恰好是 12-iter demo run，probe 集合大小 = 8），而每张卡的 `metrics.total` 走的是各自 run 的真实样本数。

**后果**

读者会以为"9 个 run 都被同样的 8 个 case 评了，只是结果不同"，从而把 `1/8` 和 `80/96` 当成同尺度结果直接比较——和 F4 叠加之后，可解读性几乎归零。

正确写法应当是把 `over N cases` 移到每张卡内部，用各自 run 的 `metrics.total` 或 `probeResults.length`。

### F6（P2）`loss_delta_pct` 在 last_loss = 0.0 时返回 null

**现象**

[build-lab-data.mjs:62](../../web/scripts/build-lab-data.mjs)：

```js
const loss_delta_pct = firstLoss && lastLoss ? +(((firstLoss - lastLoss) / firstLoss) * 100).toFixed(1) : null;
```

`firstLoss && lastLoss` 是 JS 真值检查，`lastLoss === 0.0` 为 falsy，结果整体回退为 null。

**实例**

`outputs/gemma4-e2b-real-mlx-lora-single-tool-control/train-metrics.jsonl` 末尾连续多步 `loss = 0.0`（训练集被完全背下来）。该 run 在页面上 `loss drop = —`。

**后果**

**过拟合最严重的 run 反而失去 loss drop 数字**——和 F2 叠加之后，可解读性进一步劣化。
正确写法应当是 `firstLoss != null && lastLoss != null`（或更明确地 `Number.isFinite(firstLoss) && Number.isFinite(lastLoss)`）。

## 严重程度小结

| ID | 主题 | 级别 | 是否影响"微调结果可信度" |
| --- | --- | --- | --- |
| F1 | 漏 18 个 run（含 SOTA） | P0 | 是 |
| F2 | Hero KPI 选 train loss drop 当门面 | P0 | 是 |
| F3 | simulated / real 视觉无区分 | P1 | 是 |
| F4 | probe 跨 run 比较未归一化 | P1 | 是 |
| F5 | run 排序按 step，`latest` 语义错位 | P1 | 否（潜伏） |
| F6 | `loss_delta_pct` 真值 bug | P2 | 否（仅丢字段） |
| F7 | Probe Compare 副标题硬编码"over 8 cases" | P1 | 是 |

## 建议（不在本次执行）

后续若安排修复，建议按以下顺序，每项独立提交：

1. **修 F1**：`getRuns()` 改为递归扫描 `run-manifest.json`，并在 manifest schema 里补 `parent_run_id / stage_id` 字段，让前端能把同一条 curriculum 的多个 stage 折叠成一组展示。
2. **改 F2**：把 Hero KPI "LOSS ↓" 替换为"PROBE EXACT"（取所有 real run 中 probe 测试集 ≥ N 的最高 exact_name_match 比例），同时保留 loss drop 作为副指标但贴上"training-only"标签。
3. **修 F3**：在 Run cards 和 RUNS 计数旁加 `real / simulated` 徽章；考虑把 simulated run 默认折叠在二级视图。
4. **修 F4**：probe 数字始终带分母与背景（mixed-task vs single-tool）。
5. **修 F5**：把排序键换为 manifest 里的时间戳（若没有则补一个 `created_at`）。
6. **修 F6**：`firstLoss != null && lastLoss != null`。

## 参考

- 数据装配脚本：[web/scripts/build-lab-data.mjs](../../web/scripts/build-lab-data.mjs)
- 渲染入口：[web/src/App.tsx](../../web/src/App.tsx)
- 入门讲解：[docs/ai/beginner-guide.md](../ai/beginner-guide.md)
- 之前的前端验收 review：[2026-04-22-finetune-lab-frontend-lab-review.md](2026-04-22-finetune-lab-frontend-lab-review.md)
- 联动 review：[2026-04-26-web-beginner-ux-questions-review.md](2026-04-26-web-beginner-ux-questions-review.md)（J 段 P0 修复时已经把 F1 / F3 / F7 顺手处理了）

---

## 已修复（2026-04-26）

F1 / F3 / F7 在姊妹 review 的 J 段（P0 一轮）已修，下面这一轮把 F2 / F4 / F5 / F6 全部收口。

| ID | 修复内容 | 文件 |
| --- | --- | --- |
| F1 | `getRuns()` 改递归扫 `outputs/**/run-manifest.json`，从 9 → 28 个 run；nested run 的 `manifest.run_id` 自动 `{family}/{id}` 防 React key 冲突；新增 `family / is_top_level` 字段。`buildRunDelta` 限定 top-level real run 计算。 | [web/scripts/build-lab-data.mjs:84-150](../../web/scripts/build-lab-data.mjs) |
| F2 | Hero KPI 从 4 张扩成 5 张：新增 **`BEST PROBE EXACT`** 卡作为模型质量主指标（绿色 accent，挑选条件：所有 real run 中 `probe.total ≥ 8` 的最高 exact rate）。`TRAIN LOSS ↓` 保留但去 accent + 加"训练目标，越接近 100% 越要看是否过拟合"提示。验证：headline 现在显示 100% (96/96) from `large-stage-curriculum-consolidation/stage4-consolidation` —— 这正是 F1 当时抱怨"页面任何位置都看不到的 SOTA"。 | [web/src/App.tsx:174-242](../../web/src/App.tsx) |
| F3 | RunModeBadge 全站铺开（Run registry / Run metrics / Probe Compare / Training curves）；Training curves 颜色按 `training_mode` 分（SIM 粉 / REAL 绿）。 | [web/src/App.tsx:55-63](../../web/src/App.tsx) |
| F4 | Probe Compare 卡 + Run metrics dl 都加了 dataset 维度上下文：`scope v1-gemma4-e2b-single-tool-control · trained on 32 rows` vs `scope v1-gemma4-e2b-large · trained on 320 rows`。`datasetScope()` 从 `dataset_path` 取倒数第二段作为数据集家族名（因为 `dataset_role` 实测全部是 "train"，没有判别力）。Run comparison 副标题加一句"不同口径不要直接比"。 | [web/src/App.tsx:65-69, 1306, 1232](../../web/src/App.tsx) |
| F5 | `build-lab-data.mjs` 在每个 manifest 上挂 `completed_at`（用 `run-manifest.json` 文件 mtime，因为原 manifest 没有时间字段）。Hero headline 选 run 改为按 `completed_at` 排序，挑最近完成的 top-level real run。Run registry 排序仍按 `max_steps`（curriculum 内部从短到长可读性更好）。 | [web/scripts/build-lab-data.mjs:101-108](../../web/scripts/build-lab-data.mjs)、[web/src/App.tsx:178-183](../../web/src/App.tsx) |
| F6 | `firstLoss && lastLoss` 改成 `Number.isFinite(firstLoss) && Number.isFinite(lastLoss) && firstLoss !== 0`。验证：`single-tool-control` 等 last_loss = 0 的过拟合 run 现在显示 `↓ 100%` 而不是 `—`，过拟合反而成显眼信号。 | [web/scripts/build-lab-data.mjs:60-64](../../web/scripts/build-lab-data.mjs) |
| F7 | Probe Compare 卡片副标题改用每张卡 `metrics.total` 真实分母；section 副标题加说明；case 列表用所有 run 的 union。 | [web/src/App.tsx:1298-1304](../../web/src/App.tsx) |

### 顺带做的（不在 F1-F7 内但相关）

- 28 个 run 在 Run registry 用 `<details>` 按 family 折叠分组（否则铺平太挤）。
- Probe Compare 把 `metrics.total === 0` 的 8 个 curriculum 子 stage 折进 `<details>` 收尾，主 grid 从 28 → 20 张实卡。
- BehaviorEvalPanel 用 `${run_id}-${max_steps}` 作 React key，消除 3 个 stage4-consolidation 同 key 的告警。
- `manifest.train_row_count` 也透传到前端，Run metrics 加了 `train rows / completed` 两行。
- 类型补：`RunManifest` 加 `family / is_top_level / completed_at / train_row_count`。

### 验证

- `make web-build` 通过。
- preview 五张 KPI 卡显示：`BEST PROBE EXACT 100% (96/96 on held-out)`、`TRAIN LOSS ↓ 99.8%`，accent 转移到 BEST PROBE 卡。
- Probe Compare 实测：`4/4 scope v1-gemma4-e2b-single-tool-control · 32 rows` 和 `80/96 scope v1-gemma4-e2b-large · 320 rows` 视觉差异显著，不会被误读为同口径。
- 5 个 tab 全切完触发 0 个 React 错误。

### 没做（继续留给后续）

- 给 manifest schema 真补一个 `created_at` / `completed_at` 字段（目前依赖文件 mtime，跨机器拷贝时可能失真）。
- F2 提到的"训练 loss drop 标 training-only 标签"我用文案"训练目标"代替；如果想做更显眼的 chip，可以后续加。
- "页面把 simulated 默认折叠"还没做（J 段加了 SIM 徽章已能区分，但没默认折叠）。
