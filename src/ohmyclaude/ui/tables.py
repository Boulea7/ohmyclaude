"""Table display utilities using Rich.

Provides formatted table output for installation results and configuration display.
"""

from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def create_result_table(result: dict[str, Any]) -> Table:
    """Create a result table from installation result.

    Args:
        result: Installation result dictionary with 'installed', 'skipped', 'errors' keys.

    Returns:
        Rich Table instance.
    """
    table = Table(
        title="Installation Result / 安装结果",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Type / 类型", style="cyan", width=15)
    table.add_column("Name / 名称", style="green", width=30)
    table.add_column("Status / 状态", width=15)

    # Add installed items
    for item in result.get("installed", []):
        item_type = item.get("type", "unknown")
        item_name = item.get("name", "unknown")
        table.add_row(item_type, item_name, "[green]Installed[/]")

    # Add skipped items
    for item in result.get("skipped", []):
        item_type = item.get("type", "unknown")
        item_name = item.get("name", "unknown")
        reason = item.get("reason", "")
        table.add_row(item_type, item_name, f"[yellow]Skipped[/] ({reason})")

    # Add errors
    for item in result.get("errors", []):
        item_type = item.get("type", "unknown")
        error = item.get("error", "unknown error")
        table.add_row(item_type, f"[red]{error}[/]", "[red]Failed[/]")

    return table


def create_preset_table() -> Table:
    """Create a table showing preset package comparison.

    Returns:
        Rich Table instance.
    """
    table = Table(
        title="Preset Packages / 预设包",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Package / 包", style="cyan", width=12)
    table.add_column("MCP Servers", width=30)
    table.add_column("Commands", width=20)
    table.add_column("Token Cost", width=15)

    table.add_row(
        "[green]Starter[/]",
        "filesystem, context7",
        "/commit, /review",
        "~3,300 (~2%)",
    )
    table.add_row(
        "[blue]Standard[/]",
        "+ web-reader, web-search",
        "+ /test, /codex",
        "~5,500 (~3.5%)",
    )
    table.add_row(
        "[magenta]Full[/]",
        "+ zai-mcp, unified-diff",
        "+ /dev-docs",
        "~8,800 (~6%)",
    )

    return table


def create_provider_table(providers: list[dict], current: str | None = None) -> Table:
    """Create a table showing available API providers.

    Args:
        providers: List of provider configurations.
        current: Name of current provider (to highlight).

    Returns:
        Rich Table instance.
    """
    table = Table(
        title="API Providers / API 供应商",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Name / 名称", style="cyan", width=12)
    table.add_column("Display Name", width=20)
    table.add_column("Status", width=12)
    table.add_column("Description / 说明", width=35)

    for provider in providers:
        name = provider.get("name", "unknown")
        display_name = provider.get("display_name", name)
        description = provider.get("description", "")

        if current and name == current:
            status = "[bold green]Current[/]"
            name_style = f"[bold green]{name}[/]"
        else:
            status = ""
            name_style = name

        table.add_row(name_style, display_name, status, description)

    return table


def create_mcp_table(mcps: list[dict]) -> Table:
    """Create a table showing MCP server configuration.

    Args:
        mcps: List of MCP server configurations.

    Returns:
        Rich Table instance.
    """
    table = Table(
        title="MCP Servers",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Transport", width=10)
    table.add_column("Description", width=35)
    table.add_column("Tokens", width=10)

    for mcp in mcps:
        name = mcp.get("name", "unknown")
        transport = mcp.get("transport", "stdio")
        description = mcp.get("description", "")
        tokens = mcp.get("estimated_tokens", "?")

        table.add_row(name, transport, description, f"~{tokens}")

    return table


def create_health_table(checks: list[dict]) -> Table:
    """Create a table showing health check results.

    Args:
        checks: List of health check results.

    Returns:
        Rich Table instance.
    """
    table = Table(
        title="Health Check / 健康检查",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Check / 检查项", style="cyan", width=30)
    table.add_column("Status / 状态", width=15)
    table.add_column("Details / 详情", width=40)

    for check in checks:
        name = check.get("name", "unknown")
        status = check.get("status", "unknown")
        details = check.get("details", "")

        if status == "pass":
            status_display = "[green]PASS[/]"
        elif status == "warn":
            status_display = "[yellow]WARN[/]"
        else:
            status_display = "[red]FAIL[/]"

        table.add_row(name, status_display, details)

    return table


def show_summary(installed_count: int, skipped_count: int, error_count: int) -> None:
    """Show a summary line after installation.

    Args:
        installed_count: Number of successfully installed items.
        skipped_count: Number of skipped items.
        error_count: Number of errors.
    """
    console.print()

    parts = []
    if installed_count > 0:
        parts.append(f"[green]{installed_count} installed[/]")
    if skipped_count > 0:
        parts.append(f"[yellow]{skipped_count} skipped[/]")
    if error_count > 0:
        parts.append(f"[red]{error_count} failed[/]")

    summary = ", ".join(parts) if parts else "No changes"
    console.print(f"Summary: {summary}")


if __name__ == "__main__":
    # Test tables
    print("Testing result table...")

    result = {
        "installed": [
            {"type": "mcp", "name": "filesystem"},
            {"type": "mcp", "name": "context7"},
            {"type": "command", "name": "/commit"},
            {"type": "hook", "name": "SessionStart"},
        ],
        "skipped": [
            {"type": "mcp", "name": "web-reader", "reason": "requires GLM key"},
        ],
        "errors": [
            {"type": "command", "error": "Template not found: /custom"},
        ],
    }

    table = create_result_table(result)
    console.print(table)

    show_summary(4, 1, 1)

    print("\nTesting preset table...")
    preset_table = create_preset_table()
    console.print(preset_table)
