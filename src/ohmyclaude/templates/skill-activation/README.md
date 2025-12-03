# Skill Activation Templates / 技能激活模板

This directory contains templates for the Claude Code skill auto-activation system.

## Files / 文件

| File | Description | 描述 |
|------|-------------|------|
| `skill-rules.json` | Skill trigger configuration (bilingual) | 技能触发配置（双语） |
| `skill-activation-prompt.ts` | UserPromptSubmit hook | 用户提示提交钩子 |
| `post-tool-use-tracker.sh` | File edit tracking hook | 文件编辑追踪钩子 |

## Installation / 安装

These files are automatically installed to `~/.claude/` when using OhMyClaude with skill activation enabled.

使用 OhMyClaude 启用技能激活时，这些文件会自动安装到 `~/.claude/`。

## skill-rules.json

The skill rules file defines when skills should be triggered based on:

- **Keywords**: Words in the user's prompt that trigger skills
- **Intent Patterns**: Regex patterns for detecting user intent
- **File Triggers**: File paths that trigger skills when edited

### Enforcement Levels / 执行级别

| Level | Behavior | 行为 |
|-------|----------|------|
| `suggest` | Shows suggestion, doesn't block | 显示建议，不阻断 |
| `warn` | Shows warning, allows proceeding | 显示警告，允许继续 |
| `block` | Requires skill usage before proceeding | 需要先使用技能 |

### Priority Levels / 优先级

| Priority | When Triggered | 触发时机 |
|----------|----------------|---------|
| `critical` | Always when matched | 匹配时始终触发 |
| `high` | Most matches | 大多数匹配 |
| `medium` | Clear matches | 明确匹配 |
| `low` | Explicit matches only | 仅显式匹配 |

## Customization / 自定义

To customize skill rules for your project:

1. Copy `skill-rules.json` to your project's `.claude/skills/`
2. Modify keywords and patterns for your domain
3. Add project-specific file triggers

要为项目自定义技能规则：

1. 复制 `skill-rules.json` 到项目的 `.claude/skills/`
2. 修改关键词和模式以适应你的领域
3. 添加项目特定的文件触发器

## Hook Configuration / 钩子配置

Add to `settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "npx ts-node ~/.claude/hooks/skill-activation-prompt.ts",
        "timeout": 5000
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/post-tool-use-tracker.sh"
          }
        ]
      }
    ]
  }
}
```

## Based On / 基于

[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Production-grade Claude Code configuration patterns.
