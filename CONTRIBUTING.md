# Contributing to finetune-lab

Thanks for helping make fine-tuning easier to understand.

`finetune-lab` is not trying to become a general training framework. The project is a learning lab: every contribution should help someone see the full loop from SFT data to LoRA training, held-out probe, case diff, and runtime behavior checks.

## Good First Contributions

The best starter contributions are usually small and evidence-backed:

- Add or improve a recipe that answers one concrete learning question.
- Improve docs where a beginner would otherwise guess commands.
- Add a held-out probe case that exposes a real behavior gap.
- Improve validation around data contracts or tool-call outputs.
- Polish the Web lab when the UI makes an artifact easier to understand.

## Local Readiness

Use the Makefile entrypoints instead of hand-assembling commands:

```bash
make ai-onboarding
make ai-setup
make ai-lab
```

`make ai-onboarding` writes `outputs/agent/onboarding-report.json` and `outputs/agent/onboarding-report.md`. If the report says the repo is ready, `make ai-lab` refreshes the smallest teaching loop:

```text
onboarding -> data -> train -> probe -> compare -> frontend
```

For a narrow change, run the closest target listed in `make help` or `docs/ai/workflows.md`.

## Contribution Shape

Please keep changes focused:

- Docs and recipe names use English kebab-case.
- Design or behavior changes should include a short note under `docs/changes/`.
- Generated data and benchmark artifacts should be included only when they are part of the evidence for the change.
- Do not present simulated smoke runs as real LoRA training.
- Do not claim same-LoRA runtime parity unless the target runtime has been verified with matching artifacts.

## Pull Request Checklist

Before opening a PR, include:

- The learning problem or user confusion this change addresses.
- The command(s) you ran.
- The key artifact paths you inspected or generated.
- Any known limitation, especially around SIM vs REAL runs or runtime-specific behavior.

## Useful Starting Points

- `AGENTS.md` explains how agents should take over the repo.
- `docs/ai/setup.md` explains the readiness flow.
- `docs/ai/workflows.md` maps common tasks to Makefile targets.
- `training/data_pipeline/README.md` explains SFT sample generation and validation.
- `training/finetune/README.md` explains simulated and real MLX LoRA paths.

