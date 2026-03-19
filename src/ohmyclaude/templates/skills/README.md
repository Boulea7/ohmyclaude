# Skills

Reference skill templates for Claude Code, with optional compatibility notes for Codex-aware workflows.

---

## What These Skills Are

These templates are **project-scoped skill assets** intended primarily for Claude Code.

They are useful for:

- packaging repeatable workflow guidance
- keeping long instructions out of a single global prompt
- attaching examples, references, and anti-patterns to one topic

They are **not** a guarantee of automatic activation by themselves.

## What OhMyClaude Actually Ships

Current template groups:

- `coding-standards`
- `tdd-workflow`
- `e2e-testing`
- `worktree-isolation`
- `backend-dev-guidelines`
- `frontend-dev-guidelines`
- `route-tester`
- `error-tracking`
- `skill-developer`
- `api-design`
- `deep-research`
- `git-workflow`
- `performance`
- `search-first`
- `security-review`
- `verification-loop`

For Claude home installs, these are installed only by presets that opt into them.

For generated `codex-project` and `gemini-extension` bundles, OhMyClaude may also
include a portable baseline skill set even when a preset does not list every
skill explicitly.

The current portable baseline is intentionally curated and centered on:

- `api-design`
- `coding-standards`
- `deep-research`
- `git-workflow`
- `performance`
- `search-first`
- `security-review`
- `tdd-workflow`
- `verification-loop`

## Activation Model

There are two different layers to keep in mind:

### Native Skill Usage

Modern Claude and Codex workflows both support skill-centric organization.

Use skills when you want:

- reusable domain guidance
- task-specific checklists
- structured references that are too large for a single prompt

### Optional Auto-Activation Layer

OhMyClaude also includes a `skill-rules.json` + hook-based auto-activation pattern in the `full` preset.

This layer is:

- optional
- Claude-oriented
- helpful for teams that want prompt/file-trigger suggestions

It should be treated as a **compatibility workflow**, not the only valid way to use skills.

## Available Skill Templates

### skill-developer

Meta-skill for creating and maintaining skills.

Use it when you need to:

- create a new skill
- split a large skill into resources
- design trigger rules
- debug skill activation behavior

### coding-standards

Shared KISS/DRY/YAGNI guardrails for writing and reviewing code.

Best suited for:

- keeping new changes simple
- reviewing maintainability tradeoffs
- reducing unnecessary abstractions

### tdd-workflow

Practical RED-GREEN-REFACTOR guidance for feature work and regression fixes.

Best suited for:

- writing one failing test at a time
- protecting refactors with behavior-based tests
- turning bug reports into repeatable regressions

### e2e-testing

Stable browser-flow testing guidance for Playwright and similar suites.

Best suited for:

- designing critical user-flow coverage
- reviewing flaky end-to-end tests
- improving selectors, waits, and CI artifacts

### worktree-isolation

Safe git worktree setup guidance for isolated or parallel work.

Best suited for:

- risky feature work
- parallel investigations
- clean handoffs between execution lanes

### backend-dev-guidelines

Backend conventions and examples for Node.js / Express / TypeScript style projects.

Focus areas:

- layered architecture
- services and repositories
- validation
- monitoring and error handling

### frontend-dev-guidelines

Frontend conventions and examples for React / TypeScript style projects.

Focus areas:

- component structure
- routing and data fetching
- file organization
- performance and loading states

### route-tester

Task-focused testing guidance for authenticated API routes.

Best suited for:

- debugging route behavior
- validating auth-protected endpoints
- producing reproducible curl-based checks

### error-tracking

Sentry-oriented error tracking patterns.

Best suited for:

- adding monitoring
- improving exception context
- wiring observability into backend or frontend code

## How To Use Them In A Project

### Claude Code

Copy the selected skill directory into `.claude/skills/`.

If you also want auto-activation:

1. copy `skill-rules.json`
2. copy the matching hook scripts
3. customize path and intent triggers for the project

In generated `claude-home`, `claude-plugin`, and `gemini-extension` outputs,
OhMyClaude now ships that `skill-rules.json` file automatically when the `full`
preset enables the activation hooks.

### Codex

For generated Codex project bundles, OhMyClaude installs portable skills into `.agents/skills/`.

Keep in mind:

- the skill content is portable
- Claude hook-based trigger rules are still Claude-specific
- Codex-native discovery should come from `.agents/skills/` and `AGENTS.md`

### Gemini CLI

For generated Gemini extension bundles, OhMyClaude copies the same portable skill directories into `skills/`.

Keep in mind:

- Gemini extension packaging is explicit and destination-based
- skill portability is high, but hook and command behavior still differs by harness

## Customization Advice

Customize before shipping these templates into another project:

- update path patterns
- remove stack-specific assumptions
- check example imports and framework references
- keep only the skills that match the target repository

## Repository Notes

This README describes the **template assets inside OhMyClaude**.

It does not mean:

- OhMyClaude is a universal skill installer
- all skills auto-activate by default
- the same activation mechanism works unchanged across Claude Code and Codex
