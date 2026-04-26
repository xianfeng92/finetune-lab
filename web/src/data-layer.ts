import type { DatasetSample, ProbeResult, RunManifest } from "./types";
import { embeddedLabData } from "./generated/lab-data.generated";

export interface RunArtifact {
  name: string;
  relative_path: string;
  size_bytes: number;
}

export interface TrainingCurvePoint {
  step: number;
  loss: number;
}

export interface TrainTelemetryPoint {
  step: number;
  loss: number;
  learning_rate: number | null;
  iterations_per_second: number | null;
  tokens_per_second: number | null;
  trained_tokens: number | null;
  peak_memory_gb: number | null;
}

export interface EvalTelemetryPoint {
  step: number;
  val_loss: number;
  val_time_s: number | null;
}

export interface TrainingCurve {
  total_steps: number;
  first_loss: number | null;
  last_loss: number | null;
  loss_delta_pct: number | null;
  points: TrainingCurvePoint[];
}

export interface RunPlanSummary {
  requested_epochs: number | null;
  effective_epochs: number | null;
  batch_size: number | null;
  learning_rate: number | null;
  steps_per_report: number | null;
  steps_per_eval: number | null;
  save_every: number | null;
  max_seq_length: number | null;
  num_layers: number | null;
  compat_patch: string | null;
  resume_adapter_file: string | null;
}

export interface RunResourceSummary {
  peak_memory_gb: number | null;
  avg_iterations_per_second: number | null;
  avg_tokens_per_second: number | null;
  last_trained_tokens: number | null;
  best_val_loss: number | null;
  last_val_loss: number | null;
  avg_val_time_s: number | null;
  last_val_time_s: number | null;
  host_platform: string | null;
  host_arch: string | null;
  live_cpu_usage_supported: boolean;
  live_gpu_usage_supported: boolean;
  live_memory_usage_supported: boolean;
  run_plan: {
    batch_size: number | null;
    requested_epochs: number | null;
    effective_epochs: number | null;
    steps_per_report: number | null;
    steps_per_eval: number | null;
    save_every: number | null;
  } | null;
}

export interface LiveResourceSample {
  sampled_at: string;
  process_cpu_percent: number | null;
  process_memory_gb: number | null;
  process_threads: number | null;
  system_memory_total_gb: number | null;
  system_memory_used_gb: number | null;
  system_memory_available_gb: number | null;
  load_average_1m: number | null;
  load_average_5m: number | null;
  load_average_15m: number | null;
  gpu_usage_percent: number | null;
}

export interface RunLiveStatus {
  run_id: string;
  title: string;
  status: "starting" | "running" | "completed" | "failed";
  phase: string;
  started_at: string;
  updated_at: string;
  completed_at: string | null;
  paths: {
    output_dir: string;
    local_status_path: string;
    public_status_path: string;
    run_plan_path: string;
  };
  plan: {
    model_name: string;
    dataset_path: string;
    total_steps: number;
    effective_epochs: number;
    batch_size: number;
    learning_rate: number;
  };
  progress: {
    current_step: number;
    current_epoch: number;
    target_epochs: number;
    last_train_loss: number | null;
    last_val_loss: number | null;
    last_learning_rate: number | null;
    last_trained_tokens: number | null;
    last_peak_memory_gb: number | null;
  };
  resources: {
    process_cpu_percent: number | null;
    process_memory_gb: number | null;
    process_threads: number | null;
    system_memory_total_gb: number | null;
    system_memory_used_gb: number | null;
    system_memory_available_gb: number | null;
    load_average_1m: number | null;
    load_average_5m: number | null;
    load_average_15m: number | null;
    gpu_usage_percent: number | null;
    gpu_live_supported: boolean;
    cpu_live_supported: boolean;
    memory_live_supported: boolean;
  };
  recent_train_points: TrainTelemetryPoint[];
  recent_eval_points: EvalTelemetryPoint[];
  recent_resource_samples: LiveResourceSample[];
  notes: string[];
  manifest_path?: string;
}

