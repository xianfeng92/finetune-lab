# finetune-lab

An AI-native open-source lab for understanding data generation, fine-tuning, and tool-call behavior.

这个仓库把一条最小可学习链路收成了标准入口：

1. 生成 SFT demo 数据
2. 运行本地 smoke train 脚手架
3. 对训练产物做 post-train probe
4. 用前端实验台查看数据、run 和 probe 对比

说明：

- 默认 `smoke train` / `probe` 仍然是教学用 simulated 路径
- `probe` 现在读取 `held-out.jsonl`，不再直接复用训练 split
- 现在也提供一条 Apple Silicon / MLX LoRA 的真实小规模微调路径
- 这条真实路径默认使用 `mlx-community/gemma-4-e2b-it-4bit` 这样的 MLX-converted Gemma 4 checkpoint

## AI-native Onboarding

这个仓库的目标不是“用户自己先手工配环境”，而是：

1. 用户下载仓库后，可以直接让 Codex / Claude 接手
2. agent 先判断环境 readiness，再决定该先 setup 还是直接跑实验
3. agent 能一路把 `onboarding -> data -> train -> probe -> compare -> frontend` 讲清楚

推荐先执行：

```bash
make ai-onboarding
```

如果用户希望 agent 直接完成依赖准备：

```bash
make ai-setup
```

如果用户希望 agent 直接跑通最小教学闭环：

```bash
make ai-lab
```

可以直接把下面这段发给 Codex 或 Claude：

```text
阅读 AGENTS.md、project-context.json、docs/ai/setup.md、docs/ai/workflows.md。
先运行 make ai-onboarding 判断当前状态；如果依赖未准备好先执行 make ai-setup；
然后继续运行 make ai-lab，并在每一步告诉我当前产物、为什么要做这一步、下一步是什么。
```

## 先读这些

1. [AGENTS.md](/Users/xforg/AI_SPACE/finetune-lab/AGENTS.md)
2. [project-context.json](/Users/xforg/AI_SPACE/finetune-lab/project-context.json)
3. [docs/ai/setup.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/setup.md)
4. [docs/ai/workflows.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/workflows.md)
5. [docs/ai/gemma4-real-finetune-guide.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/gemma4-real-finetune-guide.md)

## 标准入口

```bash
make help
make ai-onboarding
make ai-setup
make ai-lab
make bootstrap-data
make data-demo
make test-data
make level1-pack
make gemma-track-pack
make env-probe
make smoke-train-mac
make probe-mac
make bootstrap-real-finetune
make real-finetune-data
make real-train-mac
make real-probe-mac
make real-single-tool-compare
make real-stage-curriculum
make real-stage-curriculum-consolidation
make real-stage-curriculum-replay
make smoke-train-mac-100
make probe-mac-100
make compare-probes
make level5-pack
make level6-demo
make web-install
make web-sync-data
make web-build
```

## 最小学习路径

```bash
make bootstrap-data
make data-demo
make test-data
make level1-pack
make gemma-track-pack
make smoke-train-mac
make probe-mac
make bootstrap-real-finetune
make real-finetune-data
make real-single-tool-compare
make real-stage-curriculum
make real-stage-curriculum-consolidation
make real-stage-curriculum-replay
make web-install
make web-build
```

## 真实微调说明

如果你更关心 Gemma 4 真实 LoRA workflow，而不是教学 smoke train，可以直接看：

- [docs/ai/gemma4-real-finetune-guide.md](/Users/xforg/AI_SPACE/finetune-lab/docs/ai/gemma4-real-finetune-guide.md)

这页会直接说明：

- 当前真实 workflow 是否已经通了
- 应该按什么顺序跑
- 真实 run 看哪些产物
- 当前验证机适合多大数据量

## 目录

```text
finetune-lab/
├── scripts/
├── data/
├── docs/
├── outputs/
├── training/
└── web/
```
