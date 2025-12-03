"""CLI entry point for OhMyClaude.

This module provides the main command-line interface using Click.
"""

import click
from rich.console import Console

from ohmyclaude import __version__
from ohmyclaude.ui.logo import show_logo, show_welcome, show_goodbye

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """OhMyClaude - Claude Code 一键配置工具

    A CLI tool to help Chinese developers configure Claude Code quickly.

    \b
    Quick start:
        ohmyclaude setup          Run the configuration wizard
        ohmyclaude setup -p full  Install full preset directly
        ohmyclaude doctor         Check configuration health
        ohmyclaude switch glm     Switch to GLM provider
    """
    pass


@cli.command()
@click.option(
    "--preset", "-p",
    type=click.Choice(["starter", "standard", "full"]),
    help="Preset package to install (skip interactive selection)."
)
@click.option(
    "--no-interactive", "-y",
    is_flag=True,
    help="Non-interactive mode, use default values."
)
def setup(preset: str | None, no_interactive: bool) -> None:
    """Run the configuration wizard.

    This command guides you through setting up Claude Code with
    pre-configured templates, MCP servers, hooks, and commands.

    \b
    Preset packages:
        starter   - Minimal configuration for beginners
        standard  - Recommended for daily development
        full      - All features including CodexMCP
    """
    show_logo()
    show_welcome()

    if preset:
        console.print(f"[blue]Selected preset: {preset}[/]")
    else:
        console.print("[dim]Run with --preset to skip interactive selection[/]")

    # TODO: Implement actual setup logic in Phase 2
    console.print("\n[yellow]Setup wizard not yet implemented.[/]")
    console.print("[dim]This will be completed in Phase 2.[/]")


@cli.command()
def doctor() -> None:
    """Check configuration health status.

    Verifies that all Claude Code configurations are properly set up
    and all MCP servers are accessible.
    """
    show_logo(show_tagline=False)
    console.print("[bold]Running health check...[/]\n")

    # TODO: Implement actual health check in Phase 2
    console.print("[yellow]Doctor command not yet implemented.[/]")
    console.print("[dim]This will be completed in Phase 2.[/]")


@cli.command()
@click.option("--remove", is_flag=True, help="Remove shell integration.")
@click.option("--status", is_flag=True, help="Show current shell integration status.")
def init(remove: bool, status: bool) -> None:
    """Initialize shell environment for OhMyClaude.

    Configures your shell RC file (~/.zshrc, ~/.bashrc, or config.fish)
    to source OhMyClaude environment variables on startup.

    This operation is idempotent - safe to run multiple times.

    \b
    Examples:
        omc init              Configure shell integration
        omc init --status     Check if shell is configured
        omc init --remove     Remove shell integration
    """
    from ohmyclaude.core import ShellIntegration, get_shell_info

    shell = ShellIntegration()

    if status:
        info = get_shell_info()
        console.print(f"[bold]Shell Integration Status[/]\n")
        console.print(f"  Shell type:    [cyan]{info['shell']}[/]")
        console.print(f"  RC file:       [dim]{info['rc_path']}[/]")
        if info["is_installed"]:
            console.print(f"  Status:        [green]Configured[/]")
        else:
            console.print(f"  Status:        [yellow]Not configured[/]")
        return

    if remove:
        console.print(f"[blue]Removing shell integration from {shell.rc_path}...[/]")
        if shell.remove():
            console.print("[green]Shell integration removed successfully![/]")
            console.print("[dim]Restart your shell or run: source ~/.zshrc[/]")
        else:
            console.print("[yellow]Nothing to remove.[/]")
        return

    # Default: install
    console.print(f"[blue]Configuring shell integration for {shell.shell}...[/]")
    console.print(f"[dim]RC file: {shell.rc_path}[/]\n")

    if shell.inject_source():
        console.print("[green]Shell integration configured successfully![/]")
        console.print()
        console.print("[bold]Next steps:[/]")
        console.print("  1. Restart your shell, or run:")
        if shell.shell == "fish":
            console.print(f"     [cyan]source {shell.rc_path}[/]")
        else:
            console.print(f"     [cyan]source {shell.rc_path}[/]")
        console.print("  2. Run [cyan]omc setup[/] to configure Claude Code")
    else:
        console.print("[red]Failed to configure shell integration.[/]")


