# CLAUDE.md - Project Index

This file provides an overview of all resources in this repository.

---

## Project Structure

```
/Users/jialinli/ohmyclaude/
├── CLAUDE.md           # This file - project index
├── superclaude/        # SuperClaude Framework
├── codexmcp/           # CodexMCP - Claude & Codex collaboration
└── claudedocs/         # Claude official documentation (scraped)
```

---

## 1. SuperClaude Framework (`superclaude/`)

**Source**: https://github.com/SuperClaude-Org/SuperClaude_Framework
**Version**: 4.1.9
**License**: MIT

### Overview

SuperClaude is a **meta-programming configuration framework** that transforms Claude Code into a structured development platform through behavioral instruction injection and component orchestration.

### Key Statistics

| Component | Count | Description |
|-----------|-------|-------------|
| Commands | 30 | Slash commands for development lifecycle |
| Agents | 16 | Specialized AI agents |
| Modes | 7 | Behavioral modes |
| MCP Servers | 8 | Tool integrations |

### Core Features

- **PM Agent Patterns**:
  - `ConfidenceChecker`: Pre-execution confidence assessment (>=90% proceed, 70-89% alternatives, <70% ask)
  - `SelfCheckProtocol`: Post-implementation evidence-based validation
  - `ReflexionPattern`: Error learning and prevention

- **Parallel Execution**: Wave -> Checkpoint -> Wave pattern (3.5x faster)

- **Token Efficiency**: ROI 25-250x token savings through confidence checks

### Installation

```bash
# Option 1: pipx (recommended)
pipx install superclaude
superclaude install

# Option 2: From source
cd superclaude && ./install.sh
```

### Key Files

| File | Purpose |
|------|---------|
| `PLANNING.md` | Architecture, design principles |
| `TASK.md` | Current tasks and priorities |
| `KNOWLEDGE.md` | Accumulated insights |
| `CLAUDE.md` | Development guidelines |

---

## 2. CodexMCP (`codexmcp/`)

**Source**: https://github.com/GuDaStudio/codexmcp
**License**: MIT

### Overview

CodexMCP enables seamless collaboration between **Claude Code** and **Codex**:

- **Claude Code**: Requirements analysis, architecture planning, code refactoring
- **Codex**: Algorithm implementation, bug localization, code review
- **CodexMCP**: Session context management, multi-turn dialogue, parallel tasks

### Advantages over Official Codex MCP

| Feature | Official | CodexMCP |
|---------|----------|----------|
| Basic Codex calls | Yes | Yes |
| Multi-turn dialogue | No | Yes |
| Reasoning trace | No | Yes |
| Parallel tasks | No | Yes |
| Error handling | No | Yes |

### Installation

```bash
# Remove official Codex MCP if installed
claude mcp remove codex

# Install CodexMCP
claude mcp add codex -s user --transport stdio -- uvx --from git+https://github.com/GuDaStudio/codexmcp.git codexmcp

# Verify
claude mcp list
```

### Tool Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `PROMPT` | `str` | Yes | - | Task instruction for Codex |
| `cd` | `Path` | Yes | - | Working directory |
| `sandbox` | `Literal` | No | `read-only` | Sandbox policy |
| `SESSION_ID` | `UUID` | No | `None` | Session ID for multi-turn |
| `return_all_messages` | `bool` | No | `False` | Return full reasoning |

### Collaboration Protocol

1. **Requirement Analysis**: Share initial analysis with Codex for refinement
2. **Get Prototype**: Request code prototype from Codex (unified diff only)
3. **Code Review**: Use Codex to review after implementation
4. **Critical Thinking**: Challenge Codex's answers, seek truth through debate

---

## 3. Claude Documentation (`claudedocs/`)

**Source**: https://platform.claude.com/docs (scraped)

### Overview

Local copy of Claude's official documentation, scraped and converted to Markdown format for offline reference.

### Statistics

- **Total Documents**: 107 Markdown files
- **Categories**: 15 directories

### Directory Structure

```
claudedocs/
├── scraper.py              # Python scraper script
└── content/                # Downloaded documentation
    ├── about-claude/       # Model information
    ├── administration/     # Admin API
    ├── agent-sdk/          # Agent SDK guides
    ├── agent-skills/       # Agent skills
    ├── api/                # API reference
    ├── build-with-claude/  # Building features
    ├── claude-code/        # Claude Code docs
    ├── claude-on-other-platforms/  # Bedrock, Vertex, etc.
    ├── guardrails/         # Safety and guardrails
    ├── mcp/                # MCP integration
    ├── prompt-engineering/ # Prompt techniques
    ├── resources/          # Additional resources
    ├── test-and-evaluate/  # Testing guides
    └── tools/              # Tool usage
```

### Key Documentation Topics

| Category | Topics |
|----------|--------|
| API | Messages, Streaming, Batches, Files, Authentication |
| Build | Vision, PDF, Embeddings, Structured Outputs, Caching |
| Tools | Bash, Code Execution, Computer Use, Web Search/Fetch |
| Agent SDK | TypeScript/Python SDK, Subagents, Plugins, MCP |
| Prompt Engineering | CoT, XML tags, Examples, Long context tips |
| Guardrails | Hallucinations, Jailbreaks, Prompt leak |

### Re-scraping

```bash
cd claudedocs && python3 scraper.py
```

---

## Quick Reference

### Environment Setup

```bash
# Python dependencies
pip3 install requests beautifulsoup4 markdownify

# UV (for CodexMCP)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Useful Commands

```bash
# SuperClaude
cd superclaude && make dev      # Development mode
cd superclaude && make test     # Run tests

# CodexMCP
claude mcp list                 # Check MCP status

# Claude Docs
python3 claudedocs/scraper.py   # Re-scrape documentation
```

---

## Notes

- All repositories have `.git` directories removed to avoid conflicts
- You can initialize your own git repository in the root directory
- Each subfolder can be updated independently from its source
