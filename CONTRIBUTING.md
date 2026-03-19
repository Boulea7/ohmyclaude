# Contributing to OhMyClaude

Thanks for your interest in contributing.

## Development Setup

```bash
git clone https://github.com/Boulea7/ohmyclaude.git
cd ohmyclaude
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

### Run checks

```bash
ruff check .
python -m mypy src/ohmyclaude
pytest
```

### Before opening a PR

- keep changes focused
- update public docs when public behavior changes
- avoid committing local AI notes, private indexes, or personal environment files
- prefer temporary directories or patched paths in tests instead of real home-directory mutation

## Public vs Local Files

Public repository content should stay inside tracked surfaces such as:

- `README*.md`
- `src/`
- `templates/`
- `tests/`
- public root docs

Local-only material should stay in ignored paths, for example:

- `.ai-notes/`
- `docs/`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

## Commit Style

Use [Conventional Commits](https://www.conventionalcommits.org/) where practical.

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `chore:` | Build or tool update |
| `refactor:` | Internal code cleanup |
| `test:` | Test update |
| `style:` | Formatting-only change |

## Issue Reports

When opening an issue, include:

- operating system and Python version
- OhMyClaude version
- steps to reproduce
- expected vs actual behavior
- relevant error messages

## License

By contributing, you agree that your contributions are released under the MIT License.