export interface RunSummary {
  manifest: RunManifest;
  probeResults: ProbeResult[];
  metrics: {
    total: number;
    exactNameMatch: number;
    anyExpectedNameHit: number;
    parsedJson: number;
    toolSignal: number;
    nonEmptyOutput: number;
    schemaEcho: number;
  };
  artifacts: RunArtifact[];
  trainingCurve: TrainingCurve;
  trainTelemetry: TrainTelemetryPoint[];
  evalTelemetry: EvalTelemetryPoint[];
  runPlan: RunPlanSummary | null;
  resourceSummary: RunResourceSummary;
  liveStatusPath: string;
  liveStatusSnapshot: RunLiveStatus | null;
}

export interface AgentPrompt {
  title: string;
  agent: string;
  prompt: string;
}

export interface WorkflowStage {
  id: string;
  title: string;
  commands: string[];
  teaching_goal: string;
  outputs: string[];
}

export interface OnboardingCheck {
  id: string;
  label: string;
  status: "ready" | "missing";
  detail: string;
  fix_command?: string;
  artifact_path?: string;
}

export interface OnboardingStep {
  title: string;
  command: string;
  reason: string;
}

export interface OnboardingReport {
  generated_at: string;
  repo: {
    name: string;
    root: string;
    tagline: string;
  };
  machine: Record<string, string | boolean | null>;
  overall_status: string;
  readiness: OnboardingCheck[];
  stage_readiness: Array<{
    id: string;
    title: string;
    status: "ready" | "partial" | "missing";
    ready_count: number;
    total_count: number;
    detail: string;
    command: string;
    artifacts: string[];
  }>;
  learning_progress: {
    completed_stage_ids: string[];
    completed_stage_count: number;
    total_stage_count: number;
    next_stage: {
      id: string;
      title: string;
      command: string;
    } | null;
  };
  next_steps: OnboardingStep[];
  agent_prompts: AgentPrompt[];
  workflow_stages: WorkflowStage[];
  reading_order: string[];
}

export interface ManifestoTenet {
  index: string;
  title: string;
  body: string;
}

export interface Manifesto {
  eyebrow: string;
  headline: string;
  lede: string;
  tenets: ManifestoTenet[];
  hero_commands: string[];
}

export interface AgentHandoffStep {
  step: string;
  eyebrow: string;
  title: string;
  command: string;
  body: string;
  artifact: string;
}

export interface TeachingTakeaway {
  number: string;
  title: string;
  body: string;
}

export interface GemmaTrackModel {
  name: string;
  role: string;
  why: string;
}

export interface GemmaTrackFocus {
  title: string;
  body: string;
}

export interface GemmaTrack {
  headline: string;
  summary: string;
  default_model: GemmaTrackModel;
  comparison_model: GemmaTrackModel;
  specialization_focus: GemmaTrackFocus;
  upgrade_path: string[];
}

export interface GemmaTrackPack {
  generated_at: string;
  headline: string;
  summary: string;
  checkpoints: Array<{
    name: string;
    type: string;
    teaching_role: string;
    best_for: string;
    strengths: string[];
    blind_spots: string[];
  }>;
  comparison_axes: Array<{
    axis: string;
    base: string;
    instruct: string;
    why_it_matters: string;
  }>;
  teaching_experiments: Array<{
    title: string;
    command: string;
    goal: string;
  }>;
  recommended_order: string[];
  teaching_notes: string[];
}

export interface LearningRoadmapLevel {
  id: string;
  label: string;
  title: string;
  status: "live" | "partial" | "next" | "planned";
  model: string;
  goal: string;
  why_it_matters: string;
  commands: string[];
  artifacts: string[];
  focus_metrics: string[];
  pitfall: string;
}

export interface LearningRoadmap {
  headline: string;
  summary: string;
  levels: LearningRoadmapLevel[];
}

export interface ReferenceProject {
  name: string;
  url: string;
  signal: string;
  takeaway: string;
  relation?: string;
}

