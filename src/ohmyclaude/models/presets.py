"""Pydantic models for OhMyClaude preset configurations.

This module defines the data models for preset packages (starter, standard, full).
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class McpServerPreset(BaseModel):
    """MCP server preset configuration."""

    enabled: bool = True
    transport: Literal["stdio", "sse"] = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    env: dict[str, str] = Field(default_factory=dict)
    description: str = ""
    estimated_tokens: int = 0


class HookPreset(BaseModel):
    """Hook preset configuration."""

    type: Literal["command"] = "command"
    command: str
    timeout: int = 5000
    description: str = ""


class HookMatcherPreset(BaseModel):
    """Hook matcher preset configuration."""

    matcher: str
    hooks: list[HookPreset] = Field(default_factory=list)


class ResourceEstimates(BaseModel):
    """Resource consumption estimates."""

    mcp_overhead_tokens: int = 0
    context_usage_percent: float = 0.0
    available_context: int = 200000
    recommended_monthly_budget: dict[str, float] = Field(default_factory=dict)


class PresetConfig(BaseModel):
    """Complete preset configuration model.

    This model represents a preset package (starter, standard, full) that defines
    the complete configuration for Claude Code.
    """

    name: str = Field(description="Preset name (starter/standard/full)")
    description: str = Field(description="Human-readable description")
    version: str = Field(default="1.0.0", description="Preset version")

    # Model settings
    model: Literal["sonnet", "opus", "haiku"] = Field(
        default="sonnet",
        description="Default Claude model",
    )
    always_thinking_enabled: bool = Field(
        default=True,
        description="Enable extended thinking mode",
    )

    # Template selection
    claude_md_template: str = Field(
        default="general",
        description="CLAUDE.md template to use",
    )

    # MCP configuration
    mcp_packages: list[str] = Field(
        default_factory=list,
        description="MCP package groups to install (basic, reasoning, code, etc.)",
    )
    mcp_packages_optional: list[str] = Field(
        default_factory=list,
        description="Optional paid MCP packages (web-glm, ui, transform)",
    )
    mcp_servers: dict[str, McpServerPreset] = Field(
        default_factory=dict,
        description="Detailed MCP server configurations",
    )

    # Commands and agents
    commands: list[str] = Field(
        default_factory=list,
        description="Slash commands to install",
    )
    agents: list[str] = Field(
        default_factory=list,
        description="Agent templates to install",
    )

    # Hooks
    hooks_preset: str = Field(
        default="basic",
        description="Hooks preset name",
    )
    hooks: dict[str, list[HookPreset | HookMatcherPreset | dict]] = Field(
        default_factory=dict,
        description="Detailed hooks configuration",
    )

    # Optional features
    include_codex: bool = Field(
        default=False,
        description="Include CodexMCP integration",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Skills to install",
    )

    # Resource estimates
    estimated_resources: ResourceEstimates = Field(
        default_factory=ResourceEstimates,
        description="Estimated resource consumption",
    )

    # Upgrade path
    upgrade_to: str | None = Field(
        default=None,
        description="Next tier preset name",
    )
    upgrade_benefits: list[str] = Field(
        default_factory=list,
        description="Benefits of upgrading",
    )

    model_config = ConfigDict(extra="allow")

    def get_enabled_mcp_servers(self) -> dict[str, McpServerPreset]:
        """Get only enabled MCP servers."""
        return {
            name: server
            for name, server in self.mcp_servers.items()
            if server.enabled
        }

    def get_total_token_overhead(self) -> int:
        """Calculate total MCP token overhead."""
        return sum(
            server.estimated_tokens
            for server in self.mcp_servers.values()
            if server.enabled
        )
