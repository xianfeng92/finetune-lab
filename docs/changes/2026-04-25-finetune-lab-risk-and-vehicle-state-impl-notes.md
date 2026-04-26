# Risk And Vehicle State

## What changed

- upgraded the SFT demo schema so every sample now carries explicit `risk` and `vehicle_state`
- injected `vehicle_state` into the rendered system prompt so training examples include safety context, not just loaded tools
- preserved `risk` and `vehicle_state` through the real fine-tune dataset conversion step
- added risk counts into dataset summaries and the frontend lab-data payload

## Current shape

Each sample now includes:

- `risk`: `low`, `medium`, or `high`
- `vehicle_state.speed_kph`
- `vehicle_state.power_state`

The current repo still uses a teaching-oriented car-control dataset, so these fields are context signals, not yet full execution contracts. In particular:

- `door` domain samples are marked `high` risk but still remain tool-call examples when the vehicle is parked
- `window` domain samples stay in low-speed or parked states so they do not implicitly promise a `confirm` flow that the dataset has not modeled yet

## Why

The explicit behavior-label upgrade made it possible to distinguish task structure from decision intent. The next missing layer from the April 25 car-tool review was safety context:

- how risky is this request
- what vehicle state is the model seeing when it decides

Adding these now lets later iterations move toward:

- `confirm`
- `reject`
- `expected_system_action`

without rewriting the basic dataset format again.

## Validation

- `make test-data`
- `make real-finetune-data`
- `make web-build`
