# GitHub Repo Launch Checklist

> Goal: make the GitHub repository itself convert first-time visitors into stars, demo clicks, issues, and recipe requests.

This checklist covers GitHub settings that cannot be fully changed from the repo files alone. Use it right before a public launch post or release.

## About Box

### Description

```text
Learn SFT and LoRA by watching behavior change: data -> train -> held-out probe -> case diff.
```

Alternative Chinese-first version:

```text
微调第一次看懂：SFT 数据 -> LoRA 训练 -> held-out probe -> case diff。
```

### Website

```text
https://xianfeng92.github.io/finetune-lab/
```

### Topics

Use focused discovery topics. Keep them aligned with the project promise, not every internal detail.

```text
fine-tuning
lora
sft
mlx
gemma
tool-calling
structured-output
llm-evaluation
ai-native
local-first
```

Optional Chinese discovery topic if useful:

```text
chinese-ai
```

## Social Preview

Recommended image:

```text
docs/assets/launch/overview-start-here.png
```

Fallback:

```text
docs/assets/preview-overview.png
```

Alt text:

```text
finetune-lab overview showing Start Here, Loss Trap, Recipe Gallery, and the data-to-probe learning loop.
```

## Pinned README Promise

The first screen should keep these four promises visible:

- `loss 降了，不代表模型学会`
- `make ai-onboarding && make ai-setup && make ai-lab`
- Live demo before local setup
- GitHub-native feedback path through issue templates

Current local anchors:

- README Quick start
- README 反馈与贡献
- `CONTRIBUTING.md`
- `.github/ISSUE_TEMPLATE/learning_question.yml`
- `.github/ISSUE_TEMPLATE/recipe_request.yml`

## First Release Draft

Release title:

```text
v0.1.0 - Fine-tuning by behavior diff
```

Release notes:

```markdown
`finetune-lab` is an AI-native learning lab for understanding fine-tuning by behavior, not only loss curves.

The first public release focuses on one loop:

data -> LoRA train -> held-out probe -> case diff -> Web lab

Highlights:

- Beginner-friendly Web lab with Data Pipeline, Training Runs, Observatory, and Probe Compare views.
- Makefile onboarding: `make ai-onboarding`, `make ai-setup`, `make ai-lab`.
- SIM vs REAL run labeling so simulated smoke runs are not confused with real LoRA updates.
- Apple Silicon MLX LoRA path for small real fine-tuning experiments.
- Tool-calling / structured-output probes with exact name, argument, JSON, and behavior checks.
- Edge benchmark docs that keep runtime claims narrow: MLX adapter evidence is not the same as same-LoRA parity in every deployment runtime.

Start here:

```bash
make ai-onboarding
make ai-setup
make ai-lab
```

Live demo:
https://xianfeng92.github.io/finetune-lab/

Repo feedback:
- Ask a learning question if any part still feels like a black box.
- Request a recipe if there is a fine-tuning question you want to reproduce.
- Open a PR with commands and artifact paths if you improve the loop.
```

## Good First Issue Seeds

Create these as real GitHub issues after the templates are merged. Full ready-to-paste issue bodies live in [`docs/launch/good-first-issues.md`](good-first-issues.md).

1. `Recipe: loss-is-lying`
   - Build a recipe page that pairs one loss curve with held-out probe evidence.
   - Evidence: `outputs/**/train-metrics.jsonl`, `outputs/**/inference-probe-report.md`.

2. `Recipe: first-lora`
   - Explain the first real MLX LoRA run from dataset to adapter to probe.
   - Evidence: `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`.

3. `Docs: explain exact_name_match vs arguments_match`
   - Add a beginner explanation and link it from Probe Compare.
   - Evidence: one case where tool name is right but arguments are wrong.

4. `Web: add copy link for selected probe case`
   - Make individual case diffs easier to share in launch posts and issue comments.

5. `Docs: runtime reality check mini-guide`
   - Explain why MLX, llama.cpp, and LiteRT-LM claims must be scoped separately.
   - Guardrail: do not imply same-LoRA LiteRT-LM parity before matching artifacts exist.

## Launch Day Checks

- GitHub About description is set.
- Website points to the live demo.
- Topics are set.
- Social preview uses a launch image.
- Pages workflow is green.
- README image renders on GitHub.
- Latest release exists and links to the live demo.
- Issue templates show bug, recipe, and learning question paths.
- At least 3 good first issues are open.
- X / 中文 launch posts link to the repo first, demo second.

## Do Not Overclaim

- Do not call `finetune-lab` a universal fine-tuning framework.
- Do not describe SIM runs as real LoRA training.
- Do not claim same-LoRA LiteRT-LM runtime parity until the target runtime has matching verified artifacts.
- Do not turn edge-bench into a leaderboard; it is evidence for runtime-specific behavior boundaries.
