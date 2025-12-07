"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from ohmyclaude.models.presets import (
    HookMatcherPreset,
    HookPreset,
    McpServerPreset,
    PresetConfig,
    ResourceEstimates,
)
from ohmyclaude.models.settings import (
    HookConfig,
    HookMatcherConfig,
    McpServerConfig,
    PermissionsConfig,
    SettingsConfig,
    SettingsExport,
)


class TestSettingsModels:
    """Tests for settings.json models."""

    def test_permissions_config_defaults(self):
        """Test PermissionsConfig default values."""
        config = PermissionsConfig()

        assert config.additionalDirectories == []
        assert config.allow == []
        assert config.deny == []
        assert config.ask == []

    def test_permissions_config_with_values(self):
        """Test PermissionsConfig with custom values."""
        config = PermissionsConfig(
            additionalDirectories=["/home/user/projects"],
            allow=["Read", "Write"],
            deny=["Bash(rm:*)"],
            ask=["Bash(git push:*)"],
        )

        assert config.additionalDirectories == ["/home/user/projects"]
        assert "Read" in config.allow
        assert "Bash(rm:*)" in config.deny

    def test_mcp_server_config_defaults(self):
        """Test McpServerConfig default values."""
        config = McpServerConfig()

        assert config.command is None
        assert config.args == []
        assert config.env == {}
        assert config.url is None
        assert config.transport == "stdio"

    def test_mcp_server_config_stdio(self):
        """Test McpServerConfig for stdio transport."""
        config = McpServerConfig(
            command="npx",
            args=["-y", "@anthropic/mcp-server"],
            env={"DEBUG": "true"},
        )

        assert config.command == "npx"
        assert "-y" in config.args
        assert config.env["DEBUG"] == "true"

    def test_mcp_server_config_sse(self):
        """Test McpServerConfig for SSE transport."""
        config = McpServerConfig(
            transport="sse",
            url="https://mcp.example.com/sse",
        )

        assert config.transport == "sse"
        assert config.url == "https://mcp.example.com/sse"

    def test_hook_config(self):
        """Test HookConfig model."""
        config = HookConfig(
            command="echo 'Hello'",
            timeout=10000,
            description="Test hook",
        )

        assert config.type == "command"
        assert config.command == "echo 'Hello'"
        assert config.timeout == 10000
        assert config.description == "Test hook"

    def test_hook_matcher_config(self):
        """Test HookMatcherConfig model."""
        config = HookMatcherConfig(
            matcher="Edit|Write",
            hooks=[HookConfig(command="echo 'edited'")],
        )

        assert config.matcher == "Edit|Write"
        assert len(config.hooks) == 1

    def test_settings_config_defaults(self):
        """Test SettingsConfig default values."""
        config = SettingsConfig()

        assert config.model == "sonnet"
        assert config.alwaysThinkingEnabled is True
        assert config.env == {}
        assert config.mcpServers == {}
        assert config.hooks == {}

    def test_settings_config_with_values(self):
        """Test SettingsConfig with custom values."""
        config = SettingsConfig(
            model="opus",
            alwaysThinkingEnabled=False,
            env={"ANTHROPIC_AUTH_TOKEN": "test-token"},
            permissions=PermissionsConfig(allow=["Read"]),
            mcpServers={
                "filesystem": McpServerConfig(command="npx")
            },
        )

        assert config.model == "opus"
        assert config.alwaysThinkingEnabled is False
        assert config.env["ANTHROPIC_AUTH_TOKEN"] == "test-token"
        assert "Read" in config.permissions.allow
        assert "filesystem" in config.mcpServers

    def test_settings_config_extra_fields(self):
        """Test that SettingsConfig allows extra fields."""
        config = SettingsConfig(
            model="sonnet",
            customField="allowed",
        )

        assert config.customField == "allowed"

    def test_settings_export(self):
        """Test SettingsExport model."""
        export = SettingsExport(
            version="1.0.0",
            settings=SettingsConfig(),
            metadata={"exported_at": "2024-12-07"},
        )

        assert export.version == "1.0.0"
        assert export.settings.model == "sonnet"
        assert export.metadata["exported_at"] == "2024-12-07"


