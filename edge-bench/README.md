# Edge Inference Bench

`edge-bench/` 是 `finetune-lab` 的端侧推理对照子项目：把同一个 Gemma 4 E2B 车机 tool-calling LoRA 从 MLX 训练路径推到 GGUF / llama.cpp，并用同一套 strict benchmark probe 检查 PolicyGateway 语义是否保留。

## 当前结论

W2 已完成 Mac M native baseline、MLX fuse、GGUF 转换、llama.cpp fp16 / Q4_K_M probe，以及 LiteRT-LM base-only fallback。当前主结论不是“量化损失”，而是“跨引擎架构假设不一致会静默吃掉安全语义”：

| Engine | LoRA path | Dataset | behavior_accuracy | unsafe_direct_call_rate | confirmation_contract_hit | refusal_contract_hit |
|---|---:|---:|---:|---:|---:|---:|
| MLX 4-bit | adapter | 144 strict | 144/144 | 0/144 | 12/12 | 12/12 |
| llama.cpp fp16 GGUF | fused | 144 strict | 87/144 | 24/144 | 0/12 | 0/12 |
| llama.cpp Q4_K_M GGUF | fused | 144 strict | 86/144 | 24/144 | 0/12 | 0/12 |
| LiteRT-LM | base-only | 144 strict | 12/144 | 0/144 | 0/12 | 0/12 |

关键判定：

- MLX 是训练侧 ground truth：同一 strict benchmark 下 4 维 PolicyGateway 全胜。
- llama.cpp fp16 和 Q4_K_M 几乎一致，所以不是 Q4 量化导致的行为损失。
- LiteRT-LM 当前只作为官方 base-only fallback，不计入“同一 LoRA 跨三引擎保持”的结论。
- 根因集中在 Gemma 4 的 `num_kv_shared_layers: 20`：训练侧 compat shim 让 layers 15-34 拥有独立 K/V LoRA delta，但 llama.cpp 推理侧遵守 KV-sharing，导致这些 delta 不被读取。

## 文档

- [05-benchmark-results.md](docs/05-benchmark-results.md): W2 benchmark 数据汇总、4 维雷达图、产物路径。
- [06-policygateway-cross-engine.md](docs/06-policygateway-cross-engine.md): 跨引擎 PolicyGateway 语义差异与根因分析。
- [07-pitfalls-and-decisions.md](docs/07-pitfalls-and-decisions.md): MLX fuse、GGUF、llama.cpp、LiteRT-LM 的踩坑和决策记录。
- [08-blog-draft.md](docs/08-blog-draft.md): 博客主稿草稿。

## 关键代码

- `probe/behavior_eval.py`: 4 维 PolicyGateway metric helpers。
- `probe/parse.py`: 跨引擎复用的 tool-call parser wrapper。
- `edge-bench/deploy/mlx/fuse.py`: Gemma 4 LoRA fuse 到 fp16 HF 目录。
- `edge-bench/deploy/llama_cpp/convert.sh`: fp16 HF 目录转 fp16 GGUF，再量化到 Q4_K_M。
- `edge-bench/bench/probe_llama_cpp.py`: llama.cpp strict benchmark probe。
- `edge-bench/bench/probe_litert_lm.py`: LiteRT-LM base-only strict benchmark probe。

## 本地产物

W2 本地 benchmark 结果在 `outputs/edge-bench/` 下，默认不入 git：

```text
outputs/edge-bench/
├── baselines/
│   ├── mlx-stage4-strict/
│   ├── mlx-stage4-fused-strict/
│   ├── llama_cpp-stage4-fp16-strict/
│   ├── llama_cpp-stage4-Q4_K_M-strict/
│   └── litert_lm-base-strict/
└── fused/
    └── stage4-consolidation-fp16/
```

## 最小验证

```bash
make ai-onboarding

.venv-real-train/bin/python edge-bench/bench/probe_llama_cpp.py \
  --gguf outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf \
  --tokenizer-dir outputs/edge-bench/fused/stage4-consolidation-fp16 \
  --dataset data/real-finetune/v1-gemma4-e2b-benchmark/test.jsonl \
  --run-dir /tmp/edge-bench-smoke \
  --max-samples 5
```

这条 smoke 的意义是验证 `onboarding -> data -> train -> probe -> compare -> frontend` 链路里的 probe 层已经可以被端侧引擎复用；它不替代完整 144-case benchmark。
