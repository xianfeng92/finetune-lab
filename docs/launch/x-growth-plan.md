# X Growth Plan for finetune-lab

> Goal: grow a credible builder audience for `finetune-lab`, then convert the right attention into GitHub stars, demo visits, learning questions, and recipe requests.

This is not a vanity-follower plan. The account should become a trustworthy technical distribution surface for AI-native learning labs.

## Current Strategy

`finetune-lab` should be the account's first clear theme:

```text
fine-tuning by behavior diff, not loss watching
```

The account should repeatedly teach one mental model:

```text
data -> LoRA train -> held-out probe -> case diff
```

Every post should fit one of four roles:

- **Teach**: explain SFT / LoRA / probe / runtime eval in small pieces.
- **Build**: show what changed in the repo today.
- **Invite**: ask for feedback, recipes, or confusing screens.
- **Reply**: add useful context under adjacent AI / local LLM / open-source posts.

## Non-Negotiable Guardrails

- Do not ask directly for stars in normal posts.
- Do not use the account for bulk follows, generic replies, or engagement bait.
- Do not post the repo link in every reply.
- Do not overclaim `finetune-lab` as a production training framework.
- Keep SIM vs REAL and runtime-specific benchmark claims scoped.
- Do not unlock a protected account or change public profile settings without explicit user confirmation.

## Public Account Prerequisite

If the account is still protected, growth will be severely limited.

Before making it public:

1. Review recent posts for anything that should stay private.
2. Set the profile using `docs/launch/x-account-makeover.md`.
3. Pin the X launch thread:
   `https://x.com/Xforg3/status/2052039842633240833`
4. Confirm the website field points to the repo or demo.
5. Only then switch the account public.

## 7-Day Plan

Target cadence:

- 1 original post per day
- 5 to 10 high-quality replies per day
- 1 project link per 2 to 3 original posts, unless someone asks for the repo
- 15-minute comment check after posting
- 60-minute comment check later the same day

### Day 1: Profile + Pinned Thread

Objective: make the first screen explain who the account is for.

Original post:

```text
I’m going to build `finetune-lab` in public for a while.

The thesis is simple:

fine-tuning should be learned by checking behavior, not just watching loss curves.

The loop I care about:

data -> LoRA train -> held-out probe -> case diff

I’ll share build notes, mistakes, screenshots, and recipes here.
```

Reply targets:

- People discussing SFT / LoRA / local LLM training.
- People sharing AI repo launch notes.
- People complaining that fine-tuning tutorials feel like scripts without evaluation.

Good reply shape:

```text
This is exactly the gap I keep noticing too: many tutorials stop at "loss went down", but the beginner still does not know what behavior changed. Held-out probes and case diffs make the learning loop much easier to reason about.
```

### Day 2: Loss Trap

Objective: make the core idea memorable.

Use image:

```text
docs/assets/launch/loss-trap.png
```

Original post:

```text
The first fine-tuning lesson I want beginners to internalize:

loss down != behavior learned

Loss is useful, but it is not a behavior score.

After a LoRA run, I want to see:

- held-out probe cases
- expected vs actual output
- valid JSON
- right tool name
- right arguments
```

Reply prompt:

```text
What was the first moment fine-tuning stopped feeling like magic for you?
```

### Day 3: Agent-Native Repo

Objective: connect `finetune-lab` to Codex / Claude builders.

Original post:

```text
I think AI-native repos should explain themselves to agents.

For `finetune-lab`, that means:

- AGENTS.md
- project-context.json
- make ai-onboarding
- make ai-setup
- make ai-lab
- fixed artifact paths

The repo should let Codex / Claude inspect readiness, run the loop, and explain the outputs.
```

Reply targets:

- Agent framework threads.
- Open-source maintainers discussing docs / onboarding.
- Codex / Claude Code workflows.

Good reply shape:

```text
One small pattern I like: make the repo expose a read-only onboarding command first. The agent should be able to inspect readiness before guessing setup steps.
```

### Day 4: SFT Sample Anatomy

Objective: teach one concrete detail from the data layer.

Original post:

```text
An SFT sample is not just "some text".

For tool calling, the useful signal is closer to:

loaded tools
user request
assistant tool call
expected behavior

If the sample does not encode the behavior clearly, the training loop has nothing reliable to learn.
```

Optional repo link if there has been prior engagement:

```text
I’m turning this into a visual learning path in finetune-lab:
https://github.com/xianfeng92/finetune-lab
```

### Day 5: Runtime Reality Check

Objective: establish technical seriousness and avoid overclaiming.

Original post:

```text
One fine-tuning lesson that feels under-taught:

passing in the training runtime is not the same as passing in deployment.

If your LoRA behavior matters, test it where you plan to serve it.

Training-side success is evidence.
Deployment-side behavior is another check.
```

Reply targets:

- llama.cpp / MLX / LiteRT / quantization threads.
- Posts about "it worked locally but failed in production".

Good reply shape:

```text
I’d separate "model learned the task in the training runtime" from "the deployment stack preserves the behavior". They can fail for different reasons, so I like making runtime eval part of the fine-tuning lesson.
```

### Day 6: Recipe Poll

Objective: create participation and learn what to build next.

Original post:

```text
I’m deciding which `finetune-lab` recipe to deepen first.

Which would help you most?

1. loss-is-lying
2. first-lora
3. tool-calling
4. runtime-reality-check

My instinct is `loss-is-lying`, because it fixes the biggest beginner misconception first.
```

Follow-up reply:

```text
If you vote, I’d love one sentence on what currently feels confusing about that topic.
```

### Day 7: Weekly Build Recap

Objective: convert weekly attention into repo/demo visits.

Use image:

```text
docs/assets/launch/overview-start-here.png
```

Original post:

```text
Week 1 of building `finetune-lab` in public:

- launched the X thread
- published the live demo
- added recipe entry points
- added issue templates for learning questions
- shaped the first outreach pack

Next: turn feedback into better recipes.

Repo:
https://github.com/xianfeng92/finetune-lab

Demo:
https://xianfeng92.github.io/finetune-lab/
```

## Daily Reply Search Queries

Use X search with these phrases:

```text
fine-tuning loss
LoRA training
SFT dataset
held-out eval
tool calling fine-tune
structured outputs
MLX LoRA
local LLM training
agent-native repo
Claude Code repo
Codex AGENTS.md
```

Reply only when there is a real technical angle. Good replies either:

- clarify a concept
- add a small evaluation heuristic
- ask a useful question
- share one narrow lesson without dropping a link

## Weekly Metrics

Track once per day:

- followers
- profile visits
- X thread views
- original post impressions
- meaningful replies received
- meaningful replies sent
- GitHub stars
- GitHub issues / discussions opened
- demo visits if available

Suggested note path:

```text
docs/launch/x-growth-log.md
```

## Conversion Logic

The first week should not optimize for viral reach. It should optimize for a clear account identity:

```text
This is the builder working on fine-tuning education, behavior probes, and agent-native AI repos.
```

Once that identity is legible, project posts become less random. People can understand why `finetune-lab` belongs on the account.

## Operator Boundary

Codex can help with:

- drafting posts and replies
- finding adjacent posts to reply to
- using the browser to publish after explicit confirmation
- logging post URLs and metrics
- turning replies into GitHub issues or recipe ideas

Codex should not:

- change privacy settings without explicit confirmation
- create or submit login-gated accounts
- mass-follow accounts
- post generic replies
- delete old posts unless explicitly instructed
- send DMs without explicit text approval
