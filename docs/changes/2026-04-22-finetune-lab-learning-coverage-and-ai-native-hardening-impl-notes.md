# 2026-04-22 finetune-lab Learning Coverage and AI-native Hardening

## 背景

在一轮深度审查里，我们确认 `finetune-lab` 还存在几处会误导学习者或削弱 agent 体验的结构性问题：

- `probe` 还没有真正使用 held-out split
- smoke train / probe 的 simulated 属性不够显式
- Gemma base vs instruct 路线停留在文案层
- onboarding 只检查环境，不检查学习阶段

## 本轮改动

### 1. 数据链路补上 train / held-out split

- `training/data_pipeline/pipeline.py`
  - 新增 `split_samples()`
  - 输出 `train.jsonl` 和 `held-out.jsonl`
  - validation report 现在会写出 split 统计
- `training/data_pipeline/tests/test_validator.py`
  - 新增 split 行为测试
- `training/data_pipeline/README.md`
  - 更新输出说明

### 2. train / probe 标准入口正式分离

- `Makefile`
  - 新增 `FULL_DATASET` / `TRAIN_DATASET` / `HELD_OUT_DATASET`
  - `smoke-train-mac*` 改为读取 `train.jsonl`
  - `probe-mac*` 改为读取 `held-out.jsonl`
  - `level1-pack` / `level5-pack` / `level6-demo` 继续读取全集 `samples.jsonl`

### 3. simulated 属性显式化

- `training/finetune/mlx_tune_sft.py`
  - run manifest 新增 `training_mode`、`simulation_note`、`dataset_role`
- `training/finetune/post_train_probe.py`
  - probe report 新增 `evaluation_mode`、`probe_dataset_path`、`probe_dataset_role`
- `training/finetune/README.md`
  - 明确 smoke train / probe 现在如何消费 split

### 4. Gemma base-vs-instruct 教学包落地

- 新增 `training/finetune/build_gemma_track_pack.py`
- `Makefile` 新增 `make gemma-track-pack`
- 产物路径：
  - `outputs/gemma/base-vs-instruct-pack.json`

这让 `google/gemma-4-E2B` vs `google/gemma-4-E2B-it` 不再只存在于 roadmap 文案里。

### 5. onboarding 升级为学习阶段感知

- `scripts/ai_onboarding_report.py`
  - 新增 `stage_readiness`
  - 新增 `learning_progress`
  - next steps 现在会优先推荐“下一关最值得补什么”
- `docs/ai/setup.md`
  - 更新 onboarding 报告定位

### 6. 前端和 IAB 同步补强

- `web/scripts/build-lab-data.mjs`
  - 统一数据层新增 `gemma_track_pack`
  - source 元数据新增 `train_dataset` / `held_out_dataset`
- `web/src/data-layer.ts`
  - 补充 onboarding / gemma pack 的类型
- `web/src/App.tsx`
  - 新增学习阶段进度展示
  - 新增 train / held-out split 展示
  - 显式提示 simulated smoke train
  - Gemma track 面板新增 base-vs-instruct 对照内容
- `web/scripts/export-standalone-html.mjs`
  - IAB 单文件页同步展示以上内容

### 7. 项目上下文和文档同步更新

- `project-context.json`
  - 更新 workflow stages、key outputs、standard commands
- `README.md`
- `docs/ai/workflows.md`

## 验证建议

推荐按这组命令回归：

```bash
make data-demo
make test-data
make gemma-track-pack
make smoke-train-mac
make probe-mac
make level5-pack
make level6-demo
make ai-onboarding
make web-build
```

## 结果

本轮之后，`finetune-lab` 的教学闭环更接近“能让无基础用户看懂核心概念”的形态，同时也更接近真正的 AI-native 仓库：

- agent 不只知道仓库能不能跑，也知道学习路径到了哪一关
- probe 不再回看训练集
- simulated smoke train 不再被含混表达
- Gemma checkpoint 路线第一次有了可执行教学包
