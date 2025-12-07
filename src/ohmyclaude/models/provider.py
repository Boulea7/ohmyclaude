"""Pydantic models for API provider configuration.

This module defines the data models for API provider switching functionality,
supporting official Anthropic API and third-party providers like GLM, 88Code, DeepSeek.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
import os


class ProviderConfig(BaseModel):
    """API provider configuration model.

    Represents a single API provider configuration that can be used
    to switch Claude Code between different API endpoints.

    Example:
        >>> provider = ProviderConfig(
        ...     name="glm",
        ...     display_name="Zhipu AI",
        ...     anthropic_base_url="https://open.bigmodel.cn/api/anthropic",
        ...     anthropic_token_env="GLM_ANTHROPIC_AUTH_TOKEN",
        ... )
    """

    # Basic info
    name: str = Field(description="Unique provider identifier (e.g., 'official', 'glm')")
    display_name: str = Field(description="Human-readable display name")
    description: str = Field(default="", description="Provider description")

    # Anthropic API configuration
    anthropic_base_url: Optional[str] = Field(
        default=None,
        description="Anthropic API base URL (None = official default)",
    )
    anthropic_token_env: str = Field(
        description="Environment variable name for Anthropic auth token",
    )

    # OpenAI-compatible API configuration (for Codex)
    openai_base_url: Optional[str] = Field(
        default=None,
        description="OpenAI-compatible API base URL for Codex",
    )
    openai_token_env: Optional[str] = Field(
        default=None,
        description="Environment variable name for OpenAI API key",
    )

    # Extra environment variables
    extra_env: dict[str, str | int] = Field(
        default_factory=dict,
        description="Additional environment variables to set",
    )

    # Provider metadata
    is_builtin: bool = Field(
        default=True,
        description="Whether this is a built-in provider",
    )
    api_type: Literal["anthropic", "openai", "hybrid"] = Field(
        default="anthropic",
        description="API type: anthropic, openai, or hybrid (both)",
    )

    model_config = ConfigDict(extra="allow")

    def get_env_updates(self) -> dict[str, str | int | None]:
        """Generate environment variable updates for this provider.

        Returns:
            Dictionary of env vars to set. None values indicate deletion.
        """
        env: dict[str, str | int | None] = {}

        # Token from environment variable
        token = os.environ.get(self.anthropic_token_env)
        if token:
            env["ANTHROPIC_AUTH_TOKEN"] = token

        # Base URL (None means use default / should be deleted)
        if self.anthropic_base_url:
            env["ANTHROPIC_BASE_URL"] = self.anthropic_base_url
        else:
            # Explicitly mark for removal when switching to official
            env["ANTHROPIC_BASE_URL"] = None

        # Extra environment variables
        for key, value in self.extra_env.items():
            env[key] = value

        return env

    def get_token(self) -> Optional[str]:
        """Get the token from environment variable.

        Returns:
            Token string or None if not set.
        """
        return os.environ.get(self.anthropic_token_env)


class CustomProviderConfig(BaseModel):
    """User-defined custom provider configuration.

    Stored in ~/.ohmyclaude/providers.yaml for user-defined providers.
    """

    name: str
    display_name: str
    anthropic_base_url: str
    anthropic_token_env: str
    openai_base_url: Optional[str] = None
    openai_token_env: Optional[str] = None
    description: str = ""

    def to_provider_config(self) -> ProviderConfig:
        """Convert to ProviderConfig."""
        return ProviderConfig(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            anthropic_base_url=self.anthropic_base_url,
            anthropic_token_env=self.anthropic_token_env,
            openai_base_url=self.openai_base_url,
            openai_token_env=self.openai_token_env,
            is_builtin=False,
            api_type="hybrid" if self.openai_base_url else "anthropic",
        )


class SwitchResult(BaseModel):
    """Result of a provider switch operation.

    Contains details about the switch operation including success status,
    backup file paths, and any error messages.
    """

    success: bool = Field(description="Whether the switch operation succeeded")
    provider_name: str = Field(description="Name of the target provider")
    previous_provider: Optional[str] = Field(
        default=None,
        description="Name of the previous provider",
    )
    settings_backup: Optional[str] = Field(
        default=None,
        description="Path to settings.json backup file",
    )
    codex_backup: Optional[str] = Field(
        default=None,
        description="Path to Codex auth.json backup file",
    )
    codex_updated: bool = Field(
        default=False,
        description="Whether Codex auth.json was updated",
    )
    message: str = Field(
        default="",
        description="Human-readable result message",
    )
