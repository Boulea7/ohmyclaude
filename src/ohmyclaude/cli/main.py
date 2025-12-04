"""CLI entry point for OhMyClaude.

This module provides the main command-line interface using Click.
"""

import shutil
import tarfile
import tempfile
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ohmyclaude import __version__
from ohmyclaude.core import (
    BackupManager,
    ConfigEngine,
    Installer,
    ShellIntegration,
    CLAUDE_MD_FILE,
    COMMANDS_DIR,
    HOOKS_DIR,
    SETTINGS_FILE,
)
from ohmyclaude.ui.logo import show_logo, show_welcome, show_goodbye
from ohmyclaude.ui.prompts import select_preset

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

    # 1. Select preset (interactively or from option)
    if preset:
        console.print(f"[blue]Using preset: {preset}[/]\n")
    elif no_interactive:
        preset = "standard"
        console.print(f"[blue]Using default preset: {preset}[/]\n")
    else:
        console.print("[dim]Tip: Use --preset / -p to skip this selection[/]\n")
        preset = select_preset()
        console.print()

    # 2. Load preset configuration
    try:
        engine = ConfigEngine()
        preset_config = engine.load_preset(preset)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/]")
        raise SystemExit(1)

    # 3. Create backup if existing config
    backup_mgr = BackupManager()
    if SETTINGS_FILE.exists():
        backup_path = backup_mgr.create_backup(tag="pre-setup")
        console.print(f"[dim]Backed up existing config to: {backup_path.name}[/]\n")

    # 4. Install configuration
    console.print("[bold]Installing configuration...[/]\n")
    installer = Installer(preset_config, engine)
    result = installer.install()

    # 5. Show results
    _show_install_result(result)

    # 6. Show next steps
    console.print("\n[green bold]Configuration complete![/]")
    console.print()
    console.print("[bold]Next steps:[/]")
    console.print("  1. Run [cyan]omc doctor[/] to verify configuration")
    console.print("  2. Run [cyan]omc init[/] to configure shell environment")
    console.print("  3. Restart Claude Code to apply changes")


def _show_install_result(result: dict) -> None:
    """Display installation result in a table."""
    table = Table(title="Installation Summary", show_header=True, header_style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Installed", style="green")
    table.add_column("Skipped", style="yellow")
    table.add_column("Errors", style="red")

    # Count by category
    installed = result.get("installed", [])
    skipped = result.get("skipped", [])
    errors = result.get("errors", [])

    categories = {}
    for item in installed:
        cat = item.get("type", "other")
        categories.setdefault(cat, {"installed": 0, "skipped": 0, "errors": 0})
        categories[cat]["installed"] += 1

    for item in skipped:
        cat = item.get("type", "other")
        categories.setdefault(cat, {"installed": 0, "skipped": 0, "errors": 0})
        categories[cat]["skipped"] += 1

    for item in errors:
        cat = item.get("type", "other")
        categories.setdefault(cat, {"installed": 0, "skipped": 0, "errors": 0})
        categories[cat]["errors"] += 1

    # Add rows
    for cat, counts in sorted(categories.items()):
        table.add_row(
            cat,
            str(counts["installed"]) if counts["installed"] else "-",
            str(counts["skipped"]) if counts["skipped"] else "-",
            str(counts["errors"]) if counts["errors"] else "-",
        )

    console.print(table)

    # Show error details if any
    if errors:
        console.print("\n[red bold]Errors:[/]")
        for err in errors:
            console.print(f"  [red]• {err.get('name')}: {err.get('error')}[/]")


@cli.command()
def doctor() -> None:
    """Check configuration health status.

    Verifies that all Claude Code configurations are properly set up
    and all MCP servers are accessible.
    """
    show_logo(show_tagline=False)
    console.print("[bold]Running health check...[/]\n")

    checks: list[tuple[str, str, str]] = []

    # 1. Check settings.json
    if SETTINGS_FILE.exists():
        checks.append(("settings.json", "[green]OK[/]", str(SETTINGS_FILE)))
    else:
        checks.append(("settings.json", "[red]Missing[/]", "Run: omc setup"))

    # 2. Check CLAUDE.md
    if CLAUDE_MD_FILE.exists():
        checks.append(("CLAUDE.md", "[green]OK[/]", str(CLAUDE_MD_FILE)))
    else:
        checks.append(("CLAUDE.md", "[yellow]Missing[/]", "Optional"))

    # 3. Check Shell integration
    shell = ShellIntegration()
    if shell.is_installed():
        checks.append(("Shell Integration", "[green]OK[/]", f"{shell.shell} ({shell.rc_path})"))
    else:
        checks.append(("Shell Integration", "[yellow]Not configured[/]", "Run: omc init"))

    # 4. Check commands directory
    if COMMANDS_DIR.exists():
        cmd_count = len(list(COMMANDS_DIR.glob("*.md")))
        if cmd_count > 0:
            checks.append(("Slash Commands", "[green]OK[/]", f"{cmd_count} command(s)"))
        else:
            checks.append(("Slash Commands", "[yellow]Empty[/]", "No commands installed"))
    else:
        checks.append(("Slash Commands", "[yellow]Missing[/]", "Directory not found"))

    # 5. Check hooks directory
    if HOOKS_DIR.exists():
        hook_count = len(list(HOOKS_DIR.glob("*")))
        if hook_count > 0:
            checks.append(("Hooks", "[green]OK[/]", f"{hook_count} hook(s)"))
        else:
            checks.append(("Hooks", "[dim]Empty[/]", "No hooks installed"))
    else:
        checks.append(("Hooks", "[dim]Missing[/]", "Directory not found"))

    # 6. Check backups
    backup_mgr = BackupManager()
    backups = backup_mgr.list_backups()
    if backups:
        checks.append(("Backups", "[green]OK[/]", f"{len(backups)} backup(s)"))
    else:
        checks.append(("Backups", "[dim]None[/]", "No backups yet"))

    # Display results table
    table = Table(title="OhMyClaude Health Check", show_header=True, header_style="bold")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    for name, status, detail in checks:
        table.add_row(name, status, detail)

    console.print(table)

    # Summary
    ok_count = sum(1 for _, status, _ in checks if "OK" in status)
    total = len(checks)

    console.print()
    if ok_count == total:
        console.print("[green bold]All checks passed![/]")
    elif ok_count >= total // 2:
        console.print(f"[yellow]{ok_count}/{total} checks passed. Some optional components missing.[/]")
    else:
        console.print(f"[red]{ok_count}/{total} checks passed. Run 'omc setup' to configure.[/]")


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
    output_path = Path(output)

    # Normalize to .tar.gz suffix
    if output_path.suffix == ".tgz":
        pass  # Keep .tgz as-is
    elif not str(output_path).endswith(".tar.gz"):
        output_path = Path(str(output_path).rstrip(".tar").rstrip(".gz") + ".tar.gz")

    console.print(f"[blue]Exporting configuration to: {output_path}[/]\n")

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if there's anything to export
    if not SETTINGS_FILE.exists():
        console.print("[yellow]No configuration found. Run 'omc setup' first.[/]")
        raise SystemExit(1)

    # Create temporary backup
    backup_mgr = BackupManager()
    backup_path = backup_mgr.create_backup(tag="export")

    # Create tar.gz archive
    try:
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(backup_path, arcname=backup_path.name)

        console.print(f"[green]Configuration exported to: {output_path}[/]")
        console.print(f"[dim]Archive contains: settings.json, CLAUDE.md, commands/[/]")
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/]")
        raise SystemExit(1)
    finally:
        # Always clean up temporary backup
        backup_mgr.delete_backup(backup_path.name)


