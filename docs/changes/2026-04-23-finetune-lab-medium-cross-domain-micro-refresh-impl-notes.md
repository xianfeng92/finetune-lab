# Medium Cross-Domain Micro Refresh

## What changed

- added `make real-medium-cross-domain-focus-refresh` as a reproducible experiment entrypoint
- standardized the medium `cross_domain_multi_tool` focus stage and the follow-on `0.25 epoch` full-mixed micro refresh
- recorded the result that this refresh path does not beat the focused stage by itself

## Why

The medium `stage4 consolidation` run still missed two `cross_domain_multi_tool` held-out cases. A focused stage improved exact routing from `6/8` to `7/8`, but introduced one parse failure. This experiment checked whether a short full-mixed refresh could recover formatting stability without giving up the focused routing gain.

## Result

- `stage4 consolidation`: `6/8 exact`, `8/8 structured`, `6/8 args`
- `stage5 cross-domain focus`: `7/8 exact`, `7/8 structured`, `6/8 args`
- `stage6 micro refresh`: `6/8 exact`, `7/8 structured`, `6/8 args`

The micro refresh did not recover the `door + hvac` parse failure, and it also regressed the recovered `hvac + window` case back to a single-tool output. The best medium result therefore remains the focused stage for routing accuracy, while the earlier consolidation run remains better on structured validity.

## Artifacts

- `outputs/real/real-finetune-dataset-pack-medium-cross-domain-focus.json`
- `outputs/gemma4-e2b-real-mlx-lora-medium-cross-domain-focus/stage5-cross-domain/`
- `outputs/gemma4-e2b-real-mlx-lora-medium-cross-domain-focus-refresh/stage6-micro-refresh/`
