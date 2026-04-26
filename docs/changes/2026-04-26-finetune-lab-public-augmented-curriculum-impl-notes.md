---
status: implemented
summary: 为 public-augmented medium 新增 curriculum + consolidation 路线，并验证公开样本在课程化训练下开始形成 mixed-task 正收益。
---

# Public-Augmented Curriculum

## 本次实现

- 新增 `make real-medium-public-augmented-stage-curriculum-consolidation`
- 新增三段 stage 数据目录：
  - `stage1-single-tool`
  - `stage2-reroute-meta`
  - `stage3-multi-tool`
- 新增最终 consolidation run：
  - `outputs/gemma4-e2b-real-mlx-lora-medium-public-augmented-stage-curriculum-consolidation/stage4-consolidation`
- 扩展 `data-scale-compare-pack`，可纳入 `Medium · Public-augmented · Curriculum + consolidation`

## 训练配置

沿用 current medium best 的课程结构：

1. `single_tool`
2. `reroute/meta(+confirm/reject)`
3. `multi_tool`
4. `full mixed consolidation`

数据仍然是同一套 public-augmented medium：

- `439 train / 52 valid / 48 test`
- 其中新增公开样本 `39` 条

## 结果对比

### Public-augmented direct mixed

- `43/48 exact_name_match`
- `46/48 structured_output_valid`
- `37/48 arguments_match`
- `46/48 behavior_accuracy`

### Public-augmented curriculum + consolidation

- `48/48 exact_name_match`
- `48/48 structured_output_valid`
- `45/48 arguments_match`
- `48/48 behavior_accuracy`
- `confirm 2/2`
- `reject 2/2`
- `unsafe_direct_call_rate = 0/48`

### Core medium curriculum + consolidation

- `47/48 exact_name_match`
- `47/48 structured_output_valid`
- `45/48 arguments_match`
- `48/48 behavior_accuracy`

## 结论

这轮最关键的结论不是“公开样本直接变强”，而是：

- 公开样本直接并进 `direct mixed`，不会立刻带来主线 held-out 提升
- 但把同一批样本放进 `curriculum + consolidation` 后，会开始转化成 mixed-task 的真实收益

换句话说：

- **public data alone**：更像 domain / phrasing 补丁
- **public data + curriculum**：开始成为真正可吸收的监督信号

## 仍然存在的边界

- `arguments_match` 目前是 `45/48`，说明公开样本更多帮助的是路由与行为稳定性，而不是进一步把参数细节也全面拉满
- 当前结论仍基于 `48` 条 held-out mixed-task test set，适合做实验判断，不等于生产信心
