"""Integration tests for CLI commands."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ohmyclaude.cli.main import cli
from ohmyclaude.models.provider import SwitchResult


class TestCLIBasic:
    """Basic CLI tests."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_cli_version(self, runner):
        """Test --version option."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "ohmyclaude" in result.output.lower() or "version" in result.output.lower()

    def test_cli_help(self, runner):
        """Test --help option."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "OhMyClaude" in result.output or "ohmyclaude" in result.output
        assert "setup" in result.output
        assert "doctor" in result.output
        assert "switch" in result.output

    def test_cli_no_args(self, runner):
        """Test CLI with no arguments shows usage."""
        result = runner.invoke(cli, [])

        # Click group without args shows help/usage and exits with code 0 or 2
        # Code 2 is standard Click behavior for missing required command
        assert result.exit_code in (0, 2), f"Unexpected exit code: {result.exit_code}"
        assert "Usage:" in result.output or "ohmyclaude" in result.output.lower()


class TestSetupCommand:
    """Tests for setup command."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_env(self, tmp_path: Path):
        """Set up a temporary environment."""
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

    def test_setup_help(self, runner):
        """Test setup --help."""
        result = runner.invoke(cli, ["setup", "--help"])

        assert result.exit_code == 0
        assert "--preset" in result.output or "-p" in result.output
        assert "starter" in result.output
        assert "standard" in result.output
        assert "full" in result.output

    def test_setup_with_preset_starter(self, runner, temp_env):
        """Test setup with starter preset."""
        with (
            patch("ohmyclaude.cli.main.SETTINGS_FILE", temp_env["SETTINGS_FILE"]),
            patch("ohmyclaude.cli.main.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]),
            patch("ohmyclaude.cli.main.COMMANDS_DIR", temp_env["COMMANDS_DIR"]),
            patch("ohmyclaude.cli.main.HOOKS_DIR", temp_env["HOOKS_DIR"]),
            patch("ohmyclaude.cli.main.SKILLS_DIR", temp_env["SKILLS_DIR"]),
            patch("ohmyclaude.core.installer.SETTINGS_FILE", temp_env["SETTINGS_FILE"]),
            patch("ohmyclaude.core.installer.CLAUDE_DIR", temp_env["CLAUDE_DIR"]),
            patch("ohmyclaude.core.installer.COMMANDS_DIR", temp_env["COMMANDS_DIR"]),
            patch("ohmyclaude.core.installer.HOOKS_DIR", temp_env["HOOKS_DIR"]),
            patch("ohmyclaude.core.installer.AGENTS_DIR", temp_env["AGENTS_DIR"]),
            patch("ohmyclaude.core.installer.SKILLS_DIR", temp_env["SKILLS_DIR"]),
            patch("ohmyclaude.core.installer.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]),
            patch("ohmyclaude.core.installer.ensure_claude_dirs"),
            patch("ohmyclaude.core.backup.SETTINGS_FILE", temp_env["SETTINGS_FILE"]),
        ):
            result = runner.invoke(cli, ["setup", "-p", "starter"])

            # Should complete successfully
            assert result.exit_code == 0, (f"Setup failed: {result.output}")

            # "Errors" is a table header; check for actual failures instead.
            assert "Configuration complete" in result.output


class TestDoctorCommand:
    """Tests for doctor command."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_env(self, tmp_path: Path):
        """Set up a temporary environment."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        return {
            "CLAUDE_DIR": claude_dir,
            "SETTINGS_FILE": claude_dir / "settings.json",
            "COMMANDS_DIR": claude_dir / "commands",
            "HOOKS_DIR": claude_dir / "hooks",
            "SKILLS_DIR": claude_dir / "skills",
            "CLAUDE_MD_FILE": claude_dir / "CLAUDE.md",
        }

    def test_doctor_help(self, runner):
        """Test doctor --help."""
        result = runner.invoke(cli, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "health" in result.output.lower() or "check" in result.output.lower()

    def test_doctor_no_config(self, runner, temp_env):
        """Test doctor when no config exists."""
        with patch("ohmyclaude.cli.main.SETTINGS_FILE", temp_env["SETTINGS_FILE"]):
            with patch("ohmyclaude.cli.main.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]):
                with patch("ohmyclaude.cli.main.COMMANDS_DIR", temp_env["COMMANDS_DIR"]):
                    with patch("ohmyclaude.cli.main.HOOKS_DIR", temp_env["HOOKS_DIR"]):
                        with patch("ohmyclaude.cli.main.SKILLS_DIR", temp_env["SKILLS_DIR"]):
                            with patch("ohmyclaude.cli.main.ShellIntegration") as mock_shell:
                                mock_shell.return_value.is_installed.return_value = False
                                mock_shell.return_value.shell = "zsh"
                                mock_shell.return_value.rc_path = Path("~/.zshrc")

                                # Mock BackupManager
                                with patch("ohmyclaude.cli.main.BackupManager") as mock_backup:
                                    mock_backup.return_value.list_backups.return_value = []

                                    result = runner.invoke(cli, ["doctor"])

                                    assert result.exit_code == 0
                                    assert (
                                        "Missing" in result.output
                                        or "Not configured" in result.output
                                    )

    def test_doctor_with_config(self, runner, temp_env):
        """Test doctor when config exists."""
        # Create settings.json
        temp_env["SETTINGS_FILE"].write_text('{"model": "sonnet"}')
        temp_env["CLAUDE_MD_FILE"].write_text("# CLAUDE.md")
        temp_env["COMMANDS_DIR"].mkdir()
        (temp_env["COMMANDS_DIR"] / "test.md").write_text("test")

        with patch("ohmyclaude.cli.main.SETTINGS_FILE", temp_env["SETTINGS_FILE"]):
            with patch("ohmyclaude.cli.main.CLAUDE_MD_FILE", temp_env["CLAUDE_MD_FILE"]):
                with patch("ohmyclaude.cli.main.COMMANDS_DIR", temp_env["COMMANDS_DIR"]):
                    with patch("ohmyclaude.cli.main.HOOKS_DIR", temp_env["HOOKS_DIR"]):
                        with patch("ohmyclaude.cli.main.SKILLS_DIR", temp_env["SKILLS_DIR"]):
                            with patch("ohmyclaude.cli.main.ShellIntegration") as mock_shell:
                                mock_shell.return_value.is_installed.return_value = True
                                mock_shell.return_value.shell = "zsh"
                                mock_shell.return_value.rc_path = Path("~/.zshrc")

                                with patch("ohmyclaude.cli.main.BackupManager") as mock_backup:
                                    mock_backup.return_value.list_backups.return_value = []

                                    result = runner.invoke(cli, ["doctor"])

                                    assert result.exit_code == 0
                                    assert "OK" in result.output


class TestSwitchCommand:
    """Tests for switch command."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_switch_help(self, runner):
        """Test switch --help."""
        result = runner.invoke(cli, ["switch", "--help"])

        assert result.exit_code == 0
        assert "--token" in result.output or "-t" in result.output
        assert "--list" in result.output or "-l" in result.output

    def test_switch_list(self, runner, tmp_path: Path):
        """Test switch --list."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                result = runner.invoke(cli, ["switch", "--list"])

                assert result.exit_code == 0
                # Should show provider names
                assert "official" in result.output.lower() or "glm" in result.output.lower()

    def test_switch_defaults_to_not_touch_codex(self, runner):
        """Switch should skip Codex auth updates unless explicitly requested."""
        with patch("ohmyclaude.core.provider.ProviderSwitcher.switch") as mock_switch:
            mock_switch.return_value = SwitchResult(success=True, provider_name="official")

            result = runner.invoke(cli, ["switch", "official"])

            assert result.exit_code == 0
            assert mock_switch.call_args.kwargs["skip_codex"] is True
            assert "not touched" in result.output.lower()

    def test_switch_can_opt_in_to_codex_sync(self, runner):
        """Switch should pass skip_codex=False only with explicit opt-in."""
        with patch("ohmyclaude.core.provider.ProviderSwitcher.switch") as mock_switch:
            mock_switch.return_value = SwitchResult(
                success=True,
                provider_name="glm",
                codex_updated=True,
            )

            result = runner.invoke(cli, ["switch", "glm", "--sync-codex-auth"])

            assert result.exit_code == 0
            assert mock_switch.call_args.kwargs["skip_codex"] is False
            assert "codex auth.json updated" in result.output.lower()


class TestProviderCommand:
    """Tests for provider subcommand group."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_provider_help(self, runner):
        """Test provider --help."""
        result = runner.invoke(cli, ["provider", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output
        assert "add" in result.output
        assert "show" in result.output

    def test_provider_list(self, runner, tmp_path: Path):
        """Test provider list."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                result = runner.invoke(cli, ["provider", "list"])

                assert result.exit_code == 0

    def test_provider_show(self, runner, tmp_path: Path):
        """Test provider show."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text('{"env": {"_OHMYCLAUDE_PROVIDER": "official"}}')

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                result = runner.invoke(cli, ["provider", "show"])

                assert result.exit_code == 0
                assert "official" in result.output.lower()

    def test_provider_add_help(self, runner):
        """Test provider add --help."""
        result = runner.invoke(cli, ["provider", "add", "--help"])

        assert result.exit_code == 0
        assert "--base-url" in result.output
        assert "--token-env" in result.output


class TestInitCommand:
    """Tests for init command."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_init_help(self, runner):
        """Test init --help."""
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "--remove" in result.output
        assert "--status" in result.output

    def test_init_status(self, runner):
        """Test init --status."""
        with patch("ohmyclaude.core.shell.ShellIntegration") as mock_shell:
            mock_shell.return_value.is_installed.return_value = False
            mock_shell.return_value.shell = "zsh"
            mock_shell.return_value.rc_path = Path("~/.zshrc")

            with patch("ohmyclaude.core.get_shell_info") as mock_info:
                mock_info.return_value = {
                    "shell": "zsh",
                    "rc_path": "~/.zshrc",
                    "is_installed": False,
                }

                result = runner.invoke(cli, ["init", "--status"])

                assert result.exit_code == 0
                assert "zsh" in result.output.lower()


class TestExportImportCommands:
    """Tests for export and import commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_export_help(self, runner):
        """Test export --help."""
        result = runner.invoke(cli, ["export", "--help"])

        assert result.exit_code == 0

    def test_import_help(self, runner):
        """Test import --help."""
        result = runner.invoke(cli, ["import", "--help"])

        assert result.exit_code == 0

    def test_export_no_config(self, runner, tmp_path: Path):
        """Test export when no config exists."""
        settings_file = tmp_path / ".claude" / "settings.json"

        with patch("ohmyclaude.cli.main.SETTINGS_FILE", settings_file):
            output_file = tmp_path / "export.tar.gz"
            result = runner.invoke(cli, ["export", str(output_file)])

            assert result.exit_code == 1
            assert "No configuration found" in result.output


class TestTargetBundles:
    """Tests for explicit render/install target commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_render_codex_project_bundle(self, runner, tmp_path: Path):
        """Render should write Codex project assets into the chosen directory."""
        output_dir = tmp_path / "codex-project"

        result = runner.invoke(
            cli,
            [
                "render",
                "--target",
                "codex-project",
                "--preset",
                "standard",
                "--output",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0, result.output
        assert (output_dir / "AGENTS.md").exists()
        assert (output_dir / ".codex" / "config.toml").exists()
        assert (output_dir / ".agents" / "skills").exists()

    def test_install_requires_confirm(self, runner, tmp_path: Path):
        """Install should refuse explicit writes without the confirmation flag."""
        dest_dir = tmp_path / "gemini-extension"

        result = runner.invoke(
            cli,
            ["install", "--target", "gemini-extension", "--dest", str(dest_dir)],
        )

        assert result.exit_code == 1
        assert "--confirm" in result.output

    def test_install_gemini_extension_bundle(self, runner, tmp_path: Path):
        """Install should write a Gemini extension bundle into an explicit destination."""
        dest_dir = tmp_path / "gemini-extension"

        result = runner.invoke(
            cli,
            [
                "install",
                "--target",
                "gemini-extension",
                "--preset",
                "starter",
                "--dest",
                str(dest_dir),
                "--confirm",
                "--backup",
            ],
        )

        assert result.exit_code == 0, result.output
        assert (dest_dir / "gemini-extension.json").exists()
        assert (dest_dir / "GEMINI.md").exists()
        assert (dest_dir / "commands").exists()

    def test_render_refuses_real_home_target(self, runner, tmp_path: Path):
        """Render should refuse writes into real harness home directories."""
        real_home = tmp_path / "home"
        real_home.mkdir()

        with patch("ohmyclaude.cli.main.Path.home", return_value=real_home):
            result = runner.invoke(
                cli,
                [
                    "render",
                    "--target",
                    "claude-home",
                    "--preset",
                    "starter",
                    "--output",
                    str(real_home / ".claude"),
                ],
            )

        assert result.exit_code == 1
        assert "real harness home" in result.output.lower()

    def test_doctor_codex_project_target(self, runner, tmp_path: Path):
        """Doctor should inspect project-scoped Codex assets at an explicit path."""
        (tmp_path / "AGENTS.md").write_text("# Test AGENTS\n", encoding="utf-8")
        (tmp_path / ".codex" / "agents").mkdir(parents=True)
        (tmp_path / ".codex" / "config.toml").write_text("approval_policy = \"on-request\"\n")
        (tmp_path / ".agents" / "skills" / "search-first").mkdir(parents=True)
        (tmp_path / ".agents" / "skills" / "search-first" / "SKILL.md").write_text(
            "---\nname: search-first\ndescription: test\n---\n",
            encoding="utf-8",
        )

        result = runner.invoke(
            cli,
            ["doctor", "--target", "codex-project", "--path", str(tmp_path)],
        )

        assert result.exit_code == 0, result.output
        assert "codex-project: AGENTS.md" in result.output
        assert "OK" in result.output


class TestUpdateCommand:
    """Tests for update command."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_update_help(self, runner):
        """Test update --help."""
        result = runner.invoke(cli, ["update", "--help"])

        assert result.exit_code == 0
        assert "--check" in result.output

    def test_update_shows_version_info(self, runner):
        """Test update command shows version info."""
        result = runner.invoke(cli, ["update"])

        assert result.exit_code == 0
        # Should show checking message and version info (or network error)
        assert "checking for updates" in result.output.lower()
