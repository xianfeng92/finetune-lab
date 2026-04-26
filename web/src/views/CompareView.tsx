import { memo, useEffect, useMemo, useState } from "react";
import type { RunSummary } from "../data-layer";
import type { ProbeResult } from "../types";
import { Term } from "../components/Term";
import {
  MetricBar,
  RunModeBadge,
  SectionTitle,
  datasetScope,
  formatRatio,
} from "../components/ui";

type CaseAggregate = {
  caseId: string;
  perRun: Array<{ run: RunSummary; result: ProbeResult }>;
};

type ViewFilter = "all" | "all-fail" | "split" | "highest-divergence";

type CompareSort = "default" | "exact" | "any" | "signal" | "steps";

function aggregateCases(runs: RunSummary[]): Map<string, CaseAggregate> {
  const map = new Map<string, CaseAggregate>();
  for (const run of runs) {
    for (const probe of run.probeResults) {
      let agg = map.get(probe.id);
      if (!agg) {
        agg = { caseId: probe.id, perRun: [] };
        map.set(probe.id, agg);
      }
      agg.perRun.push({ run, result: probe });
    }
  }
  return map;
}

function jaccardDistance(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter += 1;
  const union = a.size + b.size - inter;
  return union === 0 ? 0 : 1 - inter / union;
}

function avgPairwiseDivergence(perRun: CaseAggregate["perRun"]): number {
  const sets = perRun.map((r) => new Set(r.result.predicted_names));
  if (sets.length < 2) return 0;
  let sum = 0;
  let pairs = 0;
  for (let i = 0; i < sets.length; i += 1) {
    for (let j = i + 1; j < sets.length; j += 1) {
      sum += jaccardDistance(sets[i], sets[j]);
      pairs += 1;
    }
  }
  return pairs === 0 ? 0 : sum / pairs;
}

function CasePillRow(props: { expected: string[]; predicted: string[] }) {
  const expectedSet = new Set(props.expected);
  const predictedSet = new Set(props.predicted);
  const match = props.expected.filter((n) => predictedSet.has(n));
  const extra = props.predicted.filter((n) => !expectedSet.has(n));
  const missing = props.expected.filter((n) => !predictedSet.has(n));
  if (match.length === 0 && extra.length === 0 && missing.length === 0) {
    return <span className="pill subtle">none</span>;
  }
  return (
    <span className="case-pill-row">
      {match.map((n) => <span key={`m-${n}`} className="case-pill match">{n}</span>)}
      {extra.map((n) => <span key={`e-${n}`} className="case-pill extra">+{n}</span>)}
      {missing.map((n) => <span key={`x-${n}`} className="case-pill missing">−{n}</span>)}
    </span>
  );
}

function CaseInputPanel(props: { result: ProbeResult }) {
  const r = props.result;
  return (
    <article className="case-detail-card">
      <h3>Input</h3>
      <div className="case-field">
        <div className="case-field-label">prompt_user</div>
        <p className="case-prompt">{r.prompt_user || <em>（空）</em>}</p>
      </div>
      <div className="case-field">
        <div className="case-field-label"><Term term="tool calling">loaded_tool_names</Term></div>
        <div className="pill-row">
          {r.loaded_tool_names.length
            ? r.loaded_tool_names.map((n) => <span key={n} className="pill subtle">{n}</span>)
            : <span className="pill subtle">none</span>}
        </div>
      </div>
      {r.vehicle_state ? (
        <div className="case-field">
          <div className="case-field-label">vehicle_state</div>
          <code className="case-inline-code">{r.vehicle_state.power_state} · {r.vehicle_state.speed_kph} kph</code>
        </div>
      ) : null}
    </article>
  );
}

