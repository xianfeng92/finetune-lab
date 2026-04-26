---
title: Web Beginner UX Questions Review
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26 (P1+P2 done)
implements: []
reviews: []
---

# 2026-04-26 Web Beginner UX Questions Review

## 目的

以**完全没接触过模型微调**的人的视角，把当前 web 前端（`make web-build`）从头到尾走一遍，把每一处卡住、看不懂、可能产生误解的地方都如实记下来。

这份文档**不给答案、不做解读**。它是给后续设计/重构 web 前端用的需求输入：哪些信息默认对小白不可读，就是要被改写、被解释、被分层、或被藏起来的。

走查方式：从 Overview 顶部一直滚到底，再依次切 Agent Handoff / Data Pipeline / Training Runs / Probe Compare 四个 tab，每个 tab 都从顶部往下逐屏看。

---

## A. 整体感受（在打开任何具体 tab 之前）

A1. 一打开就看到 Hero `Clone it. Hand it to an agent. Watch a model learn.`——我作为小白完全不知道 "agent" 在这里指什么。是浏览器里某个虚拟人物？还是命令行里跑的程序？还是这个网站本身？

A2. 五个左侧 tab `Overview / Agent Handoff / Data Pipeline / Training Runs / Probe Compare` 从字面我**只看得懂第一个**。后面四个分别是什么意思、谁应该看哪个，我无从判断。

A3. 全站没有"我应该按什么顺序读这五个 tab"的提示。我会下意识从 Overview 开始，但其它四个之间有没有先后关系？

A4. 没有任何"如果我从来没微调过，先看哪个？"的入口。

---

## B. Overview tab

### B1. Hero 区

- **三个起手命令** `make ai-onboarding / ai-setup / ai-lab`：
  - 这是要我打开终端跑的吗？还是网站会替我跑？
  - 我没装过这个仓库，"make" 本身是什么我也不一定知道。
  - 三个命令放一起，但没有解释三者的依赖关系（必须按顺序跑？跳一个会怎样？）。

- **`AI-NATIVE FINE-TUNING LAB`** 这个 eyebrow 文字：
  - "AI-native" 没有任何解释。是说这个仓库自己用了 AI？还是用来训练 AI？还是说前端里嵌了 AI？

### B2. 四张 KPI 卡

- `SAMPLES 100 — SFT demo`：
  - "SFT" 是缩写，第一次出现就用了。我得自己猜或自己查。
  - "100" 是多还是少？小白没参照系。
  - "demo" 是说这是演示用、不严肃的数据吗？那真实数据会更多吗？

- `RUNS 9 — 12 → 800 steps`：
  - "Run" 是什么？一次训练叫一次 run？
  - "12 → 800 steps" 是范围还是从→到？为什么是这两个数？
  - 9 个 run 是被推荐都看的还是有主次？

- **`LOSS ↓ 99.8% — 800-iter real MLX LoRA run`**：
  - **整张卡是绿色的，看起来像是核心成绩**。
  - 但我完全不知道 "loss 降 99.8%" 等价于"模型变好了 99.8%"吗？
  - "800-iter real MLX LoRA run" 这一行是 hint，但 "iter / real / MLX / LoRA" 四个词每一个都需要解释。
  - 别的 run 的 loss 降幅是不是都接近 100%？这数字是惊艳还是平庸？

- `ONBOARDING ready — make ai-lab`：
  - "ready" 是说什么 ready 了？我做好准备，还是仓库做好准备？
  - 既然 ready 了，为什么还要我跑 `make ai-lab`？

### B3. Roadmap（六张 Level 卡）

- 卡片 header 是 `LEVEL 1 / LEVEL 2 / ...` + 一个绿色 `LIVE` 徽章：
  - "LIVE" 是什么意思？正在直播？这一级在跑？还是这一级已经做好可以用？
  - 唯一一个 Level 6 上的 `PARTIAL` 又是什么意思？比 LIVE 差一档？

