"""Core engine components for OhMyClaude.

This module provides the foundational infrastructure for safe configuration
management, credential storage, and shell environment integration.
"""

# Phase 1.5 - Core tools
from ohmyclaude.core.atomic import atomic_write, save_json, save_text
from ohmyclaude.core.backup import BackupManager
from ohmyclaude.core.config import ConfigEngine
from ohmyclaude.core.installer import Installer, InstallResult
from ohmyclaude.core.keyring import CredentialManager
from ohmyclaude.core.merge import deep_merge

# Phase 2 - Configuration management
from ohmyclaude.core.paths import (
    BACKUPS_DIR,
    CLAUDE_DIR,
    CLAUDE_MD_FILE,
    COMMANDS_DIR,
    GEMINI_DIR,
    HOOKS_DIR,
    OHMYCLAUDE_DIR,
    SETTINGS_FILE,
    SKILLS_DIR,
    ensure_claude_dirs,
    ensure_ohmyclaude_dirs,
)
from ohmyclaude.core.provider import ProviderSwitcher
from ohmyclaude.core.shell import ShellIntegration, get_shell_info
from ohmyclaude.core.targets import (
    HarnessBundleBuilder,
    HarnessTarget,
    InstallTransactionResult,
    RenderedBundle,
    TargetPaths,
    resolve_target_paths,
)

__all__ = [
    # Atomic file operations
    "atomic_write",
    "save_json",
    "save_text",
    # Configuration merge
    "deep_merge",
    # Credential management
    "CredentialManager",
    # Shell integration
    "ShellIntegration",
    "get_shell_info",
    # Path constants
    "CLAUDE_DIR",
    "CLAUDE_MD_FILE",
    "SETTINGS_FILE",
    "COMMANDS_DIR",
    "HOOKS_DIR",
    "SKILLS_DIR",
    "OHMYCLAUDE_DIR",
    "BACKUPS_DIR",
    "GEMINI_DIR",
    "ensure_claude_dirs",
    "ensure_ohmyclaude_dirs",
    # Configuration engine
    "ConfigEngine",
    # Backup manager
    "BackupManager",
    # Installer
    "Installer",
    "InstallResult",
    # Bundle builder
    "HarnessTarget",
    "RenderedBundle",
    "TargetPaths",
    "InstallTransactionResult",
    "HarnessBundleBuilder",
    "resolve_target_paths",
    # Provider switcher
    "ProviderSwitcher",
]
