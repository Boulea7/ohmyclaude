"""Integration tests for Installer."""

import json
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ohmyclaude.core.config import ConfigEngine
from ohmyclaude.core.installer import Installer, InstallResult
from ohmyclaude.models.presets import PresetConfig


@contextmanager
def patched_installer_paths(temp_env: dict[str, Path]):
    """Patch installer path constants into a temporary Claude directory."""
    with (
        patch("ohmyclaude.core.installer.SETTINGS_FILE", temp_env["SETTINGS_FILE"]),
        patch("ohmyclaude.core.installer.CLAUDE_DIR", temp_env["CLAUDE_DIR"]),
        patch("ohmyclaude.core.installer.COMMANDS_DIR", temp_env["COMMANDS_DIR"]),
        patch("ohmyclaude.core.installer.HOOKS_DIR", temp_env["HOOKS_DIR"]),
        patch("ohmyclaude.core.installer.AGENTS_DIR", temp_env["AGENTS_DIR"]),
        patch("ohmyclaude.core.installer.SKILLS_DIR", temp_env["SKILLS_DIR"]),
        patch("ohmyclaude.core.installer.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]),
        patch("ohmyclaude.core.installer.ensure_claude_dirs"),
    ):
        yield


class TestInstallResult:
    """Tests for InstallResult class."""

    def test_init(self):
        """Test InstallResult initialization."""
        result = InstallResult()

        assert result.installed == []
        assert result.skipped == []
        assert result.errors == []

    def test_add_installed(self):
        """Test adding installed item."""
        result = InstallResult()
        result.add_installed("settings", "settings.json", "/path/to/settings.json")

        assert len(result.installed) == 1
        assert result.installed[0]["type"] == "settings"
        assert result.installed[0]["name"] == "settings.json"

    def test_add_skipped(self):
        """Test adding skipped item."""
        result = InstallResult()
        result.add_skipped("command", "custom-cmd", "Template not found")

        assert len(result.skipped) == 1
        assert result.skipped[0]["reason"] == "Template not found"

    def test_add_error(self):
        """Test adding error."""
        result = InstallResult()
        result.add_error("hook", "custom-hook", "Permission denied")

        assert len(result.errors) == 1
        assert result.errors[0]["error"] == "Permission denied"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = InstallResult()
        result.add_installed("settings", "settings.json", "/path")
        result.add_skipped("command", "cmd", "Not found")

        data = result.to_dict()

        assert data["success"] is True
        assert data["summary"]["installed_count"] == 1
        assert data["summary"]["skipped_count"] == 1
        assert data["summary"]["error_count"] == 0

    def test_to_dict_with_errors(self):
        """Test that errors make success False."""
        result = InstallResult()
        result.add_error("settings", "settings.json", "Failed")

        data = result.to_dict()

        assert data["success"] is False
        assert data["summary"]["error_count"] == 1


class TestInstallerBasic:
    """Basic tests for Installer class."""

    @pytest.fixture
    def mock_preset(self) -> PresetConfig:
        """Create a minimal preset for testing."""
        return PresetConfig(
            name="test",
            description="Test preset",
            model="sonnet",
            always_thinking_enabled=True,
            mcp_packages=[],
            commands=[],
            hooks_preset="basic",
            agents=[],
        )

    @pytest.fixture
    def mock_engine(self) -> MagicMock:
        """Create a mock ConfigEngine."""
        engine = MagicMock(spec=ConfigEngine)
        engine.generate_settings.return_value = MagicMock(
            model_dump=lambda exclude_none: {
                "model": "sonnet",
                "alwaysThinkingEnabled": True,
                "env": {},
            }
        )
        return engine

    def test_init_with_engine(self, mock_preset, mock_engine):
        """Test Installer initialization with provided engine."""
        installer = Installer(mock_preset, mock_engine)

        assert installer.preset == mock_preset
        assert installer.engine == mock_engine

    def test_init_creates_engine(self, mock_preset):
        """Test Installer creates engine if not provided."""
        installer = Installer(mock_preset)

        assert installer.engine is not None
        assert isinstance(installer.engine, ConfigEngine)

    def test_safe_segment_valid(self, mock_preset, mock_engine):
        """Test _safe_segment with valid input."""
        installer = Installer(mock_preset, mock_engine)

        assert installer._safe_segment("valid-name", "command") == "valid-name"
        assert installer._safe_segment("test_file", "template") == "test_file"

    def test_safe_segment_invalid_empty(self, mock_preset, mock_engine):
        """Test _safe_segment rejects empty string."""
        installer = Installer(mock_preset, mock_engine)

        with pytest.raises(ValueError, match="empty value"):
            installer._safe_segment("", "command")

    def test_safe_segment_invalid_traversal(self, mock_preset, mock_engine):
        """Test _safe_segment rejects path traversal."""
        installer = Installer(mock_preset, mock_engine)

        with pytest.raises(ValueError):
            installer._safe_segment("../etc/passwd", "command")

        with pytest.raises(ValueError):
            installer._safe_segment(".hidden", "template")

        with pytest.raises(ValueError):
            installer._safe_segment("path/to/file", "agent")


class TestInstallerIntegration:
    """Integration tests for full installation flow."""

    @pytest.fixture
    def temp_env(self, tmp_path: Path):
        """Set up a temporary environment for testing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        commands_dir = claude_dir / "commands"
        hooks_dir = claude_dir / "hooks"
        agents_dir = claude_dir / "agents"
        skills_dir = claude_dir / "skills"
        claude_md_file = claude_dir / "CLAUDE.md"

        patches = {
            "CLAUDE_DIR": claude_dir,
            "SETTINGS_FILE": settings_file,
            "COMMANDS_DIR": commands_dir,
            "HOOKS_DIR": hooks_dir,
            "AGENTS_DIR": agents_dir,
            "SKILLS_DIR": skills_dir,
            "CLAUDE_MD_FILE": claude_md_file,
        }

        return patches

    def test_install_settings(self, tmp_path: Path, temp_env):
        """Test installing settings.json."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            model="sonnet",
        )

        with patched_installer_paths(temp_env):
            installer = Installer(preset)
            installer._install_settings()

            assert temp_env["SETTINGS_FILE"].exists()

            settings = json.loads(temp_env["SETTINGS_FILE"].read_text())
            assert settings["model"] == "sonnet"
            assert len(installer.result.installed) == 1
            assert installer.result.installed[0]["type"] == "settings"

    def test_install_claude_md(self, tmp_path: Path, temp_env):
        """Test installing CLAUDE.md."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            claude_md_template="general",
        )

        with patch("ohmyclaude.core.installer.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]):
            with patch("ohmyclaude.core.installer.SETTINGS_FILE", temp_env["SETTINGS_FILE"]):
                with patch("ohmyclaude.core.installer.CLAUDE_DIR", temp_env["CLAUDE_DIR"]):
                    with patch("ohmyclaude.core.installer.ensure_claude_dirs"):
                        installer = Installer(preset)
                        installer._install_claude_md()

                        # Check CLAUDE.md was created
                        assert temp_env["CLAUDE_MD_FILE"].exists()
                        content = temp_env["CLAUDE_MD_FILE"].read_text()
                        assert len(content) > 0

    def test_install_full_flow(self, tmp_path: Path, temp_env):
        """Test complete installation flow."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            model="sonnet",
            commands=[],
            hooks_preset="basic",
            agents=[],
        )

        with patched_installer_paths(temp_env):
            installer = Installer(preset)
            result = installer.install()

            assert "installed" in result
            assert "skipped" in result
            assert "errors" in result
            assert "success" in result
            assert "summary" in result
            assert result["summary"]["installed_count"] >= 2

    def test_install_skip_mcp(self, tmp_path: Path, temp_env):
        """Test installation with skip_mcp option."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
        )

        with patched_installer_paths(temp_env):
            installer = Installer(preset)
            result = installer.install(skip_mcp=True)

            assert result["success"] is True


class TestInstallerWithRealPresets:
    """Tests using real preset files."""

    @pytest.fixture
    def temp_env(self, tmp_path: Path):
        """Set up a temporary environment for testing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        return {
            "CLAUDE_DIR": claude_dir,
            "SETTINGS_FILE": claude_dir / "settings.json",
            "COMMANDS_DIR": claude_dir / "commands",
            "HOOKS_DIR": claude_dir / "hooks",
            "AGENTS_DIR": claude_dir / "agents",
            "SKILLS_DIR": claude_dir / "skills",
            "CLAUDE_MD_FILE": claude_dir / "CLAUDE.md",
        }

    def test_install_starter_preset(self, temp_env):
        """Test installing starter preset."""
        engine = ConfigEngine()
        preset = engine.load_preset("starter")

        with patched_installer_paths(temp_env):
            installer = Installer(preset, engine)
            result = installer.install()

            assert result["success"] is True
            assert temp_env["SETTINGS_FILE"].exists()

    def test_install_standard_preset(self, temp_env):
        """Test installing standard preset."""
        engine = ConfigEngine()
        preset = engine.load_preset("standard")

        with patched_installer_paths(temp_env):
            installer = Installer(preset, engine)
            result = installer.install()

            assert result["success"] is True

            if preset.commands:
                commands_exist = temp_env["COMMANDS_DIR"].exists()
                skipped = result["summary"]["skipped_count"] > 0
                assert commands_exist or skipped

            assert (temp_env["COMMANDS_DIR"] / "tdd.md").exists()
            assert (temp_env["SKILLS_DIR"] / "coding-standards" / "SKILL.md").exists()
            assert (temp_env["SKILLS_DIR"] / "tdd-workflow" / "SKILL.md").exists()

    def test_install_full_preset(self, temp_env):
        """Test installing full preset."""
        engine = ConfigEngine()
        preset = engine.load_preset("full")

        with patched_installer_paths(temp_env):
            installer = Installer(preset, engine)
            result = installer.install()

            assert result["success"] is True
            assert result["summary"]["installed_count"] >= 2
            assert (temp_env["COMMANDS_DIR"] / "worktree.md").exists()
            assert (temp_env["AGENTS_DIR"] / "security-reviewer.md").exists()
            assert (temp_env["SKILLS_DIR"] / "skill-rules.json").exists()

    def test_install_preserves_existing_curated_skill(self, temp_env):
        """Installer should not overwrite an existing user-maintained skill."""
        engine = ConfigEngine()
        preset = engine.load_preset("standard")

        existing_skill = temp_env["SKILLS_DIR"] / "coding-standards"
        existing_skill.mkdir(parents=True, exist_ok=True)
        existing_file = existing_skill / "SKILL.md"
        existing_file.write_text("custom skill\n", encoding="utf-8")

        with patched_installer_paths(temp_env):
            installer = Installer(preset, engine)
            result = installer.install()

            assert result["success"] is True
            assert existing_file.read_text(encoding="utf-8") == "custom skill\n"
            assert any(
                item["name"] == "coding-standards"
                and "preserved" in item["reason"]
                for item in result["skipped"]
            )

    def test_install_preserves_existing_skill_rules_file(self, temp_env):
        """Installer should not overwrite an existing skill-rules file."""
        engine = ConfigEngine()
        preset = engine.load_preset("full")

        skills_dir = temp_env["SKILLS_DIR"]
        skills_dir.mkdir(parents=True, exist_ok=True)
        rules_file = skills_dir / "skill-rules.json"
        rules_file.write_text("{\"custom\": true}\n", encoding="utf-8")

        with patched_installer_paths(temp_env):
            installer = Installer(preset, engine)
            result = installer.install()

            assert result["success"] is True
            assert rules_file.read_text(encoding="utf-8") == "{\"custom\": true}\n"
            assert any(
                item["name"] == "skill-rules.json"
                and "preserved" in item["reason"]
                for item in result["skipped"]
            )
