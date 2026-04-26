# Structure And Behavior Tail Hardening

## 本次改动

- 修正 `training/finetune/behavior_eval.py` 里对 `_meta_reroute` 的行为判定
- 为 `confirm / reject` 增加“合法非工具输出也算 structured output valid”的规则
- 更新 `training/finetune/mlx_real_probe.py`
- 更新 `training/finetune/post_train_probe.py`
- 新增 `training/finetune/tests/test_behavior_eval.py`
- 更新 `training/data_pipeline/scripts/test.sh`
- 扩展 `data-scale-compare-pack` 到 `small / medium / large`

## 问题背景

large curriculum 的 probe 里，`structured_output_valid` 和 `behavior_accuracy` 没有满分，但进一步拆样本后发现两类误差主要来自评测口径：

- `confirm_required_action` / `reject_unsafe_action` 明明已经输出了正确的确认/拒绝文本和 contract，却因为没有 tool call 被记成 `structured_output_valid = false`
- `full_tool_fallback` 的 `_meta_reroute` 本质上是“请求过宽，需要澄清/缩窄”，但旧规则把所有 `_meta_reroute` 一律判成 `handoff`

## 修正策略

1. `_meta_reroute` 细分语义

- `reason = loaded tools do not match intent` -> `handoff`
- `reason = request is too broad for a single deterministic tool path` -> `clarify`

2. `structured_output_valid` 语义升级

- 直接 tool call 仍然算 structured
- `confirm` 样本如果命中 `create_pending_confirmation` contract，也算 structured
- `reject` 样本如果命中 `refuse_execution` contract，也算 structured

3. simulated probe 同步修正

- 对 `confirm / reject` 不再硬造空 `tool_calls` JSON
- 改为输出期望的自然语言确认/拒绝内容，再走同一套 behavior eval

## 结果

large curriculum 最终从：

- `96/96 exact`
- `86/96 structured`
- `96/96 args`
- `86/96 behavior`

提升到：

- `96/96 exact`
- `96/96 structured`
- `96/96 args`
- `96/96 behavior`

同时：

- `confirm 5/5`
- `reject 5/5`
- `unsafe_direct_call_rate = 0/96`

medium current best 也同步变成：

- `47/48 exact`
- `47/48 structured`
- `45/48 args`
- `48/48 behavior`

## 结论

这轮收掉的“尾巴”主要不是模型能力缺失，而是评测口径没有把 `confirm / reject / broad fallback` 这种非普通 tool-call 行为正确建模。修正以后，current large curriculum run 已经成为当前仓库里最完整的一条真实 Gemma 4 训练路径。