export interface DatasetCardFrontmatter {
  name?: string;
  version?: string;
  generated_at?: string;
  generator?: string;
  total_samples?: number;
  splits?: Record<string, number>;
  license?: string;
  sensitivity?: string;
  pii_scanned?: boolean;
  pii_redacted_count?: number;
  policy_version_at_generation?: string;
  schema_ref?: string;
}

export interface RedactionReportFrontmatter {
  dataset?: string;
  generated_at?: string;
  policy_version?: string;
  records_scanned?: number;
  records_redacted?: number;
  match_counts?: Record<string, number>;
  fields_scanned?: string[];
  spot_check_count?: number;
}

export interface DatasetCard {
  dir_relative: string;
  frontmatter: DatasetCardFrontmatter;
  body: string;
  redaction: { frontmatter: RedactionReportFrontmatter; body: string } | null;
}

export interface Level1PromptSurface {
  kind: string;
  text: string;
}

export interface Level1TaskFramingPack {
  generated_at: string;
  dataset_path: string;
  task_brief: {
    title: string;
    user_job: string;
    target_behavior: string;
    why_finetune: string[];
  };
  dataset_profile: {
    total_samples: number;
    category_counts: Array<{ category: string; count: number }>;
    top_expected_tools: Array<{ tool_name: string; count: number }>;
    domain_counts: Array<{ domain: string; count: number }>;
  };
  success_rubric: Array<{
    criterion: string;
    pass_signal: string;
    fail_signal: string;
  }>;
  failure_buckets: Array<{
    bucket: string;
    label: string;
    description: string;
    why_it_matters: string;
    sample_count: number;
    example_case_id: string | null;
    affected_category: string;
  }>;
  held_out_seed_cases: Array<{
    id: string;
    category: string;
    prompt_surface: Level1PromptSurface;
    loaded_tool_names: string[];
    expected_tool_calls: Array<{ name: string; arguments: Record<string, unknown> }>;
    risk_flags: string[];
    rubric_focus: string[];
    baseline_hypothesis: string;
  }>;
  teaching_notes: string[];
}

export interface Level1BaselineEvalPack {
  generated_at: string;
  baseline_profile: {
    name: string;
    strategy: string;
    strengths: string[];
    weaknesses: string[];
  };
  summary: {
    case_count: number;
    route_selection_hit: number;
    executable_output: number;
    arguments_complete: number;
    full_chain_coverage: number;
    meta_reroute_correct: number;
    overall_pass: number;
    failure_bucket_counts: Array<{ bucket: string; count: number }>;
  };
  cases: Array<{
    id: string;
    category: string;
    prompt_surface: Level1PromptSurface;
    loaded_tool_names: string[];
    expected_tool_calls: Array<{ name: string; arguments: Record<string, unknown> }>;
    baseline_prediction: {
      strategy: string;
      output_shape: string;
      predicted_names: string[];
      raw_output: string;
    };
    scorecard: {
      route_selection_hit: boolean;
      executable_output: boolean;
      arguments_complete: boolean;
      full_chain_coverage: boolean;
      meta_reroute_correct: boolean;
      overall_pass: boolean;
    };
    likely_failure_bucket: string;
    lesson: string;
  }>;
  next_actions: string[];
  teaching_notes: string[];
}

export interface RunDelta {
  baseline: {
    run_id: string;
    title: string;
    max_steps: number;
    avg_loss: number;
    metrics: RunSummary["metrics"];
  };
  improved: {
    run_id: string;
    title: string;
    max_steps: number;
    avg_loss: number;
    metrics: RunSummary["metrics"];
  };
  avg_loss_delta: number;
  avg_loss_delta_pct: number | null;
  steps_multiplier: number | null;
  exact_delta: number;
  parsed_delta: number;
  signal_delta: number;
}

export interface ToolRoutingFocusSample {
  id: string;
  category: string;
  prompt_user: string | null;
  loaded_tool_names: string[];
  expected_name: string;
  expected_arguments: Record<string, unknown>;
  route_type: string;
}

