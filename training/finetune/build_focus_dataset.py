from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def matches_focus(row: dict, categories: set[str], prompts: set[str]) -> bool:
    if categories and row.get("category") in categories:
        return True
    if prompts and row.get("prompt_user") in prompts:
        return True
    return False


def duplicate_rows(rows: list[dict], categories: set[str], prompts: set[str], repeat_factor: int) -> tuple[list[dict], list[dict]]:
    if repeat_factor < 2:
        return rows, []

    extra_rows: list[dict] = []
    for row in rows:
        if not matches_focus(row, categories, prompts):
            continue
        for repeat_index in range(1, repeat_factor):
            duplicate = copy.deepcopy(row)
            duplicate["id"] = f"{row['id']}::focus-{repeat_index}"
            duplicate["source_id"] = row["id"]
            extra_rows.append(duplicate)
    return rows + extra_rows, extra_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pack-output", type=Path, required=True)
    parser.add_argument("--focus-category", action="append", default=[])
    parser.add_argument("--focus-prompt", action="append", default=[])
    parser.add_argument("--repeat-factor", type=int, default=3)
    args = parser.parse_args()

    train_rows = load_jsonl(args.source_dir / "train.jsonl")
    valid_rows = load_jsonl(args.source_dir / "valid.jsonl")
    test_rows = load_jsonl(args.source_dir / "test.jsonl")
    focus_categories = set(args.focus_category)
    focus_prompts = set(args.focus_prompt)

    merged_train, extra_rows = duplicate_rows(train_rows, focus_categories, focus_prompts, args.repeat_factor)

    write_jsonl(args.output_dir / "train.jsonl", merged_train)
    write_jsonl(args.output_dir / "valid.jsonl", valid_rows)
    write_jsonl(args.output_dir / "test.jsonl", test_rows)

    pack = {
        "title": "Gemma real fine-tune focus dataset pack",
        "source_dir": rel(args.source_dir),
        "output_dir": rel(args.output_dir),
        "focus_categories": sorted(focus_categories),
        "focus_prompts": sorted(focus_prompts),
        "repeat_factor": args.repeat_factor,
        "counts": {
            "train": len(merged_train),
            "valid": len(valid_rows),
            "test": len(test_rows),
            "focused_duplicates": len(extra_rows),
        },
        "categories": {
            "train": dict(Counter(row["category"] for row in merged_train)),
            "focused_duplicates": dict(Counter(row["category"] for row in extra_rows)),
        },
        "focus_samples": [
            {
                "id": row["id"],
                "source_id": row.get("source_id"),
                "category": row["category"],
                "prompt_user": row.get("prompt_user"),
            }
            for row in extra_rows[:20]
        ],
        "notes": [
            "This dataset keeps valid/test unchanged and only duplicates targeted train rows.",
            "Use it after a broader run when you want to patch specific behavior tails without rewriting the whole curriculum.",
        ],
    }
    args.pack_output.parent.mkdir(parents=True, exist_ok=True)
    args.pack_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pack, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
