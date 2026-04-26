import { memo, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { DatasetCard, LabData } from "../data-layer";
import { Term } from "../components/Term";
import { ChartBars, CollapsiblePanel, SectionTitle } from "../components/ui";

function DatasetCardEntry(props: { card: DatasetCard }) {
  const fm = props.card.frontmatter;
  const r = props.card.redaction;
  const rfm = r?.frontmatter;
  const totalSamples = fm.total_samples ?? "—";
  const sensitivity = fm.sensitivity ?? "—";
  const piiCount = fm.pii_redacted_count ?? 0;
  const matches = rfm?.match_counts ?? {};
  const matchSummary = Object.entries(matches).map(([k, v]) => `${k}=${v}`).join(" · ");
  return (
    <details className="dataset-card-entry">
      <summary>
        <div className="dataset-card-summary">
          <div>
            <strong>{fm.name ?? props.card.dir_relative}</strong>
            <code className="dataset-card-path">{props.card.dir_relative}</code>
          </div>
          <div className="dataset-card-pills">
            <span className={`dataset-card-pill sens-${sensitivity}`}>sensitivity: {sensitivity}</span>
            <span className="dataset-card-pill">{totalSamples} samples</span>
            <span className={`dataset-card-pill ${piiCount > 0 ? "pii-hit" : "pii-clean"}`}>
              redacted: {piiCount}/{rfm?.records_scanned ?? totalSamples}
            </span>
          </div>
        </div>
      </summary>
      <div className="dataset-card-body">
        <div className="dataset-card-meta">
          <span><strong>generator</strong>: {fm.generator ?? "—"}</span>
          <span><strong>license</strong>: {fm.license ?? "—"}</span>
          <span><strong>generated_at</strong>: {fm.generated_at ?? "—"}</span>
          {fm.splits ? (
            <span><strong>splits</strong>: {Object.entries(fm.splits).map(([k, v]) => `${k}=${v}`).join(" · ")}</span>
          ) : null}
        </div>
        <article className="markdown-body dataset-card-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{props.card.body}</ReactMarkdown>
        </article>
        {r ? (
          <details className="dataset-card-redaction">
            <summary>redaction-report.md{matchSummary ? ` · ${matchSummary}` : ""}</summary>
            <article className="markdown-body dataset-card-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{r.body}</ReactMarkdown>
            </article>
          </details>
        ) : null}
      </div>
    </details>
  );
}

function DatasetCardsPanel(props: { cards: DatasetCard[] }) {
  if (!props.cards || props.cards.length === 0) return null;
  return (
    <CollapsiblePanel
      title="Dataset cards"
      subtitle={<>每个数据集都有 <code>dataset-card.md</code> + <code>redaction-report.md</code> 治理产物。<code>make dataset-governance</code> 可重新刷新。<Term term="held-out"> </Term></>}
      audience="工程"
      defaultOpen={false}
    >
      <div className="dataset-card-list">
        {props.cards.map((card) => (
          <DatasetCardEntry key={card.dir_relative} card={card} />
        ))}
      </div>
    </CollapsiblePanel>
  );
}

function DataViewImpl(props: { data: LabData }) {
  const samples = props.data.dataset.samples;
  const [selectedId, setSelectedId] = useState(samples[0]?.id ?? "");
  const selected = samples.find((sample) => sample.id === selectedId) ?? samples[0];
  const categoryItems = useMemo(
    () => props.data.dataset.summary.category_counts.map(({ category, count }) => ({ label: category, value: count })),
    [props.data.dataset.summary.category_counts],
  );
  const domainItems = useMemo(
    () => props.data.dataset.summary.domain_counts.map(({ domain, count }) => ({ label: domain, value: count })),
    [props.data.dataset.summary.domain_counts],
  );
  return (
    <div className="view-grid">
      <section className="panel">
        <SectionTitle title="Category coverage" subtitle="demo 数据集的类别分布。" audience="工程" />
        <ChartBars items={categoryItems} tone="lime" total={props.data.dataset.summary.total_samples} />
      </section>
      <section className="panel">
        <SectionTitle title="Train / held-out split" subtitle={<>训练和 <Term term="probe">probe</Term> 现在不再复用同一份样本：<Term term="held-out">held-out</Term> 是专门留出来评估的子集。</>} audience="工程" />
        <div className="track-pack-notes">
          <article className="track-pack-note">
            <strong>full dataset</strong>
            <p>{props.data.source.dataset}</p>
          </article>
          <article className="track-pack-note">
            <strong>train</strong>
            <p>{props.data.source.train_dataset}</p>
          </article>
          <article className="track-pack-note">
            <strong>held-out probe</strong>
            <p>{props.data.source.held_out_dataset}</p>
          </article>
        </div>
      </section>
      <section className="panel">
        <SectionTitle title="Domain footprint" subtitle="按 domain 统计样本覆盖。一条样本可能涉及多个 domain，所以加起来可能超过样本总数。" audience="工程" />
        <ChartBars items={domainItems} tone="magenta" />
      </section>
      <section className="panel span-2">
        <SectionTitle title="Sample anatomy" subtitle="system prompt、messages 和 sft_text 同屏查看。sft_text 就是把 messages 拼成模型实际看到的字符串。" audience="工程" />
        <div className="sample-layout">
          <aside className="sample-list compact">
            {samples.map((sample) => (
              <button key={sample.id} type="button" className={`sample-item ${sample.id === selected?.id ? "active" : ""}`} onClick={() => setSelectedId(sample.id)}>
                <span>{sample.id}</span>
                <strong>{sample.category}</strong>
              </button>
            ))}
          </aside>
          {selected ? (
            <div className="sample-detail">
              <div className="pill-row">
                {selected.loaded_tool_names.map((name) => (
                  <span key={name} className="pill">{name}</span>
                ))}
              </div>
              <div className="detail-grid">
                <article className="detail-card"><h3>system_prompt</h3><pre>{selected.system_prompt}</pre></article>
                <article className="detail-card"><h3>messages</h3><pre>{JSON.stringify(selected.messages, null, 2)}</pre></article>
                <article className="detail-card span-2"><h3>sft_text</h3><pre>{selected.sft_text}</pre></article>
              </div>
            </div>
          ) : null}
        </div>
      </section>
      <DatasetCardsPanel cards={props.data.dataset_cards} />
    </div>
  );
}

export const DataView = memo(DataViewImpl);
