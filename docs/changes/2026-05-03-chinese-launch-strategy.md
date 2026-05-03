---
title: Chinese Launch Strategy for finetune-lab
status: proposed
owner: codex
created: 2026-05-03
target_audience: Chinese AI learners and indie developers
primary_message: 微调第一次看懂
---

# Chinese Launch Strategy for finetune-lab

## 目标

第一波不把 `finetune-lab` 当成通用 fine-tuning framework 推，而是当成一个中文 AI 学习者能立刻看懂、收藏、复现、转发的微调学习项目。

核心承诺：

> 不是又一个微调脚本仓库，而是一个让你看见模型行为如何改变的微调实验课。

第一波目标用户：

- 刚开始学 LLM fine-tuning 的中文 AI 学习者
- 想在 Mac / 本地环境跑通一次微调的独立开发者
- 想理解 SFT、LoRA、tool calling、probe 的工程实践者
- 想把 Codex / Claude 带进仓库工作流的 AI-native 开发者

## 当前机会判断

`finetune-lab` 现在已经具备一个很稀缺的组合：

- `make ai-onboarding` 能判断 readiness
- `make ai-lab` 能跑最小教学闭环
- Web 实验台能看 data、training runs、observatory、probe compare
- 真实 MLX LoRA 路线已经有多轮 run 和 probe 证据
- 项目已经开始把 `loss 下降 != 学会了` 作为核心教学心智

但是，中文圈传播时不能首先讲“我们有 38 个 run、strict benchmark、LiteRT parity、PolicyGateway”。这些是可信度材料，不是第一屏卖点。

第一屏要讲：

1. 微调到底在学什么
2. 为什么不能只看 loss
3. 怎么用 3 条命令跑通
4. 跑完以后在哪里看模型有没有真的学会

## 参考项目与可借鉴机制

截至 2026-05-03 的公开 GitHub 页面和趋势页显示，当前热门 AI 开源项目有几个共同传播机制：

| 项目 | 公开信号 | 爆点机制 | 对 finetune-lab 的启发 |
| --- | --- | --- | --- |
| Ollama | 约 171k stars | 一条命令，本地跑模型 | 把 `make ai-lab` 做成第一心智 |
| Open WebUI | 约 135k stars | 非专家也能使用的本地 AI UI | Web 不只是 dashboard，要像课程入口 |
| Dify | 约 140k stars | 可视化 workflow + 应用搭建 | 把微调链路包装成可复用 recipe |
| ComfyUI | 约 111k stars | workflow 可视化、可分享 | 做 `Recipe Gallery`，让实验路径可截图传播 |
| LLaMA-Factory | 约 70.8k stars | 统一 fine-tuning recipe | 不拼通用性，借鉴 stage/recipe 心智 |
| Unsloth | 约 63.5k stars | 低门槛训练、速度感、免费 notebook | 提供“先看 demo，再本地跑”的双入口 |
| LLMs-from-scratch | 约 91.8k stars | 章节化学习、代码即教材 | 定位成 `learn fine-tuning by running it` |
| Codex / Goose / ADK | agent-native 项目快速增长 | 让 agent 接手工程流程 | 强化 `AGENTS.md + ai-onboarding` 差异化 |

这些项目的共性不是功能最多，而是第一眼能回答：

- 我是谁
- 我解决什么痛点
- 我怎么开始
- 我能不能马上看到结果

## 核心定位

英文定位：

> Learn fine-tuning by watching a model change behavior, not by staring at loss curves.

中文定位：

> 用一条可视化链路，把 SFT 数据、LoRA 微调、held-out probe、case diff 全部跑给你看。

短口号：

- 微调第一次看懂
- 别只看 loss，看模型到底学会了什么
- 3 条命令跑通 data -> train -> probe -> diff
- 把微调从黑盒训练，变成可视化实验课

## 主线打法：A. 微调第一次看懂

