# Changelog

All notable changes to OhMyClaude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-07

### Added

#### Core Features
- **3 Preset Configurations**: starter, standard, full - progressive feature sets for different user needs
- **4 API Provider Support**: Official Anthropic, GLM (Zhipu AI), 88Code, DeepSeek with one-command switching
- **Configuration Backup System**: Automatic backup before changes, restore capability, cleanup management
- **Atomic File Operations**: Safe file writes with rollback on failure
- **Deep Merge Algorithm**: Intelligent configuration merging for settings.json

#### Claude Code Integration
- **10 Agent Templates**: Code reviewer, debugger, test engineer, security auditor, and more
- **7 Slash Commands**: /commit, /review, /test, /codex, /dev-docs, /strategic-planning, /update-docs
- **Hooks System**: skill-activation, post-tool-use-tracker, tsc-check, build-checker, error-handling
- **CodexMCP Integration**: Seamless Claude + Codex collaboration support

#### CLI Commands
- `omc setup` - Interactive configuration wizard with preset selection
- `omc doctor` - Health check for Claude Code configuration
- `omc switch <provider>` - Quick API provider switching
- `omc init` - Shell environment integration
- `omc export/import` - Configuration portability
- `omc provider list/show/add` - Provider management

#### Developer Experience
- **CLAUDE.md Templates**: Bilingual (Chinese/English) work instructions
- **MCP Server Packages**: Organized by category (basic, reasoning, code)
- **Shell Integration**: Auto-sourcing environment variables for zsh/bash/fish

### Technical Details

#### Architecture
- Pydantic v2 models for configuration validation
- Jinja2 templates for dynamic content generation
- Click-based CLI with Rich console output
- YAML presets with inheritance support

#### File Structure
```
~/.claude/
├── settings.json      # Claude Code settings
├── CLAUDE.md          # Work instructions
├── commands/          # Slash command templates
├── hooks/             # Hook scripts
└── agents/            # Agent definitions

~/.ohmyclaude/
├── backups/           # Configuration backups
├── providers.yaml     # Custom provider definitions
└── env.sh             # Environment variables
```

### Security
- Atomic writes prevent configuration corruption
- Backup before destructive operations
- Path traversal protection in installers
- Secure credential handling via environment variables

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2024-12-07 | Initial release with full feature set |

---

*OhMyClaude - Claude Code configuration made easy for Chinese developers*
