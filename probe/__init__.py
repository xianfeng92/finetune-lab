"""Top-level probe package.

Extracted from `training/finetune/behavior_eval.py` so that downstream
consumers (edge-bench, future eval tools) can import behavior metric
helpers without depending on training-side cwd magic.
"""

from probe.behavior_eval import (
    classify_predicted_behavior,
    confirmation_contract_hit,
    refusal_contract_hit,
    structured_output_valid,
    summarize_behavior_metrics,
    unsafe_direct_call,
)

__all__ = [
    "classify_predicted_behavior",
    "confirmation_contract_hit",
    "refusal_contract_hit",
    "structured_output_valid",
    "summarize_behavior_metrics",
    "unsafe_direct_call",
]
