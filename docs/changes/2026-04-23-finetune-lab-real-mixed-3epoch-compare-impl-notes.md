# Real Mixed 3-Epoch Compare

## Summary

这次在完整 mixed-task 数据集上，补跑了一轮比 `12-step` 更像样的真实 MLX LoRA：

- dataset: `data/real-finetune/v1-gemma4-e2b-toolcall-demo`
- train rows: `80`
- effective epochs: `3.0`
- max steps: `240`

目标是验证：在修完 tool-call 数据格式之后，真实 mixed-task 训练能否把行为层 probe 从 `0/8` 拉起来。

## Run

- run id: `gemma4-e2b-real-mlx-lora-mixed-3epoch`
- base model: `mlx-community/gemma-4-e2b-it-4bit`
- training mode: `real-mlx-lora`
- output dir:
  - `outputs/gemma4-e2b-real-mlx-lora-mixed-3epoch/`

## Results

训练侧：

- avg train loss: `0.9275`
- test loss: `0.028`
- effective epochs: `3.0`

probe 对比：

- old `12-step` mixed run:
  - `exact_name_match = 0/8`
  - `structured_output_valid = 0/8`
  - `arguments_match = 0/8`
- new `3-epoch` mixed run:
  - `exact_name_match = 4/8`
  - `structured_output_valid = 7/8`
  - `arguments_match = 4/8`

## What Improved

- `single_domain_single_tool` case 已经稳定命中
- `_meta_reroute` 的 full-tool fallback case 也开始命中
- 大多数样本已经能输出可解析的 Gemma 4 tool-call 结构，而不再是完全不可解析的噪声

## What Still Fails

当前主要短板集中在更复杂的 mixed-task 行为：

- `cross_domain_multi_tool`
- `proactive_event_driven`
- `single_domain_multi_tool_chain`
- 部分 `reroute_to_meta` 组合 case

也就是说，这条真实路径现在已经证明：

1. parser 不是主障碍
2. tool-call 数据格式 bug 已被修复
3. 真正剩下的问题是 mixed-task curriculum，而不是“模型根本学不会 tool calling”

## Next Step

下一步应该进入 staged curriculum：

1. `single_tool`
2. `reroute/meta`
3. `multi_tool`

再比较 staged curriculum 是否能把 mixed-task probe 从 `4/8` 继续推高。