- 每张卡都列了一个 model id（如 `mlx-community/gemma-4-e2b-it-4bit`、`google/gemma-4-E2B-it`）：
  - 同一份 roadmap 里不同 Level 用了**不同的模型 id 写法**（`mlx-community/...`、`google/...-it`、`google/...-E4B-it`）。我搞不清楚这些是同一个模型的不同版本，还是完全不同的模型。
  - "4bit"、"E2B"、"E4B"、"-it" 这些后缀都没解释。

- 每张卡里都有 `WHY IT MATTERS / FOCUS METRICS / ARTIFACTS / Pitfall`：
  - "FOCUS METRICS" 里塞了 `failure buckets / held-out cases / baseline behavior / schema validity / tool candidate set / ...` 这些都是行话。
  - "ARTIFACTS" 列出来一堆 `outputs/level1/...json` 路径，但我**根本无法点击**它们看里面是什么。所以列这些路径对我没意义。
  - "Pitfall" 写得不错（中文、是反面教材），但放在卡尾，我已经被前面所有专有名词砸晕了。

- 卡片密度：**6 张卡同屏堆**，每张又是七八段子结构。第一次打开的人不可能从头读到尾。

### B4. Level 1 详情（roadmap 下面又出现了一次）

- 突然多出一个 `Level 1: Baseline and Task Framing` 详情区，里面有 `TASK FRAMING PACK / BASELINE EVAL PACK` 两个子卡：
  - 我不理解为什么 Level 1 单独被详细展开，而 Level 2~6 没有。
  - "TASK FRAMING PACK" / "BASELINE EVAL PACK" 是行话，第一次出现没解释。
  - 子卡里有 `ROUTE HIT 2/6 / EXECUTABLE 3/6 / ARGUMENTS 2/6 / OVERALL PASS 0/6` 四个分子分母指标——四个都没解释。"OVERALL PASS 0/6" 还是 0，看起来像失败，但我不知道这是预期的（baseline 当然差）还是出 bug 了。

### B5. Gemma track 区

- 出现 `DEFAULT BASE / COMPARE WITH / SPECIALIZATION FOCUS` 三个 column。"BASE" 是什么意思（基础？基座？base model？）我得自己脑补。
- `Structured outputs + tool calling` 这一框写得很专业，但它假设我已经知道 "structured outputs"、"tool calling"、"route selection"、"JSON validity"、"tool choice accuracy" 都是干嘛的。

### B6. 参考项目

- 列了 `LLaMA-Factory / Unsloth / LitGPT / Alignment Handbook` 四个项目，每个一句中文描述。
- 我一个都没听过，看完反而更迷茫——是说这个项目和它们一样？比它们好？还是借鉴了它们？

### B7. 训练曲线区（藏在最底部，scrollY ≈ 17700）

- 一直滚到 Overview 倒数第二屏才看到 9 张 loss 曲线小图。
- 每张图标着 `MLX-LM.LORA · 800 STEPS` 或 `LOCAL-SIMULATED · 100 STEPS`：
  - 我现在才第一次知道有 simulated 这种东西。前面 KPI 卡里把所有 run 都数进 9 个，没区分。
  - "LOCAL-SIMULATED" 卡上写的"This run writes teaching artifacts with synthetic loss/adapter outputs instead of updating a real model checkpoint" —— 这是英文，而且讲的是"写假数据假装真的训"，听起来有点诡异。这是好事还是坏事？
- 几张曲线长得很奇怪，需要解读但没解读：
  - `12-iter` 那张降得比较平稳——但旁边显示 `avg loss 7.704`，对应右下角 `82.2%` 降幅。但卡尾的 probe（在 Probe Compare tab 看到）是 `0/8 exact`。我看不懂"loss 降了 82% 但 probe 全错"是怎么回事。
  - `96-iter` 那张猛降到接近 0 后变成一条贴底的直线——这看起来是不是哪里坏了？
  - `100-step smoke train` 那张是一条几乎完全平滑的直线，从左上斜到右下——看起来像是合成的不像是训练曲线。
