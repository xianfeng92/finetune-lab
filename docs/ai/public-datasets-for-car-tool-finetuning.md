# Public Datasets For Car Tool Finetuning

## 目的

这份文档回答两个问题：

1. 现在网上有哪些公开数据，值得拿来补 `finetune-lab`
2. 这些公开数据怎样映射到当前仓库的 schema，帮助我们继续观察 `Gemma 4 E2B` 微调后的真实能力

先说结论：

- 公开数据里，**很难找到 OEM 级真实用户日志**
- 但可以找到一些很有价值的 **近邻数据**
- 对当前项目最值得优先接入的，是：
  - `CAR-Bench`
  - `ClarifyVC`
  - `KVRET`

它们更适合做：

- 表达多样性补充
- ambiguity / clarify / confirm 样本补充
- 多轮车内助手风格补充

不适合被误解成：

- 真实线上脱敏日志
- 可直接替代产品内真实数据的主训练集

## 现状判断

当前 `finetune-lab` 已经有：

- 车控工具 schema
- SFT 教学数据
- 真实 MLX LoRA 微调路径
- `behavior / risk / vehicle_state / expected_system_action`

但当前主数据仍然主要来自：

- 规则生成
- seed anchors
- 仓库内的教学型 task design

这足够做 workflow 和能力验证，但还不够回答：

- 更真实的自然表达变体会不会拉低效果
- ambiguity / clarify / confirm 这类行为，在更开放表达下还能不能稳住

所以现在补公开数据是值得的，但目标要明确：

- 不是追求“大而全”
- 而是优先补最能影响 `Gemma 4 E2B` 真实能力判断的 slice

## 候选公开数据

## 1. CAR-Bench

来源：

