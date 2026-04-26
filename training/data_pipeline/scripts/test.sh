#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PYTHON_BIN="$ROOT/.venv-data/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m pytest "$ROOT/training/data_pipeline/tests" "$ROOT/training/finetune/tests"
"$PYTHON_BIN" "$ROOT/training/data_pipeline/pipeline.py" --output-dir "$ROOT/data/sft/v1-seed-anchor-demo"
