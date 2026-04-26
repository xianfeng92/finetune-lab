# 2026-04-25 finetune-lab public datasets research impl notes

## 本次补充

- 新增公开数据研究与接入方案文档：
  - `docs/ai/public-datasets-for-car-tool-finetuning.md`

## 补充目标

- 给当前 `Gemma 4 E2B` 微调路线补一份公开数据盘点
- 说明哪些公开数据适合当前仓库
- 给出第一版映射到 `finetune-lab` schema 的接入方案

## 当前结论

- 最值得优先接入的公开来源：
  - `CAR-Bench`
  - `ClarifyVC`
  - `KVRET`
- 最合理的接入顺序：
  1. 先 `CAR-Bench`
  2. 再 `ClarifyVC`
  3. 最后 `KVRET`

## 范围说明

- 这次只新增研究与接入方案文档
- 没有开始实现公开数据导入脚本
- 没有新增训练或评测运行
