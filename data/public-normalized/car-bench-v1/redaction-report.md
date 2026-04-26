---
dataset: car-bench-v1
generated_at: "2026-04-26T20:31:59+08:00"
policy_version: 1.0
records_scanned: 30
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

### `car-bench-base_84` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=navigation_set_route
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `You are in Warsaw late at night (23:15) and need to travel to Hamburg urgently for an important early morning business meeting at 10:00 AM. You're concerned abo…`

### `car-bench-base_14` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=seat_set_heating
vehicle_state:
{"speed_kph": 35, "power_state": "driving"}`
- `messages[*].content`: `You're driving with a passenger and have had the seat heating on for a while. You're starting to feel a bit too warm now, and you want to turn down the seat hea…`

### `car-bench-base_6` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=lighting_set_ambient
vehicle_state:
{"speed_kph": 35, "power_state": "driving"}`
- `messages[*].content`: `You are driving alone in the evening (around 8 PM) and want to create a more relaxing atmosphere in your car. The current ambient lighting is yellow, but you pr…`

### `car-bench-base_96` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=navigation_set_route
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `You want to set up navigation. You want to set up a charging stop in Mannheim, if it does not rain there, else drive to Cologne. Ask the assistant to navigate t…`

### `car-bench-base_44` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=lighting_set_headlight_beam
vehicle_state:
{"speed_kph": 35, "power_state": "driving"}`
- `messages[*].content`: `You are driving at night on a dark road in Wuppertal at 23:30 in December. The current low beam headlights are not providing sufficient visibility for safe driv…`

### `car-bench-base_42` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `You are in the car and it feels a bit stuffy inside. You want some air circulation without opening more windows. You ask the assistant to provide some air circu…`

### `car-bench-disambiguation_4` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=lighting_set_ambient
vehicle_state:
{"speed_kph": 35, "power_state": "driving"}`
- `messages[*].content`: `You are driving alone in the evening (around 8 PM). The current ambient lighting is yellow, but you want to change it. You will ask the assistant to change the …`

### `car-bench-base_30` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=lighting_set_headlight_beam
vehicle_state:
{"speed_kph": 35, "power_state": "driving"}`
- `messages[*].content`: `You are driving on a dark rural road in the evening and need better visibility ahead. You want to turn on the high beam headlights for better illumination. When…`

### `car-bench-disambiguation_52` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=navigation_set_route
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `You want to navigate to Munich. You ask the assistant to navigate to Munich. If the assistant presents route options, you say you want to take the one you usual…`

### `car-bench-base_76` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_temperature,seat_set_heating
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`
- `messages[*].content`: `You are the driver in the car on a cold late evening (22:30). The passenger side climate is set nicely but your driver side is too warm. You want to sync your d…`

## 残留风险

- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。
- 不做 NER，不识别非结构化人名。
- IP / MAC / 银行卡号不在策略覆盖范围。
