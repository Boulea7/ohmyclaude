# Contributing to OhMyClaude

感谢您对 OhMyClaude 的关注！欢迎提交贡献。

## Development Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/Boulea7/ohmyclaude.git
cd ohmyclaude

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install development dependencies
pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=ohmyclaude --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_version.py -v
```

### Code Style

```bash
# Lint check
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

### Type Checking

```bash
mypy src/ohmyclaude --ignore-missing-imports
```

### Security Scan

```bash
pip install bandit[toml]
bandit -r src/ohmyclaude -c pyproject.toml
```

## Submitting Pull Requests

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Ensure tests pass: `pytest tests/ -v`
4. Ensure code style: `ruff check src/ tests/`
5. Commit changes: `git commit -m 'feat: add your feature'`
6. Push branch: `git push origin feature/your-feature`
7. Create a Pull Request

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `chore:` | Build/tool update |
| `refactor:` | Code refactoring |
| `test:` | Test update |
| `style:` | Code style (formatting) |

Examples:
```
feat: add version check command
fix: resolve provider switching error
docs: update installation guide
```

## Issue Reporting

When submitting an Issue, please include:

- Operating system and Python version
- OhMyClaude version (`omc --version`)
- Steps to reproduce
- Expected behavior vs actual behavior
- Error messages (if any)

## Code Structure

```
src/ohmyclaude/
├── cli/          # CLI commands (Click)
├── core/         # Core business logic
├── models/       # Pydantic data models
├── modules/      # Configuration modules
├── ui/           # UI components (Rich)
└── templates/    # Jinja2 templates
```

## License

Contributed code will be licensed under the MIT License.
