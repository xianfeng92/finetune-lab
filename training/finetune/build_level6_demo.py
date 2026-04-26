from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


CATEGORY_ORDER = [
    "single_domain_single_tool",
    "single_domain_multi_tool_chain",
    "cross_domain_multi_tool",
    "reroute_to_meta",
    "full_tool_fallback",
    "proactive_event_driven",
]

RUBRIC_DIMENSIONS = [
    {
        "id": "route_selection",
        "title": "Route selection",
        "weight": 0.22,
        "target_for_e4b": 85,
        "why": "先稳定选对工具，再讨论更大的 checkpoint 是否值得。",
    },
    {
        "id": "executable_output",
        "title": "Executable structure",
        "weight": 0.2,
        "target_for_e4b": 90,
        "why": "偏好优化最关键的不是文风，而是输出能不能直接驱动 agent 行为。",
    },
    {
        "id": "argument_fidelity",
        "title": "Argument fidelity",
        "weight": 0.18,
        "target_for_e4b": 80,
        "why": "只挑对 tool name 还不够，参数完整性才决定是否真的可执行。",
    },
    {
        "id": "chain_coverage",
        "title": "Chain coverage",
        "weight": 0.14,
        "target_for_e4b": 75,
        "why": "跨 domain 和 multi-call 是 scale-up 最容易出幻觉的地方。",
    },
    {
        "id": "meta_reroute_judgment",
        "title": "Meta reroute judgment",
        "weight": 0.14,
        "target_for_e4b": 85,
        "why": "如果该 reroute 时还在乱选 tool，更大模型只会更自信地出错。",
    },
    {
        "id": "event_grounding",
        "title": "Event grounding",
        "weight": 0.12,
        "target_for_e4b": 75,
        "why": "事件驱动 case 能区分'会解释'和'会行动'这两种完全不同的能力。",
    },
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
        description = event.get("description") or event.get("signal") or "unknown event"
        return {"kind": "event", "text": f"事件触发：{description}"}
    assistant = next((msg["content"] for msg in sample["messages"] if msg["role"] == "assistant"), None)
    return {"kind": "assistant", "text": assistant or "(no prompt surface)"}


def pick_pairs_source_samples(samples: list[dict], per_category: int = 2) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        grouped[sample["category"]].append(sample)

    selected = []
    for category in CATEGORY_ORDER:
        selected.extend(grouped.get(category, [])[:per_category])
    return selected


def output_shape(parsed_output: object) -> str:
    if isinstance(parsed_output, dict) and isinstance(parsed_output.get("tool_calls"), list):
        return "tool_calls_array"
    if isinstance(parsed_output, dict) and isinstance(parsed_output.get("tool_name"), str):
        return "tool_name_only"
    if isinstance(parsed_output, dict) and "tool_schema" in parsed_output:
        return "schema_echo"
    return "non_executable"


def predicted_names(parsed_output: object) -> list[str]:
    if isinstance(parsed_output, dict) and isinstance(parsed_output.get("tool_calls"), list):
        return [call.get("name", "none") for call in parsed_output["tool_calls"]]
    if isinstance(parsed_output, dict) and isinstance(parsed_output.get("tool_name"), str):
        return [parsed_output["tool_name"]]
    return []


def mutated_arguments(arguments: dict) -> dict:
    wrong_args = dict(arguments)
    for key, value in list(wrong_args.items()):
        if isinstance(value, bool):
            wrong_args[key] = not value
            return wrong_args
        if isinstance(value, int):
            wrong_args[key] = value + 1
            return wrong_args
        if isinstance(value, str):
            wrong_args[key] = f"{value}-alt"
            return wrong_args
    return wrong_args


def rejection_variant(sample: dict, variant_index: int) -> tuple[str, str, object, str]:
    calls = expected_calls(sample)
    first_call = calls[0] if calls else {"name": "none", "arguments": {}}
    expected_name = first_call.get("name")
    loaded = sample["loaded_tool_names"]
    alt_tool = next((tool for tool in loaded if tool != expected_name), expected_name)
    category = sample["category"]

    if category == "single_domain_single_tool":
        if variant_index % 2 == 0:
            parsed = {"tool_name": expected_name}
            return (
                "tool_name_only",
                "只输出 tool_name，看起来像懂了，但还没有形成可执行的 tool_calls 结构。",
                parsed,
                json.dumps(parsed, ensure_ascii=False),
            )
        parsed = {"tool_calls": [{"name": expected_name, "arguments": mutated_arguments(first_call.get("arguments", {}))}]}
        return (
            "wrong_arguments",
            "挑对工具名不够，参数不完整时 agent 仍然无法稳定执行。",
            parsed,
            json.dumps(parsed, ensure_ascii=False),
        )

    if category == "single_domain_multi_tool_chain":
        parsed = {"tool_calls": calls[:1]}
        return (
            "first_call_only",
            "baseline 往往会只完成第一步，把多调用链压缩成单调用。",
            parsed,
            json.dumps(parsed, ensure_ascii=False),
        )

    if category == "cross_domain_multi_tool":
        if variant_index % 2 == 0:
            parsed = {"tool_calls": calls[:1]}
            return (
                "cross_domain_drop",
                "跨 domain 请求最容易退化成'只抓住一个意图'。",
                parsed,
                json.dumps(parsed, ensure_ascii=False),
            )
        parsed = {"tool_calls": [{"name": alt_tool, "arguments": first_call.get("arguments", {})}]}
        return (
            "wrong_tool_loaded",
            "loaded tools 变多后，baseline 更容易抓错 route。",
            parsed,
            json.dumps(parsed, ensure_ascii=False),
        )

    if category == "reroute_to_meta":
        parsed = {"tool_calls": [{"name": alt_tool, "arguments": {}}]}
        return (
            "wrong_tool_loaded",
            "当真正应该 `_meta_reroute` 时，baseline 容易硬选一个看起来相关的工具。",
            parsed,
            json.dumps(parsed, ensure_ascii=False),
        )

    if category == "full_tool_fallback":
        raw = '{"tool_schema": {"name": "tool_name", "arguments": {"...": "..."}}}'
        return (
            "schema_echo",
            "宽泛请求很容易把模型推回 schema echo，而不是给出明确 reroute。",
            {"tool_schema": {"name": "tool_name", "arguments": {"...": "..."}}},
            raw,
        )

    raw = "检测到事件，我会继续关注。"
    return (
        "natural_language_only",
        "事件 case 最容易暴露这个问题：模型会解释事件，但不会直接采取行动。",
        None,
        raw,
    )


def build_pair(sample: dict, index: int, variant_index: int) -> dict:
    calls = expected_calls(sample)
    chosen = {
        "raw_output": json.dumps({"tool_calls": calls}, ensure_ascii=False),
        "parsed_output": {"tool_calls": calls},
        "output_shape": "tool_calls_array",
    }
    rejection_type, reason, rejected_parsed, rejected_raw = rejection_variant(sample, variant_index)
    surface = prompt_surface(sample)
    return {
        "id": f"pref-{index + 1:04d}",
        "source_sample_id": sample["id"],
        "category": sample["category"],
        "prompt_user": surface["text"],
        "prompt_kind": surface["kind"],
        "loaded_tool_names": sample["loaded_tool_names"],
        "expected_tool_name": calls[0].get("name") if calls else "none",
        "expected_tool_names": [call.get("name", "none") for call in calls],
        "expected_tool_calls": calls,
        "has_event_context": bool(sample.get("event")),
        "preference_reason": reason,
        "rejection_type": rejection_type,
        "chosen": chosen,
        "rejected": {
            "raw_output": rejected_raw,
            "parsed_output": rejected_parsed,
            "output_shape": output_shape(rejected_parsed),
        },
    }


def build_dataset_pack(pairs: list[dict], dataset_path: Path) -> dict:
    rejection_counts = Counter(pair["rejection_type"] for pair in pairs)
    category_counts = Counter(pair["category"] for pair in pairs)
    return {
        "generated_at": iso_now(),
        "dataset_path": str(dataset_path),
        "summary": {
            "pair_count": len(pairs),
            "distinct_rejection_types": len(rejection_counts),
            "distinct_categories": len(category_counts),
            "event_driven_pairs": sum(1 for pair in pairs if pair["has_event_context"]),
            "multi_call_pairs": sum(1 for pair in pairs if len(pair["expected_tool_calls"]) > 1),
            "rejection_counts": [
                {"rejection_type": key, "count": count}
                for key, count in rejection_counts.most_common()
            ],
            "category_counts": [
                {"category": key, "count": count}
                for key, count in category_counts.most_common()
            ],
            "chosen_shape": "tool_calls_array",
        },
        "focus_pairs": pairs[:6],
        "teaching_notes": [
            "偏好数据不再问'正确答案是什么'，而是问'两个答案里哪个更好'。",
            "更真实的 Level 6 不能只盯着单一 tool-call case，而要覆盖 multi-call、reroute 和 event-driven 场景。",
            "如果 pair 只覆盖最简单 case，scale-up compare 很容易高估更大 checkpoint 的收益。",
        ],
    }


def exact_arguments_score(expected_calls_list: list[dict], predicted_calls_list: list[dict]) -> float:
    if not predicted_calls_list or not expected_calls_list:
        return 0.0
    matched = 0
    for expected, predicted in zip(expected_calls_list, predicted_calls_list):
        if expected.get("name") == predicted.get("name") and expected.get("arguments") == predicted.get("arguments"):
            matched += 1
    return round(matched / max(len(expected_calls_list), 1), 2)


def route_selection_score(expected_names: list[str], predicted_names_list: list[str]) -> float:
    if predicted_names_list == expected_names:
        return 1.0
    if predicted_names_list and len(predicted_names_list) <= len(expected_names):
        if all(name == expected_names[idx] for idx, name in enumerate(predicted_names_list)):
            return round(len(predicted_names_list) / len(expected_names), 2)
    if any(name in expected_names for name in predicted_names_list):
        return 0.25
    return 0.0


def meta_reroute_score(expected_names: list[str], predicted_names_list: list[str]) -> float | None:
    expected_meta = "_meta_reroute" in expected_names
    predicted_meta = "_meta_reroute" in predicted_names_list
    if expected_meta:
        return 1.0 if predicted_meta and predicted_names_list == expected_names else 0.0
    if predicted_meta:
        return 0.0
    return 1.0


def event_grounding_score(pair: dict, executable_score: float, route_score: float) -> float | None:
    if not pair["has_event_context"]:
        return None
    return round((executable_score + route_score) / 2, 2)


def evaluate_candidate(pair: dict, candidate: dict) -> dict:
    expected_calls_list = pair["expected_tool_calls"]
    expected_names = [call.get("name", "none") for call in expected_calls_list]
    parsed = candidate.get("parsed_output")
    predicted_calls_list = parsed.get("tool_calls", []) if isinstance(parsed, dict) else []
    predicted_names_list = predicted_names(parsed)
    executable_score = 1.0 if output_shape(parsed) == "tool_calls_array" else 0.0
    route_score = route_selection_score(expected_names, predicted_names_list)
    arguments_score = exact_arguments_score(expected_calls_list, predicted_calls_list)
    chain_score = round(len(predicted_calls_list) / max(len(expected_calls_list), 1), 2) if executable_score else 0.0
    meta_score = meta_reroute_score(expected_names, predicted_names_list)
    event_score = event_grounding_score(pair, executable_score, route_score)

    criteria = {
        "route_selection": route_score,
        "executable_output": executable_score,
        "argument_fidelity": arguments_score,
        "chain_coverage": chain_score,
        "meta_reroute_judgment": meta_score,
        "event_grounding": event_score,
    }

    applicable_weight = 0.0
    weighted_score = 0.0
    for dimension in RUBRIC_DIMENSIONS:
        score = criteria[dimension["id"]]
        if score is None:
            continue
        applicable_weight += dimension["weight"]
        weighted_score += score * dimension["weight"]

    score_points = round((weighted_score / max(applicable_weight, 0.0001)) * 100, 1)
    hard_failures = []
    if executable_score < 1:
        hard_failures.append("non_executable")
    if route_score < 0.5:
        hard_failures.append("route_miss")
    if arguments_score < 1 and executable_score == 1 and expected_names != ["_meta_reroute"]:
        hard_failures.append("argument_loss")
    if chain_score < 1 and len(expected_calls_list) > 1:
        hard_failures.append("chain_drop")
    if event_score is not None and event_score < 1:
        hard_failures.append("event_not_actionable")

    return {
        "predicted_names": predicted_names_list,
        "output_shape": output_shape(parsed),
        "score_points": score_points,
        "criteria": {
            key: None if value is None else round(value * 100, 1)
            for key, value in criteria.items()
        },
        "hard_failures": hard_failures,
    }


def baseline_policy_decision(pair: dict) -> tuple[str, dict, str]:
    rejection_type = pair["rejection_type"]
    if rejection_type in {"wrong_tool_loaded"}:
        selected = pair["chosen"]
        note = "baseline 有时还能猜中 route，但不代表结构和参数已经稳定。"
        return ("chosen", selected, note)
    if rejection_type in {"first_call_only", "cross_domain_drop"} and len(pair["expected_tool_calls"]) == 1:
        selected = pair["chosen"]
        note = "单调用 case baseline 看起来像能过，但一扩到更复杂场景就会掉链子。"
        return ("chosen", selected, note)
    selected = pair["rejected"]
    note = "这类偏好点通常是 prompt-only baseline 最先失手的地方。"
    return ("rejected", selected, note)


def preference_policy_decision(pair: dict) -> tuple[str, dict, str]:
    return (
        "chosen",
        pair["chosen"],
        "Preference-aware policy 明确偏好可执行、结构化、参数完整且覆盖完整动作链的答案。",
    )


def summarize_policy(compare_cases: list[dict], policy_key: str, title: str) -> dict:
    wins = sum(1 for case in compare_cases if case[policy_key]["decision"] == "chosen")
    total_cases = max(len(compare_cases), 1)
    structured_pref = sum(1 for case in compare_cases if case[policy_key]["assessment"]["criteria"]["executable_output"] == 100.0)
    weighted_scores = [case[policy_key]["assessment"]["score_points"] for case in compare_cases]
    hard_failure_cases = sum(1 for case in compare_cases if case[policy_key]["assessment"]["hard_failures"])
    return {
        "policy_id": "sft_only" if policy_key == "baseline_policy" else "preference_aware",
        "title": title,
        "summary": {
            "chosen_win_rate": wins,
            "total_cases": total_cases,
            "structured_output_preference": structured_pref,
            "weighted_rubric_score": round(sum(weighted_scores) / max(len(weighted_scores), 1), 1),
            "hard_failure_cases": hard_failure_cases,
            "behavior": (
                "会挑对部分工具，但对结构化输出、链式覆盖和事件触发的稳定性仍然不够。"
                if policy_key == "baseline_policy"
                else "更稳定地偏好可执行、结构化、参数完整、链式覆盖更完整的答案。"
            ),
        },
    }


def build_policy_compare(pairs: list[dict]) -> dict:
    compare_cases = []
    for pair in pairs:
        baseline_choice, baseline_selected, baseline_note = baseline_policy_decision(pair)
        preference_choice, preference_selected, preference_note = preference_policy_decision(pair)
        compare_cases.append(
            {
                "id": pair["id"],
                "category": pair["category"],
                "prompt_user": pair["prompt_user"],
                "preference_reason": pair["preference_reason"],
                "rejection_type": pair["rejection_type"],
                "chosen_preview": pair["chosen"]["raw_output"],
                "rejected_preview": pair["rejected"]["raw_output"],
                "baseline_policy": {
                    "decision": baseline_choice,
                    "win": baseline_choice == "chosen",
                    "notes": baseline_note,
                    "assessment": evaluate_candidate(pair, baseline_selected),
                },
                "preference_policy": {
                    "decision": preference_choice,
                    "win": preference_choice == "chosen",
                    "notes": preference_note,
                    "assessment": evaluate_candidate(pair, preference_selected),
                },
            }
        )

    return {
        "generated_at": iso_now(),
        "policies": [
            summarize_policy(compare_cases, "baseline_policy", "SFT-only policy"),
            summarize_policy(compare_cases, "preference_policy", "Preference-aware policy"),
        ],
        "compare_cases": compare_cases,
        "scale_up_guidance": [
            {
                "step": "1",
                "title": "Stabilize the rubric on E2B",
                "body": "先在 Gemma 4 E2B-it 上把 route、structure、arguments、chain coverage 这套 rubric 跑稳。 ",
            },
            {
                "step": "2",
                "title": "Use E4B for confirmation, not discovery",
                "body": "更大 checkpoint 应该用来验证已经稳定的偏好假设，而不是在口径还没定住时盲目放大实验。 ",
            },
            {
                "step": "3",
                "title": "Upgrade only when the hard failures are rare",
                "body": "如果 non_executable、route_miss、chain_drop 仍然频繁出现，scale-up 只会让结论更贵，不会更真。 ",
            },
        ],
        "teaching_notes": [
            "更真实的 Level 6 不该只看 chosen win rate，还要看 weighted rubric score 和 hard failures。",
            "当 policy compare 已经能在多类 case 上稳定分出优劣时，scale-up compare 才有意义。",
        ],
    }


def build_scale_up_rubric(dataset_pack: dict, compare_report: dict) -> dict:
    preference_cases = [case["preference_policy"]["assessment"] for case in compare_report["compare_cases"]]
    baseline_cases = [case["baseline_policy"]["assessment"] for case in compare_report["compare_cases"]]
    criteria = []
    overall_current = 0.0
    overall_baseline = 0.0
    weight_sum = 0.0
    for dimension in RUBRIC_DIMENSIONS:
        dim_id = dimension["id"]
        current_scores = [case["criteria"][dim_id] for case in preference_cases if case["criteria"][dim_id] is not None]
        baseline_scores = [case["criteria"][dim_id] for case in baseline_cases if case["criteria"][dim_id] is not None]
        current_score = round(sum(current_scores) / max(len(current_scores), 1), 1)
        baseline_score = round(sum(baseline_scores) / max(len(baseline_scores), 1), 1)
        current_ready = current_score >= dimension["target_for_e4b"]
        criteria.append(
            {
                "id": dim_id,
                "title": dimension["title"],
                "weight": round(dimension["weight"] * 100, 1),
                "baseline_score": baseline_score,
                "current_score": current_score,
                "target_for_e4b": dimension["target_for_e4b"],
                "status": "pass" if current_ready else "hold",
                "why": dimension["why"],
            }
        )
        overall_current += current_score * dimension["weight"]
        overall_baseline += baseline_score * dimension["weight"]
        weight_sum += dimension["weight"]

    category_counts = dataset_pack["summary"]["category_counts"]
    coverage = [
        {
            "category": item["category"],
            "pairs": item["count"],
            "status": "pass" if item["count"] >= 2 else "hold",
            "why": "真实 scale-up compare 需要每类 failure bucket 至少有基础覆盖。",
        }
        for item in category_counts
    ]
    overall_score = round(overall_current / max(weight_sum, 0.0001), 1)
    baseline_score = round(overall_baseline / max(weight_sum, 0.0001), 1)
    return {
        "generated_at": iso_now(),
        "summary": {
            "weighted_rubric_score": overall_score,
            "baseline_weighted_score": baseline_score,
            "coverage_categories": len(category_counts),
            "pair_count": dataset_pack["summary"]["pair_count"],
        },
        "criteria": criteria,
        "coverage": coverage,
        "acceptance_bar": [
            "weighted rubric score >= 85",
            "六类 category 至少都有基础 pair 覆盖",
            "hard failure rate <= 15%",
            "event-driven 和 multi-call case 不再只停留在自然语言解释",
        ],
        "cost_model": [
            {
                "model": "google/gemma-4-E2B-it",
                "compute_class": "low",
                "iteration_speed": "fast",
                "best_use": "继续扩 pair、改 judge、磨 compare view",
            },
            {
                "model": "google/gemma-4-E4B-it",
                "compute_class": "medium",
                "iteration_speed": "slower",
                "best_use": "在 rubric 稳定后做确认性实验，验证更强 checkpoint 的稳定收益",
            },
        ],
        "experiment_plan": [
            {
                "stage": "stage-1",
                "title": "Strengthen E2B-it rubric",
                "goal": "把 route / executable / arguments / chain / reroute / event 六维 rubric 先压稳。",
            },
            {
                "stage": "stage-2",
                "title": "Run a narrow E4B-it confirmation pass",
                "goal": "只在已经稳定的 pair 和 compare rubric 上验证是否真的减少 hard failures。",
            },
            {
                "stage": "stage-3",
                "title": "Decide whether scale-up is worth the cost",
                "goal": "如果 weighted rubric score 提升有限，就继续停留在 E2B-it 做教学主线。",
            },
        ],
    }


def build_scale_up_compare(dataset_pack: dict, compare_report: dict, rubric_pack: dict) -> dict:
    baseline_policy = next(policy for policy in compare_report["policies"] if policy["policy_id"] == "sft_only")
    preference_policy = next(policy for policy in compare_report["policies"] if policy["policy_id"] == "preference_aware")
    pair_count = dataset_pack["summary"]["pair_count"]
    category_count = dataset_pack["summary"]["distinct_categories"]
    rejection_types = dataset_pack["summary"]["distinct_rejection_types"]
    weighted_score = rubric_pack["summary"]["weighted_rubric_score"]
    hard_failure_rate = round(
        preference_policy["summary"]["hard_failure_cases"] / max(preference_policy["summary"]["total_cases"], 1) * 100,
        1,
    )
    win_gap = round(
        (
            preference_policy["summary"]["chosen_win_rate"] / max(preference_policy["summary"]["total_cases"], 1)
            - baseline_policy["summary"]["chosen_win_rate"] / max(baseline_policy["summary"]["total_cases"], 1)
        )
        * 100,
        1,
    )

    pair_ready = pair_count >= 18
    coverage_ready = category_count == len(CATEGORY_ORDER)
    rubric_ready = weighted_score >= 85
    hard_failure_ready = hard_failure_rate <= 15

    gates = [
        {
            "gate": "pair volume",
            "current": pair_count,
            "target_for_e4b": 18,
            "status": "pass" if pair_ready else "hold",
            "why": "真实 scale-up compare 至少要覆盖一轮分层 pair，而不只是少量演示案例。",
        },
        {
            "gate": "coverage breadth",
            "current": category_count,
            "target_for_e4b": len(CATEGORY_ORDER),
            "status": "pass" if coverage_ready else "hold",
            "why": "如果 six-level 里的关键 failure bucket 没被覆盖，大模型收益就没有可比性。",
        },
        {
            "gate": "weighted rubric score",
            "current": weighted_score,
            "target_for_e4b": 85,
            "status": "pass" if rubric_ready else "hold",
            "why": "scale-up 之前先确认当前 preference 方案已经在 rubric 上稳定，不然只是在放大噪声。",
        },
        {
            "gate": "hard failure rate",
            "current": hard_failure_rate,
            "target_for_e4b": 15,
            "status": "pass" if hard_failure_ready else "hold",
            "why": "只要 non_executable、route_miss、chain_drop 还常见，升级模型就还太早。",
        },
    ]

    hold_count = sum(1 for gate in gates if gate["status"] == "hold")
    recommended_model = "google/gemma-4-E2B-it" if hold_count else "google/gemma-4-E4B-it"
    recommendation_stage = "stay-small" if recommended_model.endswith("E2B-it") else "scale-up"

    model_profiles = [
        {
            "model": "google/gemma-4-E2B-it",
            "role": "classroom checkpoint",
            "fit_score": 94 if recommendation_stage == "stay-small" else 78,
            "best_for": "pair / judge / compare 迭代，快速验证 rubric 是否真的站住。",
            "strength": "本地成本低、反馈快，最适合继续扩 pair 和压 hard failures。",
            "risk": "如果 pair 已经扩到更广 coverage，E2B-it 可能在复杂 case 上开始早饱和。",
            "cost_class": "low",
            "expected_cycle": "minutes",
        },
        {
            "model": "google/gemma-4-E4B-it",
            "role": "confirmation checkpoint",
            "fit_score": 90 if recommendation_stage == "scale-up" else 58,
            "best_for": "在 rubric 稳定后验证更大模型是否真的减少 hard failures。",
            "strength": "更适合在 route、chain、event 三类复杂 case 上追求更稳的偏好行为。",
            "risk": "如果 rubric 还不稳，E4B-it 只会把实验成本抬高，结论仍然摇摆。",
            "cost_class": "medium",
            "expected_cycle": "longer local run",
        },
    ]

    decision_matrix = [
        {
            "criterion": "weighted rubric score",
            "current_state": f"{weighted_score} vs target 85",
            "e2b_it": "继续补齐 rubric 更划算",
            "e4b_it": "只有 rubric 稳住后才值得验证更强 checkpoint",
        },
        {
            "criterion": "hard failure rate",
            "current_state": f"{hard_failure_rate}% hard failures",
            "e2b_it": "适合先把 non_executable / route_miss / chain_drop 压低",
            "e4b_it": "如果 hard failures 已低，再看更大模型能否继续改善",
        },
        {
            "criterion": "coverage breadth",
            "current_state": f"{category_count}/{len(CATEGORY_ORDER)} categories covered",
            "e2b_it": "先让 pair 覆盖更完整",
            "e4b_it": "覆盖足够后再做确认性 scale-up",
        },
        {
            "criterion": "compute overhead",
            "current_state": "需要频繁迭代 pair / judge / compare",
            "e2b_it": "更适合 discovery",
            "e4b_it": "更适合 confirmation",
        },
    ]

    return {
        "generated_at": iso_now(),
        "current_state": {
            "pair_count": pair_count,
            "rejection_types": rejection_types,
            "coverage_categories": category_count,
            "baseline_chosen_win_rate": {
                "wins": baseline_policy["summary"]["chosen_win_rate"],
                "total": baseline_policy["summary"]["total_cases"],
            },
            "preference_chosen_win_rate": {
                "wins": preference_policy["summary"]["chosen_win_rate"],
                "total": preference_policy["summary"]["total_cases"],
            },
            "win_gap_points": win_gap,
            "weighted_rubric_score": weighted_score,
            "hard_failure_rate": hard_failure_rate,
        },
        "gates": gates,
        "model_profiles": model_profiles,
        "decision_matrix": decision_matrix,
        "recommendation": {
            "model": recommended_model,
            "stage": recommendation_stage,
            "summary": (
                "当前更适合继续留在 Gemma 4 E2B-it 上扩 rubric 和压 hard failures。"
                if recommendation_stage == "stay-small"
                else "当前已经具备把 Gemma 4 E4B-it 拉进来做确认性实验的条件。"
            ),
            "reasoning": [
                f"当前 weighted rubric score 是 {weighted_score}，chosen win gap 是 {win_gap} 个点；这比单看 chosen win rate 更能反映 preference 方案是否真的稳定。",
                f"当前 hard failure rate 是 {hard_failure_rate}%，说明是否 scale-up 的关键已经不是'模型能不能看懂任务'，而是复杂 case 上的稳定性是否够高。",
            ],
            "next_actions": [
                "继续扩 pair 到更广 domain，并补更多 chain / reroute / event cases。",
                "优先用 weighted rubric score 和 hard failure rate 作为 Level 6 的主指标，而不是只看 chosen win。",
                "如果后续 rubric >= 85 且 hard failure <= 15%，再用 E4B-it 跑一轮确认性实验。",
            ],
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--preferences-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    samples = load_jsonl(args.dataset)
    selected_samples = pick_pairs_source_samples(samples)
    variant_counter: dict[str, int] = defaultdict(int)
    pairs = []
    for index, sample in enumerate(selected_samples):
        category = sample["category"]
        pairs.append(build_pair(sample, index, variant_counter[category]))
        variant_counter[category] += 1

    args.preferences_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pairs_path = args.preferences_dir / "pairs.jsonl"
    pairs_path.write_text("\n".join(json.dumps(pair, ensure_ascii=False) for pair in pairs) + "\n", encoding="utf-8")

    dataset_pack = build_dataset_pack(pairs, pairs_path)
    compare_report = build_policy_compare(pairs)
    rubric_pack = build_scale_up_rubric(dataset_pack, compare_report)
    scale_up_compare = build_scale_up_compare(dataset_pack, compare_report, rubric_pack)

    dataset_json = args.output_dir / "preference-dataset-pack.json"
    compare_json = args.output_dir / "policy-compare-report.json"
    rubric_json = args.output_dir / "scale-up-rubric.json"
    scale_up_json = args.output_dir / "gemma-scale-up-compare.json"

    write_json(dataset_json, dataset_pack)
    write_json(compare_json, compare_report)
    write_json(rubric_json, rubric_pack)
    write_json(scale_up_json, scale_up_compare)

    write_markdown(
        args.output_dir / "preference-dataset-pack.md",
        [
            "# Preference Dataset Pack",
            "",
            f"- pair_count: {dataset_pack['summary']['pair_count']}",
            f"- distinct_rejection_types: {dataset_pack['summary']['distinct_rejection_types']}",
            f"- distinct_categories: {dataset_pack['summary']['distinct_categories']}",
            "",
            "## Teaching Notes",
            "",
            *[f"- {note}" for note in dataset_pack["teaching_notes"]],
        ],
    )
    write_markdown(
        args.output_dir / "policy-compare-report.md",
        [
            "# Policy Compare Report",
            "",
            *[
                f"- {policy['title']}: win {policy['summary']['chosen_win_rate']}/{policy['summary']['total_cases']} · weighted rubric {policy['summary']['weighted_rubric_score']} · hard failures {policy['summary']['hard_failure_cases']}"
                for policy in compare_report["policies"]
            ],
            "",
            "## Teaching Notes",
            "",
            *[f"- {note}" for note in compare_report["teaching_notes"]],
        ],
    )
    write_markdown(
        args.output_dir / "scale-up-rubric.md",
        [
            "# Scale-up Rubric",
            "",
            f"- weighted_rubric_score: {rubric_pack['summary']['weighted_rubric_score']}",
            f"- baseline_weighted_score: {rubric_pack['summary']['baseline_weighted_score']}",
            "",
            "## Acceptance Bar",
            "",
            *[f"- {item}" for item in rubric_pack["acceptance_bar"]],
        ],
    )
    write_markdown(
        args.output_dir / "scale-up-guidance.md",
        [
            "# Scale-up Guidance",
            "",
            *[
                f"## {item['step']}. {item['title']}\n\n{item['body']}\n"
                for item in compare_report["scale_up_guidance"]
            ],
        ],
    )
    write_markdown(
        args.output_dir / "gemma-scale-up-compare.md",
        [
            "# Gemma Scale-up Compare",
            "",
            f"- recommended_model: {scale_up_compare['recommendation']['model']}",
            f"- stage: {scale_up_compare['recommendation']['stage']}",
            f"- pair_count: {scale_up_compare['current_state']['pair_count']}",
            f"- weighted_rubric_score: {scale_up_compare['current_state']['weighted_rubric_score']}",
            f"- hard_failure_rate: {scale_up_compare['current_state']['hard_failure_rate']}",
            "",
            "## Next Actions",
            "",
            *[f"- {item}" for item in scale_up_compare["recommendation"]["next_actions"]],
        ],
    )

    print(
        json.dumps(
            {
                "pairs_path": str(pairs_path),
                "dataset_pack": str(dataset_json),
                "policy_compare": str(compare_json),
                "scale_up_rubric": str(rubric_json),
                "scale_up_compare": str(scale_up_json),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
