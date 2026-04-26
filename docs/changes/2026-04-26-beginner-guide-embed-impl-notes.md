---
title: Beginner Guide Embed Implementation Notes
status: implemented
owner: claude
created: 2026-04-26
updated: 2026-04-26
implements:
  - docs/specs/2026-04-26-beginner-guide-embed-spec.md
---

## 范围

按 [docs/specs/2026-04-26-beginner-guide-embed-spec.md](../specs/2026-04-26-beginner-guide-embed-spec.md) 实现，把 [docs/ai/beginner-guide.md](../ai/beginner-guide.md) 渲染进 web 前端，做成新手第一站 tab。

## 改动

| 区块 | 内容 | 文件 |
| --- | --- | --- |
| 依赖 | `npm i react-markdown remark-gfm`（97 个传递依赖，0 vulnerabilities） | [web/package.json](../../web/package.json) |
| 数据装配 | `build-lab-data.mjs` 读取 `docs/ai/beginner-guide.md` 成 utf8 字符串，挂到 payload `beginner_guide_markdown`；文件不存在时回退 null。 | [web/scripts/build-lab-data.mjs:236-241](../../web/scripts/build-lab-data.mjs) |
| 类型 | `LabData.beginner_guide_markdown: string \| null` | [web/src/data-layer.ts:701](../../web/src/data-layer.ts) |
| View 类型 | `View` 加 `"beginner-guide"` 字面量 | [web/src/App.tsx:7](../../web/src/App.tsx) |
| Nav | sidebar nav 顶部新增 `["beginner-guide", "Beginner Guide"]`（在 Overview 之上），让它视觉上是第一站 | [web/src/App.tsx:1654](../../web/src/App.tsx) |
| BeginnerGuideView | 新组件，渲染 SectionTitle + `<article className="markdown-body">` + `<ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>`；md 为 null 时给降级提示。 | [web/src/App.tsx:1034-1054](../../web/src/App.tsx) |
| StarterGuide | 第一张卡 onClick 改 `"onboarding"` → `"beginner-guide"`；标题改 "先读 Beginner Guide"，正文改"系统讲清楚什么是 SFT / LoRA / probe，为什么 loss ≠ 学到了。" | [web/src/App.tsx:63-67](../../web/src/App.tsx) |
| CSS | 新增 `.markdown-body` 主题：h1-h4 字号阶梯、p 行高 1.65、inline `code` 用 lime 浅色、`pre` 暗底块 + `overflow-x: auto`、`blockquote` 左 lime border + 淡底、`table` 边框 + 表头底色、`hr / img / del` 等基础规则。 | [web/src/styles.css:912-1015](../../web/src/styles.css) |

## 决策与偏离

- **没改路径解析方式**：spec 提到 build-lab-data.mjs 已经在 `web/scripts/` 跑，`repoRoot` 已可用，直接 `path.join(repoRoot, "docs", "ai", "beginner-guide.md")` 即可。
- **bundle 体积超出预估**：spec 写"+25KB gzip"，实测 +53KB（143KB → 196KB gzip）。原因是 react-markdown 6.x 带 micromark + 一系列子包。仍可接受（教学站，不在意首屏），未来若想减重可换 `marked` + `dompurify`，或用 dynamic import lazy 这一个 view。**当前不动**。
- **降级路径**：md 为 null 时显示 "没找到 docs/ai/beginner-guide.md，请确认仓库里有这份文档。" 文案，避免空白。

## 验证

- `make web-build` 通过。
- preview 实测：新 nav `Beginner Guide` 在最顶部；点击进入显示完整 markdown。统计：1 个 h1、7 个 h2、4 个 table、5 个代码块、2 个 blockquote、63 个 inline code。
- StarterGuide 第一卡跳转目标已切换为 `beginner-guide` view。
- 全 6 个 tab（多了 Beginner Guide）切换 0 个 React 错误。
- 视觉：tables 有边框 + lime header，inline code 是 lime 浅色，blockquote 左 lime 竖条 + 淡底色（如"重要心智：loss 下降 ≠ 学会了"那条很显眼）。

## 没做（spec 排除项保留）

- 语法高亮（pre code 单色等宽）。
- inline 跨链接（"`outputs/<run>/...`" 不点击）。
- 自动 `<Term>` wrap glossary 术语。
- sticky TOC。
- code block 复制按钮。
- markdown frontmatter 剥离（当前 guide 没 frontmatter，未来若加再处理）。

这些写在 spec 的 "Future enhancement" 段，需要时再起单独的小 spec。

## 参考

- spec：[docs/specs/2026-04-26-beginner-guide-embed-spec.md](../specs/2026-04-26-beginner-guide-embed-spec.md)
- review 来源：[docs/reviews/2026-04-26-web-beginner-ux-questions-review.md](../reviews/2026-04-26-web-beginner-ux-questions-review.md)
- 内容源：[docs/ai/beginner-guide.md](../ai/beginner-guide.md)
