from __future__ import annotations

from pathlib import Path

from training.finetune.live_status import build_initial_live_status, parse_vm_stat


def test_parse_vm_stat_reads_page_size_and_counters() -> None:
    raw = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                               128.
Pages active:                            4096.
Pages inactive:                          2048.
Pages speculative:                        256.
"""
    page_size, values = parse_vm_stat(raw)
    assert page_size == 16384
    assert values["Pages free"] == 128
    assert values["Pages inactive"] == 2048
    assert values["Pages speculative"] == 256


def test_initial_live_status_uses_run_live_paths() -> None:
    status = build_initial_live_status(
        run_id="demo-run",
        title="demo",
        model_name="mlx-community/gemma-4-e2b-it-4bit",
        dataset_path="data/real-finetune/demo/train.jsonl",
        output_dir=Path("/Users/xforg/AI_SPACE/finetune-lab/outputs/demo-run"),
        total_steps=12,
        effective_epochs=1.5,
        batch_size=1,
        learning_rate=1e-5,
        run_plan_path=Path("/Users/xforg/AI_SPACE/finetune-lab/outputs/demo-run/run-plan.json"),
    )
    assert status["paths"]["public_status_path"] == "run-live/demo-run.json"
    assert status["resources"]["cpu_live_supported"] is True
    assert status["resources"]["gpu_live_supported"] is False
