---
name: e2e-testing
description: Use when creating, reviewing, or stabilizing end-to-end tests, especially Playwright-based browser flows. Covers selector strategy, flaky test prevention, fixtures, and CI-friendly reporting.
---

# E2E Testing

## When To Use

- Adding critical user-flow coverage
- Debugging flaky browser tests
- Reviewing Playwright test structure
- Designing smoke tests for CI

## Core Rules

- Test user-visible behavior, not internal implementation.
- Prefer resilient selectors such as roles, labels, or stable `data-testid` values.
- Never rely on arbitrary sleeps when you can wait on UI state or network completion.
- Keep each test independent so retries are safe.

## Recommended Structure

1. Group tests by workflow, not by page count.
2. Extract reusable navigation/login helpers when setup repeats.
3. Keep fixtures lightweight and explicit.
4. Capture traces, screenshots, or videos on failure only.

## Flaky Test Prevention

- Wait for the actual condition you care about.
- Use locator APIs instead of brittle raw selectors.
- Avoid shared mutable state across tests.
- Quarantine known flakes instead of letting them silently erode trust.

## Review Checklist

- Are assertions tied to behavior the user would notice?
- Do selectors survive visual refactors?
- Is the test isolated from previous runs?
- Are retries masking a real product bug?

## CI Notes

- Prefer a deterministic base URL and seeded data.
- Upload failure artifacts.
- Keep the default suite small enough for pull requests, and reserve heavier scenarios for scheduled runs.

## Output Expectation

Summarize:
- flow covered
- weakest selector or timing assumption
- missing edge cases or follow-up test gaps
