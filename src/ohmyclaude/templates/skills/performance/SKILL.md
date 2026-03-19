---
name: performance
description: Use when diagnosing slowness, reducing context/tool overhead, or choosing an efficient workflow for coding agents and build pipelines.
---

# Performance

## Focus Areas

- Remove unnecessary work before optimizing code.
- Keep context surfaces small and relevant.
- Prefer targeted validation over full-suite reruns when safe.

## Checklist

1. Measure the slow path or high-cost loop.
2. Identify whether the bottleneck is I/O, build tooling, context size, or algorithmic work.
3. Reduce broad scans, redundant tool calls, and oversized payloads.
4. Verify the optimization did not change behavior.

## Guardrails

- Avoid micro-optimizations without evidence.
- Prefer changes that improve both clarity and speed.
