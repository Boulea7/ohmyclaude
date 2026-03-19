"""Path constants for OhMyClaude.

This module defines all commonly used paths for Claude Code configuration.
"""

import os
from pathlib import Path

# User home directory
HOME = Path.home()

# Claude Code configuration directory
CLAUDE_DIR = HOME / ".claude"

# Claude Code settings file
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Claude Code CLAUDE.md file (user-level)
CLAUDE_MD_FILE = CLAUDE_DIR / "CLAUDE.md"

# Claude Code commands directory
COMMANDS_DIR = CLAUDE_DIR / "commands"

# Claude Code hooks directory
HOOKS_DIR = CLAUDE_DIR / "hooks"

# Claude Code agents directory (for subagent configs)
AGENTS_DIR = CLAUDE_DIR / "agents"

# Claude Code skills directory
SKILLS_DIR = CLAUDE_DIR / "skills"

# OhMyClaude configuration directory
OHMYCLAUDE_DIR = HOME / ".ohmyclaude"

# OhMyClaude backups directory
BACKUPS_DIR = OHMYCLAUDE_DIR / "backups"

# OhMyClaude providers configuration
PROVIDERS_FILE = OHMYCLAUDE_DIR / "providers.yaml"

# OhMyClaude environment file (for shell integration)
ENV_FILE = OHMYCLAUDE_DIR / "env.sh"

# Codex configuration directory
CODEX_DIR = HOME / ".codex"

# Codex auth file
CODEX_AUTH_FILE = CODEX_DIR / "auth.json"

# Gemini CLI configuration directory
GEMINI_DIR = HOME / ".gemini"


def _chmod_dir(path: Path, mode: int) -> None:
    """Best-effort chmod for directories (POSIX only)."""
    if os.name == "nt":
        return
    try:
        path.chmod(mode)
    except OSError:
        pass


def ensure_claude_dirs() -> None:
    """Ensure Claude Code directories exist."""
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    # Set restrictive permissions for POSIX systems
    _chmod_dir(CLAUDE_DIR, 0o700)
    _chmod_dir(COMMANDS_DIR, 0o700)
    _chmod_dir(HOOKS_DIR, 0o700)
    _chmod_dir(AGENTS_DIR, 0o700)
    _chmod_dir(SKILLS_DIR, 0o700)


def ensure_ohmyclaude_dirs() -> None:
    """Ensure OhMyClaude directories exist."""
    OHMYCLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    # Set restrictive permissions for POSIX systems
    _chmod_dir(OHMYCLAUDE_DIR, 0o700)
    _chmod_dir(BACKUPS_DIR, 0o700)


def get_project_templates_dir() -> Path:
    """Get the templates directory from the installed package."""
    return Path(__file__).parent.parent / "templates"


def get_presets_dir() -> Path:
    """Get the presets directory."""
    # First try package templates
    pkg_presets = get_project_templates_dir() / "presets"
    if pkg_presets.exists():
        return pkg_presets

    # Fallback to project root templates (development mode)
    # Path: src/ohmyclaude/core/paths.py -> templates/presets/
    root_presets = Path(__file__).parent.parent.parent.parent / "templates" / "presets"
    if root_presets.exists():
        return root_presets

    raise FileNotFoundError("Presets directory not found")
