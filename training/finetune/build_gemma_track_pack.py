from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_pack() -> dict:
    return {
        "generated_at": iso_now(),
        "headline": "Gemma 4 E2B base vs instruct pack",
        "summary": (
            "把 `google/gemma-4-E2B` 和 `google/gemma-4-E2B-it` 的教学角色拆开，"
            "让学习路线图不只停留在文案承诺，而是真正有一个可复用的对照实验说明包。"
        ),
        "checkpoints": [
            {
                "name": "google/gemma-4-E2B",
                "type": "base",
                "teaching_role": "对照基座",
                "best_for": "理解 pretraining checkpoint 为什么还不会直接遵守 agent / tool-calling 协议。",
                "strengths": [
                    "更接近原始基座能力，便于解释为什么 instruction tuning 会改变行为先验。",
                    "适合做 prompt baseline、continued pretraining 和 domain adaptation 的概念入口。",
                ],
                "blind_spots": [
                    "默认不会稳定产出 tool_calls 数组。",
                    "对 schema-bound structured output 的先验较弱。",
                ],
            },
            {
                "name": "google/gemma-4-E2B-it",
                "type": "instruct",
                "teaching_role": "默认教学基座",
                "best_for": "第一次 SFT、probe、tool calling 和 structured outputs 教学。",
                "strengths": [
                    "更容易稳定遵守 instruction 和工具调用格式。",
                    "更适合把少量数据 + 少量 step 的行为差异讲清楚。",
                ],
                "blind_spots": [
                    "如果直接拿来做所有实验，用户会忽略 base vs instruct 的本质差异。",
                    "在复杂 rubric 上达到瓶颈时，仍然需要更严格的 probe 或 scale-up。",
                ],
            },
        ],
        "comparison_axes": [
            {
                "axis": "Instruction following prior",
                "base": "需要更强 prompt scaffold 才能维持格式。",
                "instruct": "天然更接近 agent / chat / schema-following 预期。",
                "why_it_matters": "解释为什么第一次教学实验优先从 `-it` 开始。",
            },
            {
                "axis": "Structured outputs",
                "base": "更容易退回自然语言或半结构化文本。",
                "instruct": "更容易稳定到 `tool_calls` 或 JSON 样式。",
                "why_it_matters": "帮助用户把 Level 5 的 probe 指标和 checkpoint 选择联系起来。",
            },
            {
                "axis": "Fine-tuning teaching value",
                "base": "适合解释为何 instruction tuning 本身就会改变行为。",
                "instruct": "适合解释少量高质量数据如何进一步塑造工具选择和参数补全。",
                "why_it_matters": "让学习路径从'会跑'升级到'知道为什么先用哪个模型'。",
            },
        ],
        "teaching_experiments": [
            {
                "title": "Prompt baseline first",
                "command": "make level1-pack",
                "goal": "先看 baseline failure buckets，再决定是否需要微调。",
            },
            {
                "title": "Teach the first SFT on instruct",
                "command": "make smoke-train-mac && make probe-mac",
                "goal": "先在 `google/gemma-4-E2B-it` 心智模型上解释最小 SFT 闭环。",
            },
            {
                "title": "Review the base-vs-instruct pack",
                "command": "make gemma-track-pack",
                "goal": "把 base checkpoint 和 instruct checkpoint 的角色差异显式化。",
            },
        ],
        "recommended_order": [
            "先用 `google/gemma-4-E2B-it` 跑 Level 1-5，确保用户能看懂可执行结构、probe 和行为 diff。",
            "再阅读 base-vs-instruct pack，理解为什么 `google/gemma-4-E2B` 更适合做对照而不是第一次 demo。",
            "等 Level 6 的 rubric 稳定后，再讨论是否需要升级到 `google/gemma-4-E4B-it`。",
        ],
        "teaching_notes": [
            "这个 pack 先把 checkpoint 选择的理论差异讲清楚，不假装已经跑完真实 base-vs-instruct 训练实验。",
            "如果后续补上真实 Gemma base / instruct compare run，可以在不改心智模型的前提下继续扩这个 pack。",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/gemma"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_pack()
    output_path = args.output_dir / "base-vs-instruct-pack.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_path": str(output_path), "headline": payload["headline"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
