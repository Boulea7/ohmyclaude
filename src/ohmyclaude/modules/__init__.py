"""Configuration modules for OhMyClaude."""

from ohmyclaude.modules.mcp import (
    McpPackage,
    McpPackageRegistry,
    McpServerConfig,
    get_registry,
)
from ohmyclaude.modules.provider import (
    BUILTIN_PROVIDERS,
    CLEANUP_KEYS,
    get_cleanup_keys,
    get_provider,
    get_provider_names,
    is_builtin_provider,
    list_providers,
)

__all__ = [
    # MCP modules
    "McpPackage",
    "McpPackageRegistry",
    "McpServerConfig",
    "get_registry",
    # Provider modules
    "BUILTIN_PROVIDERS",
    "CLEANUP_KEYS",
    "get_provider",
    "get_provider_names",
    "get_cleanup_keys",
    "is_builtin_provider",
    "list_providers",
]
