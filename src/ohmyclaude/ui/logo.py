"""ASCII Logo display for OhMyClaude."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ohmyclaude import __version__

console = Console()

LOGO = r"""
 ╔═╗╦ ╦  ╔╦╗╦ ╦  ╔═╗╦  ╔═╗╦ ╦╔╦╗╔═╗
 ║ ║╠═╣  ║║║╚╦╝  ║  ║  ╠═╣║ ║ ║║╠╣
 ╚═╝╩ ╩  ╩ ╩ ╩   ╚═╝╩═╝╩ ╩╚═╝═╩╝╚═╝
"""

TAGLINE = "Claude Code 一键配置工具"
SUBTITLE = "One-click configuration for Claude Code"


def show_logo(show_tagline: bool = True) -> None:
    """Display the OhMyClaude ASCII logo with optional tagline.

    Args:
        show_tagline: Whether to show the tagline below the logo.
    """
    logo_text = Text(LOGO, style="bold blue")

    if show_tagline:
        content = Text()
        content.append(LOGO, style="bold blue")
        content.append("\n")
        content.append(f"      {TAGLINE}\n", style="cyan")
        content.append(f"      {SUBTITLE}", style="dim")
    else:
        content = logo_text

    panel = Panel(
        content,
        title=f"[bold]OhMyClaude v{__version__}[/]",
        border_style="blue",
        padding=(0, 2),
    )
    console.print(panel)


def show_welcome() -> None:
    """Display welcome message after logo."""
    console.print()
    console.print("[bold green]Welcome to OhMyClaude![/]")
    console.print()
    console.print("This wizard will help you configure Claude Code in minutes.")
    console.print("Use [cyan]--help[/] for more options.\n")


def show_goodbye() -> None:
    """Display goodbye message."""
    console.print()
    console.print("[bold green]Configuration complete![/]")
    console.print()
    console.print("Next steps:")
    console.print("  1. Restart Claude Code or open a new terminal")
    console.print("  2. Try the [cyan]/commit[/] command")
    console.print("  3. Run [cyan]ohmyclaude doctor[/] to verify configuration")
    console.print()


if __name__ == "__main__":
    # Test the logo display
    show_logo()
    show_welcome()
