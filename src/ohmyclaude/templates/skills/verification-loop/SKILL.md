---
name: verification-loop
description: Use before marking work complete to run focused validation such as tests, lint, type checks, and manual sanity checks.
---

# Verification Loop

## Workflow

1. Identify the smallest meaningful validation set for the changed behavior.
2. Run fast checks first.
3. Escalate to broader checks when risk or blast radius increases.
4. Compare expected versus actual results.
5. Report what was verified and what was not.

## Validation Order

- Targeted unit or integration tests
- Lint and type checks
- Build or packaging checks
- Manual review of high-risk paths

## Guardrails

- Never claim verification you did not run.
- State blockers and skipped checks explicitly.