export interface ToolRoutingPack {
  generated_at: string;
  summary: {
    total_samples: number;
    single_tool_samples: number;
    multi_tool_samples: number;
    distinct_tools: number;
    avg_candidate_count: number;
    candidate_histogram: Array<{ candidate_count: number; samples: number }>;
    domain_counts: Array<{ domain: string; count: number }>;
    route_counts: Array<{ tool_name: string; count: number; avg_candidate_count: number }>;
  };
  focus_samples: ToolRoutingFocusSample[];
  teaching_notes: string[];
}

export interface StructuredOutputPackCase {
  id: string;
  prompt_user: string | null;
  loaded_tool_names: string[];
  expected_names: string[];
  predicted_names: string[];
  output_shape: string;
  structured_output_valid: boolean;
  arguments_match: boolean;
  exact_name_match: boolean;
  raw_output: string;
}

export interface StructuredOutputPackRun {
  run_id: string;
  title: string;
  max_steps: number;
  model_name: string;
  summary: {
    total_cases: number;
    exact_name_match: number;
    json_valid: number;
    structured_output_valid: number;
    arguments_match: number;
    tool_signal: number;
    tool_name_only: number;
    tool_calls_array: number;
    schema_echo: number;
  };
  cases: StructuredOutputPackCase[];
}

export interface StructuredOutputCompareCase {
  id: string;
  prompt_user: string | null;
  expected_names: string[];
  loaded_tool_names: string[];
  runs: Array<{
    run_id: string;
    title: string;
    max_steps: number;
    predicted_names: string[];
    output_shape: string;
    structured_output_valid: boolean;
    arguments_match: boolean;
    exact_name_match: boolean;
  }>;
}

export interface StructuredOutputPack {
  generated_at: string;
  runs: StructuredOutputPackRun[];
  compare_cases: StructuredOutputCompareCase[];
  teaching_notes: string[];
}

export interface PreferenceDatasetPack {
  generated_at: string;
  dataset_path: string;
  summary: {
    pair_count: number;
    distinct_rejection_types: number;
    distinct_categories: number;
    event_driven_pairs: number;
    multi_call_pairs: number;
    rejection_counts: Array<{ rejection_type: string; count: number }>;
    category_counts: Array<{ category: string; count: number }>;
    chosen_shape: string;
  };
  focus_pairs: Array<{
    id: string;
    source_sample_id: string;
    category: string;
    prompt_user: string | null;
    prompt_kind: string;
    loaded_tool_names: string[];
    expected_tool_name: string;
    expected_tool_names: string[];
    expected_tool_calls: Array<{ name: string; arguments: Record<string, unknown> }>;
    has_event_context: boolean;
    preference_reason: string;
    rejection_type: string;
    chosen: {
      raw_output: string;
      output_shape: string;
    };
    rejected: {
      raw_output: string;
      output_shape: string;
    };
  }>;
  teaching_notes: string[];
}

export interface PolicyCompareReport {
  generated_at: string;
  policies: Array<{
    policy_id: string;
    title: string;
    summary: {
      chosen_win_rate: number;
      total_cases: number;
      structured_output_preference: number;
      weighted_rubric_score: number;
      hard_failure_cases: number;
      behavior: string;
    };
  }>;
  compare_cases: Array<{
    id: string;
    category: string;
    prompt_user: string | null;
    preference_reason: string;
    rejection_type: string;
    chosen_preview: string;
    rejected_preview: string;
    baseline_policy: {
      decision: string;
      win: boolean;
      notes: string;
      assessment: {
        predicted_names: string[];
        output_shape: string;
        score_points: number;
        criteria: Record<string, number | null>;
        hard_failures: string[];
      };
    };
    preference_policy: {
      decision: string;
      win: boolean;
      notes: string;
      assessment: {
        predicted_names: string[];
        output_shape: string;
        score_points: number;
        criteria: Record<string, number | null>;
        hard_failures: string[];
      };
    };
  }>;
  scale_up_guidance: Array<{
    step: string;
    title: string;
    body: string;
  }>;
  teaching_notes: string[];
}

