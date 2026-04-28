# Pitfalls And Decisions

这份文档记录 W2 从 MLX LoRA 到 GGUF / llama.cpp / LiteRT-LM 的主要坑点，以及当前采用的决策。它的目标不是复述所有命令，而是把以后最容易重复踩的地方钉住。

## 1. Gemma 4 MLX Fuse Must Load The Compat Shim

问题：

`mlx_lm.fuse` 直接处理 Gemma 4 E2B 时，会遇到参数和 model class 不匹配的问题。原因是训练路径用了 `gemma4_e2b_compat.py`，而普通 fuse 路径没有加载同一套 patch。

决策：

使用仓库内 wrapper：

```bash
.venv-real-train/bin/python edge-bench/deploy/mlx/fuse.py \
  --model mlx-community/gemma-4-e2b-it-4bit \
  --adapter-path outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum-consolidation/stage4-consolidation/adapters \
  --save-path outputs/edge-bench/fused/stage4-consolidation-fp16 \
  --dequantize
```

不要直接调用裸 `mlx_lm.fuse`。

## 2. Fuse Flag Is `--dequantize`

问题：

4-bit MLX base 如果直接 fuse，会保留 4-bit 形态，下游 GGUF / LiteRT-LM 转换不适合作为 canonical fp16 中间产物。

决策：

使用 `--dequantize`。注意不是 `--de-quantize`。

## 3. `mlx_lm --export-gguf` Does Not Cover This Gemma 4 Path

问题：

Gemma 4 E2B fused HF 目录不能依赖 `mlx_lm` 自己的 GGUF export。

决策：

走 llama.cpp 的 `convert_hf_to_gguf.py`：

```bash
edge-bench/deploy/llama_cpp/convert.sh \
  outputs/edge-bench/fused/stage4-consolidation-fp16 \
  ggml-stage4
```

这会生成：

- `ggml-stage4-fp16.gguf`
- `ggml-stage4-Q4_K_M.gguf`

## 4. PyPI `gguf==0.18.0` Is Too Old

问题：

Homebrew llama.cpp 的 `convert_hf_to_gguf.py` 已经知道 Gemma 4，但 PyPI `gguf==0.18.0` 没有匹配的 `MODEL_ARCH.GEMMA4` enum。

决策：

在 `.venv-real-train` 中安装 llama.cpp master 的 `gguf-py`：

```bash
uv pip install --python .venv-real-train/bin/python \
  "gguf @ git+https://github.com/ggml-org/llama.cpp.git@master#subdirectory=gguf-py"
```

## 5. Use `llama-completion`, Not Conversation Mode

问题：

Gemma 4 chat template 使用自定义 markers，llama.cpp conversation mode / minja template path 会崩。

决策：

先用 HF `AutoTokenizer.apply_chat_template(..., tools=...)` 生成完整 prompt 文件，再调用：

```bash
llama-completion \
  -m outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf \
  -f /tmp/prompt.txt \
  -n 256 \
  --no-display-prompt \
  -no-cnv \
  --temp 0
```

`-no-cnv` 在这里是必须项。

## 6. First-Token-Out Is Not Enough

问题：

llama.cpp fused GGUF 可以跑出 first token，也能在简单 5-case smoke 里输出正确 tool-call 格式。但 strict benchmark 上安全 contract 仍然失败。

决策：

端侧 smoke 至少包含：

- 普通 `tool_call`
- `confirm`
- `reject`
- `handoff`
- `clarify`

只看 first-token-out 或 JSON validity，会错过最关键的 PolicyGateway 退化。

## 7. Q4_K_M Is Not The Root Cause

问题：

看到 Q4_K_M 上 behavior 60%、unsafe 17%，直觉上容易归因到量化。

决策：

先跑 fp16 GGUF 诊断。当前 fp16 和 Q4_K_M 对照如下：

| Metric | fp16 | Q4_K_M |
|---|---:|---:|
| `behavior_accuracy` | 87/144 | 86/144 |
| `unsafe_direct_call_rate` | 24/144 | 24/144 |
| `confirmation_contract_hit` | 0/12 | 0/12 |
| `refusal_contract_hit` | 0/12 | 0/12 |

这说明量化不是主因。

## 8. Do Not Patch `num_kv_shared_layers` Blindly

问题：

看起来可以把 `config.num_kv_shared_layers: 20` 改成 0，让 llama.cpp 读取 layers 15-34 的独立 K/V。实测失败。

原因：

这个字段在 Gemma 4 C++ runtime 里不只是 K/V sharing 开关，还影响 FFN width 解释。改成 0 后权重 shape 对不上：

```text
tensor 'blk.15.ffn_gate.weight' has wrong shape;
expected 1536, 6144, got 1536, 12288
```

决策：

把这条视为架构不兼容，不作为 metadata 修复路径。后续如果要恢复 GGUF 语义，应做 LoRA target ablation，而不是改 config。

## 9. LiteRT-LM Is Base-Only For Now

问题：

W2 目标原本包含 fused LoRA -> `.litertlm`。但当前 ai-edge-torch / LiteRT-LM 路径没有 Gemma 4 generative self-fuse 示例，官方可用路径是 `litert-community/gemma-4-E2B-it-litert-lm` base bundle。

决策：

LiteRT-LM 只作为 base-only fallback 写入报告：

- 可用于说明官方 bundle 能跑。
- 可用于说明无 tools 注入时 `unsafe_direct_call_rate=0` 是被动安全。
- 不用于声称同一 LoRA 已跨三引擎保留。

## 10. Current Path (b)

当前发布口径采用 path (b)：

- N=2 完整 LoRA 对照：MLX + llama.cpp。
- LiteRT-LM 作为 base-only 定性章节。
- Android NDK 仍是可选 W3，不阻塞博客主线。
- W5 文档和博客主轴放在 PolicyGateway 跨引擎差异，而不是三引擎性能排行榜。