function CaseExpectedPanel(props: { result: ProbeResult }) {
  const r = props.result;
  return (
    <article className="case-detail-card">
      <h3>Expected</h3>
      <div className="case-field">
        <div className="case-field-label">behavior · risk</div>
        <div className="pill-row">
          {r.behavior ? <span className="pill">{r.behavior}</span> : null}
          {r.risk ? <span className={`pill risk-${r.risk}`}>risk: {r.risk}</span> : null}
        </div>
      </div>
      <div className="case-field">
        <div className="case-field-label">expected_names</div>
        <div className="pill-row">
          {r.expected_names.length
            ? r.expected_names.map((n) => <span key={n} className="pill">{n}</span>)
            : <span className="pill subtle">none (non-tool-call)</span>}
        </div>
      </div>
      {r.expected_assistant_content ? (
        <div className="case-field">
          <div className="case-field-label">expected_assistant_content</div>
          <p className="case-prompt">{r.expected_assistant_content}</p>
        </div>
      ) : null}
      {r.expected_system_action ? (
        <div className="case-field">
          <div className="case-field-label">expected_system_action</div>
          <code className="case-inline-code">
            {r.expected_system_action.type}
            {r.expected_system_action.tool ? ` · ${r.expected_system_action.tool}` : ""}
            {r.expected_system_action.reason_code ? ` · ${r.expected_system_action.reason_code}` : ""}
          </code>
        </div>
      ) : null}
      {r.expected_tool_calls && r.expected_tool_calls.length > 0 ? (
        <details className="case-json-fold">
          <summary>expected_tool_calls JSON ({r.expected_tool_calls.length})</summary>
          <pre>{JSON.stringify(r.expected_tool_calls, null, 2)}</pre>
        </details>
      ) : null}
    </article>
  );
}

function CaseRunRow(props: { run: RunSummary; result: ProbeResult }) {
  const r = props.result;
  const exact = r.exact_name_match;
  const beh = r.behavior_match;
  const args = (r as ProbeResult & { arguments_match?: boolean }).arguments_match;
  const parsed = r.parsed_output !== null;
  const signal = r.has_tool_calls_signal;
  const unsafe = r.unsafe_direct_call;
  const confirm = r.confirmation_contract_hit;
  const refuse = r.refusal_contract_hit;
  return (
    <article className="case-runrow">
      <header className="case-runrow-head">
        <div className="case-runrow-title">
          <strong>{props.run.manifest.title}</strong>
          <RunModeBadge run={props.run} />
          <code className="case-runrow-runid">{props.run.manifest.run_id}</code>
        </div>
        <div className="case-runrow-pills">
          <span className={`case-status-pill ${exact ? "ok" : "fail"}`}>exact {exact ? "✓" : "✗"}</span>
          {r.behavior !== undefined ? <span className={`case-status-pill ${beh ? "ok" : "fail"}`}>behavior {beh ? "✓" : "✗"}</span> : null}
          {args !== undefined ? <span className={`case-status-pill ${args ? "ok" : "fail"}`}>args {args ? "✓" : "✗"}</span> : null}
          <span className={`case-status-pill ${parsed ? "ok" : "fail"}`}>parsed {parsed ? "✓" : "✗"}</span>
          <span className={`case-status-pill ${signal ? "ok" : "fail"}`}>signal {signal ? "✓" : "✗"}</span>
          {unsafe ? <span className="case-status-pill alert">unsafe!</span> : null}
          {confirm ? <span className="case-status-pill ok">confirm ok</span> : null}
          {refuse ? <span className="case-status-pill ok">reject ok</span> : null}
        </div>
      </header>
      <div className="case-runrow-grid">
        <div>
          <div className="case-field-label">predicted_names (vs expected)</div>
          <CasePillRow expected={r.expected_names} predicted={r.predicted_names} />
        </div>
        <div>
          <div className="case-field-label">predicted_behavior</div>
          <span className={`pill ${beh ? "" : "risk-high"}`}>{r.predicted_behavior ?? "—"}</span>
        </div>
      </div>
      <details className="case-runrow-output">
        <summary>raw_output（点击展开）</summary>
        <pre>{r.raw_output || "[empty]"}</pre>
      </details>
    </article>
  );
}

