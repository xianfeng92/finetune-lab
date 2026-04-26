---
title: Training Observatory Spec
status: implemented
owner: codex
created: 2026-04-26
updated: 2026-04-26 (implemented; phase-2 live polling)
implements:
  - docs/changes/2026-04-26-training-observatory-impl-notes.md
  - docs/changes/2026-04-26-training-observatory-live-status-impl-notes.md
reviews: []
---

## 目标

在现有 `web` 实验台里新增一个 **Training Observatory** 视图，把“训练进度 / 关键指标 / 行为级质量 / 资源摘要”收成一页专业看板，让用户可以在不翻日志的前提下直接回答：

1. 这次 run 训到哪了、配方是什么
2. train / val loss 怎么走
3. throughput 和 peak memory 怎么样
4. probe 指标里，exact / structured / behavior / confirm / reject 到底到什么水平

## 第一版范围

第一版是 **静态 observatory skeleton**，只读取已有 run 产物：

- `run-manifest.json`
- `run-plan.json`
- `train-metrics.jsonl`
- `eval-metrics.jsonl`
- `inference-probe-results.json`

第一版不做 websocket，不做后台轮询，不做 live CPU/GPU 采集守护进程。

## 不在范围

- 不做真正实时的 CPU / GPU usage 曲线
- 不做训练中途自动刷新
- 不做多用户 / 远程训练任务监控
- 不新增后端服务
- 不替换现有 `Training Runs` / `Probe Compare` 视图

## 数据设计

在 `RunSummary` 上新增 observability 字段：

- `trainTelemetry`
  - `step`
  - `loss`
  - `learning_rate`
  - `iterations_per_second`
  - `tokens_per_second`
  - `trained_tokens`
  - `peak_memory_gb`
- `evalTelemetry`
  - `step`
  - `val_loss`
  - `val_time_s`
- `runPlan`
  - `requested_epochs`
  - `effective_epochs`
  - `batch_size`
  - `learning_rate`
  - `steps_per_report`
  - `steps_per_eval`
  - `save_every`
  - `max_seq_length`
  - `num_layers`
  - `compat_patch`
- `resourceSummary`
  - `peak_memory_gb`
  - `avg_iterations_per_second`
  - `avg_tokens_per_second`
  - `best_val_loss`
  - `last_val_loss`
  - `avg_val_time_s`
  - `last_val_time_s`
  - `host_platform`
  - `host_arch`
  - `live_cpu_usage_supported`
  - `live_gpu_usage_supported`
  - `live_memory_usage_supported`

另加顶层 `observatory`：

- `latest_real_run_id`
- `best_exact_run_id`
- `best_behavior_run_id`
- `telemetry_coverage`
- `host_machine`
- `teaching_notes`

## UI 结构

新增侧边栏入口：`Observatory`

页面结构：

1. **Hero**
   - latest real run
   - best exact
   - best behavior
   - telemetry coverage
   - live CPU/GPU support status
2. **Run picker**
   - 选择要观察的 real run
3. **Control room**
   - dataset / steps / avg loss / best val / epochs / batch / eval cadence
4. **Curves**
   - Train loss
   - Validation loss
5. **Resources**
   - peak memory
   - avg it/s
   - avg tok/s
   - last eval time
   - host machine info
6. **Behavior KPIs**
   - exact
   - structured
   - args
   - behavior
   - unsafe
   - confirm / reject contract
7. **Telemetry snapshots**
   - 最近 8 个 train telemetry 点

## 设计原则

- 明确区分“训练过程指标”和“行为级质量指标”
- 明确区分“训练期间真实采集到的资源 telemetry”和“尚未接入的 live CPU/GPU”
- 第一版先做成专业的静态监控板，而不是半成品实时系统
- 不把 observatory 做成通用 dashboard，要保留 `finetune-lab` 的教学属性

## 成功标准

- 前端出现 `Observatory` 入口
- 能选择真实 run 查看训练看板
- 至少能看见 train loss、val loss、peak memory、avg it/s、avg tok/s、behavior KPIs
- 页面明确说明 live CPU/GPU 尚未接入，而不是误导用户以为没有这类指标
- `make web-build` 可以完整构建通过

## 后续扩展

- 训练进行中定期刷新 `run-live-status.json`
- 新增 CPU / GPU / memory 采集脚本
- 让 observatory 在训练中 live refresh
- 为 stage run 加一个“课程进度”总览条
