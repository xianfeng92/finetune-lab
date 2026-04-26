# Real Single-Tool Control Experiment

## Summary

这次把真实 MLX LoRA 路径从固定的 `12-step` demo，推进成了一个更像样的对照实验工作流：

- real dataset 支持按 category 过滤
- real train 支持按 epoch 自动换算 iter
- 新增 `make real-single-tool-compare` 标准入口

目标是先回答一个更基础的问题：`Gemma 4 E2B-it` 在最简单的 `single_domain_single_tool` 切片上，经过约 3 个 epoch 的真实 LoRA 更新后，能不能先学会稳定 tool-call。

## What Changed

- `training/finetune/build_real_finetune_dataset.py`
  新增 `--category-filter`
- `training/finetune/mlx_real_lora_train.py`
  新增 `--epochs`，会按 train split 行数和 batch size 自动换算 iter 数
- `Makefile`
  新增 `make real-single-tool-compare`
- `README.md`
- `training/finetune/README.md`
- `docs/ai/workflows.md`
- `project-context.json`

## New Standard Entry

```bash
make real-single-tool-compare
```

它会串起：

1. 生成 `single_domain_single_tool` 子集数据
2. 对这个子集跑约 3 个 epoch 的真实 MLX LoRA
3. 对控制实验 run 做 best-effort probe

## Teaching Impact

- 真实训练不再只有“12-step 教学 smoke 配置”
- agent 可以先把任务复杂度降到最简单单工具切片，再判断模型有没有学会最小 structured tool calling
- 如果 single-tool 先学会而 full mixed-task 仍学不会，就能更有把握地把问题归因到任务混合复杂度，而不是 parser 或底层兼容

## Verification

- `make real-single-tool-compare`
- `make real-probe-mac`

## Results

- control dataset:
  - train: `32`
  - valid: `4`
  - test: `4`
- control train run:
  - `effective_epochs = 3.0`
  - `iters = 96`
  - test loss: `0.000`
- control probe:
  - `exact_name_match = 4/4`
  - `structured_output_valid = 4/4`
  - `arguments_match = 4/4`

这说明修完 real dataset 的 tool-call 参数格式之后，`mlx-community/gemma-4-e2b-it-4bit` 在最简单的单工具切片上已经能稳定学会正确的 Gemma 4 tool-call 语法。  
因此之前 full mixed-task run 的 `0/8`，更应该归因到：

- `12-step` 训练量远远不够
- mixed-task 任务分布比单工具切片复杂得多
- 下一阶段应该优先做 curriculum / staged training，而不是继续怀疑 parser 本身

## Follow-up Questions

- 如果 single-tool 仍然学不会，下一步要继续检查 prompt template、训练目标 masking、LoRA 层数和学习率
- 如果 single-tool 学会而 mixed-task 学不会，就说明下一阶段该做 curriculum，而不是继续硬堆 parser 逻辑
