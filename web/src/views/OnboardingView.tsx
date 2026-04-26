import { memo } from "react";
import type { LabData } from "../data-layer";
import { SectionTitle, StatusBadge } from "../components/ui";

function OnboardingViewImpl(props: { data: LabData }) {
  return (
    <div className="view-grid">
      <section className="panel span-2">
        <SectionTitle title="Agent handoff timeline" subtitle="先 sense（探仓库），再 prepare（装环境），再 teach（跑训练），再 compare（对比 probe）。" audience="新手" />
        <ol className="timeline">
          {props.data.agent_handoff_timeline.map((step) => (
            <li key={step.step} className="timeline-step">
              <div className="timeline-dot">{step.step}</div>
              <div>
                <div className="eyebrow">{step.eyebrow}</div>
                <h3>{step.title}</h3>
                <code className="timeline-cmd">{step.command}</code>
                <p>{step.body}</p>
                <div className="artifact-hint">artifact → <code>{step.artifact}</code></div>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <section className="panel">
        <SectionTitle title="Readiness" subtitle="当前机器、依赖和关键产物状态。这反映的是仓库本地状态，不是访客本地状态。" audience="工程" />
        <div className="checklist">
          {props.data.onboarding.readiness.map((item) => (
            <article key={item.id} className="check-item">
              <div className="stage-head">
                <strong>{item.label}</strong>
                <StatusBadge status={item.status} />
              </div>
              <p>{item.detail}</p>
              {item.fix_command ? <code>{item.fix_command}</code> : null}
            </article>
          ))}
        </div>
      </section>
      <section className="panel">
        <SectionTitle title="Learning progress" subtitle="agent 不只知道仓库能不能跑，也知道学习链路现在推进到哪一关。" audience="工程" />
        <div className="run-card">
          <div className="run-tag">
            {props.data.onboarding.learning_progress.completed_stage_count}/{props.data.onboarding.learning_progress.total_stage_count} stages
          </div>
          <h3>{props.data.onboarding.learning_progress.next_stage?.title ?? "All stages ready"}</h3>
          <p>{props.data.onboarding.learning_progress.next_stage?.command ?? "make ai-lab"}</p>
        </div>
        <div className="checklist compact-list">
          {props.data.onboarding.stage_readiness.map((stage) => (
            <article key={stage.id} className="check-item">
              <div className="stage-head">
                <strong>{stage.title}</strong>
                <span>{stage.ready_count}/{stage.total_count}</span>
              </div>
              <p>{stage.detail}</p>
              <div className="pill-row">
                <span className="pill subtle">{stage.status}</span>
                <span className="pill">{stage.command}</span>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="panel">
        <SectionTitle title="Agent prompts" subtitle="复制给 Codex / Claude 即可接手。" audience="工程" />
        <div className="prompt-grid">
          {props.data.agent_prompts.map((prompt) => (
            <article key={prompt.title} className="prompt-card">
              <div className="stage-head">
                <strong>{prompt.title}</strong>
                <span>{prompt.agent}</span>
              </div>
              <pre>{prompt.prompt}</pre>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

export const OnboardingView = memo(OnboardingViewImpl);
