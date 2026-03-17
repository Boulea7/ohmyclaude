"""UI utilities for consistent CLI output.

This module provides centralized UI components for:
- Status icons and colors
- Progress indicators
- Formatted panels and tables
- Consistent theming
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Literal, TypeVar

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.theme import Theme

if TYPE_CHECKING:
    from ohmyclaude.models.provider import ProviderConfig

# Unified color theme
OHMYCLAUDE_THEME = Theme(
    {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "dim": "dim",
        "highlight": "cyan",
        "provider": "magenta",
        "path": "dim cyan",
        "version": "green bold",
    }
)

# Status icons for consistent visual feedback
STATUS_ICONS = {
    "ok": "✓",
    "success": "✓",
    "warn": "⚠",
    "warning": "⚠",
    "error": "✗",
    "fail": "✗",
    "info": "ℹ",
    "pending": "○",
    "progress": "◐",
    "skip": "⊘",
}

# Status colors mapping
STATUS_COLORS = {
    "ok": "green",
    "success": "green",
    "warn": "yellow",
    "warning": "yellow",
    "error": "red",
    "fail": "red",
    "info": "blue",
    "pending": "dim",
    "progress": "cyan",
    "skip": "dim",
}

T = TypeVar("T")


@dataclass
class StatusMessage:
    """A formatted status message with icon and color."""

    status: Literal["ok", "warn", "error", "info", "pending", "progress", "skip"]
    message: str
    detail: str | None = None

    def __rich__(self) -> str:
        icon = STATUS_ICONS.get(self.status, "•")
        color = STATUS_COLORS.get(self.status, "white")
        base = f"[{color}]{icon}[/{color}] {self.message}"
        if self.detail:
            base += f" [dim]({self.detail})[/dim]"
        return base


def create_themed_console(stderr: bool = False) -> Console:
    """Create a console with the OhMyClaude theme.

    Args:
        stderr: Whether to output to stderr

    Returns:
        Themed Console instance
    """
    return Console(theme=OHMYCLAUDE_THEME, stderr=stderr)


def print_status(
    console: Console,
    status: Literal["ok", "warn", "error", "info", "pending", "progress", "skip"],
    message: str,
    detail: str | None = None,
) -> None:
    """Print a formatted status message.

    Args:
        console: Rich Console instance
        status: Status type
        message: Main message
        detail: Optional detail in parentheses
    """
    msg = StatusMessage(status=status, message=message, detail=detail)
    console.print(msg)


def print_error_panel(
    console: Console,
    title: str,
    message: str,
    suggestion: str | None = None,
) -> None:
    """Print an error in a formatted panel.

    Args:
        console: Rich Console instance
        title: Panel title
        message: Error message
        suggestion: Optional suggestion for resolution
    """
    content = f"[red]{message}[/red]"
    if suggestion:
        content += f"\n\n[dim]Suggestion: {suggestion}[/dim]"

    panel = Panel(
        content,
        title=f"[red bold]{STATUS_ICONS['error']} {title}[/red bold]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def print_success_panel(
    console: Console,
    title: str,
    message: str,
    items: list[str] | None = None,
) -> None:
    """Print a success message in a formatted panel.

    Args:
        console: Rich Console instance
        title: Panel title
        message: Success message
        items: Optional list of items to display
    """
    content = f"[green]{message}[/green]"
    if items:
        content += "\n\n" + "\n".join(f"  • {item}" for item in items)

    panel = Panel(
        content,
        title=f"[green bold]{STATUS_ICONS['success']} {title}[/green bold]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def create_installation_progress() -> Progress:
    """Create a progress bar for installation tasks.

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        transient=True,
    )


class InstallationTracker:
    """Track installation progress with visual feedback.

    Example:
        >>> with InstallationTracker(console) as tracker:
        ...     tracker.start_phase("Installing commands", total=5)
        ...     for cmd in commands:
        ...         install(cmd)
        ...         tracker.advance()
    """

    def __init__(self, console: Console):
        """Initialize tracker.

        Args:
            console: Rich Console instance
        """
        self.console = console
        self.progress = create_installation_progress()
        self._current_task: TaskID | None = None
        self._installed: list[str] = []
        self._skipped: list[str] = []
        self._errors: list[str] = []

    def __enter__(self) -> InstallationTracker:
        self.progress.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.progress.stop()

    def start_phase(self, description: str, total: int) -> None:
        """Start a new installation phase.

        Args:
            description: Phase description
            total: Total items to install
        """
        self._current_task = self.progress.add_task(description, total=total)

    def advance(self, item_name: str | None = None, status: str = "ok") -> None:
        """Advance progress and record result.

        Args:
            item_name: Name of the item (for tracking)
            status: Result status ("ok", "skip", "error")
        """
        if self._current_task is not None:
            self.progress.advance(self._current_task)

        if item_name:
            if status == "ok":
                self._installed.append(item_name)
            elif status == "skip":
                self._skipped.append(item_name)
            elif status == "error":
                self._errors.append(item_name)

    def get_summary(self) -> dict[str, object]:
        """Get installation summary.

        Returns:
            Dictionary with installed, skipped, and error counts
        """
        return {
            "installed": self._installed,
            "skipped": self._skipped,
            "errors": self._errors,
            "installed_count": len(self._installed),
            "skipped_count": len(self._skipped),
            "error_count": len(self._errors),
        }


def create_provider_table(
    providers: dict[str, ProviderConfig],
    current: str | None = None,
) -> Table:
    """Create a formatted table of providers.

    Args:
        providers: Dictionary of provider name to ProviderConfig
        current: Name of the current provider (highlighted)

    Returns:
        Formatted Rich Table
    """
    table = Table(
        title="Available Providers",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("", width=3)  # Status icon
    table.add_column("Name", style="bold")
    table.add_column("Display Name")
    table.add_column("Type", style="dim")
    table.add_column("Base URL", style="dim")

    for name, provider in sorted(providers.items()):
        is_current = name == current
        icon = STATUS_ICONS["ok"] if is_current else ""
        icon_style = "green" if is_current else ""

        name_style = "green bold" if is_current else ""
        type_label = "Built-in" if provider.is_builtin else "Custom"

        table.add_row(
            f"[{icon_style}]{icon}[/{icon_style}]",
            f"[{name_style}]{name}[/{name_style}]",
            provider.display_name,
            type_label,
            provider.anthropic_base_url or "(default)",
        )

    return table


def format_version_info(current: str, latest: str, is_outdated: bool) -> str:
    """Format version comparison output.

    Args:
        current: Current version
        latest: Latest version
        is_outdated: Whether an update is available

    Returns:
        Formatted string
    """
    if is_outdated:
        return (
            f"  Current: [yellow]{current}[/yellow]\n"
            f"  Latest:  [green]{latest}[/green] [yellow](update available)[/yellow]"
        )
    return (
        f"  Current: [green]{current}[/green]\n"
        f"  Latest:  [green]{latest}[/green] [dim](up to date)[/dim]"
    )


def iter_with_progress(
    items: list[T],
    description: str,
    console: Console | None = None,
) -> Iterator[T]:
    """Iterate over items with a progress bar.

    Args:
        items: Items to iterate over
        description: Progress description
        console: Optional console (creates one if not provided)

    Yields:
        Items from the list
    """
    if not items:
        return

    with create_installation_progress() as progress:
        task = progress.add_task(description, total=len(items))
        for item in items:
            yield item
            progress.advance(task)
