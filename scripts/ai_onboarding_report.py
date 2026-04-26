from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "agent"
REPORT_JSON = OUTPUT_DIR / "onboarding-report.json"
REPORT_MD = OUTPUT_DIR / "onboarding-report.md"
PROJECT_CONTEXT_PATH = ROOT / "project-context.json"
DATA_VENV_PYTHON = ROOT / ".venv-data" / "bin" / "python"
REAL_TRAIN_VENV_PYTHON = ROOT / ".venv-real-train" / "bin" / "python"
REAL_TRAIN_MLX_LORA = ROOT / ".venv-real-train" / "bin" / "mlx_lm.lora"
WEB_NODE_MODULES = ROOT / "web" / "node_modules"
DATASET_PATH = ROOT / "data" / "sft" / "v1-seed-anchor-demo" / "samples.jsonl"
TRAIN_DATASET_PATH = ROOT / "data" / "sft" / "v1-seed-anchor-demo" / "train.jsonl"
HELD_OUT_DATASET_PATH = ROOT / "data" / "sft" / "v1-seed-anchor-demo" / "held-out.jsonl"
VALIDATION_REPORT_PATH = ROOT / "data" / "sft" / "v1-seed-anchor-demo" / "validation_report.md"
REAL_FT_DATA_DIR = ROOT / "data" / "real-finetune" / "v1-gemma4-e2b-toolcall-demo"
REAL_FT_TRAIN_PATH = REAL_FT_DATA_DIR / "train.jsonl"
REAL_FT_VALID_PATH = REAL_FT_DATA_DIR / "valid.jsonl"
REAL_FT_TEST_PATH = REAL_FT_DATA_DIR / "test.jsonl"
REAL_FT_PACK_PATH = ROOT / "outputs" / "real" / "real-finetune-dataset-pack.json"
RUN_MANIFEST_PATH = ROOT / "outputs" / "gemma4-e2b-mlx-demo-unsloth-vlm" / "run-manifest.json"
PROBE_RESULTS_PATH = ROOT / "outputs" / "gemma4-e2b-mlx-demo-unsloth-vlm" / "inference-probe-results.json"
REAL_RUN_MANIFEST_PATH = ROOT / "outputs" / "gemma4-e2b-real-mlx-lora-demo" / "run-manifest.json"
REAL_PROBE_RESULTS_PATH = ROOT / "outputs" / "gemma4-e2b-real-mlx-lora-demo" / "inference-probe-results.json"
LEVEL1_TASK_PACK_PATH = ROOT / "outputs" / "level1" / "task-framing-pack.json"
LEVEL1_BASELINE_PACK_PATH = ROOT / "outputs" / "level1" / "baseline-eval-pack.json"
GEMMA_TRACK_PACK_PATH = ROOT / "outputs" / "gemma" / "base-vs-instruct-pack.json"
LEVEL5_TOOL_PACK_PATH = ROOT / "outputs" / "level5" / "tool-routing-dataset-pack.json"
LEVEL5_STRUCTURED_PACK_PATH = ROOT / "outputs" / "level5" / "structured-output-probe-pack.json"
LEVEL6_PREFERENCE_PACK_PATH = ROOT / "outputs" / "level6" / "preference-dataset-pack.json"
LEVEL6_RUBRIC_PATH = ROOT / "outputs" / "level6" / "scale-up-rubric.json"
LEVEL6_SCALE_COMPARE_PATH = ROOT / "outputs" / "level6" / "gemma-scale-up-compare.json"
WEB_DIST_PATH = ROOT / "web" / "dist" / "index.html"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def command_version(command: str, args: list[str] | None = None) -> str | None:
    if shutil.which(command) is None:
        return None
    result = subprocess.run(
        [command, *(args or ["--version"])],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0] if output else None


def status_item(
    item_id: str,
    label: str,
    ready: bool,
    detail: str,
    *,
    fix_command: str | None = None,
    artifact_path: str | None = None,
) -> dict:
    payload = {
        "id": item_id,
        "label": label,
        "status": "ready" if ready else "missing",
        "detail": detail,
    }
    if fix_command:
        payload["fix_command"] = fix_command
    if artifact_path:
        payload["artifact_path"] = artifact_path
    return payload


