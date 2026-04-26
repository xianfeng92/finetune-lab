# Reroute Signal Refresh

## Summary

这次把 `reroute_to_meta` 里的 `window / hvac / door` 提示词改得更明确：

- `window`: `车里太闷了，想透透气`
- `hvac`: `车里太冷了，想把空调调暖一点`
- `door`: `我想把门都锁上`

目标是减少原先 `有点闷` / `这会儿有点冷` 这类过短提示带来的 domain 歧义，然后把整条真实 workflow 重新跑一遍，看 mixed-task probe 是否会更稳。

## What Changed

- `training/data_pipeline/pipeline.py`
- `Makefile`
  - 同步把 `real-tail-polish` 里的 focus prompt 更新到新 window 文案

## Verification

- `make data-demo`
- `make test-data`
- `make real-stage-curriculum-consolidation`

## Results

数据层面，新文案已经正确进入 train / held-out split：

- reroute train:
  - `车里太闷了，想透透气 -> window`
  - `车里太冷了，想把空调调暖一点 -> hvac`
  - `我想把门都锁上 -> door`
- reroute held-out:
  - `sft-v1-0080 = 车里太闷了，想透透气 -> window`

但整条真实 workflow 重跑后的最终 mixed-task probe 结果没有变好，反而从此前的 `7/8` 退回到：

- `exact_name_match = 4/8`
- `structured_output_valid = 7/8`
- `arguments_match = 4/8`

关键 miss：

- `sft-v1-0080` 现在直接 parse fail，没有稳定产出 `_meta_reroute`
- `sft-v1-0055` 仍然只输出一个 `seat_set_heating`
- `sft-v1-0100` 还出现了错误的 `window_set_temperature`

## Takeaway

这轮实验说明：

1. 只把 reroute 文案写得更清楚，还不足以稳定拉开 `window / hvac` 的 mixed-task 边界
2. 当前最主要的结构性问题仍然不是单条 prompt，而是数据任务定义本身还在互相打架
3. 最可疑的一点是 `single_domain_multi_tool_chain` 目前并不是真正的链式调用，而是同一个 tool call 重复两次；这会持续干扰 mixed-task 学习
