# 2026-04-22 finetune-lab Level 1 Baseline Pack Implementation Notes

## 本轮目标

把 Gemma 4 E2B 学习路线里的 `Level 1: Baseline and Task Framing` 从 `partial` 补成可执行教学包：

- 不再只在路线图上写“先做 baseline”
- 而是给出一份真正可读的 task framing pack
- 再给出一份 baseline eval pack，明确展示 prompt baseline 大概率怎么错

## 实现内容

### 1. 新增标准入口

新增：

- `make level1-pack`

对应脚本：

- `training/finetune/build_level1_pack.py`

会读取：

- `data/sft/v1-seed-anchor-demo/samples.jsonl`

并生成：

- `outputs/level1/task-framing-pack.json`
- `outputs/level1/task-framing-pack.md`
- `outputs/level1/baseline-eval-pack.json`
- `outputs/level1/baseline-eval-pack.md`

### 2. Level 1 教学产物结构

`task-framing-pack` 主要回答四个问题：

1. 这个任务到底在学什么
2. success rubric 是什么
3. baseline 最容易踩进哪些 failure buckets
4. 哪些 held-out seed cases 值得后续 Level 3/4 继续追踪

`baseline-eval-pack` 主要回答：

1. prompt-only baseline 在 6 类代表 case 上会怎么出错
2. 错误更多是 route selection、结构化输出、arguments 还是 chain coverage
3. 为什么后续 probe 不该只看 loss

### 3. 统一接入项目上下文和前端

更新了：

- `project-context.json`
- `docs/ai/workflows.md`
- `README.md`
- `web/scripts/build-lab-data.mjs`
- `web/src/App.tsx`
- `web/scripts/export-standalone-html.mjs`

现在 React 前端和 IAB 静态页都能直接展示：

- task framing
- success rubric
- failure buckets
- held-out seed cases
- baseline eval case summary

## 教学价值

这轮最重要的不是新增一个“更早的 tab”，而是补齐一个之前缺失的心智模型：

- 训练前，先定义什么算成功
- 训练前，先知道模型会怎么错
- 训练后，才能把 SFT / probe / compare 的变化讲清楚

## 验证

本轮实际执行：

```bash
make level1-pack
make web-build
```

预期结果：

- `outputs/level1/*.json` 已生成
- `web/public/lab-data.json` 已包含 `level1`
- `web/dist/index.html` 可直接在 `file://` 下展示 Level 1 baseline 区块
