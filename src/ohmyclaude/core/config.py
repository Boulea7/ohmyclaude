"""Configuration engine for OhMyClaude.

This module provides the ConfigEngine class for loading presets, rendering templates,
and generating Claude Code configurations.
"""

from typing import Any

from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined
from ruamel.yaml import YAML

from ohmyclaude.core.merge import deep_merge
from ohmyclaude.core.paths import CLAUDE_DIR, get_presets_dir, get_project_templates_dir
from ohmyclaude.models.presets import PresetConfig
from ohmyclaude.models.settings import SettingsConfig

# Configure YAML parser to preserve comments
yaml = YAML()
yaml.preserve_quotes = True


class ConfigEngine:
    """Configuration engine for loading presets and generating configs.

    This class is responsible for:
    - Loading preset configurations from YAML files
    - Rendering Jinja2 templates (CLAUDE.md, commands, etc.)
    - Generating settings.json content
    - Merging configurations

    Example:
        >>> engine = ConfigEngine()
        >>> preset = engine.load_preset("standard")
        >>> settings = engine.generate_settings(preset)
    """

    def __init__(self):
        """Initialize the configuration engine."""
        self._init_template_env()
        self.presets_dir = get_presets_dir()

    def _init_template_env(self) -> None:
        """Initialize Jinja2 template environment."""
        templates_dir = get_project_templates_dir()

        # Use FileSystemLoader for development, PackageLoader for installed package
        if templates_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
                undefined=StrictUndefined,
            )
        else:
            # Fallback to package loader
            self.env = Environment(
                loader=PackageLoader("ohmyclaude", "templates"),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
                undefined=StrictUndefined,
            )

    def load_preset(self, name: str) -> PresetConfig:
        """Load a preset configuration from YAML file.

        Args:
            name: Preset name (starter, standard, full)

        Returns:
            PresetConfig instance

        Raises:
            FileNotFoundError: If preset file doesn't exist
            ValueError: If preset file is invalid
        """
        preset_file = self.presets_dir / f"{name}.yaml"

        if not preset_file.exists():
            raise FileNotFoundError(f"Preset '{name}' not found at {preset_file}")

        with open(preset_file, encoding="utf-8") as f:
            data = yaml.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid preset file: {preset_file}")

        return PresetConfig(**data)

    def list_presets(self) -> list[str]:
        """List available preset names.

        Returns:
            List of preset names
        """
        return [
            f.stem
            for f in self.presets_dir.glob("*.yaml")
            if f.is_file()
        ]

    def render_template(self, template_path: str, context: dict[str, Any]) -> str:
        """Render a Jinja2 template.

        Args:
            template_path: Path to template relative to templates directory
            context: Template context variables

        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_path)
        return template.render(**context)

    def generate_settings(
        self,
        preset: PresetConfig,
        custom: dict[str, Any] | None = None,
    ) -> SettingsConfig:
        """Generate settings.json configuration from preset.

        Args:
            preset: Preset configuration
            custom: Optional custom overrides

        Returns:
            SettingsConfig instance ready to write
        """
        # Build base settings from preset
        settings_dict: dict[str, Any] = {
            "model": preset.model,
            "alwaysThinkingEnabled": preset.always_thinking_enabled,
            "env": {
                # OHMYCLAUDE_ROOT points to ~/.claude where hooks are installed.
                # This is different from shell.py's OHMYCLAUDE_ROOT (~/.ohmyclaude)
                # which is for OhMyClaude CLI tools. Claude Code reads this env
                # from settings.json when executing hooks.
                "OHMYCLAUDE_ROOT": str(CLAUDE_DIR),
            },
            "permissions": {
                "additionalDirectories": [],
                "allow": [],
                "deny": [],
                "ask": [],
            },
            "mcpServers": {},
            "hooks": {},
        }

        # Add MCP servers
        for name, server in preset.get_enabled_mcp_servers().items():
            server_config: dict[str, Any] = {}

            if server.transport == "stdio":
                if server.command:
                    server_config["command"] = server.command
                if server.args:
                    server_config["args"] = server.args
            elif server.transport == "sse":
                if not server.url:
                    raise ValueError(f"Missing url for sse MCP server '{name}'")
                server_config["url"] = server.url
            else:
                raise ValueError(f"Unsupported transport '{server.transport}' for MCP '{name}'")

            if server.env:
                server_config["env"] = server.env

            settings_dict["mcpServers"][name] = server_config

        # Add hooks
        for event_name, hooks_list in preset.hooks.items():
            settings_dict["hooks"][event_name] = []
            for hook in hooks_list:
                if isinstance(hook, dict):
                    settings_dict["hooks"][event_name].append(hook)
                else:
                    settings_dict["hooks"][event_name].append(hook.model_dump())

        # Apply custom overrides
        if custom:
            settings_dict = deep_merge(settings_dict, custom)

        return SettingsConfig(**settings_dict)

    def merge_configs(self, base: dict, override: dict) -> dict:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        return deep_merge(base, override)
