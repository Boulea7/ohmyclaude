"""API provider switching engine.

This module implements the core logic for switching between API providers,
including backup management, settings update, and Codex auth synchronization.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import os
import shutil

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
    get_provider,
)


BACKUP_SUFFIX_FMT = "%Y%m%d-%H%M%S"


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
            import yaml

            with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            for name, config in data.get("providers", {}).items():
                self._custom_providers[name] = ProviderConfig(
                    name=name,
                    is_builtin=False,
                    **config,
                )
        except yaml.YAMLError as e:
            from rich.console import Console

            Console(stderr=True).print(
                f"[yellow]Warning: Failed to parse {PROVIDERS_FILE}: {e}[/]"
            )
        except Exception as e:
            from rich.console import Console

            Console(stderr=True).print(
                f"[yellow]Warning: Failed to load custom providers: {e}[/]"
            )

    def get_all_providers(self) -> dict[str, ProviderConfig]:
        """Get all available providers (built-in + custom).

        Returns:
            Dictionary of provider name to ProviderConfig
        """
        return {**BUILTIN_PROVIDERS, **self._custom_providers}

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get provider by name.

        Args:
            name: Provider name

        Returns:
            ProviderConfig or None
        """
        return BUILTIN_PROVIDERS.get(name) or self._custom_providers.get(name)

    def get_current(self) -> Optional[str]:
        """Detect current provider from settings.json.

        Returns:
            Current provider name or None if not configured
        """
        settings = self._load_json(SETTINGS_FILE)
        env = settings.get("env", {})

        # Check for stored provider marker (handles OpenAI-only providers like deepseek)
        stored_provider = env.get("_OHMYCLAUDE_PROVIDER")
        if stored_provider:
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
        token: Optional[str] = None,
        base_url: Optional[str] = None,
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
        save_json(SETTINGS_FILE, settings)

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
        token_override: Optional[str] = None,
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

        save_json(CODEX_AUTH_FILE, auth)

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
        openai_base_url: Optional[str] = None,
        openai_token_env: Optional[str] = None,
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
        ensure_ohmyclaude_dirs()

        # Load existing providers
        providers_data: dict[str, Any] = {}
        if PROVIDERS_FILE.exists():
            try:
                import yaml

                with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                    providers_data = yaml.safe_load(f) or {}
            except Exception:
                providers_data = {}

        # Add new provider
        if "providers" not in providers_data:
            providers_data["providers"] = {}

        providers_data["providers"][name] = {
            "display_name": display_name,
            "description": description or f"Custom provider: {name}",
            "anthropic_base_url": base_url,
            "anthropic_token_env": token_env,
        }

        if openai_base_url:
            providers_data["providers"][name]["openai_base_url"] = openai_base_url
        if openai_token_env:
            providers_data["providers"][name]["openai_token_env"] = openai_token_env

        # Save
        try:
            import yaml

            with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
                yaml.dump(providers_data, f, default_flow_style=False, allow_unicode=True)

            # Reload custom providers
            self._load_custom_providers()
            return True
        except Exception:
            return False

    def _load_json(self, path: Path) -> dict:
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
                return json.load(f)
        except json.JSONDecodeError:
            # Backup corrupt file
            backup = path.with_suffix(
                path.suffix + f".corrupt-{datetime.now().strftime(BACKUP_SUFFIX_FMT)}"
            )
            shutil.copy2(path, backup)
            return {}

    def _backup_file(self, path: Path) -> Optional[Path]:
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

    def _apply_env(self, data: dict, env_updates: dict) -> dict:
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
