# 2026-04-22 finetune-lab Learning Coverage and AI-native Review

## 结论

本轮对 `finetune-lab` 做了一次更偏课程设计和 agent 体验的深度审查，重点不是“页面能不能打开”，而是：

1. 一个无基础的人，能不能通过这个项目真正学会微调核心概念
2. 整个项目，是否已经足够 AI-native

初始审查结论：不通过。

原因不是链路跑不通，而是有几处结构性问题会让学习者高估自己已经“学会微调”，同时也会让 agent 只能判断环境是否 ready，而不能判断学习路径是否 ready。

## 核对范围

- train / probe 是否真正分离
- simulated smoke train 是否被明确标注
- 学习路线图承诺的 checkpoint 心智模型是否有可执行入口
- onboarding 是否只看环境 readiness，还是也看学习阶段 readiness
- Level 6 是否被过度包装成“真实 preference / scale-up 结论”

## Findings

### 1. Probe 不是 held-out

原实现里，`probe` 直接从传给训练的同一份 dataset 里截前 5 条样本做“评测”。这会让项目最关键的教学点之一讲偏，因为用户看到的是训练集内回放，不是 held-out 行为变化。

影响：

- 初学者会误以为 probe 指标已经代表泛化能力
- 前端里“held-out case”这层叙事会失真

处理结果：

- 已补 `train.jsonl` 和 `held-out.jsonl`
- `smoke-train-mac` 现在读 `train.jsonl`
- `probe-mac` 现在读 `held-out.jsonl`

参考：

- `training/data_pipeline/pipeline.py`
- `Makefile`
- `training/finetune/post_train_probe.py`

### 2. Simulated 训练链路没有被显式讲清

原实现虽然在 README 里写了 smoke train 是模拟，但 run manifest、onboarding 和前端展示没有把这层限制说得足够显眼，容易让用户把它误读成“最小真实训练”。

影响：

- 学习者会把 synthetic loss 曲线误当成真实收敛信号
- 项目会在“教学实验台”和“真实微调脚手架”之间传达不清

处理结果：

- run manifest 现在显式写入 `training_mode: simulated`
- probe report 现在显式写入 `evaluation_mode: simulated-rule-based`
- React 前端和 IAB 静态页都新增了 simulated 提示

参考：

- `training/finetune/mlx_tune_sft.py`
- `training/finetune/post_train_probe.py`
- `web/src/App.tsx`
- `web/scripts/export-standalone-html.mjs`

### 3. Gemma base vs instruct 路线只有概念，没有产物

路线图里承诺了 `google/gemma-4-E2B` 和 `google/gemma-4-E2B-it` 的对照心智模型，但仓库缺少一个最小可执行入口去承接这层教学。

影响：

- 路线图会看起来比实际课程内容更完整
- 用户知道“有这条主线”，但不知道仓库里到底从哪里开始看

处理结果：

- 已新增 `make gemma-track-pack`
- 已生成 `outputs/gemma/base-vs-instruct-pack.json`
- 前端和 IAB 都能直接展示这个对照教学包

参考：

- `training/finetune/build_gemma_track_pack.py`
- `Makefile`
- `web/src/App.tsx`

### 4. AI-native onboarding 只判断环境，不判断学习进度

原始 onboarding 报告只能告诉 agent “仓库能不能跑”，但不能告诉 agent “现在学到了哪一关、下一关该补什么”。

影响：

- agent 更像 setup helper，而不是 teaching copilot
- 学习路线图和 onboarding 报告之间没有闭环

处理结果：

- onboarding 报告新增 `stage_readiness`
- 新增 `learning_progress`
- next steps 会优先推荐下一关最值得补的标准入口

参考：

- `scripts/ai_onboarding_report.py`
- `outputs/agent/onboarding-report.json`
- `web/src/App.tsx`

### 5. Level 6 需要更明确地区分“教学 compare”与“真实实验结论”

Level 6 现在的 rubric 和 scale-up compare 已经比早期版本真实很多，但本质上仍是教学用 compare layer，而不是已经跑完真实 `E4B-it` 确认性实验。

影响：

- 如果不明示，用户会高估自己已经掌握真实 preference tuning / scale-up 决策

处理结果：

- 当前项目继续保留 `Level 6: partial`
- 文档和前端统一强调它是更真实的 teaching rubric，而不是最终实验定论

参考：

- `project-context.json`
- `docs/ai/workflows.md`
- `web/src/App.tsx`

## 优化落实

基于这份审查，本轮已经完成这些优化：

1. 数据链路新增 `train.jsonl` / `held-out.jsonl`
2. train / probe 标准入口完成分离
3. simulated smoke train / probe 被显式标注到 manifest、report、前端和 IAB
4. onboarding 升级为“环境 readiness + 学习阶段 readiness”
5. Gemma base-vs-instruct 教学包新增为标准入口

## 剩余风险

- 默认训练链路仍然是 teaching-oriented simulated path，不是完整真实微调
- `Level 6` 仍然没有真实 `google/gemma-4-E4B-it` 确认性实验记录
- 如果项目下一阶段目标改成“真正教会用户做真实微调实验”，还需要再补一条真实小规模 fine-tune 入口
