from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def allocate_counts(total: int, buckets: int) -> list[int]:
    base = total // buckets
    remainder = total % buckets
    return [base + (1 if index < remainder else 0) for index in range(buckets)]


def sample_replay_rows(replay_dirs: list[Path], replay_ratio: float, primary_train: list[dict]) -> tuple[list[dict], list[dict]]:
    if not replay_dirs or replay_ratio <= 0:
        return [], []

    replay_total = max(1, round(len(primary_train) * replay_ratio))
    per_dir = allocate_counts(replay_total, len(replay_dirs))

    replay_rows: list[dict] = []
    replay_meta: list[dict] = []
    seen_ids = {row["id"] for row in primary_train}
    for replay_dir, requested in zip(replay_dirs, per_dir):
        source_rows = sorted(load_jsonl(replay_dir / "train.jsonl"), key=lambda row: row["id"])
        picked = 0
        for row in source_rows:
            if row["id"] in seen_ids:
                continue
            replay_rows.append(row)
            replay_meta.append(
                {
                    "source_dir": str(replay_dir.resolve().relative_to(ROOT)),
                    "id": row["id"],
                    "category": row["category"],
                }
            )
            seen_ids.add(row["id"])
            picked += 1
            if picked >= requested:
                break
    return replay_rows, replay_meta


def build_pack(primary_dir: Path, output_dir: Path, replay_dirs: list[Path], replay_ratio: float, train_rows: list[dict], valid_rows: list[dict], test_rows: list[dict], replay_rows: list[dict]) -> dict:
    return {
        "title": "Gemma real fine-tune replay dataset pack",
        "primary_dir": str(primary_dir.resolve().relative_to(ROOT)),
        "output_dir": str(output_dir.resolve().relative_to(ROOT)),
        "replay_dirs": [str(path.resolve().relative_to(ROOT)) for path in replay_dirs],
        "replay_ratio": replay_ratio,
        "counts": {
            "train": len(train_rows),
            "valid": len(valid_rows),
            "test": len(test_rows),
            "replay_train_rows": len(replay_rows),
        },
        "categories": {
            "train": dict(Counter(row["category"] for row in train_rows)),
            "valid": dict(Counter(row["category"] for row in valid_rows)),
            "test": dict(Counter(row["category"] for row in test_rows)),
            "replay_train": dict(Counter(row["category"] for row in replay_rows)),
        },
        "notes": [
            "valid/test remain from the primary stage so stage-local eval stays focused.",
            "train rows append a deterministic replay slice from earlier stages.",
            "replay_ratio is measured against the primary train split size.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-dir", type=Path, required=True)
    parser.add_argument("--replay-dir", action="append", type=Path, default=[])
    parser.add_argument("--replay-ratio", type=float, default=0.25)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pack-output", type=Path, required=True)
    args = parser.parse_args()

    primary_train = load_jsonl(args.primary_dir / "train.jsonl")
    primary_valid = load_jsonl(args.primary_dir / "valid.jsonl")
    primary_test = load_jsonl(args.primary_dir / "test.jsonl")
    replay_rows, replay_meta = sample_replay_rows(args.replay_dir, args.replay_ratio, primary_train)
    merged_train = primary_train + replay_rows

    write_jsonl(args.output_dir / "train.jsonl", merged_train)
    write_jsonl(args.output_dir / "valid.jsonl", primary_valid)
    write_jsonl(args.output_dir / "test.jsonl", primary_test)

    pack = build_pack(
        args.primary_dir,
        args.output_dir,
        args.replay_dir,
        args.replay_ratio,
        merged_train,
        primary_valid,
        primary_test,
        replay_rows,
    )
    pack["replay_samples"] = replay_meta
    args.pack_output.parent.mkdir(parents=True, exist_ok=True)
    args.pack_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pack, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
