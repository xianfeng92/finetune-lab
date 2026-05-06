# finetune-lab Recipes

Recipes are short, reproducible learning paths. Each one starts with one fine-tuning question, names the Makefile commands, and points to the artifacts that prove the answer.

Use these when you want to understand the project by doing one small loop instead of reading the whole repo.

| Recipe | Question | Start here |
| --- | --- | --- |
| [`loss-is-lying`](loss-is-lying.md) | Why can loss improve while behavior still fails? | `make ai-lab` |
| [`first-lora`](first-lora.md) | What does a first LoRA run produce? | `make bootstrap-real-finetune` |
| [`tool-calling`](tool-calling.md) | How does SFT teach tool selection and arguments? | `make data-demo` |
| [`curriculum-vs-direct`](curriculum-vs-direct.md) | When is staged curriculum better than direct mixed training? | `make real-medium-stage-curriculum-consolidation` |

## Reading Order

1. Start with `loss-is-lying` if you are new to fine-tuning metrics.
2. Use `first-lora` to understand run manifests, adapters, and probe outputs.
3. Use `tool-calling` to inspect the training signal inside SFT samples.
4. Use `curriculum-vs-direct` after you understand a single run and want to compare strategies.

## Guardrails

- `SIM` smoke runs are teaching scaffolds, not real model updates.
- `REAL` MLX runs are real LoRA updates, but probe parsing is still runtime-specific.
- Runtime claims must be scoped to the runtime that produced the artifact.

