# Medium Dataset Schema Refresh

## What changed

- rebuilt `data/sft/v1-gemma4-e2b-medium` from the current `pipeline.py`
- rebuilt `data/real-finetune/v1-gemma4-e2b-medium`
- upgraded the medium dataset path so it now preserves the same schema enrichments as the small dataset path:
  - `behavior`
  - `risk`
  - `vehicle_state`
  - `expected_system_action`
  - `confirm_required_action`
  - `reject_unsafe_action`
- refreshed user-facing docs to reflect the new medium split counts

## Why

The previous `400/51/49` medium pack was generated before the car-tool schema upgrades landed.
That made small-vs-medium comparisons unfair, because the small dataset already carried safety-context fields and
`confirm / reject` behavior slices while the medium dataset still reflected the older tool-call-only schema.

This refresh moves the medium dataset onto the same behavior-aware, safety-aware schema so later data-scale comparisons
measure dataset size and training strategy, rather than schema mismatch.

## Current result

- medium SFT dataset now contains `500` samples total
- medium real fine-tune pack now contains:
  - `400 train`
  - `52 valid`
  - `48 test`
- medium real pack now includes:
  - `20` `confirm` train rows
  - `20` `reject` train rows
  - `create_pending_confirmation` and `refuse_execution` in split-level counters

## Validation

- `make test-data`
- `make data-medium`
- `make real-finetune-data-medium`