export interface Level6ScaleUpRubric {
  generated_at: string;
  summary: {
    weighted_rubric_score: number;
    baseline_weighted_score: number;
    coverage_categories: number;
    pair_count: number;
  };
  criteria: Array<{
    id: string;
    title: string;
    weight: number;
    baseline_score: number;
    current_score: number;
    target_for_e4b: number;
    status: "pass" | "hold";
    why: string;
  }>;
  coverage: Array<{
    category: string;
    pairs: number;
    status: "pass" | "hold";
    why: string;
  }>;
  acceptance_bar: string[];
  cost_model: Array<{
    model: string;
    compute_class: string;
    iteration_speed: string;
    best_use: string;
  }>;
  experiment_plan: Array<{
    stage: string;
    title: string;
    goal: string;
  }>;
}

export interface Level6ScaleUpCompare {
  generated_at: string;
  current_state: {
    pair_count: number;
    rejection_types: number;
    coverage_categories: number;
    baseline_chosen_win_rate: {
      wins: number;
      total: number;
    };
    preference_chosen_win_rate: {
      wins: number;
      total: number;
    };
    win_gap_points: number;
    weighted_rubric_score: number;
    hard_failure_rate: number;
  };
  gates: Array<{
    gate: string;
    current: number;
    target_for_e4b: number;
    status: "pass" | "hold";
    why: string;
  }>;
  model_profiles: Array<{
    model: string;
    role: string;
    fit_score: number;
    best_for: string;
    strength: string;
    risk: string;
    cost_class: string;
    expected_cycle: string;
  }>;
  decision_matrix: Array<{
    criterion: string;
    current_state: string;
    e2b_it: string;
    e4b_it: string;
  }>;
  recommendation: {
    model: string;
    stage: string;
    summary: string;
    reasoning: string[];
    next_actions: string[];
  };
}

export interface BehaviorEvalPack {
  generated_at: string;
  teaching_notes: string[];
  runs: Array<{
    run_id: string;
    title: string;
    training_mode: string;
    model_name: string;
    max_steps: number;
    behavior_metrics: {
      total_cases: number;
      behavior_accuracy: {
        hit: number;
        total: number;
      };
      unsafe_direct_call_rate: {
        count: number;
        total: number;
      };
      high_risk_direct_call_rate: {
        count: number;
        total: number;
      };
      confirmation_contract_hit: {
        hit: number;
        total: number;
      };
      refusal_contract_hit: {
        hit: number;
        total: number;
      };
      predicted_behavior_counts: Record<string, number>;
    };
    behavior_counts: Record<string, number>;
    risk_counts: Record<string, number>;
    miss_cases: Array<{
      id: string;
      category: string;
      behavior: string;
      predicted_behavior: string;
      risk: string;
      unsafe_direct_call: boolean;
      confirmation_contract_hit: boolean;
      refusal_contract_hit: boolean;
      expected_system_action: {
        type: string;
        tool?: string;
        arguments?: Record<string, unknown>;
        expires_in_seconds?: number;
        reason_code?: string;
      } | null;
      predicted_names: string[];
    }>;
  }>;
}

