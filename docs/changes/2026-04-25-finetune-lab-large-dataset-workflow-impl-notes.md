# Large Dataset Workflow

## 本次改动

- 新增 `make data-large`
- 新增 `make real-finetune-data-large`
- 新增 `make real-large-direct-compare`
- 更新真实微调和 workflow 文档

## 目标

在当前 `500 total` 的 medium 路线之上，再补一个 `1000 total` 的 large 数据档位，用来回答：

- 当 `Gemma 4 E2B` 继续扩数据量时，真实 `MLX LoRA` 的 direct mixed 表现会不会继续提升
- 这一档数据量在当前 `Apple Silicon + 48GB` 环境下是否仍然适合作为本地实验路径

## 标准入口

```bash
make data-large
make real-finetune-data-large
make real-large-direct-compare
```

## 预期产物

- `data/sft/v1-gemma4-e2b-large/`
- `data/real-finetune/v1-gemma4-e2b-large/`
- `outputs/real/real-finetune-dataset-pack-large.json`
- `outputs/gemma4-e2b-real-mlx-lora-large-direct/`

## 说明

- `data-large` 使用当前新版 schema，继续保留：
  - `behavior`
  - `risk`
  - `vehicle_state`
  - `expected_system_action`
  - `confirm / reject`
- `real-large-direct-compare` 固定走 `1 epoch direct mixed`，这样可以和现有 `medium direct` 做公平对比
