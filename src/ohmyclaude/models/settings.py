"""Pydantic models for Claude Code settings.json configuration.

This module defines the data models that map to the ~/.claude/settings.json file.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PermissionsConfig(BaseModel):
    """Permissions configuration for Claude Code."""

    additionalDirectories: list[str] = Field(
        default_factory=list,
        description="Additional directories Claude can access",
    )
    allow: list[str] = Field(
        default_factory=list,
        description="Commands/tools allowed without asking",
    )
    deny: list[str] = Field(
        default_factory=list,
        description="Commands/tools always denied",
    )
    ask: list[str] = Field(
        default_factory=list,
        description="Commands/tools that require user confirmation",
    )


class McpServerConfig(BaseModel):
    """MCP server configuration."""

    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    transport: Literal["stdio", "sse"] = "stdio"


class HookConfig(BaseModel):
    """Individual hook configuration."""

    type: Literal["command"] = "command"
    command: str
    timeout: int = 5000
    description: str = ""


class HookMatcherConfig(BaseModel):
    """Hook matcher configuration for tool-based hooks."""

    matcher: str
    hooks: list[HookConfig] = Field(default_factory=list)


class SettingsConfig(BaseModel):
    """Main settings.json configuration model.

    This model represents the complete ~/.claude/settings.json file structure.
    """

    model: Literal["sonnet", "opus", "haiku"] = Field(
        default="sonnet",
        description="Default Claude model to use",
    )
    alwaysThinkingEnabled: bool = Field(
        default=True,
        description="Enable extended thinking mode",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to inject",
    )
    permissions: PermissionsConfig = Field(
        default_factory=PermissionsConfig,
        description="Permissions configuration",
    )
    mcpServers: dict[str, McpServerConfig] = Field(
        default_factory=dict,
        description="MCP server configurations",
    )
    hooks: dict[str, list[HookConfig | HookMatcherConfig]] = Field(
        default_factory=dict,
        description="Hook configurations by event type",
    )

    model_config = ConfigDict(extra="allow")


class SettingsExport(BaseModel):
    """Export format for settings backup/restore."""

    version: str = "1.0.0"
    settings: SettingsConfig
    metadata: dict[str, Any] = Field(default_factory=dict)
