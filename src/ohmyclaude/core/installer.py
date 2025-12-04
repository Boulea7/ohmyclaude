"""Installer for OhMyClaude.

This module provides the Installer class that writes configurations to target locations.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any

from ohmyclaude.core.atomic import atomic_write, save_json
from ohmyclaude.core.config import ConfigEngine
from ohmyclaude.core.paths import (
    CLAUDE_DIR,
    CLAUDE_MD_FILE,
    COMMANDS_DIR,
    HOOKS_DIR,
    SETTINGS_FILE,
    ensure_claude_dirs,
    get_project_templates_dir,
)
from ohmyclaude.models.presets import PresetConfig


class InstallResult:
    """Result of an installation operation."""

    def __init__(self):
        """Initialize install result."""
        self.installed: list[dict[str, Any]] = []
        self.skipped: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []

    def add_installed(self, item_type: str, name: str, path: str) -> None:
        """Record a successful installation."""
        self.installed.append({
            "type": item_type,
            "name": name,
            "path": path,
        })

    def add_skipped(self, item_type: str, name: str, reason: str) -> None:
        """Record a skipped item."""
        self.skipped.append({
            "type": item_type,
            "name": name,
            "reason": reason,
        })

    def add_error(self, item_type: str, name: str, error: str) -> None:
        """Record an error."""
        self.errors.append({
            "type": item_type,
            "name": name,
            "error": error,
        })

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "installed": self.installed,
            "skipped": self.skipped,
            "errors": self.errors,
            "success": len(self.errors) == 0,
            "summary": {
                "installed_count": len(self.installed),
                "skipped_count": len(self.skipped),
                "error_count": len(self.errors),
            },
        }


class Installer:
    """Installer for Claude Code configurations.

    This class handles writing configurations to target locations:
    - settings.json
    - CLAUDE.md
    - Slash commands
    - Hooks
    - MCP configurations

    Example:
        >>> engine = ConfigEngine()
        >>> preset = engine.load_preset("standard")
        >>> installer = Installer(preset, engine)
        >>> result = installer.install()
    """

    def __init__(self, preset: PresetConfig, engine: ConfigEngine | None = None):
        """Initialize installer.

        Args:
            preset: Preset configuration to install
            engine: Configuration engine (created if not provided)
        """
        self.preset = preset
        self.engine = engine or ConfigEngine()
        self.result = InstallResult()
        self.templates_dir = get_project_templates_dir()

    def install(self, skip_mcp: bool = False) -> dict[str, Any]:
        """Execute the complete installation.

        Args:
            skip_mcp: Skip MCP configuration

        Returns:
            Installation result dictionary
        """
        # Ensure directories exist
        ensure_claude_dirs()

        # Install components
        self._install_settings()
        self._install_claude_md()
        self._install_commands()
        self._install_hooks()

        if not skip_mcp:
            self._install_mcp()

        return self.result.to_dict()

    def _install_settings(self) -> None:
        """Install settings.json configuration."""
        try:
            settings = self.engine.generate_settings(self.preset)

            # Convert to dict for JSON serialization
            settings_dict = settings.model_dump(exclude_none=True)

            save_json(SETTINGS_FILE, settings_dict)

            self.result.add_installed(
                item_type="settings",
                name="settings.json",
                path=str(SETTINGS_FILE),
            )
        except Exception as e:
            self.result.add_error(
                item_type="settings",
                name="settings.json",
                error=str(e),
            )

    def _install_claude_md(self) -> None:
        """Install CLAUDE.md template."""
        try:
            # Validate template name to prevent path traversal
            template_key = self._safe_segment(self.preset.claude_md_template, "template")
            template_name = f"claude_md/{template_key}.md.j2"

            # Check if template exists
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                # Use default template
                template_name = "claude_md/general.md.j2"
                template_path = self.templates_dir / template_name

            if not template_path.exists():
                # Create a basic CLAUDE.md if no template
                content = self._generate_basic_claude_md()
            else:
                content = self.engine.render_template(template_name, {
                    "config": self.preset,
                    "user_name": self._get_user_name(),
                })

            with atomic_write(CLAUDE_MD_FILE) as f:
                f.write(content)

            self.result.add_installed(
                item_type="claude_md",
                name="CLAUDE.md",
                path=str(CLAUDE_MD_FILE),
            )
        except Exception as e:
            self.result.add_error(
                item_type="claude_md",
                name="CLAUDE.md",
                error=str(e),
            )

    def _install_commands(self) -> None:
        """Install slash commands."""
        COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

        commands_templates = self.templates_dir / "commands"
        if not commands_templates.exists():
            return

        for cmd_name in self.preset.commands:
            try:
                # Validate command name to prevent path traversal
                safe_cmd = self._safe_segment(cmd_name, "command")

                # Try .md.j2 template first, then .md
                template_file = commands_templates / f"{safe_cmd}.md.j2"
                if template_file.exists():
                    content = self.engine.render_template(
                        f"commands/{safe_cmd}.md.j2",
                        {"config": self.preset},
                    )
                else:
                    static_file = commands_templates / f"{safe_cmd}.md"
                    if static_file.exists():
                        content = static_file.read_text(encoding="utf-8")
                    else:
                        self.result.add_skipped(
                            item_type="command",
                            name=cmd_name,
                            reason="Template not found",
                        )
                        continue

                cmd_path = COMMANDS_DIR / f"{safe_cmd}.md"
                with atomic_write(cmd_path) as f:
                    f.write(content)

                self.result.add_installed(
                    item_type="command",
                    name=cmd_name,
                    path=str(cmd_path),
                )
            except Exception as e:
                self.result.add_error(
                    item_type="command",
                    name=cmd_name,
                    error=str(e),
                )

    def _install_hooks(self) -> None:
        """Install hook scripts to ~/.claude/hooks/.

        Copies hook scripts from templates based on hooks_preset:
        - basic: No scripts (inline commands only)
        - standard: No scripts (inline commands only)
        - full: All hook scripts for advanced workflows
        """
        # Define which scripts each preset needs
        preset_scripts: dict[str, list[str]] = {
            "basic": [],
            "standard": [],
            "full": [
                "skill-activation-prompt.ts",
                "skill-activation-prompt.sh",
                "post-tool-use-tracker.sh",
                "tsc-check.sh",
                "stop-build-check-enhanced.sh",
                "trigger-build-resolver.sh",
                "error-handling-reminder.ts",
                "error-handling-reminder.sh",
            ],
        }

        hooks_preset = self.preset.hooks_preset

        # Warn if hooks_preset is unknown
        if hooks_preset not in preset_scripts:
            self.result.add_skipped(
                item_type="hook",
                name=f"hooks_preset:{hooks_preset}",
                reason=f"Unknown hooks preset '{hooks_preset}', expected one of: {list(preset_scripts.keys())}",
            )
            return

        scripts_to_install = preset_scripts[hooks_preset]

        if not scripts_to_install:
            return

        hooks_templates = self.templates_dir / "hooks"
        if not hooks_templates.exists():
            self.result.add_error(
                item_type="hook",
                name="hooks_templates",
                error=f"Hooks templates directory not found: {hooks_templates}",
            )
            return

        HOOKS_DIR.mkdir(parents=True, exist_ok=True)

        for script_name in scripts_to_install:
            try:
                src = hooks_templates / script_name
                if not src.exists():
                    self.result.add_skipped(
                        item_type="hook",
                        name=script_name,
                        reason="Template not found",
                    )
                    continue

                dst = HOOKS_DIR / script_name
                shutil.copy2(src, dst)

                # Set executable permission for shell scripts (controlled chmod)
                if script_name.endswith(".sh"):
                    dst.chmod(0o755)

                self.result.add_installed(
                    item_type="hook",
                    name=script_name,
                    path=str(dst),
                )
            except Exception as e:
                self.result.add_error(
                    item_type="hook",
                    name=script_name,
                    error=str(e),
                )

    def _install_mcp(self) -> None:
        """Install MCP server configurations.

        Note: MCP configurations are embedded in settings.json,
        this method is for additional MCP-related setup.
        """
        # MCP configs are already in settings.json via generate_settings
        # This method can be used for additional MCP setup like
        # installing npm packages, creating env files, etc.
        pass

    @staticmethod
    def _safe_segment(value: str, label: str) -> str:
        """Guard against path traversal in user-supplied names.

        Args:
            value: User-supplied segment (template name, command name, etc.)
            label: Human-readable label for error messages

        Returns:
            The validated value

        Raises:
            ValueError: If the value contains path traversal patterns
        """
        if not value:
            raise ValueError(f"Invalid {label} name: empty value")
        if value.startswith(".") or ".." in value or "/" in value or "\\" in value:
            raise ValueError(f"Invalid {label} name: {value!r}")
        return value

    def _get_user_name(self) -> str:
        """Get the current user's name."""
        return os.environ.get("USER", os.environ.get("USERNAME", "User"))

    def _generate_basic_claude_md(self) -> str:
        """Generate a basic CLAUDE.md file."""
        return f"""# Claude Code 工作规则

> 由 OhMyClaude 自动生成
> 预设: {self.preset.name}

## 1. 核心原则

- **沟通语言**: 使用中文与用户交流
- **代码注释**: 使用英文编写注释和文档字符串
- **思维模式**: 追求简单实现 (KISS)，拒绝过度设计

## 2. 工作流程

### 开始任务前
1. 阅读项目文档 (README.md, CLAUDE.md)
2. 检查 Git 状态和项目结构
3. 确认需求，必要时提问

### 执行任务时
1. 遵循现有代码风格
2. 保持代码简洁
3. 添加必要的错误处理

### 完成任务后
1. 验证功能正常
2. 确保没有引入问题
3. 提供清晰的说明

## 3. Git 安全检查

提交前检查 .gitignore 是否包含:
- `.env`, `.env.*`
- `**/api_key*`, `**/secret*`
- `credentials*`, `*.pem`, `*.key`

---
*使用 OhMyClaude 配置 - {self.preset.description}*
"""
