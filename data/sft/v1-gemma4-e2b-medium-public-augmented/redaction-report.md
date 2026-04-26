---
dataset: v1-gemma4-e2b-medium-public-augmented
generated_at: "2026-04-26T20:35:28+08:00"
policy_version: 1.0
records_scanned: 539
records_redacted: 0
match_counts:
  phone_cn: 0
  id_cn: 0
  plate_cn: 0
  email: 0
fields_scanned:
  - prompt_user
  - expected_assistant_content
  - system_prompt
  - messages[*].content
spot_check_count: 10
---

## 应用的策略

### `phone_cn`

中国大陆手机号（11 位，1[3-9]xxxxxxxxx，前后非数字）
替换为 `[PHONE_REDACTED]`。

### `id_cn`

中国大陆身份证（18 位，含日期段 + 校验位 X/x）
替换为 `[ID_REDACTED]`。

### `plate_cn`

中国机动车牌（蓝/绿牌，省份字 + 字母 + 5-6 位 alnum）
替换为 `[PLATE_REDACTED]`。

### `email`

标准 email
替换为 `[EMAIL_REDACTED]`。

## 命中明细

本批无命中（`records_redacted = 0`）。

## Spot-check（10 例）

### `sft-v1-0115` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=seat_set_heating
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `副驾座椅加热开2档`

### `sft-v1-0026` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=window_set_open_percent
vehicle_state:
{"speed_kph": 6, "power_state": "parked"}`
- `messages[*].content`: `开点窗，前排留条缝`

### `sft-v1-0352` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=door_set_lock,hvac_set_temperature,window_set_open_percent,seat_set_heating,_meta_reroute
vehicle_state:
{"speed_kph":…`
- `messages[*].content`: `把车里弄舒服一点`

### `sft-v1-0311` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,door_set_lock
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`
- `messages[*].content`: `车里太冷了，想把空调调暖一点`

### `sft-v1-0274` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,hvac_set_temperature,window_set_open_percent
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `冷死了，主驾调到24度，顺便把window也处理一下`

### `sft-v1-0173` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`
- `messages[*].content`: `副驾温度降到20度，风速调到4档`

### `sft-v1-0105` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`
- `messages[*].content`: `冷死了，主驾调到24度`

### `sft-v1-0090` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=window_set_open_percent
vehicle_state:
{"speed_kph": 6, "power_state": "parked"}`
- `messages[*].content`: `开点窗，前排留条缝`

### `clarifyvc-tier2-hvac-intensity` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier2_ambiguity_detection_and_clarification
loaded_tool_names=hvac_set_temperature
vehicle_state:
{"speed_kph": 18, "powe…`
- `messages[*].content`: `Make it a bit cooler.`

### `sft-v1-0033` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed,hvac_set_temperature
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`
- `messages[*].content`: `冷死了，主驾调到24度`

## 残留风险

- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。
- 不做 NER，不识别非结构化人名。
- IP / MAC / 银行卡号不在策略覆盖范围。
