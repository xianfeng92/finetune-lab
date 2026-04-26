---
title: finetune-lab vs Gemma 4 E2B Car Tool Finetuning Design Review
status: implemented
owner: claude
created: 2026-04-25
updated: 2026-04-26 (in-scope findings closed)
implements: []
reviews: []
---

# 2026-04-25 finetune-lab vs Gemma 4 E2B Car Tool Finetuning Design Review

## 结论

本轮审查把外部设计文档 [2026-04-25-gemma4-e2b-car-tool-finetuning-design.md](/Users/xforg/Downloads/2026-04-25-gemma4-e2b-car-tool-finetuning-design.md) 和当前 `finetune-lab` 做了一次逐项对照。

结论：部分通过。

`finetune-lab` 已经足够覆盖这份设计里最关键的“训练实验层”和“方法验证层”，尤其是：

1. Gemma 4 E2B LoRA 微调路径
2. held-out probe
3. curriculum / consolidation / focused repair 这类训练策略探索
4. AI-native onboarding 和教学前端

但它还没有覆盖这份设计真正面向车机落地的“产品集成层”，尤其缺：

1. 显式行为标签：`clarify / confirm / reject / handoff`
2. 带 `risk / vehicle_state / expected_system_action` 的训练样本 contract
3. 真实链路日志抽取、脱敏、dataset-card 和 redaction-report
4. Android LiteRT / ZeroClaw / parser / manifest / fallback 的完整回灌链路
5. 待确认动作与安全执行边界

一句话说，当前仓库已经是这份设计很好的上游实验台，但还不是这份设计本身对应的车机微调落地仓库。

## 核对范围

- 项目目标和范围是否对齐
- 数据类别和训练样本格式是否能承接车机场景
- LoRA / adapter 微调路径是否已经具备
- 评测指标是否覆盖行为级验证
- 是否具备安全边界、确认流程和真实链路回灌
- 仓库的 AI-native 能力是否能作为这份设计的实施底座

## Findings

### 1. 训练实验层已经基本具备

当前 `finetune-lab` 已经不是只有 simulated smoke train。它同时具备：

- held-out split 数据链路
- Gemma 4 E2B 真实 MLX LoRA workflow
- single-tool control、stage curriculum、consolidation、focused repair
- small / medium 数据量级实验

这意味着这份设计里“先做 LoRA / adapter 微调，再做前后对比评测”的核心训练方法，在当前仓库里已经有较完整的实验基础。

参考：

- `Makefile`
- `training/finetune/README.md`
- `docs/ai/workflows.md`
- `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md`

### 2. 当前数据类别更像任务形态，不是完整行为标签

设计文档要求显式区分：

- `answer_only`
- `tool_call`
- `clarify`
- `confirm`
- `reject`
- `handoff`

而当前 `finetune-lab` 的数据主要按以下类别组织：

- `single_domain_single_tool`
- `single_domain_multi_tool_chain`
- `cross_domain_multi_tool`
- `reroute_to_meta`
- `full_tool_fallback`
- `proactive_event_driven`

这些类别足以支撑“工具调用教学”和“行为变化分析”，但还不足以直接承接车机场景里的动作选择 contract。

影响：

- 现在的模型更像在学“任务结构”和“工具路由”
- 还没有明确学会“该追问、该确认、该拒绝、该 handoff”

参考：

- `training/data_pipeline/pipeline.py`

### 3. 训练样本格式还没有风险与系统动作层

设计文档里的训练样本除了输入输出，还要求显式包含：

- `behavior`
- `risk`
- `vehicle_state`
- `expected_system_action`
- `routing`

当前 `finetune-lab` 的真实训练数据虽然已经能稳定导出成 `openai-chat-with-tools`，但核心仍然是：

- `messages`
- `tools`
- `expected_tool_calls`
- `loaded_tool_names`

这很适合做 LoRA 和 parser 级实验，却还不足以承载“待确认动作创建”“高风险动作拒绝”“多轮确认后执行”这些车机执行 contract。

影响：

- 当前仓库已经能验证“模型会不会调对工具”
- 但还不能验证“模型是否正确触发系统动作和安全流程”

参考：

- `training/finetune/build_real_finetune_dataset.py`
- `outputs/real/real-finetune-dataset-pack-medium.json`

### 4. 评测已经有行为级基础，但还没达到车机验收指标

当前仓库已经不是只看 loss，而是在看：

- `exact_name_match`
- `parsed_json`
- `structured_output_valid`
- `arguments_match`

这和设计文档强调“不要只看训练曲线，要看工具调用行为”是高度一致的。

但设计文档要求的更完整指标还没有落齐，例如：

- `behavior_accuracy`
- `argument_semantic_match`
- `false_tool_call_rate`
- `unsafe_direct_call_rate`
- `pending_confirmation_created_rate`
- `turn_success_rate`
- `latency_p50/p95`

影响：

- 当前 probe 很适合训练实验对比
- 但还不足以作为车机上线前的验收基线

参考：

- `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md`
- `outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md`

### 5. 安全边界现在更多是教学语义，不是真实执行 contract

设计文档的安全边界非常明确：

1. 模型只提出动作
2. ZeroClaw 做 allowlist 校验
3. schema 校验和工具执行逻辑继续留在系统层
4. 高风险动作必须创建 `pending_confirmation`
5. 用户确认后才能放行

当前 `finetune-lab` 已经有 `_meta_reroute`、fallback 和 event-driven 这些相近教学结构，但没有真正实现：

- `pending_confirmation`
- 确认对象过期
- 下一轮确认匹配
- 状态变化失效
- 审计日志

这是当前和设计文档之间最大的结构性差距之一。

参考：

- `training/data_pipeline/pipeline.py`
- `project-context.json`

