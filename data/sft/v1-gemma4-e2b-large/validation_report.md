# Dataset Summary

- total_samples: 1000
- train_samples: 800
- held_out_samples: 200
- multiplier: 10
- held_out_ratio: 0.2
- avg_loaded_tool_count: 2.21
- avg_expected_tool_call_count: 1.2
- multi_tool_sample_count: 300
- event_driven_sample_count: 100
- schema_valid_rate: 1000/1000

## Category Counts

- single_domain_single_tool: total=300 train=240 held_out=60
- single_domain_multi_tool_chain: total=150 train=120 held_out=30
- cross_domain_multi_tool: total=150 train=120 held_out=30
- reroute_to_meta: total=100 train=80 held_out=20
- full_tool_fallback: total=100 train=80 held_out=20
- proactive_event_driven: total=100 train=80 held_out=20
- confirm_required_action: total=50 train=40 held_out=10
- reject_unsafe_action: total=50 train=40 held_out=10

## Train / Held-out Split

- single_domain_single_tool: train=240 held_out=60
- single_domain_multi_tool_chain: train=120 held_out=30
- cross_domain_multi_tool: train=120 held_out=30
- reroute_to_meta: train=80 held_out=20
- full_tool_fallback: train=80 held_out=20
- proactive_event_driven: train=80 held_out=20
- confirm_required_action: train=40 held_out=10
- reject_unsafe_action: train=40 held_out=10

## Behavior Counts

- tool_call: 700
- handoff: 100
- clarify: 100
- confirm: 50
- reject: 50

## Risk Counts

- low: 383
- medium: 310
- high: 307

## Expected System Actions

- create_pending_confirmation: 50
- refuse_execution: 50

## Validation Errors

- none
