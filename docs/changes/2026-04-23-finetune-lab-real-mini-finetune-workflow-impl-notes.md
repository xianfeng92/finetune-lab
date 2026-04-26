# Real Mini Fine-tune Workflow

## Summary

这次补了一条真实小规模微调 workflow，用来把项目从“只有 simulated smoke train”推进到“在 Apple Silicon 上可执行的真实 MLX LoRA mini fine-tune”。

## What Changed

- 新增 `make bootstrap-real-finetune`
  安装 `.venv-real-train` 和 `mlx-lm[train]`
- 新增 `make real-finetune-data`
  把 `train.jsonl` / `held-out.jsonl` 转成 MLX 需要的 `train/valid/test.jsonl`
- 新增 `make real-train-mac`
  通过 `mlx_lm.lora` 对 `mlx-community/gemma-4-e2b-it-4bit` 跑真实 LoRA mini fine-tune
- 新增 `make real-probe-mac`
  对真实 adapters 做 best-effort probe，并尽量沿用现有 `inference-probe-results.json` 结构
- 新增仓库内 Gemma 4 E2B 兼容层
  `training/finetune/mlx_compat/gemma4_e2b_compat.py` 和 `training/finetune/mlx_lora_entry.py` 会在真实训练/推理前显式注入兼容修正，不再依赖手改 `.venv`
- 修正 real dataset 的 tool-call 参数编码
  `training/finetune/build_real_finetune_dataset.py` 现在保留原生 `arguments` 对象，不再提前 `json.dumps(...)`。
  这样 Gemma 4 chat template 会生成可被 tokenizer parser 识别的 `call:name{...}` 结构，而不是错误的 `call:name{{...}}`
- 加强 real probe 的 parser 容错
  `training/finetune/mlx_real_probe.py` 现在会在 `<|tool_call>...<tool_call|>` 分段解析失败时保留 `parse_error` 并继续回退到后续 best-effort 路径，不会因为单条坏 payload 直接崩掉

## New Artifacts

- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/valid.jsonl`
- `data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl`
- `outputs/real/real-finetune-dataset-pack.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json`
- `outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-results.json`

## Teaching Impact

- Level 3 现在不再只有 simulated 路径，也有真实 optimizer update 路径
- onboarding 报告可以显式告诉 agent：当前仓库有没有 real MLX LoRA 能力
- 前端统一数据层会自动读到新的 real run manifest，后续可以直接展示 simulated vs real

## Verification

- `make bootstrap-real-finetune`
- `.venv-real-train/bin/python -m mlx_lm.lora --help`
- `make real-finetune-data`
- `.venv-real-train/bin/python - <<'PY' ... tokenizer.apply_chat_template(...)` 验证修复后训练样本会渲染成可解析的 `call:name{...}`，不再是双大括号 payload
- `.venv-real-train/bin/python - <<'PY' ... load('mlx-community/gemma-4-e2b-it-4bit')` 在无 compat 时失败、在仓库 compat 下成功
- `make real-train-mac`
- `make real-probe-mac`

## Remaining Boundaries

- 默认 `ai-lab` 仍然保持轻量 simulated 路径，不强制拉起真实模型下载
- `mlx_lm.lora` 这里需要 MLX-converted Gemma 4 checkpoint，不能直接拿原始 `google/gemma-4-E2B-it` 权重开训
- `real-probe-mac` 是 best-effort 解析，不应被描述成统一 benchmark
- 这次没有在本机完整跑完 `google/gemma-4-E2B-it` 的真实训练，因为它会触发较大的模型下载与算力消耗