第一波只打一条主线：

> loss 降了，不代表模型学会了。`finetune-lab` 让你看到模型到底学到了什么。

原因：

- 中文 AI 学习者普遍听过微调，但不理解训练结果怎么判断
- “loss 下降但 probe 失败”有天然反差，容易形成传播钩子
- 项目已有真实 artifacts 支撑，不是纯科普
- Web 实验台和 case diff 能把这个反差讲透

侧翼卖点：

- Mac / Apple Silicon 本地真实 LoRA 路径
- AI-native 仓库交接：Codex / Claude 能自己读、跑、解释
- Tool calling / structured output 是真实 agent 场景

## 产品改造范围

### 1. README 首屏

目标：30 秒让中文用户知道为什么要 star。

首屏结构：

1. 一句话定位：微调第一次看懂
2. 一张关键截图或 GIF：probe diff / loss trap / data-to-diff
3. 三条命令：

```bash
make ai-onboarding
make ai-setup
make ai-lab
```

4. 一个反直觉结果：

```text
loss 下降很漂亮，不代表模型真的学会。
finetune-lab 会用 held-out probe 和 case diff 告诉你：模型到底选对工具没有、JSON 有没有合法、行为有没有符合预期。
```

5. 两个入口：

- 在线 demo：先看，不装依赖
- 本地实验：clone 后跑 `make ai-lab`

### 2. Web 首屏

当前 Web 已经有 Beginner Guide、Overview、Data Pipeline、Observatory、Training Runs、Probe Compare。下一步需要把第一屏改成“课程入口”，而不是把指标先抛给用户。

推荐新增或重排：

- `Start Here`：新手三步
- `Loss Trap`：loss 下降但 probe 失败的可视化对照
- `First Fine-tune Tour`：从一条样本走到一次 probe diff
- `Recipe Gallery`：四个可复现实验卡片

保留专业面板，但降到二层：

- edge-bench
- strict benchmark
- LiteRT parity
- long run registry
- data governance

### 3. Recipe Gallery

第一波只做 4 个 recipe：

| Recipe | 教学问题 | 产物 |
| --- | --- | --- |
| `loss-is-lying` | 为什么 loss 降了也可能没学会 | 一组 loss/probe 反例卡 |
| `first-lora` | 第一次本地 LoRA 微调会产出什么 | run manifest、adapter、metrics、probe |
| `tool-calling` | 模型如何学会选工具 | sample anatomy + expected/predicted diff |
| `curriculum-vs-direct` | 为什么课程式训练可能更稳 | direct vs curriculum compare |

每个 recipe 都要有：

- 一句话问题
- 标准 `make` 命令
- 输入 artifact
- 输出 artifact
- Web 查看位置
- 30 秒解释
- 可截图卡片

### 4. 推广素材包

新增 `docs/launch/`，只放传播素材，不混进工程 specs：

```text
docs/launch/
├── chinese-launch-thread.md
├── x-launch-thread.md
├── zhihu-article-draft.md
├── juejin-post.md
├── v2ex-post.md
├── bilibili-script.md
├── xiaohongshu-engineering-note.md
└── assets-checklist.md
```

第一波素材主题：

1. `loss 降了 99%，模型为什么还是没学会？`
2. `AI 小白第一次微调：从 SFT 数据到 LoRA 到 probe`
3. `别再只看训练曲线了：用 case diff 看模型行为变化`
4. `把微调仓库交给 Codex/Claude：agent 自己 onboarding、训练、评测`

X 单独处理，不直接搬运中文稿。X 的职责是把项目打进全球开发者视野，用英文/双语 thread 强调：

- fine-tuning should be learned by behavior diffs, not only loss curves
- local-first / Apple Silicon path
- agent-native onboarding
- visual lab and recipes

## 推广渠道

### 第一优先级

