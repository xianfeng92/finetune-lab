# X Launch Thread Draft

## 目标

X 不是中文首发主阵地，但要同步发布一条英文/双语 thread，把 `finetune-lab` 带进全球 open-source AI、Local LLM、fine-tuning、agent-native 开发者视野。

核心钩子：

> Fine-tuning is not about watching loss go down. It is about checking whether model behavior actually changed, in the runtime you plan to use.

配图建议：

1. README / Web hero：`docs/assets/launch/overview-start-here.png`
2. Loss Trap：`docs/assets/launch/loss-trap.png`
3. Recipe Gallery：`docs/assets/launch/recipe-gallery.png`
4. Mobile crop：`docs/assets/launch/mobile-start-here.png`

发图顺序建议：

- 1/13 带 `overview-start-here.png`
- 3/13 带 `loss-trap.png`
- 10/13 带 `recipe-gallery.png`
- 中文补充短帖带 `mobile-start-here.png`

发布时间建议：

- 中文首发当天同步发
- 如果主账号中文粉丝多，首条可以中英双语；如果想打全球圈，首条英文，thread 内补一条中文说明
- 发完 2 小时内主动回复每个高质量评论
- 第 2 天单独发一条 `loss trap` follow-up

## Thread v2

### 1/13

I’m building `finetune-lab`.

Not another fine-tuning framework.

A visual lab for beginners to understand fine-tuning by checking behavior, not just training curves:

```text
data -> LoRA train -> held-out probe -> case diff
```

Core idea:

loss going down does not mean the model learned the behavior you care about.

### 2/13

Most fine-tuning tutorials show one of two things:

- concepts: “what is LoRA / SFT?”
- scripts: “run this command”

But the real beginner question is:

> After training, what exactly changed in the model’s behavior?

That is what this project tries to make visible.

### 3/13

The first lesson in `finetune-lab`:

```text
loss != learned
```

A run can have a beautiful training loss curve and still fail held-out cases.

So the lab always pairs training metrics with probe results and case-level diffs.

### 4/13

The default learning loop:

```bash
make ai-onboarding
make ai-setup
make ai-lab
```

This runs the smallest teaching path:

```text
onboarding -> data -> train -> probe -> compare -> frontend
```

The point is not just to run fine-tuning.
The point is to understand it.

### 5/13

What the web lab shows:

- SFT sample anatomy
- train / held-out split
- simulated vs real LoRA runs
- training curves
- probe accuracy
- tool-calling JSON validity
- input / expected / actual diffs

Beginners should be able to see the whole chain in one place.

### 6/13

The project focuses on a concrete teaching task:

tool calling / structured outputs.

Instead of asking “can the model write nicer text?”, we ask:

- did it choose the right tool?
- did it fill the right arguments?
- did it produce valid structured output?

### 7/13

Why tool calling?

Because it makes fine-tuning behavior measurable.

Natural language quality is fuzzy.

But tool routing gives us concrete checks:

```text
exact tool name match
arguments match
parsed JSON
behavior match
unsafe direct call rate
```

### 8/13

One extra lesson from the edge benchmark:

passing in the training runtime is not the same as passing in the deployment runtime.

In this repo, an MLX LoRA kept PolicyGateway semantics, but fused GGUF via llama.cpp regressed on confirm/refusal contracts.

So runtime eval is part of the lesson.

### 9/13

The repo is also agent-native.

It ships with `AGENTS.md`, project context, and Makefile targets so Codex / Claude can inspect readiness, run the teaching loop, and explain artifacts.

The intended workflow:

> clone it, hand it to an agent, watch the lab explain itself.

### 10/13

The first recipes I’m shaping:

- `loss-is-lying`
- `first-lora`
- `tool-calling`
- `curriculum-vs-direct`

Each recipe should have:

- one question
- one command path
- artifacts
- screenshots
- a short explanation

### 11/13

This is not trying to replace LLaMA-Factory or Unsloth.

Those are great fine-tuning systems.

`finetune-lab` is the learning companion:

> use it to understand what SFT / LoRA / probe / tool-calling fine-tuning actually mean in practice.

### 12/13

If you are learning fine-tuning, I want this repo to answer four questions:

1. What does an SFT sample actually teach?
2. What does LoRA training output?
3. Why is loss not enough?
4. How do I inspect whether behavior changed?

### 13/13

Repo:

`https://github.com/xianfeng92/finetune-lab`

Live demo:

`https://xianfeng92.github.io/finetune-lab/`

If you try it, I’d love feedback on one thing:

Where did fine-tuning become clearer, and where did it still feel like magic?

## 中文补充短帖

如果主账号中文读者较多，可以在 thread 后补一条：

```text
中文一句话：我想把 finetune-lab 做成“微调第一次看懂”的开源实验课。

不是教你只看 loss 曲线，而是把 SFT 数据、LoRA 训练、held-out probe、case diff 串起来，让你看到模型行为到底有没有改变。
```

## Follow-up Posts

### Follow-up 1: Loss Trap

```text
The most important beginner lesson in fine-tuning:

A beautiful loss curve can lie.

You need held-out probes and case-level diffs to know whether the model actually learned the behavior you wanted.

This is why finetune-lab treats probe results as first-class artifacts.
```

### Follow-up 2: Agent-native Repo

```text
I think future open-source AI repos should be agent-native by default.

For finetune-lab, that means:

- AGENTS.md
- project-context.json
- make ai-onboarding
- make ai-lab
- fixed artifact paths
- agent-readable readiness reports

The repo should explain itself to Codex / Claude.
```

### Follow-up 3: Tool Calling

```text
Tool calling is a great fine-tuning teaching task because the behavior is measurable.

Instead of asking “is the answer better?”, we can ask:

- right tool?
- right args?
- valid JSON?
- safe action?

That makes SFT much easier to understand.
```
