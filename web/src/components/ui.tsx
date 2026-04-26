import type { RunSummary, TrainingCurve } from "../data-layer";
import { AUDIENCE_KEY, type Audience } from "../ui-types";

export function AudienceChip(props: { audience?: Audience }) {
  if (!props.audience) return null;
  return (
    <span className="audience-chip" data-audience={AUDIENCE_KEY[props.audience]}>
      面向：{props.audience}
    </span>
  );
}

export function SectionTitle(props: { title: string; subtitle: React.ReactNode; audience?: Audience }) {
  return (
    <header className="section-title">
      <div className="section-title-row">
        <div className="eyebrow">finetune-lab</div>
        <AudienceChip audience={props.audience} />
      </div>
      <h2>{props.title}</h2>
      <p>{props.subtitle}</p>
    </header>
  );
}

export function KpiCard(props: { label: string; value: string; hint: string; accent?: boolean }) {
  return (
    <article className={`kpi-card ${props.accent ? "accent" : ""}`}>
      <div className="kpi-label">{props.label}</div>
      <div className="kpi-value">{props.value}</div>
      <div className="kpi-hint">{props.hint}</div>
    </article>
  );
}

export function StatusBadge(props: { status: string }) {
  return <span className={`status-badge ${props.status}`}>{props.status}</span>;
}

export function CollapsiblePanel(props: { title: string; subtitle: React.ReactNode; audience?: Audience; defaultOpen?: boolean; children: React.ReactNode; spanFull?: boolean }) {
  return (
    <details open={props.defaultOpen ?? false} className={`panel panel-collapsible ${props.spanFull === false ? "" : "span-2"}`}>
      <summary className="panel-summary">
        <div className="panel-summary-text">
          <div className="section-title-row">
            <div className="eyebrow">finetune-lab</div>
            <AudienceChip audience={props.audience} />
          </div>
          <h2>{props.title}</h2>
          <p>{props.subtitle}</p>
        </div>
        <span className="panel-summary-chevron" aria-hidden="true">▾</span>
      </summary>
      <div className="panel-body">{props.children}</div>
    </details>
  );
}

export function datasetScope(datasetPath?: string): string {
  if (!datasetPath) return "?";
  const segments = datasetPath.split("/").filter(Boolean);
  return segments[segments.length - 2] ?? segments[segments.length - 1] ?? "?";
}

export function RunModeBadge(props: { run: RunSummary }) {
  const isSim = props.run.manifest.training_mode === "simulated";
  return (
    <span className={`run-mode-badge ${isSim ? "sim" : "real"}`} title={isSim ? "教学用 simulated 数据，没有真实更新模型" : "真实 LoRA 微调跑出来的"}>
      {isSim ? "SIM" : "REAL"}
    </span>
  );
}

export function RoadmapBadge(props: { status: "live" | "partial" | "next" | "planned" }) {
  return <span className={`roadmap-badge ${props.status}`}>{props.status}</span>;
}

export function formatRatio(value: number, total: number) {
  return `${value}/${total}`;
}

export function ChartBars(props: { items: Array<{ label: string; value: number }>; tone?: string; total?: number }) {
  const tone = props.tone ?? "lime";
  const max = Math.max(...props.items.map((item) => item.value), 1);
  return (
    <div className="chart-bars">
      {props.items.map((item) => (
        <div key={item.label} className="chart-row">
          <div className="chart-head">
            <span>{item.label}</span>
            <strong>
              {item.value}
              {props.total ? <span className="chart-denom"> / {props.total}</span> : null}
            </strong>
          </div>
          <div className="bar-shell">
            <div className={`bar-fill ${tone}`} style={{ width: `${(item.value / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function MetricBar(props: { n: number; d: number }) {
  const pct = props.d > 0 ? (props.n / props.d) * 100 : 0;
  return (
    <span className="metric-bar" aria-hidden="true">
      <span className="metric-bar-fill" style={{ width: `${pct}%` }} />
    </span>
  );
}

export function LossCurve(props: { curve: TrainingCurve; tone: "lime" | "magenta"; yMin?: number; yMax?: number }) {
  const points = props.curve.points;
  if (!points.length) return <div className="curve-empty">no train-metrics.jsonl</div>;
  const width = 640;
  const height = 200;
  const padL = 44;
  const padR = 12;
  const padT = 12;
  const padB = 26;
  const steps = points.map((p) => p.step);
  const losses = points.map((p) => p.loss);
  const minStep = Math.min(...steps);
  const maxStep = Math.max(...steps);
  const localMin = Math.min(...losses);
  const localMax = Math.max(...losses);
  const minLoss = props.yMin ?? localMin;
  const maxLoss = props.yMax ?? localMax;
  const stepSpan = Math.max(1, maxStep - minStep);
  const lossSpan = Math.max(0.0001, maxLoss - minLoss);
  const toX = (s: number) => padL + ((s - minStep) / stepSpan) * (width - padL - padR);
  const toY = (l: number) => padT + (1 - (l - minLoss) / lossSpan) * (height - padT - padB);
  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.step).toFixed(1)},${toY(p.loss).toFixed(1)}`)
    .join(" ");
  const yTicks = [maxLoss, (maxLoss + minLoss) / 2, minLoss];
  const xTicks = [minStep, Math.round((minStep + maxStep) / 2), maxStep];
  const fmtY = (v: number) => (Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2));
  return (
    <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className={`loss-svg ${props.tone}`} role="img" aria-label="training loss curve">
      {yTicks.map((t, i) => {
        const y = toY(t);
        return (
          <g key={`y-${i}`} className="loss-grid">
            <line x1={padL} x2={width - padR} y1={y} y2={y} stroke="rgba(255,255,255,0.06)" strokeDasharray="2 4" />
            <text x={padL - 6} y={y + 4} textAnchor="end" className="loss-axis-text">{fmtY(t)}</text>
          </g>
        );
      })}
      {xTicks.map((s, i) => {
        const x = toX(s);
        return (
          <g key={`x-${i}`} className="loss-grid">
            <line x1={x} x2={x} y1={height - padB} y2={height - padB + 4} stroke="rgba(255,255,255,0.18)" />
            <text x={x} y={height - padB + 16} textAnchor="middle" className="loss-axis-text">{s}</text>
          </g>
        );
      })}
      <line x1={padL} x2={width - padR} y1={height - padB} y2={height - padB} stroke="rgba(255,255,255,0.18)" />
      <line x1={padL} x2={padL} y1={padT} y2={height - padB} stroke="rgba(255,255,255,0.18)" />
      <path d={linePath} fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
