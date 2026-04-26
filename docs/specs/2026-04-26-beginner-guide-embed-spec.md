---
title: Beginner Guide Embed Spec
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26 (implemented)
implements:
  - docs/changes/2026-04-26-beginner-guide-embed-impl-notes.md
reviews:
  - docs/reviews/2026-04-26-web-beginner-ux-questions-review.md
---

## 目标

把 [docs/ai/beginner-guide.md](../ai/beginner-guide.md) 真正渲染进 web 前端，作为"我从来没微调过"的访客的第一站。当前 StarterGuide 只把这种用户引到 Agent Handoff（让 agent 替你跑），少了一条"我自己想理解一遍"的路径。

## 不在范围

- **不重写 beginner-guide.md 内容**。markdown 文件保持权威，UI 只读它。
- **不做内容编辑器 / 评论 / 高亮**。
- **不做语法高亮**（代码块单色等宽即可，无需 prism / shiki）。
- **不做 inline 跨链接**（"`outputs/<run>/...`" 现在不点击；guide 里提到的术语也暂不自动 wrap `<Term>`）。这些放进 future enhancement。
- **不引入路由库**。沿用现有的 `view: View` 切 tab 模式，加一个 `"beginner-guide"` 即可。
- **不做 print / export**。

## 数据流

```
docs/ai/beginner-guide.md
  ↓ build 时由 build-lab-data.mjs 读成字符串
labData.beginner_guide_markdown: string
  ↓
<BeginnerGuideView> 用 react-markdown 渲染
```

走 `lab-data.generated.ts` 嵌入路径，保证 `dist/index.html` standalone 模式仍能离线打开。

## UI 结构

### 1. 新 nav item

[App.tsx](../../web/src/App.tsx) 的 sidebar nav 加一个 `Beginner Guide`，**插在 Overview 上面**，让它成为视觉上的第一站：

```
[ Beginner Guide ]   ← 新增
  Overview
  Agent Handoff
  Data Pipeline
  Training Runs
  Probe Compare
```

`type View` 加 `"beginner-guide"` 字面量。

### 2. StarterGuide 调整

当前三张卡的第一张：「完全没微调过 → 先看 Agent Handoff」。改成两阶段引导：

| 卡 | 现在 | 改后 |
|---|---|---|
| 1 | 完全没微调过 → Agent Handoff | **完全没微调过 → 先读 Beginner Guide**（点击切到新 tab） |
| 2 | 想看真训练 → Training Runs | （不变） |
| 3 | 想知道哪个 run 最好 → Probe Compare | （不变） |

Agent Handoff 仍在 nav 里，给"想让 agent 接手"那条路径用。新手通路是：先 Beginner Guide 看完知识背景 → 再去 Agent Handoff 看具体怎么交接。

### 3. BeginnerGuideView 布局

单 panel `span-2`，内部就是渲染好的 markdown。结构：

```
┌─ panel ─────────────────────────────────────┐
│ SectionTitle: 新手向导读 (audience: 新手)    │
│ subtitle: 这份是写给"完全没接触过模型微调"   │
│           的人的，markdown 来源 docs/ai/...  │
│                                              │
│ <article class="markdown-body">              │
│   ## 1. 用一句话理解微调                     │
│   ...                                        │
│   ## 7. 一些常见误区                         │
│ </article>                                   │
└──────────────────────────────────────────────┘
```

不做 sticky TOC（250 行 markdown 浏览器原生滚动够用，Cmd-F 可搜）。如果未来扩到 1000+ 行，再加 TOC。

### 4. CSS scope: `.markdown-body`

需要单独给以下 markdown 元素调样式（继承现有暗色主题）：

| 选择器 | 关键样式 |
|---|---|
| `.markdown-body h1, h2, h3, h4` | 字号阶梯、与现有 `.section-title h2` 协调 |
| `.markdown-body p` | 行高 1.65、color #d8dcd0 |
| `.markdown-body code` | 单色等宽，行内 inline-code 用浅底色 |
| `.markdown-body pre` | 暗底块、`overflow-x: auto`、不限高度 |
| `.markdown-body table` | 边框 `var(--line)`、表头底色、单元格 8-12px padding |
| `.markdown-body blockquote` | 左边框 `var(--lime)`、淡底色，配合"重要心智"那种 callout |
| `.markdown-body a` | lime 色 + hover 下划线 |
| `.markdown-body ul/ol` | 缩进、项目符号样式 |
| `.markdown-body strong` | 粗体保持白色不变 |

### 5. 库选择

`react-markdown` + `remark-gfm`：
- 体积：合计 gzip ~25KB；可接受。
- 必须支持 GFM（guide 里有 `|` 表格、删除线、任务列表场景）。
- API 简单：`<ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>`。
- 不用 `dangerouslySetInnerHTML`，免 XSS 风险（虽然 markdown 是仓库自己写的，安全网仍要保留）。