class TestPresetModels:
    """Tests for preset configuration models."""

    def test_mcp_server_preset_defaults(self):
        """Test McpServerPreset default values."""
        preset = McpServerPreset()

        assert preset.enabled is True
        assert preset.transport == "stdio"
        assert preset.estimated_tokens == 0

    def test_mcp_server_preset_with_values(self):
        """Test McpServerPreset with custom values."""
        preset = McpServerPreset(
            enabled=True,
            command="uvx",
            args=["--from", "mcp-server"],
            description="Test server",
            estimated_tokens=500,
        )

        assert preset.command == "uvx"
        assert "--from" in preset.args
        assert preset.estimated_tokens == 500

    def test_hook_preset(self):
        """Test HookPreset model."""
        preset = HookPreset(
            command="bash script.sh",
            timeout=30000,
            description="Run script",
        )

        assert preset.type == "command"
        assert preset.timeout == 30000

    def test_hook_matcher_preset(self):
        """Test HookMatcherPreset model."""
        preset = HookMatcherPreset(
            matcher="Edit|MultiEdit",
            hooks=[HookPreset(command="echo 'edited'")],
        )

        assert preset.matcher == "Edit|MultiEdit"

    def test_resource_estimates_defaults(self):
        """Test ResourceEstimates default values."""
        estimates = ResourceEstimates()

        assert estimates.mcp_overhead_tokens == 0
        assert estimates.context_usage_percent == 0.0
        assert estimates.available_context == 200000

    def test_preset_config_minimal(self):
        """Test PresetConfig with minimal required fields."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
        )

        assert preset.name == "test"
        assert preset.version == "1.0.0"
        assert preset.model == "sonnet"
        assert preset.always_thinking_enabled is True
        assert preset.include_codex is False

    def test_preset_config_full(self):
        """Test PresetConfig with all fields."""
        preset = PresetConfig(
            name="full",
            description="Full preset",
            version="1.0.0",
            model="opus",
            always_thinking_enabled=True,
            claude_md_template="full",
            mcp_packages=["basic", "reasoning", "code"],
            commands=["commit", "review", "test"],
            agents=["code-reviewer", "debugger"],
            hooks_preset="full",
            include_codex=True,
            skills=["frontend-dev-guidelines"],
            upgrade_to=None,
        )

        assert preset.model == "opus"
        assert "basic" in preset.mcp_packages
        assert "commit" in preset.commands
        assert "code-reviewer" in preset.agents
        assert preset.include_codex is True

    def test_preset_config_get_enabled_servers(self):
        """Test get_enabled_mcp_servers method."""
        preset = PresetConfig(
            name="test",
            description="Test",
            mcp_servers={
                "enabled_server": McpServerPreset(enabled=True, estimated_tokens=100),
                "disabled_server": McpServerPreset(enabled=False, estimated_tokens=200),
            },
        )

        enabled = preset.get_enabled_mcp_servers()

        assert "enabled_server" in enabled
        assert "disabled_server" not in enabled

    def test_preset_config_get_total_tokens(self):
        """Test get_total_token_overhead method."""
        preset = PresetConfig(
            name="test",
            description="Test",
            mcp_servers={
                "server1": McpServerPreset(enabled=True, estimated_tokens=100),
                "server2": McpServerPreset(enabled=True, estimated_tokens=200),
                "server3": McpServerPreset(enabled=False, estimated_tokens=300),
            },
        )

        total = preset.get_total_token_overhead()

        assert total == 300  # Only enabled servers

    def test_preset_config_extra_fields(self):
        """Test that PresetConfig allows extra fields."""
        preset = PresetConfig(
            name="test",
            description="Test",
            codex={"enabled": True, "default_sandbox": "read-only"},
        )

        assert preset.codex["enabled"] is True


class TestModelValidation:
    """Tests for model validation."""

    def test_settings_invalid_model(self):
        """Test that invalid model value raises error."""
        with pytest.raises(ValidationError):
            SettingsConfig(model="invalid-model")

    def test_mcp_server_invalid_transport(self):
        """Test that invalid transport raises error."""
        with pytest.raises(ValidationError):
            McpServerConfig(transport="invalid")

    def test_preset_invalid_model(self):
        """Test that invalid model in preset raises error."""
        with pytest.raises(ValidationError):
            PresetConfig(
                name="test",
                description="Test",
                model="gpt-4",  # Invalid for Claude
            )
