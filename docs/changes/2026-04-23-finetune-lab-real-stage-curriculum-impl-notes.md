# Real Stage Curriculum

## Summary

这次把真实 MLX LoRA workflow 从“单轮 mixed-task”推进成了真正的 staged curriculum：

1. `single_tool`
2. `reroute/meta`
3. `multi_tool`

每个 stage 都会先生成自己的 real fine-tune dataset，再在上一阶段的 adapter 基础上继续训练，最后回到 full mixed-task test set 上统一做 probe。

## What Changed

- `training/finetune/mlx_real_lora_train.py`
  新增 `--resume-adapter-file`
- `Makefile`
  新增 `make real-stage-curriculum`
- `README.md`
- `training/finetune/README.md`
- `docs/ai/workflows.md`
- `project-context.json`

## Stages

- stage 1:
  - category filter: `single_domain_single_tool`
- stage 2:
  - category filter: `reroute_to_meta,full_tool_fallback`
- stage 3:
  - category filter: `single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven`

默认每个 stage 都跑 `3 epoch`。

## Why

single-tool control 已经证明这颗模型能学会最小 tool calling。  
剩下的问题不是“模型完全不会”，而是 mixed-task 一次性混训难度过高。

staged curriculum 的目的，就是把 mixed-task 的难度拆开，验证是否能比直接 `3 epoch mixed run` 的 `4/8` probe 更进一步。

## Verification

- `make real-stage-curriculum`

## Results

full mixed-task test set 上的最终 probe：

- direct mixed `3 epoch`:
  - `exact_name_match = 4/8`
  - `structured_output_valid = 7/8`
  - `arguments_match = 4/8`
- staged curriculum:
  - `exact_name_match = 3/8`
  - `structured_output_valid = 6/8`
  - `arguments_match = 3/8`

但细分 case 很有启发：

- curriculum 学会了：
  - `cross_domain_multi_tool`
  - `proactive_event_driven`
  - `single_domain_multi_tool_chain`
- curriculum 退化了：
  - `full_tool_fallback`
  - `reroute_to_meta`
  - `single_domain_single_tool` 出现重复调用（同一个 tool call 输出两次）

## Interpretation

这说明 staged curriculum 不是无效，而是发生了明显的 stage bias：

- 后续 `multi_tool` stage 确实强化了复杂结构化调用
- 但没有保留好 earlier-stage 的 reroute/meta 与 single-tool 边界
- 当前更合理的下一步不该是继续硬分 stage，而应该加 replay / mixed refresh，例如：
  - 每个后续 stage 混入一部分 earlier-stage 样本
  - 或在最后加一个 short full-mixed consolidation stage
