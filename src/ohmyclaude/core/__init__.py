"""Core engine components for OhMyClaude.

This module provides the foundational infrastructure for safe configuration
management, credential storage, and shell environment integration.
"""

from ohmyclaude.core.atomic import atomic_write, save_json, save_text
from ohmyclaude.core.merge import deep_merge
from ohmyclaude.core.keyring import CredentialManager
from ohmyclaude.core.shell import ShellIntegration, get_shell_info

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
]
