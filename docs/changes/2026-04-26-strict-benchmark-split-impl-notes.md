# Strict Benchmark Split Implementation Notes

## Why

之前的 `held-out` split 已经避免了逐行复用训练样本，但模板数量很少，train 和 held-out 仍会共享同一个 prompt/target 模板。对教学闭环来说这足够直观；对严肃微调 benchmark 来说，它会把“模板复现”误读成“泛化学会”。

## What Changed

1. `training/data_pipeline/pipeline.py`
   - 每条生成样本新增 `template_id`、`split_group`、`eval_split`、`split_strategy`
   - 新增 `--split-strategy group`
   - `dataset_summary.json/.md` 新增 `benchmark_leakage`
   - 补足 `full_tool_fallback` 多模板变体，避免严格 group split 下某个 category 训练侧为空

2. `training/finetune/build_real_finetune_dataset.py`
   - 保留 benchmark split 元数据到 MLX chat+tools 数据
   - valid/test re-split 按 `split_group` 保持分组完整
   - 新增 `--validation-source train`，用于 strict benchmark：validation 从 train groups 留出，完整 held-out 作为 final test

3. `training/finetune/mlx_real_probe.py`
   - probe result 保留 `template_id / split_group / eval_split / split_strategy`
   - 新增 `--base-only`，支持无 adapter base checkpoint probe

4. `Makefile`
   - 新增 `make data-benchmark`
   - 新增 `make real-finetune-data-benchmark`
   - 新增 `make real-probe-base-mac`
   - 新增 `make real-benchmark-direct-compare`
   - 新增 medium/large 4-epoch direct budget parity targets

## Current Artifacts

- `data/sft/v1-gemma4-e2b-benchmark/`
- `data/real-finetune/v1-gemma4-e2b-benchmark/`
- `outputs/real/real-finetune-dataset-pack-benchmark.json`

Current strict benchmark summary:

- SFT split: `500 total / 356 train / 144 held-out`
- MLX split: `230 train / 126 valid / 144 test`
- prompt/input overlap: `0`
- split_group overlap: `0`
- exact target overlap: `0`

## Verification

```bash
make test-data
.venv-data/bin/python -m pytest training/finetune/tests
make data-benchmark
make real-finetune-data-benchmark
```

Notes:

- `python3 -m pytest training/finetune/tests` uses the system Python 3.9 on this machine and fails on existing `datetime.UTC` compatibility. The repo venv path above uses Python 3.14 and passes.
- This change adds the strict benchmark path but does not run the expensive real LoRA benchmark training by default.
