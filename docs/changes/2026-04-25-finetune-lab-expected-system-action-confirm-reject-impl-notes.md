# Expected System Action, Confirm, And Reject

## What changed

- added a new optional `expected_system_action` contract field to SFT samples
- introduced two new dataset categories:
  - `confirm_required_action`
  - `reject_unsafe_action`
- expanded behavior coverage so the demo dataset now includes:
  - `tool_call`
  - `clarify`
  - `handoff`
  - `confirm`
  - `reject`
- preserved `expected_system_action` into the real fine-tune dataset conversion step
- updated the Level 5 route pack to ignore non-`tool_call` samples when computing route statistics

## Why

The previous upgrades added explicit `behavior`, `risk`, and `vehicle_state`, but the dataset still did not say what the surrounding system should do after a confirmation or rejection decision.

Adding `expected_system_action` makes the dataset closer to the car-tool design contract:

- confirm samples can request `create_pending_confirmation`
- reject samples can request `refuse_execution`

This keeps the model/output boundary explicit: the model does not execute the action itself, but the sample can still describe the system transition it is supposed to trigger.

## Current shape

The new high-risk behavior slices are intentionally small and teaching-oriented:

- `confirm_required_action`: high-risk actions that should create a pending confirmation instead of directly calling a tool
- `reject_unsafe_action`: clearly unsafe actions that should be refused

The existing six route-oriented categories remain in place, so earlier Level 1-6 material can continue to work while the dataset gradually shifts toward a fuller car-control contract.

## Validation

- `make test-data`
- `make real-finetune-data`
- `make web-build`
