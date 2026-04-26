import { memo } from "react";
import type { LabData } from "../data-layer";
import { Term } from "../components/Term";
import {
  AudienceChip,
  ChartBars,
  CollapsiblePanel,
  KpiCard,
  RoadmapBadge,
  formatRatio,
} from "../components/ui";
import type { View } from "../ui-types";

function StarterGuide(props: { onPick: (view: View) => void }) {
  return (
    <section className="panel span-2 starter-guide">
      <header className="section-title">
        <div className="section-title-row">
          <div className="eyebrow">从这里开始</div>
          <AudienceChip audience="新手" />
        </div>
        <h2>不知道先看哪儿？</h2>
        <p>三种典型用户，三个起点。点一下直接跳过去。</p>
      </header>
      <div className="starter-grid">
        <button type="button" className="starter-card" onClick={() => props.onPick("beginner-guide")}>
          <div className="starter-eyebrow">完全没微调过</div>
          <h3>先读 Beginner Guide</h3>
          <p>系统讲清楚什么是 SFT / LoRA / probe，为什么 loss ≠ 学到了。新手第一站。看完再回头看其它 tab。</p>
        </button>
        <button type="button" className="starter-card" onClick={() => props.onPick("runs")}>
          <div className="starter-eyebrow">想看真训练能跑出什么</div>
          <h3>跳到 Training Runs</h3>
          <p>所有 <Term term="real run">real run</Term> 和 <Term term="simulated">simulated</Term> 占位的 loss 曲线、产物文件都在这里。SIM 是教学占位，REAL 是真跑。</p>
        </button>
        <button type="button" className="starter-card" onClick={() => props.onPick("compare")}>
          <div className="starter-eyebrow">想知道哪个 run 最好</div>
          <h3>跳到 Probe Compare</h3>
          <p>用 <Term term="held-out">held-out</Term> <Term term="probe">probe</Term> 横向比所有 run 的命中率。注意：不同 run 的分母可能不同，看每张卡。</p>
        </button>
      </div>
    </section>
  );
}

function ManifestoHero(props: { data: LabData }) {
  const manifesto = props.data.manifesto;
  const runs = props.data.runs;
  const realTopLevelRuns = runs.filter((r) => r.manifest.is_top_level && r.manifest.training_mode !== "simulated");
  const sortedByTime = [...realTopLevelRuns].sort((a, b) => {
    const ta = a.manifest.completed_at ? Date.parse(a.manifest.completed_at) : 0;
    const tb = b.manifest.completed_at ? Date.parse(b.manifest.completed_at) : 0;
    return ta - tb;
  });
  const latestRealRun = sortedByTime[sortedByTime.length - 1] ?? realTopLevelRuns[realTopLevelRuns.length - 1] ?? runs[runs.length - 1];
  const probeCandidates = runs.filter((r) => r.manifest.training_mode !== "simulated" && r.metrics.total >= 8);
  const bestProbeRun = probeCandidates.length
    ? [...probeCandidates].sort((a, b) => {
        const ra = a.metrics.exactNameMatch / a.metrics.total;
        const rb = b.metrics.exactNameMatch / b.metrics.total;
        if (rb !== ra) return rb - ra;
        return b.metrics.total - a.metrics.total;
      })[0]
    : null;
  const first = runs[0];
  const latestStepRun = runs[runs.length - 1];
  const latestPoints = latestRealRun?.trainingCurve?.points ?? [];
  const lossPeak = latestPoints.length ? Math.max(...latestPoints.map((p) => p.loss)) : null;
  const lossFloor = latestPoints.length ? Math.min(...latestPoints.map((p) => p.loss)) : null;
  const bestProbeRatio = bestProbeRun ? `${bestProbeRun.metrics.exactNameMatch}/${bestProbeRun.metrics.total}` : "—";
  const bestProbePct = bestProbeRun ? Math.round((bestProbeRun.metrics.exactNameMatch / bestProbeRun.metrics.total) * 100) : null;
  const headlineLines = (manifesto?.headline ?? "Clone it.\nHand it to an agent.\nWatch a model learn.").split("\n");
  return (
    <section className="manifesto">
      <div className="manifesto-head">
        <span className="eyebrow">{manifesto?.eyebrow ?? "AI-native fine-tuning lab"}</span>
        <span className="mini-note">snapshot · {new Date(props.data.generated_at).toLocaleString()}</span>
      </div>
      <h1 className="manifesto-title">
        {headlineLines.map((line, idx) => (
          <span key={idx} className={idx === 1 ? "accent" : ""}>{line}</span>
        ))}
      </h1>
      <p className="manifesto-lede">{manifesto?.lede ?? props.data.project.primary_goal}</p>
      <div className="manifesto-cmds">
        {(manifesto?.hero_commands ?? ["make ai-onboarding", "make ai-setup", "make ai-lab"]).map((cmd, i) => (
          <div key={cmd} className="manifesto-cmd">
            <span className="manifesto-cmd-idx">{String(i + 1).padStart(2, "0")}</span>
            <code>{cmd}</code>
          </div>
        ))}
      </div>
      <div className="kpi-grid kpi-grid-5">
        <KpiCard label="samples" value={`${props.data.dataset.summary.total_samples}`} hint="SFT demo 样本数" />
        <KpiCard label="runs" value={`${runs.length}`} hint={`${first?.manifest.max_steps ?? 0} → ${latestStepRun?.manifest.max_steps ?? 0} steps`} />
        <KpiCard
          label="best probe exact"
          value={bestProbePct !== null ? `${bestProbePct}%` : "—"}
          hint={bestProbeRun ? `${bestProbeRun.manifest.title} · ${bestProbeRatio} on held-out` : "no probe yet"}
          accent
        />
        <KpiCard
          label="train loss"
          value={lossPeak !== null && lossFloor !== null ? `${lossPeak.toFixed(2)}→${lossFloor.toFixed(2)}` : "—"}
          hint={`${latestRealRun?.manifest.title ?? "no run"} · peak→floor，仅训练目标，不代表模型质量`}
        />
        <KpiCard label="onboarding" value={props.data.onboarding.overall_status} hint={props.data.onboarding.next_steps[0]?.command ?? "make ai-onboarding"} />
      </div>
      <div className="hero-glossary">
        <span className="hero-glossary-label">速查：</span>
        <Term term="sft">SFT</Term>
        <Term term="lora">LoRA</Term>
        <Term term="mlx">MLX</Term>
        <Term term="held-out">held-out</Term>
        <Term term="probe">probe</Term>
        <Term term="exact name match">exact name match</Term>
        <Term term="parsed json">parsed json</Term>
        <Term term="tool signal">tool signal</Term>
        <Term term="curriculum">curriculum</Term>
        <Term term="consolidation">consolidation</Term>
        <Term term="adapter">adapter</Term>
        <Term term="simulated">simulated</Term>
      </div>
    </section>
  );
}

