from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


CATEGORY_BUCKETS = {
    "single_domain_single_tool": {
        "bucket": "missing_executable_structure",
        "label": "Missing executable structure",
        "description": "能猜到大概意图，但只会说自然语言或 tool_name，没稳定产出可执行的 tool_calls。",
        "why_it_matters": "如果 baseline 连可执行结构都不稳，训练后的 JSON validity 和 tool_calls 才有意义。",
    },
    "single_domain_multi_tool_chain": {
        "bucket": "drops_multi_call_plan",
        "label": "Drops multi-call plan",
        "description": "只完成第一步调用，忽略后续链式动作。",
        "why_it_matters": "这类样本决定模型能不能从'挑对工具'升级到'完成完整动作计划'。",
    },
    "cross_domain_multi_tool": {
        "bucket": "misses_cross_domain_request",
        "label": "Misses cross-domain request",
        "description": "抓住一个 domain，但漏掉顺手提出的第二个请求。",
        "why_it_matters": "真实 agent 请求常常跨 domain，baseline 容易把多意图压扁成单意图。",
    },
    "reroute_to_meta": {
        "bucket": "fails_meta_reroute",
        "label": "Fails meta reroute",
        "description": "当 loaded tools 不匹配真实意图时，不会及时退到 _meta_reroute。",
        "why_it_matters": "这类错误会让模型在'没有合适工具'时强行乱选。",
    },
    "full_tool_fallback": {
        "bucket": "cannot_disambiguate_broad_request",
        "label": "Cannot disambiguate broad request",
        "description": "面对过宽泛的请求时，既不会稳定澄清，也不会返回可执行 reroute。",
        "why_it_matters": "Level 1 要先讲清楚任务边界，不是什么自然语言请求都该直接落成一个工具调用。",
    },
    "proactive_event_driven": {
        "bucket": "misses_event_trigger",
        "label": "Misses event trigger",
        "description": "遇到事件驱动样本时，只会解释事件，不会直接采取动作。",
        "why_it_matters": "这类 case 说明任务不只是 user prompt routing，还包括 event-to-action 映射。",
    },
}

