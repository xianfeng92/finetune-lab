import { memo, useMemo, useState } from "react";
import type { RunSummary } from "../data-layer";
import { Term } from "../components/Term";
import { LossCurve, RunModeBadge, SectionTitle, formatRatio } from "../components/ui";

function TrainingCurvesGrid(props: { runs: RunSummary[] }) {
  const [sharedY, setSharedY] = useState(true);
  const realRuns = props.runs.filter((r) => r.manifest.training_mode !== "simulated");
  const referenceRuns = realRuns.length > 0 ? realRuns : props.runs;
  const allLosses = referenceRuns.flatMap((r) => r.trainingCurve.points.map((p) => p.loss));
  const yMin = allLosses.length ? Math.min(...allLosses) : 0;
  const yMax = allLosses.length ? Math.max(...allLosses) : 1;
  return (
    <>
      <div className="curve-controls">
        <label className="curve-toggle">
          <input type="checkbox" checked={sharedY} onChange={(e) => setSharedY(e.target.checked)} />
          <span>共享 y 轴（按 real run 范围对齐，便于横向比较）</span>
        </label>
      </div>
      <div className="curve-row">
        {props.runs.map((run) => {
          const isSim = run.manifest.training_mode === "simulated";
          const points = run.trainingCurve.points;
          const firstLoss = points[0]?.loss;
          const lastLoss = points[points.length - 1]?.loss;
          return (
            <article key={run.manifest.run_id} className={`curve-card ${isSim ? "magenta" : "lime"}`}>
              <div className="curve-head">
                <div>
                  <div className="eyebrow">{run.manifest.engine} · {run.manifest.max_steps} steps</div>
                  <div className="curve-title-row">
                    <h3>{run.manifest.title}</h3>
                    <RunModeBadge run={run} />
                  </div>
                  {run.manifest.simulation_note ? <p className="curve-note">{run.manifest.simulation_note}</p> : null}
                </div>
                <div className="curve-delta">
                  <div className="delta-label">avg loss</div>
                  <div className="delta-value">{run.manifest.avg_loss.toFixed(3)}</div>
                  {firstLoss !== undefined && lastLoss !== undefined ? (
                    <div className="delta-sub">{firstLoss.toFixed(2)} → {lastLoss.toFixed(2)}</div>
                  ) : null}
                </div>
              </div>
              <LossCurve
                curve={run.trainingCurve}
                tone={isSim ? "magenta" : "lime"}
                yMin={sharedY ? yMin : undefined}
                yMax={sharedY ? yMax : undefined}
              />
            </article>
          );
        })}
      </div>
    </>
  );
}

function TrainingRunsViewImpl(props: { runs: RunSummary[] }) {
  const [selectedRunId, setSelectedRunId] = useState(props.runs[props.runs.length - 1]?.manifest.run_id ?? "");
  const selectedRun = props.runs.find((run) => run.manifest.run_id === selectedRunId) ?? props.runs[0];
  const grouped = useMemo(() => {
    const map = new Map<string, RunSummary[]>();
    for (const run of props.runs) {
      const key = run.manifest.family ?? "other";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(run);
    }
    return [...map.entries()];
  }, [props.runs]);
  return (
    <div className="view-grid">
      <section className="panel">
        <SectionTitle title="Run registry" subtitle={<>按 family 分组：top-level run 和 <Term term="curriculum">curriculum</Term> 子 stage 都在这里。<Term term="simulated">SIM</Term> = 教学占位。</>} audience="工程" />
        <div className="run-family-list">
          {grouped.map(([family, familyRuns]) => (
            <details key={family} open className="run-family">
              <summary>
                <span className="run-family-name">{family}</span>
                <span className="run-family-count">{familyRuns.length}</span>
              </summary>
              <div className="sample-list compact">
                {familyRuns.map((run) => (
                  <button key={run.manifest.run_id} type="button" className={`sample-item ${selectedRun?.manifest.run_id === run.manifest.run_id ? "active" : ""}`} onClick={() => setSelectedRunId(run.manifest.run_id)}>
                    <div className="sample-item-head">
                      <span>{run.manifest.run_id}</span>
                      <RunModeBadge run={run} />
                    </div>
                    <strong>{run.manifest.title}</strong>
                  </button>
                ))}
              </div>
            </details>
          ))}
        </div>
      </section>
      <section className="panel">
        <SectionTitle title="Run metrics" subtitle="从 manifest 和 probe 汇总。指标名带虚下划线的可以鼠标悬停看解释。" audience="工程" />
        {selectedRun ? (
          <article className="run-card">
            <div className="run-card-head">
              <div className="run-tag">{selectedRun.manifest.engine}</div>
              <RunModeBadge run={selectedRun} />
            </div>
            <h3>{selectedRun.manifest.title}</h3>
            <p>{selectedRun.manifest.model_name}</p>
            {selectedRun.manifest.simulation_note ? <div className="run-note">{selectedRun.manifest.simulation_note}</div> : null}
            <dl className="run-stats">
              <div><dt><Term term="step">max steps</Term></dt><dd>{selectedRun.manifest.max_steps}</dd></div>
              <div><dt>avg <Term term="loss delta">loss</Term></dt><dd>{selectedRun.manifest.avg_loss.toFixed(4)}</dd></div>
              <div><dt>train split</dt><dd>{selectedRun.manifest.dataset_path}</dd></div>
              <div><dt>dataset role</dt><dd>{selectedRun.manifest.dataset_role ?? "train"}</dd></div>
              <div><dt>train rows</dt><dd>{selectedRun.manifest.train_row_count ?? "—"}</dd></div>
              <div><dt>completed</dt><dd>{selectedRun.manifest.completed_at ? new Date(selectedRun.manifest.completed_at).toLocaleDateString() : "—"}</dd></div>
              <div><dt><Term term="tool signal">tool signal</Term></dt><dd>{formatRatio(selectedRun.metrics.toolSignal, selectedRun.metrics.total)}</dd></div>
              <div><dt><Term term="parsed json">parsed JSON</Term></dt><dd>{formatRatio(selectedRun.metrics.parsedJson, selectedRun.metrics.total)}</dd></div>
            </dl>
          </article>
        ) : null}
      </section>
      {props.runs.length > 0 ? (
        <section className="panel span-2">
          <SectionTitle title="Training curves" subtitle={<>train-metrics.jsonl 每步 <Term term="loss delta">loss</Term> 直接可视化。<Term term="simulated">SIM</Term> = 合成 loss 的教学占位（不更新真实 <Term term="checkpoint">checkpoint</Term>），<Term term="real run">REAL</Term> = mlx-lm.lora 真实跑出来的。</>} audience="工程" />
          <TrainingCurvesGrid runs={props.runs} />
        </section>
      ) : null}
      <section className="panel span-2">
        <SectionTitle title="Artifacts" subtitle={<><Term term="adapter">adapter</Term> 输出文件。LoRA 训练只产几 MB 到几十 MB 的小补丁，不是完整模型。</>} audience="工程" />
        {selectedRun ? (
          <div className="artifact-grid">
            {selectedRun.artifacts.map((artifact) => (
              <article key={artifact.relative_path} className="artifact-card">
                <div className="artifact-name">{artifact.name}</div>
                <div className="artifact-path">{artifact.relative_path}</div>
                <div className="artifact-size">{artifact.size_bytes} bytes</div>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}

export const TrainingRunsView = memo(TrainingRunsViewImpl);
