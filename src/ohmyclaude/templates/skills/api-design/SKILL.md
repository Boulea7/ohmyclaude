---
name: api-design
description: Use when designing or reviewing REST-style API endpoints, payloads, status codes, filtering, sorting, or pagination behavior.
---

# API Design

Use this skill for external or internal HTTP API design work.

## Goals

- Keep endpoints predictable and easy to document.
- Prefer stable resource naming over action-heavy URLs.
- Make response and error shapes consistent.

## Checklist

1. Identify the resource and its lifecycle.
2. Choose verbs through HTTP methods, not path names.
3. Define request validation, success response, and error response.
4. Decide pagination, filtering, and sorting only if the endpoint needs them.
5. Document compatibility constraints before changing existing wire behavior.

## Guardrails

- Do not invent versioning unless there is a real compatibility need.
- Do not add optional fields without stating defaults and omission behavior.
- For updates, prefer partial updates only when patch semantics are clear.
