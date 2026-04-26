# Data Scale vs Strategy Compare

## What changed

- added standardized compare targets for:
  - small direct mixed
  - medium direct mixed
  - medium curriculum + consolidation
- added `training/finetune/build_data_scale_compare_pack.py`
- prepared a dedicated frontend / IAB compare panel for:
  - small vs medium
  - direct mixed vs curriculum + consolidation
  - route quality vs behavior / safety contract metrics

## Why

The repo already had many individual experiment runs, but the teaching value was still fragmented:

- one page showed Level 5
- another area showed behavior eval
- medium-data experiments lived in separate run directories

This change turns those experiments into one explicit teaching question:

`When does more data help, and when does curriculum design matter more than raw sample count?`

## Notes

- The compare pack is only meaningful when small and medium datasets share the same schema.
- This iteration assumes the refreshed medium dataset now carries:
  - `behavior`
  - `risk`
  - `vehicle_state`
  - `expected_system_action`
  - `confirm / reject`
- Final metrics depend on the compare runs being regenerated on top of that refreshed schema.

## Validation

- `make real-small-direct-compare`
- `make real-medium-direct-compare`
- `make real-medium-stage-curriculum-consolidation`
- `make data-scale-compare-pack`
- `make web-build`
