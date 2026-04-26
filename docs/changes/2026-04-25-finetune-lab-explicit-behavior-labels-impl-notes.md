# Explicit Behavior Labels

## What changed

- upgraded the SFT demo schema so every sample now carries an explicit `behavior` label
- preserved that label through the real fine-tune dataset conversion step
- added behavior counts into dataset summaries and the frontend lab-data payload

## Behavior mapping in the current dataset

The current demo dataset still centers on tool-calling pedagogy, so the first explicit label set is intentionally small:

- `tool_call`
- `clarify`
- `handoff`

Category-to-behavior mapping:

- `single_domain_single_tool` -> `tool_call`
- `single_domain_multi_tool_chain` -> `tool_call`
- `cross_domain_multi_tool` -> `tool_call`
- `reroute_to_meta` -> `handoff`
- `full_tool_fallback` -> `clarify`
- `proactive_event_driven` -> `tool_call`

This is a stepping stone toward the fuller car-tool contract in the April 25 design review, where later iterations should add `confirm`, `reject`, and `answer_only`.

## Why

The previous dataset schema only encoded task shape via `category`. That was enough for route-selection experiments, but not enough to support behavior-level teaching or later vehicle-control evaluation layers.

Adding an explicit `behavior` field lets the repo distinguish:

- structure (`category`)
- decision intent (`behavior`)

without breaking the existing training or probe workflows.

## Validation

- `make test-data`
- `make real-finetune-data`
- `make web-build`
