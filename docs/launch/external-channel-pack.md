# External Channel Launch Pack

> Goal: turn the X launch into a broader developer feedback loop without sounding like a product ad.

Use this pack after the GitHub repo, live demo, issue templates, and X thread are live.

## Canonical Links

- Repo: `https://github.com/xianfeng92/finetune-lab`
- Live demo: `https://xianfeng92.github.io/finetune-lab/`
- X thread: `https://x.com/Xforg3/status/2052039842633240833`

## Positioning Rule

Lead with the learning problem, not the repo.

Good:

```text
I built a visual lab to understand why fine-tuning loss can lie.
```

Avoid:

```text
Please star my new fine-tuning framework.
```

`finetune-lab` is not positioned as a replacement for LLaMA-Factory, Unsloth, Axolotl, or a production trainer. It is a learning companion that makes `data -> LoRA train -> held-out probe -> case diff` inspectable.

## Posting Order

1. Hacker News `Show HN`
2. Reddit low-risk targets
3. Discord / community short post
4. GitHub Discussion / issue feedback bump
5. Chinese developer channels from `docs/launch/chinese-launch-pack.md`

Do not cross-post all channels in the same 10 minutes. Leave at least a few hours between major communities so replies can be handled thoughtfully.

## Hacker News

### Title Option A

```text
Show HN: finetune-lab - a visual lab for understanding fine-tuning behavior
```

### Title Option B

```text
Show HN: I built a lab to show why fine-tuning loss can lie
```

Recommended: **Option B**. It is more specific and asks a technical question immediately.

### URL

```text
https://github.com/xianfeng92/finetune-lab
```

Use the repo URL as the submitted URL. Add the live demo in the first comment.

### First Comment

```text
Hi HN, I built finetune-lab because I kept seeing beginner fine-tuning material stop at either concepts or scripts.

The part I wanted to make visible is the behavior check after training:

data -> LoRA train -> held-out probe -> case diff

The core teaching point is that training loss going down does not prove the model learned the behavior you care about. The lab pairs training curves with held-out probe results and case-level expected/actual diffs.

It currently focuses on tool calling / structured outputs because behavior is easier to measure there:

- exact tool name match
- argument match
- parsed JSON
- behavior match
- runtime-specific regressions

There is also an agent-native path:

make ai-onboarding
make ai-setup
make ai-lab

Codex / Claude can inspect readiness, run the teaching loop, and explain artifacts.

Live demo:
https://xianfeng92.github.io/finetune-lab/

I would love technical feedback on two things:

1. Does the lab make the fine-tuning loop clearer than a normal README/tutorial?
2. What would you want the first serious recipe to cover: loss traps, first LoRA, tool-calling, or runtime mismatch?
```

## Reddit

### Channel Risk

- `r/MachineLearning`: high signal but strict. Prefer the current self-promotion thread if available.
- `r/LocalLLaMA`: strong fit for local LLM / MLX / LoRA, but self-promotion is sensitive. Post only if the account has normal participation and the title is feedback-first.
- `r/learnmachinelearning`: good fit for the beginner-learning angle. Keep it educational.
- `r/SideProject`: lower technical depth, but accepts builder posts more naturally.
- `r/opensource`: possible fit if the post asks for contributors and feedback, not stars.

Recommended first Reddit move:

1. `r/learnmachinelearning`
2. `r/SideProject`
3. `r/MachineLearning` self-promotion thread
4. Only then consider `r/LocalLLaMA`

### Reddit Title Option A

```text
I built a visual lab to understand why fine-tuning loss can lie
```

### Reddit Title Option B

```text
Learning LoRA/SFT: I made a small lab that pairs loss curves with held-out probes
```

Recommended: **Option A** for `r/learnmachinelearning`; **Option B** for more technical communities.

### Reddit Body

````markdown
I built an open-source project called `finetune-lab`.

The motivation is a beginner problem I kept running into:

> after fine-tuning, how do I know what behavior actually changed?

Most tutorials either explain concepts or give a training command. I wanted a small lab that connects the whole loop:

```text
data -> LoRA train -> held-out probe -> case diff -> web lab
```

The main lesson is:

```text
loss down != behavior learned
```

So the lab does not stop at a loss curve. It shows:

- SFT sample anatomy
- train / held-out split
- simulated vs real MLX LoRA runs
- training curves
- probe metrics
- tool-calling JSON validity
- input / expected / actual case diffs

The first task focus is tool calling / structured outputs because it makes behavior easier to measure:

- did the model choose the right tool?
- did it fill the right arguments?
- did it produce valid JSON?
- did it keep the expected behavior in the target runtime?

Quick start:

```bash
make ai-onboarding
make ai-setup
make ai-lab
```