- "Training curves" 这一节为什么放在 Overview 最底部，而不是在叫做 Training Runs 的那个 tab 里？

---

## C. Agent Handoff tab

C1. Tab 标题是 "Agent Handoff"——"handoff"（交接）是什么意思？谁交接给谁？

C2. 顶部 4 步 timeline `Probe the repo / Make it ready / Run the loop / Read the delta`：
  - 步骤名都是英文动词短语，加上 eyebrow `SENSE / PREPARE / TEACH / COMPARE`——文学感很强，但我作为小白看不出每一步具体会发生什么变化。
  - 第 4 步要我跑 `make smoke-train-mac-100 && make probe-mac-100 && make compare-probes`，三个命令链在一起。"compare-probes" 是比谁和谁？

C3. `Readiness` 区列了 8 个绿色 READY 徽章（`Python data env / Frontend dependencies / Demo dataset / ...`）：
  - 全绿，看起来很安心。但是我打开网页之前**根本没装过仓库**，怎么可能 8 项都 ready？
  - 这是不是反映的是 **Claude / 仓库作者的本地状态**，而不是我访问页面时的状态？

C4. `Learning progress 8/8 stages` —— 同样的疑问：这是谁的进度？每个访问者看到的都是 8/8 吗？那"进度"还有意义吗？

---

## D. Data Pipeline tab

D1. `Category coverage` 横条图列了 `single_domain_single_tool 30 / single_domain_multi_tool_chain 15 / cross_domain_multi_tool 15 / reroute_to_meta 10 / full_tool_fallback 10 / proactive_event_driven 10 / confirm_required_action 5 / reject_unsafe_action 5`：
  - 八个类别名都是英文 snake_case，没有一个有解释。
  - "reroute_to_meta"、"proactive_event_driven" 这些是行业术语还是这个仓库自己造的？
  - 数量分布悬殊（30 vs 5），但没说"这个分布是设计选择还是数据偏差"。

D2. `Train / held-out split`：
  - 三行只有路径名 `samples.jsonl / train.jsonl / held-out.jsonl`，没有数量、没有比例、没有解释为什么要分 train / held-out。
  - "held-out" 这个词第一次出现，但 Overview B7 里 "held-out probe" 也用过了。我不知道这是同一个东西。

D3. `Domain footprint` 横条图：`hvac 45 / window 37 / door 33 / seat 30`：
  - 这是数据集里**多少条样本涉及到这个 domain**，还是"领域特征覆盖率"？计数单位不明确。
  - 加起来是 145，但 SAMPLES 是 100。这不一致，我会怀疑数据。（推测是：一条样本可能多 domain，但没说明。）

D4. `Sample anatomy` 三栏并列：
  - 左侧 5 个样本 id `sft-v1-0001 ~ 0005` —— 但数据集是 100 条，剩下 95 条看不到？
  - 中间是 `SYSTEM_PROMPT`，写着 `loaded_tool_names=hvac_set_fan_speed,hvac_set_temperature` 和 `vehicle_state: {"speed_kph": 0, "power_state": "parked"}`：
    - "loaded_tool_names" 是模型可以用的工具？还是模型必须用的工具？
    - "vehicle_state" 这个上下文为什么放在 system prompt 里？小白容易以为这是模型生成的内容。
  - 右侧 `MESSAGES` 和最下方 `SFT_TEXT` 之间的关系不明：
    - 看起来 SFT_TEXT 是把 messages 拼接成 `<system>...</system><user>...</user>...` 格式。
    - 但为什么要看这种"拼接形式"？小白不明白训练时模型实际"看到"的是 SFT_TEXT 还是 MESSAGES。
    - 没解释 `<assistant_tool_calls>` 这种标签为什么不是普通对话。

---

## E. Training Runs tab

