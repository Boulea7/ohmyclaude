# Agent Templates / 代理模板

These are **Claude-oriented markdown agent templates** bundled with OhMyClaude.

---

## What This Directory Is For

This directory contains reusable subagent definitions for common development tasks.

They are intended to be:

- installed into `~/.claude/agents/` by supported presets
- used as reference material for project-specific agent design
- kept lightweight and easy to copy or adapt

They are **not** a claim that OhMyClaude is a hosted multi-harness agent marketplace.

## Included Templates

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Code review and risk finding |
| `debugger` | Systematic debugging |
| `test-engineer` | Test design and automation |
| `refactor-expert` | Focused refactoring help |
| `doc-writer` | Technical documentation |
| `code-architecture-reviewer` | Architecture review |
| `auto-error-resolver` | Error triage and resolution |
| `security-reviewer` | Security-focused review before merge |
| `web-research-specialist` | Research and source gathering |
| `documentation-architect` | Documentation structure design |
| `plan-reviewer` | Plan validation |

## Format

Each template is a standalone markdown file with frontmatter.

```markdown
---
name: agent-name
description: Agent purpose
model: sonnet|haiku|opus
color: blue|red|green|purple|cyan
---

[agent instructions]
```

## Usage Notes

### Claude Code

These templates map naturally to Claude-style agent directories and markdown-based agent definitions.

### Codex

For generated Codex bundles, OhMyClaude emits native `.codex/agents/*.toml` role files separately.

Treat the markdown files in this directory as reference-style agent prompts, not as a drop-in Codex role format.

### Gemini CLI

Gemini extension bundles can reuse markdown-based agent definitions in `agents/`, but feature parity is still evolving.

## Design Guidelines

When adding or revising a template:

- keep one agent focused on one job
- define the expected output clearly
- prefer concrete checklists over vague roleplay
- avoid embedding repo-specific paths unless the template is intentionally project-specific
