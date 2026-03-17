# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it through GitHub Issues:

1. Go to [Issues](https://github.com/Boulea7/ohmyclaude/issues)
2. Create a new issue with the `security` label
3. Provide detailed information about the vulnerability

For critical vulnerabilities that should not be disclosed publicly, please use GitHub's private vulnerability reporting feature if available.

## Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 72 hours |
| Fix timeline | Based on severity |

## Supported Versions

| Version | Security Support |
|---------|------------------|
| 1.x | ✅ Supported |
| < 1.0 | ❌ Not supported |

## Security Best Practices

When using OhMyClaude, please follow these guidelines:

### API Key Security

- **Use environment variables** to store API keys
- **Never hardcode** API keys in configuration files
- Use `omc switch` to manage provider credentials securely

```bash
# Good: Use environment variable
export ANTHROPIC_AUTH_TOKEN="your-key"

# Bad: Hardcoded in files (don't do this)
```

### Configuration Files

- Do not commit `~/.claude/settings.json` to version control
- The `.gitignore` template excludes sensitive files by default
- Review generated configurations before sharing

### MCP Server Security

- Only install MCP servers from trusted sources
- Review MCP server permissions before installation
- Use `omc doctor` to verify configuration integrity

## Security Considerations

### What OhMyClaude Accesses

| Resource | Access Level | Purpose |
|----------|--------------|---------|
| `~/.claude/` | Read/Write | Claude Code configuration |
| `~/.ohmyclaude/` | Read/Write | Backups and provider settings |
| System keyring | Read/Write | Credential storage |
| PyPI API | Read-only | Version checking |

### Data Handling

- OhMyClaude does **not** collect telemetry or analytics
- API keys are stored in the system keyring when possible
- Backups are stored locally and never transmitted

## Acknowledgments

We appreciate security researchers who help improve OhMyClaude. Contributors who report valid security issues will be acknowledged in our release notes (unless they prefer to remain anonymous).
