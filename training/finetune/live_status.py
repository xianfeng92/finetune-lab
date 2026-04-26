from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEB_PUBLIC_RUN_LIVE = ROOT / "web" / "public" / "run-live"
WEB_DIST_RUN_LIVE = ROOT / "web" / "dist" / "run-live"
VM_STAT_PAGE_RE = re.compile(r"page size of (\d+) bytes")
VM_STAT_VALUE_RE = re.compile(r"^([^:]+):\s+(\d+)\.$")


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def live_status_slug(output_dir: Path) -> str:
    outputs_root = ROOT / "outputs"
    try:
        relative = output_dir.resolve().relative_to(outputs_root.resolve())
        return relative.as_posix() + ".json"
    except ValueError:
        return f"{output_dir.name}.json"


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def live_status_targets(output_dir: Path) -> list[Path]:
    slug = live_status_slug(output_dir)
    targets = [
        output_dir / "run-live-status.json",
        WEB_PUBLIC_RUN_LIVE / slug,
    ]
    if WEB_DIST_RUN_LIVE.parent.exists():
        targets.append(WEB_DIST_RUN_LIVE / slug)
    return targets


def write_live_status(output_dir: Path, payload: dict[str, Any]) -> None:
    for target in live_status_targets(output_dir):
        write_json_atomic(target, payload)


def write_live_index(output_dir: Path, payload: dict[str, Any]) -> None:
    slug = live_status_slug(output_dir)
    index_payload = {
        "generated_at": now_iso(),
        "latest_run_id": payload.get("run_id"),
        "status": payload.get("status"),
        "updated_at": payload.get("updated_at"),
        "run_path": f"run-live/{slug}",
    }
    for base in (WEB_PUBLIC_RUN_LIVE, WEB_DIST_RUN_LIVE):
        if base.parent.exists():
            write_json_atomic(base / "index.json", index_payload)


def tail_points(points: list[dict[str, Any]], keep: int = 60) -> list[dict[str, Any]]:
    if len(points) <= keep:
        return points
    return points[-keep:]


def sample_process_metrics(pid: int) -> dict[str, Any]:
    try:
        output = subprocess.check_output(
            ["ps", "-o", "%cpu=,rss=", "-p", str(pid)],
            text=True,
        ).strip()
    except Exception:
        return {
            "process_cpu_percent": None,
            "process_memory_gb": None,
            "process_threads": None,
        }

    if not output:
        return {
            "process_cpu_percent": None,
            "process_memory_gb": None,
            "process_threads": None,
        }
    parts = output.split()
    if len(parts) < 2:
        return {
            "process_cpu_percent": None,
            "process_memory_gb": None,
            "process_threads": None,
        }
    try:
        cpu = float(parts[0])
        rss_kb = float(parts[1])
    except ValueError:
        return {
            "process_cpu_percent": None,
            "process_memory_gb": None,
            "process_threads": None,
        }
    return {
        "process_cpu_percent": round(cpu, 2),
        "process_memory_gb": round(rss_kb / (1024 * 1024), 3),
        "process_threads": None,
    }


def parse_vm_stat(raw: str) -> tuple[int, dict[str, int]]:
    page_size = 4096
    values: dict[str, int] = {}
    for line in raw.splitlines():
        if match := VM_STAT_PAGE_RE.search(line):
            page_size = int(match.group(1))
        elif match := VM_STAT_VALUE_RE.match(line.strip()):
            values[match.group(1)] = int(match.group(2))
    return page_size, values


