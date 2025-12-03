# CLAUDE.md - Project Index

This file provides an overview of all resources in this repository.

---

## Project Structure

```
/Users/jialinli/ohmyclaude/
├── CLAUDE.md           # This file - project index
├── docs/               # Project documentation (PRD, Architecture, etc.)
├── superclaude/        # SuperClaude Framework
├── codexmcp/           # CodexMCP - Claude & Codex collaboration
├── claudedocs/         # Claude official documentation (scraped)
└── claude-code-infrastructure-showcase/  # Production-grade Claude Code config examples
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

### PM Agent Quick Reference

**ConfidenceChecker (执行前)** - 5 个检查维度:

| 检查项 | 权重 | 验证方式 |
|--------|------|----------|
| 无重复实现 | 25% | Glob/Grep 搜索代码库 |
| 架构兼容 | 25% | 检查 CLAUDE.md 技术栈 |
| 官方文档验证 | 20% | Context7 MCP / WebFetch |
| OSS 参考 | 15% | WebSearch 开源实现 |
| 根因确认 | 15% | 验证问题分析确定性 |

**SelfCheckProtocol (执行后)** - 4 个关键问题:
1. 所有测试通过了吗？→ 显示实际输出
2. 所有需求满足了吗？→ 列出对比
3. 没有未验证的假设？→ 检查官方文档
4. 有证据吗？→ test_results + code_changes

**ReflexionPattern (错误学习)**:
```
错误检测 → 查找相似错误?
  ├─ YES → 应用已知解决方案 (0 tokens)
  └─ NO  → 调查 → 记录 → 存储供未来使用
```

> **详细文档**: [docs/REFERENCE_SUPERCLAUDE.md](docs/REFERENCE_SUPERCLAUDE.md)

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

## 4. Claude Code Infrastructure Showcase (`claude-code-infrastructure-showcase/`)

**Source**: https://github.com/diet103/claude-code-infrastructure-showcase
**License**: MIT

### Overview

A production-grade Claude Code configuration showcase based on 6 months of intensive use. This repository demonstrates best practices for Skills auto-activation, Dev Docs workflow, and specialized agents.

### Key Statistics

| Component | Count | Description |
|-----------|-------|-------------|
| Skills | 5 | Development guidelines (frontend, backend, planning, etc.) |
| Hooks | 6 | Auto-activation, file tracking, build checking |
| Agents | 10 | Quality control, testing, debugging, planning |
| Commands | 3 | Dev docs, update docs, strategic planning |

### Core Innovations

1. **Skills Auto-Activation System**
   - `skill-rules.json` - Rule-based skill trigger configuration
   - `skill-activation-prompt.ts` - UserPromptSubmit hook for automatic skill injection
   - Supports keywords, intent patterns, and file path triggers

2. **Dev Docs Three-File System**
   - Prevents Claude from "losing direction" in long tasks
   - Structure: `[task]-plan.md`, `[task]-context.md`, `[task]-tasks.md`
   - Enables seamless session continuation with "continue" command

3. **500-Line Rule & Progressive Disclosure**
   - Main SKILL.md files kept under 500 lines
   - Detailed content split into resource files
   - 40-60% token efficiency improvement

### Directory Structure

```
claude-code-infrastructure-showcase/
└── .claude/
    ├── skills/
    │   ├── skill-rules.json        # Skill trigger rules
    │   ├── backend-dev-guidelines/
    │   ├── frontend-dev-guidelines/
    │   └── ...
    ├── hooks/
    │   ├── skill-activation-prompt.ts
    │   ├── post-tool-use-tracker.sh
    │   └── ...
    ├── agents/
    │   ├── code-architecture-reviewer.md
    │   ├── build-error-resolver.md
    │   └── ...
    └── commands/
        ├── dev-docs.md
        └── ...
```

### Key Files Reference

| File | Purpose | OhMyClaude Integration |
|------|---------|------------------------|
| `skill-rules.json` | Skill trigger configuration | Template for bilingual support |
| `skill-activation-prompt.ts` | UserPromptSubmit hook | Core hook template |
| `post-tool-use-tracker.sh` | File edit tracking | Utility hook template |
| `dev-docs.md` | Dev docs command | Optional workflow template |

### Related Resources

- **Reddit Article**: "Claude Code is a Beast – Tips from 6 Months of Hardcore Use"
- **Author**: u/diet103

> **详细文档**: [docs/REFERENCE_SHOWCASE.md](docs/REFERENCE_SHOWCASE.md) - 完整 Hook 代码、代理模板、enforcement 级别详解

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

## Reference Documentation

### SuperClaude Framework

| Document | Description |
|----------|-------------|
| [REFERENCE_SUPERCLAUDE.md](docs/REFERENCE_SUPERCLAUDE.md) | Core patterns (ConfidenceChecker, SelfCheckProtocol, Reflexion) |
| [REFERENCE_COMMANDS.md](docs/REFERENCE_COMMANDS.md) | 30 Slash commands reference |
| [REFERENCE_AGENTS.md](docs/REFERENCE_AGENTS.md) | 20 Specialized agents |
| [REFERENCE_MODES.md](docs/REFERENCE_MODES.md) | 7 Behavioral modes |
| [REFERENCE_FLAGS.md](docs/REFERENCE_FLAGS.md) | FLAGS system (25+ flags) |

### CodexMCP

| Document | Description |
|----------|-------------|
| [REFERENCE_CODEXMCP.md](docs/REFERENCE_CODEXMCP.md) | Complete CodexMCP reference and collaboration protocol |

### Claude Code Infrastructure

| Document | Description |
|----------|-------------|
| [REFERENCE_SHOWCASE.md](docs/REFERENCE_SHOWCASE.md) | Production-grade config showcase |
| [REFERENCE_HOOKS_COMPLETE.md](docs/REFERENCE_HOOKS_COMPLETE.md) | Hook system (6 hooks, skill-rules.json) |

### Project Documentation

| Document | Description |
|----------|-------------|
| [PRD.md](docs/PRD.md) | Product Requirements Document |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Implementation roadmap |

---

## Notes

- All repositories have `.git` directories removed to avoid conflicts
- You can initialize your own git repository in the root directory
- Each subfolder can be updated independently from its source
