# finetune-lab Chinese Launch Pack

> 主线：微调第一次看懂。别只看 loss，看模型行为到底有没有改变。

## 资产路径

| 场景 | 图片 | 用法 |
| --- | --- | --- |
| GitHub README / 首发主图 | `docs/assets/launch/overview-start-here.png` | 首图，说明这是一个“微调学习实验课”而不是脚本集合 |
| 核心反差钩子 | `docs/assets/launch/loss-trap.png` | 配合 `loss 降了 100%，probe exact 0/8` 的短帖 |
| 学习路径 | `docs/assets/launch/recipe-gallery.png` | 展示 4 条可复现路径 |
| 手机端预览 | `docs/assets/launch/mobile-start-here.png` | 适合即刻、小红书、朋友圈 |

## 一句话定位

```text
finetune-lab：一个让 AI 小白第一次看懂微调的开源实验课。
它把 SFT 数据、LoRA 训练、held-out probe、case diff 串成一条可跑可看的链路，专门解决“loss 降了，模型到底学没学会？”这个问题。
```

## GitHub Release / README 短介绍

```text
finetune-lab 是一个 AI-native fine-tuning learning lab。

它不是又一个“给你一堆训练脚本”的仓库，而是把微调拆成一条可以观察的学习链路：

data -> LoRA train -> held-out probe -> case diff -> Web lab

核心教学点很简单：

训练 loss 降了，不代表模型学会；一个 runtime 通过，也不代表部署 runtime 等价。

你需要看 held-out probe、工具名是否命中、参数是否正确、JSON 是否合法、行为是否真的符合预期。

第一次上手：

make ai-onboarding
make ai-setup
make ai-lab

Live demo: https://xianfeng92.github.io/finetune-lab/
Repo: https://github.com/xianfeng92/finetune-lab

补一句给工程读者：当前 edge-bench 证据显示 MLX adapter 保留 PolicyGateway 语义，但 GGUF fused runtime 暴露 confirm/refusal contract regression；LiteRT-LM 还只有 base-only 边界，不能写成 same-LoRA parity。
```

## 即刻 / 朋友圈短帖

配图：`docs/assets/launch/loss-trap.png`

```text
我做了一个开源项目：finetune-lab。

一句话：让 AI 小白第一次看懂“微调到底有没有学会”。

最想讲清楚的反直觉是：

loss 降了，不代表模型学会。

我在项目里放了一个很直观的 loss trap：
一条真实 LoRA run，train loss 从 7.24 降到 0.01，看起来很漂亮，但 held-out probe exact 是 0/8。

所以这个项目不让你只盯训练曲线，而是把 SFT 数据、LoRA 训练、held-out probe、case diff 放到一个 Web 实验台里看。

适合刚开始学 SFT / LoRA / tool calling / 本地微调的人。

Live demo: https://xianfeng92.github.io/finetune-lab/
Repo: https://github.com/xianfeng92/finetune-lab
```

## V2EX 项目帖

标题：

```text
做了一个让 AI 小白第一次看懂微调的开源实验课：finetune-lab
```

正文：

```text
最近在做一个开源项目 finetune-lab，想把“微调”从一堆黑盒训练脚本，变成一条能看懂、能复现、能让 agent 接手的学习链路。

它主要解决一个新手常见问题：

训练 loss 降了，模型到底学没学会？

项目里有一个很典型的 loss trap：
真实 LoRA run 的 train loss 从 7.24 降到 0.01，但 held-out probe exact 是 0/8。

所以 finetune-lab 的默认心智不是“看 loss”，而是：

data -> LoRA train -> held-out probe -> case diff -> Web lab

现在已经有：

- Beginner Guide：讲 SFT / LoRA / probe / loss trap
- Data Pipeline：看 SFT 样本和 held-out split
- Training Runs：看 SIM / REAL run、loss 曲线和 artifacts
- Probe Compare：看多 run 横向对比和 case-level diff
- AGENTS.md + make ai-onboarding：可以交给 Codex / Claude 接手

第一次跑：

make ai-onboarding
make ai-setup
make ai-lab

在线 demo：
https://xianfeng92.github.io/finetune-lab/

Repo：
https://github.com/xianfeng92/finetune-lab

想听听大家反馈：微调学习里，你最卡的是数据、训练、评测，还是“怎么判断模型真的学会了”？
```