export interface DataScaleComparePack {
  generated_at: string;
  scenarios: Array<{
    scenario_id: string;
    label: string;
    data_scale: "small" | "medium";
    strategy: "direct_mixed" | "curriculum_consolidation";
    strategy_label: string;
    run_dir: string;
    run_id: string;
    title: string;
    max_steps: number;
    avg_loss: number;
    dataset: {
      counts: {
        train: number;
        valid: number;
        test: number;
      };
      train_behaviors: Record<string, number>;
      test_behaviors: Record<string, number>;
      train_risks: Record<string, number>;
      test_risks: Record<string, number>;
      train_expected_system_actions: Record<string, number>;
      test_expected_system_actions: Record<string, number>;
    };
    metrics: {
      total_cases: number;
      exact_name_match: { hit: number; total: number; rate: number };
      structured_output_valid: { hit: number; total: number; rate: number };
      arguments_match: { hit: number; total: number; rate: number };
      behavior_accuracy: { hit: number; total: number; rate: number };
      unsafe_direct_call_rate: { count: number; total: number; rate: number };
      confirmation_contract_hit: { hit: number; total: number; rate: number };
      refusal_contract_hit: { hit: number; total: number; rate: number };
    };
  }>;
  matrix: Array<{
    metric: string;
    label: string;
    scenarios: Array<{
      scenario_id: string;
      label: string;
      value: number;
      total: number;
      rate: number;
    }>;
  }>;
  teaching_notes: string[];
}

export interface TrainingObservatoryPack {
  generated_at: string;
  latest_real_run_id: string | null;
  best_exact_run_id: string | null;
  best_behavior_run_id: string | null;
  live_polling_supported: boolean;
  telemetry_coverage: {
    run_count: number;
    train_metric_runs: number;
    eval_metric_runs: number;
    peak_memory_runs: number;
    live_cpu_usage_supported: boolean;
    live_gpu_usage_supported: boolean;
    live_memory_usage_supported: boolean;
  };
  host_machine: {
    platform: string | null;
    machine: string | null;
    python: string | null;
    node: string | null;
  };
  teaching_notes: string[];
}

export interface LabData {
  generated_at: string;
  project: {
    name: string;
    tagline: string;
    primary_goal: string;
  };
  beginner_guide_markdown: string | null;
  dataset_cards: DatasetCard[];
  manifesto: Manifesto | null;
  agent_handoff_timeline: AgentHandoffStep[];
  teaching_takeaways: TeachingTakeaway[];
  gemma_track: GemmaTrack | null;
  learning_roadmap: LearningRoadmap | null;
  reference_projects: ReferenceProject[];
  gemma_track_pack: GemmaTrackPack | null;
  level1: {
    task_framing_pack: Level1TaskFramingPack | null;
    baseline_eval_pack: Level1BaselineEvalPack | null;
  };
  level5: {
    tool_routing_pack: ToolRoutingPack | null;
    structured_output_pack: StructuredOutputPack | null;
  };
  behavior_eval_pack: BehaviorEvalPack | null;
  data_scale_compare_pack: DataScaleComparePack | null;
  observatory: TrainingObservatoryPack | null;
  level6: {
    preference_dataset_pack: PreferenceDatasetPack | null;
    policy_compare_report: PolicyCompareReport | null;
    scale_up_rubric: Level6ScaleUpRubric | null;
    scale_up_compare: Level6ScaleUpCompare | null;
  };
  source: { dataset: string; train_dataset: string; held_out_dataset: string };
  agent_prompts: AgentPrompt[];
  workflow_stages: WorkflowStage[];
  onboarding: OnboardingReport;
  dataset: {
    samples: DatasetSample[];
    summary: {
      total_samples: number;
      category_counts: Array<{ category: string; count: number }>;
      behavior_counts: Array<{ behavior: string; count: number }>;
      risk_counts: Array<{ risk: string; count: number }>;
      expected_system_action_counts: Array<{ action: string; count: number }>;
      generator_counts: Array<{ model: string; count: number }>;
      domain_counts: Array<{ domain: string; count: number }>;
    };
  };
  runs: RunSummary[];
  run_delta: RunDelta | null;
}

export async function loadLabData(): Promise<LabData> {
  if (window.location.protocol === "file:") {
    return embeddedLabData as unknown as LabData;
  }
  const dataUrl = new URL("lab-data.json", window.location.href).toString();
  try {
    const response = await fetch(dataUrl, { cache: "no-store" });
    if (response.ok) return (await response.json()) as LabData;
  } catch {
    // network error — fall through to the embedded snapshot
  }
  return embeddedLabData as unknown as LabData;
}
