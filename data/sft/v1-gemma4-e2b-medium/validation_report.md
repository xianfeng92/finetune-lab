# Dataset Summary

- total_samples: 500
- train_samples: 400
- held_out_samples: 100
- multiplier: 5
- held_out_ratio: 0.2
- avg_loaded_tool_count: 2.24
- avg_expected_tool_call_count: 1.2
- multi_tool_sample_count: 150
- event_driven_sample_count: 50
- schema_valid_rate: 500/500

## Category Counts

- single_domain_single_tool: total=150 train=120 held_out=30
- single_domain_multi_tool_chain: total=75 train=60 held_out=15
- cross_domain_multi_tool: total=75 train=60 held_out=15
- reroute_to_meta: total=50 train=40 held_out=10
- full_tool_fallback: total=50 train=40 held_out=10
- proactive_event_driven: total=50 train=40 held_out=10
- confirm_required_action: total=25 train=20 held_out=5
- reject_unsafe_action: total=25 train=20 held_out=5

## Train / Held-out Split

- single_domain_single_tool: train=120 held_out=30
- single_domain_multi_tool_chain: train=60 held_out=15
- cross_domain_multi_tool: train=60 held_out=15
- reroute_to_meta: train=40 held_out=10
- full_tool_fallback: train=40 held_out=10
- proactive_event_driven: train=40 held_out=10
- confirm_required_action: train=20 held_out=5
- reject_unsafe_action: train=20 held_out=5

## Behavior Counts

- tool_call: 350
- handoff: 50
- clarify: 50
- confirm: 25
- reject: 25

## Risk Counts

- low: 192
- medium: 156
- high: 152

## Expected System Actions

- create_pending_confirmation: 25
- refuse_execution: 25

## Validation Errors

- none
