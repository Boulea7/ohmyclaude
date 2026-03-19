---
name: tdd-workflow
description: Use when implementing or fixing behavior with testable logic. Follows a practical RED-GREEN-REFACTOR loop for backend logic, utilities, render logic, CLI behavior, and regression fixes.
---

# TDD Workflow

## Goal

Drive changes from behavior instead of intuition. Prefer one failing test at a time, then the smallest implementation that makes it pass.

## RED-GREEN-REFACTOR

1. **Understand the behavior**
   - Define what should happen.
   - Name the scenario in user-facing terms, not implementation terms.

2. **Write a failing test**
   - Start with the simplest case that proves the behavior matters.
   - Run the test and confirm it fails for the expected reason.

3. **Write the minimum code**
   - Change only what is needed to make that test pass.
   - Avoid speculative cleanup during the first green pass.

4. **Run the focused test again**
   - Confirm it passes.
   - If it still fails, fix the production code before broadening scope.

5. **Add the next case**
   - Cover edge cases, error paths, and regression scenarios one by one.

6. **Refactor with tests green**
   - Simplify naming, extraction, and structure only after behavior is protected.

## What To Test

- Happy path behavior
- Boundary conditions
- Error handling
- Regression cases from the bug report or review finding

## What Not To Test

- Framework internals
- Third-party library behavior
- Private implementation details with no user-visible effect

## Useful Patterns

- Prefer descriptive test names like `should ... when ...`.
- Keep fixtures minimal and local to the test module when possible.
- Use narrow test runs first, then the broader suite before finishing.

## Output Expectation

Report:
- which test failed first
- what minimal change made it pass
- what additional edge cases were added before refactor
