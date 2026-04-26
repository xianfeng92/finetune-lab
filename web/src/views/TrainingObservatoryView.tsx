import { memo, useEffect, useMemo, useState } from "react";
import type {
  EvalTelemetryPoint,
  LabData,
  LiveResourceSample,
  RunLiveStatus,
  RunSummary,
  TrainTelemetryPoint,
  TrainingCurve,
} from "../data-layer";
import { Term } from "../components/Term";
import { KpiCard, LossCurve, RunModeBadge, SectionTitle, formatRatio } from "../components/ui";

interface RunLiveIndex {
  generated_at: string;
  latest_run_id: string | null;
  status: RunLiveStatus["status"] | null;
  updated_at: string | null;
  run_path: string | null;
}

function formatMaybe(value: number | null, digits = 2) {
  if (value === null || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}

function isFileProtocol() {
  return typeof window !== "undefined" && window.location.protocol === "file:";
}

async function fetchJson<T>(path: string): Promise<T | null> {
  const response = await fetch(`./${path}?t=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) return null;
  return response.json();
}

async function fetchLiveIndex(): Promise<RunLiveIndex | null> {
  return fetchJson<RunLiveIndex>("run-live/index.json");
}

async function fetchLiveStatusPath(path: string): Promise<RunLiveStatus | null> {
  return fetchJson<RunLiveStatus>(path);
}

async function fetchLiveStatus(run: RunSummary): Promise<RunLiveStatus | null> {
  return fetchLiveStatusPath(run.liveStatusPath);
}

function toEvalCurve(points: EvalTelemetryPoint[]): TrainingCurve {
  if (!points.length) {
    return { total_steps: 0, first_loss: null, last_loss: null, loss_delta_pct: null, points: [] };
  }
  const first = points[0].val_loss;
  const last = points[points.length - 1].val_loss;
  return {
    total_steps: points.length,
    first_loss: first,
    last_loss: last,
    loss_delta_pct: first !== 0 ? +(((first - last) / first) * 100).toFixed(1) : null,
    points: points.map((point) => ({ step: point.step, loss: point.val_loss })),
  };
}

function toTrainCurve(points: TrainTelemetryPoint[]): TrainingCurve {
  if (!points.length) {
    return { total_steps: 0, first_loss: null, last_loss: null, loss_delta_pct: null, points: [] };
  }
  const first = points[0].loss;
  const last = points[points.length - 1].loss;
  return {
    total_steps: points.length,
    first_loss: first,
    last_loss: last,
    loss_delta_pct: first !== 0 ? +(((first - last) / first) * 100).toFixed(1) : null,
    points: points.map((point) => ({ step: point.step, loss: point.loss })),
  };
}

function mergeTrainTelemetry(base: TrainTelemetryPoint[], live: TrainTelemetryPoint[]): TrainTelemetryPoint[] {
  const byStep = new Map<number, TrainTelemetryPoint>();
  for (const point of base) byStep.set(point.step, point);
  for (const point of live) byStep.set(point.step, point);
  return [...byStep.values()].sort((a, b) => a.step - b.step);
}

function mergeEvalTelemetry(base: EvalTelemetryPoint[], live: EvalTelemetryPoint[]): EvalTelemetryPoint[] {
  const byStep = new Map<number, EvalTelemetryPoint>();
  for (const point of base) byStep.set(point.step, point);
  for (const point of live) byStep.set(point.step, point);
  return [...byStep.values()].sort((a, b) => a.step - b.step);
}

function buildRunLabel(run: RunSummary) {
  const family = run.manifest.family ?? "run";
  return `${family} · ${run.manifest.max_steps} steps`;
}

function exactRate(run: RunSummary) {
  return run.metrics.total ? run.metrics.exactNameMatch / run.metrics.total : 0;
}

function behaviorRate(run: RunSummary) {
  return run.probeResults.length ? run.probeResults.filter((row) => row.behavior_match).length / run.probeResults.length : 0;
}

function buildLiveOnlyRun(liveStatus: RunLiveStatus, liveStatusPath: string): RunSummary {
  const outputDir = liveStatus.paths.output_dir;
  const recentEvalLosses = liveStatus.recent_eval_points.map((point) => point.val_loss);
  return {
    manifest: {
      run_id: liveStatus.run_id,
      title: liveStatus.title,
      engine: "mlx_lm.lora",
      training_mode: "real",
      model_name: liveStatus.plan.model_name,
      dataset_path: liveStatus.plan.dataset_path,
      adapter_dir: `${outputDir}/adapter`,
      max_steps: liveStatus.plan.total_steps,
      avg_loss: liveStatus.progress.last_train_loss ?? 0,
      probe_results_path: `${outputDir}/inference-probe-results.json`,
      probe_report_path: `${outputDir}/inference-probe-report.md`,
      live_status_path: liveStatus.paths.local_status_path,
      public_live_status_path: liveStatusPath,
      family: outputDir.split("/").filter(Boolean).slice(-1)[0] ?? liveStatus.run_id,
      is_top_level: true,
      completed_at: liveStatus.completed_at ?? liveStatus.updated_at,
    },
    probeResults: [],
    metrics: {
      total: 0,
      exactNameMatch: 0,
      anyExpectedNameHit: 0,
      parsedJson: 0,
      toolSignal: 0,
      nonEmptyOutput: 0,
      schemaEcho: 0,
    },
    artifacts: [],
    trainingCurve: toTrainCurve(liveStatus.recent_train_points),
    trainTelemetry: liveStatus.recent_train_points,
    evalTelemetry: liveStatus.recent_eval_points,
    runPlan: {
      requested_epochs: liveStatus.progress.target_epochs,
      effective_epochs: liveStatus.plan.effective_epochs,
      batch_size: liveStatus.plan.batch_size,
      learning_rate: liveStatus.plan.learning_rate,
      steps_per_report: null,
      steps_per_eval: null,
      save_every: null,
      max_seq_length: null,
      num_layers: null,
      compat_patch: null,
      resume_adapter_file: null,
    },
    resourceSummary: {
      peak_memory_gb: liveStatus.progress.last_peak_memory_gb,
      avg_iterations_per_second: null,
      avg_tokens_per_second: null,
      last_trained_tokens: liveStatus.progress.last_trained_tokens,
      best_val_loss: recentEvalLosses.length ? Math.min(...recentEvalLosses) : null,
      last_val_loss: liveStatus.progress.last_val_loss,
      avg_val_time_s: null,
      last_val_time_s: liveStatus.recent_eval_points[liveStatus.recent_eval_points.length - 1]?.val_time_s ?? null,
      host_platform: null,
      host_arch: null,
      live_cpu_usage_supported: liveStatus.resources.cpu_live_supported,
      live_gpu_usage_supported: liveStatus.resources.gpu_live_supported,
      live_memory_usage_supported: liveStatus.resources.memory_live_supported,
      run_plan: {
        batch_size: liveStatus.plan.batch_size,
        requested_epochs: liveStatus.progress.target_epochs,
        effective_epochs: liveStatus.plan.effective_epochs,
        steps_per_report: null,
        steps_per_eval: null,
        save_every: null,
      },
    },
    liveStatusPath,
    liveStatusSnapshot: liveStatus,
  };
}

function mergeLiveRun(runs: RunSummary[], liveStatus: RunLiveStatus | null, liveStatusPath: string | null) {
  if (!liveStatus || !liveStatusPath) return runs;
  let matched = false;
  const merged = runs.map((run) => {
    if (run.manifest.run_id !== liveStatus.run_id) return run;
    matched = true;
    return {
      ...run,
      liveStatusPath,
      liveStatusSnapshot: liveStatus,
    };
  });
  return matched ? merged : [buildLiveOnlyRun(liveStatus, liveStatusPath), ...merged];
}

function telemetryRows(trainTelemetry: TrainTelemetryPoint[]) {
  return trainTelemetry.slice(-8).reverse();
}

function coverageLabel(supported: boolean) {
  return supported ? "live" : "planned";
}

function statusLabel(status: RunLiveStatus["status"] | "static") {
  return status;
}

function RunPicker(props: { runs: RunSummary[]; selectedRunId: string; liveIndex: RunLiveIndex | null; onSelect: (id: string) => void }) {
  return (
    <section className="panel">
      <SectionTitle title="Run picker" subtitle="优先看 REAL run。这里会轮询 run-live/index.json，训练开始后不用刷新页面也能跟到最新 live 文件。" audience="工程" />
      <div className="sample-list compact">
        {props.runs.map((run) => {
          const isIndexedLive = props.liveIndex?.latest_run_id === run.manifest.run_id;
          return (
            <button
              key={run.manifest.run_id}
              type="button"
              className={`sample-item ${props.selectedRunId === run.manifest.run_id ? "active" : ""}`}
              onClick={() => props.onSelect(run.manifest.run_id)}
            >
              <div className="sample-item-head">
                <span>{buildRunLabel(run)}</span>
                <span className="observatory-run-badges">
                  {isIndexedLive ? <span className="observatory-live-pill">{props.liveIndex?.status ?? "live"}</span> : null}
                  <RunModeBadge run={run} />
                </span>
              </div>
              <strong>{run.manifest.title}</strong>
              <span className="observatory-run-subtle">{run.manifest.model_name}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function RunControlRoom(props: { run: RunSummary; liveStatus: RunLiveStatus | null }) {
  const run = props.run;
  const live = props.liveStatus;
  const bestEval = run.resourceSummary.best_val_loss;
  const lastEval = live?.progress.last_val_loss ?? run.resourceSummary.last_val_loss;
  const plan = run.runPlan;
  return (
    <section className="panel">
      <SectionTitle title="Control room" subtitle="这一栏集中看当前 run 的配方、loss、throughput 和资源摘要。" audience="工程" />
      <div className="run-card">
        <div className="run-card-head">
          <div className="run-tag">{run.manifest.engine}</div>
          <RunModeBadge run={run} />
        </div>
        <h3>{run.manifest.title}</h3>
        <p>{run.manifest.model_name}</p>
        <dl className="run-stats">
          <div><dt>status</dt><dd>{statusLabel(live?.status ?? "static")}</dd></div>
          <div><dt>updated</dt><dd>{live?.updated_at ?? "static snapshot"}</dd></div>
          <div><dt>dataset</dt><dd>{run.manifest.dataset_path}</dd></div>
          <div><dt>steps</dt><dd>{run.manifest.max_steps}</dd></div>
          <div><dt>current step</dt><dd>{live?.progress.current_step ?? run.trainingCurve.total_steps ?? "—"}</dd></div>
          <div><dt>current epoch</dt><dd>{live?.progress.current_epoch ?? plan?.effective_epochs ?? "—"}</dd></div>
          <div><dt>train rows</dt><dd>{run.manifest.train_row_count ?? "—"}</dd></div>
          <div><dt>avg loss</dt><dd>{run.manifest.avg_loss.toFixed(4)}</dd></div>
          <div><dt>best val loss</dt><dd>{formatMaybe(bestEval, 3)}</dd></div>
          <div><dt>last val loss</dt><dd>{formatMaybe(lastEval, 3)}</dd></div>
          <div><dt>epochs</dt><dd>{plan?.effective_epochs ?? "—"}</dd></div>
          <div><dt>batch size</dt><dd>{plan?.batch_size ?? "—"}</dd></div>
          <div><dt>lr</dt><dd>{plan?.learning_rate ?? "—"}</dd></div>
          <div><dt>steps / eval</dt><dd>{plan?.steps_per_eval ?? "—"}</dd></div>
          <div><dt>save every</dt><dd>{plan?.save_every ?? "—"}</dd></div>
          <div><dt>compat patch</dt><dd>{plan?.compat_patch ?? "—"}</dd></div>
        </dl>
      </div>
    </section>
  );
}

function ObservatoryHero(props: { data: LabData; runs: RunSummary[]; liveStatus: RunLiveStatus | null }) {
  const liveLatest = props.liveStatus
    ? props.runs.find((run) => run.manifest.run_id === props.liveStatus?.run_id) ?? null
    : null;
  const latest = liveLatest ?? (props.data.observatory?.latest_real_run_id
    ? props.runs.find((run) => run.manifest.run_id === props.data.observatory?.latest_real_run_id) ?? props.runs[0]
    : props.runs[0]);
  const bestExact = props.data.observatory?.best_exact_run_id
    ? props.runs.find((run) => run.manifest.run_id === props.data.observatory?.best_exact_run_id) ?? null
    : null;
  const bestBehavior = props.data.observatory?.best_behavior_run_id
    ? props.runs.find((run) => run.manifest.run_id === props.data.observatory?.best_behavior_run_id) ?? null
    : null;
  return (
    <section className="panel span-2">
      <SectionTitle
        title="Training Observatory"
        subtitle={<>这不是另一个普通 <Term term="dashboard">dashboard</Term>。它把训练曲线、行为级 <Term term="probe">probe</Term>、资源摘要和运行配方放到一个视图里，帮助你解释“模型正在怎么学”。</>}
        audience="工程"
      />
      <div className="kpi-grid kpi-grid-5 observatory-hero-grid">
        <KpiCard label="latest real run" value={latest?.manifest.max_steps ? `${latest.manifest.max_steps} steps` : "—"} hint={latest?.manifest.title ?? "no real run"} accent />
        <KpiCard label="best exact" value={bestExact ? `${Math.round(exactRate(bestExact) * 100)}%` : "—"} hint={bestExact?.manifest.title ?? "—"} />
        <KpiCard label="best behavior" value={bestBehavior ? `${Math.round(behaviorRate(bestBehavior) * 100)}%` : "—"} hint={bestBehavior?.manifest.title ?? "—"} />
        <KpiCard label="peak mem coverage" value={props.data.observatory ? `${props.data.observatory.telemetry_coverage.peak_memory_runs}/${props.data.observatory.telemetry_coverage.run_count}` : "—"} hint="有多少 real runs 已经记录了 peak_memory_gb" />
        <KpiCard label="live cpu/gpu" value={props.data.observatory?.telemetry_coverage.live_cpu_usage_supported ? "cpu/mem live" : "planned"} hint="第二版已接半实时 CPU / memory；Apple GPU usage 仍保留为 planned" />
      </div>
    </section>
  );
}

function ResourcePanel(props: { data: LabData; run: RunSummary; liveStatus: RunLiveStatus | null; pollingDisabled: boolean }) {
  const summary = props.run.resourceSummary;
  const live = props.liveStatus;
  return (
    <section className="panel">
      <SectionTitle title="Resources" subtitle="优先展示训练期间真实采到的 throughput / peak memory，再补主机静态信息。" audience="工程" />
      <div className="kpi-grid observatory-resource-grid">
        <KpiCard label="peak memory" value={summary.peak_memory_gb !== null ? `${summary.peak_memory_gb.toFixed(2)} GB` : "—"} hint="来自 train-metrics.jsonl 的 peak_memory_gb" accent />
        <KpiCard label="avg it/s" value={summary.avg_iterations_per_second !== null ? summary.avg_iterations_per_second.toFixed(2) : "—"} hint="训练平均 iterations per second" />
        <KpiCard label="avg tok/s" value={summary.avg_tokens_per_second !== null ? summary.avg_tokens_per_second.toFixed(1) : "—"} hint="训练平均 tokens per second" />
        <KpiCard label="last eval" value={summary.last_val_time_s !== null ? `${summary.last_val_time_s.toFixed(1)}s` : "—"} hint="最后一次 validation 耗时" />
        <KpiCard label="live cpu" value={live?.resources.process_cpu_percent !== null && live?.resources.process_cpu_percent !== undefined ? `${live.resources.process_cpu_percent.toFixed(1)}%` : "—"} hint={props.pollingDisabled ? "file:// 下不轮询；HTTP 预览时可半实时刷新" : "训练进程 CPU 占用"} />
        <KpiCard label="live mem" value={live?.resources.process_memory_gb !== null && live?.resources.process_memory_gb !== undefined ? `${live.resources.process_memory_gb.toFixed(2)} GB` : "—"} hint="训练进程当前 RSS" />
        <KpiCard label="system mem" value={live && live.resources.system_memory_used_gb !== null && live.resources.system_memory_total_gb !== null ? `${live.resources.system_memory_used_gb.toFixed(1)} / ${live.resources.system_memory_total_gb.toFixed(1)} GB` : "—"} hint="系统当前内存占用" />
      </div>
      <dl className="run-stats observatory-machine-stats">
        <div><dt>host platform</dt><dd>{props.data.observatory?.host_machine.platform ?? "—"}</dd></div>
        <div><dt>host arch</dt><dd>{props.data.observatory?.host_machine.machine ?? "—"}</dd></div>
        <div><dt>python</dt><dd>{props.data.observatory?.host_machine.python ?? "—"}</dd></div>
        <div><dt>node</dt><dd>{props.data.observatory?.host_machine.node ?? "—"}</dd></div>
        <div><dt>CPU usage</dt><dd>{coverageLabel(live?.resources.cpu_live_supported ?? summary.live_cpu_usage_supported)}</dd></div>
        <div><dt>GPU usage</dt><dd>{coverageLabel(live?.resources.gpu_live_supported ?? summary.live_gpu_usage_supported)}</dd></div>
        <div><dt>memory live</dt><dd>{coverageLabel(live?.resources.memory_live_supported ?? summary.live_memory_usage_supported)}</dd></div>
        <div><dt>last sample</dt><dd>{live?.updated_at ?? "—"}</dd></div>
      </dl>
    </section>
  );
}

function ProbeKpiPanel(props: { run: RunSummary }) {
  const run = props.run;
  const rows = run.probeResults;
  const behaviorHits = rows.filter((row) => row.behavior_match).length;
  const confirmTotal = rows.filter((row) => row.behavior === "confirm").length;
  const confirmHit = rows.filter((row) => row.behavior === "confirm" && row.confirmation_contract_hit).length;
  const rejectTotal = rows.filter((row) => row.behavior === "reject").length;
  const rejectHit = rows.filter((row) => row.behavior === "reject" && row.refusal_contract_hit).length;
  const unsafeCount = rows.filter((row) => row.unsafe_direct_call).length;
  return (
    <section className="panel span-2">
      <SectionTitle title="Behavior KPIs" subtitle="这组指标回答的不是“loss 漂不漂亮”，而是“模型是否真的做对了工具选择、行为决策和安全 contract”。" audience="工程" />
      <div className="kpi-grid kpi-grid-5">
        <KpiCard label="exact" value={formatRatio(run.metrics.exactNameMatch, run.metrics.total)} hint="工具名是否完全命中" accent />
        <KpiCard label="structured" value={formatRatio(rows.filter((row) => row.structured_output_valid).length, rows.length)} hint="结构化输出是否可被系统消费" />
        <KpiCard label="args" value={formatRatio(rows.filter((row) => row.arguments_match).length, rows.length)} hint="参数是否对齐预期" />
        <KpiCard label="behavior" value={formatRatio(behaviorHits, rows.length)} hint="tool_call / clarify / confirm / reject / handoff 是否做对" />
        <KpiCard label="unsafe" value={formatRatio(unsafeCount, rows.length)} hint="不该直接调用工具的 case 里是否越界执行" />
      </div>
      <div className="observatory-contracts">
        <article className="observatory-contract-card">
          <strong>confirm contract</strong>
          <p>{formatRatio(confirmHit, confirmTotal)}</p>
        </article>
        <article className="observatory-contract-card">
          <strong>reject contract</strong>
          <p>{formatRatio(rejectHit, rejectTotal)}</p>
        </article>
      </div>
    </section>
  );
}

function TelemetryCharts(props: { trainTelemetry: TrainTelemetryPoint[]; evalTelemetry: EvalTelemetryPoint[] }) {
  const trainCurve = useMemo(() => toTrainCurve(props.trainTelemetry), [props.trainTelemetry]);
  const evalCurve = useMemo(() => toEvalCurve(props.evalTelemetry), [props.evalTelemetry]);
  const bestEval = props.evalTelemetry.length ? Math.min(...props.evalTelemetry.map((point) => point.val_loss)) : null;
  return (
    <section className="panel span-2">
      <SectionTitle title="Curves" subtitle="第一张是 train loss，第二张是 validation loss。训练曲线和行为指标要并排看，不能只看 loss。" audience="工程" />
      <div className="curve-row observatory-curve-row">
        <article className="curve-card lime">
          <div className="curve-head">
            <div>
              <div className="eyebrow">train-metrics.jsonl + live tail</div>
              <h3>Train loss</h3>
            </div>
            <div className="curve-delta">
              <div className="delta-label">delta</div>
              <div className="delta-value">{trainCurve.loss_delta_pct !== null ? `${trainCurve.loss_delta_pct}%` : "—"}</div>
            </div>
          </div>
          <LossCurve curve={trainCurve} tone="lime" />
        </article>
        <article className="curve-card magenta">
          <div className="curve-head">
            <div>
              <div className="eyebrow">eval-metrics.jsonl + live tail</div>
              <h3>Validation loss</h3>
            </div>
            <div className="curve-delta">
              <div className="delta-label">best</div>
              <div className="delta-value">{formatMaybe(bestEval, 3)}</div>
            </div>
          </div>
          <LossCurve curve={evalCurve} tone="magenta" />
        </article>
      </div>
    </section>
  );
}

function TelemetryTable(props: { trainTelemetry: TrainTelemetryPoint[]; liveStatus: RunLiveStatus | null }) {
  const rows = telemetryRows(props.trainTelemetry);
  const resourceRows = (props.liveStatus?.recent_resource_samples ?? []).slice(-6).reverse();
  return (
    <section className="panel span-2">
      <SectionTitle title="Telemetry snapshots" subtitle="直接从 train-metrics.jsonl 取最后 8 个点，用来回答速度、tokens 和 peak memory 在训练过程中是怎么变化的。" audience="工程" />
      <div className="observatory-table-wrap">
        <table className="observatory-table">
          <thead>
            <tr>
              <th>step</th>
              <th>loss</th>
              <th>lr</th>
              <th>it/s</th>
              <th>tok/s</th>
              <th>trained tokens</th>
              <th>peak mem</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.step}>
                <td>{row.step}</td>
                <td>{row.loss.toFixed(3)}</td>
                <td>{row.learning_rate ?? "—"}</td>
                <td>{formatMaybe(row.iterations_per_second, 2)}</td>
                <td>{formatMaybe(row.tokens_per_second, 1)}</td>
                <td>{row.trained_tokens ?? "—"}</td>
                <td>{row.peak_memory_gb !== null ? `${row.peak_memory_gb.toFixed(2)} GB` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {resourceRows.length ? (
        <div className="observatory-table-wrap">
          <table className="observatory-table">
            <thead>
              <tr>
                <th>sampled</th>
                <th>cpu %</th>
                <th>proc mem</th>
                <th>system mem</th>
                <th>threads</th>
                <th>load1</th>
              </tr>
            </thead>
            <tbody>
              {resourceRows.map((row: LiveResourceSample) => (
                <tr key={row.sampled_at}>
                  <td>{row.sampled_at}</td>
                  <td>{formatMaybe(row.process_cpu_percent, 1)}</td>
                  <td>{row.process_memory_gb !== null ? `${row.process_memory_gb.toFixed(2)} GB` : "—"}</td>
                  <td>{row.system_memory_used_gb !== null && row.system_memory_total_gb !== null ? `${row.system_memory_used_gb.toFixed(1)} / ${row.system_memory_total_gb.toFixed(1)} GB` : "—"}</td>
                  <td>{row.process_threads ?? "—"}</td>
                  <td>{formatMaybe(row.load_average_1m, 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

function TrainingObservatoryViewImpl(props: { data: LabData }) {
  const pollingDisabled = isFileProtocol();
  const baseRealRuns = useMemo(
    () => props.data.runs.filter((run) => run.manifest.training_mode !== "simulated").sort((a, b) => {
      const ta = a.manifest.completed_at ? Date.parse(a.manifest.completed_at) : 0;
      const tb = b.manifest.completed_at ? Date.parse(b.manifest.completed_at) : 0;
      return tb - ta;
    }),
    [props.data.runs],
  );
  const [liveIndex, setLiveIndex] = useState<RunLiveIndex | null>(null);
  const [indexedLiveStatus, setIndexedLiveStatus] = useState<RunLiveStatus | null>(null);
  const liveIndexPath = liveIndex?.run_path ?? indexedLiveStatus?.paths.public_status_path ?? null;
  const realRuns = useMemo(
    () => mergeLiveRun(baseRealRuns, indexedLiveStatus, liveIndexPath).sort((a, b) => {
      const ta = a.manifest.completed_at ? Date.parse(a.manifest.completed_at) : 0;
      const tb = b.manifest.completed_at ? Date.parse(b.manifest.completed_at) : 0;
      return tb - ta;
    }),
    [baseRealRuns, indexedLiveStatus, liveIndexPath],
  );
  const defaultRunId = indexedLiveStatus?.run_id ?? props.data.observatory?.latest_real_run_id ?? realRuns[0]?.manifest.run_id ?? "";
  const [selectedRunId, setSelectedRunId] = useState(defaultRunId);
  const [userPinnedRun, setUserPinnedRun] = useState(false);
  const [liveStatus, setLiveStatus] = useState<RunLiveStatus | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const selectedRun = realRuns.find((run) => run.manifest.run_id === selectedRunId) ?? realRuns[0] ?? null;

  useEffect(() => {
    if (!selectedRunId && defaultRunId) setSelectedRunId(defaultRunId);
  }, [defaultRunId, selectedRunId]);

  useEffect(() => {
    if (pollingDisabled) return undefined;
    let cancelled = false;
    let timer: number | undefined;

    async function tick() {
      try {
        const nextIndex = await fetchLiveIndex();
        if (cancelled || !nextIndex) return;
        setLiveIndex(nextIndex);
        const nextStatus = nextIndex.run_path ? await fetchLiveStatusPath(nextIndex.run_path) : null;
        if (cancelled) return;
        setIndexedLiveStatus(nextStatus);
        if (!userPinnedRun && nextStatus?.run_id) {
          setSelectedRunId(nextStatus.run_id);
        }
      } catch {
        if (!cancelled) {
          setLiveIndex(null);
          setIndexedLiveStatus(null);
        }
      }
    }

    tick();
    timer = window.setInterval(tick, 2000);
    return () => {
      cancelled = true;
      if (timer) window.clearInterval(timer);
    };
  }, [pollingDisabled, userPinnedRun]);

  useEffect(() => {
    if (!selectedRun) return undefined;
    let cancelled = false;
    let timer: number | undefined;

    if (pollingDisabled) {
      setLiveStatus(selectedRun.liveStatusSnapshot ?? null);
      setLiveError("file-protocol");
      return undefined;
    }

    async function tick() {
      try {
        const next = await fetchLiveStatus(selectedRun);
        if (!cancelled) {
          setLiveStatus(next ?? selectedRun.liveStatusSnapshot ?? null);
          setLiveError(null);
        }
      } catch {
        if (!cancelled) {
          setLiveStatus(selectedRun.liveStatusSnapshot ?? null);
          setLiveError("fetch-failed");
        }
      }
    }

    tick();
    timer = window.setInterval(tick, 2000);
    return () => {
      cancelled = true;
      if (timer) window.clearInterval(timer);
    };
  }, [selectedRun, pollingDisabled]);

  if (!selectedRun) {
    return (
      <section className="panel span-2">
        <SectionTitle title="Training Observatory" subtitle="当前还没有 real run，可先执行 `make real-train-mac` 或更高层的 compare 入口。" audience="工程" />
      </section>
    );
  }

  const mergedTrainTelemetry = mergeTrainTelemetry(
    selectedRun.trainTelemetry,
    liveStatus?.recent_train_points ?? [],
  );
  const mergedEvalTelemetry = mergeEvalTelemetry(
    selectedRun.evalTelemetry,
    liveStatus?.recent_eval_points ?? [],
  );

  return (
    <div className="view-grid">
      <ObservatoryHero data={props.data} runs={realRuns} liveStatus={indexedLiveStatus} />
      <RunPicker
        runs={realRuns}
        selectedRunId={selectedRun.manifest.run_id}
        liveIndex={liveIndex}
        onSelect={(id) => {
          setUserPinnedRun(true);
          setSelectedRunId(id);
        }}
      />
      <RunControlRoom run={selectedRun} liveStatus={liveStatus} />
      <TelemetryCharts trainTelemetry={mergedTrainTelemetry} evalTelemetry={mergedEvalTelemetry} />
      <ResourcePanel data={props.data} run={selectedRun} liveStatus={liveStatus} pollingDisabled={pollingDisabled} />
      <ProbeKpiPanel run={selectedRun} />
      <TelemetryTable trainTelemetry={mergedTrainTelemetry} liveStatus={liveStatus} />
      {liveError ? (
        <section className="panel span-2">
          <SectionTitle title="Live mode note" subtitle="半实时模式依赖浏览器通过 HTTP 读取 `run-live/*.json`。如果你现在是在 `file://` 静态页里看，Observatory 会自动回退到最后一次静态快照。" audience="工程" />
        </section>
      ) : null}
    </div>
  );
}

export const TrainingObservatoryView = memo(TrainingObservatoryViewImpl);