- [CAR-Bench 数据集（Hugging Face）](https://huggingface.co/datasets/johanneskirmayr/car-bench-dataset)
- [CAR-Bench 代码仓库（GitHub）](https://github.com/CAR-bench/car-bench)
- [CAR-Bench 论文（arXiv）](https://arxiv.org/abs/2601.22027)

我为什么把它排第一：

- 它最接近你现在的任务定义
- 它不是单纯 ASR 语音数据，而是 **automotive assistant benchmark**
- 它显式覆盖：
  - vehicle controls
  - disambiguation
  - hallucination / missing tools
  - policy-constrained behavior

和当前仓库最贴近的点：

- `tool_call`
- `clarify`
- `handoff`
- `_meta_reroute`
- 缺工具 / 缺参数时的保守行为

数据结构里最值得用的字段：

- `instruction`
- `context_init_config`
- `actions`
- `task_type`
- `disambiguation_element_*`
- `removed_part`

最适合当前仓库的使用方式：

- 不直接全量塞进训练
- 优先抽 `tasks_base`
- 再抽 `tasks_disambiguation`
- 最后把 `tasks_hallucination` 用作：
  - `handoff`
  - `clarify`
  - `unsafe hallucination` 评测集

最适合补强的能力：

- ambiguous routing
- missing-tool robustness
- policy-aware behavior

## 2. ClarifyVC

来源：

- [ClarifyVC（OpenReview）](https://openreview.net/forum?id=afO3vnSNsS)

我为什么把它排第二：

- 你当前最值得补的不是更多普通 `tool_call`
- 而是更真实的 `clarify / confirm` 样本
- ClarifyVC 正好聚焦 **ambiguous vehicle control commands**

和当前仓库最贴近的点：

- `clarify`
- `confirm`
- ambiguous vehicle command resolution
- multi-turn disambiguation

最适合当前仓库的使用方式：

- 优先抽 ambiguity case
- 把需要追问澄清的 case 映射成 `behavior = clarify`
- 把明确需要先确认的 case 映射成 `behavior = confirm`
- 暂时不要追求完整复现它的研究 pipeline

当前仓库里的最小接入入口：

- `make import-clarifyvc`

这条入口目前会做两件事：

- 镜像 `OpenReview` 论坛页和论文 PDF 到 `data/public-source/clarifyvc/`
- 生成一个 `paper_protocol_seed` 版本的最小 preview 到 `data/public-normalized/clarifyvc-v1/`

需要明确说明的是：

- 论文正文公开了协议、tier 和示例
- 但论文给出的匿名数据地址当前在本机环境下返回 `403`
- 所以这版 importer 是“协议接入”，不是“raw dataset mirror”

最适合补强的能力：

- 模型何时不该直接调用工具
- 模型何时应该先问一个 disambiguation question
- 模型何时应该进入高风险确认路径

需要注意的边界：

- ClarifyVC 更像研究数据和研究协议
- 你要吸收的是“歧义样本和行为决策信号”
- 不是把整个论文框架原封不动搬进仓库

## 3. KVRET

来源：

- [KVRET 官方下载页](https://nlp.stanford.edu/projects/kvret/)
- [KVRET Hugging Face 镜像](https://huggingface.co/datasets/ConvLab/kvret)
- [KVRET 论文](https://nlp.stanford.edu/pubs/eric2017kvret.pdf)

我为什么把它排第三：

- 它是经典的 in-car assistant 多轮对话集
- 但它主要是：
  - weather
  - calendar
  - point-of-interest navigation
- 和你当前的 HVAC / door / window / seat 车控工具不完全同域

所以它不是最适合直接补主训练集的。

它最有价值的地方是：

- 提供更自然的车内助手表达风格
- 提供多轮 dialogue 结构
- 提供用户澄清、上下文延续、非单轮工具调用语气

最适合当前仓库的使用方式：

- 先不把它映射成当前主线 `tool_call` 数据
- 更适合做：
  - `handoff`
  - `answer_only`
  - future domain extension
  - prompt / dialogue style augmentation

如果后续你扩 schema 到：

- navigation
- calendar
- weather

那 KVRET 的价值会显著上升。

## 不建议当前优先接入的公开数据

### Car-Command

来源：

- [Car-Command（Kaggle）](https://www.kaggle.com/datasets/oortdatahub/car-command)

问题：

- 它更偏音频命令识别
- 更适合 ASR 前段或 command classification
- 不适合当前这个以文本 tool-calling 和行为决策为主的微调主线

### CI-AVSR

来源：

- [CI-AVSR（ACL Anthology）](https://aclanthology.org/2022.lrec-1.731/)
- [CI-AVSR（arXiv）](https://arxiv.org/abs/2201.03804)

问题：

- 也是音视频 / 语音命令识别数据
- 和当前 `Gemma 4 E2B` 文本化工具调用微调距离较远

## 第一版接入策略

我建议不要把公开数据直接“并表”塞进当前主训练集，而是分三层接入。

### Layer A: Public Source Raw

放公开数据的原始镜像和最小清洗结果。

建议目录：

```text
data/public-source/
├── car-bench/
├── clarifyvc/
└── kvret/
```

这一层的目标：

- 保留原始来源
- 不和主训练集混在一起
- 方便以后重做映射

### Layer B: Public Source Normalized

把公开数据统一成仓库内部的中间格式。

建议目录：

```text
data/public-normalized/
├── car-bench-v1.jsonl
├── clarifyvc-v1.jsonl
└── kvret-v1.jsonl
```

这一层的目标：

- 每条样本都带上来源信息
- 每条样本都带上映射置信度
- 不直接进入主训练集

### Layer C: Public Blend Packs

从公开数据里抽取当前主线最需要的 slice，再并入实验包。

建议目录：

```text
data/public-blends/
├── public-ambiguity-pack-v1.jsonl
├── public-policy-pack-v1.jsonl
└── public-dialogue-style-pack-v1.jsonl
```

这一层的目标：

- 有选择地进入训练实验
- 不让整个仓库被公开数据“污染”
- 保持每次实验可解释

## 映射到现有 finetune-lab schema

当前仓库最重要的 schema 目标字段有：

- `category`
- `behavior`
- `risk`
- `vehicle_state`
- `domains_loaded`
- `loaded_tool_names`
- `messages`
- `expected_system_action`

下面是第一版映射规则。

## A. CAR-Bench -> finetune-lab

### 直接可映射字段

- `instruction` -> `messages[0].content` 的语义来源
- `context_init_config` -> `vehicle_state` 的候选来源
- `actions` -> `expected_tool_calls`
- `task_type` -> `category` / `behavior` 的重要线索

### 第一版映射建议

- `tasks_base`
  - 单工具动作 -> `single_domain_single_tool`
  - 多动作串联 -> `single_domain_multi_tool_chain` 或 `cross_domain_multi_tool`
  - `behavior = tool_call`

- `tasks_disambiguation`
  - 需要用户澄清 -> `behavior = clarify`
  - `category = clarify_required_action`

- `tasks_hallucination`
  - 缺工具 / 缺参数 -> 优先映射为 `handoff` 或 `clarify`
  - 不建议一开始把它们硬塞成 `tool_call`

### 风险映射

- vehicle controls like door/window while driving -> `risk = high`
- HVAC / seat comfort -> `risk = low` 或 `medium`
- 无法稳定判断时 -> 默认 `medium`

### 第一版接入目标

- 先只抽文本指令和动作序列
- 先不引入复杂 mock DB
- 先把它当成“行为与路由数据源”

## B. ClarifyVC -> finetune-lab

### 直接可映射字段

基于论文描述，最有价值的是：

- ambiguous command text
- clarification requirement
- disambiguation target
- resolved action

### 第一版映射建议

- ambiguity 需要追问 -> `behavior = clarify`
- ambiguity 但风险较高 -> `behavior = confirm`
- 已有足够上下文可 resolve -> `behavior = tool_call`

### category 映射

- `clarify_required_action`
- `confirm_required_action`
- 少数可直接映射成：
  - `single_domain_single_tool`
  - `cross_domain_multi_tool`

### expected_system_action 映射

- 需要先确认的 case:
  - `expected_system_action.type = create_pending_confirmation`

### 第一版接入目标

- 先把它作为 `clarify / confirm` 样本库
- 不追求动作域全覆盖
- 优先补强高价值 ambiguity slice

## C. KVRET -> finetune-lab

### 直接可映射字段

- dialogue turn text
- domain
- multi-turn context

### 第一版映射建议

当前不建议把 KVRET 大规模直接映射到主线 `tool_call`。

第一版更适合：

- `behavior = handoff`
- `behavior = answer_only`
- 未来扩 domain 时再升级成真正的 task data

### 当前价值

- 补车内助手表达风格
- 补自然问句和 multi-turn 语气
- 补“不属于当前车控 schema”的对话表达

## 第一版实施建议

如果现在就开始做，我建议分 4 步。

### Step 1

先落一层来源文档和下载协议。

产物建议：

- `docs/ai/public-datasets-for-car-tool-finetuning.md`
- `data/public-source/README.md`

### Step 2

先做最小 normalize 脚本，只处理文本和标签，不碰音频。

建议脚本：

- `training/data_pipeline/import_car_bench.py`
- `training/data_pipeline/import_kvret.py`
- `training/data_pipeline/import_clarifyvc.py`

### Step 3

先生成 3 个中间包：

- `public-ambiguity-pack-v1.jsonl`
- `public-policy-pack-v1.jsonl`
- `public-dialogue-style-pack-v1.jsonl`

### Step 4

只做两类实验，不要一开始全混：

- `small + current schema + public ambiguity boost`
- `medium + current schema + public ambiguity/policy boost`

这样最容易回答：

- `Gemma 4 E2B` 到底有没有因为公开数据补充而更会 `clarify / confirm`
- 而不是被新来源噪音拖坏整体结果

## 我最推荐的第一优先顺序

1. `CAR-Bench`
2. `ClarifyVC`
3. `KVRET`

原因很简单：

- `CAR-Bench` 最接近当前工具调用和 policy-aware 行为
- `ClarifyVC` 最接近当前最值得补的 ambiguity 能力
- `KVRET` 最适合做语言风格补充，但不适合先当主训练集

## 不要做的事

- 不要一开始把 KVRET 全量硬映射成当前车控工具
- 不要把音频数据优先级放到文本任务前面
- 不要把公开数据当成“真实 OEM 日志替代品”
- 不要一开始直接把 3 个数据源和主训练集合并成一个大包

## 建议的下一步

最合理的下一步不是立刻大规模训练，而是：

1. 先做 `CAR-Bench` 文本任务导入
2. 再做 `ClarifyVC` ambiguity slice 导入
3. 最后再补 `KVRET` 的风格层

这样你最先能看到的是：

- `Gemma 4 E2B` 在更真实 ambiguity 样本下会不会退化
- `clarify / confirm / reject` 这些行为会不会更稳

## 当前已实现的最小入口

仓库里现在已经有一个最小 `CAR-Bench` 导入器：

```bash
make import-car-bench
```

它当前会做三件事：

- 下载 `CAR-Bench` task JSONL 原始文件
- 镜像到 `data/public-source/car-bench/`
- 生成一个最小的 mapping preview 到 `data/public-normalized/car-bench-v1/`

注意：

- 当前只覆盖最容易映射到现有 schema 的 direct tool-call 子集
- 它是公开数据接入的第一步，不是完整训练集接入

## 参考来源

- [CAR-Bench 数据集（Hugging Face）](https://huggingface.co/datasets/johanneskirmayr/car-bench-dataset)
- [CAR-Bench 代码仓库（GitHub）](https://github.com/CAR-bench/car-bench)
- [CAR-Bench 论文（arXiv）](https://arxiv.org/abs/2601.22027)
- [ClarifyVC（OpenReview）](https://openreview.net/forum?id=afO3vnSNsS)
- [KVRET 官方下载页](https://nlp.stanford.edu/projects/kvret/)
- [KVRET Hugging Face 镜像](https://huggingface.co/datasets/ConvLab/kvret)
- [KVRET 论文](https://nlp.stanford.edu/pubs/eric2017kvret.pdf)
- [Car-Command（Kaggle）](https://www.kaggle.com/datasets/oortdatahub/car-command)
- [CI-AVSR（ACL Anthology）](https://aclanthology.org/2022.lrec-1.731/)
- [CI-AVSR（arXiv）](https://arxiv.org/abs/2201.03804)
