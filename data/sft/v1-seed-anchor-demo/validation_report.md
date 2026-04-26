# Dataset Summary

- total_samples: 100
- train_samples: 80
- held_out_samples: 20
- multiplier: 1
- held_out_ratio: 0.2
- split_strategy: row_tail
- unique_user_prompt_count: 26
- unique_template_id_count: 26
- unique_split_group_count: 26
- avg_loaded_tool_count: 2.28
- avg_expected_tool_call_count: 1.2
- multi_tool_sample_count: 30
- event_driven_sample_count: 10
- schema_valid_rate: 100/100

## Category Counts

- single_domain_single_tool: total=30 train=24 held_out=6
- single_domain_multi_tool_chain: total=15 train=12 held_out=3
- cross_domain_multi_tool: total=15 train=12 held_out=3
- reroute_to_meta: total=10 train=8 held_out=2
- full_tool_fallback: total=10 train=8 held_out=2
- proactive_event_driven: total=10 train=8 held_out=2
- confirm_required_action: total=5 train=4 held_out=1
- reject_unsafe_action: total=5 train=4 held_out=1

## Train / Held-out Split

- single_domain_single_tool: train=24 held_out=6
- single_domain_multi_tool_chain: train=12 held_out=3
- cross_domain_multi_tool: train=12 held_out=3
- reroute_to_meta: train=8 held_out=2
- full_tool_fallback: train=8 held_out=2
- proactive_event_driven: train=8 held_out=2
- confirm_required_action: train=4 held_out=1
- reject_unsafe_action: train=4 held_out=1

## Benchmark Leakage Checks

- held_out_prompt_overlap_with_train: 20
- held_out_split_group_overlap_with_train: 20
- held_out_exact_target_overlap_with_train: 20
- held_out_count: 20

## Behavior Counts

- tool_call: 70
- handoff: 10
- clarify: 10
- confirm: 5
- reject: 5

## Risk Counts

- low: 41
- medium: 30
- high: 29

## Expected System Actions

- create_pending_confirmation: 5
- refuse_execution: 5

## Validation Errors

- none
