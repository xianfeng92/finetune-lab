# Recipe: tool-calling

## Question

How does an SFT sample teach a model to choose a tool, fill arguments, and produce structured output?

## Run

Generate and validate the demo data:

```bash
make data-demo
make test-data
make level5-pack
```

## Inspect

Start with the dataset and Level 5 packs:

- `data/sft/v1-seed-anchor-demo/samples.jsonl`
- `data/sft/v1-seed-anchor-demo/train.jsonl`
- `data/sft/v1-seed-anchor-demo/held-out.jsonl`
- `data/sft/v1-seed-anchor-demo/validation_report.md`
- `outputs/level5/tool-routing-dataset-pack.md`
- `outputs/level5/structured-output-probe-pack.md`

Read one sample as a contract:

```text
loaded_tool_names + user message -> expected assistant tool call
```

Then check whether the probe preserves that contract:

- exact tool name match
- parsed JSON
- structured output validity
- argument match
- behavior accuracy

## Web View

Open:

```text
https://xianfeng92.github.io/finetune-lab/#/data
https://xianfeng92.github.io/finetune-lab/#/compare
```

## What To Learn

Tool-calling is a good fine-tuning teaching task because the behavior is measurable.

Instead of judging vague language quality, you can ask:

- Was the right tool available?
- Did the model pick it?
- Were the arguments correct?
- Did the system-level behavior match the risk and vehicle state?

## Do Not Overclaim

- More samples are not automatically better if the schema contract is weak.
- A target tool call must not reference tools that are missing from `loaded_tool_names`.
- Safety behaviors such as confirmation and refusal need their own probe checks, not only text inspection.

