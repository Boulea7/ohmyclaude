"""MCP package management module.

This module handles loading MCP package definitions and resolving them
to server configurations for Claude Code settings.json.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class McpServerConfig(BaseModel):
    """MCP server configuration for settings.json."""

    name: str
    description: str = ""
    transport: Literal["stdio", "sse"] = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    env: dict[str, str] = Field(default_factory=dict)
    estimated_tokens: int = 0
    cost_tier: Literal["free", "free-tier", "paid"] = "free"
    api_key_env: str | None = None
    api_key_url: str | None = None
    requires: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    def to_settings_dict(self) -> dict[str, Any]:
        """Convert to Claude Code settings.json format."""
        result: dict[str, Any] = {}

        if self.transport == "stdio":
            result["command"] = self.command
            result["args"] = self.args
        else:  # sse
            result["type"] = "sse"
            result["url"] = self.url

        # Process environment variables
        if self.env:
            resolved_env = {}
            for key, value in self.env.items():
                # Resolve ${VAR} references from environment
                if value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    resolved_value = os.environ.get(env_var, "")
                    if resolved_value:
                        resolved_env[key] = resolved_value
                else:
                    resolved_env[key] = value
            if resolved_env:
                result["env"] = resolved_env

        return result


class McpPackage(BaseModel):
    """MCP package definition (group of related servers)."""

    name: str
    description: str = ""
    description_cn: str = ""
    cost_tier: Literal["free", "free-tier", "paid"] = "free"
    servers: list[str] = Field(default_factory=list)
    api_key_env: str | None = None
    api_key_url: str | None = None
    optional: bool = False
    requires: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class McpPackageRegistry:
    """Registry for loading and resolving MCP packages."""

    def __init__(self, packages_file: Path | None = None):
        """Initialize the registry.

        Args:
            packages_file: Path to mcp_packages.yaml. If None, uses default template.
        """
        self._packages: dict[str, McpPackage] = {}
        self._servers: dict[str, McpServerConfig] = {}
        self._bundles: dict[str, dict[str, Any]] = {}

        if packages_file is None:
            # Use bundled template
            packages_file = (
                Path(__file__).parent.parent.parent.parent
                / "templates"
                / "mcp"
                / "mcp_packages.yaml"
            )

        self._load_packages(packages_file)

    def _load_packages(self, packages_file: Path) -> None:
        """Load package definitions from YAML file."""
        if not packages_file.exists():
            raise FileNotFoundError(f"MCP packages file not found: {packages_file}")

        with open(packages_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(
                    f"Invalid YAML in MCP packages file: {packages_file}"
                ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                f"MCP packages file must be a mapping at top-level: {packages_file}"
            )

        # Load server definitions
        servers_data = data.get("servers") or {}
        if not isinstance(servers_data, dict):
            raise ValueError("servers must be a mapping of server name to config")

        for key, server_data in servers_data.items():
            if not isinstance(server_data, dict):
                raise ValueError(f"Server '{key}' config must be a mapping")

            server_data_copy = dict(server_data)
            if "name" not in server_data_copy:
                server_data_copy["name"] = key

            server = McpServerConfig(**server_data_copy)

            # Validate required fields based on transport
            if server.transport == "stdio" and not server.command:
                raise ValueError(
                    f"Server '{key}' (stdio) is missing required 'command'"
                )
            if server.transport == "sse" and not server.url:
                raise ValueError(f"Server '{key}' (sse) is missing required 'url'")

            self._servers[key] = server

        # Load package definitions
        packages_data = data.get("packages") or {}
        if not isinstance(packages_data, dict):
            raise ValueError("packages must be a mapping of package name to config")

        for key, pkg_data in packages_data.items():
            if not isinstance(pkg_data, dict):
                raise ValueError(f"Package '{key}' config must be a mapping")

            pkg_data_copy = dict(pkg_data)
            if "name" not in pkg_data_copy:
                pkg_data_copy["name"] = key

            package = McpPackage(**pkg_data_copy)

            # Validate server references
            for server_name in package.servers:
                if server_name not in self._servers:
                    raise ValueError(
                        f"Package '{key}' references unknown server '{server_name}'"
                    )

            self._packages[key] = package

        # Load bundle definitions
        bundles_data = data.get("bundles") or {}
        if not isinstance(bundles_data, dict):
            raise ValueError("bundles must be a mapping of bundle name to config")
        self._bundles = bundles_data

    def get_package(self, name: str) -> McpPackage | None:
        """Get a package by name."""
        return self._packages.get(name)

    def get_server(self, name: str) -> McpServerConfig | None:
        """Get a server by name."""
        return self._servers.get(name)

    def list_packages(self) -> list[str]:
        """List all available package names."""
        return list(self._packages.keys())

    def list_servers(self) -> list[str]:
        """List all available server names."""
        return list(self._servers.keys())

    def list_bundles(self) -> list[str]:
        """List all available bundle names."""
        return list(self._bundles.keys())

    def resolve_packages(
        self, package_names: list[str], strict: bool = True
    ) -> tuple[dict[str, McpServerConfig], list[str]]:
        """Resolve package names to server configurations.

        Args:
            package_names: List of package names to resolve.
            strict: If True, raise ValueError for unknown packages.

        Returns:
            Tuple of (servers dict, sorted missing API keys list).

        Raises:
            ValueError: If strict=True and unknown packages are found.
        """
        servers: dict[str, McpServerConfig] = {}
        missing_keys: set[str] = set()
        unknown_packages: list[str] = []

        for pkg_name in package_names:
            package = self._packages.get(pkg_name)
            if not package:
                unknown_packages.append(pkg_name)
                continue

            # Check API key requirements
            if package.api_key_env:
                if not os.environ.get(package.api_key_env):
                    missing_keys.add(package.api_key_env)

            # Add all servers from package
            for server_name in package.servers:
                server = self._servers.get(server_name)
                if server:
                    servers[server_name] = server

        if strict and unknown_packages:
            raise ValueError(
                f"Unknown MCP packages: {', '.join(sorted(unknown_packages))}"
            )

        return servers, sorted(missing_keys)

    def resolve_bundle(
        self, bundle_name: str, include_optional: bool = False
    ) -> tuple[dict[str, McpServerConfig], list[str]]:
        """Resolve a bundle to server configurations.

        Args:
            bundle_name: Name of the bundle (starter, standard, full-free, full).
            include_optional: If True, also include optional_packages.

        Returns:
            Tuple of (servers dict, missing API keys list).

        Raises:
            ValueError: If bundle_name is unknown.
        """
        bundle = self._bundles.get(bundle_name)
        if not bundle:
            raise ValueError(f"Unknown MCP bundle: {bundle_name}")

        package_names = list(bundle.get("packages", []))
        if include_optional:
            package_names += bundle.get("optional_packages", [])

        return self.resolve_packages(package_names)

    def generate_settings_json(
        self,
        package_names: list[str],
        allowed_directories: list[str] | None = None,
    ) -> tuple[dict[str, Any], list[str]]:
        """Generate MCP servers config for settings.json.

        Args:
            package_names: List of package names to include.
            allowed_directories: Directories to allow for filesystem MCP.

        Returns:
            Tuple of (settings dict, missing API keys list).
            The settings dict is ready for settings.json mcpServers field.
        """
        servers, missing_keys = self.resolve_packages(package_names)
        result: dict[str, Any] = {}

        for name, server in servers.items():
            config = server.to_settings_dict()

            # Special handling for filesystem server
            if name == "filesystem" and allowed_directories:
                config["args"] = config.get("args", []) + allowed_directories

            result[name] = config

        return result, missing_keys

    def get_package_info(self, name: str) -> dict[str, Any] | None:
        """Get detailed info about a package for display."""
        package = self._packages.get(name)
        if not package:
            return None

        servers_info = []
        total_tokens = 0
        for server_name in package.servers:
            server = self._servers.get(server_name)
            if server:
                servers_info.append(
                    {
                        "name": server.name,
                        "description": server.description,
                        "tokens": server.estimated_tokens,
                    }
                )
                total_tokens += server.estimated_tokens

        return {
            "name": package.name,
            "description": package.description,
            "description_cn": package.description_cn,
            "cost_tier": package.cost_tier,
            "optional": package.optional,
            "servers": servers_info,
            "total_tokens": total_tokens,
            "api_key_env": package.api_key_env,
            "api_key_url": package.api_key_url,
        }

    def check_requirements(self, package_names: list[str]) -> dict[str, list[str]]:
        """Check system requirements for packages.

        Args:
            package_names: List of package names to check.

        Returns:
            Dict mapping package names to list of missing requirements.
        """
        missing: dict[str, list[str]] = {}

        for pkg_name in package_names:
            package = self._packages.get(pkg_name)
            if not package:
                continue

            pkg_missing = []

            # Check server requirements
            for server_name in package.servers:
                server = self._servers.get(server_name)
                if server and server.requires:
                    for req in server.requires:
                        # Basic checks - can be expanded
                        if "Python" in req:
                            # Python version check
                            pass
                        elif "uv" in req:
                            # Check if uv is installed
                            import shutil

                            if not shutil.which("uvx"):
                                pkg_missing.append(req)
                        elif "Codex" in req:
                            # Check if codex is installed
                            import shutil

                            if not shutil.which("codex"):
                                pkg_missing.append(req)

            if pkg_missing:
                missing[pkg_name] = pkg_missing

        return missing


# Module-level singleton for convenience
_registry: McpPackageRegistry | None = None


def get_registry() -> McpPackageRegistry:
    """Get the global MCP package registry."""
    global _registry
    if _registry is None:
        _registry = McpPackageRegistry()
    return _registry