E1. **这个 tab 叫 Training Runs，但里面看不到 loss 曲线**。曲线在 Overview 最底部。这个信息架构很反直觉。

E2. `Run registry` 左栏列出 9 个 run，每个 run 标题是 run-id（`gemma4-e2b-real-mlx-lora-large-direct`），副标题是 `800-iter real MLX LoRA run`：
  - run-id 又长又像哈希，不友好。我看不出 run 之间的关系（哪个是基线？哪个是改进？）。
  - "real MLX LoRA run" 和 "smoke train" 这两类副标题文字差别很小，颜色也一样，**很容易看不出有 simulated 路径混在里面**。
  - 9 个 run 没分组、没排序解释。我点哪个开始看？

E3. `Run metrics` 右栏：选中一个 run 后显示 `MAX STEPS / AVG LOSS / TRAIN SPLIT / DATASET ROLE / TOOL SIGNAL / PARSED JSON`。
  - "TRAIN SPLIT" 显示一长串路径，被截断 (`data/real-finetune/v1-gemma4-e2b-large/train.jsonl`)。这是给谁看的？
  - "DATASET ROLE: train" —— role 有几个取值？为什么单独露出？
  - "TOOL SIGNAL 82/96" 和 "PARSED JSON 82/96" 数字一模一样，让我怀疑是不是同一个东西。
  - **关键问题：avg loss 0.4101 是好是坏？没有任何参照线、对照基线、"过拟合警告"等信号。**

E4. `Artifacts` 区列了一堆 `0000160_adapters.safetensors` 这种文件：
  - 这些文件我能下载吗？打开吗？
  - `14599486 bytes` 的文件大小重要吗？
  - "adapters" 和"模型"是什么关系？

---

## F. Probe Compare tab

F1. `Run comparison` 一上来就是 9 张并排小卡，每张 4 个数字：
  - **每张卡的副标题都写 `held-out probe over 8 cases`，但卡内的分子/分母实际上是 4/4、14/20、4/10、20/20、43/48、80/96 等等**——分母完全不是 8。
    - 这是显示错误。小白会以为"每个 run 都被同样的 8 个 case 评了，只是结果不同"，于是把 `1/8` 和 `80/96` 直接做比较得出错误结论。
  - "EXACT / ANY HIT / PARSED / SIGNAL" 四个指标的差异没有解释：
    - "EXACT" vs "ANY HIT" 有什么区别？
    - "SIGNAL" 是什么信号？
  - 同样地，simulated 的 `100-step smoke train` 显示 `EXACT 20/20`，看起来是满分，但我不知道它"模拟"会怎么影响这个分数。

F2. 9 张卡按什么顺序排？小步数到大步数？simulated 和 real 没分离？

F3. 数字越大越好还是越小越好？没有箭头/颜色提示。

F4. `Probe cases` 区在右侧（被遮挡，需要继续滚），列出 case id（`sft-v1-0xxx`）。点进去能看具体的 input / expected / actual 对比吗？没明显的引导。

---

## G. 跨页面共有的小白疑问

G1. **专有名词从不在第一次出现时解释**。仅出现一次的英文术语包括但不限于：
  - SFT、LoRA、MLX、adapter、checkpoint、base model、instruct、chat template、tool calling、tool schema、structured output、route selection、held-out、probe、smoke train、simulated、real run、curriculum、consolidation、replay、preference tuning、DPO、focus metrics、artifacts、avg loss、loss delta、exact name match、parsed json、tool signal、any hit、route hit、executable、arguments、overall pass、loaded_tool_names、vehicle_state、reroute_to_meta、proactive_event_driven、confirm_required_action、reject_unsafe_action、failure bucket、Gemma 4、E2B、E2B-it、E4B、E4B-it、4bit、iter、step、epoch……
  - 同一概念在不同位置文案不一致：`step / iter / max_steps`；`probe / probe results / inference-probe-results`。

