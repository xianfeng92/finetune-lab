# AI Workflows

## Workflow 0: AI-native Onboarding

```bash
make ai-onboarding
make ai-setup
```

输出：

- `outputs/agent/onboarding-report.json`
- `outputs/agent/onboarding-report.md`

作用：

- 判断当前机器和仓库是否 ready
- 告诉 agent 下一步应该补依赖、跑数据还是直接跑完整实验
- 告诉 agent 学习链路当前推进到了哪一关

## Workflow 0.5: Minimal AI-native Lab

```bash
make ai-lab
```

作用：

- 一次性跑通最小教学闭环
- 让 agent 能把 `data -> train -> probe -> frontend` 一次解释清楚
- 同时刷新 Level 1、Gemma track、held-out probe 这些教学支点

## Workflow 1: Level 1 Baseline Pack

```bash
make level1-pack
```

输出：

- `outputs/level1/task-framing-pack.json`
- `outputs/level1/baseline-eval-pack.json`

作用：

- 先定义任务、success rubric 和 failure buckets
- 用最小 held-out seed cases 说明 prompt baseline 大概率会怎么错

## Workflow 2: Data Demo

```bash
make bootstrap-data
make data-demo
make test-data
```

输出：

- `data/sft/v1-seed-anchor-demo/samples.jsonl`
- `data/sft/v1-seed-anchor-demo/train.jsonl`
- `data/sft/v1-seed-anchor-demo/held-out.jsonl`
- `data/sft/v1-seed-anchor-demo/validation_report.md`

说明：

- 每条样本现在都显式带 `behavior` 字段，区分 `tool_call / clarify / handoff`
- 每条样本也显式带 `risk` 和 `vehicle_state`
- 高风险样本开始引入 `confirm / reject` 行为和 `expected_system_action`
- `category` 继续描述任务结构，`behavior` 则开始承接更贴近车机设计的动作决策层

中等规模版本：

```bash
make data-medium
make real-finetune-data-medium
make data-large
make real-finetune-data-large
```

输出：

- `data/sft/v1-gemma4-e2b-medium/samples.jsonl`
- `data/sft/v1-gemma4-e2b-medium/train.jsonl`
- `data/sft/v1-gemma4-e2b-medium/held-out.jsonl`
- `data/sft/v1-gemma4-e2b-medium/dataset_summary.json`
- `data/real-finetune/v1-gemma4-e2b-medium/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-medium/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-medium/test.jsonl`
- `outputs/real/real-finetune-dataset-pack-medium.json`
- `data/sft/v1-gemma4-e2b-large/samples.jsonl`
- `data/sft/v1-gemma4-e2b-large/train.jsonl`
- `data/sft/v1-gemma4-e2b-large/held-out.jsonl`
- `data/sft/v1-gemma4-e2b-large/dataset_summary.json`
- `data/real-finetune/v1-gemma4-e2b-large/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-large/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-large/test.jsonl`
- `outputs/real/real-finetune-dataset-pack-large.json`

说明：

- medium 路线现在也保留 `behavior`
- medium 路线现在也保留 `risk` 和 `vehicle_state`
- medium 路线现在也保留 `expected_system_action`
- medium 路线已经包含 `confirm_required_action` 和 `reject_unsafe_action`
- 当前最新 medium real pack 切分为 `400 train / 52 valid / 48 test`
- large 路线用于把同一份新版 schema 扩到 `1000 total` 左右，并和 medium 做同口径 direct mixed 对比

## Workflow 2.5: Gemma Base-vs-Instruct Pack

```bash
make gemma-track-pack
```

输出：

- `outputs/gemma/base-vs-instruct-pack.json`

作用：

- 把 `google/gemma-4-E2B` 和 `google/gemma-4-E2B-it` 的教学角色显式化
- 让路线图里的 base vs instruct 不只停留在概念层

## Workflow 3: Smoke Train

```bash
make smoke-train-mac
make probe-mac
```

输出：

- `outputs/gemma4-e2b-mlx-demo-unsloth-vlm/run-manifest.json`
- `outputs/gemma4-e2b-mlx-demo-unsloth-vlm/inference-probe-results.json`

说明：

- 当前默认是教学用 simulated smoke train
- train 吃 `train.jsonl`，probe 读 `held-out.jsonl`

## Workflow 3.5: Real Mini Fine-tune

```bash
make bootstrap-real-finetune
make real-finetune-data
make real-train-mac
make real-probe-mac
make real-single-tool-compare
make real-stage-curriculum
make real-stage-curriculum-consolidation
make real-small-direct-compare
make real-medium-direct-compare
make real-medium-public-augmented-direct-compare
make real-large-direct-compare
make real-medium-stage-curriculum-consolidation
make real-large-stage-curriculum-consolidation
make data-scale-compare-pack
make real-stage-curriculum-replay
```

输出：

- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl`
- `outputs/real/real-finetune-dataset-pack.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-results.json`
- `outputs/real/real-finetune-dataset-pack-single-tool-control.json`
- `outputs/gemma4-e2b-real-mlx-lora-single-tool-control/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-single-tool-control/inference-probe-results.json`
- `outputs/real/real-finetune-dataset-pack-stage1-single-tool.json`
- `outputs/real/real-finetune-dataset-pack-stage2-reroute-meta.json`
- `outputs/real/real-finetune-dataset-pack-stage3-multi-tool.json`
- `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum/stage3-multi-tool/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation/stage4-consolidation/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-small-direct/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-direct/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-public-augmented-direct/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-large-direct/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum-consolidation/stage4-consolidation/inference-probe-results.json`
- `outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum-consolidation/stage4-consolidation/inference-probe-results.json`
- `outputs/compare/data-scale-compare-pack.json`
- `outputs/real/real-finetune-dataset-pack-stage2-reroute-meta-replay.json`
- `outputs/real/real-finetune-dataset-pack-stage3-multi-tool-replay.json`
- `outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-replay/stage3-multi-tool/inference-probe-results.json`

说明：

- 这条路径面向 Apple Silicon，本机通过 `mlx_lm.lora` 做真实 LoRA 更新
- 默认模型使用 `mlx-community/gemma-4-e2b-it-4bit`，因为 `mlx_lm` 真实训练需要 MLX-converted checkpoint
- 仓库内的 `training/finetune/mlx_lora_entry.py` 会主动加载 `mlx_compat/gemma4_e2b_compat.py`，把 Gemma 4 E2B 的兼容修正留在仓库内
- `real-finetune-data` 会把现有教学数据转换成 OpenAI chat + tools 格式，直接喂给 `tokenizer.apply_chat_template(..., tools=...)`
- `REAL_CATEGORY_FILTER=single_domain_single_tool make real-finetune-data` 可以先只保留最简单的单工具切片，适合做控制实验
- `REAL_EPOCHS=3 make real-train-mac` 会按数据行数自动估算 iter 数，避免继续停留在 12-step 不到一轮的教学 smoke 配置
- `real-probe-mac` 使用 best-effort 解析，不会伪装成“完全可靠的统一 benchmark”
- `real-small-direct-compare` 和 `real-medium-direct-compare` 用来回答“同一 schema 下，直接 mixed 训练时扩数据会发生什么”
- `real-medium-public-augmented-direct-compare` 用来回答“把当前可映射的 `CAR-Bench + ClarifyVC` 公开样本直接并进 medium train split，会不会立刻提升主线 mixed-task probe”
- `real-large-direct-compare` 用来继续回答“把同一 schema 扩到 1000 total 后，direct mixed 还能不能继续收益”
- `real-medium-stage-curriculum-consolidation` 用来回答“同一份 medium 数据，curriculum + consolidation 能不能比 direct mixed 更稳”
- `real-large-stage-curriculum-consolidation` 用来回答“把同一份新版 schema 扩到 1000 total 后，curriculum + consolidation 能不能真正超过 current medium best”
- `data-scale-compare-pack` 会把 small / medium / large、public-augmented medium，以及 direct mixed / curriculum + consolidation 收成一份统一 compare 数据包
- `real-single-tool-compare` 把上面两条收成一个标准入口，适合先回答“这颗模型能不能先学会最小单工具调用”
- `real-stage-curriculum` 会显式按 `single_tool -> reroute/meta -> multi_tool` 续训 adapter，最后再回到 full mixed-task test set 上做统一 probe
- `real-stage-curriculum-consolidation` 会在 pure curriculum 之后，再补一个短的 full-mixed consolidation stage，检查 repeated call / fallback miss 这类边界问题能不能被收回来
- `real-stage-curriculum-replay` 会在 stage 2/3 的 train split 里混入约 `25%` 的 earlier-stage replay，避免后续 stage 把 earlier-stage 能力完全覆盖掉
- 当前实测里，`real-stage-curriculum-consolidation` 已经把 mixed-task probe 推到 `7/8 exact_name_match`、`8/8 structured_output_valid`、`6/8 arguments_match`
- 当前实测里，`real-stage-curriculum-replay` 最终是 `2/8 exact_name_match`、`6/8 structured_output_valid`，还没有超过 direct mixed-task `3 epoch` 的 `4/8`

用户导向说明：

- [docs/ai/gemma4-real-finetune-guide.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/gemma4-real-finetune-guide.md)

## Workflow 4: Compare Runs

```bash
make smoke-train-mac-100
make probe-mac-100
make compare-probes
```

## Workflow 4.5: Behavior Eval Pack

```bash
make behavior-eval-pack
```

输出：

- `outputs/behavior/behavior-eval-pack.json`
- `outputs/behavior/behavior-eval-pack.md`

作用：

- 把 route accuracy 和行为决策评测拆开
- 额外统计 `behavior_accuracy`
- 对高风险样本统计 `unsafe_direct_call_rate`
- 对 `confirm / reject` 样本统计 contract 命中情况

## Workflow 5: Level 5 Pack

```bash
make level5-pack
```

输出：

- `outputs/level5/tool-routing-dataset-pack.json`
- `outputs/level5/structured-output-probe-pack.json`

作用：

- 把 route selection 和 structured outputs 单独抽成教学专题
- 让前端能直接展示 tool-routing dataset pack 和 structured-output probe pack

## Workflow 6: Level 6 Demo

```bash
make level6-demo
```

输出：

- `data/preferences/v1-gemma4-e2b-demo/pairs.jsonl`
- `outputs/level6/preference-dataset-pack.json`
- `outputs/level6/policy-compare-report.json`
- `outputs/level6/scale-up-rubric.json`
- `outputs/level6/gemma-scale-up-compare.json`

作用：

- 用更分层的 preference pairs 覆盖 multi-call、reroute 和 event-driven case
- 用 policy compare 展示 SFT-only 和 preference-aware 的行为差异
- 用 scale-up rubric 和 compare 明确回答“现在该继续留在 E2B-it，还是值得升级到 E4B-it”

## Workflow 7: Frontend Lab

```bash
make web-install
make web-sync-data
make web-build
```

输出：

- `web/public/lab-data.json`
- `web/dist/index.html`
