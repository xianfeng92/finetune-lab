import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webRoot = path.resolve(__dirname, "..");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatRatio(value, total) {
  return `${value}/${total}`;
}

function formatPercent(value, total) {
  if (!total) return "0%";
  return `${Math.round((value / total) * 100)}%`;
}

function formatBytes(value) {
  if (value >= 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(2)} MB`;
  if (value >= 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${value} B`;
}

function formatTimestamp(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function pickPromptUser(sample) {
  const userMessage = sample.messages.find((message) => message.role === "user");
  return typeof userMessage?.content === "string" ? userMessage.content : "";
}

function pickAssistantToolNames(sample) {
  const assistantMessage = sample.messages.find((message) => message.role === "assistant");
  const toolCalls = Array.isArray(assistantMessage?.tool_calls) ? assistantMessage.tool_calls : [];
  return toolCalls.map((tool) => tool?.name).filter(Boolean);
}

function pickAssistantToolArgs(sample) {
  const assistantMessage = sample.messages.find((message) => message.role === "assistant");
  const toolCalls = Array.isArray(assistantMessage?.tool_calls) ? assistantMessage.tool_calls : [];
  return toolCalls[0]?.arguments ?? null;
}

function renderPills(items, className = "pill") {
  return items.map((item) => `<span class="${className}">${escapeHtml(item)}</span>`).join("");
}

function renderBars(items, tone = "lime") {
  if (!items.length) return `<p class="mini-note">no data</p>`;
  const max = Math.max(...items.map((item) => item.value), 1);
  return items.map((item) => `
    <div class="bar-row">
      <div class="bar-head">
        <span>${escapeHtml(item.label)}</span>
        <strong>${item.value}</strong>
      </div>
      <div class="bar-track">
        <div class="bar-fill ${tone}" style="width:${(item.value / max) * 100}%"></div>
      </div>
    </div>
  `).join("");
}

function renderLossCurveSVG(curve, tone = "lime") {
  const points = Array.isArray(curve?.points) ? curve.points : [];
  if (!points.length) return `<div class="curve-empty">no train-metrics.jsonl</div>`;
  const width = 640;
  const height = 180;
  const padX = 32;
  const padY = 22;
  const steps = points.map((p) => p.step);
  const losses = points.map((p) => p.loss);
  const minStep = Math.min(...steps);
  const maxStep = Math.max(...steps);
  const minLoss = Math.min(...losses);
  const maxLoss = Math.max(...losses);
  const stepSpan = Math.max(1, maxStep - minStep);
  const lossSpan = Math.max(0.0001, maxLoss - minLoss);
  const toX = (s) => padX + ((s - minStep) / stepSpan) * (width - 2 * padX);
  const toY = (l) => padY + (1 - (l - minLoss) / lossSpan) * (height - 2 * padY);
  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.step).toFixed(1)},${toY(p.loss).toFixed(1)}`).join(" ");
  const areaPath = `${linePath} L${toX(maxStep).toFixed(1)},${(height - padY).toFixed(1)} L${toX(minStep).toFixed(1)},${(height - padY).toFixed(1)} Z`;
  const gridLines = [0.25, 0.5, 0.75].map((t) => {
    const y = padY + t * (height - 2 * padY);
    return `<line x1="${padX}" y1="${y}" x2="${width - padX}" y2="${y}" class="grid-line"/>`;
  }).join("");
  const lastPoint = points[points.length - 1];
  const firstPoint = points[0];
  return `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" class="loss-svg ${tone}" role="img" aria-label="training loss curve">
      <defs>
        <linearGradient id="grad-${tone}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="currentColor" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="currentColor" stop-opacity="0"/>
        </linearGradient>
      </defs>
      ${gridLines}
      <path d="${areaPath}" fill="url(#grad-${tone})" />
      <path d="${linePath}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="${toX(firstPoint.step).toFixed(1)}" cy="${toY(firstPoint.loss).toFixed(1)}" r="3" fill="currentColor"/>
      <circle cx="${toX(lastPoint.step).toFixed(1)}" cy="${toY(lastPoint.loss).toFixed(1)}" r="4" fill="currentColor"/>
      <text x="${toX(firstPoint.step).toFixed(1) - 4}" y="${(toY(firstPoint.loss) - 8).toFixed(1)}" class="curve-label">step ${firstPoint.step} · loss ${firstPoint.loss.toFixed(2)}</text>
      <text x="${toX(lastPoint.step).toFixed(1) - 4}" y="${(toY(lastPoint.loss) - 8).toFixed(1)}" text-anchor="end" class="curve-label">step ${lastPoint.step} · loss ${lastPoint.loss.toFixed(2)}</text>
    </svg>
  `;
}

function renderHero(data) {
  const manifesto = data.manifesto ?? {};
  const headline = (manifesto.headline ?? "Clone it.\nHand it to an agent.\nWatch a model learn.")
    .split("\n")
    .map((line) => `<span class="hero-line">${escapeHtml(line)}</span>`)
    .join("");
  const commands = manifesto.hero_commands ?? ["make ai-onboarding", "make ai-setup", "make ai-lab"];
  const runs = data.runs ?? [];
  const latestRun = runs[runs.length - 1];
  const firstRun = runs[0];
  const lossDelta = latestRun?.trainingCurve?.loss_delta_pct;
  const steps = latestRun?.manifest?.max_steps ?? 0;
  const samples = data.dataset.summary.total_samples;
  return `
    <section class="hero">
      <div class="hero-head">
        <div class="hero-tag">
          <span class="hero-dot"></span>
          <span class="eyebrow">${escapeHtml(manifesto.eyebrow ?? "AI-native fine-tuning lab")}</span>
          <span class="hero-meta">snapshot · ${escapeHtml(formatTimestamp(data.generated_at))}</span>
        </div>
        <div class="hero-cta">
          <a class="hero-repo" href="../../README.md">README.md</a>
          <a class="hero-repo" href="../../AGENTS.md">AGENTS.md</a>
        </div>
      </div>
      <h1 class="hero-title">${headline}</h1>
      <p class="hero-lede">${escapeHtml(manifesto.lede ?? data.project.primary_goal)}</p>
      <div class="hero-cmd-row">
        ${commands.map((cmd, i) => `
          <div class="hero-cmd">
            <span class="hero-cmd-idx">${String(i + 1).padStart(2, "0")}</span>
            <code>${escapeHtml(cmd)}</code>
          </div>
        `).join("")}
      </div>
      <div class="hero-stats">
        <article class="hero-stat">
          <div class="hero-stat-label">samples</div>
          <div class="hero-stat-value">${samples}</div>
          <div class="hero-stat-hint">SFT demo dataset</div>
        </article>
        <article class="hero-stat">
          <div class="hero-stat-label">runs</div>
          <div class="hero-stat-value">${runs.length}</div>
          <div class="hero-stat-hint">${escapeHtml(firstRun?.manifest.title ?? "no runs")} → ${escapeHtml(latestRun?.manifest.title ?? "—")}</div>
        </article>
        <article class="hero-stat accent">
          <div class="hero-stat-label">loss ↓</div>
          <div class="hero-stat-value">${lossDelta !== null && lossDelta !== undefined ? `${lossDelta}%` : "—"}</div>
          <div class="hero-stat-hint">across ${steps} smoke-train steps</div>
        </article>
        <article class="hero-stat">
          <div class="hero-stat-label">onboarding</div>
          <div class="hero-stat-value">${escapeHtml(data.onboarding.overall_status)}</div>
          <div class="hero-stat-hint">${escapeHtml(data.onboarding.next_steps[0]?.command ?? "make ai-onboarding")}</div>
        </article>
      </div>
    </section>
  `;
}

function renderTenets(data) {
  const tenets = data.manifesto?.tenets ?? [];
  if (!tenets.length) return "";
  return `
    <section class="tenets">
      ${tenets.map((t) => `
        <article class="tenet">
          <div class="tenet-idx">${escapeHtml(t.index)}</div>
          <h3>${escapeHtml(t.title)}</h3>
          <p>${escapeHtml(t.body)}</p>
        </article>
      `).join("")}
    </section>
  `;
}

function renderRoadmapBlock(data) {
  const roadmap = data.learning_roadmap;
  const track = data.gemma_track;
  const trackPack = data.gemma_track_pack;
  const references = data.reference_projects ?? [];
  if (!roadmap) return "";
  return `
    <section class="block" id="roadmap">
      <header class="block-head">
        <div>
          <div class="eyebrow">01 · Gemma roadmap</div>
          <h2>${escapeHtml(roadmap.headline)}</h2>
          <p>${escapeHtml(roadmap.summary)}</p>
        </div>
      </header>
      ${track ? `
        <div class="grid two-col roadmap-meta-grid">
          <article class="card">
            <div class="card-head"><h3>${escapeHtml(track.headline)}</h3><span class="mini-note">base model strategy</span></div>
            <p class="roadmap-summary">${escapeHtml(track.summary)}</p>
            <div class="track-grid">
              <article class="track-card">
                <div class="track-label">Default base</div>
                <h4>${escapeHtml(track.default_model.name)}</h4>
                <p>${escapeHtml(track.default_model.role)}</p>
                <div class="track-why">${escapeHtml(track.default_model.why)}</div>
              </article>
              <article class="track-card alt">
                <div class="track-label">Compare with</div>
                <h4>${escapeHtml(track.comparison_model.name)}</h4>
                <p>${escapeHtml(track.comparison_model.role)}</p>
                <div class="track-why">${escapeHtml(track.comparison_model.why)}</div>
              </article>
              <article class="track-card">
                <div class="track-label">Specialization focus</div>
                <h4>${escapeHtml(track.specialization_focus.title)}</h4>
                <p>${escapeHtml(track.specialization_focus.body)}</p>
              </article>
            </div>
            <div class="chip-row">
              ${(track.upgrade_path ?? []).map((item) => `<span class="chip ghost">${escapeHtml(item)}</span>`).join("")}
            </div>
            ${trackPack ? `
              <div class="level6-list">
                ${(trackPack.checkpoints ?? []).map((item) => `
                  <article class="level6-item">
                    <strong>${escapeHtml(item.name)}</strong>
                    <p>${escapeHtml(item.teaching_role)}</p>
                    <div class="level6-reason">${escapeHtml(item.best_for)}</div>
                    <div class="chip-row">
                      ${(item.strengths ?? []).slice(0, 2).map((strength) => `<span class="chip ghost">${escapeHtml(strength)}</span>`).join("")}
                    </div>
                  </article>
                `).join("")}
              </div>
              <div class="level6-list">
                ${(trackPack.comparison_axes ?? []).map((item) => `
                  <article class="level6-item">
                    <strong>${escapeHtml(item.axis)}</strong>
                    <p>base: ${escapeHtml(item.base)}</p>
                    <p>instruct: ${escapeHtml(item.instruct)}</p>
                    <div class="level6-reason">${escapeHtml(item.why_it_matters)}</div>
                  </article>
                `).join("")}
              </div>
            ` : ""}
          </article>
          <article class="card">
            <div class="card-head"><h3>What to learn from hot open-source labs</h3><span class="mini-note">repo positioning</span></div>
            <div class="reference-list">
              ${references.map((project) => `
                <article class="reference-item">
                  <div class="reference-top">
                    <a href="${escapeHtml(project.url)}" target="_blank" rel="noreferrer">${escapeHtml(project.name)}</a>
                    <span>${escapeHtml(project.signal)}</span>
                  </div>
                  <p>${escapeHtml(project.takeaway)}</p>
                </article>
              `).join("")}
            </div>
          </article>
        </div>
      ` : ""}
      <div class="roadmap-grid">
        ${(roadmap.levels ?? []).map((level) => `
          <article class="roadmap-card ${escapeHtml(level.status)}">
            <div class="roadmap-card-head">
              <div>
                <div class="eyebrow small">${escapeHtml(level.label)}</div>
                <h3>${escapeHtml(level.title)}</h3>
              </div>
              <span class="roadmap-badge ${escapeHtml(level.status)}">${escapeHtml(level.status)}</span>
            </div>
            <div class="roadmap-model">${escapeHtml(level.model)}</div>
            <p>${escapeHtml(level.goal)}</p>
            <div class="roadmap-why">
              <strong>Why it matters</strong>
              <span>${escapeHtml(level.why_it_matters)}</span>
            </div>
            <div class="chip-row">
              ${(level.commands ?? []).map((command) => `<span class="chip">${escapeHtml(command)}</span>`).join("")}
            </div>
            <div class="roadmap-detail-grid">
              <div>
                <h4>Focus metrics</h4>
                <div class="chip-row">
                  ${(level.focus_metrics ?? []).map((metric) => `<span class="chip ghost">${escapeHtml(metric)}</span>`).join("")}
                </div>
              </div>
              <div>
                <h4>Artifacts</h4>
                <div class="roadmap-artifacts">
                  ${(level.artifacts ?? []).map((artifact) => `<code>${escapeHtml(artifact)}</code>`).join("")}
                </div>
              </div>
            </div>
            <div class="roadmap-pitfall">Pitfall: ${escapeHtml(level.pitfall)}</div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderLevel1Block(data) {
  const taskPack = data.level1?.task_framing_pack;
  const baselinePack = data.level1?.baseline_eval_pack;
  if (!taskPack && !baselinePack) return "";
  return `
    <section class="block" id="level1">
      <header class="block-head">
        <div>
          <div class="eyebrow">02 · Level 1 baseline</div>
          <h2>Task framing before the first training run</h2>
          <p>先把任务定义、success rubric 和 baseline failure buckets 讲清楚。这样后面的 SFT、probe 和 compare 才知道自己在改什么。</p>
        </div>
      </header>
      <div class="grid two-col">
        ${taskPack ? `
          <article class="card">
            <div class="card-head"><h3>Task framing pack</h3><span class="mini-note">${escapeHtml(taskPack.dataset_profile.total_samples)} samples</span></div>
            <p class="roadmap-summary">${escapeHtml(taskPack.task_brief.user_job)}</p>
            <div class="level1-reason">${escapeHtml(taskPack.task_brief.target_behavior)}</div>
            <div class="chip-row">
              ${(taskPack.dataset_profile.category_counts ?? []).slice(0, 4).map((item) => `<span class="chip">${escapeHtml(item.category)} ${escapeHtml(item.count)}</span>`).join("")}
            </div>
            <div class="level1-bucket-grid">
              ${(taskPack.failure_buckets ?? []).map((bucket) => `
                <article class="level1-bucket-card">
                  <strong>${escapeHtml(bucket.label)}</strong>
                  <p>${escapeHtml(bucket.description)}</p>
                  <div class="chip-row">
                    <span class="chip ghost">${escapeHtml(bucket.affected_category)}</span>
                    <span class="chip ghost">${escapeHtml(bucket.sample_count)} samples</span>
                  </div>
                </article>
              `).join("")}
            </div>
            <div class="level1-list">
              ${(taskPack.held_out_seed_cases ?? []).slice(0, 3).map((item) => `
                <article class="level1-item">
                  <strong>${escapeHtml(item.id)}</strong>
                  <p>${escapeHtml(item.prompt_surface?.text ?? "")}</p>
                  <div class="chip-row">
                    ${(item.risk_flags ?? []).map((flag) => `<span class="chip ghost">${escapeHtml(flag)}</span>`).join("")}
                  </div>
                  <div class="level1-reason">${escapeHtml(item.baseline_hypothesis)}</div>
                </article>
              `).join("")}
            </div>
          </article>
        ` : ""}
        ${baselinePack ? `
          <article class="card">
            <div class="card-head"><h3>Baseline eval pack</h3><span class="mini-note">${escapeHtml(baselinePack.summary.case_count)} held-out cases</span></div>
            <p class="roadmap-summary">${escapeHtml(baselinePack.baseline_profile.strategy)}</p>
            <div class="level1-metric-grid">
              <article class="level1-metric-card"><span>route hit</span><strong>${formatRatio(baselinePack.summary.route_selection_hit, baselinePack.summary.case_count)}</strong></article>
              <article class="level1-metric-card"><span>executable</span><strong>${formatRatio(baselinePack.summary.executable_output, baselinePack.summary.case_count)}</strong></article>
              <article class="level1-metric-card"><span>arguments</span><strong>${formatRatio(baselinePack.summary.arguments_complete, baselinePack.summary.case_count)}</strong></article>
              <article class="level1-metric-card"><span>overall pass</span><strong>${formatRatio(baselinePack.summary.overall_pass, baselinePack.summary.case_count)}</strong></article>
            </div>
            <div class="level1-list">
              ${(baselinePack.cases ?? []).slice(0, 3).map((item) => `
                <article class="level1-item">
                  <strong>${escapeHtml(item.id)}</strong>
                  <p>${escapeHtml(item.prompt_surface?.text ?? "")}</p>
                  <div class="chip-row">
                    <span class="chip ghost">${escapeHtml(item.baseline_prediction.output_shape)}</span>
                    <span class="chip">${escapeHtml(item.likely_failure_bucket)}</span>
                  </div>
                  <div class="level1-reason">${escapeHtml(item.lesson)}</div>
                </article>
              `).join("")}
            </div>
            <div class="level1-notes">
              ${(baselinePack.next_actions ?? []).map((item) => `<p>${escapeHtml(item)}</p>`).join("")}
            </div>
          </article>
        ` : ""}
      </div>
    </section>
  `;
}

function renderTimeline(data) {
  const timeline = data.agent_handoff_timeline ?? [];
  const readiness = data.onboarding?.readiness ?? [];
  const stageReadiness = data.onboarding?.stage_readiness ?? [];
  const progress = data.onboarding?.learning_progress ?? {};
  const nextSteps = data.onboarding?.next_steps ?? [];
  return `
    <section class="block" id="agent-handoff">
      <header class="block-head">
        <div>
          <div class="eyebrow">03 · Agent handoff</div>
          <h2>How an agent picks up this repo</h2>
          <p>不是"让用户自己先配好环境"，而是一条 agent 可以独立推进的时间线。每一步都指向一个可验证的产物。</p>
        </div>
      </header>
      <ol class="timeline">
        ${timeline.map((step) => `
          <li class="timeline-step">
            <div class="timeline-rail">
              <span class="timeline-dot">${escapeHtml(step.step)}</span>
            </div>
            <div class="timeline-body">
              <div class="timeline-top">
                <span class="eyebrow small">${escapeHtml(step.eyebrow)}</span>
                <h3>${escapeHtml(step.title)}</h3>
                <code class="timeline-cmd">${escapeHtml(step.command)}</code>
              </div>
              <p>${escapeHtml(step.body)}</p>
              <div class="artifact-hint">artifact → <code>${escapeHtml(step.artifact)}</code></div>
            </div>
          </li>
        `).join("")}
      </ol>
      <div class="grid two-col readiness-grid">
        <article class="card">
          <div class="card-head">
            <h3>Readiness checklist</h3>
            <span class="mini-note">${escapeHtml(formatTimestamp(data.onboarding.generated_at))}</span>
          </div>
          <div class="check-list">
            ${readiness.map((item) => `
              <div class="check-row ${item.status}">
                <span class="check-dot"></span>
                <div>
                  <div class="check-label">${escapeHtml(item.label)}</div>
                  <p>${escapeHtml(item.detail)}</p>
                  ${item.fix_command ? `<code>${escapeHtml(item.fix_command)}</code>` : ""}
                </div>
                <span class="status-tag ${item.status}">${escapeHtml(item.status)}</span>
              </div>
            `).join("")}
          </div>
        </article>
        <article class="card">
          <div class="card-head">
            <h3>Next recommended actions</h3>
            <span class="mini-note">agent-facing</span>
          </div>
          <div class="next-card">
            <div class="next-top">
              <strong>Learning progress</strong>
              <code>${escapeHtml(`${progress.completed_stage_count ?? 0}/${progress.total_stage_count ?? 0}`)}</code>
            </div>
            <p>${escapeHtml(progress.next_stage?.title ?? "All learning stages are currently ready.")}</p>
            ${progress.next_stage?.command ? `<code>${escapeHtml(progress.next_stage.command)}</code>` : ""}
          </div>
          <div class="next-list">
            ${(nextSteps.length ? nextSteps : [{ title: "Looks ready", command: "make ai-lab", reason: "可以直接刷一遍最小闭环。" }]).map((step) => `
              <article class="next-card">
                <div class="next-top">
                  <strong>${escapeHtml(step.title)}</strong>
                  <code>${escapeHtml(step.command)}</code>
                </div>
                <p>${escapeHtml(step.reason)}</p>
              </article>
            `).join("")}
          </div>
          <div class="level6-list">
            ${stageReadiness.map((stage) => `
              <article class="level6-item">
                <div class="stage-head">
                  <strong>${escapeHtml(stage.title)}</strong>
                  <span>${escapeHtml(`${stage.ready_count}/${stage.total_count}`)}</span>
                </div>
                <p>${escapeHtml(stage.detail)}</p>
                <div class="chip-row">
                  <span class="chip ghost">${escapeHtml(stage.status)}</span>
                  <span class="chip">${escapeHtml(stage.command)}</span>
                </div>
              </article>
            `).join("")}
          </div>
          <div class="prompt-panel">
            <div class="prompt-panel-head">
              <span class="eyebrow small">copy to agent</span>
              <span class="mini-note">粘贴给 Codex / Claude 即可接手</span>
            </div>
            ${(data.agent_prompts ?? []).map((prompt) => `
              <details class="prompt-accordion">
                <summary><span class="agent-tag ${escapeHtml(prompt.agent)}">${escapeHtml(prompt.agent)}</span><span>${escapeHtml(prompt.title)}</span></summary>
                <pre>${escapeHtml(prompt.prompt)}</pre>
              </details>
            `).join("")}
          </div>
        </article>
      </div>
    </section>
  `;
}

function renderDataBlock(data) {
  const categoryItems = data.dataset.summary.category_counts.map(({ category, count }) => ({
    label: category,
    value: count,
  }));
  const domainItems = data.dataset.summary.domain_counts.map(({ domain, count }) => ({
    label: domain,
    value: count,
  }));
  const generatorItems = data.dataset.summary.generator_counts.map(({ model, count }) => ({
    label: model,
    value: count,
  }));
  const featured = data.dataset.samples.slice(0, 3);

  return `
    <section class="block" id="data-pipeline">
      <header class="block-head">
        <div>
          <div class="eyebrow">04 · Data pipeline</div>
          <h2>What a tool-call training sample actually looks like</h2>
          <p>每一条 SFT 样本的信号结构是固定的：<code>loaded_tool_names</code> 给出候选工具，<code>user</code> 给出自然语言意图，<code>assistant.tool_calls</code> 是期望输出。微调学的就是这三者之间的映射。</p>
        </div>
      </header>
      <div class="data-hero">
        ${featured.map((sample, idx) => {
          const promptUser = pickPromptUser(sample);
          const expectedNames = pickAssistantToolNames(sample);
          const expectedArgs = pickAssistantToolArgs(sample);
          return `
            <article class="anatomy-card">
              <div class="anatomy-head">
                <span class="sample-id">${escapeHtml(sample.id)}</span>
                <span class="anatomy-cat">${escapeHtml(sample.category)}</span>
              </div>
              <div class="anatomy-row">
                <span class="anatomy-label">loaded tools</span>
                <div class="pill-row">${renderPills(sample.loaded_tool_names)}</div>
              </div>
              <div class="anatomy-row user-row">
                <span class="anatomy-label">user</span>
                <div class="user-utterance">${escapeHtml(promptUser || "—")}</div>
              </div>
              <div class="anatomy-arrow">↓ fine-tune signal ${idx + 1}</div>
              <div class="anatomy-row">
                <span class="anatomy-label">expected</span>
                <div class="pill-row">${renderPills(expectedNames.length ? expectedNames : ["none"], "pill alt")}</div>
              </div>
              ${expectedArgs ? `<pre class="anatomy-args">${escapeHtml(JSON.stringify(expectedArgs, null, 2))}</pre>` : ""}
            </article>
          `;
        }).join("")}
      </div>
      <div class="grid two-col">
        <article class="card">
          <div class="card-head"><h3>Category coverage</h3><span class="mini-note">${data.dataset.summary.total_samples} samples</span></div>
          <div class="bars">${renderBars(categoryItems, "lime")}</div>
        </article>
        <article class="card">
          <div class="card-head"><h3>Train / held-out split</h3><span class="mini-note">probe no longer reuses train rows</span></div>
          <div class="level6-list">
            <article class="level6-item">
              <strong>full dataset</strong>
              <p>${escapeHtml(data.source.dataset)}</p>
            </article>
            <article class="level6-item">
              <strong>train</strong>
              <p>${escapeHtml(data.source.train_dataset)}</p>
            </article>
            <article class="level6-item">
              <strong>held-out probe</strong>
              <p>${escapeHtml(data.source.held_out_dataset)}</p>
            </article>
          </div>
        </article>
        <article class="card">
          <div class="card-head"><h3>Domain footprint</h3><span class="mini-note">vehicle-control demo</span></div>
          <div class="bars">${renderBars(domainItems, "magenta")}</div>
          <div class="chip-row">
            ${generatorItems.map((item) => `<span class="chip ghost">${escapeHtml(item.label)} · ${item.value}</span>`).join("")}
          </div>
        </article>
      </div>
    </section>
  `;
}

function renderTrainingBlock(data) {
  const runs = data.runs ?? [];
  if (!runs.length) return "";
  return `
    <section class="block" id="training">
      <header class="block-head">
        <div>
          <div class="eyebrow">05 · Training curves</div>
          <h2>Watch the loss come down</h2>
          <p>train-metrics.jsonl 里每一步的 loss 都被读出来画成曲线。这里明确展示的是 teaching-oriented simulated smoke train，不是假装真实大规模训练。</p>
        </div>
      </header>
      <div class="grid train-grid">
        ${runs.map((run, idx) => {
          const tone = idx === 0 ? "lime" : "magenta";
          const curve = run.trainingCurve;
          return `
            <article class="card curve-card ${tone}">
              <div class="curve-head">
                <div>
                  <div class="eyebrow small">${escapeHtml(run.manifest.engine)} · ${run.manifest.max_steps} steps</div>
                  <h3>${escapeHtml(run.manifest.title)}</h3>
                  <p class="mini-note">${escapeHtml(run.manifest.model_name)}</p>
                  ${run.manifest.simulation_note ? `<p class="mini-note">${escapeHtml(run.manifest.simulation_note)}</p>` : ""}
                </div>
                <div class="curve-delta">
                  <div class="delta-top">avg loss</div>
                  <div class="delta-value">${run.manifest.avg_loss.toFixed(3)}</div>
                  ${curve?.loss_delta_pct !== null && curve?.loss_delta_pct !== undefined ? `<div class="delta-sub">↓ ${curve.loss_delta_pct}% from first step</div>` : ""}
                </div>
              </div>
              ${renderLossCurveSVG(curve, tone)}
              <div class="curve-footer">
                <span class="chip">exact ${formatPercent(run.metrics.exactNameMatch, run.metrics.total)}</span>
                <span class="chip">parsed ${formatPercent(run.metrics.parsedJson, run.metrics.total)}</span>
                <span class="chip">signal ${formatPercent(run.metrics.toolSignal, run.metrics.total)}</span>
              </div>
              <div class="artifact-strip">
                ${run.artifacts.map((artifact) => `
                  <div class="artifact-row">
                    <span class="artifact-name">${escapeHtml(artifact.name)}</span>
                    <span class="artifact-size">${formatBytes(artifact.size_bytes)}</span>
                    <span class="artifact-path">${escapeHtml(artifact.relative_path)}</span>
                  </div>
                `).join("")}
              </div>
            </article>
          `;
        }).join("")}
      </div>
    </section>
  `;
}

function renderCompareBlock(data) {
  const runs = data.runs ?? [];
  if (runs.length < 2) return "";
  const delta = data.run_delta;
  const baseline = runs[0];
  const improved = runs[runs.length - 1];
  const metricRows = [
    { label: "max steps", a: baseline.manifest.max_steps, b: improved.manifest.max_steps, kind: "raw" },
    { label: "avg loss", a: baseline.manifest.avg_loss, b: improved.manifest.avg_loss, kind: "loss" },
    { label: "exact name match", a: baseline.metrics.exactNameMatch, b: improved.metrics.exactNameMatch, total: baseline.metrics.total, kind: "ratio" },
    { label: "any expected hit", a: baseline.metrics.anyExpectedNameHit, b: improved.metrics.anyExpectedNameHit, total: baseline.metrics.total, kind: "ratio" },
    { label: "parsed JSON", a: baseline.metrics.parsedJson, b: improved.metrics.parsedJson, total: baseline.metrics.total, kind: "ratio" },
    { label: "tool-call signal", a: baseline.metrics.toolSignal, b: improved.metrics.toolSignal, total: baseline.metrics.total, kind: "ratio" },
  ];
  return `
    <section class="block" id="compare">
      <header class="block-head">
        <div>
          <div class="eyebrow">06 · Before / After</div>
          <h2>${escapeHtml(baseline.manifest.title)} <span class="big-arrow">→</span> ${escapeHtml(improved.manifest.title)}</h2>
          <p>同一个数据集、同一组 probe case，两个 run 只差训练步数。avg loss 下降 <strong>${delta?.avg_loss_delta_pct ?? "—"}%</strong>，training steps 放大 <strong>${delta?.steps_multiplier ?? "—"}×</strong>。</p>
        </div>
      </header>
      <div class="grid two-col compare-grid">
        <article class="card compare-side lime">
          <div class="compare-tag">baseline · ${baseline.manifest.max_steps} steps</div>
          <h3>${escapeHtml(baseline.manifest.title)}</h3>
          <dl class="stat-grid">
            <div><dt>avg loss</dt><dd>${baseline.manifest.avg_loss.toFixed(3)}</dd></div>
            <div><dt>exact</dt><dd>${formatRatio(baseline.metrics.exactNameMatch, baseline.metrics.total)}</dd></div>
            <div><dt>parsed</dt><dd>${formatRatio(baseline.metrics.parsedJson, baseline.metrics.total)}</dd></div>
            <div><dt>signal</dt><dd>${formatRatio(baseline.metrics.toolSignal, baseline.metrics.total)}</dd></div>
          </dl>
        </article>
        <article class="card compare-side magenta">
          <div class="compare-tag">improved · ${improved.manifest.max_steps} steps</div>
          <h3>${escapeHtml(improved.manifest.title)}</h3>
          <dl class="stat-grid">
            <div><dt>avg loss</dt><dd>${improved.manifest.avg_loss.toFixed(3)}</dd></div>
            <div><dt>exact</dt><dd>${formatRatio(improved.metrics.exactNameMatch, improved.metrics.total)}</dd></div>
            <div><dt>parsed</dt><dd>${formatRatio(improved.metrics.parsedJson, improved.metrics.total)}</dd></div>
            <div><dt>signal</dt><dd>${formatRatio(improved.metrics.toolSignal, improved.metrics.total)}</dd></div>
          </dl>
        </article>
      </div>
      <article class="card delta-matrix">
        <div class="card-head"><h3>Delta matrix</h3><span class="mini-note">baseline → improved</span></div>
        <table class="delta-table">
          <thead>
            <tr><th>metric</th><th>${escapeHtml(baseline.manifest.title)}</th><th>${escapeHtml(improved.manifest.title)}</th><th>Δ</th></tr>
          </thead>
          <tbody>
            ${metricRows.map((row) => {
              let aDisplay = "";
              let bDisplay = "";
              let deltaDisplay = "";
              let deltaClass = "neutral";
              if (row.kind === "raw") {
                aDisplay = String(row.a);
                bDisplay = String(row.b);
                const diff = row.b - row.a;
                deltaDisplay = diff === 0 ? "0" : (diff > 0 ? `+${diff}` : `${diff}`);
                deltaClass = diff === 0 ? "neutral" : (diff > 0 ? "up" : "down");
              } else if (row.kind === "loss") {
                aDisplay = row.a.toFixed(3);
                bDisplay = row.b.toFixed(3);
                const diff = +(row.b - row.a).toFixed(3);
                deltaDisplay = diff === 0 ? "0" : (diff > 0 ? `+${diff}` : `${diff}`);
                deltaClass = diff < 0 ? "up" : (diff > 0 ? "down" : "neutral");
              } else {
                aDisplay = formatRatio(row.a, row.total);
                bDisplay = formatRatio(row.b, row.total);
                const diff = row.b - row.a;
                deltaDisplay = diff === 0 ? "held" : (diff > 0 ? `+${diff}` : `${diff}`);
                deltaClass = diff === 0 ? "neutral" : (diff > 0 ? "up" : "down");
              }
              return `
                <tr>
                  <td>${escapeHtml(row.label)}</td>
                  <td>${aDisplay}</td>
                  <td>${bDisplay}</td>
                  <td><span class="delta-chip ${deltaClass}">${escapeHtml(deltaDisplay)}</span></td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
        <p class="delta-note">
          注意：这个 demo 的 probe 是 5 条 case 的小集合，在 20 步就已经饱和。<br/>
          真实微调里 avg loss 持续下降 + probe 饱和 = 脚手架稳定；曲线还有空间 + probe 饱和 = 可以尝试扩数据或调难度。
        </p>
      </article>
    </section>
  `;
}

function renderLevel5Block(data) {
  const toolPack = data.level5?.tool_routing_pack;
  const structuredPack = data.level5?.structured_output_pack;
  if (!toolPack && !structuredPack) return "";
  return `
    <section class="block" id="level5">
      <header class="block-head">
        <div>
          <div class="eyebrow">07 · Level 5 pack</div>
          <h2>Structured outputs and tool calling, as a teaching pack</h2>
          <p>这层不再只看“loss 有没有下降”，而是单独抽出 route selection、tool_calls 结构和 arguments match 来看模型是不是学会了 agent 场景里的关键行为。</p>
        </div>
      </header>
      <div class="grid two-col">
        ${toolPack ? `
          <article class="card">
            <div class="card-head"><h3>Tool-routing dataset pack</h3><span class="mini-note">${toolPack.summary.multi_tool_samples} multi-choice samples</span></div>
            <div class="chip-row">
              <span class="chip">avg candidates ${escapeHtml(toolPack.summary.avg_candidate_count)}</span>
              <span class="chip">single ${escapeHtml(toolPack.summary.single_tool_samples)}</span>
              <span class="chip">multi ${escapeHtml(toolPack.summary.multi_tool_samples)}</span>
            </div>
            <div class="level5-split">
              <div>
                <h4>Top routes</h4>
                <div class="bars">${renderBars((toolPack.summary.route_counts ?? []).slice(0, 5).map((item) => ({ label: item.tool_name, value: item.count })), "lime")}</div>
              </div>
              <div>
                <h4>Focus samples</h4>
                <div class="level5-list">
                  ${(toolPack.focus_samples ?? []).slice(0, 3).map((sample) => `
                    <article class="level5-item">
                      <strong>${escapeHtml(sample.expected_name)}</strong>
                      <p>${escapeHtml(sample.prompt_user ?? "")}</p>
                      <div class="chip-row">
                        <span class="chip ghost">${escapeHtml(sample.route_type)}</span>
                        ${(sample.loaded_tool_names ?? []).map((tool) => `<span class="chip ghost">${escapeHtml(tool)}</span>`).join("")}
                      </div>
                    </article>
                  `).join("")}
                </div>
              </div>
            </div>
            <div class="level5-notes">
              ${(toolPack.teaching_notes ?? []).map((note) => `<p>${escapeHtml(note)}</p>`).join("")}
            </div>
          </article>
        ` : ""}
        ${structuredPack ? `
          <article class="card">
            <div class="card-head"><h3>Structured-output probe pack</h3><span class="mini-note">${escapeHtml(structuredPack.runs?.length ?? 0)} run views</span></div>
            <div class="level5-run-grid">
              ${(structuredPack.runs ?? []).map((run) => `
                <article class="level5-item">
                  <div class="stage-head">
                    <strong>${escapeHtml(run.title)}</strong>
                    <span>${escapeHtml(run.max_steps)} steps</span>
                  </div>
                  <div class="chip-row">
                    <span class="chip">exact ${formatRatio(run.summary.exact_name_match, run.summary.total_cases)}</span>
                    <span class="chip">tool_calls ${formatRatio(run.summary.tool_calls_array, run.summary.total_cases)}</span>
                    <span class="chip">args ${formatRatio(run.summary.arguments_match, run.summary.total_cases)}</span>
                  </div>
                </article>
              `).join("")}
            </div>
            <div class="level5-list">
              ${(structuredPack.compare_cases ?? []).slice(0, 2).map((probeCase) => `
                <article class="level5-item">
                  <strong>${escapeHtml(probeCase.id)}</strong>
                  <p>${escapeHtml(probeCase.prompt_user ?? "")}</p>
                  <div class="chip-row">
                    ${(probeCase.runs ?? []).map((run) => `<span class="chip ghost">${escapeHtml(run.max_steps)} step · ${escapeHtml(run.output_shape)}</span>`).join("")}
                  </div>
                </article>
              `).join("")}
            </div>
            <div class="level5-notes">
              ${(structuredPack.teaching_notes ?? []).map((note) => `<p>${escapeHtml(note)}</p>`).join("")}
            </div>
          </article>
        ` : ""}
      </div>
    </section>
  `;
}

function renderBehaviorEvalBlock(data) {
  const pack = data.behavior_eval_pack;
  if (!pack) return "";
  return `
    <section class="block" id="behavior-eval">
      <header class="block-head">
        <div>
          <div class="eyebrow">Behavior eval pack</div>
          <h2>Route accuracy is not enough if behavior and safety contracts drift</h2>
          <p>这层单独看 behavior accuracy、unsafe direct call、confirm contract 和 reject contract。它的目的是把“工具名选对了”和“系统下一步做对了”拆开来验。</p>
        </div>
      </header>
      <div class="grid two-col">
        ${(pack.runs ?? []).map((run) => `
          <article class="card">
            <div class="card-head"><h3>${escapeHtml(run.title)}</h3><span class="mini-note">${escapeHtml(run.max_steps)} steps</span></div>
            <div class="chip-row">
              <span class="chip">behavior ${formatRatio(run.behavior_metrics.behavior_accuracy.hit, run.behavior_metrics.behavior_accuracy.total)}</span>
              <span class="chip ghost">unsafe ${formatRatio(run.behavior_metrics.unsafe_direct_call_rate.count, run.behavior_metrics.unsafe_direct_call_rate.total)}</span>
              <span class="chip ghost">high-risk ${formatRatio(run.behavior_metrics.high_risk_direct_call_rate.count, run.behavior_metrics.high_risk_direct_call_rate.total)}</span>
              <span class="chip">confirm ${formatRatio(run.behavior_metrics.confirmation_contract_hit.hit, run.behavior_metrics.confirmation_contract_hit.total)}</span>
              <span class="chip ghost">reject ${formatRatio(run.behavior_metrics.refusal_contract_hit.hit, run.behavior_metrics.refusal_contract_hit.total)}</span>
            </div>
            <div class="level5-split">
              <div>
                <h4>Predicted behaviors</h4>
                <div class="bars">${renderBars(Object.entries(run.behavior_metrics.predicted_behavior_counts ?? {}).map(([label, value]) => ({ label, value })), "magenta")}</div>
              </div>
              <div>
                <h4>Miss cases</h4>
                <div class="level6-list">
                  ${(run.miss_cases ?? []).slice(0, 3).map((item) => `
                    <article class="level6-item">
                      <strong>${escapeHtml(item.id)}</strong>
                      <div class="chip-row">
                        <span class="chip ghost">${escapeHtml(item.category)}</span>
                        <span class="chip">${escapeHtml(item.behavior)} → ${escapeHtml(item.predicted_behavior)}</span>
                        <span class="chip ghost">${escapeHtml(item.risk)}</span>
                      </div>
                      <div class="level6-reason">predicted tools: ${escapeHtml((item.predicted_names ?? []).join(", ") || "none")}</div>
                      ${item.expected_system_action ? `<div class="level6-reason">expected system action: ${escapeHtml(item.expected_system_action.type)}</div>` : ""}
                      ${item.unsafe_direct_call ? `<div class="level6-reason">unsafe direct call triggered</div>` : ""}
                    </article>
                  `).join("")}
                </div>
              </div>
            </div>
          </article>
        `).join("")}
      </div>
      <div class="level6-notes">
        ${(pack.teaching_notes ?? []).map((note) => `<p>${escapeHtml(note)}</p>`).join("")}
      </div>
    </section>
  `;
}

function renderDataScaleCompareBlock(data) {
  const pack = data.data_scale_compare_pack;
  if (!pack) return "";
  return `
    <section class="block" id="data-scale-compare">
      <header class="block-head">
        <div>
          <div class="eyebrow">Data scale compare</div>
          <h2>Small, medium, and large only make sense when strategy stays visible</h2>
          <p>这一块把 small / medium / large 和 direct mixed / curriculum + consolidation 放在一起看，避免误读成“数据多就一定更好”。</p>
        </div>
      </header>
      <div class="grid two-col">
        ${(pack.scenarios ?? []).map((scenario) => `
          <article class="card">
            <div class="card-head"><h3>${escapeHtml(scenario.label)}</h3><span class="mini-note">${escapeHtml(scenario.dataset.counts.train)}/${escapeHtml(scenario.dataset.counts.valid)}/${escapeHtml(scenario.dataset.counts.test)}</span></div>
            <div class="chip-row">
              <span class="chip">exact ${formatRatio(scenario.metrics.exact_name_match.hit, scenario.metrics.exact_name_match.total)}</span>
              <span class="chip ghost">structured ${formatRatio(scenario.metrics.structured_output_valid.hit, scenario.metrics.structured_output_valid.total)}</span>
              <span class="chip">args ${formatRatio(scenario.metrics.arguments_match.hit, scenario.metrics.arguments_match.total)}</span>
              <span class="chip ghost">behavior ${formatRatio(scenario.metrics.behavior_accuracy.hit, scenario.metrics.behavior_accuracy.total)}</span>
            </div>
            <div class="chip-row">
              <span class="chip ghost">unsafe ${formatRatio(scenario.metrics.unsafe_direct_call_rate.count, scenario.metrics.unsafe_direct_call_rate.total)}</span>
              <span class="chip">confirm ${formatRatio(scenario.metrics.confirmation_contract_hit.hit, scenario.metrics.confirmation_contract_hit.total)}</span>
              <span class="chip ghost">reject ${formatRatio(scenario.metrics.refusal_contract_hit.hit, scenario.metrics.refusal_contract_hit.total)}</span>
              <span class="chip ghost">loss ${escapeHtml(scenario.avg_loss.toFixed(3))}</span>
            </div>
            <div class="level6-reason">train behaviors: ${escapeHtml(Object.entries(scenario.dataset.train_behaviors ?? {}).map(([key, value]) => `${key} ${value}`).join(" · "))}</div>
          </article>
        `).join("")}
      </div>
      <div class="level6-rubric-grid">
        ${(pack.matrix ?? []).map((row) => `
          <article class="level6-item">
            <strong>${escapeHtml(row.label)}</strong>
            <div class="level6-list">
              ${(row.scenarios ?? []).map((scenario) => `
                <article class="level6-item">
                  <div class="chip-row">
                    <span class="chip">${escapeHtml(scenario.label)}</span>
                    <span class="chip ghost">${formatRatio(scenario.value, scenario.total)}</span>
                  </div>
                  <div class="level6-reason">rate ${escapeHtml((scenario.rate * 100).toFixed(1))}%</div>
                </article>
              `).join("")}
            </div>
          </article>
        `).join("")}
      </div>
      <div class="level6-notes">
        ${(pack.teaching_notes ?? []).map((note) => `<p>${escapeHtml(note)}</p>`).join("")}
      </div>
    </section>
  `;
}

function renderLevel6Block(data) {
  const datasetPack = data.level6?.preference_dataset_pack;
  const compareReport = data.level6?.policy_compare_report;
  const scaleUpRubric = data.level6?.scale_up_rubric;
  const scaleUpCompare = data.level6?.scale_up_compare;
  if (!datasetPack && !compareReport && !scaleUpRubric && !scaleUpCompare) return "";
  return `
    <section class="block" id="level6">
      <header class="block-head">
        <div>
          <div class="eyebrow">08 · Level 6 demo</div>
          <h2>Preference tuning, rubric, and realistic scale-up compare</h2>
          <p>Level 6 现在不只看 chosen win，而是一起看 rubric、hard failures、coverage breadth 和什么时候才值得把 E4B-it 拉进来做确认性实验。</p>
        </div>
      </header>
      <div class="grid two-col">
        ${datasetPack ? `
          <article class="card">
            <div class="card-head"><h3>Preference dataset pack</h3><span class="mini-note">${datasetPack.summary.pair_count} pairs</span></div>
            <div class="chip-row">
              <span class="chip">chosen ${escapeHtml(datasetPack.summary.chosen_shape)}</span>
              <span class="chip">multi-call ${escapeHtml(datasetPack.summary.multi_call_pairs)}</span>
              <span class="chip">event ${escapeHtml(datasetPack.summary.event_driven_pairs)}</span>
              ${(datasetPack.summary.rejection_counts ?? []).slice(0, 3).map((item) => `<span class="chip ghost">${escapeHtml(item.rejection_type)} ${escapeHtml(item.count)}</span>`).join("")}
            </div>
            <div class="level6-list">
              ${(datasetPack.focus_pairs ?? []).slice(0, 3).map((pair) => `
                <article class="level6-item">
                  <strong>${escapeHtml(pair.id)}</strong>
                  <p>${escapeHtml(pair.prompt_user ?? "")}</p>
                  <div class="chip-row">
                    <span class="chip">chosen ${escapeHtml(pair.chosen.output_shape)}</span>
                    <span class="chip ghost">rejected ${escapeHtml(pair.rejected.output_shape)}</span>
                    <span class="chip ghost">${escapeHtml(pair.category)}</span>
                  </div>
                  <div class="level6-reason">${escapeHtml(pair.preference_reason)}</div>
                </article>
              `).join("")}
            </div>
            <div class="level6-notes">
              ${(datasetPack.teaching_notes ?? []).map((note) => `<p>${escapeHtml(note)}</p>`).join("")}
            </div>
          </article>
        ` : ""}
        ${compareReport ? `
          <article class="card">
            <div class="card-head"><h3>Policy compare report</h3><span class="mini-note">${escapeHtml(compareReport.compare_cases?.length ?? 0)} cases</span></div>
            <div class="level6-policy-grid">
              ${(compareReport.policies ?? []).map((policy) => `
                <article class="level6-item">
                  <strong>${escapeHtml(policy.title)}</strong>
                  <div class="chip-row">
                    <span class="chip">win ${formatRatio(policy.summary.chosen_win_rate, policy.summary.total_cases)}</span>
                    <span class="chip ghost">structured ${formatRatio(policy.summary.structured_output_preference, policy.summary.total_cases)}</span>
                    <span class="chip">rubric ${escapeHtml(policy.summary.weighted_rubric_score)}</span>
                    <span class="chip ghost">hard fail ${escapeHtml(policy.summary.hard_failure_cases)}</span>
                  </div>
                  <p>${escapeHtml(policy.summary.behavior)}</p>
                </article>
              `).join("")}
            </div>
            <div class="level6-list">
              ${(compareReport.compare_cases ?? []).slice(0, 2).map((item) => `
                <article class="level6-item">
                  <strong>${escapeHtml(item.id)}</strong>
                  <p>${escapeHtml(item.prompt_user ?? "")}</p>
                  <div class="chip-row">
                    <span class="chip ghost">baseline ${escapeHtml(item.baseline_policy.decision)}</span>
                    <span class="chip">preference ${escapeHtml(item.preference_policy.decision)}</span>
                    <span class="chip ghost">rubric ${escapeHtml(item.preference_policy.assessment.score_points)}</span>
                  </div>
                  <div class="level6-reason">${escapeHtml(item.preference_reason)}</div>
                  ${item.preference_policy.assessment.hard_failures?.length ? `<div class="level6-reason">Hard failures: ${escapeHtml(item.preference_policy.assessment.hard_failures.join(", "))}</div>` : ""}
                </article>
              `).join("")}
            </div>
            <div class="level6-scale-grid">
              ${(compareReport.scale_up_guidance ?? []).map((item) => `
                <article class="level6-scale-card">
                  <div class="eyebrow small">Step ${escapeHtml(item.step)}</div>
                  <strong>${escapeHtml(item.title)}</strong>
                  <p>${escapeHtml(item.body)}</p>
                </article>
              `).join("")}
            </div>
          </article>
        ` : ""}
      </div>
      ${scaleUpRubric ? `
        <article class="card level6-rubric-panel">
          <div class="card-head">
            <div>
              <div class="eyebrow">Scale-up rubric</div>
              <h3>${escapeHtml(scaleUpRubric.summary.weighted_rubric_score)} weighted score</h3>
            </div>
            <span class="roadmap-badge ${escapeHtml(scaleUpRubric.summary.weighted_rubric_score >= 85 ? "live" : "partial")}">${escapeHtml(scaleUpRubric.summary.weighted_rubric_score >= 85 ? "live" : "partial")}</span>
          </div>
          <p class="roadmap-summary">baseline ${escapeHtml(scaleUpRubric.summary.baseline_weighted_score)} → preference ${escapeHtml(scaleUpRubric.summary.weighted_rubric_score)}</p>
          <div class="level6-gate-grid">
            ${(scaleUpRubric.criteria ?? []).map((criterion) => `
              <article class="level6-gate-card ${escapeHtml(criterion.status)}">
                <div class="stage-head">
                  <strong>${escapeHtml(criterion.title)}</strong>
                  <span class="roadmap-badge ${escapeHtml(criterion.status === "pass" ? "live" : "partial")}">${escapeHtml(criterion.status)}</span>
                </div>
                <div class="chip-row">
                  <span class="chip">current ${escapeHtml(criterion.current_score)}</span>
                  <span class="chip ghost">baseline ${escapeHtml(criterion.baseline_score)}</span>
                  <span class="chip ghost">target ${escapeHtml(criterion.target_for_e4b)}</span>
                </div>
                <p>${escapeHtml(criterion.why)}</p>
              </article>
            `).join("")}
          </div>
          <div class="level6-rubric-grid">
            <article class="level6-item">
              <strong>Coverage</strong>
              <div class="level6-list">
                ${(scaleUpRubric.coverage ?? []).map((item) => `
                  <article class="level6-item">
                    <div class="chip-row">
                      <span class="chip">${escapeHtml(item.category)}</span>
                      <span class="chip ghost">${escapeHtml(item.pairs)} pairs</span>
                    </div>
                    <div class="level6-reason">${escapeHtml(item.why)}</div>
                  </article>
                `).join("")}
              </div>
            </article>
            <article class="level6-item">
              <strong>Acceptance bar</strong>
              <div class="level6-list">
                ${(scaleUpRubric.acceptance_bar ?? []).map((item) => `
                  <article class="level6-item"><p>${escapeHtml(item)}</p></article>
                `).join("")}
              </div>
            </article>
            <article class="level6-item">
              <strong>Experiment plan</strong>
              <div class="level6-list">
                ${(scaleUpRubric.experiment_plan ?? []).map((item) => `
                  <article class="level6-item">
                    <div class="chip-row"><span class="chip">${escapeHtml(item.stage)}</span></div>
                    <p>${escapeHtml(item.title)}</p>
                    <div class="level6-reason">${escapeHtml(item.goal)}</div>
                  </article>
                `).join("")}
              </div>
            </article>
          </div>
        </article>
      ` : ""}
      ${scaleUpCompare ? `
        <article class="card level6-scaleup-panel">
          <div class="card-head">
            <div>
              <div class="eyebrow">Gemma scale-up compare</div>
              <h3>${escapeHtml(scaleUpCompare.recommendation.model)}</h3>
            </div>
            <span class="roadmap-badge ${escapeHtml(scaleUpCompare.recommendation.stage === "scale-up" ? "live" : "partial")}">${escapeHtml(scaleUpCompare.recommendation.stage)}</span>
          </div>
          <p class="roadmap-summary">${escapeHtml(scaleUpCompare.recommendation.summary)}</p>
          <div class="chip-row">
            <span class="chip">weighted rubric ${escapeHtml(scaleUpCompare.current_state.weighted_rubric_score)}</span>
            <span class="chip ghost">hard failures ${escapeHtml(scaleUpCompare.current_state.hard_failure_rate)}%</span>
            <span class="chip ghost">coverage ${escapeHtml(scaleUpCompare.current_state.coverage_categories)}</span>
          </div>
          <div class="level6-policy-grid">
            ${(scaleUpCompare.model_profiles ?? []).map((profile) => `
              <article class="level6-item">
                <strong>${escapeHtml(profile.model)}</strong>
                <div class="chip-row">
                  <span class="chip">fit ${escapeHtml(profile.fit_score)}</span>
                  <span class="chip ghost">${escapeHtml(profile.cost_class)}</span>
                  <span class="chip ghost">${escapeHtml(profile.expected_cycle)}</span>
                </div>
                <p>${escapeHtml(profile.best_for)}</p>
                <div class="level6-reason">${escapeHtml(profile.strength)}</div>
                <div class="level6-reason">Risk: ${escapeHtml(profile.risk)}</div>
              </article>
            `).join("")}
          </div>
          <div class="level6-gate-grid">
            ${(scaleUpCompare.gates ?? []).map((gate) => `
              <article class="level6-gate-card ${escapeHtml(gate.status)}">
                <div class="stage-head">
                  <strong>${escapeHtml(gate.gate)}</strong>
                  <span class="roadmap-badge ${escapeHtml(gate.status === "pass" ? "live" : "partial")}">${escapeHtml(gate.status)}</span>
                </div>
                <div class="chip-row">
                  <span class="chip">current ${escapeHtml(gate.current)}</span>
                  <span class="chip ghost">target ${escapeHtml(gate.target_for_e4b)}</span>
                </div>
                <p>${escapeHtml(gate.why)}</p>
              </article>
            `).join("")}
          </div>
          <div class="level6-rubric-grid">
            ${(scaleUpCompare.decision_matrix ?? []).map((item) => `
              <article class="level6-item">
                <strong>${escapeHtml(item.criterion)}</strong>
                <p>${escapeHtml(item.current_state)}</p>
                <div class="level6-reason">E2B-it: ${escapeHtml(item.e2b_it)}</div>
                <div class="level6-reason">E4B-it: ${escapeHtml(item.e4b_it)}</div>
              </article>
            `).join("")}
          </div>
          <div class="level6-list">
            ${(scaleUpCompare.recommendation.reasoning ?? []).map((item) => `
              <article class="level6-item"><p>${escapeHtml(item)}</p></article>
            `).join("")}
          </div>
          <div class="level6-list">
            ${(scaleUpCompare.recommendation.next_actions ?? []).map((item) => `
              <article class="level6-item"><strong>Next</strong><p>${escapeHtml(item)}</p></article>
            `).join("")}
          </div>
        </article>
      ` : ""}
    </section>
  `;
}

function renderProbeBlock(data) {
  const runs = data.runs ?? [];
  if (!runs.length) return "";
  const probeRows = runs[0].probeResults.slice(0, 4);
  return `
    <section class="block" id="probe">
      <header class="block-head">
        <div>
          <div class="eyebrow">09 · Probe cases</div>
          <h2>Case-by-case: did the model pick the right tool?</h2>
          <p>每条 held-out case 都同时展示期望值、raw output 和工具名命中情况。当前 probe 数据来自 <code>${escapeHtml(data.source.held_out_dataset)}</code>，不再直接复用训练集。</p>
        </div>
      </header>
      <div class="probe-stack">
        ${probeRows.map((row) => `
          <article class="card probe-card">
            <div class="probe-top">
              <div>
                <span class="sample-id">${escapeHtml(row.id)}</span>
                <h3>${escapeHtml(row.prompt_user || "—")}</h3>
                <p class="mini-note">category · ${escapeHtml(row.category)}</p>
              </div>
              <div class="pill-row">
                <span class="pill alt">expected: ${escapeHtml(row.expected_names.join(", ") || "none")}</span>
              </div>
            </div>
            <div class="probe-columns">
              ${runs.map((run, idx) => {
                const result = run.probeResults.find((item) => item.id === row.id);
                if (!result) return "";
                const tone = idx === 0 ? "lime" : "magenta";
                const hit = result.exact_name_match;
                return `
                  <section class="probe-col ${tone} ${hit ? "hit" : "miss"}">
                    <div class="probe-col-head">
                      <strong>${escapeHtml(run.manifest.title)}</strong>
                      <span class="status-tag ${hit ? "ready" : "missing"}">${hit ? "exact" : "miss"}</span>
                    </div>
                    <div class="mini-strip">
                      <span>predicted: ${escapeHtml(result.predicted_names.join(", ") || "—")}</span>
                      <span>parsed: ${escapeHtml(String(result.parsed_output !== null))}</span>
                      <span>signal: ${escapeHtml(String(result.has_tool_calls_signal))}</span>
                      <span>${escapeHtml(run.manifest.training_mode ?? "unknown")} probe</span>
                    </div>
                    <pre>${escapeHtml(result.raw_output || "[empty]")}</pre>
                  </section>
                `;
              }).join("")}
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderTakeaways(data) {
  const items = data.teaching_takeaways ?? [];
  if (!items.length) return "";
  return `
    <section class="block" id="takeaways">
      <header class="block-head">
        <div>
          <div class="eyebrow">10 · Takeaways</div>
          <h2>What you should be able to explain after one loop</h2>
          <p>跑完 <code>make ai-lab</code> 之后，你已经看过一条微调训练最完整的最小信号链。这些是值得带走的四个结论。</p>
        </div>
      </header>
      <div class="takeaway-grid">
        ${items.map((item) => `
          <article class="takeaway">
            <div class="takeaway-num">${escapeHtml(item.number)}</div>
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(item.body)}</p>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderFooter(data) {
  const stages = data.workflow_stages ?? [];
  return `
    <footer class="site-footer">
      <div class="footer-grid">
        <div>
          <div class="eyebrow">workflow map</div>
          <ol class="workflow-map">
            ${stages.map((s) => `
              <li>
                <strong>${escapeHtml(s.title)}</strong>
                <code>${escapeHtml(s.commands[0] ?? "")}</code>
                <span>${escapeHtml(s.teaching_goal)}</span>
              </li>
            `).join("")}
          </ol>
        </div>
        <div>
          <div class="eyebrow">run it yourself</div>
          <pre class="footer-cmd">$ git clone &lt;repo&gt; && cd finetune-lab
$ make ai-onboarding
$ make ai-setup
$ make ai-lab</pre>
          <p class="footer-note">
            page rendered from <code>web/public/lab-data.json</code><br/>
            last build · ${escapeHtml(formatTimestamp(data.generated_at))}
          </p>
        </div>
      </div>
    </footer>
  `;
}

function renderHtml(data) {
  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>finetune-lab · agent handoff teaching lab</title>
    <style>
      :root {
        color-scheme: dark;
        --ink: #0b0d0c;
        --ink-2: #111514;
        --ink-3: #1a1f1d;
        --line: rgba(212, 255, 58, 0.14);
        --line-soft: rgba(255, 255, 255, 0.06);
        --text: #f2f1ea;
        --muted: #8a8f88;
        --lime: #d4ff3a;
        --lime-soft: rgba(212, 255, 58, 0.12);
        --magenta: #ff5eac;
        --magenta-soft: rgba(255, 94, 172, 0.14);
        --amber: #ffb347;
        --red: #ff6b6b;
        --shadow: 0 40px 120px rgba(0, 0, 0, 0.55);
        font-family: "Geist", "IBM Plex Sans", "Inter", "Avenir Next", sans-serif;
        line-height: 1.5;
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        color: var(--text);
        background:
          radial-gradient(1100px 520px at 12% -10%, rgba(212, 255, 58, 0.12), transparent 60%),
          radial-gradient(900px 480px at 92% 8%, rgba(255, 94, 172, 0.10), transparent 60%),
          radial-gradient(700px 480px at 50% 100%, rgba(255, 179, 71, 0.06), transparent 60%),
          linear-gradient(180deg, #080a09 0%, #0b0d0c 40%, #050706 100%);
      }

      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image:
          linear-gradient(transparent 0 calc(100% - 1px), rgba(255, 255, 255, 0.035) 100%),
          linear-gradient(90deg, transparent 0 calc(100% - 1px), rgba(255, 255, 255, 0.035) 100%);
        background-size: 48px 48px;
        pointer-events: none;
        z-index: 0;
        mask-image: radial-gradient(ellipse at 50% 40%, rgba(0, 0, 0, 0.85), transparent 75%);
      }

      main {
        position: relative;
        z-index: 1;
        width: min(1260px, calc(100vw - 28px));
        margin: 0 auto;
        padding: 34px 0 72px;
      }

      h1, h2, h3, h4 {
        margin: 0;
        font-family: "Geist", "IBM Plex Sans", "Inter", sans-serif;
        letter-spacing: -0.02em;
        color: var(--text);
      }

      p { margin: 0; color: var(--muted); }

      code, pre, table, .mono {
        font-family: "Geist Mono", "IBM Plex Mono", "JetBrains Mono", "SFMono-Regular", ui-monospace, monospace;
      }

      a { color: var(--lime); text-decoration: none; }
      a:hover { text-decoration: underline; }

      .eyebrow {
        color: var(--lime);
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.72rem;
        font-weight: 700;
      }

      .eyebrow.small { font-size: 0.66rem; }

      .mini-note { color: var(--muted); font-size: 0.82rem; letter-spacing: 0.02em; }

      .hero {
        position: relative;
        padding: 32px 36px 28px;
        border: 1px solid var(--line);
        border-radius: 28px;
        background:
          linear-gradient(180deg, rgba(17, 21, 20, 0.86), rgba(11, 13, 12, 0.92)),
          radial-gradient(680px 380px at 80% 0%, rgba(212, 255, 58, 0.14), transparent 60%);
        box-shadow: var(--shadow);
        overflow: hidden;
      }

      .hero::after {
        content: "";
        position: absolute;
        right: -80px;
        bottom: -140px;
        width: 380px;
        height: 380px;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(212, 255, 58, 0.22), transparent 70%);
        pointer-events: none;
      }

      .hero-head {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 18px;
      }

      .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 7px 14px 7px 10px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.02);
      }

      .hero-dot {
        width: 8px; height: 8px; border-radius: 999px;
        background: var(--lime); box-shadow: 0 0 14px rgba(212, 255, 58, 0.8);
      }

      .hero-meta { color: var(--muted); font-size: 0.76rem; }

      .hero-cta { display: flex; gap: 8px; flex-wrap: wrap; }

      .hero-repo {
        padding: 7px 12px;
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--text);
        font-size: 0.82rem;
        font-family: "Geist Mono", ui-monospace, monospace;
      }
      .hero-repo:hover { border-color: var(--lime); color: var(--lime); text-decoration: none; }

      .hero-title {
        display: block;
        font-size: clamp(2.6rem, 6.4vw, 5.2rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
        font-weight: 700;
        margin-top: 8px;
      }

      .hero-title .hero-line {
        display: block;
      }

      .hero-title .hero-line:nth-child(2) {
        color: var(--lime);
      }

      .hero-lede {
        max-width: 66ch;
        margin-top: 20px;
        color: #c6cbc1;
        font-size: 1.06rem;
      }

      .hero-cmd-row {
        margin-top: 26px;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }

      .hero-cmd {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(10, 12, 11, 0.65);
      }

      .hero-cmd-idx {
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.72rem;
        color: var(--lime);
        letter-spacing: 0.12em;
      }

      .hero-cmd code {
        color: var(--text);
        font-size: 0.96rem;
      }

      .hero-stats {
        margin-top: 26px;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
      }

      .hero-stat {
        padding: 16px 18px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(10, 12, 11, 0.65);
      }

      .hero-stat.accent {
        background:
          linear-gradient(180deg, rgba(212, 255, 58, 0.08), rgba(10, 12, 11, 0.9));
        border-color: rgba(212, 255, 58, 0.28);
      }

      .hero-stat-label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.72rem;
      }

      .hero-stat-value {
        margin-top: 8px;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
      }

      .hero-stat.accent .hero-stat-value { color: var(--lime); }

      .hero-stat-hint {
        margin-top: 6px;
        color: var(--muted);
        font-size: 0.82rem;
      }

      .tenets {
        margin-top: 22px;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
      }

      .tenet {
        position: relative;
        padding: 22px 22px 22px 24px;
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(17, 21, 20, 0.78), rgba(10, 12, 11, 0.92));
        min-height: 168px;
      }

      .tenet-idx {
        font-family: "Geist Mono", ui-monospace, monospace;
        color: var(--lime);
        font-size: 0.82rem;
        letter-spacing: 0.1em;
      }

      .tenet h3 {
        margin-top: 10px;
        font-size: 1.14rem;
      }

      .tenet p {
        margin-top: 8px;
      }

      .roadmap-meta-grid { margin-top: 0; }

      .roadmap-summary {
        margin-top: 0;
        color: #c5ccbe;
      }

      .track-grid,
      .reference-list {
        display: grid;
        gap: 12px;
        margin-top: 16px;
      }

      .track-card,
      .reference-item {
        padding: 16px;
        border: 1px solid var(--line-soft);
        border-radius: 16px;
        background: rgba(12, 15, 14, 0.74);
      }

      .track-card.alt { border-color: rgba(255, 94, 172, 0.22); }

      .track-label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
      }

      .track-card h4 {
        margin-top: 8px;
        font-size: 1.06rem;
      }

      .track-card p,
      .track-why,
      .reference-item p {
        margin-top: 6px;
        color: #c6ccbf;
      }

      .reference-top {
        display: grid;
        gap: 4px;
      }

      .reference-top a {
        color: var(--text);
        font-weight: 700;
        text-decoration: none;
      }

      .reference-top a:hover { color: var(--lime); }

      .reference-top span {
        color: var(--muted);
        font-size: 0.84rem;
      }

      .roadmap-grid {
        margin-top: 18px;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }

      .roadmap-card {
        padding: 22px;
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        background: rgba(9, 11, 10, 0.8);
      }

      .roadmap-card.live { border-color: rgba(212, 255, 58, 0.24); }
      .roadmap-card.partial { border-color: rgba(255, 255, 255, 0.12); }
      .roadmap-card.next { border-color: rgba(255, 94, 172, 0.24); }
      .roadmap-card.planned { border-style: dashed; }

      .roadmap-card-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
      }

      .roadmap-card-head h3 {
        margin-top: 6px;
        font-size: 1.2rem;
      }

      .roadmap-badge {
        display: inline-flex;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }

      .roadmap-badge.live { background: rgba(212, 255, 58, 0.14); color: var(--lime); }
      .roadmap-badge.partial { background: rgba(255, 255, 255, 0.06); color: var(--text); }
      .roadmap-badge.next { background: rgba(255, 94, 172, 0.14); color: var(--magenta); }
      .roadmap-badge.planned { background: rgba(255, 107, 107, 0.14); color: var(--red); }

      .roadmap-model {
        margin-top: 10px;
        color: var(--lime);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.84rem;
      }

      .roadmap-why {
        margin-top: 12px;
        display: grid;
        gap: 4px;
      }

      .roadmap-why strong,
      .roadmap-detail-grid h4 {
        color: var(--muted);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }

      .roadmap-why span {
        color: #c6ccbf;
      }

      .roadmap-detail-grid {
        margin-top: 14px;
        display: grid;
        gap: 14px;
      }

      .roadmap-artifacts {
        display: grid;
        gap: 6px;
        margin-top: 8px;
      }

      .roadmap-artifacts code {
        padding: 8px 10px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--line-soft);
        color: var(--text);
      }

      .roadmap-pitfall {
        margin-top: 14px;
        color: var(--muted);
        font-size: 0.84rem;
      }

      .level1-bucket-grid,
      .level1-metric-grid {
        display: grid;
        gap: 12px;
      }

      .level1-bucket-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        margin-top: 14px;
      }

      .level1-metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        margin-top: 14px;
      }

      .level1-item,
      .level1-bucket-card,
      .level1-metric-card {
        padding: 16px;
        border: 1px solid var(--line-soft);
        border-radius: 16px;
        background: rgba(10, 12, 11, 0.62);
      }

      .level1-list,
      .level1-notes {
        display: grid;
        gap: 10px;
        margin-top: 14px;
      }

      .level1-item p,
      .level1-notes p,
      .level1-bucket-card p {
        color: #c8cec2;
        margin: 6px 0 0;
      }

      .level1-reason {
        margin-top: 8px;
        color: var(--muted);
        font-size: 0.84rem;
      }

      .level1-metric-card span {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.72rem;
      }

      .level1-metric-card strong {
        display: block;
        margin-top: 8px;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 1.16rem;
      }

      .level5-split,
      .level5-run-grid,
      .level5-list,
      .level5-notes {
        display: grid;
        gap: 12px;
      }

      .level5-split {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        margin-top: 14px;
      }

      .level5-list,
      .level5-notes {
        margin-top: 14px;
      }

      .level5-item {
        padding: 16px;
        border: 1px solid var(--line-soft);
        border-radius: 16px;
        background: rgba(12, 15, 14, 0.72);
      }

      .level5-item p,
      .level5-notes p {
        margin-top: 6px;
        color: #c6ccbf;
      }

      .level5-split h4 {
        margin: 0 0 10px;
        color: var(--muted);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }

      .level6-policy-grid,
      .level6-list,
      .level6-notes,
      .level6-rubric-grid,
      .level6-scale-grid {
        display: grid;
        gap: 12px;
      }

      .level6-list,
      .level6-notes,
      .level6-rubric-grid,
      .level6-scale-grid {
        margin-top: 14px;
      }

      .level6-item,
      .level6-scale-card {
        padding: 16px;
        border: 1px solid var(--line-soft);
        border-radius: 16px;
        background: rgba(12, 15, 14, 0.72);
      }

      .level6-item p,
      .level6-notes p,
      .level6-scale-card p {
        margin-top: 6px;
        color: #c6ccbf;
      }

      .level6-reason {
        margin-top: 8px;
        color: var(--muted);
        font-size: 0.84rem;
      }

      .level6-scale-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .level6-rubric-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .level6-rubric-panel,
      .level6-scaleup-panel {
        margin-top: 16px;
      }

      .level6-gate-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 14px;
      }

      .level6-gate-card {
        padding: 14px;
        border: 1px solid var(--line-soft);
        border-radius: 14px;
        background: rgba(12, 15, 14, 0.72);
      }

      .level6-gate-card.pass { border-color: rgba(212, 255, 58, 0.22); }
      .level6-gate-card.hold { border-color: rgba(255, 94, 172, 0.22); }

      .block {
        position: relative;
        margin-top: 56px;
        padding: 30px 30px 32px;
        border: 1px solid var(--line-soft);
        border-radius: 28px;
        background: linear-gradient(180deg, rgba(15, 18, 17, 0.82), rgba(9, 11, 10, 0.92));
      }

      .block-head {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 22px;
        flex-wrap: wrap;
      }

      .block-head h2 {
        margin-top: 8px;
        font-size: clamp(1.8rem, 3.2vw, 2.6rem);
        letter-spacing: -0.03em;
        line-height: 1.05;
      }

      .block-head p {
        margin-top: 10px;
        max-width: 78ch;
        color: #b8bfb3;
      }

      .big-arrow { color: var(--lime); font-weight: 800; }

      .timeline {
        margin: 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 6px;
      }

      .timeline-step {
        display: grid;
        grid-template-columns: 60px 1fr;
        gap: 18px;
        padding: 10px 0;
        border-bottom: 1px dashed var(--line-soft);
      }

      .timeline-step:last-child { border-bottom: 0; }

      .timeline-rail {
        display: flex;
        justify-content: center;
      }

      .timeline-dot {
        display: grid;
        place-items: center;
        width: 44px;
        height: 44px;
        border-radius: 999px;
        background: rgba(212, 255, 58, 0.08);
        border: 1px solid rgba(212, 255, 58, 0.35);
        color: var(--lime);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-weight: 700;
      }

      .timeline-top {
        display: flex;
        align-items: baseline;
        gap: 14px;
        flex-wrap: wrap;
      }

      .timeline-top h3 {
        font-size: 1.24rem;
      }

      .timeline-cmd {
        padding: 5px 10px;
        border-radius: 10px;
        background: rgba(212, 255, 58, 0.08);
        border: 1px solid rgba(212, 255, 58, 0.22);
        color: var(--lime);
        font-size: 0.92rem;
      }

      .timeline-body p {
        margin-top: 8px;
        color: #bcc2b6;
      }

      .artifact-hint {
        margin-top: 8px;
        color: var(--muted);
        font-size: 0.84rem;
      }
      .artifact-hint code {
        color: var(--text);
      }

      .grid { display: grid; gap: 18px; }
      .grid.two-col { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .train-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .compare-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

      .card {
        padding: 22px;
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        background: rgba(8, 10, 9, 0.78);
      }

      .card-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: baseline;
        margin-bottom: 14px;
      }

      .card-head h3 { font-size: 1.14rem; }

      .readiness-grid { margin-top: 22px; }

      .check-list { display: grid; gap: 10px; }

      .check-row {
        display: grid;
        grid-template-columns: 24px 1fr auto;
        gap: 12px;
        align-items: start;
        padding: 12px 14px;
        border: 1px solid var(--line-soft);
        border-radius: 14px;
        background: rgba(14, 17, 16, 0.7);
      }

      .check-row p {
        margin-top: 4px;
        color: var(--muted);
        font-size: 0.88rem;
      }

      .check-row code {
        display: inline-block;
        margin-top: 6px;
        padding: 4px 8px;
        border-radius: 8px;
        background: rgba(212, 255, 58, 0.08);
        border: 1px solid rgba(212, 255, 58, 0.2);
        color: var(--lime);
        font-size: 0.82rem;
      }

      .check-dot {
        width: 12px; height: 12px; margin-top: 6px;
        border-radius: 999px;
        background: var(--muted);
      }
      .check-row.ready .check-dot { background: var(--lime); box-shadow: 0 0 10px rgba(212, 255, 58, 0.45); }
      .check-row.missing .check-dot { background: var(--red); }

      .check-label { font-weight: 600; }

      .status-tag {
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        align-self: start;
      }
      .status-tag.ready { background: rgba(212, 255, 58, 0.16); color: var(--lime); }
      .status-tag.missing { background: rgba(255, 107, 107, 0.16); color: var(--red); }

      .next-list { display: grid; gap: 10px; margin-bottom: 14px; }

      .next-card {
        padding: 12px 14px;
        border: 1px solid var(--line-soft);
        border-radius: 14px;
        background: rgba(14, 17, 16, 0.7);
      }

      .next-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: baseline;
      }

      .next-top code {
        padding: 4px 8px;
        border-radius: 8px;
        background: rgba(212, 255, 58, 0.1);
        border: 1px solid rgba(212, 255, 58, 0.24);
        color: var(--lime);
        font-size: 0.82rem;
      }

      .next-card p { margin-top: 4px; font-size: 0.9rem; }

      .prompt-panel {
        padding: 14px;
        border: 1px dashed var(--line-soft);
        border-radius: 14px;
        background: rgba(10, 12, 11, 0.5);
      }

      .prompt-panel-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 10px;
      }

      .prompt-accordion { border-top: 1px solid var(--line-soft); padding: 10px 0; }
      .prompt-accordion:first-of-type { border-top: 0; }
      .prompt-accordion summary {
        display: flex;
        gap: 10px;
        align-items: center;
        cursor: pointer;
        font-weight: 600;
      }
      .prompt-accordion pre {
        margin-top: 10px;
      }

      .agent-tag {
        display: inline-flex;
        padding: 3px 10px;
        border-radius: 999px;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: lowercase;
      }
      .agent-tag.codex { background: rgba(212, 255, 58, 0.14); color: var(--lime); border: 1px solid rgba(212, 255, 58, 0.3); }
      .agent-tag.claude { background: rgba(255, 94, 172, 0.14); color: var(--magenta); border: 1px solid rgba(255, 94, 172, 0.3); }

      .data-hero {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-bottom: 22px;
      }

      .anatomy-card {
        position: relative;
        padding: 20px;
        border: 1px solid var(--line-soft);
        border-radius: 20px;
        background:
          linear-gradient(180deg, rgba(14, 17, 16, 0.9), rgba(8, 10, 9, 0.9)),
          radial-gradient(420px 280px at 100% 0%, rgba(212, 255, 58, 0.08), transparent 55%);
      }

      .anatomy-head {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: center;
        margin-bottom: 14px;
      }

      .anatomy-cat {
        color: var(--muted);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.76rem;
        letter-spacing: 0.06em;
      }

      .anatomy-row {
        margin-top: 10px;
      }

      .anatomy-label {
        display: block;
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 6px;
      }

      .user-utterance {
        padding: 12px 14px;
        border-radius: 14px;
        background: rgba(255, 94, 172, 0.08);
        border: 1px solid rgba(255, 94, 172, 0.24);
        color: #ffd6ea;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.92rem;
      }

      .anatomy-arrow {
        margin: 14px 0 10px;
        color: var(--lime);
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-size: 0.7rem;
        font-family: "Geist Mono", ui-monospace, monospace;
      }

      .anatomy-args {
        margin-top: 10px;
        padding: 12px;
        border-radius: 12px;
        background: rgba(212, 255, 58, 0.06);
        border: 1px solid rgba(212, 255, 58, 0.18);
        color: #e1ffa3;
        font-size: 0.82rem;
        max-height: 160px;
        overflow: auto;
      }

      .bars { display: grid; gap: 10px; margin-top: 8px; }
      .bar-row + .bar-row { margin-top: 4px; }
      .bar-head {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        font-size: 0.86rem;
        margin-bottom: 4px;
        color: #c8ceb9;
      }
      .bar-head strong { color: var(--text); }

      .bar-track {
        height: 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        overflow: hidden;
      }

      .bar-fill { height: 100%; border-radius: inherit; }
      .bar-fill.lime { background: linear-gradient(90deg, #d4ff3a, #8ec91f); }
      .bar-fill.magenta { background: linear-gradient(90deg, #ff5eac, #b73f7e); }

      .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }

      .chip, .pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-family: "Geist Mono", ui-monospace, monospace;
        letter-spacing: 0.02em;
      }

      .chip {
        background: rgba(212, 255, 58, 0.06);
        border: 1px solid rgba(212, 255, 58, 0.2);
        color: #e7ffbb;
      }

      .chip.ghost {
        background: rgba(255, 255, 255, 0.02);
        border-color: var(--line-soft);
        color: #c6ccbc;
      }

      .pill {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--line-soft);
        color: #d5dbcb;
      }

      .pill.alt {
        background: rgba(255, 94, 172, 0.1);
        border-color: rgba(255, 94, 172, 0.3);
        color: #ffd6ea;
      }

      .curve-card { padding: 22px; }
      .curve-card.lime { background: linear-gradient(180deg, rgba(30, 36, 20, 0.7), rgba(10, 12, 9, 0.92)); border-color: rgba(212, 255, 58, 0.2); }
      .curve-card.magenta { background: linear-gradient(180deg, rgba(40, 18, 32, 0.7), rgba(10, 8, 10, 0.92)); border-color: rgba(255, 94, 172, 0.22); }

      .curve-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 10px;
      }

      .curve-head h3 {
        margin-top: 6px;
        font-size: 1.2rem;
      }

      .curve-delta {
        text-align: right;
      }

      .delta-top { color: var(--muted); font-size: 0.76rem; letter-spacing: 0.12em; text-transform: uppercase; }
      .delta-value {
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
      }
      .curve-card.lime .delta-value { color: var(--lime); }
      .curve-card.magenta .delta-value { color: var(--magenta); }
      .delta-sub { color: var(--muted); font-size: 0.82rem; margin-top: 2px; }

      .loss-svg { width: 100%; height: 180px; display: block; margin: 8px 0 14px; }
      .loss-svg.lime { color: var(--lime); }
      .loss-svg.magenta { color: var(--magenta); }
      .loss-svg .grid-line { stroke: rgba(255, 255, 255, 0.05); stroke-width: 1; }
      .loss-svg .curve-label {
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 9px;
        fill: currentColor;
        opacity: 0.8;
      }

      .curve-empty { padding: 24px; text-align: center; color: var(--muted); font-style: italic; }

      .curve-footer { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }

      .artifact-strip {
        margin-top: 6px;
        border-top: 1px dashed var(--line-soft);
        padding-top: 12px;
        display: grid;
        gap: 6px;
      }

      .artifact-row {
        display: grid;
        grid-template-columns: minmax(120px, auto) minmax(80px, auto) 1fr;
        gap: 10px;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.8rem;
        color: #c3c9b7;
      }

      .artifact-name { color: var(--text); }
      .artifact-size { color: var(--lime); }
      .artifact-path { color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

      .compare-side { padding: 24px; border-radius: 22px; }
      .compare-side.lime { background: linear-gradient(180deg, rgba(30, 36, 20, 0.8), rgba(9, 11, 9, 0.92)); border-color: rgba(212, 255, 58, 0.24); }
      .compare-side.magenta { background: linear-gradient(180deg, rgba(40, 18, 32, 0.8), rgba(10, 8, 10, 0.92)); border-color: rgba(255, 94, 172, 0.26); }
      .compare-side h3 { margin-top: 10px; font-size: 1.4rem; }
      .compare-tag {
        display: inline-flex;
        padding: 5px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--line-soft);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.78rem;
        color: var(--muted);
      }

      .stat-grid {
        margin: 20px 0 0;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }

      .stat-grid dt { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em; }
      .stat-grid dd {
        margin: 4px 0 0;
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 1.3rem;
        font-weight: 700;
      }

      .delta-matrix { margin-top: 18px; }
      .delta-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-family: "Geist Mono", ui-monospace, monospace; font-size: 0.9rem; }
      .delta-table th { text-align: left; color: var(--muted); padding: 10px 8px; border-bottom: 1px solid var(--line-soft); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.72rem; }
      .delta-table td { padding: 12px 8px; border-bottom: 1px solid var(--line-soft); }
      .delta-table tbody tr:last-child td { border-bottom: 0; }

      .delta-chip {
        display: inline-flex;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
      }
      .delta-chip.up { background: rgba(212, 255, 58, 0.14); color: var(--lime); border: 1px solid rgba(212, 255, 58, 0.28); }
      .delta-chip.down { background: rgba(255, 107, 107, 0.14); color: var(--red); border: 1px solid rgba(255, 107, 107, 0.28); }
      .delta-chip.neutral { background: rgba(255, 255, 255, 0.04); color: var(--muted); border: 1px solid var(--line-soft); }

      .delta-note { margin-top: 14px; color: var(--muted); font-size: 0.9rem; line-height: 1.6; }

      .probe-stack { display: grid; gap: 14px; }

      .probe-card { padding: 22px; }
      .probe-top {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: flex-start;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      .probe-top h3 {
        margin-top: 6px;
        font-size: 1.14rem;
      }

      .probe-columns {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 12px;
      }

      .probe-col {
        padding: 14px;
        border-radius: 16px;
        border: 1px solid var(--line-soft);
        background: rgba(14, 17, 16, 0.7);
      }

      .probe-col.lime.hit { border-color: rgba(212, 255, 58, 0.35); background: linear-gradient(180deg, rgba(20, 26, 12, 0.9), rgba(9, 11, 9, 0.92)); }
      .probe-col.magenta.hit { border-color: rgba(255, 94, 172, 0.35); background: linear-gradient(180deg, rgba(32, 14, 26, 0.9), rgba(9, 9, 9, 0.92)); }
      .probe-col.miss { border-color: rgba(255, 107, 107, 0.3); }

      .probe-col-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }

      .mini-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        color: var(--muted);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-size: 0.76rem;
        margin-bottom: 10px;
      }

      .mini-strip span { padding: 3px 8px; border-radius: 8px; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--line-soft); }

      pre {
        margin: 0;
        padding: 12px;
        border-radius: 12px;
        background: rgba(6, 8, 7, 0.75);
        color: #e3e9d4;
        border: 1px solid var(--line-soft);
        white-space: pre-wrap;
        word-break: break-word;
        max-height: 260px;
        overflow: auto;
        font-size: 0.84rem;
      }

      .takeaway-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }

      .takeaway {
        padding: 24px;
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 18, 17, 0.86), rgba(9, 11, 10, 0.92));
        position: relative;
      }

      .takeaway-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 36px;
        border-radius: 12px;
        background: rgba(212, 255, 58, 0.12);
        border: 1px solid rgba(212, 255, 58, 0.28);
        color: var(--lime);
        font-family: "Geist Mono", ui-monospace, monospace;
        font-weight: 700;
        letter-spacing: 0.1em;
      }

      .takeaway h3 { margin-top: 12px; font-size: 1.24rem; }
      .takeaway p { margin-top: 10px; color: #bdc4b5; }

      .site-footer {
        position: relative;
        z-index: 1;
        margin: 56px auto 0;
        padding: 30px 30px 40px;
        width: min(1260px, calc(100vw - 28px));
        border-top: 1px solid var(--line-soft);
        color: var(--muted);
      }

      .footer-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
      }

      .workflow-map {
        margin: 12px 0 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 10px;
      }

      .workflow-map li {
        display: grid;
        grid-template-columns: minmax(140px, auto) minmax(180px, auto) 1fr;
        gap: 14px;
        padding: 10px 0;
        border-bottom: 1px dashed var(--line-soft);
        font-size: 0.88rem;
      }

      .workflow-map li:last-child { border-bottom: 0; }
      .workflow-map strong { color: var(--text); font-family: "Geist Mono", ui-monospace, monospace; }
      .workflow-map code { color: var(--lime); font-family: "Geist Mono", ui-monospace, monospace; }
      .workflow-map span { color: var(--muted); }

      .footer-cmd {
        margin-top: 10px;
        background: rgba(212, 255, 58, 0.04);
        border-color: rgba(212, 255, 58, 0.16);
        color: #e7ffbb;
      }

      .footer-note { margin-top: 10px; font-size: 0.84rem; }

      @media (max-width: 1080px) {
        .hero-cmd-row, .hero-stats, .tenets, .grid.two-col, .train-grid, .compare-grid, .data-hero, .takeaway-grid, .footer-grid, .roadmap-grid, .level1-bucket-grid, .level1-metric-grid, .level5-split, .level6-rubric-grid, .level6-scale-grid, .level6-gate-grid {
          grid-template-columns: 1fr;
        }
        .hero-title { font-size: clamp(2.2rem, 9vw, 4rem); }
      }

      @media (max-width: 680px) {
        main { width: calc(100vw - 20px); padding: 22px 0 48px; }
        .hero, .block { padding: 22px; border-radius: 20px; }
        .stat-grid, .hero-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .hero-cmd-row { grid-template-columns: 1fr; }
        .timeline-step { grid-template-columns: 48px 1fr; gap: 12px; }
        .probe-columns { grid-template-columns: 1fr; }
        .check-row { grid-template-columns: 20px 1fr; }
        .check-row .status-tag { grid-column: 1 / -1; justify-self: start; margin-top: 6px; }
      }
    </style>
  </head>
  <body>
    <main>
      ${renderHero(data)}
      ${renderTenets(data)}
      ${renderRoadmapBlock(data)}
      ${renderLevel1Block(data)}
      ${renderTimeline(data)}
      ${renderDataBlock(data)}
      ${renderTrainingBlock(data)}
      ${renderCompareBlock(data)}
      ${renderLevel5Block(data)}
      ${renderBehaviorEvalBlock(data)}
      ${renderDataScaleCompareBlock(data)}
      ${renderLevel6Block(data)}
      ${renderProbeBlock(data)}
      ${renderTakeaways(data)}
    </main>
    ${renderFooter(data)}
  </body>
</html>`;
}

async function main() {
  const labDataPath = path.join(webRoot, "public", "lab-data.json");
  const distDir = path.join(webRoot, "dist");
  const distHtmlPath = path.join(distDir, "index.html");
  const raw = await fs.readFile(labDataPath, "utf8");
  const data = JSON.parse(raw);
  await fs.mkdir(distDir, { recursive: true });
  await fs.writeFile(distHtmlPath, renderHtml(data), "utf8");
  console.log("Wrote standalone dist/index.html");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
