# Observatory Key Metrics First Impl Notes

## What changed

- Added a first-position `Key Metrics` panel to the Observatory view.
- The panel surfaces selected-run status, progress, latest train loss, latest validation loss, selected-run probe exact/behavior, peak memory, and live memory.
- Historical/global context remains below the key metrics so the first viewport is focused on the currently watched fine-tuning run.

## Why

During live fine-tuning, the first question is whether the selected run is moving, healthy, and improving. The previous first viewport mixed live run state with historical best-run summaries, which was useful for context but less direct for monitoring.

## Verification

- `make web-build`