@cli.command()
@click.argument("provider", required=False)
@click.option("--token", "-t", help="API Token (overrides environment variable).")
@click.option("--base-url", "-u", help="API Base URL for custom providers.")
@click.option("--skip-codex", is_flag=True, help="Skip Codex configuration update.")
@click.option("--list", "-l", "list_all", is_flag=True, help="List available providers.")
def switch(
    provider: str | None,
    token: str | None,
    base_url: str | None,
    skip_codex: bool,
    list_all: bool
) -> None:
    """Switch API provider.

    Quickly switch between different API providers like official Anthropic,
    GLM (Zhipu AI), 88Code, or DeepSeek.

    \b
    Examples:
        ohmyclaude switch glm         Switch to GLM provider
        ohmyclaude switch official    Switch back to official API
        ohmyclaude switch --list      List all available providers
    """
    if list_all or not provider:
        console.print("[bold]Available API Providers:[/]\n")
        console.print("  [cyan]official[/]  - Anthropic official API (requires subscription)")
        console.print("  [cyan]glm[/]       - Zhipu AI (China optimized)")
        console.print("  [cyan]88code[/]    - Third-party proxy")
        console.print("  [cyan]deepseek[/]  - DeepSeek V3 (cost-effective)")
        console.print()
        console.print("[dim]Use: ohmyclaude switch <provider>[/]")
        return

    console.print(f"[blue]Switching to provider: {provider}[/]")

    # TODO: Implement actual switching logic in Phase 6
    console.print("\n[yellow]Switch command not yet implemented.[/]")
    console.print("[dim]This will be completed in Phase 6.[/]")


@cli.group()
def provider() -> None:
    """Manage API providers.

    Add, remove, and list custom API providers.
    """
    pass


@provider.command("list")
def provider_list() -> None:
    """List all available providers."""
    console.print("[bold]Configured API Providers:[/]\n")
    console.print("  [green]official[/]  - Anthropic official API")
    console.print("  [dim]glm[/]       - Zhipu AI")
    console.print("  [dim]88code[/]    - Third-party proxy")
    console.print("  [dim]deepseek[/]  - DeepSeek")
    console.print()
    console.print("[dim]Use: ohmyclaude provider add <name> to add custom provider[/]")


@provider.command("show")
def provider_show() -> None:
    """Show current provider configuration."""
    # TODO: Implement in Phase 6
    console.print("[yellow]Current provider detection not yet implemented.[/]")


@provider.command("add")
@click.argument("name")
@click.option("--base-url", "-u", required=True, help="API base URL.")
@click.option("--token-env", required=True, help="Environment variable name for token.")
def provider_add(name: str, base_url: str, token_env: str) -> None:
    """Add a custom API provider."""
    console.print(f"[blue]Adding custom provider: {name}[/]")
    console.print(f"  Base URL: {base_url}")
    console.print(f"  Token env: {token_env}")

    # TODO: Implement in Phase 6
    console.print("\n[yellow]Provider add not yet implemented.[/]")


@cli.command("export")
@click.argument("output", type=click.Path())
def export_config(output: str) -> None:
    """Export current configuration to a file.

    Creates a backup of your Claude Code configuration that can be
    imported on another machine or shared with team members.
    """
    console.print(f"[blue]Exporting configuration to: {output}[/]")

    # TODO: Implement in Phase 2
    console.print("\n[yellow]Export command not yet implemented.[/]")


@cli.command("import")
@click.argument("input_file", type=click.Path(exists=True))
def import_config(input_file: str) -> None:
    """Import configuration from a file.

    Restores Claude Code configuration from a previously exported file.
    """
    console.print(f"[blue]Importing configuration from: {input_file}[/]")

    # TODO: Implement in Phase 2
    console.print("\n[yellow]Import command not yet implemented.[/]")


@cli.command()
@click.option("--check", is_flag=True, help="Only check for updates, don't apply.")
def update(check: bool) -> None:
    """Update configuration to the latest version.

    Checks for updates to OhMyClaude and applies new configurations
    while preserving your customizations.
    """
    if check:
        console.print("[blue]Checking for updates...[/]")
    else:
        console.print("[blue]Updating configuration...[/]")

    # TODO: Implement update logic
    console.print("\n[yellow]Update command not yet implemented.[/]")


if __name__ == "__main__":
    cli()
