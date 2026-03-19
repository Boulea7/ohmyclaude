# Changelog

All notable changes to OhMyClaude are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Repositioned the repository as **Claude-first, Codex-aware**
- Rewrote public README content around current product boundaries
- Simplified public template wording to better match current Claude / Codex terminology
- Clarified the separation between public repository content and local AI-private material
- Upgraded the product direction to **Claude-first, multi-harness, local-safe**
- Made Codex auth sync explicit via opt-in `--sync-codex-auth`

### Added

- English default `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- Explicit bundle targets for `claude-home`, `claude-plugin`, `codex-project`, and `gemini-extension`
- New `omc render` and `omc install` commands for destination-based output
- New Codex project templates: `AGENTS.md`, `.codex/config.toml`, `.codex/agents/*.toml`
- New Gemini extension templates: `gemini-extension.json`, `GEMINI.md`, TOML commands, hooks, skills, and agents
- Portable workflow skills: `api-design`, `deep-research`, `git-workflow`, `performance`, `search-first`, `security-review`, `verification-loop`

### Cleaned Up

- Moved AI-private repository files out of the public tracked surface
- Reworked public docs to remove stale or machine-specific release guidance
- Kept conservative backups for previously evaluated cleanup candidates

## [1.0.0] - 2024-12-07

### Added

- preset-based Claude Code configuration installation
- provider switching for official and third-party endpoints
- configuration backup and restore support
- generated `CLAUDE.md`, commands, hooks, agents, and MCP configuration
- Click-based CLI with Rich output

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| Unreleased | 2026-03 | Multi-target bundles, explicit render/install commands, safer Codex sync defaults, and docs cleanup |
| 1.0.0 | 2024-12-07 | Initial release |
