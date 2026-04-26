# Behavior Eval Pack

## What changed

- upgraded both simulated and real probe outputs to carry:
  - `behavior`
  - `risk`
  - `vehicle_state`
  - `expected_system_action`
  - `predicted_behavior`
  - `behavior_match`
  - `unsafe_direct_call`
  - `confirmation_contract_hit`
  - `refusal_contract_hit`
- added a reusable `make behavior-eval-pack` entrypoint
- added `outputs/behavior/behavior-eval-pack.json/.md`
- wired `behavior_eval_pack` into `web/public/lab-data.json`
- added a dedicated Behavior Eval panel to both the React app and the standalone IAB export

## Why

The repo already had route-selection and structured-output metrics, but the April 25 car-tool design review called out a missing layer: behavior-level evaluation.

This change adds the first explicit metric layer for:

- whether the model picked the right action class
- whether high-risk requests leaked into direct tool calls
- whether `confirm / reject` samples matched their expected system contracts

## Scope

This is still a best-effort evaluation layer. It does not yet read a real execution log or confirmation state machine. Instead, it classifies behavior from:

- predicted tool calls
- raw text markers
- expected system action contracts in the dataset

That makes it suitable for learning and regression checks, but not yet a production safety audit.

## Validation

- `make probe-mac`
- `make behavior-eval-pack`
- `make web-build`
