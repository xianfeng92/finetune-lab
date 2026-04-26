# finetune

这里放的是本机可执行的最小微调脚手架。

当前默认策略：

- 优先生成稳定的 run 产物
- 默认不要求真实 GPU / MLX 依赖
- 用轻量 smoke train 模拟出 adapter、manifest 和 step metrics
- smoke train 默认吃 `train.jsonl`，probe 默认读 `held-out.jsonl`
- 需要真实训练时，额外提供 Apple Silicon / MLX LoRA 路径

## 运行

```bash
make env-probe
make smoke-train-mac
make probe-mac
make gemma-track-pack
make bootstrap-real-finetune
make real-finetune-data
make real-train-mac
make real-probe-mac
make level5-pack
make level6-demo
```

## Real Mini Fine-tune

真实路径现在使用 `mlx_lm.lora`：

- `make bootstrap-real-finetune`
- `make real-finetune-data`
- `make real-train-mac`
- `make real-probe-mac`
- `make real-single-tool-compare`
- `make real-stage-curriculum`
- `make real-stage-curriculum-consolidation`
- `make real-small-direct-compare`
- `make real-medium-direct-compare`
- `make real-large-direct-compare`
- `make real-medium-stage-curriculum-consolidation`
- `make real-large-stage-curriculum-consolidation`
- `make data-scale-compare-pack`
- `make real-stage-curriculum-replay`
- `make real-medium-cross-domain-focus-refresh`

说明：

- 这条路径默认以 `mlx-community/gemma-4-e2b-it-4bit` 为 base model
- 依赖 Apple Silicon + MLX + 模型下载
- `real-finetune-data` 会把现有 `train.jsonl` / `held-out.jsonl` 转成 MLX 需要的 `train/valid/test.jsonl`
- `REAL_CATEGORY_FILTER=single_domain_single_tool make real-finetune-data` 可以只保留更简单的单工具教学切片
- `REAL_EPOCHS=3 make real-train-mac` 会按 train split 行数自动换算成覆盖约 3 个 epoch 的 iter 数
- `real-probe-mac` 是 best-effort tool-call probe，会尽量按 tokenizer 的 tool parser 解析真实输出
- 仓库内自带 `training/finetune/mlx_compat/gemma4_e2b_compat.py`，用于把 Gemma 4 E2B 的 MLX 兼容修正收敛在仓库里，而不是手改 `.venv`
- `real-single-tool-compare` 会把上面两件事收成一个标准控制实验：先只训 `single_domain_single_tool`，再看模型能不能先学会最小 tool-call 任务
- `real-stage-curriculum` 会按 `single_tool -> reroute/meta -> multi_tool` 续训 adapter，并在最后用 full mixed-task test set 做 probe
- `real-stage-curriculum-consolidation` 会在 pure curriculum 之后，再补一个短的 full-mixed refresh stage，检查能不能把 earlier-stage 边界重新拉齐
- `real-small-direct-compare` 和 `real-medium-direct-compare` 会固定用 full test set 重新 probe，方便做数据量对比
- `real-large-direct-compare` 会在 `800 train / 200 held-out` 的 large 数据上跑同口径 `1 epoch` direct mixed，方便和 medium direct 做公平比较
- `real-medium-stage-curriculum-consolidation` 会把 medium 数据也拉成 `single_tool -> reroute/meta(+confirm/reject) -> multi_tool -> full mixed consolidation`
- `real-large-stage-curriculum-consolidation` 会把 `1000 total` 的 large 数据也拉成同一条 curriculum，用来验证“更多数据 + 课程化训练”能不能真正超过 current medium best
- `data-scale-compare-pack` 会把 small / medium / large 和 direct mixed / curriculum + consolidation 多条路径整理成一份统一 compare pack，供前端和 IAB 展示
- `real-stage-curriculum-replay` 会在 stage 2/3 的 train split 里混入约 `25%` earlier-stage replay，尽量缓解单纯 staged curriculum 带来的 stage bias
- 当前新版 full-test 比较里，small direct 是 `4/10 exact_name_match`，small curriculum + consolidation 是 `8/10`；medium direct 是 `43/48`，medium curriculum + consolidation 是 `47/48`
- `real-medium-cross-domain-focus-refresh` 会先在 medium 数据上做 `cross_domain_multi_tool` focused stage，再补一个 `0.25 epoch` full-mixed micro refresh；当前实测里，这条路径没有超过 focused stage 本身，结果是 `6/8 exact_name_match`、`7/8 structured_output_valid`
