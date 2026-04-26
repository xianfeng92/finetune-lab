# Dataset Summary

- total_samples: 500
- train_samples: 356
- held_out_samples: 144
- multiplier: 5
- held_out_ratio: 0.2
- split_strategy: group
- unique_user_prompt_count: 26
- unique_template_id_count: 26
- unique_split_group_count: 26
- avg_loaded_tool_count: 2.23
- avg_expected_tool_call_count: 1.2
- multi_tool_sample_count: 150
- event_driven_sample_count: 50
- schema_valid_rate: 500/500

## Category Counts

- single_domain_single_tool: total=150 train=113 held_out=37
- single_domain_multi_tool_chain: total=75 train=50 held_out=25
- cross_domain_multi_tool: total=75 train=57 held_out=18
- reroute_to_meta: total=50 train=34 held_out=16
- full_tool_fallback: total=50 train=38 held_out=12
- proactive_event_driven: total=50 train=38 held_out=12
- confirm_required_action: total=25 train=13 held_out=12
- reject_unsafe_action: total=25 train=13 held_out=12

## Train / Held-out Split

- single_domain_single_tool: train=113 held_out=37
- single_domain_multi_tool_chain: train=50 held_out=25
- cross_domain_multi_tool: train=57 held_out=18
- reroute_to_meta: train=34 held_out=16
- full_tool_fallback: train=38 held_out=12
- proactive_event_driven: train=38 held_out=12
- confirm_required_action: train=13 held_out=12
- reject_unsafe_action: train=13 held_out=12

## Benchmark Leakage Checks

- held_out_prompt_overlap_with_train: 0
- held_out_split_group_overlap_with_train: 0
- held_out_exact_target_overlap_with_train: 0
- held_out_count: 144

## Behavior Counts

- tool_call: 350
- handoff: 50
- clarify: 50
- confirm: 25
- reject: 25

## Risk Counts

- low: 205
- medium: 143
- high: 152

## Expected System Actions

- create_pending_confirmation: 25
- refuse_execution: 25

## Validation Errors

- none
