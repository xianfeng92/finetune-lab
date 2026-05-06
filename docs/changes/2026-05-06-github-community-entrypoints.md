---
title: GitHub community entrypoints for launch feedback
status: implemented
owner: codex
created: 2026-05-06
---

# GitHub Community Entrypoints

## Why

The project is being optimized toward a first public growth milestone: make it easy for learners and open-source visitors to understand, try, star, and contribute to `finetune-lab`.

The repo already has a strong README, live demo, launch assets, and Makefile onboarding flow. The missing lightweight launch surface was GitHub-native feedback capture: issue templates and PR guidance that turn first-time readers into actionable feedback.

## What changed

- Added `CONTRIBUTING.md` with the project contribution shape, readiness commands, and SIM/REAL/runtime claim guardrails.
- Added `.github/PULL_REQUEST_TEMPLATE.md` with evidence, artifact, and scope checks.
- Added issue templates for:
  - bug reports
  - recipe requests
  - learning questions
- Added `.github/ISSUE_TEMPLATE/config.yml` with links to the live demo and workflow docs.
- Added `docs/launch/github-repo-launch-checklist.md` so GitHub About, topics, social preview, first release notes, and good-first-issue seeds are ready before public posting.
- Added `docs/launch/good-first-issues.md` with ready-to-paste issue bodies for launch contributors.
- Added `docs/recipes/` for the four launch recipes promised by README and the Web Recipe Gallery: `loss-is-lying`, `first-lora`, `tool-calling`, and `curriculum-vs-direct`.

## Growth rationale

These templates are deliberately centered on the project promise:

```text
data -> LoRA train -> held-out probe -> case diff -> runtime behavior check
```

For a project trying to reach its first 100 stars, the goal is not only to look polished. The repo should quickly answer:

- How do I try it?
- Where do I give feedback?
- What kind of contribution is welcome?
- What evidence do maintainers need?

## Guardrails

- Keep Makefile targets as the default command surface.
- Do not describe simulated smoke runs as real LoRA training.
- Do not overclaim same-LoRA runtime parity without matching runtime artifacts.
- Keep new recipes focused on one learning question, one command loop, and concrete artifacts.
- Keep README recipe links pointed at real recipe docs, not only Web tabs.

## Next manual launch actions

These require GitHub UI or authenticated GitHub operations after the local changes are merged:

1. Set the repo About description and website.
2. Add focused discovery topics.
3. Upload the social preview image.
4. Create the first release from the draft notes.
5. Open at least three good first issues from `docs/launch/good-first-issues.md`.
