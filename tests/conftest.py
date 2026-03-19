"""Shared fixtures for OhMyClaude tests.

This module provides common fixtures used across unit and integration tests.
"""

import json
import os
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ohmyclaude.models.presets import PresetConfig
from ohmyclaude.models.settings import SettingsConfig

# ============================================================================
# Path Fixtures - Mock ~/.claude and ~/.ohmyclaude directories
# ============================================================================


@pytest.fixture
def temp_home(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary home directory for testing.

    This fixture patches the HOME constant in paths module to use tmp_path.
    All tests using this fixture will have isolated file system operations.
    """
    home = tmp_path / "home"
    home.mkdir()

    claude_dir = home / ".claude"
    ohmyclaude_dir = home / ".ohmyclaude"
    codex_dir = home / ".codex"
    gemini_dir = home / ".gemini"

    # Also patch the derived paths
    with (
        patch("ohmyclaude.core.paths.HOME", home),
        patch("ohmyclaude.core.paths.CLAUDE_DIR", claude_dir),
        patch("ohmyclaude.core.paths.SETTINGS_FILE", claude_dir / "settings.json"),
        patch("ohmyclaude.core.paths.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"),
        patch("ohmyclaude.core.paths.COMMANDS_DIR", claude_dir / "commands"),
        patch("ohmyclaude.core.paths.HOOKS_DIR", claude_dir / "hooks"),
        patch("ohmyclaude.core.paths.AGENTS_DIR", claude_dir / "agents"),
        patch("ohmyclaude.core.paths.SKILLS_DIR", claude_dir / "skills"),
        patch("ohmyclaude.core.paths.OHMYCLAUDE_DIR", ohmyclaude_dir),
        patch("ohmyclaude.core.paths.BACKUPS_DIR", ohmyclaude_dir / "backups"),
        patch("ohmyclaude.core.paths.CODEX_DIR", codex_dir),
        patch("ohmyclaude.core.paths.CODEX_AUTH_FILE", codex_dir / "auth.json"),
        patch("ohmyclaude.core.paths.GEMINI_DIR", gemini_dir),
    ):
        yield home


@pytest.fixture
def temp_claude_dir(temp_home: Path) -> Path:
    """Create a temporary ~/.claude directory with basic structure."""
    claude_dir = temp_home / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    (claude_dir / "commands").mkdir(exist_ok=True)
    (claude_dir / "hooks").mkdir(exist_ok=True)
    (claude_dir / "agents").mkdir(exist_ok=True)
    (claude_dir / "skills").mkdir(exist_ok=True)
    return claude_dir


@pytest.fixture
def temp_ohmyclaude_dir(temp_home: Path) -> Path:
    """Create a temporary ~/.ohmyclaude directory."""
    ohmyclaude_dir = temp_home / ".ohmyclaude"
    ohmyclaude_dir.mkdir(parents=True, exist_ok=True)
    (ohmyclaude_dir / "backups").mkdir(exist_ok=True)
    return ohmyclaude_dir


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_settings_dict() -> dict[str, Any]:
    """Return a sample settings.json structure."""
    return {
        "env": {
            "ANTHROPIC_AUTH_TOKEN": "test-token-123",
            "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        },
        "permissions": {
            "allow": ["Bash(git:*)", "Read", "Write", "Edit"],
            "deny": [],
        },
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@anthropic/mcp-filesystem"],
            }
        },
    }


@pytest.fixture
def sample_settings_file(temp_claude_dir: Path, sample_settings_dict: dict) -> Path:
    """Create a sample settings.json file."""
    settings_file = temp_claude_dir / "settings.json"
    settings_file.write_text(json.dumps(sample_settings_dict, indent=2))
    return settings_file


@pytest.fixture
def sample_preset_dict() -> dict[str, Any]:
    """Return a sample preset configuration."""
    return {
        "name": "test-preset",
        "description": "Test preset for unit tests",
        "version": "1.0.0",
        "model": "sonnet",
        "always_thinking_enabled": True,
        "claude_md_template": "general",
        "mcp_packages": ["basic"],
        "commands": ["commit", "review"],
        "agents": ["code-reviewer", "debugger"],
        "hooks_preset": "basic",
        "include_codex": False,
    }


@pytest.fixture
def sample_preset(sample_preset_dict: dict) -> PresetConfig:
    """Return a PresetConfig instance."""
    return PresetConfig(**sample_preset_dict)


# ============================================================================
# Model Fixtures
# ============================================================================


@pytest.fixture
def sample_settings_config(sample_settings_dict: dict) -> SettingsConfig:
    """Return a SettingsConfig instance."""
    return SettingsConfig(**sample_settings_dict)


# ============================================================================
# Environment Fixtures
# ============================================================================


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Temporarily clear OhMyClaude-related environment variables."""
    env_vars = [
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
        "GLM_ANTHROPIC_AUTH_TOKEN",
        "CODE88_ANTHROPIC_AUTH_TOKEN",
        "DEEPSEEK_API_KEY",
        "OHMYCLAUDE_ROOT",
    ]
    original = {k: os.environ.get(k) for k in env_vars}

    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


# ============================================================================
# Fixture Data Files
# ============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_yaml_content() -> str:
    """Return sample YAML content for testing."""
    return """
name: test-preset
description: Test preset
version: "1.0.0"
model: sonnet
mcp_packages:
  - basic
commands:
  - commit
"""


# ============================================================================
# Pytest Markers Configuration
# ============================================================================


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests that may take longer")
