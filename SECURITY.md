# Security Policy

## Reporting a Vulnerability

If you discover a security issue in OhMyClaude:

1. open a GitHub issue with enough reproduction detail for non-sensitive problems
2. use private reporting channels if the issue would expose users to immediate risk
3. include environment details, affected command flow, and expected vs actual behavior

## Security Scope

OhMyClaude is a local CLI for generating and installing Claude Code configuration and workflow assets.

Important current behaviors:

- it reads and writes inside `~/.claude/`
- it reads and writes inside `~/.ohmyclaude/`
- it can render or install bundle assets into explicit caller-provided target roots
- it updates `~/.codex/auth.json` only when switching to an OpenAI-compatible provider with `--sync-codex-auth`
- it does **not** collect telemetry or analytics

## Supported Versions

| Version | Security Support |
|---------|------------------|
| 1.x | Supported |
| < 1.0 | Not supported |

## Security Best Practices

### Secrets

- keep API credentials in environment variables
- never hardcode secrets in repository files
- do not commit generated local configuration or private AI notes

### Local Configuration

- do not commit your real `~/.claude/settings.json`
- do not commit your real `~/.codex/auth.json`
- keep local AI working files in ignored paths such as `.ai-notes/`

### Provider Switching

When testing or reviewing provider changes:

- prefer plain `omc switch <provider>` for default-safe provider changes
- use `--sync-codex-auth` only when Codex auth changes are intentional
- treat `--skip-codex` as a deprecated compatibility flag, not the primary workflow
- inspect backups before restoring or deleting them
- review diff and generated config before sharing outputs

### Template Safety

- only enable MCP servers from trusted sources
- review hook behavior before installing the `full` preset
- prefer minimum required permissions and minimum required automation

## Data Handling

- backups stay local
- generated files stay local unless you explicitly publish them
- the project is designed so repository tests can run against temporary paths instead of real user directories

## Response Expectations

| Stage | Target |
|-------|--------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 72 hours |
| Fix timeline | Based on severity and reproducibility |
