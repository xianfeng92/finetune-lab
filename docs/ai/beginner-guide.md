# finetune-lab 新手向导读

这份文档面向**完全没接触过模型微调**的人。看完之后你应该能回答三个问题：

1. 微调到底在做什么、为什么需要它
2. 这个仓库把"微调"拆成了哪几块、每一块的产物是什么
3. 我自己第一次该跑什么

不需要先看 `AGENTS.md` 或 `project-context.json`，那些是写给 AI agent 的；这份是写给人的。

---

## 1. 用一句话理解微调

一个大模型（比如 Gemma 4 E2B-it）出厂时已经在海量通用语料上**预训练**过，会"说话"，但不会按你的业务规则说话。**微调（fine-tuning）** 就是用一份小而精的样本，把它的行为往你想要的方向再推一下。

类比一下：

| 阶段           | 类比                          | 这个仓库怎么对应                                  |
| -------------- | ----------------------------- | ------------------------------------------------- |
| 预训练         | 念完了大学，通识能力很强      | `google/gemma-4-E2B` / `gemma-4-E2B-it` 这些权重 |
| 指令微调       | 学会"听人话、按格式回答"     | `-it` 后缀的 instruct checkpoint                  |
| 你做的微调     | 进你的部门、学你们的工作流    | 本仓库 `make real-train-mac` 干的事               |
| 评测 / probe   | 入职考核                      | `make probe-mac` / `make real-probe-mac`         |

**关键反直觉：** 微调不是把"知识"塞进模型，而是改变它**在已有能力上的偏好**。所以数据样本的"行为信号"比数据数量更重要——这一点贯穿整个仓库。

---

## 2. 你会反复遇到的几个术语

只列你在这个仓库里**真的会看到**的概念，别的先不管。

### 2.1 SFT（Supervised Fine-Tuning，监督微调）

给模型成对的「输入 → 期望输出」样本，让它学着模仿。这是最常见、最简单的微调方式，也是本仓库默认走的路径。

样本长这样（简化版）：

```json
{
  "messages": [
    {"role": "user", "content": "帮我把空调调到 22 度"},
    {"role": "assistant", "tool_calls": [{"name": "set_ac_temperature", "arguments": {"value": 22}}]}
  ],
  "tools": [ /* 候选工具 schema */ ]
}
```

模型要学的不是「天气知识」，而是「在候选工具里挑对名字、把参数填对」。

### 2.2 LoRA（Low-Rank Adaptation）

全参数微调要更新整个模型的所有权重，对显存和磁盘都很狠。LoRA 的做法是：**冻结原模型，只在旁边训练一组很小的"补丁矩阵"（adapter）**。训练快、产物小（几 MB～几十 MB）、可以挂载/卸载。

本仓库的"真实训练"路径全部是 LoRA：你训完得到的不是一个新模型，而是一个 adapter 目录。

### 2.3 MLX

Apple 自己出的本地训练/推理框架，专门吃 Apple Silicon 的统一内存。本仓库的真实微调通过 `mlx_lm.lora` 完成，所以模型要用 **MLX-converted** 版本（默认 `mlx-community/gemma-4-e2b-it-4bit`），原始 `google/*` 权重不能直接喂给 MLX。

### 2.4 base vs instruct

- `gemma-4-E2B`：base 模型，只会续写，不会"听话"
- `gemma-4-E2B-it`：instruct 模型，已经做过指令对齐，会按对话格式回答

新手默认用 `-it` 版本（教学更直观），`make gemma-track-pack` 会把两者的角色显式对照出来。

### 2.5 tool call / structured output

让模型的输出不是自然语言，而是**结构化的工具调用 JSON**。这是本仓库的核心专题——比起"让模型写得更通顺"，"让模型在候选工具里挑对、参数填对"是更适合小模型的微调任务。

### 2.6 held-out / probe

训练数据要切出一小份**不参与训练**的样本（held-out），训完之后用它来"考"模型，看到底学到了没有。这一步在本仓库叫 **probe**。

> 重要心智：**loss 下降 ≠ 学会了**。loss 只说明训练曲线在收敛；probe 才告诉你模型在 unseen case 上行为有没有真的变。

### 2.7 curriculum / consolidation / replay

微调进阶时会遇到的三种数据组织策略，本仓库都有现成入口：

- **curriculum（课程式）**：先训简单（单工具）→ 再训复杂（多工具），分阶段
- **consolidation（巩固）**：分阶段训完后再补一轮 mixed 数据，把"边界能力"找回来
- **replay（回放）**：后期阶段里混入早期样本，避免**灾难性遗忘**

