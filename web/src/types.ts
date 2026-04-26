export interface DatasetSample {
  id: string;
  category: string;
  behavior: "answer_only" | "tool_call" | "clarify" | "confirm" | "reject" | "handoff";
  risk: "low" | "medium" | "high";
  vehicle_state: {
    speed_kph: number;
    power_state: "parked" | "driving";
  };
  expected_system_action?: {
    type: "create_pending_confirmation" | "refuse_execution";
    tool?: string;
    arguments?: Record<string, unknown>;
    expires_in_seconds?: number;
    reason_code?: string;
  };
  domains_loaded: string[];
  loaded_tool_names: string[];
  system_prompt: string;
  messages: Array<Record<string, unknown>>;
  meta: {
    prompt_token_count: number;
    generator_model: string;
    adversarial: boolean;
    seed_anchor_id: string | null;
  };
  sft_text: string;
}

export interface ProbeResult {
  id: string;
  category: string;
  behavior?: "answer_only" | "tool_call" | "clarify" | "confirm" | "reject" | "handoff";
  risk?: "low" | "medium" | "high";
  vehicle_state?: {
    speed_kph: number;
    power_state: "parked" | "driving";
  };
  expected_system_action?: {
    type: "create_pending_confirmation" | "refuse_execution";
    tool?: string;
    arguments?: Record<string, unknown>;
    expires_in_seconds?: number;
    reason_code?: string;
  };
  loaded_tool_names: string[];
  expected_tool_calls: Array<Record<string, unknown>>;
  expected_names: string[];
  prompt_user: string | null;
  expected_assistant_content: string | null;
  raw_output: string;
  parsed_output: unknown;
  parse_error: string | null;
  predicted_names: string[];
  has_tool_calls_signal: boolean;
  looks_like_schema_echo: boolean;
  exact_name_match: boolean;
  structured_output_valid: boolean;
  arguments_match: boolean;
  predicted_names_all_loaded: boolean;
  prompt_style: string;
  predicted_behavior?: "answer_only" | "tool_call" | "clarify" | "confirm" | "reject" | "handoff";
  behavior_match?: boolean;
  unsafe_direct_call?: boolean;
  confirmation_contract_hit?: boolean;
  refusal_contract_hit?: boolean;
}

export interface RunManifest {
  run_id: string;
  title: string;
  engine: string;
  training_mode?: string;
  simulation_note?: string;
  model_name: string;
  dataset_path: string;
  dataset_role?: string;
  adapter_dir: string;
  max_steps: number;
  avg_loss: number;
  probe_results_path: string;
  probe_report_path: string;
  live_status_path?: string;
  public_live_status_path?: string;
  family?: string;
  is_top_level?: boolean;
  completed_at?: string | null;
  train_row_count?: number;
}
