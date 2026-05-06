---
title: Launch recipe docs
status: implemented
owner: codex
created: 2026-05-06
---

# Launch Recipe Docs

## Why

The README and Web Overview already present four first-launch learning paths:

- `loss-is-lying`
- `first-lora`
- `tool-calling`
- `curriculum-vs-direct`

For launch conversion, those paths should not only be UI cards. They need durable Markdown pages that a visitor can open from GitHub, share in posts, and follow without learning the whole repository first.

## What changed

- Added `docs/recipes/index.md`.
- Added `docs/recipes/loss-is-lying.md`.
- Added `docs/recipes/first-lora.md`.
- Added `docs/recipes/tool-calling.md`.
- Added `docs/recipes/curriculum-vs-direct.md`.
- Updated the README learning-path table to link to the recipe docs.
- Updated the Web Recipe Gallery cards so each path has both an in-app view action and a GitHub recipe link.

## Recipe contract

Each recipe has:

- one learning question
- standard Makefile command path
- artifact paths to inspect
- Web view links
- the expected takeaway
- explicit overclaim guardrails

## Growth rationale

This makes the project easier to star and share because the first four learning promises now resolve to concrete pages instead of only broad Web tabs.

For a first public launch, these pages can also seed:

- good first issues
- social follow-up posts
- docs search traffic
- beginner support links

## Verification

- `make web-build`
- Markdown fence check for `docs/recipes/*.md`, README, and this change note
- Artifact existence check for the probe reports and Level 5 / compare packs referenced by the recipes
