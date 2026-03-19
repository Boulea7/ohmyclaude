# Skill Activation Templates / 技能激活模板

Legacy duplicate templates for a Claude Code skill auto-activation workflow.
历史遗留的重复模板，用于 Claude Code 技能自动激活工作流。

> Note / 说明
>
> This directory is currently kept for reference only.
> The active installer path uses `src/ohmyclaude/templates/hooks/` and
> `src/ohmyclaude/templates/skills/skill-rules.json` instead.
> 本目录当前仅作为参考保留；
> 现行安装流程使用 `src/ohmyclaude/templates/hooks/` 与
> `src/ohmyclaude/templates/skills/skill-rules.json`。

## Files / 文件

| File | Description | 描述 |
|------|-------------|------|
| `skill-rules.json` | Skill trigger configuration (bilingual) | 技能触发配置（双语） |
| `skill-activation-prompt.ts` | UserPromptSubmit hook | 用户提示提交钩子 |
| `post-tool-use-tracker.sh` | File edit tracking hook | 文件编辑追踪钩子 |

## Installation / 安装

These files are **not** the current authoritative install source.

这些文件**不是**当前权威安装来源。

For live hook and rule wiring, inspect these current sources instead:

- `src/ohmyclaude/templates/hooks/`
- `src/ohmyclaude/templates/skills/skill-rules.json`
- `templates/presets/full.yaml`

如需查看现行 hook / rule 接线方式，请以这些路径为准：

- `src/ohmyclaude/templates/hooks/`
- `src/ohmyclaude/templates/skills/skill-rules.json`
- `templates/presets/full.yaml`

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

## Historical Note / 历史说明

Older examples in this directory may still reference `~/.claude/hooks/` or
`ts-node`.

These snippets are historical reference material only and should not be treated
as the current OhMyClaude installer contract.

本目录中的旧示例可能仍然会引用 `~/.claude/hooks/` 或 `ts-node`。

这些片段仅用于历史参考，不应视为当前 OhMyClaude 安装流程的权威约定。

## Based On / 基于

[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Production-grade Claude Code configuration patterns.