function CompareViewImpl(props: { runs: RunSummary[]; heldOutDatasetPath: string }) {
  const cases = useMemo(() => aggregateCases(props.runs), [props.runs]);
  const caseIds = useMemo(() => Array.from(cases.keys()), [cases]);
  const [sortBy, setSortBy] = useState<CompareSort>("exact");
  const [includeSim, setIncludeSim] = useState(false);
  const [caseQuery, setCaseQuery] = useState("");
  const casesByView = useMemo(() => {
    const allFail: string[] = [];
    const split: string[] = [];
    const divergenceScored: Array<{ id: string; score: number }> = [];
    for (const [id, agg] of cases) {
      const realRuns = agg.perRun.filter((p) => p.run.manifest.training_mode !== "simulated");
      if (realRuns.length === 0) continue;
      const exacts = realRuns.map((p) => p.result.exact_name_match);
      const passCount = exacts.filter(Boolean).length;
      if (passCount === 0) allFail.push(id);
      else if (passCount < exacts.length) split.push(id);
      const div = avgPairwiseDivergence(realRuns);
      divergenceScored.push({ id, score: div });
    }
    divergenceScored.sort((a, b) => b.score - a.score);
    const highestDivergence = divergenceScored.filter((x) => x.score > 0).slice(0, 5).map((x) => x.id);
    return { allFail, split, highestDivergence };
  }, [cases]);
  const [viewFilter, setViewFilter] = useState<ViewFilter>("all");
  const visibleCaseIds = useMemo(() => {
    let base: string[];
    if (viewFilter === "all-fail") base = casesByView.allFail;
    else if (viewFilter === "split") base = casesByView.split;
    else if (viewFilter === "highest-divergence") base = casesByView.highestDivergence;
    else base = caseIds;
    const q = caseQuery.trim().toLowerCase();
    if (!q) return base;
    return base.filter((id) => {
      if (id.toLowerCase().includes(q)) return true;
      const promptText = cases.get(id)?.perRun[0]?.result.prompt_user?.toLowerCase() ?? "";
      return promptText.includes(q);
    });
  }, [viewFilter, casesByView, caseIds, caseQuery, cases]);
  const defaultCaseId = useMemo(
    () => casesByView.highestDivergence[0] ?? casesByView.split[0] ?? caseIds[0] ?? "",
    [casesByView, caseIds],
  );
  const [selectedCaseId, setSelectedCaseId] = useState(defaultCaseId);
  useEffect(() => {
    if (!selectedCaseId && defaultCaseId) setSelectedCaseId(defaultCaseId);
  }, [selectedCaseId, defaultCaseId]);
  const selectedAgg = cases.get(selectedCaseId);
  const sampleResult = selectedAgg?.perRun[0]?.result;
  return (
    <div className="view-grid">
      <section className="panel span-2">
        <SectionTitle title="Run comparison" subtitle={<>不同 run 的 <Term term="probe">probe</Term> 总数可能不同（<Term term="curriculum">curriculum</Term> 各 stage 的 <Term term="held-out">held-out</Term> 子集不同），分母看每张卡。<strong>scope</strong> 显示这是窄域控制（如 single-tool-control 4 cases）还是 mixed-task（96 cases），不同口径不要直接比。<Term term="simulated">SIM</Term> = 教学占位，<Term term="real run">REAL</Term> = 真实 <Term term="lora">LoRA</Term>。</>} audience="工程" />
        {(() => {
          const withProbesAll = props.runs.filter((r) => r.metrics.total > 0);
          const sims = withProbesAll.filter((r) => r.manifest.training_mode === "simulated");
          const reals = withProbesAll.filter((r) => r.manifest.training_mode !== "simulated");
          const visible = includeSim ? withProbesAll : reals;
          const empty = props.runs.filter((r) => r.metrics.total === 0);
          const rate = (n: number, d: number) => (d > 0 ? n / d : 0);
          const sortKey = (r: RunSummary) => {
            switch (sortBy) {
              case "exact": return rate(r.metrics.exactNameMatch, r.metrics.total);
              case "any": return rate(r.metrics.anyExpectedNameHit, r.metrics.total);
              case "signal": return rate(r.metrics.toolSignal, r.metrics.total);
              case "steps": return r.manifest.max_steps;
              default: return 0;
            }
          };
          const sorted = sortBy === "default" ? visible : [...visible].sort((a, b) => sortKey(b) - sortKey(a));
          const bestExactRate = reals.length ? Math.max(...reals.map((r) => rate(r.metrics.exactNameMatch, r.metrics.total))) : 0;
          return (
            <>
              <div className="compare-toolbar">
                <div className="compare-toolbar-group">
                  <span className="compare-toolbar-label">排序：</span>
                  {(["exact", "any", "signal", "steps", "default"] as CompareSort[]).map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      className={`compare-sort-btn ${sortBy === opt ? "active" : ""}`}
                      onClick={() => setSortBy(opt)}
                    >
                      {opt === "default" ? "原始顺序" : `by ${opt}`}
                    </button>
                  ))}
                </div>
                {sims.length > 0 ? (
                  <label className="compare-toolbar-toggle">
                    <input type="checkbox" checked={includeSim} onChange={(e) => setIncludeSim(e.target.checked)} />
                    <span>包含 SIM 占位 ({sims.length})</span>
                  </label>
                ) : null}
              </div>
              <div className="compare-grid">
                {sorted.map((run) => {
                  const isBest = run.manifest.training_mode !== "simulated"
                    && bestExactRate > 0
                    && rate(run.metrics.exactNameMatch, run.metrics.total) === bestExactRate;
                  return (
                    <article key={run.manifest.run_id} className={`compare-card ${isBest ? "best" : ""}`}>
                      <div className="compare-card-head">
                        <h3>{run.manifest.title}</h3>
                        <div className="compare-card-badges">
                          {isBest ? <span className="compare-best-tag" title="real run 中 exact 命中率最高">★ best exact</span> : null}
                          <RunModeBadge run={run} />
                        </div>
                      </div>
                      <p className="mini-note"><Term term="held-out">held-out</Term> <Term term="probe">probe</Term> · {run.metrics.total} cases · scope <code>{datasetScope(run.manifest.dataset_path)}</code>{run.manifest.train_row_count ? ` · trained on ${run.manifest.train_row_count} rows` : ""}</p>
                      <dl className="run-stats">
                        <div><dt><Term term="exact name match">exact</Term></dt><dd>{formatRatio(run.metrics.exactNameMatch, run.metrics.total)}<MetricBar n={run.metrics.exactNameMatch} d={run.metrics.total} /></dd></div>
                        <div><dt><Term term="any hit">any hit</Term></dt><dd>{formatRatio(run.metrics.anyExpectedNameHit, run.metrics.total)}<MetricBar n={run.metrics.anyExpectedNameHit} d={run.metrics.total} /></dd></div>
                        <div><dt><Term term="parsed json">parsed</Term></dt><dd>{formatRatio(run.metrics.parsedJson, run.metrics.total)}<MetricBar n={run.metrics.parsedJson} d={run.metrics.total} /></dd></div>
                        <div><dt><Term term="tool signal">signal</Term></dt><dd>{formatRatio(run.metrics.toolSignal, run.metrics.total)}<MetricBar n={run.metrics.toolSignal} d={run.metrics.total} /></dd></div>
                      </dl>
                    </article>
                  );
                })}
              </div>
              {empty.length > 0 ? (
                <details className="compare-empty-fold">
                  <summary>{empty.length} 个 run 没有 probe 结果（curriculum 子 stage 通常只在最末汇总评估），点击展开</summary>
                  <div className="compare-empty-list">
                    {empty.map((run) => (
                      <span key={run.manifest.run_id} className="compare-empty-item">
                        <RunModeBadge run={run} />
                        <code>{run.manifest.run_id}</code>
                      </span>
                    ))}
                  </div>
                </details>
              ) : null}
            </>
          );
        })()}
      </section>
      <section className="panel">
        <SectionTitle title="Probe cases" subtitle={<>固定 <Term term="held-out">held-out</Term> case，来自 {props.heldOutDatasetPath}。默认显示分歧最大的 case，便于看出不同 run 的判别差异。</>} audience="工程" />
        <div className="case-savedviews">
          <button type="button" className={`case-savedview ${viewFilter === "all" ? "active" : ""}`} onClick={() => setViewFilter("all")}>
            <strong>all</strong><span>{caseIds.length}</span>
          </button>
          <button type="button" className={`case-savedview ${viewFilter === "highest-divergence" ? "active" : ""}`} onClick={() => setViewFilter("highest-divergence")} title="不同 run 在这条 case 上预测差异最大的 top 5">
            <strong>highest-divergence</strong><span>{casesByView.highestDivergence.length}</span>
          </button>
          <button type="button" className={`case-savedview ${viewFilter === "split" ? "active" : ""}`} onClick={() => setViewFilter("split")} title="至少一个 real run 通过、至少一个失败：体现训练策略差异">
            <strong>split</strong><span>{casesByView.split.length}</span>
          </button>
          <button type="button" className={`case-savedview ${viewFilter === "all-fail" ? "active" : ""}`} onClick={() => setViewFilter("all-fail")} title="所有 real run 都没通过：最难的 case">
            <strong>all-fail</strong><span>{casesByView.allFail.length}</span>
          </button>
        </div>
        <div className="case-search-row">
          <input
            type="search"
            className="case-search-input"
            placeholder="搜索 case id 或 prompt 文本"
            value={caseQuery}
            onChange={(e) => setCaseQuery(e.target.value)}
            aria-label="搜索 case"
          />
          {caseQuery ? <span className="case-search-count">{visibleCaseIds.length} 命中</span> : null}
        </div>
        <div className="sample-list compact case-list">
          {visibleCaseIds.length === 0 ? (
            <p className="mini-note">该 view 下没有匹配 case。</p>
          ) : null}
          {visibleCaseIds.map((caseId) => {
            const promptPreview = cases.get(caseId)?.perRun[0]?.result.prompt_user ?? "";
            return (
              <button key={caseId} type="button" className={`sample-item ${selectedCaseId === caseId ? "active" : ""}`} onClick={() => setSelectedCaseId(caseId)}>
                <span>{caseId}</span>
                {promptPreview ? <strong className="case-preview">{promptPreview.slice(0, 60)}{promptPreview.length > 60 ? "…" : ""}</strong> : null}
              </button>
            );
          })}
        </div>
      </section>
      {selectedAgg && sampleResult ? (
        <section className="panel span-2 case-detail-panel">
          <SectionTitle title={`Case detail · ${selectedAgg.caseId}`} subtitle={<>Input / Expected 是 case 级共享数据。下方每个 run 一行，显示在这条 case 上的命中情况和 predicted_names 集合 diff。<span className="case-diff-legend"> <span className="case-pill match">match</span> <span className="case-pill extra">+ extra</span> <span className="case-pill missing">− missing</span></span></>} audience="工程" />
          <div className="case-detail-grid">
            <CaseInputPanel result={sampleResult} />
            <CaseExpectedPanel result={sampleResult} />
          </div>
          <div className="case-runrows">
            {selectedAgg.perRun.map(({ run, result }) => (
              <CaseRunRow key={run.manifest.run_id} run={run} result={result} />
            ))}
          </div>
        </section>
      ) : (
        <section className="panel span-2">
          <p className="mini-note">没选中 case，或者所选 view 没有匹配的 case。</p>
        </section>
      )}
    </div>
  );
}

export const CompareView = memo(CompareViewImpl);
