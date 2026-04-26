---
title: Data Governance Artifacts Spec
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26 (implemented)
implements:
  - docs/changes/2026-04-26-data-governance-artifacts-impl-notes.md
reviews:
  - docs/reviews/2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md
---

## 目标

补齐 [2026-04-25 review #6](../reviews/2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md#6-数据治理层基本缺失) 指出的数据治理空白：每个 dataset 目录除 `samples.jsonl / dataset_summary.{json,md} / validation_report.md` 外，再多两个产物：

- **`dataset-card.md`** —— 人 + agent 都能读的"数据目录条目"。描述、来源、size、splits、license、sensitivity 评级、生成器型号、生成时间。
- **`redaction-report.md`** —— 治理审计：本批数据应用了哪些脱敏规则、命中数、spot-check 样本、残留风险。

走"管道存在 + 跑一遍 + UI 暴露"路径（review 讨论时的方案 c）。

理由：当前仓库数据 99% 是合成数据（`generator_model` 字段标识），PII 风险极低；但 `data/public-source/{car-bench, clarifyvc}` 已经在引入外部公开数据，未来还可能接车机真实日志。**先把治理框架建好，等真实日志来了直接接，比之后回过头补要稳。**

## 不在范围

- **不引入 NER**（spaCy / transformers 太重，误判多）。姓名靠"模板级 placeholder 替换"在生成端控制，不靠运行时识别。
- **不实现"原始日志最长保留 7 天"自动清理**。retention policy 是部署侧问题，governance 模块不动文件系统层面调度；只在 dataset-card 里**记录**该 dataset 来自的原始日志保留窗口。
- **不做 cross-dataset 去重 / 差分隐私**。后续 spec。
- **不替换 / 删除现有 `dataset_summary.json/.md` 或 `validation_report.md`**。这两个分别承担"统计描述"和"schema/contract 校验"，跟 governance 是不同角色。dataset-card 在内容上有一点重叠（描述、size），但侧重点是**数据治理元信息**。
- **不写真正的"日志抽取规范"文档**（review 第 6 项提到了这个）。日志抽取属于上游（车机端），finetune-lab 是下游消费者。本 spec 只规定**消费侧的入境 contract**。

## 数据流

```
原始数据（合成 generator / 公开 dataset / 真实日志）
   ↓
training/data_pipeline/ 现有生成 / import 链路
   ↓
governance.redact_record(record, policy)  ← 新增
   ↓ 命中计数 + 脱敏后样本
samples.jsonl / train.jsonl / held-out.jsonl
   ↓
governance.write_dataset_card(...)   ← 新增  →  dataset-card.md
governance.write_redaction_report(...) ← 新增  →  redaction-report.md
   ↓
build-lab-data.mjs 读 dataset-card.md → labData.dataset_cards
   ↓
web 前端 Data Pipeline tab 渲染
```

## 新产物 schema

### `dataset-card.md` — frontmatter + body

```markdown
---
name: v1-seed-anchor-demo
version: 1.0
generated_at: 2026-04-22T10:30:00+08:00
generator: synthetic-claude (claude-sonnet-4-6)
total_samples: 100
splits:
  train: 80
  held-out: 20
  valid: 0
  test: 0
license: internal-research-only
sensitivity: low
pii_scanned: true
pii_redacted_count: 0
schema:
  - DatasetSample (training/types or web/src/types.ts)
links:
  redaction_report: ./redaction-report.md
  validation_report: ./validation_report.md
  dataset_summary: ./dataset_summary.md
---

## 描述
（一段中文：这份数据是干什么用的、教学目标是什么、不能拿去做什么）

## 来源 / Provenance
- 生成器：synthetic-claude
- 种子：seed-anchor schema v1
- 不包含：真实用户对话、车机日志、地理定位
- 包含：合成的多轮 tool-call 演示样本

## Schema
（指向 types.ts DatasetSample，不重复字段定义）

## 已知限制
（明确写：合成数据无法覆盖真实方言、口语化、跨说法，任何上线前必须用真实样本回归）

## 治理
- 脱敏策略：见 redaction-report.md
- schema 校验：见 validation_report.md
- 统计描述：见 dataset_summary.md
```

### `redaction-report.md` — frontmatter + body

```markdown
---
dataset: v1-seed-anchor-demo
generated_at: 2026-04-22T10:30:00+08:00
policy_version: 1.0
records_scanned: 100
records_redacted: 0
match_counts:
  phone_cn: 0
  id_cn: 0
  plate_cn: 0
  email: 0
fields_scanned:
  - prompt_user
  - expected_assistant_content
  - messages[*].content
spot_check_count: 10
---

## 应用的策略

### phone_cn
正则：`(?<!\d)1[3-9]\d{9}(?!\d)` → 替换为 `[PHONE_REDACTED]`

### id_cn
正则：18 位身份证（含 X 校验位） → 替换为 `[ID_REDACTED]`

### plate_cn
正则：蓝牌 / 绿牌 / 黄牌 → 替换为 `[PLATE_REDACTED]`

### email
正则：标准 email → 替换为 `[EMAIL_REDACTED]`

## 命中明细
（如果 `records_redacted > 0`，列每个命中的 record id + 字段 + 命中类型 + 命中数；如果是 0，明确写 "本批无命中"）

## Spot-check（10 例）
随机抽 10 条原始 record（脱敏前）做人工抽查，按字段列出原文片段。如果 `records_redacted = 0`，仍然抽 10 条贴出来作为"零 PII"自证。

## 残留风险
- 模板里的人名（"小明 / 李四"）属于合成数据集中的占位，未做识别处理
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如"幺三八……"）
- 不做 NER，不识别非结构化人名
```

## 模块设计

### `training/data_pipeline/governance.py`

函数式 API（无类，无状态）：

```python
@dataclass
class RedactionPolicy:
    version: str
    rules: list[RedactionRule]
    
@dataclass
class RedactionRule:
    name: str
    pattern: re.Pattern
    replacement: str
    fields: list[str]  # which record fields to scan; "messages[*].content" supported

@dataclass
class RedactionResult:
    record_redacted: dict
    match_counts: dict[str, int]  # rule_name -> count
    redacted_fields: list[str]

def default_policy() -> RedactionPolicy:
    """phone_cn, id_cn, plate_cn, email — covered. No NER."""

def redact_record(record: dict, policy: RedactionPolicy) -> RedactionResult: ...

def redact_jsonl(input_path: Path, output_path: Path, policy: RedactionPolicy) -> AggregateRedactionStats: ...

def write_dataset_card(dataset_dir: Path, summary: DatasetSummary, redaction_stats: AggregateRedactionStats, manifest: DatasetCardManifest) -> Path:
    """渲染 dataset-card.md"""

def write_redaction_report(dataset_dir: Path, policy: RedactionPolicy, stats: AggregateRedactionStats, samples: list[dict]) -> Path:
    """渲染 redaction-report.md"""
```

### 触发时机

- **现有合成数据**：新 make target `make dataset-governance` 一次性扫所有 `data/sft/v1-*` 和 `data/real-finetune/v1-*`，产物落到各自目录。
- **新数据生成流水线**：`training/data_pipeline/pipeline.py` 在 `samples.jsonl` 写完后调 `governance.redact_jsonl(...)` 顺手出报告。
- **公开数据集导入**：`training/data_pipeline/import_car_bench.py` / `import_clarifyvc.py` 在 normalized 后强制走 redaction。

## PII 模式

仅启用以下 4 条（review #6 关心的最小集 + 合理覆盖车机场景）：

| name | pattern | 替换 |
|---|---|---|
| `phone_cn` | `(?<!\d)1[3-9]\d{9}(?!\d)` | `[PHONE_REDACTED]` |
| `id_cn` | `(?<!\d)[1-9]\d{5}(?:19\|20)\d{2}(?:0[1-9]\|1[0-2])(?:0[1-9]\|[12]\d\|3[01])\d{3}[\dX](?!\d)` | `[ID_REDACTED]` |
| `plate_cn` | 含 7-8 位规则的蓝/绿牌 | `[PLATE_REDACTED]` |
| `email` | 标准 email regex | `[EMAIL_REDACTED]` |

**不做**：姓名 NER、IP / MAC（车控场景几乎不出现）、银行卡号（不在领域内）。

如果未来真实日志接入需要更多模式，扩展 `default_policy()` 即可，不破坏 schema。

## 扫描字段

policy.rules[*].fields 支持的字段路径：

- `prompt_user`
- `expected_assistant_content`
- `messages[*].content` —— 数组字段展开扫描
- `system_prompt` —— **默认包含**，因为 system prompt 里有 `vehicle_state` 等结构化数据

不扫描：`expected_tool_calls.arguments`（结构化字段，由 schema validation 保证形状；如果 arguments 里有手机号那是数据 bug）、`raw_output` / `predicted_*`（probe 产物，不进训练集）。

## UI 暴露

Data Pipeline tab 加新 panel：

```
┌─ Dataset cards ───────────────────────────────┐
│  [v1-seed-anchor-demo]  sensitivity: low       │
│   ▾ 展开看 dataset-card.md                    │
│   📋 redaction: 0/100 records redacted         │
│  [v1-gemma4-e2b-medium]  sensitivity: low      │
│   ...                                          │
└────────────────────────────────────────────────┘
```

具体：

- `build-lab-data.mjs` 在每个 dataset 目录扫 `dataset-card.md`，把 frontmatter 解析成 JSON、body 保留为 markdown 字符串。
- LabData 类型加 `dataset_cards: DatasetCard[]`。
- Data Pipeline tab 加 `<DatasetCardsPanel>`：每个 card 折叠展开，里面用 `react-markdown` 渲染（已经引入）。
- Audience 标签：`工程`。

不加新 tab，避免 nav 膨胀。

## 实施拆步

| # | 步骤 | 验证 |
|---|---|---|
| 1 | 写 `training/data_pipeline/governance.py`：RedactionPolicy / RedactionRule / redact_record / redact_jsonl / default_policy | 单元测试覆盖 4 条规则各 3 个正反例 |
| 2 | 写 `training/data_pipeline/tests/test_governance.py` | `pytest` 通过；spot-check"幺三八"不被误命中、`13800138000` 必中 |
| 3 | 写 dataset-card 和 redaction-report 渲染函数 + 模板 | 跑一份样例 dataset 出 `.md`，肉眼检查 frontmatter + body 都对 |
| 4 | 加 Makefile target `dataset-governance`：扫所有 `data/sft/v1-*` 和 `data/real-finetune/v1-*`，逐个跑 | 每个目录新增两个 `.md` 文件 |
| 5 | `pipeline.py` / `import_car_bench.py` / `import_clarifyvc.py` 在 finalize 时调 governance | 重跑导入产生新 dataset 时自动出 governance 产物 |
| 6 | `build-lab-data.mjs` 加 `loadDatasetCards()`：扫 `data/**/dataset-card.md`，解析 frontmatter（用 `gray-matter` 或自写 minimal parser） | `lab-data.json` 多一段 `dataset_cards` 数组 |
| 7 | `LabData.dataset_cards: DatasetCard[]` 类型 | tsc 通过 |
| 8 | `<DatasetCardsPanel>` 组件 + CSS（复用 markdown-body） | preview Data Pipeline tab 看到所有 dataset 的卡 |
| 9 | 给 `make dataset-governance` 写一份 [docs/changes/...-impl-notes.md](docs/changes/) | 记录策略版本、跑了哪些 dataset、有无非零命中 |

## 成功标准

1. **每个 dataset 目录**（`data/sft/v1-*`、`data/real-finetune/v1-*`）都有 `dataset-card.md` + `redaction-report.md`。
2. **任何新增 dataset**（生成 / 导入 / 真实日志）走流水线时**强制**产出这两个产物，不能跳。
3. **Data Pipeline tab** 上能直接看每个 dataset 的 card + redaction 摘要。
4. **未来接真实日志时**：只需要扩展 `default_policy()` 多加几条规则，schema / 模板 / UI 都不动。

## 风险

- **正则误判**：phone_cn 正则可能误命中"我有 13 个苹果，800 块买的"这类数字密集文本。**缓解**：spot-check 段强制贴样本，人工核对。
- **policy 版本漂移**：`policy_version` 在 frontmatter 里写死，但实际 `default_policy()` 改了之后重跑会造成同 dataset 历史 redaction-report 失效。**缓解**：bump policy_version + 在 dataset-card 里同时记 `policy_version_at_generation`，不删历史报告。
- **performance**：合成数据 ~100~1000 条不慢；公开数据集 car-bench 可能上万条，redact_jsonl 必须流式处理（一边读一边写），不能全部加载到内存。
- **政策误读"自动 7 天清理"**：本 spec 明确不做。retention policy 是部署/CI 责任，governance 模块只**记录**，不**执行**。在 dataset-card 里写明 "原始日志保留窗口 = 7 天（部署侧 cron 控制，本仓库不直接管理）"。
- **dataset-card 内容质量**：模板能产生 frontmatter，但"描述 / 已知限制"段需要人写。**缓解**：模板给 placeholder 文字 + TODO 注释，让仓库 maintainer 在创建 dataset 时填。

## Future enhancement（不在本次范围）

- 跨 dataset 去重检测（同一条 user prompt 在多个 dataset 出现）
- redaction 命中样本的可视化对比（before / after diff）
- dataset-card 字段进入 web 顶部"全局数据健康度"指标
- 真正"日志抽取规范"文档化（车机端责任，需要协调）
- 加 `npii_quarantine/` 目录隔离命中 PII 的原始 record（不是简单替换）
- 引入 `gray-matter`（Node markdown frontmatter 解析）依赖；当前 spec 假设可能需要它，实现时确认

## 参考

- review 来源：[2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md §6](../reviews/2026-04-25-finetune-lab-vs-gemma4-e2b-car-tool-finetuning-design-review.md)
- 现有数据流水线：[training/data_pipeline/pipeline.py](../../training/data_pipeline/pipeline.py)
- 现有公开数据集导入：[training/data_pipeline/import_car_bench.py](../../training/data_pipeline/import_car_bench.py)、[training/data_pipeline/import_clarifyvc.py](../../training/data_pipeline/import_clarifyvc.py)
- HuggingFace dataset card 约定（参考但不照搬）：https://huggingface.co/docs/hub/datasets-cards
- 现有数据产物：`dataset_summary.json/.md`、`validation_report.md`
