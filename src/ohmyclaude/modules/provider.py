"""API provider definitions and utilities.

This module defines built-in API providers and provides utility functions
for provider management. Supports official Anthropic API and third-party
providers like GLM (Zhipu AI), 88Code, and DeepSeek.
"""

from typing import Optional

from ohmyclaude.models.provider import ProviderConfig


# Keys to clean up when switching to specific providers
# These keys are provider-specific and should be removed when switching away
CLEANUP_KEYS: dict[str, set[str]] = {
    "official": {
        "ANTHROPIC_BASE_URL",
        "API_TIMEOUT_MS",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    },
    "88code": {
        "API_TIMEOUT_MS",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    },
    "deepseek": {
        "API_TIMEOUT_MS",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    },
}


# Built-in provider definitions
BUILTIN_PROVIDERS: dict[str, ProviderConfig] = {
    "official": ProviderConfig(
        name="official",
        display_name="Anthropic 官方",
        description="官方 Claude API (需订阅)",
        anthropic_base_url=None,  # Use default
        anthropic_token_env="ANTHROPIC_AUTH_TOKEN",
        openai_base_url=None,
        openai_token_env=None,
        api_type="anthropic",
    ),
    "glm": ProviderConfig(
        name="glm",
        display_name="智谱 AI (GLM)",
        description="智谱 GLM 系列模型，国内访问优化",
        anthropic_base_url="https://open.bigmodel.cn/api/anthropic",
        anthropic_token_env="GLM_ANTHROPIC_AUTH_TOKEN",
        openai_base_url=None,
        openai_token_env="GLM_OPENAI_API_KEY",
        extra_env={
            "API_TIMEOUT_MS": "3000000",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        },
        api_type="anthropic",
    ),
    "88code": ProviderConfig(
        name="88code",
        display_name="88Code",
        description="第三方 Claude API 代理",
        anthropic_base_url="https://www.88code.org/api",
        anthropic_token_env="CODE88_ANTHROPIC_AUTH_TOKEN",
        openai_base_url="https://www.88code.org/openai/v1",
        openai_token_env="CODE88_OPENAI_API_KEY",
        extra_env={},
        api_type="hybrid",
    ),
    "deepseek": ProviderConfig(
        name="deepseek",
        display_name="DeepSeek",
        description="DeepSeek V3/V3.2 模型，高性价比",
        anthropic_base_url=None,  # DeepSeek does not support Anthropic protocol
        anthropic_token_env="DEEPSEEK_API_KEY",
        openai_base_url="https://api.deepseek.com/v1",
        openai_token_env="DEEPSEEK_API_KEY",
        extra_env={},
        api_type="openai",
    ),
}


def get_provider(name: str) -> Optional[ProviderConfig]:
    """Get built-in provider configuration by name.

    Args:
        name: Provider name (e.g., 'official', 'glm', '88code', 'deepseek')

    Returns:
        ProviderConfig or None if not found

    Example:
        >>> provider = get_provider("glm")
        >>> print(provider.display_name)
        智谱 AI (GLM)
    """
    return BUILTIN_PROVIDERS.get(name)


def list_providers() -> list[ProviderConfig]:
    """List all built-in providers.

    Returns:
        List of ProviderConfig instances

    Example:
        >>> for p in list_providers():
        ...     print(f"{p.name}: {p.description}")
    """
    return list(BUILTIN_PROVIDERS.values())


def get_provider_names() -> list[str]:
    """Get list of built-in provider names.

    Returns:
        List of provider name strings
    """
    return list(BUILTIN_PROVIDERS.keys())


def get_cleanup_keys(provider_name: str) -> set[str]:
    """Get environment variable keys to clean up for a provider.

    When switching to a provider, these keys should be removed from
    settings.json to avoid conflicts or stale configuration.

    Args:
        provider_name: Target provider name

    Returns:
        Set of environment variable keys to remove
    """
    return CLEANUP_KEYS.get(provider_name, set())


def is_builtin_provider(name: str) -> bool:
    """Check if a provider name is a built-in provider.

    Args:
        name: Provider name to check

    Returns:
        True if the provider is built-in, False otherwise
    """
    return name in BUILTIN_PROVIDERS
