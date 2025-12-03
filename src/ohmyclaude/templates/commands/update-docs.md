---
description: Update development documentation before context compaction
argument-hint: [optional: specific doc or focus area]
---

You are a documentation specialist. Update the development documentation to capture current progress before context is compacted or session ends.

## Task / 任务

Update existing development documentation to preserve progress, decisions, and context that would be difficult to rediscover.
更新现有开发文档，保存进度、决策和难以重新发现的上下文信息。

## Arguments / 参数

`$ARGUMENTS` - Optional: specific documentation file or focus area to update

## Workflow / 流程

### 1. Find Active Documentation / 查找活动文档

```bash
# Look for dev docs
ls -la dev/active/
find . -name "*-tasks.md" -o -name "*-context.md" -o -name "*-plan.md"
```

### 2. Update Task Checklist / 更新任务清单

In `[task]-tasks.md`:

- [ ] Mark completed tasks with [x]
- [ ] Add new tasks discovered during work
- [ ] Update effort estimates based on experience
- [ ] Note any blocked tasks and reasons
- [ ] Adjust priorities if needed

```markdown
## Completed This Session
- [x] ~~Task that was completed~~ (YYYY-MM-DD)
- [x] ~~Another completed task~~ (YYYY-MM-DD)

## New Tasks Discovered
- [ ] New task from implementation (Effort: M)
- [ ] Edge case to handle (Effort: S)

## Updated Priorities
- Moved [task] from P1 to P0 because [reason]
```

### 3. Update Technical Context / 更新技术上下文

In `[task]-context.md`:

Capture:
- **Decisions Made** / 做出的决策
  - Why certain approaches were chosen
  - Trade-offs considered

- **Problems Solved** / 解决的问题
  - Bugs fixed and how
  - Workarounds applied

- **Key Files Modified** / 修改的关键文件
  - What was changed and why

- **Dependencies Discovered** / 发现的依赖
  - New libraries or tools used
  - API integrations

```markdown
## Session Update: YYYY-MM-DD

### Decisions Made
- Chose X over Y because [reason]

### Problems Solved
- Fixed [issue] by [solution]
- Workaround for [problem]: [approach]

### Files Modified
- `path/to/file.py` - Added [functionality]
```

### 4. Document Unfinished Work / 记录未完成的工作

Critical for context recovery:

```markdown
## Current State (as of YYYY-MM-DD)

### In Progress
- Working on: [specific task]
- Current approach: [what you're trying]
- Blockers: [if any]

### Partial Implementations
- [Feature] is 70% complete
  - Done: [parts completed]
  - Remaining: [parts needed]

### Temporary Workarounds
- Using [workaround] until [proper solution]
- TODO: Remove workaround when [condition]
```

### 5. Create Handoff Notes / 创建交接备注

For seamless continuation:

```markdown
## Handoff Notes

### Exact Position
- Last file edited: `path/to/file.py:line_number`
- Last command run: `command here`
- Last test result: pass/fail

### Immediate Next Steps
1. First thing to do when resuming
2. Second step
3. Third step

### Uncommitted Changes
- `git status` shows: [summary]
- Ready to commit: yes/no
- If no: [what's missing]

### Context to Remember
- Important insight: [description]
- Gotcha to avoid: [description]
```

## Priority Focus / 优先关注

Focus on information that is:

1. **Hard to Rediscover** / 难以重新发现
   - Debugging insights
   - Why certain approaches failed
   - Undocumented API behaviors

2. **Time-Sensitive** / 时间敏感
   - Current state of implementation
   - Exact position in workflow

3. **Decision Context** / 决策上下文
   - Why choices were made
   - Alternatives considered

## Quality Standards / 质量标准

- Be specific: include file paths, line numbers, exact commands
- Be honest: note what's uncertain or incomplete
- Be practical: focus on actionable information
- Be timely: update before losing context

## Tips / 提示

- Run this command before long breaks
- Run before context window fills up
- Run after making significant progress
- Use with `/commit` to also save code changes
