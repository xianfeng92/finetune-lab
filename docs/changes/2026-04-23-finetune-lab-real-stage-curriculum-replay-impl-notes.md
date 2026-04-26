# Real Stage Curriculum Replay

## Summary

这次在 staged curriculum 的基础上，继续补了一版 `curriculum + replay`：

- stage 1: `single_tool`
- stage 2: `reroute/meta + 25% stage1 replay`
- stage 3: `multi_tool + 25% replay`（均分来自 stage1 / stage2）

目标是缓解纯 staged curriculum 的 stage bias，尽量保留 earlier-stage 能力，同时继续推进 multi-tool 行为学习。

## What Changed

- 新增 `training/finetune/build_replay_dataset.py`
- `Makefile`
  新增 `make real-stage-curriculum-replay`
- `README.md`
- `training/finetune/README.md`
- `docs/ai/workflows.md`
- `project-context.json`

## Replay Policy

- replay ratio: `0.25`
- replay 只混入 `train.jsonl`
- `valid/test` 保持当前 stage 的 primary split，不做 replay

这样做是为了：

1. 保留 stage-local eval
2. 在训练时避免把 earlier-stage 能力完全遗忘

## Verification

- `make real-stage-curriculum-replay`

## Results

最终 replay 版本已经实际跑完，结果如下：

- direct mixed `3 epoch`：`4/8 exact_name_match`，`7/8 structured_output_valid`，`4/8 arguments_match`
- pure staged curriculum：`3/8 exact_name_match`，`6/8 structured_output_valid`，`3/8 arguments_match`
- curriculum + replay：`2/8 exact_name_match`，`6/8 structured_output_valid`，`2/8 arguments_match`

这次 replay 没有超过 direct mixed `3 epoch` 的 `4/8`，也没有把 pure curriculum 里暴露出来的重复调用问题彻底修掉。

### What Replay Preserved

- `cross_domain_multi_tool` 仍然保持命中
- `single_domain_multi_tool_chain` 仍然保持命中

### What Replay Did Not Recover

- `proactive_event_driven` 重新退回 miss
- `single_domain_single_tool` 仍然会重复输出同一个 tool call
- `full_tool_fallback` 依旧没有稳定恢复

## Takeaway

这轮实验说明：

1. 简单把 earlier-stage 样本按固定比例 replay 回来，还不足以压住 stage bias
2. 当前 mixed-task 最稳的真实路径，仍然是直接 full mixed-task `3 epoch`
3. 如果继续往前推，更值得尝试的是：
   - `curriculum + consolidation`
   - `curriculum + replay + lower replay ratio`
   - 或在最后补一个短的 full-mixed refresh stage
