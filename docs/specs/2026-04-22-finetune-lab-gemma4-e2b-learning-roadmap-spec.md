---
title: finetune-lab Gemma 4 E2B Learning Roadmap Spec
status: implemented
owner: codex
created: 2026-04-22
updated: 2026-04-22
implements:
  - docs/changes/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-level1-baseline-pack-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-level5-tool-routing-and-structured-output-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-level6-preference-data-demo-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-gemma-scale-up-compare-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-level6-scale-up-rubric-impl-notes.md
  - docs/changes/2026-04-22-finetune-lab-learning-coverage-and-ai-native-hardening-impl-notes.md
reviews:
  - docs/reviews/2026-04-22-finetune-lab-gemma4-e2b-learning-roadmap-review.md
  - docs/reviews/2026-04-22-finetune-lab-learning-coverage-and-ai-native-review.md
---

## 背景

`finetune-lab` 现在已经具备最小 AI-native 闭环：

1. agent 可以接手 onboarding 和 setup
2. 仓库可以跑通 data -> train -> probe -> frontend
3. 前端已经能展示最小教学链路

下一阶段的目标，不再只是“把 pipeline 跑起来”，而是把仓库升级成一个更完整的微调学习项目：

- 让新用户知道先学什么、后学什么
- 让 agent 知道当前处于哪一个学习阶段
- 让前端从“实验结果页”升级成“学习路线图 + 教学实验台”
- 让项目围绕一个足够强、足够新、足够适合本地学习的 base model 展开

本轮默认选择 `google/gemma-4-E2B-it` 作为教学基座，并保留 `google/gemma-4-E2B` 对照路线。

## 目标

把 `finetune-lab` 设计成一个围绕 Gemma 4 E2B 的 AI-native 微调学习路线图：

1. 新用户下载仓库后，可以在 agent 帮助下，从 baseline 一路学到 SFT、probe、结构化输出与偏好优化
2. 仓库提供清晰的阶段化学习路径，而不是只给一组训练脚本
3. 前端把每个阶段的“目标、产物、差异、下一步”讲清楚
4. 学习主线优先面向本地实验、低门槛复现、可截图传播
5. 让 `finetune-lab` 更接近“热门 AI 微调学习项目”而不是“单次 demo”

## 非目标

- 本轮不追求覆盖所有开源微调框架
- 本轮不要求真实大规模 GPU 训练成为默认路径
- 本轮不把项目扩成通用生产训练平台
- 本轮不优先追求 benchmark 刷榜

## 机会判断

当前热门微调开源项目已经证明，学习型项目最有价值的不是“功能多”，而是“心智模型清晰”。

值得借鉴的对象包括：

- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory): 统一入口、统一 recipe、统一训练方法心智模型
- [Unsloth](https://github.com/unslothai/unsloth): 低门槛、本地可跑、对新模型和 UI 体验反应快
- [LitGPT](https://github.com/Lightning-AI/litgpt): 代码可读、抽象少、适合教学式理解
- [Axolotl](https://github.com/axolotl-ai-cloud/axolotl): 配置驱动、实验管理清晰
- [torchtune](https://github.com/meta-pytorch/torchtune): recipe 清楚、PyTorch 原生、适合解释训练过程
- [Alignment Handbook](https://github.com/huggingface/alignment-handbook): 把 continued pretraining、SFT、preference tuning 串成体系
- [Open Instruct](https://github.com/allenai/open-instruct): 强调 post-training 和 evaluation，不只看 loss

本项目应该从这些项目吸收四件事：

- 学习路径要分阶段，不要把几十个参数直接甩给用户
- evaluation 和 probe 必须是一等公民，不能只展示 loss
- 默认路径必须足够轻量，能在本地或低配环境跑完
- agent 必须能判断当前状态、下一步命令和产物位置

## Gemma 4 E2B 基座策略

选择 Gemma 4 E2B 的原因：

- Gemma 4 是新的开源模型家族，定位明确，适合 agent、structured outputs 和 edge 场景
- `E2B` 体量更适合作为教学起点，便于做本地实验和最小闭环
- `google/gemma-4-E2B-it` 更适合作为第一阶段默认基座，因为更容易稳定呈现“微调前后行为差异”
- `google/gemma-4-E2B` 应作为对照路线，帮助用户理解 base checkpoint 和 instruct checkpoint 的差异

本项目中的默认模型策略：

- 默认教学基座：`google/gemma-4-E2B-it`
- 对照实验基座：`google/gemma-4-E2B`
- 后续升级路线：`google/gemma-4-E4B-it`，以及更大 Gemma 4 checkpoint 的专题扩展

## 设计原则

- teaching-first：项目首先是一条学习路线，而不是一组命令
- gemma-first：主叙事围绕 Gemma 4 E2B 展开，避免模型选择过散
- agent-native：每个学习阶段都要能被 Codex / Claude 接手和解释
- diff-first：通过 before/after、20-step/100-step、base/it 对照来教学
- local-first：默认体验优先兼容本地和轻量路径
- frontend-as-curriculum：前端不只展示结果，要承担“课程目录 + 实验讲义”职责

## 六阶段学习路径

### Level 1: Baseline and Task Framing

学习目标：

- 理解什么问题值得用微调解决
- 先建立 prompt baseline，而不是一上来就训练
- 形成任务定义、成功标准和失败样本

默认产物：

- baseline prompt 集合
- held-out probe seed cases
- task brief / success rubric

前端展示重点：

- 为什么这个任务需要微调
- baseline 的典型失败类型
- 当前阶段还没有训练，主要在定义问题

### Level 2: Data and Schema

学习目标：

- 理解 instruction data、chat template、tool schema、structured outputs 的关系
- 学会看 `samples.jsonl`、validation report、schema 约束
- 理解“数据如何决定模型要学什么行为”

默认产物：

- `data/sft/**/samples.jsonl`
- `validation_report.md`
- dataset profile 和 error bucket

前端展示重点：

- 样本结构拆解
- tool choice / JSON output / instruction formatting 的信号来源
- 数据质量问题如何影响后续训练

### Level 3: First SFT on Gemma 4 E2B-it

学习目标：

- 理解 LoRA / QLoRA / full FT 的角色差异
- 用最小成本跑通第一次 SFT
- 学会读 run manifest、step metrics、adapter artifact

默认产物：

- run manifest
- train metrics
- adapter / checkpoint metadata

前端展示重点：

- 这次训练到底改了什么
- 20-step smoke train 用来验证什么
- loss 曲线只能说明什么，不能说明什么

### Level 4: Probe and Error Analysis

学习目标：

- 学会把训练结果映射回行为变化
- 用 held-out probe 看 exact hit、JSON validity、tool choice accuracy
- 建立 case-level diff 的阅读习惯

默认产物：

- probe results
- compare report
- error taxonomy

前端展示重点：

- before / after 行为对比
- exact hit 和 avg loss 不是同一件事
- 哪些 case 学会了，哪些 case 仍然没学会

### Level 5: Structured Outputs and Tool Calling Specialization

学习目标：

- 以 Gemma 4 E2B 为 base 学习工具调用、结构化 JSON、route selection
- 理解“把 tool definitions 烘焙进权重里”会带来什么收益
- 围绕 function/tool calling 做更像真实 agent 的微调专题

默认产物：

- tool-routing dataset pack
- structured output probe pack
- stage-specific compare view

前端展示重点：

- 为什么 structured outputs 是最值得学习的微调专题之一
- 模型是如何在多个候选工具之间做选择的
- schema、instruction 和 probe 如何形成闭环

### Level 6: Preference Tuning and Scale-up

学习目标：

- 理解什么时候继续堆 SFT，什么时候进入 preference tuning
- 学习 DPO / ORPO / rejection sampling 等进阶 post-training 概念
- 理解从 E2B 向更大 Gemma checkpoint 迁移时，工程和评测要怎么调整

默认产物：

- preference dataset demo
- policy compare report
- scale-up guidance

前端展示重点：

- 从“会做”到“做得更稳、更符合偏好”
- 小模型实验结论如何迁移到更大模型
- 这一阶段属于进阶路线，不作为默认第一次上手路径

## 仓库与 agent 设计要求

### 1. 学习阶段必须显式化

仓库需要新增或补全一组“学习阶段元数据”，让 agent 和前端都知道：

- 当前项目支持哪些 level
- 每个 level 的目标、命令、产物、推荐阅读
- 用户当前已经完成到哪一步
- 下一步最推荐跑什么

建议统一进入 `project-context.json` 和 `web/public/lab-data.json`。

### 2. Makefile 要按学习路径组织

在现有 `ai-onboarding`、`ai-setup`、`ai-lab` 基础上，后续命令应逐步支持：

- baseline / eval 相关入口
- Gemma 4 E2B-it 默认训练入口
- base vs it 对照实验入口
- structured output / tool calling 专题入口
- preference tuning demo 入口

要求：

- 命令命名与学习阶段一一对应
- agent 可以仅通过 `make help` 和文档判断下一步
- 重依赖步骤允许保留轻量 fallback

### 3. 产物协议要更教学化

每个 level 的输出不应只有训练文件，还应包含：

- 当前阶段说明
- 核心学习问题
- 本阶段需要关注的指标
- 常见误区

这些内容既可以写入文档，也可以被构建到统一数据层中供前端读取。

## 前端教学链路要求

前端应从“结果页”升级成“路线图 + 实验台”，至少补齐以下结构：

### 1. Learning Roadmap

一个显式的阶段导航，展示：

- Level 名称
- 当前推荐 base model
- 当前阶段学什么
- 完成该阶段后会得到什么

### 2. Why This Matters

每个阶段都要回答：

- 这一阶段解决什么问题
- 和上一阶段相比新增了什么能力
- 对真实 agent / product 有什么意义

### 3. Gemma Track

前端显式展示：

- 默认基座是 `google/gemma-4-E2B-it`
- 为什么默认从 it 开始
- 什么情况下切换到 `google/gemma-4-E2B`
- 什么时候升级到 `E4B` 或更大模型

### 4. Probe-first Views

前端必须把行为评测放在高优先级位置，而不是藏在训练指标后面。

至少包含：

- case-by-case compare
- tool choice / structured output 命中情况
- error buckets
- 训练指标与行为指标的区别说明

## 实现阶段建议

### Phase A: 路线图先落文档和数据层

- 在 `project-context.json` 增加 learning roadmap 元数据
- 在统一数据层里增加 levels / stage narratives / gemma track
- 前端先做路线图导航和阶段说明

### Phase B: 围绕 E2B-it 做默认教学链路

- 把现有 smoke train 叙事明确改成 Gemma 4 E2B-it 主线
- 增加 baseline、probe、structured output 的教学文案和对比视图
- 补一套面向 tool calling 的 stage-specific dataset/probe 说明

### Phase C: 增加对照和进阶路径

- 增加 `E2B` vs `E2B-it` 对照说明
- 增加 preference tuning / post-training 概念页
- 规划 `E4B` 或更大 Gemma 4 的升级实验

## 验收标准

- 仓库里新增一份显式的 Gemma 4 E2B 学习路线图 spec，并作为后续默认实现输入
- 新用户可以明确理解“先 baseline，再数据，再 SFT，再 probe，再专题化，再进阶”
- agent 能根据文档和数据层解释每个 level 的目标、命令和产物
- 前端首页或核心导航能体现这是一个“Gemma 4 E2B 微调学习实验台”
- 前端能解释为什么 structured outputs / tool calling 是本项目的关键学习主题
- 至少保留一条本地可跑的默认学习路径，不因引入新阶段而破坏最小闭环

## 参考对象

- [Google Developers Blog: Bring state-of-the-art agentic skills to the edge with Gemma 4](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
- [Hugging Face: Welcome Gemma 4](https://huggingface.co/blog/gemma4)
- [Google AI for Developers: Fine-tuning with FunctionGemma](https://ai.google.dev/gemma/docs/functiongemma/finetuning-with-functiongemma)
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- [Unsloth](https://github.com/unslothai/unsloth)
- [LitGPT](https://github.com/Lightning-AI/litgpt)
- [Axolotl](https://github.com/axolotl-ai-cloud/axolotl)
- [torchtune](https://github.com/meta-pytorch/torchtune)
- [Alignment Handbook](https://github.com/huggingface/alignment-handbook)
- [Open Instruct](https://github.com/allenai/open-instruct)
