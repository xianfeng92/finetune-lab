# Observatory Live Selector Impl Notes

## What changed

- `TrainingObservatoryView` now polls `run-live/index.json` in addition to the selected run's live status file.
- When the index points at a live run already present in `lab-data`, the selector refreshes that run's `liveStatusSnapshot` and `liveStatusPath`.
- When the index points at a run that is not in the static frontend data yet, the view builds a lightweight run summary from the live status JSON so the run picker can show it without a page refresh.

## Why

During real MLX LoRA training, `run-live-status.json` is mirrored into `web/public/run-live/`. The Observatory already knew how to poll an individual run, but the run picker itself was still based on static `lab-data`. Polling the live index lets the UI follow `onboarding -> data -> train -> probe -> compare -> frontend` while training is still in progress.

## Verification

- `make web-build`