G2. **没有"这一节面向谁"的标记**。每个 panel 都用同样的字号字体写，无论是给小白看的（教学曲线）还是给开发者看的（safetensors 文件路径）。

G3. **缺少"我现在该做什么"的下一步指引**。每个 tab 看完都是悬空结尾，没有"下一步去看 Y tab" 或 "回到顶部跑这条命令"。

G4. **页面非常长（Overview 高度 20400px）**。我没有目录、没有锚点跳转、没有折叠。读到一半很容易迷路。

G5. **绿色 = 好 / 粉色 = 警告？还是只是配色？** 从 Hero 的 `99.8%` 是绿色，到 Probe 卡里 `1/8 exact` 也是常规色——颜色没有承担信息含义，但因为 Hero 那张 loss ↓ 卡用了大块绿色高亮，我会下意识把绿色当好评。

G6. **页面默认展示的"运行结果"和"模拟教学结果"混在一起**。我无法区分哪些是真的训出来的、哪些是教学链路里写死的。

G7. **页面没有任何"原理"层的内容**。所有展示都是结果/产物（数据、loss、命中率），没有任何一处解释"微调到底在改模型的什么？"、"为什么 SFT 是教模型挑工具而不是教知识？"、"loss 是怎么算出来的？"。一个完全的小白看完，能学到的是"finetune-lab 长这样"，不是"微调是什么"。

---

## H. 最容易把小白误导的 4 处（Top issues）

H1. **Hero KPI `LOSS ↓ 99.8%` 配大块绿色高亮**——会让小白等同于"模型成绩 99.8 分"。但页面同一份数据里 `gemma4-e2b-real-mlx-lora-medium` 的 loss 也降了 99.3%，probe 却只命中 1/8（过拟合）。

H2. **Probe Compare 每张卡副标题写死"over 8 cases"**——分母实际不是 8。会造成"以为大家在同一份测试集上比"。

H3. **simulated 与 real run 在大多数视图里用同样的视觉权重平起平坐**——只有 Overview 最底部 Training curves 区显式区分。

H4. **左侧 tab 名 `Training Runs` 不展示 loss 曲线**——曲线在 `Overview` 末尾。导航与内容期望不匹配。

---

## I. 这份记录的下一步用法

- 后续若做 web 前端重构，把 G1（专有名词词典 / 悬停解释）和 H1~H4 列入 P0 修改项。
- 把 B5 / D / E 里能"小白点开看示例"的入口（artifact 路径、case id）改造成可展开/可点击。
- 重新分配五个 tab 的内容，特别是把 loss 曲线放回 Training Runs。
- 加一条"我从来没微调过，先看哪儿"的入门通道，把 `docs/ai/beginner-guide.md` 嵌进去。

本次只做记录，不动代码。

---

## J. 2026-04-26 已修复（P0）

只动了 H1~H4 + 与之联动的数据保真度问题（与 [2026-04-26-web-data-fidelity-review.md](2026-04-26-web-data-fidelity-review.md) F1 重叠）。P1（术语解释/glossary）和 P2（信息架构/入门通道）留给后续 spec。