def sample_system_memory() -> dict[str, Any]:
    if sys.platform == "darwin":
        try:
            total_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
            vm_raw = subprocess.check_output(["vm_stat"], text=True)
            page_size, values = parse_vm_stat(vm_raw)
            available_pages = (
                values.get("Pages free", 0)
                + values.get("Pages speculative", 0)
                + values.get("Pages inactive", 0)
            )
            available_bytes = available_pages * page_size
            used_bytes = max(total_bytes - available_bytes, 0)
            return {
                "system_memory_total_gb": round(total_bytes / (1024 ** 3), 3),
                "system_memory_used_gb": round(used_bytes / (1024 ** 3), 3),
                "system_memory_available_gb": round(available_bytes / (1024 ** 3), 3),
            }
        except Exception:
            return {
                "system_memory_total_gb": None,
                "system_memory_used_gb": None,
                "system_memory_available_gb": None,
            }

    if sys.platform.startswith("linux"):
        try:
            meminfo: dict[str, int] = {}
            for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
                if ":" not in line:
                    continue
                key, rest = line.split(":", 1)
                value = rest.strip().split()[0]
                meminfo[key] = int(value)
            total_kb = meminfo.get("MemTotal")
            avail_kb = meminfo.get("MemAvailable")
            if total_kb is None or avail_kb is None:
                raise ValueError("missing meminfo values")
            used_kb = max(total_kb - avail_kb, 0)
            return {
                "system_memory_total_gb": round(total_kb / (1024 ** 2), 3),
                "system_memory_used_gb": round(used_kb / (1024 ** 2), 3),
                "system_memory_available_gb": round(avail_kb / (1024 ** 2), 3),
            }
        except Exception:
            return {
                "system_memory_total_gb": None,
                "system_memory_used_gb": None,
                "system_memory_available_gb": None,
            }

    return {
        "system_memory_total_gb": None,
        "system_memory_used_gb": None,
        "system_memory_available_gb": None,
    }


def sample_system_metrics() -> dict[str, Any]:
    memory = sample_system_memory()
    try:
        load1, load5, load15 = os.getloadavg()
        load = {
            "load_average_1m": round(load1, 3),
            "load_average_5m": round(load5, 3),
            "load_average_15m": round(load15, 3),
        }
    except OSError:
        load = {
            "load_average_1m": None,
            "load_average_5m": None,
            "load_average_15m": None,
        }
    return {
        **memory,
        **load,
        "gpu_usage_percent": None,
        "gpu_live_supported": False,
    }


def build_initial_live_status(*, run_id: str, title: str, model_name: str, dataset_path: str, output_dir: Path, total_steps: int, effective_epochs: float, batch_size: int, learning_rate: float, run_plan_path: Path) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "title": title,
        "status": "starting",
        "phase": "training",
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "completed_at": None,
        "paths": {
            "output_dir": rel(output_dir),
            "local_status_path": rel(output_dir / "run-live-status.json"),
            "public_status_path": f"run-live/{live_status_slug(output_dir)}",
            "run_plan_path": rel(run_plan_path),
        },
        "plan": {
            "model_name": model_name,
            "dataset_path": dataset_path,
            "total_steps": total_steps,
            "effective_epochs": effective_epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
        },
        "progress": {
            "current_step": 0,
            "current_epoch": 0,
            "last_train_loss": None,
            "last_val_loss": None,
            "last_learning_rate": None,
            "last_trained_tokens": None,
            "last_peak_memory_gb": None,
        },
        "resources": {
            "process_cpu_percent": None,
            "process_memory_gb": None,
            "process_threads": None,
            "system_memory_total_gb": None,
            "system_memory_used_gb": None,
            "system_memory_available_gb": None,
            "load_average_1m": None,
            "load_average_5m": None,
            "load_average_15m": None,
            "gpu_usage_percent": None,
            "gpu_live_supported": False,
            "cpu_live_supported": True,
            "memory_live_supported": True,
        },
        "recent_train_points": [],
        "recent_eval_points": [],
        "recent_resource_samples": [],
        "notes": [
            "run-live-status.json 由训练 wrapper 持续刷新，用来支撑 Observatory 的半实时模式。",
            "当前版本支持 process/system CPU+memory 采样；Apple GPU usage 仍保留为 planned。",
        ],
    }
