"""Fuse Gemma 4 LoRA adapter into base model with finetune-lab compat shim.

mlx_lm 0.31.3's stock Gemma4 model class implements KV-sharing per
config.num_kv_shared_layers. HF safetensors ship redundant k/v weights for
those layers (round-trip safety), and finetune-lab trains LoRA on the
all-independent-KV interpretation via training/finetune/mlx_compat/
gemma4_e2b_compat.py. The two interpretations are mutually incompatible:
running mlx_lm.fuse stock raises "Received N parameters not in model".

This script imports the compat shim before mlx_lm so the patched (all-KV)
class is what fuses + saves, keeping the fused output consumable by
finetune-lab's mlx_real_probe.py (which imports the same shim).

Usage:
    .venv-real-train/bin/python edge-bench/deploy/mlx/fuse.py \\
        --model mlx-community/gemma-4-e2b-it-4bit \\
        --adapter-path outputs/.../stage4-consolidation/adapters \\
        --save-path outputs/edge-bench/fused/stage4-consolidation-fp16 \\
        --dequantize
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MLX_COMPAT_DIR = REPO_ROOT / "training" / "finetune" / "mlx_compat"
if str(MLX_COMPAT_DIR) not in sys.path:
    sys.path.insert(0, str(MLX_COMPAT_DIR))

import gemma4_e2b_compat  # noqa: E402,F401  -- applies patch on import

from mlx.utils import tree_unflatten  # noqa: E402

from mlx_lm.utils import (  # noqa: E402
    _download,
    dequantize_model,
    load_adapters,
    load_config,
    load_model,
    load_tokenizer,
    save,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--model", required=True, help="HF repo id or local path")
    parser.add_argument("--adapter-path", required=True, help="Path to LoRA adapter dir")
    parser.add_argument("--save-path", required=True, help="Where to save fused model")
    parser.add_argument("--dequantize", action="store_true", help="Dequantize 4-bit base to fp16")
    args = parser.parse_args()

    print(f"Resolving model path for {args.model}")
    model_path = _download(args.model)
    config = load_config(model_path)

    print("Loading model with gemma4_e2b_compat shim (all-independent KV)")
    model, _ = load_model(model_path, lazy=False, strict=True, model_config=config)

    print(f"Applying LoRA adapter from {args.adapter_path}")
    model = load_adapters(model, args.adapter_path)
    tokenizer = load_tokenizer(model_path, eos_token_ids=config.get("eos_token_id"))

    fused_linears = [
        (n, m.fuse(dequantize=args.dequantize))
        for n, m in model.named_modules()
        if hasattr(m, "fuse")
    ]
    if fused_linears:
        model.update_modules(tree_unflatten(fused_linears))

    if args.dequantize:
        print("Dequantizing model")
        model = dequantize_model(model)
        config.pop("quantization", None)
        config.pop("quantization_config", None)

    save_path = Path(args.save_path)
    print(f"Saving fused model to {save_path}")
    save(save_path, args.model, model, tokenizer, config, donate_model=False)
    print("Done.")


if __name__ == "__main__":
    main()
