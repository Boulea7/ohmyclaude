---
name: search-first
description: Use before adding a dependency, writing a new helper, or implementing a feature that may already have an existing solution.
---

# Search First

## Workflow

1. Search the current repository for existing utilities, patterns, or configs.
2. Check whether official tooling or an existing package already solves the problem.
3. Compare adoption cost, maintenance burden, and scope fit.
4. Only build custom code when existing options are clearly insufficient.

## Decision Rule

- Adopt when the fit is strong and maintenance is healthy.
- Extend when a small wrapper closes the gap.
- Build custom only when search results are a poor fit.