def stage_item(stage_id: str, title: str, ready_count: int, total_count: int, detail: str, command: str, artifacts: list[str]) -> dict:
    if ready_count == total_count:
        status = "ready"
    elif ready_count == 0:
        status = "missing"
    else:
        status = "partial"
    return {
        "id": stage_id,
        "title": title,
        "status": status,
        "ready_count": ready_count,
        "total_count": total_count,
        "detail": detail,
        "command": command,
        "artifacts": artifacts,
    }


def build_stage_readiness() -> list[dict]:
    return [
        stage_item(
            "level1",
            "Level 1 baseline pack",
            sum(path.exists() for path in [LEVEL1_TASK_PACK_PATH, LEVEL1_BASELINE_PACK_PATH]),
            2,
            "定义任务 framing、failure buckets 和 baseline held-out case。",
            "make level1-pack",
            [
                "outputs/level1/task-framing-pack.json",
                "outputs/level1/baseline-eval-pack.json",
            ],
        ),
        stage_item(
            "data",
            "Level 2 data split",
            sum(path.exists() for path in [DATASET_PATH, TRAIN_DATASET_PATH, HELD_OUT_DATASET_PATH, VALIDATION_REPORT_PATH]),
            4,
            "既保留全集样本，也显式区分 train / held-out，保证 probe 不回看训练集。",
            "make data-demo && make test-data",
            [
                "data/sft/v1-seed-anchor-demo/samples.jsonl",
                "data/sft/v1-seed-anchor-demo/train.jsonl",
                "data/sft/v1-seed-anchor-demo/held-out.jsonl",
                "data/sft/v1-seed-anchor-demo/validation_report.md",
            ],
        ),
        stage_item(
            "gemma",
            "Gemma base-vs-instruct pack",
            int(GEMMA_TRACK_PACK_PATH.exists()),
            1,
            "把 `google/gemma-4-E2B` 和 `google/gemma-4-E2B-it` 的教学角色显式化。",
            "make gemma-track-pack",
            ["outputs/gemma/base-vs-instruct-pack.json"],
        ),
        stage_item(
            "train_probe",
            "Level 3-4 smoke train + held-out probe",
            sum(path.exists() for path in [RUN_MANIFEST_PATH, PROBE_RESULTS_PATH]),
            2,
            "生成 simulated smoke run，并在 held-out split 上做 probe。",
            "make smoke-train-mac && make probe-mac",
            [
                "outputs/gemma4-e2b-mlx-demo-unsloth-vlm/run-manifest.json",
                "outputs/gemma4-e2b-mlx-demo-unsloth-vlm/inference-probe-results.json",
            ],
        ),
        stage_item(
            "real_train",
            "Real MLX LoRA mini fine-tune",
            sum(
                path.exists()
                for path in [
                    REAL_TRAIN_VENV_PYTHON,
                    REAL_FT_TRAIN_PATH,
                    REAL_FT_VALID_PATH,
                    REAL_FT_TEST_PATH,
                    REAL_RUN_MANIFEST_PATH,
                    REAL_PROBE_RESULTS_PATH,
                ]
            ),
            6,
            "把教学数据转换成 MLX chat+tools 格式，并在 Apple Silicon 上跑真实 LoRA update 与 best-effort probe。",
            "make bootstrap-real-finetune && make real-finetune-data && make real-train-mac && make real-probe-mac",
            [
                ".venv-real-train/bin/python",
                "data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl",
                "data/real-finetune/v1-gemma4-e2b-toolcall-demo/valid.jsonl",
                "data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl",
                "outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json",
                "outputs/gemma4-e2b-real-mlx-lora-demo/inference-probe-results.json",
            ],
        ),
        stage_item(
            "level5",
            "Level 5 structured outputs pack",
            sum(path.exists() for path in [LEVEL5_TOOL_PACK_PATH, LEVEL5_STRUCTURED_PACK_PATH]),
            2,
            "把 tool-routing 和 structured outputs 单独聚合成教学专题。",
            "make level5-pack",
            [
                "outputs/level5/tool-routing-dataset-pack.json",
                "outputs/level5/structured-output-probe-pack.json",
            ],
        ),
        stage_item(
            "level6",
            "Level 6 preference + scale-up rubric",
            sum(path.exists() for path in [LEVEL6_PREFERENCE_PACK_PATH, LEVEL6_RUBRIC_PATH, LEVEL6_SCALE_COMPARE_PATH]),
            3,
            "把 preference pair、rubric 和 scale-up compare 串成更真实的后训练解释层。",
            "make level6-demo",
            [
                "outputs/level6/preference-dataset-pack.json",
                "outputs/level6/scale-up-rubric.json",
                "outputs/level6/gemma-scale-up-compare.json",
            ],
        ),
        stage_item(
            "frontend",
            "Frontend teaching lab",
            int(WEB_DIST_PATH.exists()),
            1,
            "把 onboarding、dataset、run、probe 和 roadmap 同步到统一前端数据层。",
            "make web-build",
            ["web/dist/index.html"],
        ),
    ]


