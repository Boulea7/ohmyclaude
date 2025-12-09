"""Unit tests for configuration engine."""


import pytest

from ohmyclaude.core.config import ConfigEngine
from ohmyclaude.models.presets import McpServerPreset, PresetConfig


class TestConfigEngine:
    """Tests for ConfigEngine class."""

    @pytest.fixture
    def config_engine(self) -> ConfigEngine:
        """Create a ConfigEngine instance."""
        return ConfigEngine()

    def test_init_creates_template_env(self, config_engine: ConfigEngine):
        """Test that ConfigEngine initializes Jinja2 environment."""
        assert config_engine.env is not None
        assert config_engine.presets_dir is not None

    def test_load_preset_starter(self, config_engine: ConfigEngine):
        """Test loading starter preset."""
        preset = config_engine.load_preset("starter")

        assert preset.name == "starter"
        assert preset.model == "sonnet"
        assert preset.always_thinking_enabled is True
        assert "basic" in preset.mcp_packages

    def test_load_preset_standard(self, config_engine: ConfigEngine):
        """Test loading standard preset."""
        preset = config_engine.load_preset("standard")

        assert preset.name == "standard"
        assert len(preset.mcp_packages) > 1
        assert len(preset.commands) > 0

    def test_load_preset_full(self, config_engine: ConfigEngine):
        """Test loading full preset."""
        preset = config_engine.load_preset("full")

        assert preset.name == "full"
        assert preset.include_codex is True
        assert len(preset.agents) > 5

    def test_load_preset_not_found(self, config_engine: ConfigEngine):
        """Test loading nonexistent preset raises error."""
        with pytest.raises(FileNotFoundError):
            config_engine.load_preset("nonexistent")

    def test_list_presets(self, config_engine: ConfigEngine):
        """Test listing available presets."""
        presets = config_engine.list_presets()

        assert "starter" in presets
        assert "standard" in presets
        assert "full" in presets

    def test_render_template(self, config_engine: ConfigEngine):
        """Test rendering a Jinja2 template."""
        # Test with a simple template context
        preset = config_engine.load_preset("starter")
        context = {"config": preset, "user_name": "test_user"}

        # This should not raise
        content = config_engine.render_template("claude_md/general.md.j2", context)

        assert len(content) > 0
        assert "test_user" in content or "Claude" in content

    def test_generate_settings_basic(self, config_engine: ConfigEngine):
        """Test generating settings from preset."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            model="sonnet",
            always_thinking_enabled=True,
            mcp_packages=[],
            commands=[],
        )

        settings = config_engine.generate_settings(preset)

        assert settings.model == "sonnet"
        assert settings.alwaysThinkingEnabled is True
        assert "OHMYCLAUDE_ROOT" in settings.env

    def test_generate_settings_with_mcp_servers(self, config_engine: ConfigEngine):
        """Test generating settings with MCP servers."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            mcp_servers={
                "test_server": McpServerPreset(
                    enabled=True,
                    command="npx",
                    args=["-y", "test-server"],
                    estimated_tokens=100,
                ),
            },
        )

        settings = config_engine.generate_settings(preset)

        assert "test_server" in settings.mcpServers
        assert settings.mcpServers["test_server"].command == "npx"

    def test_generate_settings_skips_disabled_servers(self, config_engine: ConfigEngine):
        """Test that disabled MCP servers are not included."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            mcp_servers={
                "enabled": McpServerPreset(enabled=True, command="cmd1"),
                "disabled": McpServerPreset(enabled=False, command="cmd2"),
            },
        )

        settings = config_engine.generate_settings(preset)

        assert "enabled" in settings.mcpServers
        assert "disabled" not in settings.mcpServers

    def test_generate_settings_with_custom_overrides(self, config_engine: ConfigEngine):
        """Test generating settings with custom overrides."""
        preset = PresetConfig(
            name="test",
            description="Test preset",
        )

        custom = {
            "env": {
                "CUSTOM_VAR": "custom_value",
            },
        }

        settings = config_engine.generate_settings(preset, custom=custom)

        assert settings.env.get("CUSTOM_VAR") == "custom_value"
        # Original env should still be present
        assert "OHMYCLAUDE_ROOT" in settings.env

    def test_generate_settings_from_real_preset(self, config_engine: ConfigEngine):
        """Test generating settings from a real preset file."""
        preset = config_engine.load_preset("starter")
        settings = config_engine.generate_settings(preset)

        assert settings.model == preset.model
        assert settings.alwaysThinkingEnabled == preset.always_thinking_enabled

    def test_merge_configs(self, config_engine: ConfigEngine):
        """Test merging configurations."""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}}

        result = config_engine.merge_configs(base, override)

        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3


class TestConfigEngineIntegration:
    """Integration tests for ConfigEngine with real templates."""

    @pytest.fixture
    def config_engine(self) -> ConfigEngine:
        """Create a ConfigEngine instance."""
        return ConfigEngine()

    def test_render_general_claude_md(self, config_engine: ConfigEngine):
        """Test rendering general CLAUDE.md template."""
        preset = config_engine.load_preset("starter")
        content = config_engine.render_template(
            "claude_md/general.md.j2",
            {"config": preset, "user_name": "TestUser"},
        )

        assert "Claude Code" in content or "工作规则" in content
        assert preset.name in content or "starter" in content

    def test_render_full_claude_md(self, config_engine: ConfigEngine):
        """Test rendering full CLAUDE.md template."""
        preset = config_engine.load_preset("full")
        content = config_engine.render_template(
            "claude_md/full.md.j2",
            {"config": preset, "user_name": "TestUser"},
        )

        assert len(content) > 1000  # Full template should be substantial
        # Check for CodexMCP section if include_codex is True
        if preset.include_codex:
            assert "CodexMCP" in content or "Codex" in content

    def test_all_presets_generate_valid_settings(self, config_engine: ConfigEngine):
        """Test that all presets generate valid settings."""
        for preset_name in config_engine.list_presets():
            preset = config_engine.load_preset(preset_name)
            settings = config_engine.generate_settings(preset)

            # Basic validation
            assert settings.model in ["sonnet", "opus", "haiku"]
            assert isinstance(settings.alwaysThinkingEnabled, bool)
            assert isinstance(settings.env, dict)
            assert isinstance(settings.mcpServers, dict)
