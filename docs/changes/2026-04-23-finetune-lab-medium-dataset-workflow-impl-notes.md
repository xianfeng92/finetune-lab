# Medium Dataset Workflow

## Summary

把“下一阶段扩到 `300 - 800 train / 60 - 120 eval`”这件事落成了标准 workflow，而不是只停留在建议里。

这次新增了一套中等规模 Gemma 4 数据入口：

- `make data-medium`
- `make real-finetune-data-medium`

默认会生成：

- `400 train`
- `100 held-out`

然后再转换成真实 LoRA 使用的：

- `400 train`
- `51 valid`
- `49 test`

## What Changed

- [training/data_pipeline/pipeline.py](/Users/xforg/AI_SPACE/finetune-lab/training/data_pipeline/pipeline.py)
  - 支持 `--multiplier`
  - 支持 `--held-out-ratio`
  - 新增 `dataset_summary.json/.md`
- [Makefile](/Users/xforg/AI_SPACE/finetune-lab/Makefile)
  - 新增 `make data-medium`
  - 新增 `make real-finetune-data-medium`
- [training/data_pipeline/README.md](/Users/xforg/AI_SPACE/finetune-lab/training/data_pipeline/README.md)
- [docs/ai/workflows.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/workflows.md)
- [docs/ai/gemma4-real-finetune-guide.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/gemma4-real-finetune-guide.md)

## Verification

- `make test-data`
- `make data-medium`
- `make real-finetune-data-medium`

## Outcome

现在仓库里同时有两条数据规模路径：

1. `v1-seed-anchor-demo`
   - 小规模教学闭环
   - `80 train / 20 held-out`

2. `v1-gemma4-e2b-medium`
   - 下一阶段本地实验
   - `400 train / 100 held-out`
   - 对应真实 LoRA 数据 `400 train / 51 valid / 49 test`
