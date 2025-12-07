"""Hybrid credential management with fallback chain.

This module provides credential storage with multiple backend support:
1. Environment variables (highest priority)
2. System keyring (macOS Keychain, Windows Credential Locker, Linux Secret Service)
3. Local file with Base64 encoding (fallback for headless environments)

SECURITY WARNING:
- The local file fallback (level 3) uses Base64 encoding ONLY for basic obfuscation.
- Base64 is NOT encryption and provides NO security guarantee.
- Anyone with file access can trivially decode stored credentials.
- For sensitive environments, always prefer system keyring (level 2) or env vars (level 1).
- The .secrets file is protected with 0600 permissions but this is defense-in-depth only.
"""

from pathlib import Path
from typing import Optional
import base64
import json
import os

import keyring
from keyring.errors import KeyringError

# Constants
SERVICE_NAME = "ohmyclaude"
SECRETS_DIR = Path.home() / ".ohmyclaude"
SECRETS_FILE = SECRETS_DIR / ".secrets"


class CredentialManager:
    """Credential manager with fallback chain.

    Retrieves credentials from the first available source:
    1. Environment variables (highest priority)
    2. System keyring (macOS Keychain, Windows Credential Locker, etc.)
    3. Local secrets file (for environments without keyring support)

    Example:
        >>> creds = CredentialManager()
        >>> token = creds.get("anthropic", env_var="ANTHROPIC_API_KEY")
        >>> creds.set("anthropic", "sk-ant-xxx")
    """

    def __init__(self, service_name: str = SERVICE_NAME):
        """Initialize credential manager.

        Args:
            service_name: Service name for keyring storage
        """
        self.service_name = service_name
        self._keyring_available: Optional[bool] = None

    @property
    def keyring_available(self) -> bool:
        """Check if system keyring is available."""
        if self._keyring_available is None:
            try:
                # Try a dummy operation to test keyring availability
                keyring.get_password(self.service_name, "__test__")
                self._keyring_available = True
            except (KeyringError, RuntimeError):
                self._keyring_available = False
        return self._keyring_available

    def get(self, key: str, env_var: Optional[str] = None) -> Optional[str]:
        """Get credential from the first available source.

        Args:
            key: Credential key/name
            env_var: Optional environment variable name to check first

        Returns:
            Credential value or None if not found
        """
        # 1. Environment variable (highest priority)
        if env_var:
            value = os.environ.get(env_var)
            if value:
                return value

        # 2. System keyring
        if self.keyring_available:
            try:
                value = keyring.get_password(self.service_name, key)
                if value:
                    return value
            except KeyringError:
                pass

        # 3. Local secrets file
        return self._get_from_file(key)

    def set(self, key: str, value: str, use_keyring: bool = True) -> bool:
        """Store credential in the best available backend.

        Args:
            key: Credential key/name
            value: Credential value
            use_keyring: Whether to try system keyring first

        Returns:
            True if stored successfully
        """
        if use_keyring and self.keyring_available:
            try:
                keyring.set_password(self.service_name, key, value)
                return True
            except KeyringError:
                pass

        # Fallback to local file
        return self._set_to_file(key, value)

    def delete(self, key: str) -> bool:
        """Delete credential from all backends.

        Args:
            key: Credential key/name

        Returns:
            True if deleted from at least one backend
        """
        deleted = False

        # Try keyring
        if self.keyring_available:
            try:
                keyring.delete_password(self.service_name, key)
                deleted = True
            except KeyringError:
                pass

        # Try local file
        if self._delete_from_file(key):
            deleted = True

        return deleted

    def list_keys(self) -> list[str]:
        """List all stored credential keys.

        Returns:
            List of credential keys from local file
        """
        secrets = self._load_secrets_file()
        return list(secrets.keys())

    def _get_from_file(self, key: str) -> Optional[str]:
        """Read credential from local secrets file.

        Args:
            key: Credential key

        Returns:
            Credential value or None
        """
        secrets = self._load_secrets_file()
        encoded = secrets.get(key)
        if encoded:
            try:
                return base64.b64decode(encoded).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                return None
        return None

    def _set_to_file(self, key: str, value: str) -> bool:
        """Write credential to local secrets file.

        WARNING: This method uses Base64 encoding which provides NO security.
        It is only a fallback for environments without system keyring support.
        Prefer system keyring or environment variables for sensitive credentials.

        Args:
            key: Credential key
            value: Credential value

        Returns:
            True if stored successfully
        """
        try:
            secrets = self._load_secrets_file()
            # Base64 encode for basic obfuscation (NOT encryption - see module docstring)
            secrets[key] = base64.b64encode(value.encode("utf-8")).decode("ascii")
            self._save_secrets_file(secrets)
            return True
        except (OSError, ValueError):
            return False

    def _delete_from_file(self, key: str) -> bool:
        """Delete credential from local secrets file.

        Args:
            key: Credential key

        Returns:
            True if key was deleted
        """
        secrets = self._load_secrets_file()
        if key in secrets:
            del secrets[key]
            self._save_secrets_file(secrets)
            return True
        return False

    def _load_secrets_file(self) -> dict:
        """Load secrets from local file.

        Returns:
            Dictionary of secrets
        """
        if not SECRETS_FILE.exists():
            return {}
        try:
            data = json.loads(SECRETS_FILE.read_text())
            # Ensure we always return a dict
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_secrets_file(self, secrets: dict) -> None:
        """Save secrets to local file with atomic write.

        Args:
            secrets: Dictionary of secrets
        """
        from ohmyclaude.core.atomic import atomic_write

        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions on directory
        try:
            SECRETS_DIR.chmod(0o700)
        except OSError:
            pass

        # Atomic write to prevent corruption
        content = json.dumps(secrets, indent=2)
        with atomic_write(SECRETS_FILE, mode="w", encoding="utf-8") as f:
            f.write(content)

        # Set restrictive permissions on file (owner read/write only)
        try:
            SECRETS_FILE.chmod(0o600)
        except OSError:
            pass
