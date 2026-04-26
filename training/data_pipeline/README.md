# data_pipeline

最小可运行的数据生成 pipeline。

## 作用

- 读取工具 schema
- 生成 100 条 demo SFT 样本
- 也支持按倍数扩成中等规模数据集
- 给每条样本显式打上 `behavior` 标签
- 给每条样本补 `risk` 和 `vehicle_state`
- 额外切出 `train.jsonl` 和 `held-out.jsonl`
- 严格做 schema 校验
- 输出 `samples.jsonl`、`train.jsonl`、`held-out.jsonl`、`dataset_summary.json/.md` 和 `validation_report.md`

当前 demo 数据里的行为标签会显式写到样本里：

- `tool_call`
- `clarify`
- `confirm`
- `reject`
- `handoff`

这让后续训练、probe 和评测层可以逐步从“按 category 看结构”升级到“按行为决策看质量”。

同一轮里样本也会显式带：

- `risk`: `low / medium / high`
- `vehicle_state.speed_kph`
- `vehicle_state.power_state`

当前这层主要先服务于“把车机场景上下文写进训练样本”，还没有完全升级到 `confirm / reject` 那一层真实执行 contract。

当前已经开始引入最小 contract 字段：

- `expected_system_action.type = create_pending_confirmation`
- `expected_system_action.type = refuse_execution`

这让数据不只是表达“模型该说什么”，也开始表达“系统下一步应该做什么”。

## 运行

```bash
python3 pipeline.py --output-dir ../../data/sft/v1-seed-anchor-demo
```

或在仓库根目录：

```bash
make data-demo
make test-data
```

中等规模数据：

```bash
make data-medium
```

公开数据最小导入：

```bash
make import-car-bench
make import-clarifyvc
```

这条入口会：

- 下载 `CAR-Bench` 的 task JSONL 原始文件
- 把原始文件镜像到 `data/public-source/car-bench/`
- 生成一个最小的 `finetune-lab` 映射 preview 到 `data/public-normalized/car-bench-v1/`

当前这个 preview 只覆盖最容易映射到现有 schema 的 direct tool-call 任务，不会假装已经把整个 `CAR-Bench` 完整接成可训练主数据集。

`ClarifyVC` 入口会：

- 镜像 `OpenReview` 论坛页和论文 PDF 到 `data/public-source/clarifyvc/`
- 基于论文里明确公开的 tier / ambiguity 协议生成一个 `paper_protocol_seed` 预览
- 把可映射到当前 schema 的 `hvac / window / seat` 样本写到 `data/public-normalized/clarifyvc-v1/`

这条入口当前**不是**原始数据克隆。原因是论文公开页给出的匿名代码/数据地址目前在本机环境下返回 `403`，所以这版导入器会明确标注自己是 `protocol seed importer`。