不选 `marked` / 自写 mini renderer 的理由：
- `marked` 默认输出 HTML 字符串，要 `dangerouslySetInnerHTML`，多一层 trust 边界。
- 自写 mini renderer 浪费时间，guide 内容会演化，标准库更稳。

## 实现拆步

| # | 步骤 | 验证 |
|---|---|---|
| 1 | `cd web && npm i react-markdown remark-gfm` | `package.json` 出现新 deps；`package-lock.json` 更新 |
| 2 | `build-lab-data.mjs` 读取 `docs/ai/beginner-guide.md` 成 utf8 字符串，挂到 payload `beginner_guide_markdown`；如果文件不存在，回退到 `null` 不报错 | `lab-data.json` 多一字段，长度 ≈ 250 行 |
| 3 | `LabData` 接口加 `beginner_guide_markdown: string \| null` | tsc 通过 |
| 4 | `App.tsx`: 加 `View = ... \| "beginner-guide"`；nav 数组顶部加一项；render 分支加 `view === "beginner-guide" ? <BeginnerGuideView .../> : null` | nav 出现新 item，点击切换 |
| 5 | 新组件 `<BeginnerGuideView>`：渲染 SectionTitle + `<article className="markdown-body">` + `<ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>` | 看到完整渲染的 markdown |
| 6 | `StarterGuide` 第一张卡 onClick 改为 `props.onPick("beginner-guide")`；标题文字改为 `先读 Beginner Guide`；正文改为"系统讲清楚什么是 SFT/LoRA/probe，为什么 loss ≠ 学到了，新手第一站。" | 点击跳转到新 tab |
| 7 | `styles.css` 加 `.markdown-body` 一组规则（见上）。注意 `pre` 和 `code` 不要继承 `<details>` 的 cursor pointer | 表格、代码块、blockquote 渲染好看，不破暗色主题 |
| 8 | `make web-build` 跑通；preview 实测 |  截图确认 |

## 成功标准

- 完全没微调过的访客打开 web，第一眼有 nav 顶部 `Beginner Guide`，且 Overview 上的 StarterGuide 第一张卡也指向它。
- 点进去看到 250 行 markdown 完整渲染：标题层级、代码块、表格、blockquote、删除线全都正确。
- markdown 内容来自 `docs/ai/beginner-guide.md` 实时（每次 `make web-build` 更新），不是硬编码副本。
- standalone `dist/index.html` 离线能看到 guide 内容（和现有数据嵌入模式一致）。

## 风险

- **markdown bundle 体积**：当前主 chunk 已经 1.30MB / 143KB gzip，加 react-markdown 会再涨 ~25KB gzip。教学站不在意首屏，可接受。如果 vite 告警太烦人，再考虑 dynamic import：`const BeginnerGuideView = lazy(...)`。
- **markdown 跟主题样式打架**：现有 `.detail-card pre` 等规则可能影响 markdown 渲染。`.markdown-body` 必须用更具体的选择器或 `:where()` 隔离，避免 CSS 互相覆盖。
- **正文里 image 链接**：guide 暂时没有图片，但未来可能加。预留 `.markdown-body img { max-width: 100%; }` 即可，无需做更多。
- **AI Space CLAUDE.md 提到 status frontmatter**：guide 是 `docs/ai/`，不属于 `docs/specs/`，不强制要 frontmatter。但渲染时如果 guide 未来加了 frontmatter（YAML 头），react-markdown 会把它当文本输出。如果需要剥离，加 `remark-frontmatter` + 自定义 transformer。**当前 guide 没 frontmatter，先不处理**，写在 future enhancement。

## Future enhancement（不在本次范围）

- guide 里"`outputs/<run>/...`"路径自动渲染成跳转链接（点击跳到 Training Runs tab 并 highlight 对应 run）。
- guide 里 SFT / LoRA / probe 等术语自动 wrap 成 `<Term>` 组件。
- 给 markdown 加 sticky TOC（基于 h2 自动抽取）。
- 给 code block 加复制按钮。

## 参考

- 当前 guide 内容：[docs/ai/beginner-guide.md](../ai/beginner-guide.md)
- 来源 review：[2026-04-26-web-beginner-ux-questions-review.md](../reviews/2026-04-26-web-beginner-ux-questions-review.md) §A4 / §I 第 4 条
- 现有 nav 模式：[web/src/App.tsx](../../web/src/App.tsx) 的 `View` 类型 + sidebar 数组
- 现有数据嵌入模式：[web/scripts/build-lab-data.mjs](../../web/scripts/build-lab-data.mjs) → `web/src/generated/lab-data.generated.ts`