def learning_status(stage_readiness: list[dict]) -> dict:
    completed = [stage["id"] for stage in stage_readiness if stage["status"] == "ready"]
    next_stage = next((stage for stage in stage_readiness if stage["status"] != "ready"), None)
    return {
        "completed_stage_ids": completed,
        "completed_stage_count": len(completed),
        "total_stage_count": len(stage_readiness),
        "next_stage": {
            "id": next_stage["id"],
            "title": next_stage["title"],
            "command": next_stage["command"],
        } if next_stage else None,
    }


def recommended_steps(checks: list[dict], stage_readiness: list[dict]) -> list[dict]:
    missing_ids = {check["id"] for check in checks if check["status"] != "ready"}
    steps: list[dict] = []
    if {"python_venv", "web_dependencies"} & missing_ids:
        steps.append(
            {
                "title": "Setup workspace dependencies",
                "command": "make ai-setup",
                "reason": "先把 Python venv 和前端依赖准备好，再让 agent 接着跑数据和训练。",
            }
        )
    if "demo_dataset" in missing_ids:
        steps.append(
            {
                "title": "Generate demo dataset",
                "command": "make data-demo",
                "reason": "训练和前端教学页面都依赖 demo SFT 数据集。",
            }
        )
    if "dataset_split" in missing_ids:
        steps.append(
            {
                "title": "Refresh train / held-out split",
                "command": "make data-demo",
                "reason": "重新生成 `train.jsonl` 和 `held-out.jsonl`，避免 probe 继续直接回看训练样本。",
            }
        )
    if "validation_report" in missing_ids:
        steps.append(
            {
                "title": "Validate dataset",
                "command": "make test-data",
                "reason": "让 agent 在进入 smoke train 之前先确认数据 pipeline 正常。",
            }
        )
    if "smoke_run" in missing_ids:
        steps.append(
            {
                "title": "Run smoke fine-tune",
                "command": "make smoke-train-mac",
                "reason": "生成最小可解释的 run manifest、metrics 和 adapter 产物。",
            }
        )
    if "probe_results" in missing_ids:
        steps.append(
            {
                "title": "Generate probe results",
                "command": "make probe-mac",
                "reason": "probe 是前端教学链路里解释微调效果的关键输入。",
            }
        )
    if next((stage for stage in stage_readiness if stage["id"] == "real_train" and stage["status"] != "ready"), None):
        steps.append(
            {
                "title": "Advance real MLX LoRA workflow",
                "command": "make bootstrap-real-finetune && make real-finetune-data && make real-train-mac && make real-probe-mac",
                "reason": "如果当前机器是 Apple Silicon，现在已经可以从教学模拟链路升级到真实小规模 LoRA 更新路径。",
            }
        )
    if "web_lab" in missing_ids:
        steps.append(
            {
                "title": "Build the teaching frontend",
                "command": "make web-build",
                "reason": "构建完成后，用户和 agent 可以直接在前端里读完整条实验链路。",
            }
        )
    if not missing_ids:
        next_stage = next((stage for stage in stage_readiness if stage["status"] != "ready"), None)
        if next_stage:
            steps.append(
                {
                    "title": f"Advance {next_stage['title']}",
                    "command": next_stage["command"],
                    "reason": f"环境已就绪，下一步最值得补的是 {next_stage['title']}。",
                }
            )
    if not steps:
        steps.append(
            {
                "title": "Refresh the full teaching loop",
                "command": "make ai-lab",
                "reason": "当前仓库已经 ready，可以让 agent 直接刷新一遍最小教学闭环。",
            }
        )
    return steps