| 编号 | 修复内容 | 文件 |
| --- | --- | --- |
| H1 | Hero KPI `LOSS ↓` 改名 `train loss ↓`，去掉 `accent` 绿色高亮，hint 增加 `probe exact X/Y`+ "loss 是训练目标，不等于模型质量"提示。headline 选择 run 时过滤 `is_top_level && !simulated`，避免 curriculum 子 stage 抢占。 | [web/src/App.tsx:85-127](../../web/src/App.tsx) |
| H2 | Probe Compare 卡片副标题 `over 8 cases` 改为按每张卡的 `metrics.total` 真实分母显示；section 副标题说明不同 run 的 probe 集合不同；case 列表用所有 run 的 union，而不是只取 `runs[0]`。 | [web/src/App.tsx:1167-1199](../../web/src/App.tsx) |
| H3 | 新增 `RunModeBadge`（REAL / SIM 两色），同步加到 Run registry / Run metrics / Probe Compare / Training curves；Training curves 颜色改为按 `training_mode` 而非按 idx 分（SIM=粉，REAL=绿）。 | [web/src/App.tsx:32-40](../../web/src/App.tsx)、[web/src/styles.css:617-664](../../web/src/styles.css) |
| H4 | "Training curves" section 从 Overview 末尾搬到 Training Runs tab；副标题改写为说明 SIM/REAL 含义，不再用"教学用 simulated smoke train，不是假装真实大规模训练"这种容易引起误解的句式。 | [web/src/App.tsx:1099-1135](../../web/src/App.tsx) |
| F1（联动）| `build-lab-data.mjs` 改递归扫描 `outputs/**/run-manifest.json`，从 9 个 run 涨到 28 个；为 nested run 把 `manifest.run_id` 改写为 `{family}/{run_id}` 防 React key 冲突；新增 `manifest.family / is_top_level` 字段。`buildRunDelta` 只用 top-level real run 计算，避免被 stage run 污染。 | [web/scripts/build-lab-data.mjs:84-156](../../web/scripts/build-lab-data.mjs)、[web/src/types.ts:67-83](../../web/src/types.ts) |
| 顺手 | Run registry 用 `<details>` 按 family 分组（28 个 run 不再是平铺），每组里仍可单选；BehaviorEvalPanel 用 `${run_id}-${max_steps}` 作 key，消除 3 个 stage4-consolidation 同 key 的 React 警告。 | [web/src/App.tsx:1057-1095](../../web/src/App.tsx) |

### 验证

- `make web-build` 通过，0 错误。
- preview 环境逐 tab 检查：Hero KPI 文案与配色符合预期；Probe Compare 11 张卡显示 8/20/8/0/0/0/10/4/8 等实分母；Training Runs tab 同时显示 28 张 curve（粉/绿区分）；Overview 末尾不再有 Training curves。
- Console 在我修复之后导航全部 5 个 tab 触发 0 个 React key 错误。

### 还没做（继续留给后续）

- B3 / G4：LIVE/PARTIAL/READY 颜色含义说明仍未独立解释（roadmap 卡仍依赖颜色 + 字面 status，没标注图例）。
- F4：Probe cases 点开看 input/expected/actual 对比的入口。
- README / docs/ai/beginner-guide.md 嵌入 web：当前只在 StarterGuide 给入口，没把 markdown 渲染进 UI。

---

## K. 2026-04-26 已修复（P1 + P2）

继 J 之后第二批，把 P1（术语解释）和 P2（信息架构）也补齐。

### P1 — 术语词典 + 第一次出现挂解释

| 编号 | 修复内容 | 文件 |
| --- | --- | --- |
| G1（词典）| 新建 `web/src/glossary.ts`，~36 条中文释义覆盖 SFT / LoRA / MLX / Gemma 4 / E2B / E4B / -it / 4bit / adapter / checkpoint / base model / held-out / probe / smoke train / simulated / real run / curriculum / consolidation / replay / exact name match / any hit / parsed json / tool signal / route hit / loss delta / iter / step / epoch / structured output / tool calling / preference tuning / DPO / focus metrics / failure bucket / artifacts。`lookupTerm()` 做了大小写与空格归一化。 | [web/src/glossary.ts](../../web/src/glossary.ts) |
| G1（机制）| 新增 `<Term term="...">{children}</Term>` 组件：渲染成虚下划线 + 浏览器原生 `title` 提示，hover 显示中文解释。词典查不到时退化为纯文本，不会破坏渲染。 | [web/src/App.tsx:11-19](../../web/src/App.tsx) |
| G1（应用）| Hero KPI 下加了 `hero-glossary` 速查行（12 个高频术语一字排开，hover 即看含义）；Probe Compare 四个指标 dt（exact / any hit / parsed / signal）、Run metrics dl、Level 1 baseline 卡的 route hit、各 panel 副标题里的 probe / held-out / curriculum / consolidation / SIM / REAL / LoRA 都包了一层 `<Term>`。第一次出现处覆盖率 ≈ 90%。 | [web/src/App.tsx:142-220, 1183-1295](../../web/src/App.tsx) |