## 掘金工程帖

标题：

```text
别只看 loss：我做了一个从 SFT 数据到 LoRA 到 probe 的微调学习实验台
```

开头：

```text
很多微调教程会教你跑一条训练命令，然后告诉你 loss 降了。

但新手真正想知道的是：

模型到底学到了什么？

我做的 finetune-lab 试图把这个问题工程化：每次训练后，不只看 train loss，还要看 held-out probe、tool name exact match、parsed JSON、case-level expected/actual diff。
```

正文结构：

```text
1. 为什么 loss 不够
   - loss 是训练过程信号，不是行为成绩单
   - 举例：loss 7.24 -> 0.01，但 probe exact 0/8

2. finetune-lab 的学习链路
   - data: SFT 样本和 held-out split
   - train: simulated smoke train / real MLX LoRA
   - probe: held-out behavior check
   - compare: 多 run 横向对比
   - frontend: Web 实验台可视化

3. 第一次怎么跑
   make ai-onboarding
   make ai-setup
   make ai-lab

4. 为什么选择 tool calling / structured output
   - 行为可测量
   - 工具名、参数、JSON 合法性都有明确判断标准

5. 为什么做成 AI-native repo
   - AGENTS.md
   - project-context.json
   - agent 能自己 onboarding、跑命令、解释 artifacts

6. 下一步
   - recipe gallery
   - 更多真实数据集
   - 更强的 case diff 和 benchmark
```

结尾：

```text
如果你正在学微调，不妨先别追求“训一个多大的模型”，而是先回答一个小问题：

我的模型行为真的改变了吗？

finetune-lab 想做的，就是把这个问题变成你能亲眼看到的实验。
```

## 知乎长文大纲

标题：

```text
为什么训练 loss 降了，模型还是可能没学会？我做了一个微调学习实验台
```

结构：

```text
1. 新手学微调最大的误解：把 loss 当成成绩
2. loss 是体温计，不是成绩单
3. 一个真实反例：loss 下降很漂亮，held-out probe 仍然失败
4. 正确闭环：SFT 数据 -> LoRA 微调 -> held-out probe -> case diff
5. 为什么 tool calling 是微调学习的好任务
6. finetune-lab 怎么把这条链路做成 Web 实验课
7. 本地怎么跑：make ai-onboarding / ai-setup / ai-lab
8. 为什么我把它做成 AI-native：让 Codex / Claude 能接手仓库
9. 未来 recipe：loss-is-lying / first-lora / tool-calling / curriculum-vs-direct
```

## B 站 8 分钟视频脚本

```text
00:00 开场：今天不讲“怎么让 loss 降”，讲“怎么知道模型真的学会了”
00:30 展示 finetune-lab 首页：微调第一次看懂
01:20 解释 SFT 数据：模型到底吃了什么样本
02:10 解释 LoRA：不是训出一个新模型，而是 adapter
03:00 展示 loss trap：loss 7.24 -> 0.01，但 probe 0/8
04:00 解释 held-out probe：没参与训练的样本才像考试
05:00 展示 Probe Compare：多 run 横向对比
06:00 展示 case diff：input / expected / actual
07:00 展示 AI-native：make ai-onboarding，让 agent 接手
07:40 总结：微调第一次看懂，不是看 loss，而是看行为改变
```

## X / 英文短帖引流

配图：`docs/assets/launch/loss-trap.png`

```text
Fine-tuning is not about watching loss go down.

It is about checking whether model behavior actually changed.

In finetune-lab, a real LoRA run can show a beautiful loss drop while still failing held-out probes.

So the lab pairs:

data -> LoRA train -> held-out probe -> case diff

Repo: https://github.com/xianfeng92/finetune-lab
Demo: https://xianfeng92.github.io/finetune-lab/
```

## 发布顺序

1. 更新 GitHub README 和截图
2. 发 X thread，同步主图和 loss trap 图
3. 发即刻短帖，主打 `loss trap`
4. 发 V2EX，主打“开源项目求反馈”
5. 发掘金工程帖，主打 `data -> train -> probe -> diff`
6. 发知乎长文，主打“为什么 loss 不够”
7. 第 2 天补一条 follow-up：`first-lora`，讲 adapter / manifest / metrics
