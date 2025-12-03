# OhMyClaude

Claude Code 一键配置工具 - One-click configuration tool for Claude Code.

## Installation

```bash
pip install ohmyclaude
```

## Quick Start

Both `omc` (shorthand) and `ohmyclaude` commands are available:

```bash
# Run the configuration wizard
omc setup
# or: ohmyclaude setup

# Check configuration health
omc doctor

# Switch API provider
omc switch glm
```

## Commands

| Command | Description |
|---------|-------------|
| `omc setup` | Run interactive configuration wizard |
| `omc doctor` | Check configuration health |
| `omc switch <provider>` | Switch API provider (glm/88code/deepseek/official) |
| `omc export <file>` | Export configuration |
| `omc import <file>` | Import configuration |

## Presets

| Preset | Description | Token Cost |
|--------|-------------|------------|
| **Starter** | Minimal configuration for beginners | ~3,300 (~2%) |
| **Standard** | Recommended for daily development | ~5,500 (~3.5%) |
| **Full** | All features including CodexMCP | ~8,800 (~6%) |

## API Providers

| Provider | Description |
|----------|-------------|
| `official` | Anthropic official API (requires subscription) |
| `glm` | Zhipu AI (China optimized) |
| `88code` | Third-party proxy |
| `deepseek` | DeepSeek V3 (cost-effective) |

## License

MIT
