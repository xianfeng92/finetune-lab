#!/usr/bin/env bash
# Convert finetune-lab MLX-fused fp16 dir → llama.cpp GGUF (fp16 + Q4_K_M).
#
# Inputs:
#   $1 = fused dir (output of edge-bench/deploy/mlx/fuse.py --dequantize)
#   $2 = output base name without extension (e.g., ggml-stage4)
# Outputs (under $1):
#   <basename>-fp16.gguf      ~9 GB
#   <basename>-Q4_K_M.gguf    ~3 GB  (Android emulator + Mac M baseline)
#
# Prereqs (one-time):
#   brew install llama.cpp                    # convert_hf_to_gguf.py + llama-quantize
#   uv pip install --python .venv-real-train/bin/python torch \
#       "gguf @ git+https://github.com/ggml-org/llama.cpp.git@master#subdirectory=gguf-py"
#   # NOTE: pypi gguf==0.18.0 lacks MODEL_ARCH.GEMMA4. Pin gguf-py from
#   # llama.cpp master to match the convert_hf_to_gguf.py shipped by Homebrew.
#
# Why these specific args:
#   --outtype f16  -> downstream quantize chooses Q4_K_M; fp16 is the
#                     mid-step. bf16 would cost 2x storage with no quality
#                     gain at this stage.
#   Q4_K_M         -> Spec §8 picks this for Android emulator (~3 GB fits 8 GB
#                     emulator RAM with headroom for KV cache). Mac native
#                     baseline uses the same to keep cross-device data
#                     comparable.

set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "usage: $0 <fused-fp16-dir> <basename>" >&2
    echo "  e.g. $0 outputs/edge-bench/fused/stage4-consolidation-fp16 ggml-stage4" >&2
    exit 1
fi

FUSED_DIR="$1"
BASENAME="$2"
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PYTHON="${REPO_ROOT}/.venv-real-train/bin/python"
CONVERT_SCRIPT="$(brew --prefix llama.cpp 2>/dev/null || echo /opt/homebrew/Cellar/llama.cpp/8880)/bin/convert_hf_to_gguf.py"

if [ ! -x "$PYTHON" ]; then
    echo "Error: $PYTHON not found. Run from finetune-lab repo root." >&2
    exit 1
fi
if [ ! -f "$CONVERT_SCRIPT" ]; then
    echo "Error: convert_hf_to_gguf.py not found at $CONVERT_SCRIPT. Run 'brew install llama.cpp'." >&2
    exit 1
fi

FP16_OUT="${FUSED_DIR}/${BASENAME}-fp16.gguf"
Q4_OUT="${FUSED_DIR}/${BASENAME}-Q4_K_M.gguf"

echo "== Step 1/2: HF safetensors -> fp16 GGUF =="
echo "   src: $FUSED_DIR"
echo "   dst: $FP16_OUT"
"$PYTHON" "$CONVERT_SCRIPT" "$FUSED_DIR" --outfile "$FP16_OUT" --outtype f16

echo "== Step 2/2: fp16 GGUF -> Q4_K_M GGUF =="
echo "   src: $FP16_OUT"
echo "   dst: $Q4_OUT"
llama-quantize "$FP16_OUT" "$Q4_OUT" Q4_K_M

echo "== Done =="
echo "fp16 size:    $(du -h "$FP16_OUT" | cut -f1)"
echo "Q4_K_M size:  $(du -h "$Q4_OUT"  | cut -f1)"
echo
echo "Smoke (chat template MUST be applied; -no-cnv is REQUIRED, otherwise"
echo "llama-completion auto-conversation mode crashes on the embedded"
echo "Gemma 4 minja-incompatible template):"
echo
echo "  python -c \"from transformers import AutoTokenizer; \\"
echo "    t=AutoTokenizer.from_pretrained('$FUSED_DIR'); \\"
echo "    open('/tmp/p.txt','w').write(t.apply_chat_template([{'role':'user','content':'hello'}], add_generation_prompt=True, tokenize=False))\""
echo "  llama-completion -m $Q4_OUT -f /tmp/p.txt -n 64 --no-display-prompt -no-cnv"
