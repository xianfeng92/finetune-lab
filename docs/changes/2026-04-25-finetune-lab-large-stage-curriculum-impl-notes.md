# Large Stage Curriculum

## 本次改动

- 新增 `make real-large-stage-curriculum-consolidation`
- 更新 `training/finetune/README.md`
- 更新 `docs/ai/gemma4-real-finetune-guide.md`
- 更新 `docs/ai/workflows.md`

## 目标

在已经跑通的 `1000 total` large 数据基础上，复用 current medium best 的课程化训练组织方式：

- stage1: `single_domain_single_tool`
- stage2: `reroute_to_meta + full_tool_fallback + confirm_required_action + reject_unsafe_action`
- stage3: `single_domain_multi_tool_chain + cross_domain_multi_tool + proactive_event_driven`
- stage4: `full mixed consolidation`

核心问题：

- `1000 total + direct mixed` 已经验证过
- 这次要看 `1000 total + curriculum + consolidation` 能不能真正超过 current medium best

## 标准入口

```bash
make real-large-stage-curriculum-consolidation
```

## 预期产物

- `data/real-finetune/v1-gemma4-e2b-large-stage-curriculum/`
- `outputs/real/real-finetune-dataset-pack-large-stage1-single-tool.json`
- `outputs/real/real-finetune-dataset-pack-large-stage2-reroute-meta.json`
- `outputs/real/real-finetune-dataset-pack-large-stage3-multi-tool.json`
- `outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum/`
- `outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum-consolidation/`