### 6. 数据治理层基本缺失

设计文档要求：

- 原始日志只保存在受控目录
- 最长保留 7 天
- 进入训练集前必须脱敏
- 必须生成 `dataset-card.md`
- 必须生成 `redaction-report.md`

当前 `finetune-lab` 已经有：

- `dataset_summary.json/.md`
- `validation_report.md`

但还没有：

- 原始日志抽取规范
- 脱敏策略和抽查报告
- dataset card / redaction report

这意味着它目前更适合“实验生成数据集”，而不是“从真实车机链路沉淀训练集”。

参考：

- `training/data_pipeline/README.md`
- `data/sft/v1-gemma4-e2b-medium/dataset_summary.json`

### 7. Android LiteRT 回灌与台驾验收完全不在当前仓库范围内

设计文档要求的产物回灌链路包括：

- LoRA / adapter
- 合并 / 导出推理权重
- 量化
- 转 `.litertlm`
- manifest
- Android `LlmService` 加载
- fallback 文件
- SA8295P 台驾验收

当前 `finetune-lab` 真实路径跑到的是：

- MLX LoRA adapter
- run manifest
- probe report

这已经足够做训练方法验证，但还没有任何 Android LiteRT 或台驾部署相关的交付物。

影响：

- 当前仓库不能直接回答“这版模型能不能回灌到车机”
- 但可以很好地回答“这版数据和训练策略值不值得继续往车机链路推进”

参考：

- `training/finetune/README.md`
- `docs/ai/workflows.md`

### 8. AI-native 能力是当前仓库的明显优势

这份外部设计文档本身很强，但更多是训练和产品方案设计；而 `finetune-lab` 已经额外具备：

- `make ai-onboarding`
- `make ai-setup`
- `make ai-lab`
- stage readiness
- learning progress
- 前端实验台和 IAB 静态页

这意味着如果你要真正推进这份车机微调设计，`finetune-lab` 很适合作为上游方法验证平台和 agent-first 训练实验台。

它在 AI-native 这一点上，实际上比文档当前写出来的实施层更成熟。

参考：

- `README.md`
- `scripts/ai_onboarding_report.py`
- `docs/ai/workflows.md`
- `web/dist/index.html`

## 综合判断

如果把设计文档拆成两层：

1. 训练实验层
2. 车机产品集成层

那么当前 `finetune-lab` 的覆盖情况大致可以概括为：

- 训练实验层：覆盖度高，约 `70%-80%`
- 行为 contract / 数据治理层：覆盖度中低，约 `30%-40%`
- Android LiteRT / ZeroClaw / 台驾回灌层：覆盖度低，约 `10%-20%`

因此，最准确的定位是：

`finetune-lab` 已经足够承接这份设计的上游训练与评测实验，但还不能替代真正的车机落地集成仓库。

## 建议优先级

如果下一阶段目标是让 `finetune-lab` 更接近这份设计文档，最值得优先补的不是 Android 端代码，而是先补下面四件事：

1. 把数据类别升级成显式行为标签：`tool_call / clarify / confirm / reject / handoff / answer_only`
2. 给训练样本补 `risk`、`vehicle_state`、`expected_system_action`
3. 增加面向车机决策的评测 schema，补上 `behavior_accuracy`、`unsafe_direct_call_rate` 等指标
4. 把日志抽取、脱敏和 dataset card / redaction report 建成标准产物

等这四件事稳定后，再去接 Android LiteRT、parser、manifest、fallback 和台驾验收，会更顺。

## 结论补充

当前最合理的推进方式不是把 `finetune-lab` 直接改造成 ZeroClaw 车机仓库，而是：

1. 继续把它当作 Gemma 4 E2B 车控工具调用的上游实验台
2. 在这里先把数据 schema、行为标签、训练策略和评测闭环打磨稳定
3. 再把验证通过的模型和 contract 回灌到真正的 Android / ZeroClaw 集成链路

---

## 2026-04-26 进展更新

8 个 finding 现状：

| # | 主题 | 状态 |
|---|---|---|
| 1 | 训练实验层覆盖 | ✅ 28 runs 落盘；curriculum / consolidation / replay 都跑过 |
| 2 | 显式行为标签 | ✅ DONE [04-25 explicit-behavior-labels](../changes/2026-04-25-finetune-lab-explicit-behavior-labels-impl-notes.md) |
| 3 | risk / vehicle_state / expected_system_action | ✅ DONE [04-25 expected-system-action](../changes/2026-04-25-finetune-lab-expected-system-action-confirm-reject-impl-notes.md) |
| 4 | behavior_accuracy / unsafe_direct_call_rate / contract hit | ✅ DONE [04-25 behavior-eval-pack](../changes/2026-04-25-finetune-lab-behavior-eval-pack-impl-notes.md)，UI 上有 BehaviorEvalPanel |
| 5 | 安全边界 contract（pending_confirmation 过期 / 确认匹配 / 审计日志） | 🟡 数据层有 `expected_system_action.expires_in_seconds`，运行时 contract 在 ZeroClaw 集成层（out-of-scope） |
| 6 | **数据治理产物（dataset-card / redaction-report）** | ✅ **DONE 2026-04-26** [data-governance-artifacts](../changes/2026-04-26-data-governance-artifacts-impl-notes.md)。每个 dataset 都有这两个产物，UI 上有 DatasetCardsPanel 暴露，新生成 / 新导入数据走流水线时强制产出 |
| 7 | Android LiteRT 回灌 / 台驾验收 | 🚫 明确 out-of-scope（不同仓库） |
| 8 | AI-native 能力 | ✅ 评为优势 |

到此本 review 在 finetune-lab 范围内的 6 / 6 in-scope finding 全部闭环。
