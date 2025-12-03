# Dev Docs Templates / 开发文档模板

The Dev Docs system is a three-file workflow for persistent task tracking across Claude Code sessions.

Dev Docs 系统是一个三文件工作流，用于跨 Claude Code 会话的持久任务跟踪。

## The Three-File System / 三文件系统

| File | Purpose | 用途 |
|------|---------|------|
| `[task]-plan.md` | Implementation strategy and phases | 实施策略和阶段 |
| `[task]-context.md` | Key files, decisions, dependencies | 关键文件、决策、依赖 |
| `[task]-tasks.md` | Checklist for tracking progress | 进度跟踪清单 |

## Why Three Files? / 为什么是三个文件？

1. **Prevents context loss**: Claude can "lose direction" in long tasks
2. **Enables session resumption**: Continue seamlessly with "continue" command
3. **Separates concerns**: Strategy vs. context vs. execution

1. **防止上下文丢失**：Claude 在长任务中可能"迷失方向"
2. **支持会话恢复**：使用 "continue" 命令无缝继续
3. **关注点分离**：策略 vs. 上下文 vs. 执行

## Directory Structure / 目录结构

```
project/
└── dev/
    └── active/
        └── [task-name]/
            ├── [task-name]-plan.md
            ├── [task-name]-context.md
            ├── [task-name]-tasks.md
            └── [task-name]-code-review.md (optional)
```

## Templates / 模板

### plan-template.md.j2

Contains:
- Executive summary
- Current state analysis
- Proposed solution
- Implementation phases
- Risk assessment
- Success metrics

### context-template.md.j2

Contains:
- Key files to modify/create/reference
- Architecture context
- Dependencies
- Technical decisions
- API contracts
- Testing strategy

### tasks-template.md.j2

Contains:
- Task checklist by phase
- Priority categorization
- Blocked tasks tracking
- Completion log
- Session resume guide

## Usage / 使用

### Creating Dev Docs / 创建开发文档

Use the `/dev-docs` command:

```
/dev-docs implement user authentication
```

This creates the three files in `dev/active/user-authentication/`.

### Resuming a Session / 恢复会话

Say:

```
Continue working on [task-name]. Please read:
- dev/active/[task-name]/[task-name]-plan.md
- dev/active/[task-name]/[task-name]-context.md
- dev/active/[task-name]/[task-name]-tasks.md

Then continue from where we left off.
```

## Benefits / 优势

- **40-60% token efficiency** through focused context
- **Persistent state** across sessions
- **Clear progress tracking**
- **Better collaboration** between Claude and user

## Based On / 基于

[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Reddit article "Claude Code is a Beast – Tips from 6 Months of Hardcore Use".