### P2 — 信息架构

| 编号 | 修复内容 | 文件 |
| --- | --- | --- |
| A4 | 新增 `<StarterGuide>` panel，固定在 Overview 顶部（manifesto 之前）。三张可点击卡：(1) "完全没微调过 → 先看 Agent Handoff"；(2) "想看真训练能跑出什么 → 跳到 Training Runs"；(3) "想知道哪个 run 最好 → 跳到 Probe Compare"。点卡片直接切 tab。 | [web/src/App.tsx:32-65](../../web/src/App.tsx) |
| G2 | `SectionTitle` 加 `audience` 字段，渲染为右上角小 chip：`新手` / `工程` / `进阶`。三档配色（绿 / 蓝 / 粉）。所有 Overview / Agent Handoff / Data Pipeline / Training Runs / Probe Compare 的 panel 都打了 chip，让用户能看到"这一节面向谁"。 | [web/src/App.tsx:21-37](../../web/src/App.tsx) |
| G4 | 新增 `<CollapsiblePanel>`，把 Overview 的 6 个重型 panel（LearningRoadmap / Level1 / Level5 / BehaviorEval / DataScaleCompare / Level6）改成 `<details>`。Level6 默认折叠（最重最进阶）；其余默认展开。全部折叠后 Overview 高度从 16364px 缩到 4890px（-11474px / -70%）。 | [web/src/App.tsx:67-83](../../web/src/App.tsx) |
| 跨页 | Run comparison 把 `metrics.total === 0` 的 8 个 run 折进 `<details>`：`8 个 run 没有 probe 结果（curriculum 子 stage 通常只在最末汇总评估），点击展开`。主 grid 从 28 张卡 → 20 张实际有数据的卡。 | [web/src/App.tsx:1296-1326](../../web/src/App.tsx) |
| C3 | Readiness panel 副标题补一句"这反映的是仓库本地状态，不是访客本地状态"，回应 review C3 的"8/8 是谁的进度"问题。 | [web/src/App.tsx:1024](../../web/src/App.tsx) |
| D3 | Domain footprint 副标题补一句"一条样本可能涉及多个 domain，所以加起来可能超过样本总数"，回应 review D3 的"加起来 145 但 SAMPLES 是 100"质疑。 | [web/src/App.tsx:1117](../../web/src/App.tsx) |
| C2 | Agent handoff timeline 副标题里 `sense / prepare / teach / compare` 加了中文括注。 | [web/src/App.tsx:1007](../../web/src/App.tsx) |

### 验证

- `make web-build` 通过（一次因 glossary.ts 中"…"全角引号被 IME 替换成 ASCII 半角导致 TS1005，已改用 `「」`）。
- preview 实测：Overview 共 24 个 `<Term>` 实例 hover 显示中文释义；6 个 collapsible panels（5 默认 open，Level6 默认 closed）；3 张 starter card 渲染并能点击切 tab；10 个 audience chip 出现在面板标题；Probe Compare 折叠 8 个空 run，主 grid 显示 20 张。
- Console 在所有 5 个 tab 之间切换共 0 个 React 错误。

### 还没做（继续留给后续）

（暂无。）

---

## L. 2026-04-26 已修复（B3 + B6 收尾）

