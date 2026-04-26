# 2026-04-22 finetune-lab Rebuild on Main Impl Notes

## 背景

原 worktree 文件树不可恢复，因此本轮在 `main/finetune-lab` 里按当前会话信息重建一个可运行版本。

## 重建原则

- 优先恢复最小闭环
- 优先保证 `Makefile` 标准入口可跑
- 优先保证前端能读统一数据层
- 重型训练依赖用本机可执行的轻量脚手架替代

## 当前恢复范围

- AI-native 仓库入口
- 数据 pipeline
- smoke train / probe 脚手架
- 前端 Phase 2

## 实际验证

本轮实际跑过：

```bash
make bootstrap-data
make data-demo
make test-data
make env-probe
make smoke-train-mac
make probe-mac
make smoke-train-mac-100
make probe-mac-100
make compare-probes
make web-install
make web-sync-data
make web-build
```

关键产物：

- `data/sft/v1-seed-anchor-demo/samples.jsonl`
- `data/sft/v1-seed-anchor-demo/validation_report.md`
- `outputs/gemma4-e2b-mlx-demo-unsloth-vlm/run-manifest.json`
- `outputs/gemma4-e2b-mlx-demo-unsloth-vlm-100step/run-manifest.json`
- `web/public/lab-data.json`

## 已知差异

这不是丢失 worktree 的字节级恢复，而是功能级重建。
