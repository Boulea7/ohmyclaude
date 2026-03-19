---
name: worktree-isolation
description: Use when feature work, reviews, or parallel investigations should run in an isolated git worktree instead of the current checkout. Best for avoiding branch collisions and keeping validation reproducible.
---

# Worktree Isolation

## Goal

Create a clean, explicit workspace for risky or parallel work without disturbing the current checkout.

## When It Helps

- A feature or bug fix should not share the current branch state.
- Review or experiment work needs a throwaway branch.
- Multiple agent or human lanes need separate file trees.

## Workflow

1. Confirm the current repository state.
   - Check branch, dirty files, and whether the current checkout should remain untouched.

2. Pick an explicit destination.
   - Prefer a project-local `.worktrees/` or another clearly named sibling directory.
   - Avoid silently deleting or reusing an existing worktree.

3. Create the worktree on a dedicated branch.
   - Use a branch name that reflects the task.
   - Keep the original checkout unchanged.

4. Bootstrap the new workspace.
   - Install dependencies only inside the isolated path.
   - Run the smallest baseline validation that proves the worktree is usable.

5. Report the location and next step.
   - State the branch, path, and any setup or validation outcome.

## Safety Rules

- Never remove an existing worktree without explicit user approval.
- Never assume it is safe to move or discard uncommitted work in the current checkout.
- Keep the isolation step explicit in the final report so handoffs remain clear.

## Output Expectation

State:
- chosen branch name
- chosen worktree path
- bootstrap commands run
- baseline validation result
