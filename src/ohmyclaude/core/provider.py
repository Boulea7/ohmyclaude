"""API provider switching engine.

This module implements the core logic for switching between API providers,
including backup management, settings update, and Codex auth synchronization.
"""

import json
import os
import re
import shutil
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

from ohmyclaude.core.atomic import save_json
from ohmyclaude.core.paths import (
    CODEX_AUTH_FILE,
    PROVIDERS_FILE,
    SETTINGS_FILE,
    ensure_ohmyclaude_dirs,
)
from ohmyclaude.models.provider import ProviderConfig, SwitchResult
from ohmyclaude.modules.provider import (
    BUILTIN_PROVIDERS,
    get_cleanup_keys,
)

BACKUP_SUFFIX_FMT = "%Y%m%d-%H%M%S"

# Security: Allowed URL schemes
ALLOWED_URL_SCHEMES = frozenset({"https", "http"})
LOCALHOST_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def _validate_api_url(url: str) -> str:
    """Validate an API base URL for security.

    Args:
        url: URL to validate

    Returns:
        The validated URL

    Raises:
        ValueError: If the URL is invalid or potentially dangerous
    """
    if not url:
        raise ValueError("URL cannot be empty")

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}")

    # Check scheme
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        raise ValueError(f"Invalid URL scheme '{parsed.scheme}': only HTTPS/HTTP allowed")

    # HTTP only allowed for localhost
    if parsed.scheme == "http" and parsed.hostname not in LOCALHOST_HOSTS:
        raise ValueError(f"HTTP only allowed for localhost, not '{parsed.hostname}'")

    # Must have a host
    if not parsed.hostname:
        raise ValueError("URL must have a hostname")

    # Check for suspicious patterns
    suspicious = ["<", ">", '"', "'", "{", "}", "|", "^", "`"]
    for char in suspicious:
        if char in url:
            raise ValueError(f"URL contains suspicious character: '{char}'")

    return url


def _validate_api_token(token: str) -> str:
    """Validate an API token format for security.

    Args:
        token: Token to validate

    Returns:
        The validated token

    Raises:
        ValueError: If the token format is invalid
    """
    if not token:
        raise ValueError("Token cannot be empty")

    # Length check
    if len(token) < 20:
        raise ValueError("Token too short (minimum 20 characters)")

    if len(token) > 500:
        raise ValueError("Token too long (maximum 500 characters)")

    # Check for whitespace
    if token != token.strip():
        raise ValueError("Token cannot have leading/trailing whitespace")

    # Must be alphanumeric with allowed special chars
    if not re.match(r"^[a-zA-Z0-9_.-]+$", token):
        raise ValueError("Token contains invalid characters")

    return token


