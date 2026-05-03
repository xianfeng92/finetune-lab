# Web Start Here Launch Iteration

## Why

第一波传播主要打中文 AI 学习者和独立开发者圈，Web Overview 需要从“项目指标看板”前移成“新手学习入口”。用户第一次打开页面时，应该马上知道：

- 我先点哪里
- 微调最容易误解的点是什么
- 这个仓库有哪些可以复现、可以发帖的学习路径

## What changed

- 将 Overview 顶部改成 `Start Here` 四步入口：Beginner Guide → Data → Training Runs → Probe Compare。
- 新增 `Loss Trap` 首屏模块，用真实 run 对比说明 `loss 降了，不代表模型学会`。
- 新增 `Recipe Gallery`，把四条传播路径显式产品化：
  - `loss-is-lying`
  - `first-lora`
  - `tool-calling`
  - `curriculum-vs-direct`

## Design notes

- 保留原有 manifesto、roadmap、benchmark 证据层，不把项目做成空的 landing page。
- `Loss Trap` 使用当前 `LabData.runs` 动态挑选真实 run：一个 loss 降幅大但 probe exact 低的反例，一个 probe 表现最好的对照。
- 首屏叙事从 `onboarding -> data -> train -> probe -> compare -> frontend` 中抽出面向新手的可点击顺序。