`make real-stage-curriculum-consolidation` 是本仓库目前实测最好的路径。

### 2.8 preference / DPO（暂时知道有这回事就行）

SFT 教模型"该怎么答"，preference tuning 教它"在两个答案里偏好哪个"。Level 6 demo 才用得上，前期不用管。

---

## 3. 这个仓库把微调拆成了哪几块

整体是一条流水线，每一块都有 `make` 入口、都会落到磁盘上一份产物：

```
data 数据生成 → train 训练 → probe 评测 → compare 对比 → web 前端可视化
```

对应到目录：

| 目录              | 作用                                                    |
| ----------------- | ------------------------------------------------------- |
| `training/data_pipeline/` | 把 schema + seed 生成成 SFT 样本，做合法性校验   |
| `training/finetune/`      | smoke train（教学模拟） + real LoRA 训练 + probe |
| `data/`                   | 生成出来的训练/验证/测试数据                     |
| `outputs/`                | 每次跑完产生的 manifest、metrics、probe 结果     |
| `web/`                    | 把上面所有产物拼成一个可视化前端                 |
| `docs/ai/`                | 给 agent 和人读的指南（你现在看的就是其中一份） |

### 3.1 两条并行的训练路径

仓库里有**两套**训练入口，一开始很容易搞混：

| 路径          | 入口                       | 是否真的更新权重 | 适合什么          |
| ------------- | -------------------------- | ---------------- | ----------------- |
| simulated     | `make smoke-train-mac`     | ❌ 模拟          | 第一次理解流程    |
| real MLX LoRA | `make real-train-mac`      | ✅ 真的训        | 看真实行为变化    |

**新手建议先跑 simulated 的，10 秒内能看到一整条链路的产物长什么样；再去碰 real 的。**

### 3.2 六级学习路线（learning roadmap）

`project-context.json` 里定义了 Level 1 ～ Level 6，每一级都有自己的 `make` 入口和教学目标：

1. **Level 1** — 先定义任务和成功标准（不写代码）
2. **Level 2** — 理解数据 schema 和 chat template
3. **Level 3** — 第一次跑 SFT（simulated → real）
4. **Level 4** — 用 probe 解读结果
5. **Level 5** — 专题：tool routing + structured output
6. **Level 6** — 进阶：preference tuning + scale-up

按顺序往下就行，不要跳级。

---

## 4. 你第一次该跑什么

不要自己拼命令，全部走 `make` 入口。最稳的起手：

```bash
make ai-onboarding   # agent 扫一遍仓库，告诉你环境哪里没准备好
make ai-setup        # 缺什么补什么（Python 虚拟环境 / 前端依赖）
make ai-lab          # 跑一遍最小教学闭环（数据→训练→probe→前端）
```

跑完之后你应该会有这些产物，去打开看看：

- `outputs/agent/onboarding-report.md` — 当前仓库 readiness
- `data/sft/v1-seed-anchor-demo/samples.jsonl` — 真实的 SFT 样本长什么样
- `outputs/level1/baseline-eval-pack.json` — baseline 是怎么定义的
- `outputs/gemma4-e2b-mlx-demo-unsloth-vlm/inference-probe-results.json` — probe 结果

想继续走真实 LoRA 路径（要求 Apple Silicon）：

```bash
make bootstrap-real-finetune   # 安装 MLX 相关依赖
make real-finetune-data        # 把数据转成 chat+tools 格式
make real-train-mac            # 真的训一次 LoRA adapter
make real-probe-mac            # 真的评一次
```

---

## 5. loss 曲线读图

跑完真实训练之后，每个 run 目录会落两份和 loss 相关的产物：

- `outputs/<run>/train-metrics.jsonl` — 每隔若干 step 记一行的训练 metrics
- `outputs/<run>/run-manifest.json` — 整个 run 的汇总，里面有 `avg_loss`

打开 `train-metrics.jsonl` 长这样（取自 `gemma4-e2b-real-mlx-lora-large-direct`）：

```json
{"step": 40,  "loss": 5.135, "learning_rate": 1e-05, "trained_tokens": 1395}
{"step": 80,  "loss": 1.35,  "learning_rate": 1e-05, "trained_tokens": 2780}
{"step": 120, "loss": 0.644, "learning_rate": 1e-05, "trained_tokens": 4118}
...
{"step": 800, "loss": 0.012, "learning_rate": 1e-05, "trained_tokens": 26867}
```

### 5.1 loss 是什么

每一步训练，模型对当前样本做一次预测，**loss 就是预测和目标差多少**。优化器的工作就是不断调 LoRA adapter 的权重，让 loss 往下走。换句话说：**loss 是训练在不在干活的体温计，不是模型最终好不好的成绩单。**

