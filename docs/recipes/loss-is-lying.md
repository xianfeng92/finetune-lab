# Recipe: loss-is-lying

## Question

Why can training loss go down while the model still fails the behavior you care about?

## Run

Start with the smallest teaching loop:

```bash
make ai-onboarding
make ai-lab
```

To inspect the current artifacts without rerunning:

```bash
make ai-onboarding
```

## Inspect

Read these files together:

- `outputs/gemma4-e2b-real-mlx-lora-demo/train-metrics.jsonl`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-report.md`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`

Current evidence snapshot:

```text
run_id: gemma4-e2b-real-mlx-lora-demo
evaluation_mode: real-mlx-generate-best-effort
exact_name_match: 0/8
parsed_json: 0/8
structured_output_valid: 0/8
arguments_match: 0/8
```

The teaching point is not that this run is "bad." The point is that a loss curve alone cannot tell you whether the model learned the target behavior.

## Web View

Open the live demo and compare:

- Training Runs: loss curve and run metadata
- Probe Compare: exact tool name, JSON validity, argument match, behavior match

```text
https://xianfeng92.github.io/finetune-lab/#/runs
https://xianfeng92.github.io/finetune-lab/#/compare
```

## What To Learn

Loss is an optimizer signal. Probe results are behavior evidence.

For tool-calling fine-tuning, always ask:

- Did the model choose the right tool?
- Did it produce parseable structured output?
- Did it fill the right arguments?
- Did the behavior match the expected system action?

## Do Not Overclaim

- Do not use this recipe to say LoRA does not work.
- Do not compare SIM and REAL runs as if they were the same kind of training.
- Do not treat a successful training run as proof of deployment runtime behavior.

