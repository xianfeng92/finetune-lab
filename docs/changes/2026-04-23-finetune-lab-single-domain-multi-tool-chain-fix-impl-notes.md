# Single-Domain Multi-Tool Chain Fix

## Summary

这次直接修了 `single_domain_multi_tool_chain` 的数据定义，并重新跑了一整条真实 `curriculum + consolidation` workflow。

修复前，这个 category 实际上是“同一个 tool call 重复两次”，会把 mixed-task 学习往错误方向推。修复后，它变成真正的同域双调用 HVAC 链：

- `hvac_set_temperature`
- `hvac_set_fan_speed`

## What Changed

- [training/data_pipeline/pipeline.py](/Users/xforg/AI_SPACE/finetune-lab/training/data_pipeline/pipeline.py)
  - 新增真实的 `SINGLE_DOMAIN_MULTI_TOOL_CHAIN_VARIANTS`
  - `single_domain_multi_tool_chain` 改为同域双调用 HVAC 样本，不再重复同一个 tool
- [Makefile](/Users/xforg/AI_SPACE/finetune-lab/Makefile)
  - 保持 `real-tail-polish` 的 reroute focus prompt 与新的 `window` 文案一致

## Verification

- `make data-demo`
- `make test-data`
- `make real-finetune-data`
- `make real-stage-curriculum-consolidation`
- `make web-build`

## Results

这轮先确认了一个关键问题：上一次“修了数据但结果没变”的原因，不是训练脚本忽略了新样本，而是主 real-finetune 数据目录里的 `test.jsonl` 当时没有真正刷新，probe 还在吃旧 seat duplicate case。

这次强制刷新主数据目录后：

- `data/sft/v1-seed-anchor-demo/held-out.jsonl`
  - `sft-v1-0055 = 后排空调设到22度，风量开2档`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl`
  - `sft-v1-0055` 已同步变成 HVAC 双调用 test case

新的真实 consolidation probe 结果：

- `exact_name_match = 7/8`
- `parsed_json = 8/8`
- `structured_output_valid = 8/8`
- `arguments_match = 5/8`

比起“旧测试集上的 7/8”，这次的关键区别是：

1. `single_domain_multi_tool_chain` 现在名字层面已经打通
2. `reroute_to_meta` 也稳定输出 `_meta_reroute`
3. 剩余问题已经收缩成参数对齐，而不是不会出结构化 tool call

当前还剩的 3 个尾巴：

- `sft-v1-0070`
  - `cross_domain_multi_tool`
  - 仍会把 `seat + door` 压成单个 `seat_set_temperature_percent`
- `sft-v1-0080`
  - `reroute_to_meta`
  - 名字对了，但 `suggested_domains` 还会偏到 `door`
- `sft-v1-0055`
  - `single_domain_multi_tool_chain`
  - 两个工具名都对，但参数仍偏到 `driver / 24` 这类训练均值

## Takeaway

这轮修复把问题范围明显缩小了：

1. `single_domain_multi_tool_chain` 的结构性定义错误已经修掉
2. 真实 workflow 现在确实能在新的 mixed-task test set 上稳定产出链式双调用
3. 当前最主要的剩余问题已经不是“不会链式调用”，而是 mixed-task 条件下的参数对齐和 cross-domain 解耦
