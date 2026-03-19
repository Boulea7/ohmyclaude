---
name: coding-standards
description: Apply when writing or reviewing code so changes stay simple, readable, and easy to maintain. Use for new features, refactors, reviews, or anytime you need a shared KISS/DRY/YAGNI baseline.
---

# Coding Standards

## Core Principles

### KISS
- Prefer the simplest solution that fully solves the current task.
- Add abstraction only when it clearly reduces future confusion or duplication.

### DRY
- Avoid copy-pasting logic across three or more places.
- Do not create a reusable abstraction until the repeated shape is actually stable.

### YAGNI
- Do not add feature flags, extension points, or configuration knobs for hypothetical future needs.
- Build for the current requirement and refactor when the requirement becomes real.

## Implementation Checklist

1. Restate the behavior change in one sentence.
2. Keep edits focused on the smallest useful file set.
3. Validate inputs at system boundaries.
4. Prefer explicit names over clever shorthand.
5. Use early returns to reduce nesting.
6. Keep exported functions and public interfaces easy to scan.
7. Remove dead branches, stale comments, and debug leftovers before finishing.

## Review Questions

- Is this change easier to understand than the version before it?
- Did we introduce an abstraction that exists only to look reusable?
- Are errors surfaced clearly instead of being silently ignored?
- Are we preserving established project conventions where they already exist?

## Common Smells

- Functions that mix validation, business logic, and output formatting.
- Large switch statements that should become data tables or smaller helpers.
- Comments explaining obvious code instead of clarifying intent or tradeoffs.
- New utilities that are only used once.

## Output Expectation

When this skill is active, summarize:
- the main simplification choices
- any duplication intentionally left in place and why
- any follow-up cleanup worth tracking separately
