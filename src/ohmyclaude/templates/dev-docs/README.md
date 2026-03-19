# Dev Docs Templates / 开发文档模板

The Dev Docs templates provide a **three-file task tracking workflow** for long-running Claude-assisted work.

---

## Purpose

Use these templates when a task is large enough that you want durable written context across multiple sessions.

The pattern separates:

- strategy
- implementation context
- execution checklist

## Three-File Layout

| File | Purpose |
|------|---------|
| `[task]-plan.md` | 目标、方案、阶段拆分 |
| `[task]-context.md` | 关键文件、依赖、决策、接口 |
| `[task]-tasks.md` | 执行清单、状态、恢复入口 |

## Recommended Directory

```text
project/
└── dev/
    └── active/
        └── [task-name]/
            ├── [task-name]-plan.md
            ├── [task-name]-context.md
            └── [task-name]-tasks.md
```

## Why It Helps

- 减少长任务中的上下文漂移
- 让下一次会话更容易恢复
- 把“方案”和“执行清单”分开，降低噪音

## Relationship To Commands

OhMyClaude 仍然保留 `/dev-docs` 一类命令模板作为快捷入口。

但这里更重要的是 **workflow pattern 本身**：

- 你可以通过命令生成
- 也可以手动创建
- 这不是依赖某个单独命令才能成立的机制

## Template Contents

### `plan-template.md.j2`

适合记录：

- 目标摘要
- 当前状态
- 方案设计
- 实施阶段
- 风险与验证

### `context-template.md.j2`

适合记录：

- 关键文件
- 依赖关系
- 技术决策
- 接口与数据流

### `tasks-template.md.j2`

适合记录：

- 分阶段 checklist
- Blockers
- 完成情况
- 会话恢复提示

## Maintenance Notes

This directory is a reusable documentation workflow pattern.

It should not be described as:

- a guaranteed official Claude feature
- a multi-harness standard
- a substitute for current implementation docs such as `README.md`