数量级先有个感觉：

- `loss > 4` —— 基本只是在乱猜（模型还没"对上节奏"）
- `loss ≈ 1` —— 已经能把大部分 token 预测对了
- `loss < 0.1` —— 训练集上几乎能背出来

上面那条 `5.135 → 0.012` 是 800 step 的真实曲线，跨度近三个数量级。

### 5.2 一条"健康"的曲线长什么样

把 `step` 当 x 轴、`loss` 当 y 轴画出来（前端 `make web-build` 会做这件事），健康形态有三个特征：

1. **早期下降快**：前 5%～10% step 砍掉一大半 loss
2. **中段平滑下降**：没有大起大落的尖刺
3. **后段趋于平坦**：loss 不再显著下降，曲线"贴地"

`run-manifest.json` 里的 `avg_loss` 就是这条曲线的均值（large-direct 那次是 `0.4101`）。它适合做**两个 run 之间的横向比较**，但**不适合判断单个 run 的好坏**——一条只跑了 20 step、loss 还没收敛的 run，avg_loss 可能也很低，不代表它学到了。

### 5.3 几种典型病态曲线

| 形态                               | 大概在说什么                             | 你下一步该做什么                              |
| ---------------------------------- | ---------------------------------------- | --------------------------------------------- |
| 几乎是平的，没怎么降               | 学习率太低 / 数据信号太弱                | 提高 epoch、检查样本结构是否真的有学习信号    |
| 一路猛降到 ≈0，但 probe 全错       | **过拟合**：把训练集背下来了，没泛化     | 减 epoch、加数据、看 held-out 而不是 train    |
| 中途突然飙高、再也下不来           | 学习率过大 / 梯度爆炸                    | 调小 LR、检查是不是数据 schema 出了问题       |
| 抖得很厉害（噪声大）               | batch 太小或样本异质性强                 | 看是不是单个 batch 里混了截然不同的任务       |
| 降到一半就卡住                     | 模型容量不够 / LoRA rank 太小            | 短期可接受；长期考虑升级到更大 checkpoint     |

第二种"过拟合"最容易踩。它在曲线上看起来**最漂亮**，但只看 loss 你完全发现不了——这就是为什么本仓库一定要走完 `make probe-mac` / `make real-probe-mac`。

### 5.4 这个仓库目前不记 validation loss

正经训练框架通常会同时记两条曲线：

- **训练 loss**（在 train split 上）
- **验证 loss**（在 valid split 上，每隔 N step 评一次）

两者在中后期分叉就是过拟合的典型信号。**但本仓库的 `train-metrics.jsonl` 只记训练 loss**（`mlx_lm.lora` 默认行为），所以你**必须用 probe 来代替验证 loss 的角色**。这也是为什么 `data/real-finetune/v1-*/` 下要切 `train / valid / test` 三份——valid/test 留给 probe，不混进训练。

### 5.5 一句话总结

> 看 loss 是为了确认"训练在跑"；看 probe 才能确认"模型学到了什么"。两者都看，永远不要只看一个。

---

## 6. 看到不懂的概念怎么办

按下面这个顺序找答案，不要直接搜全网：

1. 先 grep 一下仓库——`docs/ai/workflows.md` 通常有最近更新的解释
2. 看 `project-context.json` 的 `learning_roadmap` 字段，里面每一级都标了 pitfall
3. 还不懂就问 Claude / Codex，让它结合仓库当前状态解释——agent 接得住，因为这个仓库就是为 agent 协作设计的

---

## 7. 一些常见误区（提前打预防针）

- **"训练 loss 一直在降，说明模型变强了"** —— 不一定。请用 probe 判断行为是否真的变了。
- **"数据越多越好"** —— 在小模型上，几百条高质量的、行为信号清晰的数据，往往比几千条噪声数据效果好得多。
- **"我能直接把 `google/gemma-4-E2B-it` 喂给 `mlx_lm.lora`"** —— 不行。MLX 真实训练需要 MLX-converted checkpoint，本仓库默认用 `mlx-community/gemma-4-e2b-it-4bit`。
- **"simulated smoke train 也算微调过了一次"** —— 不算。它只是把流程跑了一遍，不更新权重。要看真实行为变化必须走 `real-*` 那条路径。
- **"分阶段 curriculum 一定比 mixed 直接训好"** —— 仓库实测里，`real-stage-curriculum-replay` 最终还没超过 `direct mixed-task 3 epoch`；目前最好的是 `real-stage-curriculum-consolidation`。这是个开放问题，本仓库就是为了让你能复现并回答这种问题。
