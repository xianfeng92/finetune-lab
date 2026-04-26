---
dataset: v1-gemma4-e2b-stage-curriculum/stage2-reroute-meta
generated_at: "2026-04-26T16:42:16+08:00"
policy_version: 1.0
records_scanned: 24
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

### `sft-v1-0096` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `行驶中把车门都解锁`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,door_set_lock
vehicle_state:
{"speed_kph": 45, "power_state": "driving"}`

### `sft-v1-0064` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `车里太闷了，想透透气`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,hvac_set_temperature
vehicle_state:
{"speed_kph": 6, "power_state": "parked"}`

### `sft-v1-0061` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `车里太闷了，想透透气`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,window_set_open_percent
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`

### `sft-v1-0071` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `把车里弄舒服一点`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=seat_set_heating,_meta_reroute,window_set_open_percent,hvac_set_fan_speed,door_set_lock,hvac_set_temperature
vehicle_s…`

### `sft-v1-0068` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `车里太冷了，想把空调调暖一点`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,hvac_set_temperature
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`

### `sft-v1-0094` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `把车门都解锁`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,door_set_lock
vehicle_state:
{"speed_kph": 12, "power_state": "driving"}`

### `sft-v1-0065` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `车里太冷了，想把空调调暖一点`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=window_set_open_percent,_meta_reroute
vehicle_state:
{"speed_kph": 38, "power_state": "driving"}`

### `sft-v1-0098` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `行驶中把车门都解锁`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=door_set_lock,_meta_reroute
vehicle_state:
{"speed_kph": 45, "power_state": "driving"}`

### `sft-v1-0063` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `我想把门都锁上`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=_meta_reroute,door_set_lock
vehicle_state:
{"speed_kph": 0, "power_state": "parked"}`

### `sft-v1-0072` — no PII match — included as zero-PII evidence sample

- `prompt_user`: `把车里弄舒服一点`
- `messages[*].content`: `你是车机工具调用助手，只能从已加载工具中选择。
loaded_tool_names=door_set_lock,hvac_set_temperature,window_set_open_percent,seat_set_heating,_meta_reroute
vehicle_state:
{"speed_kph":…`

## 残留风险

- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。
- 不做 NER，不识别非结构化人名。
- IP / MAC / 银行卡号不在策略覆盖范围。
