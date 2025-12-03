# Agent Templates / 代理模板

Specialized agent templates for common development tasks.

专业代理模板，用于常见开发任务。

## Available Agents / 可用代理

| Agent | Purpose | 用途 | Model |
|-------|---------|------|-------|
| `code-architecture-reviewer` | Code review and architecture validation | 代码审查和架构验证 | sonnet |
| `auto-error-resolver` | Build and runtime error resolution | 构建和运行时错误解决 | sonnet |
| `plan-reviewer` | Implementation plan validation | 实施计划验证 | sonnet |
| `documentation-architect` | Documentation creation | 文档创建 | haiku |
| `web-research-specialist` | Information gathering and research | 信息收集和研究 | sonnet |

## Agent Structure / 代理结构

Each agent template follows this structure:

```markdown
---
name: agent-name
description: |
  Agent description in English and Chinese.
model: sonnet|haiku|opus
color: blue|red|green|purple|cyan
---

[Agent instructions and capabilities]
```

## Usage / 使用

Agents are used via the Task tool:

```python
# In Claude Code
Use the Task tool with subagent_type='code-architecture-reviewer' to review the changes.
```

## Installation / 安装

Agents are installed to `~/.claude/agents/` when using OhMyClaude with the full preset.

使用 OhMyClaude 的 full 预设时，代理会安装到 `~/.claude/agents/`。

## Creating Custom Agents / 创建自定义代理

1. Create a new `.md` file in this directory
2. Add the YAML frontmatter with required fields
3. Write agent instructions (bilingual recommended)
4. Install via OhMyClaude

1. 在此目录创建新的 `.md` 文件
2. 添加包含必要字段的 YAML 前置元数据
3. 编写代理指令（推荐双语）
4. 通过 OhMyClaude 安装

## Best Practices / 最佳实践

### Agent Design / 代理设计

- **Single responsibility**: One agent, one job
- **Clear output format**: Define expected output structure
- **Bilingual support**: Include Chinese translations
- **Model selection**: Use appropriate model for complexity

### Agent Instructions / 代理指令

- Be specific about capabilities
- Include step-by-step processes
- Define output formats
- List common patterns and solutions
- Provide clear guidelines

## Based On / 基于

[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Production-grade Claude Code agent patterns.