| 编号 | 修复内容 | 文件 |
| --- | --- | --- |
| B3 | LearningRoadmap 卡上方加状态图例 strip：`live` = 这一关已经做完，仓库里有完整产物可看；`partial` = 部分到位（占位 / rubric / 半成品），等待真正的大模型确认实验；`next` = 下一关重点；`planned` = 已写入 roadmap，没动手。每个 label 旁边带真实徽章作色块对照。 | [web/src/App.tsx:255-261](../../web/src/App.tsx)、[web/src/styles.css:271-286](../../web/src/styles.css) |
| B6 | `ReferenceProject` 类型加 `relation?: string` 字段；`project-context.json` 给 4 个项目都补了"和 finetune-lab 什么关系"的一句话（互补 / 工具链上游 / 心法相似 / 路线图借鉴）；卡片底部用虚线分割单独渲染。 | [project-context.json:269-296](../../project-context.json)、[web/src/data-layer.ts:200-206](../../web/src/data-layer.ts)、[web/src/App.tsx:370-378](../../web/src/App.tsx)、[web/src/styles.css:296-302](../../web/src/styles.css) |

---

## M. 2026-04-26 已修复（F4 probe diff 视图，按 spec 实现）

按 [docs/specs/2026-04-26-probe-diff-view-spec.md](../specs/2026-04-26-probe-diff-view-spec.md) 实施，详见 [docs/changes/2026-04-26-probe-diff-view-impl-notes.md](../changes/2026-04-26-probe-diff-view-impl-notes.md)。

简述：

- Probe Compare tab 下半部分从原"raw output 与命中情况"换成 Input / Expected / Per-run actuals 三段对比视图。
- 加了 4 个 saved view（all / highest-divergence / split / all-fail），数量徽章直接挂在按钮上。
- predicted_names vs expected_names 用 match（lime）/ +extra（magenta）/ −missing（删除线灰）三色集合 diff 展示，不引入 diff 库。
- 默认选中分歧最大的 case，让首次访客就能看到不同 run 在同一题上判得不一样的现象。
- per-run 行展示 5 个状态 pill + contract pill（unsafe / confirm / reject）+ predicted_behavior + raw_output 折叠。

验证：preview 实测 case `sft-v1-0029` 默认选中（highest-divergence top 1），4 个 run 在同一条 case 上一眼能看出分歧 —— `lora-small-direct` 显示红色 strikethrough `−hvac_set_temperature` 漏调用，而 `lora-stage-curriculum-consolidation/stage4` 在同一条 case 上完全命中。F4 关心的"input/expected/actual 三段对比"诉求收尾。

---

## N. 2026-04-26 已修复（beginner-guide.md 嵌入 UI，按 spec 实现）

按 [docs/specs/2026-04-26-beginner-guide-embed-spec.md](../specs/2026-04-26-beginner-guide-embed-spec.md) 实施，详见 [docs/changes/2026-04-26-beginner-guide-embed-impl-notes.md](../changes/2026-04-26-beginner-guide-embed-impl-notes.md)。

简述：

- nav 顶部新增 `Beginner Guide` tab（在 Overview 之上，视觉上的第一站）。
- StarterGuide 第一张卡的跳转目标从 Agent Handoff 改为 Beginner Guide；Agent Handoff 仍是独立 tab，给"想让 agent 接手"的用户。
- `build-lab-data.mjs` 实时读 `docs/ai/beginner-guide.md` 字符串挂到 `lab-data.beginner_guide_markdown`；走现有 `lab-data.generated.ts` 嵌入路径，standalone HTML 离线仍能看。
- 用 `react-markdown` + `remark-gfm` 渲染 GFM markdown，新增 `.markdown-body` 暗主题样式（h1-h4 字号阶梯、inline code lime 浅色、pre 暗底块、blockquote lime 左条、table 边框 + 表头底色）。
- bundle 体积 +53KB gzip（spec 估 25KB，实际 react-markdown 6.x 较重），仍在教学站可接受范围。

验证：preview 实测 1 个 h1、7 个 h2、4 个 table、5 个代码块、2 个 blockquote、63 个 inline code 全部按主题样式渲染；6 个 tab 切换 0 个 React 错误。这条 review 至此 A-N 段全部收口。
