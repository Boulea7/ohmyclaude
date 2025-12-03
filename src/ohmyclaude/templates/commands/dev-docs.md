---
description: Create comprehensive development documentation with three-file structure
argument-hint: <task name or description>
---

You are a documentation specialist. Build or refresh the three-file dev doc set for: $ARGUMENTS
你是一名文档专家，负责为 $ARGUMENTS 创建或更新"三文件"开发文档集。

## Task / 任务

Create or update structured development documentation using the three-file system to ensure task continuity across context resets.
使用三文件系统创建/更新结构化开发文档，确保上下文重置后仍可继续任务。

## Workflow / 流程

### 1. Analyze the Request / 分析需求

- Understand the scope and complexity of the task
- Identify key components, dependencies, and risks
- Determine the appropriate level of detail

### 2. Create Directory Structure / 创建目录结构

```bash
mkdir -p dev/active/[task-name]/
```

### 3. Generate Three Files / 生成三个文件

#### File 1: `[task-name]-plan.md` - The Strategic Plan / 战略计划

```markdown
# [Task Name] - Implementation Plan

> Last Updated: YYYY-MM-DD
> Status: In Progress / Completed / On Hold

## Executive Summary
Brief overview of what this task accomplishes.

## Current State Analysis
- What exists now
- Problems or limitations
- Technical debt (if applicable)

## Proposed Future State
- Target architecture
- Expected outcomes
- Success criteria

## Implementation Phases

### Phase 1: [Name]
- Objective
- Key tasks
- Deliverables

### Phase 2: [Name]
...

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| ... | High/Med/Low | High/Med/Low | Strategy |

## Success Metrics
- Metric 1: ...
- Metric 2: ...

## Timeline Estimates
- Phase 1: X days
- Phase 2: Y days
- Total: Z days
```

#### File 2: `[task-name]-context.md` - Technical Context / 技术上下文

```markdown
# [Task Name] - Technical Context

> Last Updated: YYYY-MM-DD

## Key Files
List of files most relevant to this task:
- `path/to/file1.py` - Description
- `path/to/file2.ts` - Description

## Architecture Decisions

### Decision 1: [Title]
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Consequences**: Trade-offs and implications

## Dependencies
- External: libraries, services, APIs
- Internal: other modules, components

## Environment Notes
- Required environment variables
- Configuration settings
- Development setup

## Useful Commands
```bash
# Command description
command here
```

## Reference Documentation
- Links to relevant docs
- API documentation
- Design documents
```

#### File 3: `[task-name]-tasks.md` - Task Checklist / 任务清单

```markdown
# [Task Name] - Task Checklist

> Last Updated: YYYY-MM-DD
> Progress: X/Y tasks completed

## Priority Legend
- P0: Critical - Must complete
- P1: High - Should complete
- P2: Medium - Nice to have
- P3: Low - Future consideration

## Phase 1: [Name]

### P0 - Critical
- [ ] Task description (Effort: S/M/L/XL)
  - Acceptance criteria
  - Dependencies: [list]

### P1 - High Priority
- [ ] Task description (Effort: M)

## Phase 2: [Name]

### P0 - Critical
- [ ] Task description (Effort: L)

## Completed Tasks
- [x] ~~Completed task~~ (Date)

## Blocked Tasks
- [ ] Blocked task - Reason: [explanation]

## Notes
- Important observations
- Decisions made during implementation
```

### 4. Include Metadata / 包含元数据

Each file should have:
- Last Updated timestamp
- Status or progress indicator
- Session notes (if applicable)

## Quality Standards / 质量标准

- **Self-Contained**: All context needed to continue work
- **Actionable**: Clear next steps and acceptance criteria
- **Technical**: Include specific file paths, code snippets, commands
- **Realistic**: Honest assessment of risks and effort
- **Maintained**: Update regularly as work progresses

## When to Use / 使用时机

Use this command:
- After exiting plan mode with a clear vision
- Before starting complex multi-day tasks
- When context might be lost (long tasks, collaboration)
- To create handoff documentation

## Notes / 注意事项

- Keep files focused and scannable
- Update `-tasks.md` as you complete work
- Use `-context.md` to capture hard-to-rediscover information
- Reference these files with "continue [task-name]" to resume