CATEGORY_ORDER = [
    "single_domain_single_tool",
    "single_domain_multi_tool_chain",
    "cross_domain_multi_tool",
    "reroute_to_meta",
    "full_tool_fallback",
    "proactive_event_driven",
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def expected_calls(sample: dict) -> list[dict]:
    return sample["messages"][-1].get("tool_calls", [])


def prompt_surface(sample: dict) -> dict:
    user = next((msg["content"] for msg in sample["messages"] if msg["role"] == "user"), None)
    if user:
        return {"kind": "user", "text": user}
    event = sample.get("event")
    if event:
        return {"kind": "event", "text": f"事件触发：{event.get('description', event.get('signal', 'unknown event'))}"}
    assistant = next((msg["content"] for msg in sample["messages"] if msg["role"] == "assistant"), None)
    return {"kind": "assistant", "text": assistant or "(no user prompt)"}


def risk_flags(sample: dict) -> list[str]:
    flags = []
    calls = expected_calls(sample)
    if len(calls) > 1:
        flags.append("multi_call")
    if any(call.get("name") == "_meta_reroute" for call in calls):
        flags.append("meta_reroute")
    if sample.get("event"):
        flags.append("event_driven")
    if len(sample.get("loaded_tool_names", [])) >= 3:
        flags.append("wide_candidate_set")
    if sample["category"] in {"cross_domain_multi_tool", "full_tool_fallback"}:
        flags.append("multi_intent")
    return flags


def baseline_prediction(sample: dict) -> dict:
    category = sample["category"]
    calls = expected_calls(sample)
    first_call = calls[0] if calls else {"name": "none", "arguments": {}}
    expected_names = [call.get("name", "none") for call in calls]
    loaded = sample.get("loaded_tool_names", [])

    if category == "single_domain_single_tool":
        predicted_output = {"tool_name": first_call["name"]}
        predicted_names = [first_call["name"]]
        return {
            "strategy": "tool_name_only",
            "predicted_output": json.dumps(predicted_output, ensure_ascii=False),
            "predicted_names": predicted_names,
            "output_shape": "tool_name_only",
            "scorecard": {
                "route_selection_hit": predicted_names == expected_names,
                "executable_output": False,
                "arguments_complete": False,
                "full_chain_coverage": True,
                "meta_reroute_correct": True,
                "overall_pass": False,
            },
            "lesson": "Level 1 要先看见：'挑对工具名' 不等于 '给出可执行答案'。",
        }

    if category == "single_domain_multi_tool_chain":
        predicted_output = {"tool_calls": [first_call]}
        return {
            "strategy": "first_call_only",
            "predicted_output": json.dumps(predicted_output, ensure_ascii=False),
            "predicted_names": [first_call["name"]],
            "output_shape": "tool_calls_array",
            "scorecard": {
                "route_selection_hit": True,
                "executable_output": True,
                "arguments_complete": True,
                "full_chain_coverage": False,
                "meta_reroute_correct": True,
                "overall_pass": False,
            },
            "lesson": "baseline 往往能踩中第一步，但会掉完整动作链。",
        }

    if category == "cross_domain_multi_tool":
        predicted_output = {"tool_calls": [first_call]}
        return {
            "strategy": "single_domain_focus",
            "predicted_output": json.dumps(predicted_output, ensure_ascii=False),
            "predicted_names": [first_call["name"]],
            "output_shape": "tool_calls_array",
            "scorecard": {
                "route_selection_hit": False,
                "executable_output": True,
                "arguments_complete": True,
                "full_chain_coverage": False,
                "meta_reroute_correct": True,
                "overall_pass": False,
            },
            "lesson": "一旦请求跨 domain，prompt baseline 很容易把多意图压成单意图。",
        }

    if category == "reroute_to_meta":
        wrong_tool = next((tool for tool in loaded if tool != "_meta_reroute"), "_meta_reroute")
        predicted_output = {"tool_calls": [{"name": wrong_tool, "arguments": {}}]}
        return {
            "strategy": "hallucinated_domain_tool",
            "predicted_output": json.dumps(predicted_output, ensure_ascii=False),
            "predicted_names": [wrong_tool],
            "output_shape": "tool_calls_array",
            "scorecard": {
                "route_selection_hit": False,
                "executable_output": True,
                "arguments_complete": False,
                "full_chain_coverage": True,
                "meta_reroute_correct": False,
                "overall_pass": False,
            },
            "lesson": "没有 baseline reroute 评测时，很难发现模型其实在'没有合适工具'时乱选。",
        }

    if category == "full_tool_fallback":
        raw = '{"tool_schema": {"name": "tool_name", "arguments": {"...": "..."}}}'
        return {
            "strategy": "schema_echo",
            "predicted_output": raw,
            "predicted_names": [],
            "output_shape": "schema_echo",
            "scorecard": {
                "route_selection_hit": False,
                "executable_output": False,
                "arguments_complete": False,
                "full_chain_coverage": False,
                "meta_reroute_correct": False,
                "overall_pass": False,
            },
            "lesson": "宽泛请求最容易让 baseline 回到'看起来像答案'但其实不能执行的 schema echo。",
        }

    raw = "检测到事件，我会先帮你处理。"
    return {
        "strategy": "natural_language_only",
        "predicted_output": raw,
        "predicted_names": [],
        "output_shape": "natural_language",
        "scorecard": {
            "route_selection_hit": False,
            "executable_output": False,
            "arguments_complete": False,
            "full_chain_coverage": False,
            "meta_reroute_correct": True,
            "overall_pass": False,
        },
        "lesson": "事件驱动样本能暴露 baseline 的另一个短板：会解释事件，但不会直接采取动作。",
    }


def select_seed_cases(samples: list[dict]) -> list[dict]:
    selected = []
    for category in CATEGORY_ORDER:
        match = next((sample for sample in samples if sample["category"] == category), None)
        if match:
            selected.append(match)
    return selected


def build_task_framing_pack(samples: list[dict], seed_cases: list[dict], dataset_path: Path) -> dict:
    category_counts = Counter(sample["category"] for sample in samples)
    tool_counts = Counter(call["name"] for sample in samples for call in expected_calls(sample))
    domain_counts = Counter(domain for sample in samples for domain in sample.get("domains_loaded", []))

    failure_buckets = []
    for category in CATEGORY_ORDER:
        sample = next((item for item in seed_cases if item["category"] == category), None)
        bucket = CATEGORY_BUCKETS[category]
        failure_buckets.append(
            {
                "bucket": bucket["bucket"],
                "label": bucket["label"],
                "description": bucket["description"],
                "why_it_matters": bucket["why_it_matters"],
                "sample_count": category_counts.get(category, 0),
                "example_case_id": sample["id"] if sample else None,
                "affected_category": category,
            }
        )

    return {
        "generated_at": iso_now(),
        "dataset_path": str(dataset_path),
        "task_brief": {
            "title": "Gemma 4 E2B cabin-control baseline",
            "user_job": "把车控自然语言请求或事件信号映射成可执行 tool_calls。",
            "target_behavior": "在 loaded_tool_names 约束下挑对 route、补对 arguments、遇到模糊请求时及时 reroute 到 _meta_reroute。",
            "why_finetune": [
                "这个任务不是单纯生成自然语言，而是生成可执行结构。",
                "很多失败不在语义理解，而在 route selection、参数补全和 meta reroute。",
                "Level 1 先定义 baseline 和 failure buckets，后面的 SFT / probe 才有参照系。",
            ],
        },
        "dataset_profile": {
            "total_samples": len(samples),
            "category_counts": [{"category": key, "count": value} for key, value in category_counts.most_common()],
            "top_expected_tools": [{"tool_name": key, "count": value} for key, value in tool_counts.most_common()],
            "domain_counts": [{"domain": key, "count": value} for key, value in domain_counts.most_common()],
        },
        "success_rubric": [
            {
                "criterion": "Route selection",
                "pass_signal": "expected tool names 与输出完全对齐，包含 _meta_reroute 的 case 也能正确退回。",
                "fail_signal": "乱选 loaded tool，或把需要 reroute 的 case 强行落到某个 domain 工具。",
            },
            {
                "criterion": "Executable structure",
                "pass_signal": "输出稳定落成 tool_calls 数组，而不是 tool_name / schema echo / 自然语言说明。",
                "fail_signal": "回答看起来像懂了，但实际上不能直接驱动工具调用。",
            },
            {
                "criterion": "Argument completeness",
                "pass_signal": "arguments 和 expected tool_calls 对齐，位置、档位、温度等关键信息不丢。",
                "fail_signal": "只挑对工具名，但 arguments 缺失、泛化或错位。",
            },
            {
                "criterion": "Chain and event handling",
                "pass_signal": "多调用链、跨 domain 请求和事件触发 case 都能完整覆盖。",
                "fail_signal": "只做第一步、漏掉第二意图，或事件来了只会解释不会执行。",
            },
        ],
        "failure_buckets": failure_buckets,
        "held_out_seed_cases": [
            {
                "id": sample["id"],
                "category": sample["category"],
                "prompt_surface": prompt_surface(sample),
                "loaded_tool_names": sample["loaded_tool_names"],
                "expected_tool_calls": expected_calls(sample),
                "risk_flags": risk_flags(sample),
                "rubric_focus": [
                    "route selection",
                    "executable structure",
                    "argument completeness" if len(expected_calls(sample)) == 1 else "chain coverage",
                ],
                "baseline_hypothesis": CATEGORY_BUCKETS[sample["category"]]["description"],
            }
            for sample in seed_cases
        ],
        "teaching_notes": [
            "Level 1 不是先跑训练，而是先定义任务、rubric 和 baseline failure buckets。",
            "如果不先挑出 held-out seed cases，后面的 probe 很容易退化成'看几条漂亮案例'。",
            "这个任务最容易被低估的点，是它要求模型输出可执行结构，而不只是看起来合理的回答。",
        ],
    }


def build_baseline_eval_pack(seed_cases: list[dict]) -> dict:
    evaluations = []
    failure_bucket_counts = Counter()
    route_hits = 0
    executable = 0
    arguments_complete = 0
    chain_coverage = 0
    meta_reroute = 0
    overall_pass = 0

    for sample in seed_cases:
        prediction = baseline_prediction(sample)
        failure_bucket = CATEGORY_BUCKETS[sample["category"]]["bucket"]
        failure_bucket_counts[failure_bucket] += 1
        scorecard = prediction["scorecard"]
        route_hits += int(scorecard["route_selection_hit"])
        executable += int(scorecard["executable_output"])
        arguments_complete += int(scorecard["arguments_complete"])
        chain_coverage += int(scorecard["full_chain_coverage"])
        meta_reroute += int(scorecard["meta_reroute_correct"])
        overall_pass += int(scorecard["overall_pass"])
        evaluations.append(
            {
                "id": sample["id"],
                "category": sample["category"],
                "prompt_surface": prompt_surface(sample),
                "loaded_tool_names": sample["loaded_tool_names"],
                "expected_tool_calls": expected_calls(sample),
                "baseline_prediction": {
                    "strategy": prediction["strategy"],
                    "output_shape": prediction["output_shape"],
                    "predicted_names": prediction["predicted_names"],
                    "raw_output": prediction["predicted_output"],
                },
                "scorecard": scorecard,
                "likely_failure_bucket": failure_bucket,
                "lesson": prediction["lesson"],
            }
        )

    total = max(len(evaluations), 1)
    return {
        "generated_at": iso_now(),
        "baseline_profile": {
            "name": "Prompt-only baseline",
            "strategy": "不做任何微调，假设模型只能依赖表面语义和通用指令跟随能力。",
            "strengths": [
                "能看懂最明显的单步意图。",
                "会给出看起来合理的自然语言解释。",
            ],
            "weaknesses": [
                "不稳定地产出 tool_calls 结构。",
                "多调用链、reroute 和事件驱动 case 容易失手。",
            ],
        },
        "summary": {
            "case_count": len(evaluations),
            "route_selection_hit": route_hits,
            "executable_output": executable,
            "arguments_complete": arguments_complete,
            "full_chain_coverage": chain_coverage,
            "meta_reroute_correct": meta_reroute,
            "overall_pass": overall_pass,
            "failure_bucket_counts": [
                {"bucket": key, "count": value}
                for key, value in failure_bucket_counts.most_common()
            ],
        },
        "cases": evaluations,
        "next_actions": [
            "先记住 baseline 哪里会错，再看 Level 3/4 的 SFT 和 probe 改变了什么。",
            "后续 probe 优先覆盖这里的 6 类 failure bucket，而不是只追求平均 loss 下降。",
            "如果某个 bucket 在 Level 4 里还反复出现，就回到 Level 2 补数据和 schema，而不是盲目加 steps。",
        ],
        "teaching_notes": [
            "Level 1 的 baseline 评测包不是为了证明模型很差，而是为了定义'什么叫学会了'。",
            "这里最有价值的信号不是 pass 数，而是 failure bucket 是否和任务结构一致。",
        ],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    samples = load_jsonl(args.dataset)
    seed_cases = select_seed_cases(samples)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    task_pack = build_task_framing_pack(samples, seed_cases, args.dataset)
    baseline_pack = build_baseline_eval_pack(seed_cases)

    task_json = args.output_dir / "task-framing-pack.json"
    task_md = args.output_dir / "task-framing-pack.md"
    baseline_json = args.output_dir / "baseline-eval-pack.json"
    baseline_md = args.output_dir / "baseline-eval-pack.md"

    write_json(task_json, task_pack)
    write_json(baseline_json, baseline_pack)

    write_markdown(
        task_md,
        [
            "# Task Framing Pack",
            "",
            f"- total_samples: {task_pack['dataset_profile']['total_samples']}",
            f"- held_out_seed_cases: {len(task_pack['held_out_seed_cases'])}",
            "",
            "## Success Rubric",
            "",
            *[f"- {item['criterion']}: {item['pass_signal']}" for item in task_pack["success_rubric"]],
        ],
    )
    write_markdown(
        baseline_md,
        [
            "# Baseline Eval Pack",
            "",
            f"- case_count: {baseline_pack['summary']['case_count']}",
            f"- route_selection_hit: {baseline_pack['summary']['route_selection_hit']}/{baseline_pack['summary']['case_count']}",
            f"- executable_output: {baseline_pack['summary']['executable_output']}/{baseline_pack['summary']['case_count']}",
            f"- overall_pass: {baseline_pack['summary']['overall_pass']}/{baseline_pack['summary']['case_count']}",
            "",
            "## Next Actions",
            "",
            *[f"- {item}" for item in baseline_pack["next_actions"]],
        ],
    )

    print(
        json.dumps(
            {
                "task_pack": str(task_json),
                "baseline_pack": str(baseline_json),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
