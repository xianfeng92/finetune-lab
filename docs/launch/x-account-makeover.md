# X Account Makeover Kit

> Goal: turn a personal X account into a small but credible builder account for `finetune-lab`, without overclaiming project maturity.

## Profile Positioning

The account should signal three things in the first screen:

1. The person is building an AI-native open-source learning lab.
2. The project has a sharp teaching idea: behavior diff beats loss watching.
3. Visitors have one obvious next action: open the repo or live demo.

## Recommended Profile Fields

### Name

```text
Monday | finetune-lab
```

Why: keeps the existing personal name, but immediately tells visitors what the account is building.

Alternative if the account will become broader than one project:

```text
Monday | AI-native labs
```

### Bio

Primary version:

```text
Building finetune-lab: learn SFT/LoRA by behavior diffs, not loss curves. 中文 AI builder.
```

More global version:

```text
Building AI-native open-source labs. finetune-lab helps beginners learn SFT/LoRA by behavior diffs, not loss curves.
```

More Chinese-first version:

```text
做 AI-native 开源实验课。finetune-lab: 让 AI 小白通过 behavior diff 看懂 SFT/LoRA，而不是只盯 loss。
```

### Location

```text
AI-native labs
```

Why: avoids exposing a real location while still using the field as positioning.

### Website

Use the repo during launch:

```text
https://github.com/xianfeng92/finetune-lab
```

Use the demo during teaching-heavy follow-up waves:

```text
https://xianfeng92.github.io/finetune-lab/
```

## Header And Avatar

Keep the current avatar for the first launch if personal continuity matters. The header should carry the project.

Header candidate:

```text
docs/assets/launch/overview-start-here.png
```

If X crops it poorly, create a dedicated `1500 x 500` banner later with:

```text
finetune-lab
Learn fine-tuning by behavior diffs, not loss curves.
data -> LoRA -> probe -> case diff
```

## Locked Account Policy

Do not use a protected account for launch distribution.

Before making the account public:

1. Review whether old posts are acceptable to expose publicly.
2. Confirm the profile fields are launch-ready.
3. Confirm the first pinned post is ready.
4. Then switch the account public.

Agents should not unlock the account, upload images, or save public profile changes without explicit user confirmation.

## Pinned Post Draft

```text
I’m building finetune-lab: an open-source lab that helps beginners understand fine-tuning by watching model behavior change.

Not just:
loss goes down

But:
data -> LoRA train -> held-out probe -> case diff

Repo: https://github.com/xianfeng92/finetune-lab
Demo: https://xianfeng92.github.io/finetune-lab/
```

## Three Warm-up Posts

### Day 1: Loss Trap

Pair with:

```text
docs/assets/launch/loss-trap.png
```

Post:

```text
The first fine-tuning lesson I want beginners to see:

loss going down does not mean the model learned the behavior you care about.

You need held-out probes, case-level diffs, and runtime-specific checks to see whether behavior actually changed where you plan to deploy it.
```

### Day 2: Agent-native Repo

```text
I think future AI open-source repos should be agent-native by default.

For finetune-lab, that means:

- AGENTS.md
- project-context.json
- make ai-onboarding
- fixed artifact paths
- readiness reports

The repo should explain itself to Codex / Claude.
```

### Day 3: The Learning Loop

Pair with:

```text
docs/assets/launch/overview-start-here.png
```

Post:

```text
finetune-lab’s beginner loop:

make ai-onboarding
make ai-setup
make ai-lab

Then inspect:

data -> train -> probe -> compare -> frontend

The point is not just to run fine-tuning.
The point is to understand what changed.
```

## Launch Day Account Checklist

- Account is public.
- Name contains `finetune-lab` or `AI-native labs`.
- Bio includes `SFT/LoRA`, `behavior diffs`, and `not loss curves`.
- Website points to the GitHub repo.
- Header visually shows the project or core learning loop.
- First launch post attaches `docs/assets/launch/overview-start-here.png`.
- Second or third post attaches `docs/assets/launch/loss-trap.png`.
- Replies are monitored for the first two hours.
