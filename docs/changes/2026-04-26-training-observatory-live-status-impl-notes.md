# 2026-04-26 Training Observatory Live Status Impl Notes

## Summary

第二阶段把 Observatory 从“静态 run 看板”推进成“半实时训练看板”：

- 真实训练 wrapper 现在会持续写 `run-live-status.json`
- live status 会镜像到 `web/public/run-live/`，如果 `web/dist/` 已存在，也会同步写到 `web/dist/run-live/`
- 前端 Observatory 会在 HTTP 预览环境里每 2 秒轮询一次 live status，并把最新 step、loss、CPU / memory 采样叠加到静态 run 数据上

## Training-side changes

- 新增 [training/finetune/live_status.py](/Users/xforg/AI_SPACE/finetune-lab/training/finetune/live_status.py)
  - 原子写 JSON
  - 采集训练进程 `CPU / RSS / threads`
  - 采集系统 `memory / load average`
  - 镜像 live status 到 `run-live/`
- 更新 [training/finetune/mlx_real_lora_train.py](/Users/xforg/AI_SPACE/finetune-lab/training/finetune/mlx_real_lora_train.py)
  - 从 `subprocess.run` 改成 `Popen + stream parse`
  - 训练进行中持续解析 `train / eval` metric 行
  - 每 2 秒刷新一次 live resource sample
  - 训练完成或失败时写最终状态

## Frontend changes

- `RunSummary` 新增：
  - `liveStatusPath`
  - `liveStatusSnapshot`
- `observatory` 顶层 pack 新增：
  - `live_polling_supported`
- 新版 [web/src/views/TrainingObservatoryView.tsx](/Users/xforg/AI_SPACE/finetune-lab/web/src/views/TrainingObservatoryView.tsx)
  - 轮询 `run-live/<run_id>.json`
  - 合并静态 telemetry 和 recent live telemetry
  - 显示 live CPU / process memory / system memory
  - `file://` 下自动回退静态快照，并提示需要 HTTP 预览才能半实时刷新

## Honest boundary

- 当前 live sampler 已经接通：
  - 训练进程 CPU
  - 训练进程 memory
  - 系统 memory
  - load average
- 当前仍未接通：
  - Apple GPU usage 百分比

所以这版是“CPU / memory 半实时 + GPU planned”，不是伪实时全资源面板。
