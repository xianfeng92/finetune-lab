# 2026-04-22 finetune-lab Level 6 Scale-up Rubric Implementation Notes

## 本轮目标

把 Level 6 从“教学 demo”往更真实的 scale-up compare 推进：

- 不再只看 chosen win rate
- 把多类 case 覆盖拉进来
- 把 weighted rubric score、hard failure rate 和成本视角一起纳入判断

## 实现内容

### 1. Level 6 pair 选择更真实

`training/finetune/build_level6_demo.py` 不再只取前几条样本，而是按 category 分层抽样，覆盖：

- `single_domain_single_tool`
- `single_domain_multi_tool_chain`
- `cross_domain_multi_tool`
- `reroute_to_meta`
- `full_tool_fallback`
- `proactive_event_driven`

这样 Level 6 的 compare 不再只盯着最简单的单步 tool-call case。

### 2. 新增 scale-up rubric

新增：

- `outputs/level6/scale-up-rubric.json`
- `outputs/level6/scale-up-rubric.md`

rubric 维度包括：

- route selection
- executable structure
- argument fidelity
- chain coverage
- meta reroute judgment
- event grounding

并给出：

- weighted rubric score
- acceptance bar
- coverage 检查
- cost model
- experiment plan

### 3. 更真实的 Gemma scale-up compare

`gemma-scale-up-compare.json` 现在不只看：

- pair count
- chosen win gap

还会看：

- coverage breadth
- weighted rubric score
- hard failure rate
- E2B-it / E4B-it 的迭代速度与成本角色差异

也就是说，现在 Level 6 讲的是：

- 什么时候应该继续留在 `google/gemma-4-E2B-it`
- 什么时候才值得把 `google/gemma-4-E4B-it` 拉进来做确认性实验

### 4. 前端与 IAB 同步升级

更新了：

- `web/scripts/build-lab-data.mjs`
- `web/src/data-layer.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `web/scripts/export-standalone-html.mjs`

现在 React 前端和 IAB 静态页都能展示：

- weighted rubric score
- hard failure 视角
- scale-up rubric 维度卡片
- experiment plan
- cost model / model profile

## 验证

本轮实际执行：

```bash
make level6-demo
make web-build
```

预期结果：

- `outputs/level6/scale-up-rubric.json` 已生成
- `web/public/lab-data.json` 已包含 `level6.scale_up_rubric`
- `web/dist/index.html` 能展示新的 rubric / compare 区块
