# Dataset Summary

- total_samples: 539
- train_samples: 439
- held_out_samples: 100
- multiplier: 5
- held_out_ratio: 0.186
- avg_loaded_tool_count: 2.16
- avg_expected_tool_call_count: 1.2
- multi_tool_sample_count: 158
- event_driven_sample_count: 50
- schema_valid_rate: 539/539

## Category Counts

- single_domain_single_tool: total=172 train=142 held_out=30
- single_domain_multi_tool_chain: total=81 train=66 held_out=15
- cross_domain_multi_tool: total=77 train=62 held_out=15
- reroute_to_meta: total=50 train=40 held_out=10
- full_tool_fallback: total=50 train=40 held_out=10
- proactive_event_driven: total=50 train=40 held_out=10
- confirm_required_action: total=25 train=20 held_out=5
- reject_unsafe_action: total=25 train=20 held_out=5

## Train / Held-out Split

- single_domain_single_tool: train=142 held_out=30
- single_domain_multi_tool_chain: train=66 held_out=15
- cross_domain_multi_tool: train=62 held_out=15
- reroute_to_meta: train=40 held_out=10
- full_tool_fallback: train=40 held_out=10
- proactive_event_driven: train=40 held_out=10
- confirm_required_action: train=20 held_out=5
- reject_unsafe_action: train=20 held_out=5

## Behavior Counts

- tool_call: 386
- handoff: 50
- clarify: 53
- confirm: 25
- reject: 25

## Risk Counts

- low: 219
- medium: 162
- high: 158

## Expected System Actions

- create_pending_confirmation: 25
- refuse_execution: 25

## Validation Errors

- none