- 知乎：适合长文解释“loss trap”和微调心智
- 掘金：适合工程向教程和命令链
- V2EX：适合独立开发者冷启动反馈
- 即刻：适合短图文和开发进度连续发布
- B站：适合 8-12 分钟“第一次微调跑通”视频

### 第二优先级

- X：用英文/双语 thread 承接全球开源 AI、Local LLM、fine-tuning、agent-native 开发者；不作为中文首发主阵地，但要同步发布
- 小红书：只做工程图解，不做泛泛 AI 鸡汤
- 公众号：做复盘长文，沉淀搜索流量
- GitHub Discussions / Issues：承接反馈和 good first lab

## 发布节奏

### T-7 到 T-3：产品打磨

- README 首屏重写
- Web `Start Here` 和 `Loss Trap` 到位
- Recipe Gallery 第一版到位
- `make ai-lab` 重跑并确认输出路径
- 生成 3-5 张核心截图

### T-2 到 T-1：素材预热

- 写知乎长文草稿
- 写 X thread，并准备 3 张配图：hero、loss trap、probe diff
- 写 V2EX / 掘金短版
- 录制 GIF 或短视频
- 准备 GitHub release notes
- 标出 good first issue

### T 日：首发

发布顺序：

1. GitHub README / release 更新
2. 知乎长文
3. X thread
4. 掘金工程版
5. V2EX 项目帖
6. 即刻连续图文
7. B站视频或先发预告

首发当天重点不是求 star，而是求反馈：

- “哪一步你没看懂？”
- “你最想拿什么数据集试？”
- “你希望下一个 recipe 是什么？”

### T+1 到 T+7：连续跟进

每天一个小主题：

- Day 1: loss trap
- Day 2: SFT sample anatomy
- Day 3: first LoRA adapter
- Day 4: probe diff
- Day 5: curriculum vs direct
- Day 6: agent handoff
- Day 7: roadmap 和 contributors

## 成功指标

第一波不要只看 star。

核心指标：

- GitHub stars：首周 300+，优秀 1000+
- 在线 demo 点击：首周 1000+
- README 到 `make ai-lab` 的转化反馈：至少 10 个用户成功跑通
- Issues / Discussions：至少 10 个真实问题
- 中文平台收藏/评论：知乎、掘金、V2EX 合计 100+ 互动
- X thread：首条 10k+ impressions，50+ bookmarks，10+ high-signal replies
- 新 recipe 请求：至少 5 个

质量指标：

- 用户能不能复述 `loss != learned`
- 用户能不能说清 `probe` 是干什么的
- 用户能不能从 Web 找到一条失败 case
- 用户能不能跑完 `make ai-lab`

## 明确不做

第一波不做：

- 不宣称是最强 fine-tuning framework
- 不和 LLaMA-Factory / Unsloth 正面拼训练能力
- 不把 LiteRT / Android / edge-bench 放到第一屏
- 不默认让新手跑重型真实训练
- 不用“值 10000w”做外部传播文案
- 不做夸张 benchmark 刷榜叙事

## 下一步实现切片

建议分 4 个小提交：

1. `docs: add chinese launch strategy`
   - 本文档

2. `docs: sharpen readme for chinese launch`
   - README 首屏重写
   - 增加“微调第一次看懂”主叙事
   - 增加 recipe 入口

3. `feat(web): add start-here and loss-trap launch panels`
   - Web 首屏课程化
   - Loss Trap 从 artifacts 自动取例子
   - 保留现有专业视图

4. `docs: add chinese launch asset kit`
   - `docs/launch/*`
   - X / 知乎 / 掘金 / V2EX / B站脚本草稿

## 设计自检

- 没有把目标用户扩大到所有 ML 工程师
- 没有把第一波传播变成 benchmark 宣传
- 没有要求新手直接跑重型真实训练
- 没有回避项目已有的技术证据
- README、Web、素材包三条线能互相导流
- `loss != learned` 是贯穿全部传播材料的核心记忆点
