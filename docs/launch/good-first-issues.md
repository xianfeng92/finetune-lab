# Good First Issues for Launch

These are ready-to-paste GitHub issue drafts for the first public launch wave. They are designed to convert curious visitors into small, evidence-backed contributions.

Use labels:

```text
good first issue
recipe
documentation
web
```

## Issue 1: Recipe: turn `loss-is-lying` into a richer walkthrough

Labels:

```text
good first issue, recipe, documentation
```

Body:

````markdown
## Goal

Make the `loss-is-lying` recipe more useful for beginners who have never evaluated a fine-tuned model before.

The current recipe explains the core idea:

> loss going down does not prove behavior changed.

This issue is to expand it into a clearer walkthrough with one concrete run, one probe report, and one "what to look at" checklist.

## Files

- `docs/recipes/loss-is-lying.md`
- Optional: `README.md` if the recipe link text needs a small wording tweak

## Evidence to use

- `outputs/gemma4-e2b-real-mlx-lora-demo/train-metrics.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-report.md`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-results.json`

## Acceptance criteria

- The recipe has a short "before you start" section.
- The recipe explains why loss is an optimizer signal, not a behavior score.
- The recipe points to at least one concrete probe metric.
- The recipe keeps SIM vs REAL and runtime-specific claims scoped correctly.
- Markdown code fences are balanced.

## Suggested verification

```bash
ruby -e 'f="docs/recipes/loss-is-lying.md"; open=false; File.readlines(f).each { |line| open = !open if line.start_with?("```") }; abort("unclosed fence") if open; puts "ok"'
```
````

## Issue 2: Recipe: add a visual artifact map to `first-lora`

Labels:

```text
good first issue, recipe, documentation
```

Body:

````markdown
## Goal

Help beginners understand what a first real LoRA run produces.

The current `first-lora` recipe lists dataset, manifest, adapter, metrics, and probe artifacts. This issue is to add a compact artifact map that shows how those files connect.

## Files

- `docs/recipes/first-lora.md`

## Evidence to use

- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/train-metrics.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-report.md`

## Acceptance criteria

- Add an ASCII or Markdown table artifact map.
- Explain the difference between dataset split, run manifest, adapter, metrics, and probe report.
- Do not describe simulated smoke runs as real LoRA training.
- Keep all paths relative to the repo root.

## Suggested verification

```bash
test -f docs/recipes/first-lora.md
test -f outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json
```
````

## Issue 3: Docs: explain `exact_name_match` vs `arguments_match`

Labels:

```text
good first issue, documentation
```

Body:

````markdown
## Goal

Add a beginner explanation for two probe metrics that are easy to confuse:

- `exact_name_match`
- `arguments_match`

The explanation should help a reader understand how a model can pick the right tool but still fill the wrong arguments.

## Files

Suggested options:

- `docs/recipes/tool-calling.md`
- `docs/ai/beginner-guide.md`
- Optional README link if the explanation becomes a stable anchor

## Evidence to use

- `outputs/level5/structured-output-probe-pack.md`
- `outputs/level5/tool-routing-dataset-pack.md`
- Any probe result where the tool name and arguments differ in quality

## Acceptance criteria

- Define both metrics in beginner-friendly language.
- Include one small example of right tool / wrong arguments.
- Keep the explanation tied to tool-calling and structured output, not generic text quality.
- Mention that parsed JSON and argument correctness are separate checks.

## Suggested verification

```bash
test -f outputs/level5/structured-output-probe-pack.md
test -f outputs/level5/tool-routing-dataset-pack.md
```
````

## Issue 4: Web: add a shareable selected probe case link

Labels:

```text
good first issue, web
```

Body:

````markdown
## Goal

Make Probe Compare cases easier to share in launch posts, GitHub issues, and docs.

Currently the Web lab can show case-level diffs, but a visitor cannot easily copy a stable link to one selected case. Add a small "copy link" affordance for the selected probe case.

## Files

Likely files:

- `web/src/views/ProbeCompareView.tsx`
- `web/src/styles.css`

## Acceptance criteria

- A selected probe case exposes a copyable URL or hash.
- The copied link reopens the Web lab in the relevant compare context as closely as the current router allows.
- The control is compact and does not crowd the case diff.
- `make web-build` succeeds.

## Suggested verification

```bash
make web-build
```
````

## Issue 5: Docs: add a runtime reality check mini-guide

Labels:

```text
good first issue, documentation
```

Body:

````markdown
## Goal

Add a short runtime reality check guide that explains why a LoRA can pass in one runtime and regress in another.

This is one of the strongest lessons in `finetune-lab`, but it needs a beginner-friendly page that links the README edge-bench summary to concrete reports.

## Files

Suggested options:

- `docs/recipes/curriculum-vs-direct.md` for a short warning
- New `docs/recipes/runtime-reality-check.md`
- `edge-bench/README.md` if the explanation should live with runtime evidence

## Evidence to use

- `outputs/edge-bench/baselines/mlx-stage4-strict/inference-probe-report.md`
- `outputs/edge-bench/baselines/llama_cpp-stage4-Q4_K_M-strict/inference-probe-report.md`
- `edge-bench/docs/05-benchmark-results.md`
- `edge-bench/docs/06-policygateway-cross-engine.md`

## Acceptance criteria

- Explain that MLX adapter evidence is not the same as same-LoRA parity in all deployment runtimes.
- Mention llama.cpp fused GGUF regression only within the verified evidence boundary.
- Mention that LiteRT-LM is currently base-only / separately scoped unless same-LoRA artifacts are verified.
- Do not turn the edge-bench results into a generic runtime leaderboard.

## Suggested verification

```bash
test -f outputs/edge-bench/baselines/mlx-stage4-strict/inference-probe-report.md
test -f outputs/edge-bench/baselines/llama_cpp-stage4-Q4_K_M-strict/inference-probe-report.md
```
````
