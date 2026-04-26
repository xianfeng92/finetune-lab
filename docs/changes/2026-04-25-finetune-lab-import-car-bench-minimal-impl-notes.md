# 2026-04-25 finetune-lab import car bench minimal impl notes

## 本次实现

- 新增最小 `CAR-Bench` 导入脚本：
  - `training/data_pipeline/import_car_bench.py`
- 新增标准入口：
  - `make import-car-bench`
- 新增单元测试：
  - `training/data_pipeline/tests/test_import_car_bench.py`
- 更新数据 pipeline README，补充公开数据导入入口

## 当前脚本做了什么

- 直接从 Hugging Face raw 链接下载 `CAR-Bench` task JSONL
- 把原始任务文件镜像到：
  - `data/public-source/car-bench/`
- 生成一个最小的 mapping preview 到：
  - `data/public-normalized/car-bench-v1/`

## 当前映射范围

当前只覆盖最容易映射到现有 `finetune-lab` schema 的 direct tool-call 子集：

- `set_climate_temperature`
- `set_fan_speed`
- `open_close_window`
- `set_seat_heating`

并且只保留：

- `task_type = base`
- `task_type = disambiguation_internal`

## 当前没有做的事

- 没有把 `disambiguation_user` 直接伪装成训练样本
- 没有把 `hallucination_*` 直接并入主训练集
- 没有把整个 `CAR-Bench` 映射成可直接 `real-finetune-data` 的主线数据

## 目标定位

这次实现的目标不是“完整接入 CAR-Bench”，而是：

- 先把公开数据真正拉进仓库
- 先验证哪些 task/action 能较干净地映射到现有车控 schema
- 给下一步 public-source blend 实验一个可复用的入口
