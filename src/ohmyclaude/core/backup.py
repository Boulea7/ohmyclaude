"""Backup manager for OhMyClaude.

This module provides backup and restore functionality for Claude Code configurations.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from ohmyclaude.core.atomic import atomic_write
from ohmyclaude.core.paths import (
    BACKUPS_DIR,
    CLAUDE_DIR,
    COMMANDS_DIR,
    SETTINGS_FILE,
    ensure_ohmyclaude_dirs,
)

# Regex for safe backup names (alphanumeric, dash, underscore, dot)
_SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _validate_backup_name(name: str) -> str:
    """Validate backup name to prevent path traversal attacks.

    Args:
        name: Backup name to validate

    Returns:
        The validated name

    Raises:
        ValueError: If name contains unsafe characters
    """
    if not name or not _SAFE_NAME_PATTERN.match(name):
        raise ValueError(f"Invalid backup name: {name!r}")
    return name


def _resolve_backup_path(backups_dir: Path, backup_name: str) -> Path:
    """Safely resolve a backup path within the backups directory.

    Args:
        backups_dir: The base backups directory
        backup_name: Name of the backup

    Returns:
        Resolved path guaranteed to be within backups_dir

    Raises:
        ValueError: If path escapes backups_dir
    """
    safe_name = _validate_backup_name(backup_name)
    path = (backups_dir / safe_name).resolve()
    backups_dir_resolved = backups_dir.resolve()

    if not str(path).startswith(str(backups_dir_resolved)):
        raise ValueError(f"Backup path escapes backups directory: {backup_name}")

    return path


class BackupManager:
    """Manages backups of Claude Code configuration.

    This class handles:
    - Creating timestamped backups of settings.json and related files
    - Listing available backups
    - Restoring from a specific backup
    - Cleaning up old backups

    Example:
        >>> backup = BackupManager()
        >>> if backup.has_existing_config():
        ...     backup_path = backup.create_backup()
        ...     print(f"Backup created: {backup_path}")
    """

    def __init__(self, backups_dir: Path | None = None):
        """Initialize backup manager.

        Args:
            backups_dir: Custom backups directory (default: ~/.ohmyclaude/backups)
        """
        self.backups_dir = backups_dir or BACKUPS_DIR
        ensure_ohmyclaude_dirs()

    def has_existing_config(self) -> bool:
        """Check if existing Claude Code configuration exists.

        Returns:
            True if settings.json exists
        """
        return SETTINGS_FILE.exists()

    def create_backup(self, tag: str | None = None) -> Path:
        """Create a timestamped backup of current configuration.

        Args:
            tag: Optional tag to include in backup name (must be alphanumeric/dash/underscore)

        Returns:
            Path to the backup directory

        Raises:
            ValueError: If tag contains unsafe characters
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Validate tag if provided
        if tag:
            _validate_backup_name(tag)
            backup_name = f"backup-{tag}-{timestamp}"
        else:
            backup_name = f"backup-{timestamp}"

        # Use safe path resolution
        backup_path = _resolve_backup_path(self.backups_dir, backup_name)
        backup_path.mkdir(parents=True, exist_ok=True)

        # Backup settings.json
        if SETTINGS_FILE.exists():
            shutil.copy2(SETTINGS_FILE, backup_path / "settings.json")

        # Backup CLAUDE.md (user-level)
        claude_md = CLAUDE_DIR / "CLAUDE.md"
        if claude_md.exists():
            shutil.copy2(claude_md, backup_path / "CLAUDE.md")

        # Backup commands directory
        if COMMANDS_DIR.exists() and any(COMMANDS_DIR.iterdir()):
            commands_backup = backup_path / "commands"
            shutil.copytree(COMMANDS_DIR, commands_backup, dirs_exist_ok=True)

        # Create metadata
        files = [
            str(f.relative_to(backup_path))
            for f in backup_path.rglob("*")
            if f.is_file()
        ]
        metadata = {
            "timestamp": timestamp,
            "tag": tag,
            "files": files,
        }
        with atomic_write(backup_path / "metadata.json") as f:
            json.dump(metadata, f, indent=2)

        return backup_path

    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups.

        Returns:
            List of backup info dictionaries (empty list if backups_dir doesn't exist)
        """
        if not self.backups_dir.exists():
            return []

        backups = []

        for backup_dir in sorted(self.backups_dir.iterdir(), reverse=True):
            if not backup_dir.is_dir() or not backup_dir.name.startswith("backup-"):
                continue

            metadata_file = backup_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, encoding="utf-8") as f:
                        metadata = json.load(f)
                except json.JSONDecodeError:
                    metadata = {}
            else:
                metadata = {}

            backups.append({
                "name": backup_dir.name,
                "path": str(backup_dir),
                "timestamp": metadata.get("timestamp", "unknown"),
                "tag": metadata.get("tag"),
                "files": metadata.get("files", []),
            })

        return backups

    def restore_backup(self, backup_name: str, confirm: bool = True) -> bool:
        """Restore configuration from a backup.

        Args:
            backup_name: Name of the backup to restore
            confirm: Whether to create a pre-restore backup

        Returns:
            True if restore was successful

        Raises:
            FileNotFoundError: If backup doesn't exist
            ValueError: If backup_name contains unsafe characters
        """
        # Use safe path resolution to prevent path traversal
        backup_path = _resolve_backup_path(self.backups_dir, backup_name)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        # Create pre-restore backup if requested
        if confirm and self.has_existing_config():
            self.create_backup(tag="pre-restore")

        # Restore settings.json
        backup_settings = backup_path / "settings.json"
        if backup_settings.exists():
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_settings, SETTINGS_FILE)

        # Restore CLAUDE.md
        backup_claude_md = backup_path / "CLAUDE.md"
        if backup_claude_md.exists():
            shutil.copy2(backup_claude_md, CLAUDE_DIR / "CLAUDE.md")

        # Restore commands - remove existing to ensure clean state
        backup_commands = backup_path / "commands"
        if backup_commands.exists():
            if COMMANDS_DIR.exists():
                shutil.rmtree(COMMANDS_DIR)
            shutil.copytree(backup_commands, COMMANDS_DIR)

        return True

    def delete_backup(self, backup_name: str) -> bool:
        """Delete a specific backup.

        Args:
            backup_name: Name of the backup to delete

        Returns:
            True if deletion was successful

        Raises:
            ValueError: If backup_name contains unsafe characters
        """
        # Use safe path resolution to prevent path traversal
        backup_path = _resolve_backup_path(self.backups_dir, backup_name)

        if not backup_path.exists():
            return False

        shutil.rmtree(backup_path)
        return True

    def cleanup_old_backups(self, keep: int = 5) -> int:
        """Remove old backups, keeping the most recent ones.

        Args:
            keep: Number of backups to keep

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()

        if len(backups) <= keep:
            return 0

        deleted = 0
        for backup in backups[keep:]:
            if self.delete_backup(backup["name"]):
                deleted += 1

        return deleted
