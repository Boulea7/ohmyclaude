# OhMyClaude

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![CLI](https://img.shields.io/badge/interface-CLI-black)
![Claude First](https://img.shields.io/badge/focus-Claude%20First-6f42c1)
![Codex Aware](https://img.shields.io/badge/focus-Codex%20Aware-0a7ea4)
![Local Safe](https://img.shields.io/badge/testing-local%20safe-2ea44f)

**Language:** English | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

**A local-safe multi-harness workflow CLI with Claude-first defaults.**

OhMyClaude helps you bootstrap a practical Claude Code setup on your machine: generate `settings.json`, generate `CLAUDE.md`, install commands / hooks / agents / skills templates, switch providers, initialize shell integration, and keep backups around configuration changes.

The project now has a staged scope:

- **Claude-first**: the default install path is still Claude Code
- **Multi-harness**: OhMyClaude can now render and explicitly install bundle outputs for Claude plugin, Codex project assets, and Gemini extensions
- **Local-safe**: repository development and tests should not mutate your real `~/.claude`, `~/.codex`, or Gemini CLI configuration

## Why OhMyClaude

Many Claude Code repositories fall into one of two extremes:

- they are too small to be reusable beyond a few copy-paste snippets
- or they grow into a broad multi-harness framework whose code and public docs drift apart

OhMyClaude aims for the middle:

- a focused Python CLI for installing a coherent Claude workflow
- enough templates to be useful out of the box
- clear separation between **public repository content** and **private local AI working notes**

## Highlights

| Area | What You Get |
|------|--------------|
| Claude setup | Generate `~/.claude/settings.json`, `~/.claude/CLAUDE.md`, commands, hooks, agents, and skills |
| Multi-harness bundles | Render or install `.claude-plugin/`, `.codex/`, `.agents/skills/`, and Gemini extension bundles to explicit destinations |
| Workflow assets | Install `9` commands, `11` agents, `16` skills, and `8` hook script templates |
| Curated phase 2 | Add `coding-standards`, `tdd-workflow`, `e2e-testing`, `worktree-isolation`, and a dedicated `security-reviewer` |
| MCP bundles | Compose MCP groups from `templates/mcp/mcp_packages.yaml` |
| Provider switching | Switch official, third-party, and custom providers with backup support and explicit Codex auth opt-in |
| Shell integration | Add or remove shell initialization blocks via `omc init` |
| Config safety | `doctor`, `render`, `install`, `export`, `import`, backup, restore, and rollback-friendly writes |
| Codex and Gemini awareness | Distinguish Claude-side Codex bridge usage from native Codex concepts and Gemini extension outputs |

## What It Does Today

Current implemented capabilities:

- install Claude Code configuration and templates
- generate `mcpServers` and hooks from presets
- install commands / hooks / agents / skills templates
- render explicit target bundles for `claude-home`, `claude-plugin`, `codex-project`, and `gemini-extension`
- manage API providers
- optionally update OpenAI-compatible Codex auth settings only when explicitly requested
- run health checks, shell initialization, export/import, and version checks

## What It Does Not Do

Current non-goals:

- it is **not** a hosted plugin marketplace or registry service
- it does **not** auto-register rendered bundles with Claude Code or Gemini CLI for you
- it does **not** implicitly rewrite your real `~/.codex` or `~/.gemini` during repository maintenance
- it does **not** manage Gemini CLI global settings.json merging in this phase

## Safety Model

If you are developing or maintaining this repository locally and do not want accidental tool configuration changes:

- use `omc switch <provider>` when testing provider changes; Codex auth sync is now opt-in via `--sync-codex-auth`
- rely on the repository test suite, which patches paths into temp directories
- do not manually smoke test against your real `~/.claude`, `~/.codex`, or Gemini directories
- prefer `omc render` and explicit `omc install --dest ... --confirm` into temporary locations
- `omc render` refuses paths inside your real harness home directories by design
- `setup` now preserves existing same-named skills and `skill-rules.json` instead of silently overwriting them

## Installation

### `pip`

```bash
pip install ohmyclaude
```

### `pipx`

```bash
pipx install ohmyclaude
```

### From Source

```bash
git clone https://github.com/Boulea7/ohmyclaude.git
cd ohmyclaude
pip install -e .
```

## Quick Start

```bash
# 1. Install a preset
omc setup --preset standard

# 2. Render a Codex project bundle without touching your real home directory
omc render --target codex-project --output ./.tmp/codex-project

# 3. Install a Gemini extension bundle into an explicit destination
omc install --target gemini-extension --preset standard --dest ./.tmp/gemini-extension --confirm

# 4. Check Claude configuration status
omc doctor

# 5. Check shell integration status
omc init --status

# 6. Switch provider without touching Codex auth
omc switch glm
```

## Commands

| Command | Purpose |
|---------|---------|
| `omc setup` | Install the `starter`, `standard`, or `full` preset |
| `omc doctor` | Inspect a target surface such as Claude home, plugin bundle, Codex project bundle, or Gemini extension bundle |
| `omc init` | Add or remove shell initialization blocks |
| `omc render --target <target>` | Render a target bundle into an explicit output directory |
| `omc install --target <target>` | Install a target bundle into an explicit destination with confirmation |
| `omc switch <provider>` | Switch API provider |
| `omc switch --list` | List available providers |
| `omc provider list/show/add/remove` | Manage custom providers |
| `omc export <file>` | Export current Claude configuration |
| `omc import <file>` | Restore configuration from an archive |
| `omc update` | Check for package updates |

## Preset Comparison

| Preset | Positioning | Current Shape |
|--------|-------------|---------------|
| `starter` | smallest useful setup | `basic` MCP, 3 commands, 2 agents, no skill install |
| `standard` | recommended daily workflow | `basic + reasoning + code + codex`, 5 commands, 6 agents, 2 curated skills, inline hooks |
| `full` | most complete Claude asset set | 7 base MCP groups, 3 optional MCP groups, 9 commands, 11 agents, 16 skills, 8 hook scripts |

Notes:

- this table describes the default `claude-home` install surface
- `standard` now includes a lightweight curated baseline: `coding-standards`, `tdd-workflow`, `/tdd`, and `security-reviewer`
- `full` adds browser-facing and isolation-oriented assets such as `e2e-testing`, `worktree-isolation`, and `/worktree`
- the `codex` preset entry is a **Claude-side bridge path**
- it is not the same thing as native Codex project instructions, native Codex skills, or `.codex/config.toml`
- public wording in this repository now follows modern Claude / Codex terminology more closely, but runtime behavior is still defined by the current codebase

## Targets

Current explicit output targets:

| Target | Output Shape | Typical Use |
|--------|--------------|-------------|
| `claude-home` | `settings.json`, `CLAUDE.md`, `commands/`, `hooks/`, `agents/`, `skills/` | Install into a temp Claude directory or an explicit `~/.claude` replacement |
| `claude-plugin` | `.claude-plugin/plugin.json` plus `commands/`, `hooks/`, `agents/`, `skills/` | Package a shareable Claude plugin bundle |
| `codex-project` | `AGENTS.md`, `.codex/config.toml`, `.codex/agents/`, `.agents/skills/` | Seed a project-local native Codex layer |
| `gemini-extension` | `gemini-extension.json`, `GEMINI.md`, `commands/`, `hooks/`, `agents/`, `skills/` | Create a Gemini CLI extension bundle |

For non-default locations, pass `omc doctor --target <target> --path <root>` so
the CLI inspects the intended bundle root instead of falling back to `cwd` or
`~/.claude`.

Portable plugin and Gemini hooks are currently a self-contained subset of the
full Claude home hook behavior. They remove direct `OHMYCLAUDE_ROOT` coupling
and prefer bundle-local assets, but some scripts still keep Claude-oriented
fallbacks and do not yet mirror every `full` preset hook one-for-one.

## Repository Layout

```text
src/ohmyclaude/
├── cli/            # Click CLI entrypoint
├── core/           # install, config, provider, shell, backup
├── models/         # Pydantic models
├── modules/        # MCP and provider definitions
├── templates/      # CLAUDE.md / commands / hooks / agents / skills templates
└── ui/             # Rich-based CLI presentation helpers

templates/
├── presets/        # starter / standard / full YAML
└── mcp/            # MCP package registry

tests/
├── unit/
└── integration/
```

## Public vs Local Docs

This repository intentionally separates **public GitHub content** from **private local AI working material**.

### Public

The public surface of the repository should primarily be:

- `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- `docs/`
- tracked maintainer docs such as `AGENTS.md` and `CLAUDE.md`
- `src/`
- `templates/`
- `tests/`
- root public docs such as `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `RELEASE_GUIDE.md`

### Local

Private local material should stay in ignored paths such as:

- `.ai-notes/`
- machine-specific scratch files and temporary indexes
- extra AI-facing notes that are not meant to be shared in Git history

This keeps truly private working context out of public Git history while allowing the repository to keep its curated maintainer docs under version control.

## FAQ

### Does this project configure native Codex for me?

It can now render or install project-scoped Codex assets to an explicit destination, but it does not auto-write your real `~/.codex` during normal repository maintenance.

### Can `switch` modify my Codex configuration?

Only if you explicitly opt in with `--sync-codex-auth`.

### Why are local AI notes not part of the public repo?

Because research notes, working indexes, and AI-facing scratch docs are useful locally but make the public repository noisier, less portable, and more privacy-sensitive.

### Is this a multi-harness configuration platform?

Yes, in a staged way. The current phase focuses on explicit bundle rendering and destination-based installation, not on implicit home-directory mutation across every harness.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Ruff
ruff check .

# MyPy
python -m mypy src/ohmyclaude

# Pytest
pytest
```

## Roadmap

The most realistic next steps are:

- deepen target-specific validation for Claude plugin and Gemini extension outputs
- add a lightweight install-state and troubleshooting layer without turning the CLI into a heavy runtime framework
- keep expanding curated shared skills and native Codex/Gemini target quality without bloating default presets
- add more target-aware doctor checks and troubleshooting docs
- keep the install surface explicit and local-safe as multi-harness support grows

## Acknowledgements

- [obra/superpowers](https://github.com/obra/superpowers) — workflow discipline, design-first thinking, skill-driven execution
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — layered rules / skills / hooks / troubleshooting organization
- [Claude Code Docs](https://code.claude.com/docs/en) — current hooks, plugins, memory, and subagent capabilities
- [OpenAI Codex Docs](https://developers.openai.com/codex/) — current `AGENTS.md`, skills, subagents, and config capabilities
- [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — current Gemini CLI extension, command, skill, and project context patterns
