# Recipe: first-lora

## Question

What does a first real LoRA run produce, and how do you inspect it?

## Run

On Apple Silicon, use the real MLX path:

```bash
make bootstrap-real-finetune
make real-finetune-data
make real-train-mac
make real-probe-mac
```

If you only want the lightweight teaching loop first:

```bash
make ai-lab
```

## Inspect

For the default real mini fine-tune, inspect:

- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/train-metrics.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-report.md`

Look for four artifact classes:

| Artifact | What it proves |
| --- | --- |
| dataset split | training and probe are not reading the same file |
| run manifest | which model, dataset, steps, and training mode produced the run |
| adapter directory | a real LoRA path produced trainable adapter artifacts |
| probe report | behavior was checked after training |

## Web View

Open:

```text
https://xianfeng92.github.io/finetune-lab/#/runs
https://xianfeng92.github.io/finetune-lab/#/observatory
https://xianfeng92.github.io/finetune-lab/#/compare
```

## What To Learn

A LoRA run is more than a loss curve. The minimum inspectable bundle is:

```text
dataset -> run manifest -> adapter -> metrics -> held-out probe
```

If one of those pieces is missing, the run is hard to explain and hard to reproduce.

## Do Not Overclaim

- The simulated smoke run is useful for learning artifact shape, but it is not a real model update.
- The real MLX probe is best-effort structured parsing, not a universal benchmark across all runtimes.
- A local MLX result does not automatically prove llama.cpp, LiteRT-LM, or other deployment runtime behavior.