Repo:
https://github.com/xianfeng92/finetune-lab

Live demo:
https://xianfeng92.github.io/finetune-lab/

I am looking for feedback from people learning or teaching fine-tuning:

- which part of SFT / LoRA / probe became clearer?
- which part still feels like magic?
- what recipe would be most useful next?
````

### Reddit Self-Promotion Thread Version

````markdown
I open-sourced `finetune-lab`, a visual learning lab for understanding fine-tuning by behavior rather than only loss curves.

It connects:

`data -> LoRA train -> held-out probe -> case diff -> web lab`

The first teaching focus is tool calling / structured outputs, so the lab can measure exact tool name match, argument match, parsed JSON, and behavior match.

Repo: https://github.com/xianfeng92/finetune-lab
Demo: https://xianfeng92.github.io/finetune-lab/

Looking for technical feedback on whether the probe/case-diff view makes fine-tuning easier to understand for beginners.
````

## Discord / Community Short Post

Use this in small ML, local LLM, or open-source builder communities.

```text
I just published `finetune-lab`, an open-source visual lab for learning SFT / LoRA by checking behavior, not just loss curves.

The loop is:

data -> LoRA train -> held-out probe -> case diff

It focuses first on tool calling / structured outputs because the behavior is measurable: tool name, args, valid JSON, and case-level diffs.

Repo: https://github.com/xianfeng92/finetune-lab
Demo: https://xianfeng92.github.io/finetune-lab/

I am looking for early feedback: where does fine-tuning become clearer, and where does it still feel like magic?
```

## GitHub Discussion Draft

Title:

```text
What should the first deeper recipe explain?
```

Body:

```markdown
The first public launch wave is live. I want `finetune-lab` to stay focused on one promise:

> make fine-tuning understandable by behavior, not just loss curves.

The first recipe candidates are:

- `loss-is-lying`: a run with a good-looking loss curve but weak held-out probe behavior
- `first-lora`: what a first real MLX LoRA run produces, from dataset to adapter to probe
- `tool-calling`: how SFT samples teach tool routing and structured JSON
- `runtime-reality-check`: why passing in the training runtime is not the same as passing in deployment

If you try the demo or run the repo locally, please reply with:

1. Which recipe would help you most?
2. Which screen or artifact was confusing?
3. What would make the first 10 minutes smoother?

Repo:
https://github.com/xianfeng92/finetune-lab

Demo:
https://xianfeng92.github.io/finetune-lab/
```

If GitHub Discussions are not enabled, post this as an issue with label `feedback`.

## Reply Templates

### If Someone Says "Isn't This Just Another Fine-Tuning Framework?"

```text
That is exactly what I am trying not to build. The goal is not to compete with LLaMA-Factory, Unsloth, or Axolotl.

`finetune-lab` is the learning layer around the loop: data, LoRA run artifacts, held-out probe, and case-level diffs. It tries to make "what changed after training?" visible.
```

### If Someone Asks Why Tool Calling

```text
Tool calling gives the lab concrete behavior checks. Open-ended text quality is fuzzy, but tool routing lets us inspect exact tool name, arguments, parsed JSON, and behavior match.

That makes it a useful first teaching task for SFT / LoRA.
```

### If Someone Challenges The Loss Claim

```text
I agree loss is useful. The claim is narrower: loss is an optimizer/training signal, not a complete behavior score.

The lab keeps the loss curve, but always pairs it with held-out probe cases and expected/actual diffs so a beginner can see when the behavior did or did not change.
```

### If Someone Asks About Real Training

```text
The repo has both SIM and REAL paths. SIM is only for the fast teaching loop. REAL uses MLX LoRA on Apple Silicon and labels artifacts separately so simulated smoke runs are not confused with real optimizer updates.
```

### If Someone Finds A Confusing Part

```text
That is useful feedback. If you can, please open a Learning question issue with the screen, command, or artifact path that confused you. The project is intentionally organized around turning those questions into recipes.
```

## Metrics To Track

Record these after each post:

- channel
- post URL
- title
- time posted
- first 2-hour comments
- first 24-hour comments
- repo stars before / after
- demo clicks if available
- issues opened
- recurring confusion themes

Suggested local note path:

```text
docs/launch/channel-post-log.md
```

## Operator Checklist

- Confirm the account is logged in.
- Check each community's current rules before posting.
- Prefer a text post asking for feedback over a bare link drop.
- Reply to every sincere technical comment within the first 2 hours.
- Do not ask directly for stars on Reddit or HN.
- Do not post the exact same body to multiple Reddit communities.
- If a moderator removes a post, do not repost; adapt and use the self-promotion thread or a different community.
