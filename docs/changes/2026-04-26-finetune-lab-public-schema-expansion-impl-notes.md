# Public Schema Expansion

## 本次改动

- 扩展 `data/tool-schemas/automotive-v1.json`
  - 新增 `lighting`
  - 新增 `navigation`
  - 新增 `media`
- 扩展 `training/data_pipeline/import_car_bench.py`
  - 支持 lights / navigation 相关 action 映射
  - 忽略只读 helper actions，让带 helper 链的公开任务也能落成最小可执行样本
- 扩展 `training/data_pipeline/import_clarifyvc.py`
  - 让 `lighting / navigation / media` 三个 protocol seed 真正落成样本
- 补充 importer 测试

## 目标

前一轮公开数据接入已经证明：

- `CAR-Bench` 能接进来，但和当前本地 schema 的重合度很低
- `ClarifyVC` 可以接协议 seed，但 `lighting / navigation / media` 都会被跳过

这次的目标不是把整个车机世界一次性补全，而是优先补一层**最小可执行 schema**，让公开数据接入开始真正有量。

## 新增 schema

### lighting

- `lighting_set_ambient`
- `lighting_set_headlight_beam`
- `lighting_set_fog_lights`

### navigation

- `navigation_set_destination`
- `navigation_set_route`
- `navigation_replace_final_destination`
- `navigation_delete_destination`
- `navigation_delete_waypoint`
- `navigation_replace_waypoint`
- `navigation_add_waypoint`

### media

- `media_play_content`

## CAR-Bench 接入变化

这次最重要的不是只加了几个 action 映射，而是允许 importer 跳过只读 helper actions：

- `get_location_id_by_location_name`
- `get_routes_from_start_to_destination`
- `get_current_navigation_state`
- `get_weather`
- `get_exterior_lights_status`
- 等等

这样像：

- `get_location_id -> get_routes -> set_new_navigation`
- `get_weather -> get_exterior_lights_status -> set_fog_lights`

这种任务就不再整条报废，而是可以归一到“最终执行动作”的最小样本。

## 结果

### CAR-Bench

- 之前：`normalized_sample_count = 2`
- 现在：`normalized_sample_count = 30`

主要新增来自：

- `lighting`: ambient / fog / headlight beam
- `navigation`: set / replace / delete / add waypoint

### ClarifyVC

- 之前：`normalized_sample_count = 6`
- 现在：`normalized_sample_count = 9`

三条新接入分别是：

- `clarifyvc-tier1-lighting-direct`
- `clarifyvc-tier1-navigation-direct`
- `clarifyvc-tier1-media-direct`

## 当前边界

这次仍然没有覆盖：

- `sunroof / sunshade`
- `trunk`
- `phone / email`
- 更完整的 climate helper 操作

所以公开数据虽然已经明显放大，但还不是最终形态。下一步如果继续扩，最值的会是：

- `sunroof / trunk`
- `phone / email`
- 或把这 39 条公开样本真正并进一版训练对比
