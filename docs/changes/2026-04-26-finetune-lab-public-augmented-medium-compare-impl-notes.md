---
status: implemented
summary: 将 39 条公开样本并入 medium 主线训练集，跑通 public-augmented medium 真实 Gemma 4 LoRA，并接入 compare pack 与前端展示。
---

# Public-Augmented Medium Compare

## 本次实现

- 新增 `data-medium-public-augmented`
- 新增 `real-finetune-data-medium-public-augmented`
- 新增 `real-medium-public-augmented-direct-compare`
- 扩展 `data-scale-compare-pack`，把 `Medium · Public-augmented · Direct mixed` 作为标准场景纳入 compare 数据包
- 更新 `training/finetune/README.md`、`docs/ai/workflows.md`、`docs/ai/gemma4-real-finetune-guide.md`

## 数据构成

- base medium：`400 train / 52 valid / 48 test`
- public augmentation：`39` 条
  - `CAR-Bench`: `30`
  - `ClarifyVC`: `9`
- public-augmented medium：
  - `439 train / 52 valid / 48 test`

公开样本本轮只并入 `train split`，`valid/test` 保持不变，目的是和现有 medium direct / medium curriculum 做更公平的同口径对比。

## 真实训练结果

public-augmented medium direct mixed：

- `43/48 exact_name_match`
- `46/48 structured_output_valid`
- `37/48 arguments_match`
- `46/48 behavior_accuracy`
- `confirm 2/2`
- `reject 2/2`
- `unsafe_direct_call_rate = 0/48`

对照：

- medium direct mixed：
  - `43/48 exact`
  - `47/48 structured`
  - `37/48 args`
  - `47/48 behavior`
- medium curriculum + consolidation：
  - `47/48 exact`
  - `47/48 structured`
  - `45/48 args`
  - `48/48 behavior`

## 结论

本轮结论不是“公开数据没价值”，而是：

- 当前这 `39` 条公开样本已经足够形成一个可运行的增强训练集
- 但它们直接并入 `medium direct mixed` 后，没有立刻把 mixed-task held-out 拉高
- 指标表现更接近“维持原有水平并略微扰动结构/行为边界”，而不是“立刻形成收益”

这说明当前公开样本的作用更像：

- 扩 domain coverage
- 扩 phrasing coverage
- 补 clarify / navigation / lighting 风格

而不是直接替代当前主线任务的高密度监督信号。

## 下一步建议

- 优先做 `public-augmented curriculum`，而不是继续只测 direct mixed
- 单独看 `navigation / lighting / media` 对 held-out 的影响，必要时补新的评测切片
- 如果目标是“公开数据真正形成收益”，下一步更应该扩可映射样本总量，而不是只依赖当前 `39` 条