class ProviderSwitcher:
    """API provider switching engine.

    Handles switching between different API providers by:
    1. Backing up current configuration
    2. Updating settings.json env section
    3. Optionally updating Codex auth.json

    Example:
        >>> switcher = ProviderSwitcher()
        >>> result = switcher.switch("glm")
        >>> print(f"Switched to: {result.provider_name}")
    """

    def __init__(self) -> None:
        """Initialize provider switcher."""
        self._custom_providers: dict[str, ProviderConfig] = {}
        self._load_custom_providers()

    def _load_custom_providers(self) -> None:
        """Load custom providers from user configuration."""
        if not PROVIDERS_FILE.exists():
            return

        # Clear existing custom providers to handle file updates
        self._custom_providers.clear()

        try:
            import yaml  # type: ignore[import-untyped]

            with open(PROVIDERS_FILE, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Validate structure
            if not isinstance(data, dict):
                return

            providers = data.get("providers", {})
            if not isinstance(providers, dict):
                return

            for name, config in providers.items():
                if not isinstance(name, str) or not isinstance(config, dict):
                    continue
                try:
                    self._custom_providers[name] = ProviderConfig(
                        name=name,
                        is_builtin=False,
                        **config,
                    )
                except (ValueError, TypeError):
                    # Skip invalid provider config
                    continue
        except yaml.YAMLError as e:
            from rich.console import Console

            Console(stderr=True).print(
                f"[yellow]Warning: Failed to parse {PROVIDERS_FILE}: {e}[/]"
            )
        except OSError as e:
            from rich.console import Console

            Console(stderr=True).print(
                f"[yellow]Warning: Failed to read {PROVIDERS_FILE}: {e}[/]"
            )

    def get_all_providers(self) -> dict[str, ProviderConfig]:
        """Get all available providers (built-in + custom).

        Returns:
            Dictionary of provider name to ProviderConfig
        """
        return {**BUILTIN_PROVIDERS, **self._custom_providers}

    def get_provider(self, name: str) -> ProviderConfig | None:
        """Get provider by name.

        Args:
            name: Provider name

        Returns:
            ProviderConfig or None
        """
        return BUILTIN_PROVIDERS.get(name) or self._custom_providers.get(name)

    def get_current(self) -> str | None:
        """Detect current provider from settings.json.

        Returns:
            Current provider name or None if not configured
        """
        settings = self._load_json(SETTINGS_FILE)
        env = settings.get("env", {})

        # Check for stored provider marker (handles OpenAI-only providers like deepseek)
        stored_provider = env.get("_OHMYCLAUDE_PROVIDER")
        if isinstance(stored_provider, str) and stored_provider:
            return stored_provider

        base_url = env.get("ANTHROPIC_BASE_URL")

        # No base URL means official
        if not base_url:
            return "official"

        # Match against known providers
        for name, provider in self.get_all_providers().items():
            if provider.anthropic_base_url == base_url:
                return name

        return "custom"

    def switch(
        self,
        provider_name: str,
        token: str | None = None,
        base_url: str | None = None,
        skip_codex: bool = False,
    ) -> SwitchResult:
        """Switch to specified provider.

        Args:
            provider_name: Target provider name
            token: Optional token override (uses env var if not provided)
            base_url: Optional base URL override
            skip_codex: Skip Codex auth.json update

        Returns:
            SwitchResult with operation details
        """
        # Security: Validate user-provided inputs
        if token:
            try:
                _validate_api_token(token)
            except ValueError as e:
                return SwitchResult(
                    success=False,
                    provider_name=provider_name,
                    message=f"Invalid token: {e}",
                )

        if base_url:
            try:
                _validate_api_url(base_url)
            except ValueError as e:
                return SwitchResult(
                    success=False,
                    provider_name=provider_name,
                    message=f"Invalid base URL: {e}",
                )

        # 1. Get provider configuration
        provider = self.get_provider(provider_name)

        # Fix #3: Relax validation - only require base_url for custom providers
        if not provider and not base_url:
            return SwitchResult(
                success=False,
                provider_name=provider_name,
                message=(
                    f"Unknown provider: {provider_name}. "
                    "Use --base-url for custom provider."
                ),
            )

        # Create ad-hoc provider for custom with override
        if not provider:
            provider = ProviderConfig(
                name=provider_name,
                display_name=f"Custom: {provider_name}",
                anthropic_base_url=base_url or "",
                anthropic_token_env="CUSTOM_AUTH_TOKEN",
                is_builtin=False,
            )

        # Fix #1: Validate token availability (except for official which may use default)
        effective_token = token or os.environ.get(provider.anthropic_token_env)
        if not effective_token and provider_name != "official":
            return SwitchResult(
                success=False,
                provider_name=provider_name,
                message=(
                    f"Token not found. Set environment variable "
                    f"{provider.anthropic_token_env} or use --token option."
                ),
            )

        # Get current provider for result
        previous_provider = self.get_current()

        # 2. Backup current settings.json
        settings_backup = self._backup_file(SETTINGS_FILE)

        # 3. Load and update settings.json
        settings = self._load_json(SETTINGS_FILE)
        env_updates = provider.get_env_updates()

        # Apply CLI overrides
        if token:
            env_updates["ANTHROPIC_AUTH_TOKEN"] = token
        if base_url:
            env_updates["ANTHROPIC_BASE_URL"] = base_url

        # Store provider marker for tracking (Fix #2 support)
        env_updates["_OHMYCLAUDE_PROVIDER"] = provider_name

        # Clean up keys from previous provider (not target provider)
        if previous_provider:
            for key in get_cleanup_keys(previous_provider):
                if key not in env_updates:
                    env_updates[key] = None  # Mark for deletion

        settings = self._apply_env(settings, env_updates)
        # Save with restrictive permissions to protect API tokens
        save_json(SETTINGS_FILE, settings, file_mode=0o600)

        result = SwitchResult(
            success=True,
            provider_name=provider_name,
            previous_provider=previous_provider,
            settings_backup=str(settings_backup) if settings_backup else None,
            codex_updated=False,
        )

        # 4. Update Codex auth.json if applicable
        if not skip_codex and provider.openai_base_url:
            codex_result = self._update_codex(provider, token)
            result.codex_updated = codex_result.get("updated", False)
            result.codex_backup = codex_result.get("backup")

        result.message = f"Successfully switched to {provider.display_name}"
        return result

    def _update_codex(
        self,
        provider: ProviderConfig,
        token_override: str | None = None,
    ) -> dict[str, Any]:
        """Update Codex auth.json for OpenAI-compatible providers.

        Args:
            provider: Provider configuration
            token_override: Optional token override

        Returns:
            Dict with 'updated' bool, optional 'backup' path, and 'reason' on failure
        """
        if not provider.openai_base_url:
            return {"updated": False, "reason": "no_openai_url"}

        # Determine OpenAI token (priority: override > openai env > anthropic env)
        openai_token = token_override
        if not openai_token and provider.openai_token_env:
            openai_token = os.environ.get(provider.openai_token_env)
        if not openai_token:
            openai_token = os.environ.get(provider.anthropic_token_env)

        if not openai_token:
            return {
                "updated": False,
                "reason": "missing_token",
                "env_var": provider.openai_token_env or provider.anthropic_token_env,
            }

        # Ensure directory exists
        CODEX_AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing auth.json
        backup = self._backup_file(CODEX_AUTH_FILE)

        # Load and update
        auth = self._load_json(CODEX_AUTH_FILE)
        auth["OPENAI_API_KEY"] = openai_token
        auth["OPENAI_BASE_URL"] = provider.openai_base_url

        # Save with restrictive permissions to protect API tokens
        save_json(CODEX_AUTH_FILE, auth, file_mode=0o600)

        return {
            "updated": True,
            "backup": str(backup) if backup else None,
        }

    def add_custom_provider(
        self,
        name: str,
        display_name: str,
        base_url: str,
        token_env: str,
        openai_base_url: str | None = None,
        openai_token_env: str | None = None,
        description: str = "",
    ) -> bool:
        """Add a custom provider to user configuration.

        Args:
            name: Provider identifier
            display_name: Human-readable name
            base_url: Anthropic API base URL
            token_env: Environment variable for token
            openai_base_url: Optional OpenAI-compatible URL
            openai_token_env: Optional OpenAI token env var
            description: Provider description

        Returns:
            True if added successfully
        """
        import yaml
        from rich.console import Console

        from ohmyclaude.core.atomic import atomic_write
        from ohmyclaude.core.security import (
            ValidationError,
            validate_api_url,
            validate_env_var_name,
            validate_path_segment,
        )

        console = Console(stderr=True)
        ensure_ohmyclaude_dirs()

        # Validate user input early to avoid writing broken YAML
        try:
            safe_name = validate_path_segment(name, label="provider")
            safe_base_url = validate_api_url(base_url)
            safe_token_env = validate_env_var_name(token_env)
            safe_openai_base_url = (
                validate_api_url(openai_base_url) if openai_base_url else None
            )
            safe_openai_token_env = (
                validate_env_var_name(openai_token_env) if openai_token_env else None
            )
        except (ValidationError, ValueError) as e:
            console.print(f"[red]Invalid provider configuration: {e}[/]")
            return False

        # Load existing providers
        providers_data: dict[str, Any] = {}
        if PROVIDERS_FILE.exists():
            try:
                with open(PROVIDERS_FILE, encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                if isinstance(loaded, dict):
                    providers_data = loaded
            except (OSError, yaml.YAMLError) as e:
                console.print(
                    f"[yellow]Warning: Failed to load existing providers, starting fresh: {e}[/]"
                )
                providers_data = {}

        # Add new provider
        if "providers" not in providers_data:
            providers_data["providers"] = {}

        providers_data["providers"][safe_name] = {
            "display_name": display_name,
            "description": description or f"Custom provider: {safe_name}",
            "anthropic_base_url": safe_base_url,
            "anthropic_token_env": safe_token_env,
        }

        if safe_openai_base_url:
            providers_data["providers"][safe_name]["openai_base_url"] = safe_openai_base_url
        if safe_openai_token_env:
            providers_data["providers"][safe_name]["openai_token_env"] = safe_openai_token_env

        # Save atomically with restrictive permissions
        try:
            with atomic_write(PROVIDERS_FILE, file_mode=0o600) as f:
                yaml.safe_dump(
                    providers_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=True,
                )

            # Reload custom providers
            self._load_custom_providers()
            return True
        except (OSError, yaml.YAMLError) as e:
            console.print(f"[red]Failed to save provider config: {e}[/]")
            return False

    def remove_custom_provider(self, name: str) -> bool:
        """Remove a custom provider from user configuration.

        Args:
            name: Provider identifier to remove

        Returns:
            True if removed successfully
        """
        import yaml
        from rich.console import Console

        from ohmyclaude.core.atomic import atomic_write
        from ohmyclaude.core.security import ValidationError, validate_path_segment

        console = Console(stderr=True)

        # Validate provider name
        try:
            safe_name = validate_path_segment(name, label="provider")
        except ValidationError:
            console.print(f"[red]Invalid provider name: {name}[/]")
            return False

        if not PROVIDERS_FILE.exists():
            console.print("[yellow]No custom providers found[/]")
            return False

        # Load existing providers
        try:
            with open(PROVIDERS_FILE, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError) as e:
            console.print(f"[red]Failed to load providers: {e}[/]")
            return False

        if not isinstance(data, dict):
            console.print("[red]Invalid providers file format[/]")
            return False

        providers = data.get("providers")
        if not isinstance(providers, dict) or safe_name not in providers:
            console.print(f"[yellow]Provider '{safe_name}' not found[/]")
            return False

        # Remove provider
        providers.pop(safe_name, None)
        data["providers"] = providers

        # Save atomically
        try:
            with atomic_write(PROVIDERS_FILE, file_mode=0o600) as f:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=True,
                )
            # Reload custom providers
            self._load_custom_providers()
            return True
        except (OSError, yaml.YAMLError) as e:
            console.print(f"[red]Failed to save providers: {e}[/]")
            return False

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file safely.

        Args:
            path: File path

        Returns:
            Parsed JSON or empty dict
        """
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            # Backup corrupt file
            backup = path.with_suffix(
                path.suffix + f".corrupt-{datetime.now().strftime(BACKUP_SUFFIX_FMT)}"
            )
            try:
                shutil.copy2(path, backup)
            except OSError:
                pass  # Backup failed, continue with empty dict
            return {}
        except OSError:
            # File read error (permissions, I/O error, etc.)
            return {}

    def _backup_file(self, path: Path) -> Path | None:
        """Create timestamped backup of file.

        Args:
            path: File to backup

        Returns:
            Backup path or None if file doesn't exist
        """
        if not path.exists():
            return None

        timestamp = datetime.now().strftime(BACKUP_SUFFIX_FMT)
        backup_path = path.with_suffix(f"{path.suffix}.bak-{timestamp}")
        shutil.copy2(path, backup_path)
        return backup_path

    def _apply_env(
        self,
        data: dict[str, Any],
        env_updates: dict[str, str | int | None],
    ) -> dict[str, Any]:
        """Apply environment variable updates to settings.

        Args:
            data: Settings dictionary
            env_updates: Dict of env vars (None = delete)

        Returns:
            Updated settings dictionary
        """
        current_env = data.get("env", {})
        if not isinstance(current_env, dict):
            current_env = {}

        for key, value in env_updates.items():
            if value is None:
                current_env.pop(key, None)
            else:
                current_env[key] = value

        data["env"] = current_env
        return data