def render_markdown(report: dict) -> str:
    lines = [
        "# AI Onboarding Report",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- repo_root: `{report['repo']['root']}`",
        f"- overall_status: {report['overall_status']}",
        "",
        "## Machine",
        "",
        f"- platform: {report['machine']['platform']}",
        f"- machine: {report['machine']['machine']}",
        f"- python: {report['machine']['python']}",
        f"- node: {report['machine']['node'] or 'missing'}",
        f"- npm: {report['machine']['npm'] or 'missing'}",
        "",
        "## Readiness",
        "",
    ]
    for check in report["readiness"]:
        detail = f"{check['label']} [{check['status']}]: {check['detail']}"
        if "fix_command" in check:
            detail += f" | fix: `{check['fix_command']}`"
        lines.append(f"- {detail}")
    lines.extend(["", "## Learning Progress", ""])
    lines.append(
        f"- completed: {report['learning_progress']['completed_stage_count']}/{report['learning_progress']['total_stage_count']}"
    )
    if report["learning_progress"]["next_stage"]:
        lines.append(
            f"- next_stage: {report['learning_progress']['next_stage']['title']} (`{report['learning_progress']['next_stage']['command']}`)"
        )
    for stage in report["stage_readiness"]:
        lines.append(
            f"- {stage['title']} [{stage['status']} {stage['ready_count']}/{stage['total_count']}]: {stage['detail']}"
        )
    lines.extend(["", "## Next Steps", ""])
    for step in report["next_steps"]:
        lines.append(f"- `{step['command']}`: {step['reason']}")
    lines.extend(["", "## Agent Prompts", ""])
    for prompt in report["agent_prompts"]:
        lines.extend(
            [
                f"### {prompt['title']}",
                "",
                "```text",
                prompt["prompt"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    project_context = read_json(PROJECT_CONTEXT_PATH)
    generated_at = datetime.now(timezone.utc).isoformat()

    checks = [
        status_item(
            "python_venv",
            "Python data env",
            DATA_VENV_PYTHON.exists(),
            "`.venv-data/bin/python` 已存在，可直接用于数据 pipeline。" if DATA_VENV_PYTHON.exists() else "还没有数据虚拟环境，agent 应先执行 `make ai-setup`。",
            fix_command="make ai-setup",
            artifact_path=".venv-data/bin/python",
        ),
        status_item(
            "web_dependencies",
            "Frontend dependencies",
            WEB_NODE_MODULES.exists(),
            "`web/node_modules/` 已存在，可直接构建前端。" if WEB_NODE_MODULES.exists() else "前端依赖还没安装，IAB 和本地 dev 都会缺资源。",
            fix_command="make ai-setup",
            artifact_path="web/node_modules",
        ),
        status_item(
            "demo_dataset",
            "Demo dataset",
            DATASET_PATH.exists(),
            "`samples.jsonl` 已存在，可直接进入 smoke train。" if DATASET_PATH.exists() else "还没有 demo SFT 数据集，训练链路还不能继续。",
            fix_command="make data-demo",
            artifact_path="data/sft/v1-seed-anchor-demo/samples.jsonl",
        ),
        status_item(
            "dataset_split",
            "Train / held-out split",
            TRAIN_DATASET_PATH.exists() and HELD_OUT_DATASET_PATH.exists(),
            "`train.jsonl` 和 `held-out.jsonl` 已存在，probe 不会直接复用训练集。"
            if TRAIN_DATASET_PATH.exists() and HELD_OUT_DATASET_PATH.exists()
            else "还缺显式 train / held-out split，probe 暂时还不能算真正的 held-out 评测。",
            fix_command="make data-demo",
            artifact_path="data/sft/v1-seed-anchor-demo/held-out.jsonl",
        ),
        status_item(
            "validation_report",
            "Validation report",
            VALIDATION_REPORT_PATH.exists(),
            "`validation_report.md` 已存在，说明数据输出已经有可读报告。" if VALIDATION_REPORT_PATH.exists() else "还没有 validation report，建议先跑数据校验。",
            fix_command="make test-data",
            artifact_path="data/sft/v1-seed-anchor-demo/validation_report.md",
        ),
        status_item(
            "smoke_run",
            "Smoke run manifest",
            RUN_MANIFEST_PATH.exists(),
            "`run-manifest.json` 已存在，可用于前端和 probe 汇总。" if RUN_MANIFEST_PATH.exists() else "还没有 smoke train run manifest。",
            fix_command="make smoke-train-mac",
            artifact_path="outputs/gemma4-e2b-mlx-demo-unsloth-vlm/run-manifest.json",
        ),
        status_item(
            "probe_results",
            "Probe results",
            PROBE_RESULTS_PATH.exists(),
            "`inference-probe-results.json` 已存在，可直接做前端教学展示。" if PROBE_RESULTS_PATH.exists() else "还没有 probe 结果，前端无法完整讲清训练效果。",
            fix_command="make probe-mac",
            artifact_path="outputs/gemma4-e2b-mlx-demo-unsloth-vlm/inference-probe-results.json",
        ),
        status_item(
            "web_lab",
            "Built frontend lab",
            WEB_DIST_PATH.exists(),
            "`web/dist/index.html` 已存在，可直接在 IAB 里打开。" if WEB_DIST_PATH.exists() else "还没有构建后的实验台页面。",
            fix_command="make web-build",
            artifact_path="web/dist/index.html",
        ),
        status_item(
            "real_train_env",
            "Real MLX LoRA env",
            REAL_TRAIN_VENV_PYTHON.exists() and REAL_TRAIN_MLX_LORA.exists(),
            "`.venv-real-train` 和 `mlx_lm.lora` 已就绪，可以启动真实小规模 LoRA 训练。"
            if REAL_TRAIN_VENV_PYTHON.exists() and REAL_TRAIN_MLX_LORA.exists()
            else "真实 LoRA 依赖还没准备好；如果是 Apple Silicon，可执行 `make bootstrap-real-finetune`。",
            fix_command="make bootstrap-real-finetune",
            artifact_path=".venv-real-train/bin/mlx_lm.lora",
        ),
        status_item(
            "real_train_dataset",
            "Real MLX dataset",
            all(path.exists() for path in [REAL_FT_TRAIN_PATH, REAL_FT_VALID_PATH, REAL_FT_TEST_PATH, REAL_FT_PACK_PATH]),
            "`train/valid/test.jsonl` 和 dataset pack 已存在，可直接喂给 MLX LoRA。"
            if all(path.exists() for path in [REAL_FT_TRAIN_PATH, REAL_FT_VALID_PATH, REAL_FT_TEST_PATH, REAL_FT_PACK_PATH])
            else "真实训练数据格式还没生成，建议先执行 `make real-finetune-data`。",
            fix_command="make real-finetune-data",
            artifact_path="data/real-finetune/v1-gemma4-e2b-toolcall-demo/train.jsonl",
        ),
        status_item(
            "real_run",
            "Real MLX run",
            REAL_RUN_MANIFEST_PATH.exists(),
            "`run-manifest.json` 已存在，说明真实 LoRA 训练路径至少跑通过一轮。"
            if REAL_RUN_MANIFEST_PATH.exists()
            else "还没有真实 MLX LoRA run manifest。",
            fix_command="make real-train-mac",
            artifact_path="outputs/gemma4-e2b-real-mlx-lora-demo/run-manifest.json",
        ),
    ]
    stage_readiness = build_stage_readiness()
    progress = learning_status(stage_readiness)

    report = {
        "generated_at": generated_at,
        "repo": {
            "name": project_context["project"]["name"],
            "root": str(ROOT),
            "tagline": project_context["project"]["tagline"],
        },
        "machine": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "node": command_version("node"),
            "npm": command_version("npm"),
            "nvidia_smi": command_version("nvidia-smi"),
        },
        "overall_status": "ready" if all(check["status"] == "ready" for check in checks if check["id"] not in {"real_train_env", "real_train_dataset", "real_run"}) else "needs_setup",
        "readiness": checks,
        "stage_readiness": stage_readiness,
        "learning_progress": progress,
        "next_steps": recommended_steps(checks, stage_readiness),
        "agent_prompts": project_context["ai_native_onboarding"]["agent_prompts"],
        "workflow_stages": project_context["workflow_stages"],
        "reading_order": project_context["reading_order"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
