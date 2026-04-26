# Gemma 4 Real Fine-tune Guide

## 这页是给谁看的

这页面向第一次在 `finetune-lab` 里跑真实 Gemma 4 微调的人。

目标不是解释所有理论，而是回答 4 个最实际的问题：

1. 这条真实 workflow 现在到底通没通
2. 应该按什么顺序跑
3. 跑完以后看哪些产物
4. 在当前这台机器上，数据量做到多少比较合适

## 当前结论

当前真实 Gemma 4 workflow 已经通了，但它是“小规模、可复现、教学友好”的真实路径，不是大规模生产训练。

已经验证通过的真实链路：

```bash
make bootstrap-real-finetune
make real-finetune-data
make real-train-mac
make real-probe-mac
```

也已经验证通过更完整的 staged 版本：

```bash
make real-single-tool-compare
make real-stage-curriculum
make real-stage-curriculum-consolidation
```

当前最佳真实 mixed-task probe：

- `exact_name_match = 7/8`
- `structured_output_valid = 8/8`
- `arguments_match = 5/8`

对应产物：

- [run-manifest.json](/Users/xforg/AI_SPACE/finetune-lab/outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/run-manifest.json)
- [inference-probe-report.md](/Users/xforg/AI_SPACE/finetune-lab/outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md)

## 当前真实路径用的是什么

- base model: `mlx-community/gemma-4-e2b-it-4bit`
- training mode: `MLX LoRA`
- dataset format: OpenAI-style `chat + tools`
- hardware target: Apple Silicon

说明：

- 默认教学 `smoke train` 仍然存在，但那条是 simulated
- 这页说的是仓库里的真实 LoRA 路线

## 推荐执行顺序

### 0. 看 readiness

```bash
make ai-onboarding
```

先确认这些东西是不是 ready：

- `.venv-real-train`
- `mlx_lm.lora`
- `data/real-finetune/.../train.jsonl`
- 旧 run manifest / probe report

### 1. 准备真实训练依赖

```bash
make bootstrap-real-finetune
```

### 2. 生成真实训练数据

```bash
make real-finetune-data
```

这一步会把教学用的：

- `data/sft/v1-seed-anchor-demo/train.jsonl`
- `data/sft/v1-seed-anchor-demo/held-out.jsonl`

转换成真实训练用的：

- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl`

如果你要进入下一阶段的中等规模实验，可以直接用：

```bash
make data-medium
make real-finetune-data-medium
```

这会生成一套大约 `400 train / 100 held-out` 的 SFT 数据，并进一步转换成真实 LoRA 需要的 `train/valid/test`。

现在这条 medium 路线已经和小数据一样，保留了：

- `behavior`
- `risk`
- `vehicle_state`
- `expected_system_action`
- `confirm / reject` 行为样本

当前 medium real pack 最新切分是：

- `400 train`
- `52 valid`
- `48 test`

对应产物：

- [real-finetune-dataset-pack-medium.json](/Users/xforg/AI_SPACE/finetune-lab/outputs/real/real-finetune-dataset-pack-medium.json)

如果你想看“公开来源样本直接并进主训练集，会不会立刻提升 mixed-task 表现”，可以跑：

```bash
make data-medium-public-augmented
make real-finetune-data-medium-public-augmented
make real-medium-public-augmented-direct-compare
```

这条路径会把当前可映射的 `CAR-Bench + ClarifyVC` 样本并进 medium train split，形成一套 `439 train / 52 valid / 48 test` 的 public-augmented 版本，用来和原始 medium direct 做同口径比较。

如果你要继续往上看 `1000 total` 这一档，可以直接用：

```bash
make data-large
make real-finetune-data-large
make real-large-direct-compare
```

这条 large 路线会生成：

- 约 `800 train`
- 约 `100 valid`
- 约 `100 test`

它的定位是：

- 保持和 medium 同一份新版 schema
- 用同口径 `1 epoch direct mixed` 回答“数据量继续扩到 1000 total 后，Gemma 4 E2B 的真实能力会怎么变”

如果你想继续验证“更多数据配合 curriculum 会不会比 medium 最优路径更强”，可以继续跑：

```bash
make real-large-stage-curriculum-consolidation
```

这条路径会沿用 current medium best 的训练组织方式：

- `single_tool`
- `reroute/meta(+confirm/reject)`
- `multi_tool`
- `full mixed consolidation`

### 3. 跑一轮最小真实 LoRA

```bash
make real-train-mac
make real-probe-mac
```

适合回答：

- 这台机器能不能真的把 Gemma 4 跑起来
- 模型会不会开始产出结构化 tool call

### 4. 跑控制实验

```bash
make real-single-tool-compare
```

适合回答：

- 如果只训最简单的单工具任务，模型能不能先学会

### 5. 跑更完整的 staged curriculum

```bash
make real-stage-curriculum
make real-stage-curriculum-consolidation
```

适合回答：

- mixed-task 下，模型会在哪些地方掉队
- consolidation 能不能把 earlier-stage 的边界重新收回来

## 跑完以后先看哪里

优先看这 4 类文件：

1. `run-manifest.json`
2. `train-metrics.jsonl`
3. `eval-metrics.jsonl`
4. `inference-probe-report.md`

重点不是只看 loss，而是一起看：

- loss 有没有下降
- probe 的 `exact_name_match` 有没有变好
- `structured_output_valid` 是否稳定
- `arguments_match` 是否开始跟上

## 当前数据规模

当前仓库里已经验证过的真实微调数据规模如下。

### 教学 SFT 数据

- `samples.jsonl`: `100` 条
- `train.jsonl`: `80` 条
- `held-out.jsonl`: `20` 条

### 真实 LoRA 数据

- `train`: `80`
- `valid`: `11`
- `test`: `9`

对应 pack：

- [real-finetune-dataset-pack.json](/Users/xforg/AI_SPACE/finetune-lab/outputs/real/real-finetune-dataset-pack.json)

### 当前 80 条 train 的类别分布

- `single_domain_single_tool`: `32`
- `single_domain_multi_tool_chain`: `12`
- `cross_domain_multi_tool`: `12`
- `reroute_to_meta`: `8`
- `full_tool_fallback`: `8`
- `proactive_event_driven`: `8`

## 当前机器配置

这次验证机配置：

- chip: `Apple M5 Pro`
- memory: `48 GB`
- CPU cores: `15`
- free disk: 约 `760 GiB`

这套配置对 `Gemma 4 E2B 4bit + LoRA` 来说是比较舒服的本地实验机。

## 这台机器适合多大数据量

先说结论：当前这台机器完全可以超过现在的 `80 train`，但不建议一上来就把数据量拉太大。

决定上限的，不只是“多少条样本”，更关键的是：

- 每条样本有多长
- tool schema 有多复杂
- 是单工具还是 mixed-task
- 你要跑多少 epoch
- 你希望多快完成一轮迭代

下面这个建议，默认假设你现在还是：

- `gemma-4-e2b-it-4bit`
- `MLX LoRA`
- 任务风格接近当前 automotive tool-calling
- 样本长度和当前 demo 大体同量级

### 建议分档

#### 档位 A：快速调通

- `100 - 300` train rows
- `20 - 60` eval rows

适合：

- 调 prompt
- 验证数据格式
- 查 parser / schema / tool naming 问题

#### 档位 B：第一轮认真本地实验

- `300 - 1,000` train rows
- `50 - 150` eval rows

适合：

- 让模型稳定学会单工具和简单 mixed-task
- 做第一轮 curriculum / ablation

这是我最推荐你下一阶段先打到的量级。

#### 档位 C：本地中等规模学习实验

- `1,000 - 3,000` train rows
- `100 - 300` eval rows

适合：

- 比较不同 curriculum
- 看参数对齐能不能继续提升
- 做更可信的 held-out 对比

这台机器能做，但你要接受：

- 训练时间会明显变长
- 每一轮试错成本会上升
- 更需要严格的 probe 和 pack 管理

#### 档位 D：本地上限附近

- `3,000 - 8,000` train rows
- `300 - 800` eval rows

只建议在下面条件同时满足时再做：

- 样本仍然偏短
- 你已经把数据定义打磨得比较稳定
- 你愿意跑 overnight 甚至更久

超过这个量级后，本地当然不一定完全跑不动，但“迭代效率”通常开始变差，不再适合作为主力学习循环。

## 我对你现在的建议

如果目标是把这个项目做成一个热门的 Gemma 4 微调学习项目，我建议下一阶段优先把数据扩到：

- `300 - 800` train rows
- `60 - 120` eval rows

理由很简单：

1. 比现在 `80 train` 更像一轮真正的学习实验
2. 在这台 `M5 Pro + 48GB` 机器上仍然很适合本地迭代
3. 足够支撑更像样的：
   - curriculum compare
   - direct mixed vs staged compare
   - argument alignment 分析

不建议第一步就冲到几千条，因为你现在剩下的主要问题已经从“能不能跑通”变成了：

- cross-domain 解耦
- reroute 参数对齐
- multi-tool chain 参数稳定性

这些问题先在 `300 - 800` 的量级里解决，收益更高。

## 一句话建议

当前 workflow 已经通了，下一阶段最合适的数据目标不是 `80 -> 8000`，而是先把它稳稳推到：

- `80 -> 300~800`

这样最符合这台机器的迭代效率，也最适合做成一个用户能真正跟着学会的 Gemma 4 微调项目。
