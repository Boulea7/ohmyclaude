---
description: Create an isolated git worktree before risky or parallel work
argument-hint: <branch name or task description>
---

Use the `worktree-isolation` skill to create an explicit isolated workspace for `$ARGUMENTS`.

## Task / 任务

Set up a dedicated git worktree so the requested work does not collide with the current checkout.
为当前任务创建一个显式的独立 git worktree，避免和现有 checkout 相互影响。

## Workflow / 流程

### 1. Inspect Current State / 检查当前状态
- Check branch, dirty files, and whether the current checkout must remain untouched

### 2. Choose Isolation Path / 选择隔离路径
- Prefer a clearly named project-local or sibling worktree directory
- Do not silently reuse or delete existing worktrees

### 3. Create The Worktree / 创建 worktree
- Use a dedicated branch
- Keep the original checkout unchanged

### 4. Bootstrap The Workspace / 初始化新工作区
- Run the minimum dependency or environment setup required for this repo
- Run a baseline validation command if it is cheap and useful

### 5. Hand Off Clearly / 明确交接
- Report the new branch, path, and readiness state before implementation continues
