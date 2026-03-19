# Release Guide

This guide covers the public release flow for OhMyClaude without relying on machine-specific paths.

## Pre-Release Checklist

### 1. Validate the repository state

```bash
git status
python3 --version
```

Confirm:

- you are in the repository root
- the working tree contains only intentional changes
- no local-only AI notes or private files are staged

### 2. Run verification

```bash
pip install -e ".[dev]"
ruff check .
python -m mypy src/ohmyclaude
pytest
```

Do not hardcode expected test counts in this guide; use the live result from the current repository.

### 3. Inspect public docs

Before release, re-check:

- `README.md`
- `README.zh-CN.md`
- `README.zh-TW.md`
- `README.ja.md`
- `CHANGELOG.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

## Build

```bash
python -m build
python -m pip install twine
twine check dist/*
```

## Local Install Smoke Test

```bash
python -m venv /tmp/test-ohmyclaude
source /tmp/test-ohmyclaude/bin/activate
pip install dist/*.whl
ohmyclaude --version
ohmyclaude --help
deactivate
rm -rf /tmp/test-ohmyclaude
```

## Publish

### 1. Push the release branch

```bash
git push origin main
```

### 2. Create and push a tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 3. Watch GitHub Actions

Check:

- `.github/workflows/test.yml`
- `.github/workflows/publish.yml`

Make sure build, test, and publish jobs complete successfully.

## Trusted Publishing

If using PyPI trusted publishing:

- repository owner and name must match PyPI configuration
- workflow name must match the PyPI publisher configuration
- environment name must match the configured GitHub environment if one is used

## Post-Release Validation

After publishing:

- verify the package page on PyPI
- verify README rendering
- verify wheel and sdist metadata
- verify installation from PyPI in a clean environment

## Safety Notes

- avoid blind `curl | bash` release validation in public docs
- if you distribute an install script, inspect it first or provide checksum / source review guidance
- never release with staged private AI notes, local indexes, or real user configuration snapshots
