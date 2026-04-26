from __future__ import annotations

import json
from pathlib import Path


RUNS = [
    ("20-step", Path("outputs/gemma4-e2b-mlx-demo-unsloth-vlm/inference-probe-results.json")),
    ("100-step", Path("outputs/gemma4-e2b-mlx-demo-unsloth-vlm-100step/inference-probe-results.json")),
]


def main() -> None:
    for label, path in RUNS:
        rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        summary = {
            "exact_name_match": sum(1 for row in rows if row["exact_name_match"]),
            "any_expected_name_hit": sum(1 for row in rows if set(row["predicted_names"]) & set(row["expected_names"])),
            "parsed_json": sum(1 for row in rows if row["parsed_output"] is not None),
            "tool_signal": sum(1 for row in rows if row["has_tool_calls_signal"]),
            "total": len(rows),
        }
        print(label, summary)


if __name__ == "__main__":
    main()
