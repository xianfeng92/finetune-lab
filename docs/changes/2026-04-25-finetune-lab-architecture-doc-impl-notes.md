# 2026-04-25 finetune-lab architecture doc impl notes

## 本次补充

- 新增项目导览文档：`docs/architecture-and-core-workflows.md`

## 文档目标

- 用一页文档把当前仓库的模块分层讲清楚
- 把 `onboarding -> data -> train -> probe -> compare -> frontend` 这条主链路讲清楚
- 把 simulated 路径和 real MLX LoRA 路径放在同一张图里对照
- 给后续人类读者和 AI agent 一个更高层的导航入口

## 内容范围

- Agent / orchestration 层
- data pipeline 层
- training 层
- probe / compare / eval 层
- unified data + frontend 层
- 四条最常用标准 workflow

## 备注

- 这次只新增文档，没有改代码逻辑
- 没有新增构建或测试