function LearningRoadmapPanel(props: { data: LabData }) {
  const roadmap = props.data.learning_roadmap;
  if (!roadmap) return null;
  return (
    <CollapsiblePanel title={roadmap.headline} subtitle={roadmap.summary} audience="新手">
      <div className="roadmap-legend">
        <span className="roadmap-legend-label">状态图例：</span>
        <span className="roadmap-legend-item"><RoadmapBadge status="live" /> 这一关已经做完，仓库里有完整产物可看</span>
        <span className="roadmap-legend-item"><RoadmapBadge status="partial" /> 部分到位（占位 / rubric / 半成品），等待真正的大模型确认实验</span>
        <span className="roadmap-legend-item"><RoadmapBadge status="next" /> 下一关重点</span>
        <span className="roadmap-legend-item"><RoadmapBadge status="planned" /> 已写入 roadmap，没动手</span>
      </div>
      <div className="roadmap-grid">
        {roadmap.levels.map((level) => (
          <article key={level.id} className={`roadmap-card ${level.status}`}>
            <div className="roadmap-card-top">
              <div>
                <div className="eyebrow">{level.label}</div>
                <h3>{level.title}</h3>
              </div>
              <RoadmapBadge status={level.status} />
            </div>
            <div className="roadmap-model">{level.model}</div>
            <p>{level.goal}</p>
            <div className="roadmap-note"><strong>Why it matters</strong><span>{level.why_it_matters}</span></div>
            <div className="pill-row">
              {level.commands.map((command) => (
                <span key={command} className="pill">{command}</span>
              ))}
            </div>
            <div className="roadmap-meta">
              <div>
                <h4>Focus metrics</h4>
                <div className="pill-row">
                  {level.focus_metrics.map((metric) => (
                    <span key={metric} className="pill subtle">{metric}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4>Artifacts</h4>
                <div className="roadmap-list">
                  {level.artifacts.map((artifact) => (
                    <code key={artifact}>{artifact}</code>
                  ))}
                </div>
              </div>
            </div>
            <div className="roadmap-pitfall">Pitfall: {level.pitfall}</div>
          </article>
        ))}
      </div>
    </CollapsiblePanel>
  );
}

function GemmaTrackPanel(props: { data: LabData }) {
  const track = props.data.gemma_track;
  const pack = props.data.gemma_track_pack;
  if (!track) return null;
  return (
    <CollapsiblePanel title={track.headline} subtitle={track.summary} audience="工程">
      <div className="track-stack">
        <article className="track-card">
          <div className="track-label">Default base</div>
          <h3>{track.default_model.name}</h3>
          <p>{track.default_model.role}</p>
          <div className="track-why">{track.default_model.why}</div>
        </article>
        <article className="track-card alt">
          <div className="track-label">Compare with</div>
          <h3>{track.comparison_model.name}</h3>
          <p>{track.comparison_model.role}</p>
          <div className="track-why">{track.comparison_model.why}</div>
        </article>
        <article className="track-card">
          <div className="track-label">Specialization focus</div>
          <h3>{track.specialization_focus.title}</h3>
          <p>{track.specialization_focus.body}</p>
        </article>
        <div className="pill-row">
          {track.upgrade_path.map((item) => (
            <span key={item} className="pill">{item}</span>
          ))}
        </div>
        {pack ? (
          <>
            <div className="track-pack-grid">
              {pack.checkpoints.map((checkpoint) => (
                <article key={checkpoint.name} className="track-pack-card">
                  <div className="track-label">{checkpoint.type}</div>
                  <h3>{checkpoint.name}</h3>
                  <p>{checkpoint.teaching_role}</p>
                  <div className="track-why">{checkpoint.best_for}</div>
                  <div className="pill-row">
                    {checkpoint.strengths.slice(0, 2).map((item) => (
                      <span key={item} className="pill subtle">{item}</span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
            <div className="track-pack-notes">
              {pack.comparison_axes.map((axis) => (
                <article key={axis.axis} className="track-pack-note">
                  <strong>{axis.axis}</strong>
                  <p>base: {axis.base}</p>
                  <p>instruct: {axis.instruct}</p>
                  <div className="track-why">{axis.why_it_matters}</div>
                </article>
              ))}
            </div>
          </>
        ) : null}
      </div>
    </CollapsiblePanel>
  );
}

function ReferenceProjectsPanel(props: { data: LabData }) {
  const projects = props.data.reference_projects ?? [];
  if (!projects.length) return null;
  return (
    <CollapsiblePanel title="What to steal from hot open-source labs" subtitle="热门项目最值得学的是结构，不只是功能。" audience="新手">
      <div className="reference-list">
        {projects.map((project) => (
          <article key={project.name} className="reference-card">
            <div className="reference-head">
              <a href={project.url} target="_blank" rel="noreferrer">{project.name}</a>
              <span>{project.signal}</span>
            </div>
            <p>{project.takeaway}</p>
            {project.relation ? <p className="reference-relation"><strong>关系：</strong>{project.relation}</p> : null}
          </article>
        ))}
      </div>
    </CollapsiblePanel>
  );
}

function Level1Panel(props: { data: LabData }) {
  const taskPack = props.data.level1.task_framing_pack;
  const baselinePack = props.data.level1.baseline_eval_pack;
  if (!taskPack && !baselinePack) return null;
  return (
    <CollapsiblePanel
      title="Level 1: Baseline and Task Framing"
      subtitle={<>先定义什么算"学会了"，再看训练和 <Term term="probe">probe</Term> 改变了什么。</>}
      audience="工程"
    >
      <div className="level1-grid">
        {taskPack ? (
          <article className="level1-card">
            <div className="level1-head">
              <div>
                <div className="eyebrow">Task framing pack</div>
                <h3>{taskPack.task_brief.title}</h3>
              </div>
              <div className="mini-note">{taskPack.dataset_profile.total_samples} samples</div>
            </div>
            <p>{taskPack.task_brief.user_job}</p>
            <div className="level1-reason">{taskPack.task_brief.target_behavior}</div>
            <div className="pill-row">
              {taskPack.dataset_profile.category_counts.slice(0, 4).map((item) => (
                <span key={item.category} className="pill">{item.category} {item.count}</span>
              ))}
            </div>
            <div className="level1-bucket-grid">
              {taskPack.failure_buckets.map((bucket) => (
                <article key={bucket.bucket} className="level1-bucket-card">
                  <strong>{bucket.label}</strong>
                  <p>{bucket.description}</p>
                  <div className="pill-row">
                    <span className="pill subtle">{bucket.affected_category}</span>
                    <span className="pill subtle">{bucket.sample_count} samples</span>
                  </div>
                </article>
              ))}
            </div>
            <div className="level1-list">
              {taskPack.held_out_seed_cases.slice(0, 3).map((item) => (
                <article key={item.id} className="level1-item">
                  <strong>{item.id}</strong>
                  <p>{item.prompt_surface.text}</p>
                  <div className="pill-row">
                    {item.risk_flags.map((flag) => (
                      <span key={flag} className="pill subtle">{flag}</span>
                    ))}
                  </div>
                  <div className="level1-reason">{item.baseline_hypothesis}</div>
                </article>
              ))}
            </div>
          </article>
        ) : null}
        {baselinePack ? (
          <article className="level1-card">
            <div className="level1-head">
              <div>
                <div className="eyebrow">Baseline eval pack</div>
                <h3>{baselinePack.baseline_profile.name}</h3>
              </div>
              <div className="mini-note">{baselinePack.summary.case_count} held-out cases</div>
            </div>
            <p>{baselinePack.baseline_profile.strategy}</p>
            <div className="level1-metric-grid">
              <article className="level1-metric-card">
                <span><Term term="route hit">route hit</Term></span>
                <strong>{formatRatio(baselinePack.summary.route_selection_hit, baselinePack.summary.case_count)}</strong>
              </article>
              <article className="level1-metric-card">
                <span>executable</span>
                <strong>{formatRatio(baselinePack.summary.executable_output, baselinePack.summary.case_count)}</strong>
              </article>
              <article className="level1-metric-card">
                <span>arguments</span>
                <strong>{formatRatio(baselinePack.summary.arguments_complete, baselinePack.summary.case_count)}</strong>
              </article>
              <article className="level1-metric-card">
                <span>overall pass</span>
                <strong>{formatRatio(baselinePack.summary.overall_pass, baselinePack.summary.case_count)}</strong>
              </article>
            </div>
            <div className="level1-list">
              {baselinePack.cases.slice(0, 3).map((item) => (
                <article key={item.id} className="level1-item">
                  <strong>{item.id}</strong>
                  <p>{item.prompt_surface.text}</p>
                  <div className="pill-row">
                    <span className="pill subtle">{item.baseline_prediction.output_shape}</span>
                    <span className="pill">{item.likely_failure_bucket}</span>
                  </div>
                  <div className="level1-reason">{item.lesson}</div>
                </article>
              ))}
            </div>
            <div className="level1-notes">
              {baselinePack.next_actions.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          </article>
        ) : null}
      </div>
    </CollapsiblePanel>
  );
}

function Level5Panel(props: { data: LabData }) {
  const toolPack = props.data.level5.tool_routing_pack;
  const structuredPack = props.data.level5.structured_output_pack;
  if (!toolPack && !structuredPack) return null;
  return (
    <CollapsiblePanel
      title="Level 5: Structured Outputs and Tool Calling"
      subtitle={<>把 <Term term="route hit">route selection</Term> 和 <Term term="structured output">structured output</Term> 变成可看的专题教学包。</>}
      audience="工程"
    >
      <div className="level5-grid">
        {toolPack ? (
          <article className="level5-card">
            <div className="level5-head">
              <div>
                <div className="eyebrow">Tool-routing dataset pack</div>
                <h3>{toolPack.summary.multi_tool_samples} multi-choice samples</h3>
              </div>
              <div className="mini-note">{toolPack.summary.distinct_tools} tools</div>
            </div>
            <div className="pill-row">
              <span className="pill">avg candidates {toolPack.summary.avg_candidate_count}</span>
              <span className="pill">single {toolPack.summary.single_tool_samples}</span>
              <span className="pill">multi {toolPack.summary.multi_tool_samples}</span>
            </div>
            <div className="level5-subgrid">
              <div>
                <h4>Top routes</h4>
                <ChartBars items={toolPack.summary.route_counts.slice(0, 5).map((item) => ({ label: item.tool_name, value: item.count }))} tone="lime" />
              </div>
              <div>
                <h4>Focus samples</h4>
                <div className="level5-list">
                  {toolPack.focus_samples.slice(0, 3).map((sample) => (
                    <article key={sample.id} className="level5-list-card">
                      <strong>{sample.expected_name}</strong>
                      <p>{sample.prompt_user}</p>
                      <div className="pill-row">
                        <span className="pill subtle">{sample.route_type}</span>
                        {sample.loaded_tool_names.map((tool) => (
                          <span key={tool} className="pill subtle">{tool}</span>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </div>
            <div className="level5-notes">
              {toolPack.teaching_notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          </article>
        ) : null}
        {structuredPack ? (
          <article className="level5-card">
            <div className="level5-head">
              <div>
                <div className="eyebrow">Structured-output probe pack</div>
                <h3>{structuredPack.runs.length} probe views</h3>
              </div>
              <div className="mini-note">Level 5 focus</div>
            </div>
            <div className="level5-run-grid">
              {structuredPack.runs.map((run) => (
                <article key={run.run_id} className="level5-run-card">
                  <div className="stage-head">
                    <strong>{run.title}</strong>
                    <span>{run.max_steps} steps</span>
                  </div>
                  <div className="pill-row">
                    <span className="pill">exact {formatRatio(run.summary.exact_name_match, run.summary.total_cases)}</span>
                    <span className="pill">tool_calls {formatRatio(run.summary.tool_calls_array, run.summary.total_cases)}</span>
                    <span className="pill">args {formatRatio(run.summary.arguments_match, run.summary.total_cases)}</span>
                  </div>
                </article>
              ))}
            </div>
            <div className="level5-list">
              {structuredPack.compare_cases.slice(0, 2).map((probeCase) => (
                <article key={probeCase.id} className="level5-list-card">
                  <strong>{probeCase.id}</strong>
                  <p>{probeCase.prompt_user}</p>
                  <div className="level5-case-runs">
                    {probeCase.runs.map((run) => (
                      <span key={`${probeCase.id}-${run.run_id}`} className="pill subtle">
                        {run.max_steps} step · {run.output_shape}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
            <div className="level5-notes">
              {structuredPack.teaching_notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          </article>
        ) : null}
      </div>
    </CollapsiblePanel>
  );
}

function BehaviorEvalPanel(props: { data: LabData }) {
  const pack = props.data.behavior_eval_pack;
  if (!pack) return null;
  return (
    <CollapsiblePanel
      title="Behavior Eval Pack"
      subtitle={<>把 <Term term="route hit">route 命中</Term>和动作选择拆开看，专门盯高风险样本里的 unsafe direct call、confirm contract 和 reject contract。</>}
      audience="进阶"
    >
      <div className="level6-grid">
        {pack.runs.map((run) => (
          <article key={`${run.run_id}-${run.max_steps}`} className="level6-card">
            <div className="level6-head">
              <div>
                <div className="eyebrow">{run.training_mode}</div>
                <h3>{run.title}</h3>
              </div>
              <div className="mini-note">{run.max_steps} steps</div>
            </div>
            <div className="pill-row">
              <span className="pill">
                behavior {formatRatio(run.behavior_metrics.behavior_accuracy.hit, run.behavior_metrics.behavior_accuracy.total)}
              </span>
              <span className="pill subtle">
                unsafe {formatRatio(run.behavior_metrics.unsafe_direct_call_rate.count, run.behavior_metrics.unsafe_direct_call_rate.total)}
              </span>
              <span className="pill subtle">
                high-risk {formatRatio(run.behavior_metrics.high_risk_direct_call_rate.count, run.behavior_metrics.high_risk_direct_call_rate.total)}
              </span>
              <span className="pill">
                confirm {formatRatio(run.behavior_metrics.confirmation_contract_hit.hit, run.behavior_metrics.confirmation_contract_hit.total)}
              </span>
              <span className="pill subtle">
                reject {formatRatio(run.behavior_metrics.refusal_contract_hit.hit, run.behavior_metrics.refusal_contract_hit.total)}
              </span>
            </div>
            <div className="level5-subgrid">
              <div>
                <h4>Predicted behaviors</h4>
                <ChartBars
                  items={Object.entries(run.behavior_metrics.predicted_behavior_counts).map(([label, value]) => ({ label, value }))}
                  tone="magenta"
                />
              </div>
              <div>
                <h4>Miss cases</h4>
                <div className="level6-list">
                  {run.miss_cases.slice(0, 3).map((item) => (
                    <article key={`${run.run_id}-${run.max_steps}-${item.id}`} className="level6-item">
                      <strong>{item.id}</strong>
                      <div className="pill-row">
                        <span className="pill subtle">{item.category}</span>
                        <span className="pill">{item.behavior} {"->"} {item.predicted_behavior}</span>
                        <span className="pill subtle">{item.risk}</span>
                      </div>
                      <div className="level6-reason">
                        predicted tools: {item.predicted_names.length ? item.predicted_names.join(", ") : "none"}
                      </div>
                      {item.expected_system_action ? (
                        <div className="level6-reason">expected system action: {item.expected_system_action.type}</div>
                      ) : null}
                      {item.unsafe_direct_call ? <div className="level6-reason">unsafe direct call triggered</div> : null}
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
      <div className="level6-notes">
        {pack.teaching_notes.map((note) => (
          <p key={note}>{note}</p>
        ))}
      </div>
    </CollapsiblePanel>
  );
}

function DataScaleComparePanel(props: { data: LabData }) {
  const pack = props.data.data_scale_compare_pack;
  if (!pack) return null;
  return (
    <CollapsiblePanel
      title="Data Scale vs Training Strategy"
      subtitle={<>把 small / medium / large 和 direct mixed / <Term term="curriculum">curriculum</Term> + <Term term="consolidation">consolidation</Term> 放在同一张表里看，避免只凭单个跑分下结论。</>}
      audience="进阶"
    >
      <div className="level6-grid">
        {pack.scenarios.map((scenario) => (
          <article key={scenario.scenario_id} className="level6-card">
            <div className="level6-head">
              <div>
                <div className="eyebrow">{scenario.data_scale}</div>
                <h3>{scenario.strategy_label}</h3>
              </div>
              <div className="mini-note">{scenario.dataset.counts.train}/{scenario.dataset.counts.valid}/{scenario.dataset.counts.test}</div>
            </div>
            <div className="pill-row">
              <span className="pill">exact {formatRatio(scenario.metrics.exact_name_match.hit, scenario.metrics.exact_name_match.total)}</span>
              <span className="pill subtle">structured {formatRatio(scenario.metrics.structured_output_valid.hit, scenario.metrics.structured_output_valid.total)}</span>
              <span className="pill">args {formatRatio(scenario.metrics.arguments_match.hit, scenario.metrics.arguments_match.total)}</span>
              <span className="pill subtle">behavior {formatRatio(scenario.metrics.behavior_accuracy.hit, scenario.metrics.behavior_accuracy.total)}</span>
            </div>
            <div className="pill-row">
              <span className="pill subtle">unsafe {formatRatio(scenario.metrics.unsafe_direct_call_rate.count, scenario.metrics.unsafe_direct_call_rate.total)}</span>
              <span className="pill">confirm {formatRatio(scenario.metrics.confirmation_contract_hit.hit, scenario.metrics.confirmation_contract_hit.total)}</span>
              <span className="pill subtle">reject {formatRatio(scenario.metrics.refusal_contract_hit.hit, scenario.metrics.refusal_contract_hit.total)}</span>
              <span className="pill subtle">loss {scenario.avg_loss.toFixed(3)}</span>
            </div>
            <div className="level6-reason">
              train behaviors: {Object.entries(scenario.dataset.train_behaviors).map(([key, value]) => `${key} ${value}`).join(" · ")}
            </div>
          </article>
        ))}
      </div>
      <div className="level6-rubric-grid">
        {pack.matrix.map((row) => (
          <article key={row.metric} className="level6-item">
            <strong>{row.label}</strong>
            <div className="level6-list">
              {row.scenarios.map((scenario) => (
                <article key={`${row.metric}-${scenario.scenario_id}`} className="level6-item">
                  <div className="pill-row">
                    <span className="pill">{scenario.label}</span>
                    <span className="pill subtle">{formatRatio(scenario.value, scenario.total)}</span>
                  </div>
                  <div className="level6-reason">rate {(scenario.rate * 100).toFixed(1)}%</div>
                </article>
              ))}
            </div>
          </article>
        ))}
      </div>
      <div className="level6-notes">
        {pack.teaching_notes.map((note) => (
          <p key={note}>{note}</p>
        ))}
      </div>
    </CollapsiblePanel>
  );
}

function Level6Panel(props: { data: LabData }) {
  const datasetPack = props.data.level6.preference_dataset_pack;
  const compareReport = props.data.level6.policy_compare_report;
  const scaleUpRubric = props.data.level6.scale_up_rubric;
  const scaleUpCompare = props.data.level6.scale_up_compare;
  if (!datasetPack && !compareReport && !scaleUpRubric && !scaleUpCompare) return null;
  return (
    <CollapsiblePanel
      title="Level 6: Preference Tuning and Scale-up"
      subtitle={<>不只看 chosen win，而是一起看 rubric、hard failures 和什么时候才值得 scale-up。<Term term="preference tuning"> </Term></>}
      audience="进阶"
      defaultOpen={false}
    >
      <div className="level6-grid">
        {datasetPack ? (
          <article className="level6-card">
            <div className="level6-head">
              <div>
                <div className="eyebrow">Preference dataset pack</div>
                <h3>{datasetPack.summary.pair_count} preference pairs</h3>
              </div>
              <div className="mini-note">{datasetPack.summary.distinct_categories} categories</div>
            </div>
            <div className="pill-row">
              <span className="pill">chosen shape {datasetPack.summary.chosen_shape}</span>
              <span className="pill">multi-call {datasetPack.summary.multi_call_pairs}</span>
              <span className="pill">event {datasetPack.summary.event_driven_pairs}</span>
              {datasetPack.summary.rejection_counts.slice(0, 3).map((item) => (
                <span key={item.rejection_type} className="pill subtle">{item.rejection_type} {item.count}</span>
              ))}
            </div>
            <div className="level6-list">
              {datasetPack.focus_pairs.slice(0, 3).map((pair) => (
                <article key={pair.id} className="level6-item">
                  <strong>{pair.id}</strong>
                  <p>{pair.prompt_user}</p>
                  <div className="pill-row">
                    <span className="pill">chosen {pair.chosen.output_shape}</span>
                    <span className="pill subtle">rejected {pair.rejected.output_shape}</span>
                    <span className="pill subtle">{pair.category}</span>
                  </div>
                  <div className="level6-reason">{pair.preference_reason}</div>
                </article>
              ))}
            </div>
            <div className="level6-notes">
              {datasetPack.teaching_notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          </article>
        ) : null}
        {compareReport ? (
          <article className="level6-card">
            <div className="level6-head">
              <div>
                <div className="eyebrow">Policy compare report</div>
                <h3>SFT-only vs preference-aware</h3>
              </div>
              <div className="mini-note">{compareReport.compare_cases.length} demo cases</div>
            </div>
            <div className="level6-policy-grid">
              {compareReport.policies.map((policy) => (
                <article key={policy.policy_id} className="level6-item">
                  <strong>{policy.title}</strong>
                  <div className="pill-row">
                    <span className="pill">win {formatRatio(policy.summary.chosen_win_rate, policy.summary.total_cases)}</span>
                    <span className="pill subtle">structured {formatRatio(policy.summary.structured_output_preference, policy.summary.total_cases)}</span>
                    <span className="pill">rubric {policy.summary.weighted_rubric_score}</span>
                    <span className="pill subtle">hard fail {policy.summary.hard_failure_cases}</span>
                  </div>
                  <p>{policy.summary.behavior}</p>
                </article>
              ))}
            </div>
            <div className="level6-list">
              {compareReport.compare_cases.slice(0, 2).map((item) => (
                <article key={item.id} className="level6-item">
                  <strong>{item.id}</strong>
                  <p>{item.prompt_user}</p>
                  <div className="pill-row">
                    <span className="pill subtle">baseline {item.baseline_policy.decision}</span>
                    <span className="pill">preference {item.preference_policy.decision}</span>
                    <span className="pill subtle">rubric {item.preference_policy.assessment.score_points}</span>
                  </div>
                  <div className="level6-reason">{item.preference_reason}</div>
                  {item.preference_policy.assessment.hard_failures.length ? (
                    <div className="level6-reason">Hard failures: {item.preference_policy.assessment.hard_failures.join(", ")}</div>
                  ) : null}
                </article>
              ))}
            </div>
            <div className="level6-scale-grid">
              {compareReport.scale_up_guidance.map((item) => (
                <article key={item.step} className="level6-scale-card">
                  <div className="eyebrow">Step {item.step}</div>
                  <strong>{item.title}</strong>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </article>
        ) : null}
      </div>
      {scaleUpRubric ? (
        <div className="level6-rubric-panel">
          <div className="level6-scaleup-head">
            <div>
              <div className="eyebrow">Scale-up rubric</div>
              <h3>{scaleUpRubric.summary.weighted_rubric_score} weighted score</h3>
            </div>
            <RoadmapBadge status={scaleUpRubric.summary.weighted_rubric_score >= 85 ? "live" : "partial"} />
          </div>
          <p className="level6-scaleup-summary">
            baseline {scaleUpRubric.summary.baseline_weighted_score} {"->"} preference {scaleUpRubric.summary.weighted_rubric_score}
          </p>
          <div className="level6-gate-grid">
            {scaleUpRubric.criteria.map((criterion) => (
              <article key={criterion.id} className={`level6-gate-card ${criterion.status}`}>
                <div className="stage-head">
                  <strong>{criterion.title}</strong>
                  <RoadmapBadge status={criterion.status === "pass" ? "live" : "partial"} />
                </div>
                <div className="pill-row">
                  <span className="pill">current {criterion.current_score}</span>
                  <span className="pill subtle">baseline {criterion.baseline_score}</span>
                  <span className="pill subtle">target {criterion.target_for_e4b}</span>
                </div>
                <p>{criterion.why}</p>
              </article>
            ))}
          </div>
          <div className="level6-rubric-grid">
            <article className="level6-item">
              <strong>Coverage</strong>
              <div className="level6-list">
                {scaleUpRubric.coverage.map((item) => (
                  <article key={item.category} className="level6-item">
                    <div className="pill-row">
                      <span className="pill">{item.category}</span>
                      <span className="pill subtle">{item.pairs} pairs</span>
                    </div>
                    <div className="level6-reason">{item.why}</div>
                  </article>
                ))}
              </div>
            </article>
            <article className="level6-item">
              <strong>Acceptance bar</strong>
              <div className="level6-list">
                {scaleUpRubric.acceptance_bar.map((item) => (
                  <article key={item} className="level6-item">
                    <p>{item}</p>
                  </article>
                ))}
              </div>
            </article>
            <article className="level6-item">
              <strong>Experiment plan</strong>
              <div className="level6-list">
                {scaleUpRubric.experiment_plan.map((item) => (
                  <article key={item.stage} className="level6-item">
                    <div className="pill-row">
                      <span className="pill">{item.stage}</span>
                    </div>
                    <p>{item.title}</p>
                    <div className="level6-reason">{item.goal}</div>
                  </article>
                ))}
              </div>
            </article>
          </div>
        </div>
      ) : null}
      {scaleUpCompare ? (
        <div className="level6-scaleup-panel">
          <div className="level6-scaleup-head">
            <div>
              <div className="eyebrow">Gemma scale-up compare</div>
              <h3>{scaleUpCompare.recommendation.model}</h3>
            </div>
            <RoadmapBadge status={scaleUpCompare.recommendation.stage === "scale-up" ? "live" : "partial"} />
          </div>
          <p className="level6-scaleup-summary">{scaleUpCompare.recommendation.summary}</p>
          <div className="pill-row">
            <span className="pill">weighted rubric {scaleUpCompare.current_state.weighted_rubric_score}</span>
            <span className="pill subtle">hard failures {scaleUpCompare.current_state.hard_failure_rate}%</span>
            <span className="pill subtle">coverage {scaleUpCompare.current_state.coverage_categories}</span>
          </div>
          <div className="level6-policy-grid">
            {scaleUpCompare.model_profiles.map((profile) => (
              <article key={profile.model} className="level6-item">
                <strong>{profile.model}</strong>
                <div className="pill-row">
                  <span className="pill">fit {profile.fit_score}</span>
                  <span className="pill subtle">{profile.cost_class}</span>
                  <span className="pill subtle">{profile.expected_cycle}</span>
                </div>
                <p>{profile.best_for}</p>
                <div className="level6-reason">{profile.strength}</div>
                <div className="level6-reason">Risk: {profile.risk}</div>
              </article>
            ))}
          </div>
          <div className="level6-gate-grid">
            {scaleUpCompare.gates.map((gate) => (
              <article key={gate.gate} className={`level6-gate-card ${gate.status}`}>
                <div className="stage-head">
                  <strong>{gate.gate}</strong>
                  <RoadmapBadge status={gate.status === "pass" ? "live" : "partial"} />
                </div>
                <div className="pill-row">
                  <span className="pill">current {gate.current}</span>
                  <span className="pill subtle">target {gate.target_for_e4b}</span>
                </div>
                <p>{gate.why}</p>
              </article>
            ))}
          </div>
          <div className="level6-rubric-grid">
            {scaleUpCompare.decision_matrix.map((item) => (
              <article key={item.criterion} className="level6-item">
                <strong>{item.criterion}</strong>
                <p>{item.current_state}</p>
                <div className="level6-reason">E2B-it: {item.e2b_it}</div>
                <div className="level6-reason">E4B-it: {item.e4b_it}</div>
              </article>
            ))}
          </div>
          <div className="level6-list">
            {scaleUpCompare.recommendation.reasoning.map((item) => (
              <article key={item} className="level6-item">
                <p>{item}</p>
              </article>
            ))}
          </div>
          <div className="level6-list">
            {scaleUpCompare.recommendation.next_actions.map((item) => (
              <article key={item} className="level6-item">
                <strong>Next</strong>
                <p>{item}</p>
              </article>
            ))}
          </div>
        </div>
      ) : null}
    </CollapsiblePanel>
  );
}

function OverviewViewImpl(props: { data: LabData; onPick: (view: View) => void }) {
  return (
    <div className="view-grid">
      <StarterGuide onPick={props.onPick} />
      <section className="panel span-2">
        <ManifestoHero data={props.data} />
      </section>
      <LearningRoadmapPanel data={props.data} />
      <Level1Panel data={props.data} />
      <GemmaTrackPanel data={props.data} />
      <ReferenceProjectsPanel data={props.data} />
      <Level5Panel data={props.data} />
      <BehaviorEvalPanel data={props.data} />
      <DataScaleComparePanel data={props.data} />
      <Level6Panel data={props.data} />
      <CollapsiblePanel title="Workflow stages" subtitle="agent 解释链路的锚点。" audience="新手">
        <div className="stage-list compact">
          {props.data.workflow_stages.map((stage) => (
            <article key={stage.id} className="stage-card">
              <div className="stage-head">
                <strong>{stage.title}</strong>
                <span>{stage.commands[0]}</span>
              </div>
              <p>{stage.teaching_goal}</p>
            </article>
          ))}
        </div>
      </CollapsiblePanel>
    </div>
  );
}

export const OverviewView = memo(OverviewViewImpl);
