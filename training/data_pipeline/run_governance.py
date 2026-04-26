"""CLI: write dataset-card.md + redaction-report.md for every dataset under data/.

Usage:
    python training/data_pipeline/run_governance.py --root /path/to/finetune-lab

Walks data/sft/v1-* and data/real-finetune/v1-* (recursively for the latter), runs
governance.governance_pass() over the primary jsonl, and prints a per-dataset summary.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import governance as g  # noqa: E402


def discover_datasets(repo_root: Path) -> list[tuple[Path, str]]:
    """Return (dataset_dir, kind) tuples. kind ∈ {'sft', 'real-finetune'}."""
    datasets: list[tuple[Path, str]] = []
    sft_root = repo_root / "data" / "sft"
    if sft_root.exists():
        for entry in sorted(sft_root.iterdir()):
            if entry.is_dir() and (entry / "samples.jsonl").exists():
                datasets.append((entry, "sft"))
    real_root = repo_root / "data" / "real-finetune"
    if real_root.exists():
        # real-finetune holds either flat datasets (train.jsonl directly under v1-*) or
        # curriculum stages (v1-*/<stage>/train.jsonl).
        for top in sorted(real_root.iterdir()):
            if not top.is_dir():
                continue
            if (top / "train.jsonl").exists():
                datasets.append((top, "real-finetune"))
            else:
                for stage in sorted(top.iterdir()):
                    if stage.is_dir() and (stage / "train.jsonl").exists():
                        datasets.append((stage, "real-finetune"))
    return datasets


def manifest_for(dataset_dir: Path, kind: str) -> g.DatasetCardManifest:
    name = dataset_dir.name
    parent = dataset_dir.parent.name
    if parent != ("sft" if kind == "sft" else "real-finetune"):
        # nested curriculum stage — name like "v1-...-large-stage-curriculum/stage1-single-tool"
        name = f"{parent}/{name}"
    return g.DatasetCardManifest(
        name=name,
        version=read_version_hint(dataset_dir),
        generator=infer_generator(dataset_dir),
        license="internal-research-only",
        sensitivity="low",
        description=infer_description(name, kind),
        provenance=infer_provenance(dataset_dir, kind),
        known_limitations=[
            "合成数据无法覆盖真实方言、口语化、跨说法",
            "上线前必须用真实样本回归",
        ],
    )


def read_version_hint(dataset_dir: Path) -> str:
    name = dataset_dir.name
    if name.startswith("v"):
        return name.split("-")[0]
    return "1.0"


def infer_generator(dataset_dir: Path) -> str:
    """Best-effort inference from dataset_summary.json or first sample's meta."""
    summary_path = dataset_dir / "dataset_summary.json"
    if summary_path.exists():
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            generators = data.get("generator_counts") or []
            if generators:
                top = max(generators, key=lambda x: x.get("count", 0))
                return f"synthetic-{top.get('model', top.get('generator', 'unknown'))}"
        except (json.JSONDecodeError, AttributeError):
            pass
    samples_path = dataset_dir / "samples.jsonl"
    if not samples_path.exists():
        samples_path = dataset_dir / "train.jsonl"
    if samples_path.exists():
        with samples_path.open("r", encoding="utf-8") as f:
            first = f.readline().strip()
            if first:
                try:
                    rec = json.loads(first)
                    gen = (rec.get("meta") or {}).get("generator_model")
                    if gen:
                        return f"synthetic-{gen}"
                except json.JSONDecodeError:
                    pass
    return "synthetic-unknown"


def infer_description(name: str, kind: str) -> str:
    if kind == "sft":
        return (
            f"SFT 数据集 `{name}`：合成的车控 tool-call 样本，覆盖 single-tool / multi-tool-chain / "
            "cross-domain-multi-tool / reroute_to_meta / fallback / proactive 等任务结构。"
            "用于 LoRA 微调教学，不可作为真实车机训练集。"
        )
    return (
        f"real-finetune 数据集 `{name}`：以 openai-chat-with-tools 格式存放的训练 / valid / test split。"
        "由 SFT 数据经 build_real_finetune_dataset 转换生成，承接 mlx-lm.lora 真实训练。"
    )


def infer_provenance(dataset_dir: Path, kind: str) -> list[str]:
    items = []
    if kind == "sft":
        items.append("生成器：training/data_pipeline/pipeline.py + schema_sampler + generator")
        items.append("种子：seed-anchor schema v1（合成数据，不含真实用户对话）")
    else:
        items.append("来源：training/finetune/build_real_finetune_dataset.py")
        items.append("上游：data/sft/<对应 SFT 数据集>")
    items.append(f"数据目录：{dataset_dir.relative_to(dataset_dir.parents[2]) if len(dataset_dir.parents) >= 3 else dataset_dir}")
    return items


def primary_jsonl(dataset_dir: Path, kind: str) -> str:
    if kind == "sft":
        return "samples.jsonl"
    return "train.jsonl"


def splits_for(dataset_dir: Path, kind: str) -> dict[str, str]:
    if kind == "sft":
        out: dict[str, str] = {}
        if (dataset_dir / "samples.jsonl").exists():
            out["samples"] = "samples.jsonl"
        if (dataset_dir / "train.jsonl").exists():
            out["train"] = "train.jsonl"
        if (dataset_dir / "held-out.jsonl").exists():
            out["held-out"] = "held-out.jsonl"
        return out
    out = {}
    for label in ("train", "valid", "test"):
        if (dataset_dir / f"{label}.jsonl").exists():
            out[label] = f"{label}.jsonl"
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--dataset", type=Path, default=None, help="single dataset dir; otherwise scan all")
    args = parser.parse_args()
    repo_root: Path = args.root
    targets: list[tuple[Path, str]]
    if args.dataset:
        kind = "sft" if "sft" in args.dataset.parts else "real-finetune"
        targets = [(args.dataset, kind)]
    else:
        targets = discover_datasets(repo_root)

    print(f"Scanning {len(targets)} dataset(s) under {repo_root}")
    rows = []
    for dataset_dir, kind in targets:
        manifest = manifest_for(dataset_dir, kind)
        result = g.governance_pass(
            dataset_dir,
            manifest,
            primary_jsonl=primary_jsonl(dataset_dir, kind),
            splits_jsonl=splits_for(dataset_dir, kind),
        )
        rows.append(result)
        marker = "✓" if result["records_redacted"] == 0 else "⚠"
        print(
            f"  {marker} {result['dataset']}  scanned={result['records_scanned']}  "
            f"redacted={result['records_redacted']}  matches={result['match_counts']}"
        )

    total_redacted = sum(r["records_redacted"] for r in rows)
    print(f"\nDone. {len(rows)} dataset(s); total records_redacted = {total_redacted}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
