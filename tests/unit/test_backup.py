"""Unit tests for backup manager."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from ohmyclaude.core.backup import BackupManager


class TestBackupManager:
    """Tests for BackupManager class."""

    @pytest.fixture
    def backup_manager(self, tmp_path: Path) -> BackupManager:
        """Create a BackupManager with temporary directories."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        # Also create claude dir
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        with patch("ohmyclaude.core.backup.BACKUPS_DIR", backups_dir):
            with patch("ohmyclaude.core.backup.CLAUDE_DIR", claude_dir):
                with patch("ohmyclaude.core.backup.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"):
                    with patch(
                        "ohmyclaude.core.backup.SETTINGS_FILE",
                        claude_dir / "settings.json",
                    ):
                        with patch("ohmyclaude.core.backup.COMMANDS_DIR", claude_dir / "commands"):
                            with patch("ohmyclaude.core.backup.HOOKS_DIR", claude_dir / "hooks"):
                                with patch(
                                    "ohmyclaude.core.backup.AGENTS_DIR",
                                    claude_dir / "agents",
                                ):
                                    with patch(
                                        "ohmyclaude.core.backup.SKILLS_DIR",
                                        claude_dir / "skills",
                                    ):
                                        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                                            yield BackupManager(backups_dir)

    @pytest.fixture
    def setup_config(self, tmp_path: Path):
        """Set up a mock Claude config."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(exist_ok=True)

        # Create settings.json
        settings_file = claude_dir / "settings.json"
        settings_file.write_text('{"model": "sonnet"}')

        # Create CLAUDE.md
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# CLAUDE.md content")

        # Create commands directory
        commands_dir = claude_dir / "commands"
        commands_dir.mkdir()
        (commands_dir / "test.md").write_text("test command")

        return claude_dir

    def test_init_default_backups_dir(self, tmp_path: Path):
        """Test BackupManager initialization with default directory."""
        with patch("ohmyclaude.core.backup.BACKUPS_DIR", tmp_path / "backups"):
            with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                manager = BackupManager()
                assert manager.backups_dir == tmp_path / "backups"

    def test_init_custom_backups_dir(self, tmp_path: Path):
        """Test BackupManager initialization with custom directory."""
        custom_dir = tmp_path / "custom_backups"
        custom_dir.mkdir()

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(custom_dir)
            assert manager.backups_dir == custom_dir

    def test_has_existing_config_true(self, tmp_path: Path):
        """Test has_existing_config when config exists."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.backup.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                manager = BackupManager(tmp_path)
                assert manager.has_existing_config() is True

    def test_has_existing_config_false(self, tmp_path: Path):
        """Test has_existing_config when config doesn't exist."""
        settings_file = tmp_path / "settings.json"

        with patch("ohmyclaude.core.backup.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                manager = BackupManager(tmp_path)
                assert manager.has_existing_config() is False

    def test_create_backup_basic(self, tmp_path: Path):
        """Test creating a basic backup."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        settings_file.write_text('{"model": "sonnet"}')

        with patch("ohmyclaude.core.backup.BACKUPS_DIR", backups_dir):
            with patch("ohmyclaude.core.backup.CLAUDE_DIR", claude_dir):
                with patch("ohmyclaude.core.backup.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"):
                    with patch("ohmyclaude.core.backup.SETTINGS_FILE", settings_file):
                        with patch("ohmyclaude.core.backup.COMMANDS_DIR", claude_dir / "commands"):
                            with patch("ohmyclaude.core.backup.HOOKS_DIR", claude_dir / "hooks"):
                                with patch(
                                    "ohmyclaude.core.backup.AGENTS_DIR",
                                    claude_dir / "agents",
                                ):
                                    with patch(
                                        "ohmyclaude.core.backup.SKILLS_DIR",
                                        claude_dir / "skills",
                                    ):
                                        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                                            manager = BackupManager(backups_dir)
                                            backup_path = manager.create_backup()

                                            assert backup_path.exists()
                                            assert (backup_path / "settings.json").exists()
                                            assert (backup_path / "metadata.json").exists()

    def test_create_backup_with_tag(self, tmp_path: Path):
        """Test creating a backup with a tag."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.backup.BACKUPS_DIR", backups_dir):
            with patch("ohmyclaude.core.backup.CLAUDE_DIR", claude_dir):
                with patch("ohmyclaude.core.backup.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"):
                    with patch("ohmyclaude.core.backup.SETTINGS_FILE", settings_file):
                        with patch("ohmyclaude.core.backup.COMMANDS_DIR", claude_dir / "commands"):
                            with patch("ohmyclaude.core.backup.HOOKS_DIR", claude_dir / "hooks"):
                                with patch(
                                    "ohmyclaude.core.backup.AGENTS_DIR",
                                    claude_dir / "agents",
                                ):
                                    with patch(
                                        "ohmyclaude.core.backup.SKILLS_DIR",
                                        claude_dir / "skills",
                                    ):
                                        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                                            manager = BackupManager(backups_dir)
                                            backup_path = manager.create_backup(tag="pre-install")

                                            assert "pre-install" in backup_path.name

    def test_create_backup_with_commands(self, tmp_path: Path):
        """Test creating backup that includes commands directory."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        settings_file.write_text("{}")

        commands_dir = claude_dir / "commands"
        commands_dir.mkdir()
        (commands_dir / "test.md").write_text("test")

        with patch("ohmyclaude.core.backup.BACKUPS_DIR", backups_dir):
            with patch("ohmyclaude.core.backup.CLAUDE_DIR", claude_dir):
                with patch("ohmyclaude.core.backup.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"):
                    with patch("ohmyclaude.core.backup.SETTINGS_FILE", settings_file):
                        with patch("ohmyclaude.core.backup.COMMANDS_DIR", commands_dir):
                            with patch("ohmyclaude.core.backup.HOOKS_DIR", claude_dir / "hooks"):
                                with patch(
                                    "ohmyclaude.core.backup.AGENTS_DIR",
                                    claude_dir / "agents",
                                ):
                                    with patch(
                                        "ohmyclaude.core.backup.SKILLS_DIR",
                                        claude_dir / "skills",
                                    ):
                                        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                                            manager = BackupManager(backups_dir)
                                            backup_path = manager.create_backup()

                                            assert (backup_path / "commands" / "test.md").exists()

    def test_list_backups_empty(self, tmp_path: Path):
        """Test listing backups when none exist."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            backups = manager.list_backups()

            assert backups == []

    def test_list_backups_with_backups(self, tmp_path: Path):
        """Test listing backups when backups exist."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        # Create a mock backup
        backup1 = backups_dir / "backup-20241207-120000"
        backup1.mkdir()
        (backup1 / "metadata.json").write_text(
            '{"timestamp": "20241207-120000", "tag": null, "files": []}'
        )

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            backups = manager.list_backups()

            assert len(backups) == 1
            assert backups[0]["name"] == "backup-20241207-120000"
            assert backups[0]["timestamp"] == "20241207-120000"

    def test_list_backups_sorted_by_time(self, tmp_path: Path):
        """Test that backups are sorted newest first."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        # Create multiple backups
        for ts in ["20241201-100000", "20241207-100000", "20241204-100000"]:
            backup = backups_dir / f"backup-{ts}"
            backup.mkdir()
            (backup / "metadata.json").write_text(f'{{"timestamp": "{ts}"}}')

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            backups = manager.list_backups()

            timestamps = [b["timestamp"] for b in backups]
            assert timestamps == ["20241207-100000", "20241204-100000", "20241201-100000"]

    def test_delete_backup_success(self, tmp_path: Path):
        """Test deleting a backup successfully."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        backup = backups_dir / "backup-20241207-120000"
        backup.mkdir()
        (backup / "settings.json").write_text("{}")

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            result = manager.delete_backup("backup-20241207-120000")

            assert result is True
            assert not backup.exists()

    def test_delete_backup_not_found(self, tmp_path: Path):
        """Test deleting a backup that doesn't exist."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            result = manager.delete_backup("nonexistent")

            assert result is False

    def test_cleanup_old_backups(self, tmp_path: Path):
        """Test cleaning up old backups."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        # Create 7 backups
        for i in range(7):
            backup = backups_dir / f"backup-2024120{i}-100000"
            backup.mkdir()
            (backup / "metadata.json").write_text(f'{{"timestamp": "2024120{i}-100000"}}')

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            deleted = manager.cleanup_old_backups(keep=5)

            assert deleted == 2
            remaining = manager.list_backups()
            assert len(remaining) == 5

    def test_cleanup_old_backups_nothing_to_delete(self, tmp_path: Path):
        """Test cleanup when fewer backups than keep limit."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        # Create 3 backups
        for i in range(3):
            backup = backups_dir / f"backup-2024120{i}-100000"
            backup.mkdir()
            (backup / "metadata.json").write_text("{}")

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)
            deleted = manager.cleanup_old_backups(keep=5)

            assert deleted == 0

    def test_restore_backup_success(self, tmp_path: Path):
        """Test restoring from a backup successfully."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Create backup
        backup = backups_dir / "backup-20241207-120000"
        backup.mkdir()
        (backup / "settings.json").write_text('{"restored": true}')

        with patch("ohmyclaude.core.backup.BACKUPS_DIR", backups_dir):
            with patch("ohmyclaude.core.backup.CLAUDE_DIR", claude_dir):
                with patch("ohmyclaude.core.backup.CLAUDE_MD_FILE", claude_dir / "CLAUDE.md"):
                    with patch(
                        "ohmyclaude.core.backup.SETTINGS_FILE",
                        claude_dir / "settings.json",
                    ):
                        with patch("ohmyclaude.core.backup.COMMANDS_DIR", claude_dir / "commands"):
                            with patch("ohmyclaude.core.backup.HOOKS_DIR", claude_dir / "hooks"):
                                with patch(
                                    "ohmyclaude.core.backup.AGENTS_DIR",
                                    claude_dir / "agents",
                                ):
                                    with patch(
                                        "ohmyclaude.core.backup.SKILLS_DIR",
                                        claude_dir / "skills",
                                    ):
                                        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
                                            manager = BackupManager(backups_dir)
                                            result = manager.restore_backup(
                                                "backup-20241207-120000",
                                                confirm=False,
                                            )

                                            assert result is True
                                            restored_settings = claude_dir / "settings.json"
                                            assert restored_settings.exists()
                                            assert json.loads(
                                                restored_settings.read_text()
                                            )["restored"] is True

    def test_restore_backup_not_found(self, tmp_path: Path):
        """Test restore raises error for nonexistent backup."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        with patch("ohmyclaude.core.backup.ensure_ohmyclaude_dirs"):
            manager = BackupManager(backups_dir)

            with pytest.raises(FileNotFoundError):
                manager.restore_backup("nonexistent")
