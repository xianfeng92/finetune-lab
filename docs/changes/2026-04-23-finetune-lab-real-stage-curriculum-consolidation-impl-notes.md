# Real Stage Curriculum Consolidation

## Summary

这次在 pure staged curriculum 之后，补了一版 `curriculum + consolidation`：

1. `single_tool`
2. `reroute/meta`
3. `multi_tool`
4. `full mixed consolidation`

目标不是继续把 stage 切得更细，而是在已经学到复杂结构的前提下，再用一个短的 full-mixed refresh stage 把 earlier-stage 边界重新拉齐。

## What Changed

- `Makefile`
  新增 `make real-stage-curriculum-consolidation`
- `README.md`
- `training/finetune/README.md`
- `docs/ai/workflows.md`
- `project-context.json`

## Consolidation Policy

- 先完整跑一轮 pure staged curriculum
- consolidation stage 直接回到 full mixed dataset
- consolidation 默认跑 `1 epoch`
- consolidation 从 `stage3-multi-tool` adapters 继续训练

## Verification

- `make real-stage-curriculum-consolidation`

## Results

full mixed-task test set 上的最终 probe：

- direct mixed `3 epoch`：`4/8 exact_name_match`，`7/8 structured_output_valid`，`4/8 arguments_match`
- pure staged curriculum：`3/8 exact_name_match`，`6/8 structured_output_valid`，`3/8 arguments_match`
- curriculum + replay：`2/8 exact_name_match`，`6/8 structured_output_valid`，`2/8 arguments_match`
- curriculum + consolidation：`7/8 exact_name_match`，`8/8 structured_output_valid`，`6/8 arguments_match`

这次 consolidation 明确超过了 direct mixed `3 epoch` 的 `4/8`，也把 pure curriculum / replay 里最明显的遗忘问题收回来了。

### What Improved

- `single_domain_single_tool` 的重复调用问题被完全修掉
- `full_tool_fallback` 恢复命中
- `proactive_event_driven` 保持命中
- `cross_domain_multi_tool` 保持命中
- `reroute_to_meta` 恢复到正确工具名

### Remaining Miss

- `single_domain_multi_tool_chain` 仍然只输出了一个 `seat_set_heating`，没有恢复到完整链式行为
- `reroute_to_meta` 虽然工具名正确，但参数还没完全对齐，所以 `arguments_match` 仍停在 `6/8`

## Takeaway

这轮实验说明：

1. staged curriculum 本身并不是坏方向，问题主要是缺一个 full-mixed consolidation 收口阶段
2. 与固定比例 replay 相比，short full-mixed refresh 更适合把 single-tool / reroute / fallback 这些边界重新拉齐
3. 当前 mixed-task 最好的真实路径，已经从 direct mixed `3 epoch` 升级成 `curriculum + consolidation`
