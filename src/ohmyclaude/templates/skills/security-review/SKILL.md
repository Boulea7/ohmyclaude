---
name: security-review
description: Use when reviewing auth, secrets, permissions, external input handling, or any change that could introduce security regressions.
---

# Security Review

## Review Priorities

- Authentication and authorization
- Secret handling
- Input validation
- File and shell safety
- Network and third-party boundaries

## Checklist

1. Identify trust boundaries and attacker-controlled inputs.
2. Check whether permissions are broader than necessary.
3. Look for secret exposure, unsafe logging, or insecure defaults.
4. Verify validation happens before side effects.
5. Note any missing tests around critical security behavior.

## Output

- Findings ordered by severity
- Residual risks
- Recommended fixes