def _safe_extract_tar(tar: tarfile.TarFile, dest: Path) -> None:
    """Safely extract tar archive with path traversal protection."""
    dest = dest.resolve()
    for member in tar.getmembers():
        # Check for path traversal attacks
        member_path = (dest / member.name).resolve()
        if not str(member_path).startswith(str(dest)):
            raise ValueError(f"Path traversal detected: {member.name}")
        # Reject symlinks and other dangerous file types
        if member.issym() or member.islnk():
            raise ValueError(f"Symbolic links not allowed: {member.name}")
        if member.isdev() or member.ischr() or member.isblk():
            raise ValueError(f"Device files not allowed: {member.name}")
    # Extract all members (after validation)
    tar.extractall(dest)


@cli.command("import")
@click.argument("input_file", type=click.Path(exists=True))
def import_config(input_file: str) -> None:
    """Import configuration from a file.

    Restores Claude Code configuration from a previously exported file.
    """
    input_path = Path(input_file)
    console.print(f"[blue]Importing configuration from: {input_path}[/]\n")

    # Verify it's a valid tar.gz file
    if not (str(input_path).endswith(".tar.gz") or str(input_path).endswith(".tgz")):
        console.print("[red]Error: Expected a .tar.gz or .tgz file[/]")
        raise SystemExit(1)

    if not tarfile.is_tarfile(input_path):
        console.print("[red]Error: Not a valid tar archive[/]")
        raise SystemExit(1)

    backup_mgr = BackupManager()
    pre_backup_name: str | None = None

    # Create pre-import backup if existing config
    if SETTINGS_FILE.exists():
        pre_backup = backup_mgr.create_backup(tag="pre-import")
        pre_backup_name = pre_backup.name
        console.print(f"[dim]Backed up existing config to: {pre_backup_name}[/]\n")

    # Extract to temporary directory
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Safely extract archive
            with tarfile.open(input_path, "r:gz") as tar:
                _safe_extract_tar(tar, tmpdir_path)

            # Find the extracted backup directory
            extracted_dirs = [d for d in tmpdir_path.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise ValueError("Archive contains no directories")

            # Find the backup directory (should contain settings.json or metadata.json)
            extracted = None
            for d in extracted_dirs:
                if (d / "settings.json").exists() or (d / "metadata.json").exists():
                    extracted = d
                    break

            if not extracted:
                raise ValueError("Archive does not contain a valid OhMyClaude backup")

            # Copy to backups directory and restore
            dest = backup_mgr.backups_dir / extracted.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(extracted, dest)

            # Restore from the imported backup
            backup_mgr.restore_backup(extracted.name, confirm=False)

        console.print("[green]Configuration imported successfully![/]")
        console.print("[dim]Run 'omc doctor' to verify the configuration.[/]")

    except (tarfile.TarError, ValueError) as e:
        console.print(f"[red]Error: {e}[/]")
        # Rollback to pre-import backup if available
        if pre_backup_name:
            console.print("[yellow]Rolling back to previous configuration...[/]")
            try:
                backup_mgr.restore_backup(pre_backup_name, confirm=False)
                console.print("[dim]Rollback complete.[/]")
            except Exception:
                console.print("[red]Rollback failed. Manual recovery may be needed.[/]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/]")
        # Rollback to pre-import backup if available
        if pre_backup_name:
            console.print("[yellow]Rolling back to previous configuration...[/]")
            try:
                backup_mgr.restore_backup(pre_backup_name, confirm=False)
                console.print("[dim]Rollback complete.[/]")
            except Exception:
                console.print("[red]Rollback failed. Manual recovery may be needed.[/]")
        raise SystemExit(1)


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
