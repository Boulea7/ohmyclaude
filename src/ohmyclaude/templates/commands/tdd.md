---
description: Drive implementation with a practical RED-GREEN-REFACTOR loop
argument-hint: <behavior, bug, or target module>
---

Use the `tdd-workflow` skill to implement `$ARGUMENTS` through a focused test-first loop.

## Task / 任务

Turn the requested behavior into one failing test at a time, make it pass with the smallest code change, then refactor safely.
把用户请求转成逐步推进的测试优先流程：先写失败测试，再用最小改动让它通过，最后安全重构。

## Workflow / 流程

### 1. Define The Behavior / 明确行为
- Restate the expected outcome in one sentence
- Identify the narrowest place where that behavior can be tested

### 2. Start With RED / 先进入 RED
- Write one focused failing test
- Run the smallest relevant test command and confirm it fails for the right reason

### 3. Move To GREEN / 进入 GREEN
- Implement the minimum production change required
- Re-run the same focused test until it passes

### 4. Expand Carefully / 逐步扩展
- Add edge cases, error paths, and regressions one by one
- Keep each step small enough to explain clearly

### 5. Refactor Safely / 安全重构
- Simplify only after the behavior is protected by passing tests
- Re-run the targeted test set after every meaningful refactor

## Output / 输出

Report:
- the first failing test
- the minimal fix that made it pass
- the follow-up cases added before refactor
