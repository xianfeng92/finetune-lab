---
status: implemented
summary: 新增 Training Observatory 第一版静态看板，把真实 run 的 train/eval telemetry、运行配方、行为 KPI 和资源摘要接进前端统一数据层。
---

# Training Observatory

## 本次实现

- 新增 `Observatory` 视图
- `RunSummary` 现在会携带：
  - `trainTelemetry`
  - `evalTelemetry`
  - `runPlan`
  - `resourceSummary`
- 顶层 `LabData` 新增 `observatory`
- `Overview` 的起步卡新增 observatory 入口

## 数据来源

全部来自现有 run 产物：

- `train-metrics.jsonl`
- `eval-metrics.jsonl`
- `run-plan.json`
- `run-manifest.json`
- `inference-probe-results.json`

没有引入新后端，也没有新增训练时守护进程。

## 第一版能看什么

- latest real run / best exact / best behavior
- train loss 曲线
- validation loss 曲线
- avg it/s
- avg tok/s
- peak memory
- last / best val loss
- batch / epoch / eval cadence / save cadence
- exact / structured / args / behavior / unsafe
- confirm / reject contract
- 最近 8 个 telemetry snapshots

## 第一版刻意没做什么

- 不假装已经有 live CPU usage
- 不假装已经有 live GPU usage
- 不做 training in progress 自动刷新

前端会显式把这些能力标成 `planned`，避免把“当前没有采到”误解成“训练期间没有资源指标”。

## 为什么这样切

当前 `mlx_lm.lora` 真训练日志已经稳定提供：

- `loss`
- `learning_rate`
- `iterations_per_second`
- `tokens_per_second`
- `trained_tokens`
- `peak_memory_gb`
- `val_loss`
- `val_time_s`

这些已经足够支撑一个专业的“静态 observatory”。真正的 live CPU/GPU/memory 采集应该是下一阶段的独立 telemetry 工程，不应该混在第一版 UI 骨架里硬凑。

## 下一步建议

- 给真实训练加一个轻量 `resource sampler`
- 输出 `run-live-status.json`
- 让 Observatory 在训练中轮询刷新
