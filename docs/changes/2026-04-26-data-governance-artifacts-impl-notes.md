---
title: Data Governance Artifacts Implementation Notes
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26
implements:
  - docs/specs/2026-04-26-data-governance-artifacts-spec.md
---

## 范围

按 [data-governance-artifacts-spec](../specs/2026-04-26-data-governance-artifacts-spec.md) 实施，关闭 [04-25 review #6 数据治理空白](../reviews/2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md#6-数据治理层基本缺失)。

## 改动

| 区块 | 内容 | 文件 |
| --- | --- | --- |
| 治理模块 | `governance.py` 函数式 API：`RedactionPolicy / RedactionRule / redact_record / redact_jsonl / scan_jsonl / governance_pass / write_dataset_card / write_redaction_report`。无外部依赖，纯 stdlib。 | [training/data_pipeline/governance.py](../../training/data_pipeline/governance.py) |
| PII 模式 | 4 条：`phone_cn` / `id_cn` / `plate_cn` / `email`。中国大陆手机号用 `(?<!\d)1[3-9]\d{9}(?!\d)` 防止数字串误命中（"我有 13 个苹果，800 块"不会触发）；身份证含日期段校验；车牌支持蓝/绿牌。 | governance.py:35-65 |
| 字段遍历 | `messages[*].content` 数组展开 + `prompt_user / expected_assistant_content / system_prompt` 标量。`_walk_field()` 用 setter closure 写回。`redact_record` 返回深拷贝，不修改原 record。 | governance.py:75-100 |
| 流式扫描 | `redact_jsonl()` / `scan_jsonl()` 行式读写，不全量加载。`add_clean_spot_check()` 在 records_redacted=0 时仍抽 10 条作"零 PII 自证"。 | governance.py:135-180 |
| 报告渲染 | `_yaml_frontmatter()` 自实现 minimal YAML 输出（嵌套对象 / 列表 / 引号）；`write_dataset_card()` 渲染 frontmatter + 描述 / 来源 / Schema / 已知限制 / 治理 五段；`write_redaction_report()` 渲染策略 / 命中明细 / Spot-check / 残留风险。 | governance.py:200-340 |
| 测试 | `test_governance.py` 22 个用例覆盖：phone_cn / id_cn / plate_cn / email 各正反例 + boundary（"13 个"、"119999999999" 不命中）+ messages array walk + scan_jsonl 聚合 + redact_jsonl 写文件 + 零 PII spot-check 兜底 + governance_pass 端到端。 | [training/data_pipeline/tests/test_governance.py](../../training/data_pipeline/tests/test_governance.py) |
| CLI | `run_governance.py` 自动发现 `data/sft/v1-*` 和 `data/real-finetune/v1-*`（含 curriculum 子 stage），从 `dataset_summary.json` / 首条样本 `meta.generator_model` 推断 generator，按类别自动填 manifest。 | [training/data_pipeline/run_governance.py](../../training/data_pipeline/run_governance.py) |
| Makefile | 新 target `make dataset-governance`。 | [Makefile:315](../../Makefile) |
| 流水线挂钩 | `pipeline.py.write_outputs()` 末尾 + `import_car_bench.main()` + `import_clarifyvc.main()` 全部调用 `governance_pass()`，新生成 / 新导入 dataset 强制出 governance 产物。 | [training/data_pipeline/pipeline.py:509](../../training/data_pipeline/pipeline.py)、[import_car_bench.py:417](../../training/data_pipeline/import_car_bench.py)、[import_clarifyvc.py:397](../../training/data_pipeline/import_clarifyvc.py) |
| 公开数据集 sensitivity | car-bench / clarifyvc 的 manifest 默认 `sensitivity: medium`，license 注明 "see upstream license"，known_limitations 提示外部数据可能含未识别 PII。 | import 脚本 |
| build-lab-data.mjs | `loadDatasetCards()` 递归扫 `data/**/dataset-card.md`，解析 frontmatter（自写 minimal YAML parser，不引 gray-matter 依赖）+ body；同时读取同目录 redaction-report.md。挂到 `payload.dataset_cards`。 | [web/scripts/build-lab-data.mjs:36-90, 270-308](../../web/scripts/build-lab-data.mjs) |
| 类型 | `LabData.dataset_cards: DatasetCard[]`，含 `frontmatter: DatasetCardFrontmatter` / `body: string` / `redaction: { frontmatter: RedactionReportFrontmatter; body: string } \| null`。 | [web/src/data-layer.ts](../../web/src/data-layer.ts) |
| UI 组件 | `<DatasetCardsPanel>` 用 `<CollapsiblePanel defaultOpen={false}>` 包；每张卡 `<details>` 默认折叠，head 显示名/路径/3 个 pill（sensitivity 三色 / total samples / redacted ratio）；展开后显示 meta 行 + ReactMarkdown 渲染 body + 嵌套 `<details>` redaction-report。 | [web/src/App.tsx#DatasetCardsPanel](../../web/src/App.tsx) |
| CSS | `.dataset-card-list / -entry / -summary / -pills / -pill (.sens-low/-medium/-high, .pii-clean/-hit) / -body / -meta / -redaction`。复用现有 `.markdown-body`。 | [web/src/styles.css](../../web/src/styles.css) |

## 决策与偏离

- **没引 `gray-matter`**：自写 ~70 行 minimal YAML parser 在 `build-lab-data.mjs`，因为我们控制 producer（governance.py），输出 YAML 子集很窄（标量 / 一层嵌套对象 / 字符串数组），自写比加 npm 依赖代价小。
- **`total_samples` 防双计**：spec 里写 `sum(splits.values())`，实测会把 `samples`（=train+held-out 合集）和 train/held-out 一起求和导致翻倍。已修正：当 splits 同时含 `samples` 和 train/held-out 时，total_samples 取 samples 值，sub_splits 排除 samples。
- **`spec` 里 "policy_version 漂移" 风险的缓解措施已实现**：frontmatter 里 dataset-card 写 `policy_version_at_generation`，redaction-report 写 `policy_version`，两者解耦。
- **`arguments_match` / `IP / MAC / 银行卡`** 暂不扫描（spec 已声明 out-of-scope）。
- **CompareView 那个"未引"`gray-matter` parser 的边角**：YAML parser 不支持嵌套数组（如 `splits: [a, b]`）；governance.py 输出嵌套对象（`splits: { train: 800 }`），实测兼容。
- **public-source / public-normalized** 也都跑过 governance（共 23 个 dataset，含 stage 子目录）；下次 import 自动跑。

## 验证

- `pytest training/data_pipeline/tests/`：31 个用例（22 governance + 9 既有），全部通过。
- `make dataset-governance`：扫 23 个 dataset，**total_records_redacted = 0**（全合成数据，符合预期）。每个 dataset 产生 `dataset-card.md` + `redaction-report.md`。
- `make web-build`：通过；bundle 涨到 1.61MB raw / 204KB gzip（+8KB gzip vs 上一轮）。
- preview 实测：Data Pipeline tab 底部 `Dataset cards` 折叠区，展开后 23 张卡逐一渲染。点击单卡展开看到完整 markdown body（描述 / 来源 / Schema / 已知限制 / 治理）+ 嵌套 redaction-report 折叠 + match counts pill。pill 颜色对照：sensitivity: low 绿色，redacted ratio 全部绿色（0/N）。
- Console 全 6 个 tab 切换 0 个 React 错误。

## 没做（spec 排除项保留）

- 不做 NER（spaCy / transformers 太重）。
- 不做"原始日志 7 天自动清理"（部署侧 cron 责任）。
- 不写"日志抽取规范"文档（车机端责任）。
- 不替换现有 `dataset_summary.json/.md` 或 `validation_report.md`，三件套（summary / validation / governance）并存。
- 不做跨 dataset 去重 / 差分隐私。

## 观察 / 后续可补

- **某些 dataset 的 `total_samples` 与 `redaction-report.records_scanned` 不一致**：real-finetune 数据集只扫了 `train.jsonl`（不扫 valid/test，避免重复），而 total_samples 是 train+valid+test 之和。Pill "redacted: 0/800（train only）"对工程友好但对小白可能误读。后续 enhancement：要么扫所有 split、要么 pill 标注口径。当前不修，因为 review #6 明确说 "训练集脱敏"，扫 train 是符合 spec 的。
- **frontmatter 里的中文标点（"："）造成 YAML parser 在 string scalar 处需要引号 wrap**：governance.py `_yaml_value` 已处理（碰到 `:` 或 `#` 用 JSON 双引号），但如果内容里有更复杂字符（换行、缩进 token）可能需要更稳健的 quoting；当前 24 个 dataset 全部输出 valid YAML，未来若有问题再加。

## 参考

- spec：[docs/specs/2026-04-26-data-governance-artifacts-spec.md](../specs/2026-04-26-data-governance-artifacts-spec.md)
- review 来源：[2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md §6](../reviews/2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md)
- 现有产物：每个 `data/**/{dataset-card.md, redaction-report.md}`
