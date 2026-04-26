from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MLX_COMPAT_DIR = ROOT / "training" / "finetune" / "mlx_compat"

if str(MLX_COMPAT_DIR) not in sys.path:
    sys.path.insert(0, str(MLX_COMPAT_DIR))

import gemma4_e2b_compat  # noqa: F401
from mlx_lm.lora import main


if __name__ == "__main__":
    main()
