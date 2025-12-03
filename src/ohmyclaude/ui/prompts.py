"""Interactive prompts using InquirerPy.

Provides user-friendly interactive selection for configuration options.
"""

from typing import Literal

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console

console = Console()

PresetType = Literal["starter", "standard", "full"]
ClaudeMdTemplate = Literal["general", "frontend", "backend", "ml"]


def select_preset() -> PresetType:
    """Select a preset package interactively.

    Returns:
        The selected preset name.
    """
    result = inquirer.select(
        message="Select a preset package / 选择预设包:",
        choices=[
            Choice(
                value="starter",
                name="Starter - 入门配置 (Minimal, ~3,300 tokens)"
            ),
            Choice(
                value="standard",
                name="Standard - 标准配置 (Recommended, ~5,500 tokens)"
            ),
            Choice(
                value="full",
                name="Full - 完整配置 (All features, ~8,800 tokens)"
            ),
        ],
        default="standard",
        instruction="(Use arrow keys to navigate, Enter to select)",
    ).execute()

    return result


def select_claude_md_template() -> ClaudeMdTemplate:
    """Select a CLAUDE.md template interactively.

    Returns:
        The selected template name.
    """
    result = inquirer.select(
        message="Select CLAUDE.md template / 选择 CLAUDE.md 模板:",
        choices=[
            Choice(value="general", name="General - 通用开发者"),
            Choice(value="frontend", name="Frontend - 前端开发 (React/Vue)"),
            Choice(value="backend", name="Backend - 后端开发 (Python/Go)"),
            Choice(value="ml", name="ML/RL - 机器学习研究者"),
        ],
        default="general",
    ).execute()

    return result


def select_mcp_packages(current: list[str] | None = None) -> list[str]:
    """Select MCP packages to install.

    Args:
        current: Currently selected packages (for default values).

    Returns:
        List of selected package names.
    """
    default_choices = current or ["basic"]

    result = inquirer.checkbox(
        message="Select MCP packages / 选择 MCP 包:",
        choices=[
            Choice(value="basic", name="Basic - filesystem + context7", enabled="basic" in default_choices),
            Choice(value="web", name="Web - web-reader + web-search", enabled="web" in default_choices),
            Choice(value="advanced", name="Advanced - unified-diff + zai-mcp-server", enabled="advanced" in default_choices),
        ],
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    return result


def select_commands(current: list[str] | None = None) -> list[str]:
    """Select slash commands to install.

    Args:
        current: Currently selected commands.

    Returns:
        List of selected command names.
    """
    default_choices = current or ["commit", "review", "test"]

    result = inquirer.checkbox(
        message="Select slash commands / 选择斜杠命令:",
        choices=[
            Choice(value="commit", name="/commit - Smart Git commit", enabled="commit" in default_choices),
            Choice(value="review", name="/review - Code review", enabled="review" in default_choices),
            Choice(value="test", name="/test - Run tests", enabled="test" in default_choices),
            Choice(value="codex", name="/codex - Delegate to Codex", enabled="codex" in default_choices),
        ],
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    return result


def confirm_action(message: str, default: bool = True) -> bool:
    """Confirm an action with yes/no prompt.

    Args:
        message: The confirmation message.
        default: Default value if user just presses Enter.

    Returns:
        True if user confirmed, False otherwise.
    """
    result = inquirer.confirm(
        message=message,
        default=default,
    ).execute()

    return result


def input_text(message: str, default: str = "", validate: bool = False) -> str:
    """Get text input from user.

    Args:
        message: The prompt message.
        default: Default value.
        validate: Whether to validate non-empty input.

    Returns:
        The user input string.
    """
    result = inquirer.text(
        message=message,
        default=default,
        validate=lambda x: len(x) > 0 if validate else True,
        invalid_message="Input cannot be empty.",
    ).execute()

    return result


def fuzzy_select_mcp(available: list[dict]) -> list[str]:
    """Fuzzy search and select MCP servers.

    Args:
        available: List of available MCP server configs with 'name' and 'description'.

    Returns:
        List of selected MCP server names.
    """
    choices = [
        Choice(value=mcp["name"], name=f"{mcp['name']} - {mcp.get('description', '')}")
        for mcp in available
    ]

    result = inquirer.fuzzy(
        message="Search and select MCP servers / 搜索并选择 MCP 服务器:",
        choices=choices,
        multiselect=True,
        instruction="(Type to filter, Space to select, Enter to confirm)",
    ).execute()

    return result


def select_provider() -> str:
    """Select an API provider interactively.

    Returns:
        The selected provider name.
    """
    result = inquirer.select(
        message="Select API provider / 选择 API 供应商:",
        choices=[
            Choice(value="official", name="Official - Anthropic 官方 (需订阅)"),
            Choice(value="glm", name="GLM - 智谱 AI (国内访问优化)"),
            Choice(value="88code", name="88Code - 第三方代理"),
            Choice(value="deepseek", name="DeepSeek - 高性价比"),
            Choice(value="custom", name="Custom - 自定义供应商"),
        ],
        default="official",
    ).execute()

    return result


if __name__ == "__main__":
    # Test prompts
    print("Testing prompts...")

    preset = select_preset()
    print(f"Selected preset: {preset}")

    template = select_claude_md_template()
    print(f"Selected template: {template}")

    confirmed = confirm_action("Continue with installation?")
    print(f"Confirmed: {confirmed}")
