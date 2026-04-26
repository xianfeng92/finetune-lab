# finetune-lab Agent Guide

## 项目定位

`finetune-lab/` 是一个 AI-native 开源实验仓库，用来帮助人理解：

1. SFT 数据如何生成
2. 微调脚手架如何搭
3. 训练后如何做 probe
4. 前端如何把这条链路可视化

## 读文件顺序

1. `README.md`
2. `project-context.json`
3. `docs/ai/setup.md`
4. `docs/ai/workflows.md`
5. `training/data_pipeline/README.md`
6. `training/finetune/README.md`

## 协作规范

- 输出语言：中文为主，代码/变量名用英文
- 文档命名：英文 kebab-case
- 优先通过 `Makefile` 标准入口执行，不要猜命令
- 设计变更写到 `docs/changes/`

## AI-native Onboarding 协议

当用户让 agent 接手仓库时，默认按这条顺序：

1. 先读取 `AGENTS.md`、`project-context.json`、`docs/ai/setup.md`、`docs/ai/workflows.md`
2. 先执行 `make ai-onboarding` 判断 readiness
3. 如果依赖未准备好，先执行 `make ai-setup`
4. 如果用户要跑最小教学闭环，执行 `make ai-lab`
5. 在执行过程中，持续解释 `onboarding -> data -> train -> probe -> compare -> frontend` 的关系

不要让用户自己猜命令，也不要绕开 `Makefile` 直接拼装一长串命令。

## 当前实现策略

这是基于现有会话信息重建的可运行版本。

- 优先保证最小闭环可跑
- 优先保证前端能读统一数据层
- 对需要重型依赖的步骤，默认提供可在本机运行的模拟/轻量路径
- agent 优先输出当前 readiness、下一步推荐命令和关键产物路径
