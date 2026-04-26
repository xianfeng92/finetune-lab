---
dataset: clarifyvc-v1
generated_at: "2026-04-26T20:31:00+08:00"
policy_version: 1.0
records_scanned: 9
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
spot_check_count: 9
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

### `clarifyvc-tier1-window-spatial` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier1_single_turn_structured_parsing
loaded_tool_names=window_set_open_percent
vehicle_state:
{"speed_kph": 0, "power_sta…`
- `messages[*].content`: `Open the rear-right window.`

### `clarifyvc-tier1-hvac-direct` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier1_single_turn_structured_parsing
loaded_tool_names=hvac_set_temperature
vehicle_state:
{"speed_kph": 0, "power_state"…`
- `messages[*].content`: `Set AC to 22°.`

### `clarifyvc-tier3-hvac-multi-turn` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier3_multi_turn_dialogue_grounding
loaded_tool_names=hvac_set_temperature
vehicle_state:
{"speed_kph": 24, "power_state"…`
- `messages[*].content`: `It's too hot in here.`

### `clarifyvc-tier2-hvac-intensity` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier2_ambiguity_detection_and_clarification
loaded_tool_names=hvac_set_temperature
vehicle_state:
{"speed_kph": 18, "powe…`
- `messages[*].content`: `Make it a bit cooler.`

### `clarifyvc-tier1-media-direct` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier1_single_turn_structured_parsing
loaded_tool_names=media_play_content
vehicle_state:
{"speed_kph": 0, "power_state": …`
- `messages[*].content`: `Play my jazz playlist.`

### `clarifyvc-tier2-seat-mode` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier2_ambiguity_detection_and_clarification
loaded_tool_names=seat_set_heating
vehicle_state:
{"speed_kph": 0, "power_sta…`
- `messages[*].content`: `Heat my seat.`

### `clarifyvc-tier1-navigation-direct` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier1_single_turn_structured_parsing
loaded_tool_names=navigation_set_destination
vehicle_state:
{"speed_kph": 0, "power_…`
- `messages[*].content`: `Take me to the nearest station.`

### `clarifyvc-tier1-lighting-direct` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier1_single_turn_structured_parsing
loaded_tool_names=lighting_set_ambient
vehicle_state:
{"speed_kph": 0, "power_state"…`
- `messages[*].content`: `Turn on ambient lights.`

### `clarifyvc-tier2-window-entity` — no PII match — included as zero-PII evidence sample

- `system_prompt`: `你是车机工具调用助手，只能从已加载工具中选择。
clarifyvc_tier=tier2_ambiguity_detection_and_clarification
loaded_tool_names=window_set_open_percent
vehicle_state:
{"speed_kph": 0, "po…`
- `messages[*].content`: `Open it.`

## 残留风险

- 模板里的人名（如「小明 / 李四」）属于合成数据集中的占位，未做识别处理。
- 车机方言里的口语化数字读法可能未被 phone_cn 正则覆盖（如「幺三八……」）。
- 不做 NER，不识别非结构化人名。
- IP / MAC / 银行卡号不在策略覆盖范围。
