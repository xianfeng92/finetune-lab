# AI Setup

## 推荐读取顺序

1. `AGENTS.md`
2. `project-context.json`
3. `docs/ai/workflows.md`

## 推荐第一步

```bash
make ai-onboarding
```

这个 target 会生成：

- `outputs/agent/onboarding-report.json`
- `outputs/agent/onboarding-report.md`

agent 应先看这份报告，再决定是先 setup，还是直接进入实验闭环。

这份报告现在也会额外告诉 agent：

- `train.jsonl / held-out.jsonl` 是否已经生成
- 当前学习阶段推进到了哪一关
- 下一关最值得执行的标准入口

## 环境准备

### 一次性准备 Python 和前端依赖

```bash
make ai-setup
```

如果只想单独准备 Python：

```bash
make bootstrap-data
```

如果只想单独准备前端：

```bash
make web-install
```

## Agent 提示词

```text
阅读 AGENTS.md、project-context.json、docs/ai/setup.md、docs/ai/workflows.md。
不要猜目录和命令，只使用 Makefile 提供的标准入口。
先执行 make ai-onboarding 判断 readiness；
如果依赖未准备好先执行 make ai-setup；
然后继续执行 make ai-lab，并解释每一步对应的产物和教学意义。
```
