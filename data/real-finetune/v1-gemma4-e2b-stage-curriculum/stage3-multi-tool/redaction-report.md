---
dataset: v1-gemma4-e2b-stage-curriculum/stage3-multi-tool
generated_at: "2026-04-26T16:42:16+08:00"
policy_version: 1.0
records_scanned: 32
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

### `sft-v1-0038` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `副驾温度降到20度，风速调到4档`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed,hvac_set_temperature
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`

### `sft-v1-0031` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `主驾空调调到24度，风速开3档`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed,hvac_set_temperature
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`

### `sft-v1-0057` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `把车门都锁上，顺便把hvac也处理一下`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_fan_speed,door_set_lock,_meta_reroute
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`

### `sft-v1-0039` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `后排空调设到22度，风量开2档`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_temperature
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`

### `sft-v1-0088` — no PII match — included as zero-PII evidence sample

- `prompt_user`: ``
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=door_set_lock,_meta_reroute
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}
event_context:
{"id": "evt-door-o…`

### `sft-v1-0084` — no PII match — included as zero-PII evidence sample

- `prompt_user`: ``
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,door_set_lock
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}
event_context:
{"id": "evt-door-o…`

### `sft-v1-0035` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `副驾温度降到20度，风速调到4档`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_temperature,hvac_set_fan_speed
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`

### `sft-v1-0086` — no PII match — included as zero-PII evidence sample

- `prompt_user`: ``
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,window_set_open_percent
vehicle_state:
{"speed_kph": 48, "power_state": "driving"}
event_context:
{"id":…`

### `sft-v1-0034` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `主驾空调调到24度，风速开3档`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=hvac_set_temperature,hvac_set_fan_speed
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`

### `sft-v1-0055` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `开点窗，前排留条缝，顺便把seat也处理一下`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=window_set_open_percent,_meta_reroute,seat_set_heating
vehicle_state:
{"speed_kph": 6, "power_state": "parked"}`

## 残留风险

- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。
- 不做 NER，不识别非结构化人名。
- IP / MAC / 银行卡号不在策略覆盖范围。
