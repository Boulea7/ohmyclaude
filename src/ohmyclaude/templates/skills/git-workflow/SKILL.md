---
name: git-workflow
description: Use when preparing commits, reviewing branch hygiene, or deciding how to package and describe changes for collaboration.
---

# Git Workflow

## Goals

- Keep history understandable.
- Avoid mixing unrelated changes.
- Make review easier for humans and agents.

## Checklist

1. Inspect the working tree before committing.
2. Separate unrelated changes whenever practical.
3. Use a short, specific commit message that describes the user-visible change.
4. Confirm sensitive files and secrets are not staged.
5. Mention testing or validation in the final summary.

## Guardrails

- Do not amend or rewrite history unless explicitly requested.
- Do not revert unrelated local changes.
- Prefer non-interactive git commands.
