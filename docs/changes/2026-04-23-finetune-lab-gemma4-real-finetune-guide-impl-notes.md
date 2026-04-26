# Gemma 4 Real Fine-tune Guide

## Summary

补了一页面向用户的 Gemma 4 真实微调说明，把“当前真实 workflow 是否已通”“应该按什么顺序跑”“当前验证机适合多大数据量”收成一个可直接阅读的文档，而不是散落在聊天记录和实现说明里。

## What Changed

- [docs/ai/gemma4-real-finetune-guide.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/gemma4-real-finetune-guide.md)
  - 新增用户导向说明页
  - 汇总真实 workflow、当前最佳 probe、当前数据规模、机器配置和建议数据量
- [README.md](/Users/xforg/AI_SPACE/finetune-lab/README.md)
  - 增加真实微调说明入口
- [docs/ai/workflows.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/workflows.md)
  - 在 Workflow 3.5 下补用户导向说明链接

## Verification

- `python3 training/finetune/env_probe.py`
- `sysctl -n machdep.cpu.brand_string hw.memsize hw.ncpu hw.physicalcpu`
- `df -h .`
- 核对：
  - `outputs/real/real-finetune-dataset-pack.json`
  - `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/run-manifest.json`
  - `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/inference-probe-report.md`

## Outcome

现在用户可以直接看到：

- 当前真实 Gemma 4 路线已经通到哪里
- 当前真实数据规模是 `80 train / 11 valid / 9 test`
- 当前验证机是 `Apple M5 Pro + 48 GB`
- 下一阶段最合适的扩量建议是先把 train rows 推到 `300 - 800`
