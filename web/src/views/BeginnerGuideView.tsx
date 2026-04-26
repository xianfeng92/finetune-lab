import { memo, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { LabData } from "../data-layer";
import { SectionTitle } from "../components/ui";

function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w一-龥\s-]/g, "")
    .replace(/\s+/g, "-");
}

function extractToc(md: string): Array<{ depth: 2 | 3; text: string; slug: string }> {
  const lines = md.split("\n");
  const out: Array<{ depth: 2 | 3; text: string; slug: string }> = [];
  let inFence = false;
  for (const line of lines) {
    if (/^```/.test(line)) { inFence = !inFence; continue; }
    if (inFence) continue;
    const m = /^(#{2,3})\s+(.+?)\s*$/.exec(line);
    if (!m) continue;
    const depth = m[1].length === 2 ? 2 : 3;
    const text = m[2].replace(/`/g, "");
    out.push({ depth, text, slug: slugify(text) });
  }
  return out;
}

function BeginnerGuideViewImpl(props: { data: LabData }) {
  const md = props.data.beginner_guide_markdown;
  const toc = useMemo(() => (md ? extractToc(md) : []), [md]);
  return (
    <div className="view-grid beginner-grid">
      <section className="panel span-2">
        <SectionTitle
          title="新手向导读"
          subtitle={<>这份是写给"完全没接触过模型微调"的人的。来源 <code>docs/ai/beginner-guide.md</code>，每次 <code>make web-build</code> 都会更新一次。</>}
          audience="新手"
        />
        {md ? (
          <div className="beginner-layout">
            <article className="markdown-body">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h2: ({ children }) => {
                    const text = String(children);
                    return <h2 id={slugify(text)}>{children}</h2>;
                  },
                  h3: ({ children }) => {
                    const text = String(children);
                    return <h3 id={slugify(text)}>{children}</h3>;
                  },
                }}
              >{md}</ReactMarkdown>
            </article>
            {toc.length > 0 ? (
              <nav className="beginner-toc" aria-label="Table of contents">
                <div className="beginner-toc-label">目录</div>
                <ul>
                  {toc.map((item) => (
                    <li key={item.slug} className={`toc-d${item.depth}`}>
                      <a href={`#${item.slug}`}>{item.text}</a>
                    </li>
                  ))}
                </ul>
              </nav>
            ) : null}
          </div>
        ) : (
          <p className="mini-note">没找到 docs/ai/beginner-guide.md，请确认仓库里有这份文档。</p>
        )}
      </section>
    </div>
  );
}

export const BeginnerGuideView = memo(BeginnerGuideViewImpl);
