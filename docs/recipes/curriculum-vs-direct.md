# Recipe: curriculum-vs-direct

## Question

When does staged curriculum training beat direct mixed-task training?

## Run

Use the medium comparison paths when you want a real Apple Silicon experiment:

```bash
make real-medium-direct-compare
make real-medium-stage-curriculum-consolidation
make data-scale-compare-pack
```

These targets can take much longer than the simulated teaching loop because they use real MLX LoRA training.

## Inspect

Direct mixed run:

- `outputs/gemma4-e2b-real-mlx-lora-medium-direct/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-direct/inference-probe-report.md`

Current evidence snapshot:

```text
exact_name_match: 43/48
structured_output_valid: 47/48
arguments_match: 37/48
behavior_accuracy: 47/48
```

Curriculum + consolidation run:

- `outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum-consolidation/stage4-consolidation/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md`

Current evidence snapshot:

```text
exact_name_match: 47/48
structured_output_valid: 47/48
arguments_match: 45/48
behavior_accuracy: 48/48
```

Unified compare pack:

- `outputs/compare/data-scale-compare-pack.json`
- `outputs/compare/data-scale-compare-pack.md`

## Web View

Open:

```text
https://xianfeng92.github.io/finetune-lab/#/compare
https://xianfeng92.github.io/finetune-lab/#/runs
```

## What To Learn

Direct mixed training answers:

```text
Can one pass over the mixed task distribution learn the full behavior?
```

Curriculum + consolidation answers:

```text
Can staged training learn easier slices first, then recover full mixed-task behavior?
```

In the current medium evidence, curriculum + consolidation improves exact tool selection, arguments, and behavior accuracy over medium direct mixed.

## Do Not Overclaim

- This is an evidence-backed teaching comparison, not a universal rule that curriculum always wins.
- Keep dataset size, split, model, epoch budget, and probe set aligned before comparing strategies.
- Runtime-specific deployment checks still need their own probe path.

