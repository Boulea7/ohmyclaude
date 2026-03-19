"""CLI entry point for OhMyClaude.

This module provides the main command-line interface using Click.
"""

import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from ohmyclaude import __version__
from ohmyclaude.core import (
    CLAUDE_MD_FILE,
    SETTINGS_FILE,
    BackupManager,
    ConfigEngine,
    HarnessBundleBuilder,
    HarnessTarget,
    Installer,
    ShellIntegration,
    resolve_target_paths,
)
from ohmyclaude.core.paths import COMMANDS_DIR as DEFAULT_COMMANDS_DIR
from ohmyclaude.core.paths import HOOKS_DIR as DEFAULT_HOOKS_DIR
from ohmyclaude.core.paths import SKILLS_DIR as DEFAULT_SKILLS_DIR
from ohmyclaude.core.security import ValidationError as SecurityValidationError
from ohmyclaude.core.security import safe_tar_extract
from ohmyclaude.ui.logo import show_logo, show_welcome
from ohmyclaude.ui.prompts import select_preset

console = Console()
_TARGET_CHOICES = [target.value for target in HarnessTarget]
_DOCTOR_CHOICES = ["all", *_TARGET_CHOICES]

# Keep module-level path aliases for older tests and patch-based callers.
COMMANDS_DIR = DEFAULT_COMMANDS_DIR
HOOKS_DIR = DEFAULT_HOOKS_DIR
SKILLS_DIR = DEFAULT_SKILLS_DIR


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
        full      - Full Claude-first template set with Codex-aware hints
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

    # 6. Check for errors and exit accordingly
    errors = result.get("errors", [])
    if errors:
        console.print("\n[red bold]Configuration completed with errors![/]")
        console.print("[yellow]Please review the errors above and fix them manually.[/]")
        raise SystemExit(1)

    # 7. Show next steps (only if successful)
    console.print("\n[green bold]Configuration complete![/]")
    console.print()
    console.print("[bold]Next steps:[/]")
    console.print("  1. Run [cyan]omc doctor[/] to verify configuration")
    console.print("  2. Run [cyan]omc init[/] to configure shell environment")
    console.print("  3. Restart Claude Code to apply changes")


def _show_install_result(result: dict[str, Any]) -> None:
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

    categories: dict[str, dict[str, int]] = {}
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
@click.option(
    "--target",
    "target_name",
    type=click.Choice(_DOCTOR_CHOICES),
    default=HarnessTarget.CLAUDE_HOME.value,
    show_default=True,
    help="Which target surface to inspect.",
)
@click.option(
    "--path",
    "target_path",
    type=click.Path(path_type=Path),
    help=(
        "Explicit target root path. Defaults to ~/.claude for claude-home "
        "and cwd for other targets."
    ),
)
def doctor(target_name: str, target_path: Path | None) -> None:
    """Check configuration health status.

    Verifies that all Claude Code configurations are properly set up
    and all MCP servers are accessible.
    """
    show_logo(show_tagline=False)
    console.print("[bold]Running health check...[/]\n")

    checks: list[tuple[str, str, str]] = []
    targets = (
        list(HarnessTarget)
        if target_name == "all"
        else [HarnessTarget(target_name)]
    )

    for target in targets:
        checks.extend(_build_target_checks(target, target_path))

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
        console.print(
            f"[yellow]{ok_count}/{total} checks passed. Some optional components missing.[/]"
        )
    else:
        console.print(f"[red]{ok_count}/{total} checks passed. Run 'omc setup' to configure.[/]")


def _build_target_checks(
    target: HarnessTarget,
    target_path: Path | None,
) -> list[tuple[str, str, str]]:
    """Build health-check rows for a target."""
    checks: list[tuple[str, str, str]] = []
    root = _resolve_doctor_root(target, target_path)
    paths = resolve_target_paths(target, root)
    label_prefix = target.value

    if target == HarnessTarget.CLAUDE_HOME:
        checks.append(
            _check_file(
                f"{label_prefix}: settings.json",
                paths.settings_file,
                "Run: omc setup",
            )
        )
        checks.append(_check_file(f"{label_prefix}: CLAUDE.md", paths.context_file, "Optional"))
        checks.append(_check_dir(f"{label_prefix}: commands", paths.commands_dir, "*.md"))
        checks.append(_check_dir(f"{label_prefix}: hooks", paths.hooks_dir))
        checks.append(_check_dir(f"{label_prefix}: agents", paths.agents_dir, "*.md"))
        checks.append(_check_dir(f"{label_prefix}: skills", paths.skills_dir))

        shell = ShellIntegration()
        if shell.is_installed():
            checks.append(
                (
                    f"{label_prefix}: shell integration",
                    "[green]OK[/]",
                    f"{shell.shell} ({shell.rc_path})",
                )
            )
        else:
            checks.append(
                (
                    f"{label_prefix}: shell integration",
                    "[yellow]Not configured[/]",
                    "Run: omc init",
                )
            )

        backup_mgr = BackupManager()
        backups = backup_mgr.list_backups()
        checks.append(
            (
                f"{label_prefix}: backups",
                "[green]OK[/]" if backups else "[dim]None[/]",
                f"{len(backups)} backup(s)" if backups else "No backups yet",
            )
        )
        return checks

    if target == HarnessTarget.CLAUDE_PLUGIN:
        checks.append(
            _check_file(
                f"{label_prefix}: plugin.json",
                paths.metadata_file,
                "Render or install a plugin bundle",
            )
        )
        checks.append(_check_dir(f"{label_prefix}: commands", paths.commands_dir, "*.md"))
        checks.append(_check_dir(f"{label_prefix}: hooks", paths.hooks_dir))
        checks.append(_check_dir(f"{label_prefix}: agents", paths.agents_dir, "*.md"))
        checks.append(_check_dir(f"{label_prefix}: skills", paths.skills_dir))
        return checks

    if target == HarnessTarget.CODEX_PROJECT:
        checks.append(
            _check_file(
                f"{label_prefix}: AGENTS.md",
                paths.context_file,
                "Render or install a Codex project bundle",
            )
        )
        checks.append(
            _check_file(
                f"{label_prefix}: config.toml",
                paths.metadata_file,
                "Render or install a Codex project bundle",
            )
        )
        checks.append(_check_dir(f"{label_prefix}: role configs", paths.agents_dir, "*.toml"))
        checks.append(_check_dir(f"{label_prefix}: skills", paths.skills_dir))
        return checks

    checks.append(
        _check_file(
            f"{label_prefix}: extension manifest",
            paths.metadata_file,
            "Render or install a Gemini extension bundle",
        )
    )
    checks.append(
        _check_file(
            f"{label_prefix}: GEMINI.md",
            paths.context_file,
            "Render or install a Gemini extension bundle",
        )
    )
    checks.append(_check_dir(f"{label_prefix}: commands", paths.commands_dir, "*.toml"))
    checks.append(_check_dir(f"{label_prefix}: hooks", paths.hooks_dir))
    checks.append(_check_dir(f"{label_prefix}: agents", paths.agents_dir, "*.md"))
    checks.append(_check_dir(f"{label_prefix}: skills", paths.skills_dir))
    return checks


def _resolve_doctor_root(target: HarnessTarget, target_path: Path | None) -> Path:
    """Resolve the root used for doctor checks."""
    if target_path is not None:
        return target_path

    if target == HarnessTarget.CLAUDE_HOME:
        return CLAUDE_MD_FILE.parent

    return Path.cwd()


def _uses_real_home_target(target: HarnessTarget, path: Path) -> bool:
    """Return True when a render target points into the real harness home."""
    resolved = path.resolve()
    home = Path.home().resolve()

    if target in (HarnessTarget.CLAUDE_HOME, HarnessTarget.CLAUDE_PLUGIN):
        claude_home = home / ".claude"
        return resolved == claude_home or claude_home in resolved.parents

    if target == HarnessTarget.CODEX_PROJECT:
        codex_home = home / ".codex"
        return resolved == codex_home or codex_home in resolved.parents

    gemini_home = home / ".gemini"
    return resolved == gemini_home or gemini_home in resolved.parents


def _check_file(
    label: str,
    path: Path | None,
    missing_hint: str,
) -> tuple[str, str, str]:
    """Return a formatted file check row."""
    if path is not None and path.exists():
        return (label, "[green]OK[/]", str(path))
    return (label, "[yellow]Missing[/]", missing_hint)


def _check_dir(
    label: str,
    path: Path | None,
    pattern: str = "*",
) -> tuple[str, str, str]:
    """Return a formatted directory check row."""
    if path is None or not path.exists():
        return (label, "[yellow]Missing[/]", "Directory not found")

    count = len(list(path.glob(pattern)))
    if count > 0:
        return (label, "[green]OK[/]", f"{count} item(s)")

    return (label, "[dim]Empty[/]", "No files found")


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
        console.print("[bold]Shell Integration Status[/]\n")
        console.print(f"  Shell type:    [cyan]{info['shell']}[/]")
        console.print(f"  RC file:       [dim]{info['rc_path']}[/]")
        if info["is_installed"]:
            console.print("  Status:        [green]Configured[/]")
        else:
            console.print("  Status:        [yellow]Not configured[/]")
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
@click.option(
    "--sync-codex-auth",
    is_flag=True,
    help="Explicitly sync Codex auth.json when the provider exposes an OpenAI-compatible endpoint.",
)
@click.option(
    "--skip-codex",
    is_flag=True,
    help="Deprecated compatibility flag. Codex sync is disabled by default.",
)
@click.option("--list", "-l", "list_all", is_flag=True, help="List available providers.")
def switch(
    provider: str | None,
    token: str | None,
    base_url: str | None,
    sync_codex_auth: bool,
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
        ohmyclaude switch custom -u https://api.example.com -t $TOKEN
    """
    from ohmyclaude.core.provider import ProviderSwitcher
    from ohmyclaude.ui.prompts import select_provider
    from ohmyclaude.ui.tables import create_provider_table

    switcher = ProviderSwitcher()

    # List mode: show all providers
    if list_all:
        providers = [p.model_dump() for p in switcher.get_all_providers().values()]
        current = switcher.get_current()
        table = create_provider_table(providers, current)
        console.print(table)
        console.print("\n[dim]Use: ohmyclaude switch <provider>[/]")
        return

    # Interactive selection if no provider specified
    if not provider:
        provider = select_provider()
        console.print()

    # Handle "custom" provider selection - guide user to use provider add
    if provider == "custom":
        if not base_url:
            console.print("[yellow]Custom provider requires additional configuration.[/]")
            console.print()
            console.print("[bold]To add a custom provider, use:[/]")
            console.print(
                "  [cyan]omc provider add <name> --base-url <url> --token-env <env>[/]"
            )
            console.print()
            console.print("[bold]Example:[/]")
            console.print(
                "  [dim]omc provider add myvendor \\\n"
                "      --base-url https://api.example.com --token-env MY_TOKEN[/]"
            )
            console.print("  [dim]omc switch myvendor[/]")
            return
        # If base_url provided via CLI, treat as direct custom switch
        provider = "custom"

    # Execute switch
    try:
        if sync_codex_auth and skip_codex:
            console.print("[red]Use either --sync-codex-auth or --skip-codex, not both.[/]")
            raise SystemExit(1)

        result = switcher.switch(
            provider_name=provider,
            token=token,
            base_url=base_url,
            skip_codex=not sync_codex_auth,
        )

        if not result.success:
            console.print(f"[red]Switch failed: {result.message}[/]")
            raise SystemExit(1)

        console.print(f"\n[green]✓ Successfully switched to: {result.provider_name}[/]")

        if result.settings_backup:
            console.print(f"[dim]  Settings backed up: {result.settings_backup}[/]")

        if result.codex_updated:
            console.print("[dim]  Codex auth.json updated[/]")
            if result.codex_backup:
                console.print(f"[dim]  Codex backed up: {result.codex_backup}[/]")
        elif not sync_codex_auth:
            console.print("[dim]  Codex auth.json not touched (use --sync-codex-auth to opt in)[/]")

        console.print(
            "\n[yellow]Please restart Claude Code or open a new terminal "
            "to apply changes.[/]"
        )

    except (ValueError, FileNotFoundError, OSError) as e:
        # Expected errors - show user-friendly message
        console.print(f"[red]Error: {e}[/]")
        raise SystemExit(1)
    except Exception:
        # Unexpected errors - show full traceback for debugging
        console.print("[red]Unexpected error occurred:[/]")
        console.print_exception()
        raise SystemExit(1)


@cli.group()
def provider() -> None:
    """Manage API providers.

    Add, remove, and list custom API providers.
    """
    pass


@provider.command("list")
def provider_list() -> None:
    """List all available providers."""
    from ohmyclaude.core.provider import ProviderSwitcher
    from ohmyclaude.ui.tables import create_provider_table

    switcher = ProviderSwitcher()
    providers = [p.model_dump() for p in switcher.get_all_providers().values()]
    current = switcher.get_current()

    table = create_provider_table(providers, current)
    console.print(table)
    console.print("\n[dim]Use: ohmyclaude provider add <name> to add custom provider[/]")


@provider.command("show")
def provider_show() -> None:
    """Show current provider configuration."""
    from ohmyclaude.core.provider import ProviderSwitcher

    switcher = ProviderSwitcher()
    current = switcher.get_current()
    provider_config = switcher.get_provider(current) if current else None

    console.print(f"[bold]Current Provider:[/] {current or 'unknown'}\n")

    if provider_config:
        console.print(f"  [cyan]Display Name:[/]  {provider_config.display_name}")
        console.print(f"  [cyan]Description:[/]   {provider_config.description}")
        if provider_config.anthropic_base_url:
            console.print(f"  [cyan]Base URL:[/]       {provider_config.anthropic_base_url}")
        else:
            console.print("  [cyan]Base URL:[/]       (official default)")
        console.print(f"  [cyan]Token Env:[/]      {provider_config.anthropic_token_env}")
        if provider_config.openai_base_url:
            console.print(f"  [cyan]OpenAI URL:[/]     {provider_config.openai_base_url}")
        console.print(f"  [cyan]API Type:[/]       {provider_config.api_type}")
        console.print(f"  [cyan]Built-in:[/]       {'Yes' if provider_config.is_builtin else 'No'}")
    else:
        console.print("[dim]  Provider details not available[/]")


@provider.command("add")
@click.argument("name")
@click.option("--base-url", "-u", required=True, help="API base URL.")
@click.option("--token-env", required=True, help="Environment variable name for token.")
@click.option("--display-name", "-d", help="Display name (defaults to name).")
@click.option("--openai-url", help="OpenAI-compatible URL for Codex.")
@click.option("--openai-token-env", help="Env var for OpenAI token.")
@click.option("--description", help="Provider description.")
def provider_add(
    name: str,
    base_url: str,
    token_env: str,
    display_name: str | None,
    openai_url: str | None,
    openai_token_env: str | None,
    description: str | None,
) -> None:
    """Add a custom API provider.

    \b
    Examples:
        ohmyclaude provider add myvendor -u https://api.example.com --token-env MY_TOKEN
        ohmyclaude provider add myvendor -u https://api.example.com --token-env MY_TOKEN \\
            --openai-url https://api.example.com/openai/v1
    """
    from ohmyclaude.core.provider import ProviderSwitcher

    switcher = ProviderSwitcher()

    # Check if provider already exists
    if switcher.get_provider(name):
        console.print(f"[red]Provider '{name}' already exists.[/]")
        raise SystemExit(1)

    success = switcher.add_custom_provider(
        name=name,
        display_name=display_name or name,
        base_url=base_url,
        token_env=token_env,
        openai_base_url=openai_url,
        openai_token_env=openai_token_env,
        description=description or "",
    )

    if success:
        console.print(f"[green]✓ Added custom provider: {name}[/]")
        console.print(f"  Base URL:  {base_url}")
        console.print(f"  Token env: {token_env}")
        if openai_url:
            console.print(f"  OpenAI URL: {openai_url}")
        console.print(f"\n[dim]Use: ohmyclaude switch {name}[/]")
    else:
        console.print("[red]Failed to add provider.[/]")
        raise SystemExit(1)


@provider.command("remove")
@click.argument("name")
def provider_remove(name: str) -> None:
    """Remove a custom API provider.

    \b
    Examples:
        ohmyclaude provider remove myvendor
    """
    from ohmyclaude.core.provider import ProviderSwitcher

    switcher = ProviderSwitcher()
    provider_config = switcher.get_provider(name)

    if not provider_config:
        console.print(f"[yellow]Provider '{name}' not found.[/]")
        raise SystemExit(1)

    if provider_config.is_builtin:
        console.print(f"[red]Cannot remove built-in provider '{name}'.[/]")
        raise SystemExit(1)

    if switcher.remove_custom_provider(name):
        console.print(f"[green]✓ Removed custom provider: {name}[/]")
    else:
        console.print(f"[red]Failed to remove provider '{name}'.[/]")
        raise SystemExit(1)


@cli.command("render")
@click.option(
    "--target",
    "target_name",
    type=click.Choice(_TARGET_CHOICES),
    required=True,
    help="Target bundle type to render.",
)
@click.option(
    "--preset",
    "-p",
    type=click.Choice(["starter", "standard", "full"]),
    default="standard",
    show_default=True,
    help="Preset used to render the bundle.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Directory where rendered files will be written.",
)
def render_bundle(target_name: str, preset: str, output: Path) -> None:
    """Render a target bundle into an explicit output directory."""
    target = HarnessTarget(target_name)
    if _uses_real_home_target(target, output):
        console.print(
            "[red]Refusing to render into a real harness home directory.[/]"
        )
        console.print(
            "[dim]Use a temporary output path, or use `omc install --confirm` "
            "for an explicit live destination.[/]"
        )
        raise SystemExit(1)

    builder = HarnessBundleBuilder()
    bundle = builder.render_bundle(target, preset)
    result = builder.install_bundle(bundle, output)

    console.print(f"[green]Rendered {target.value} bundle to: {result.destination}[/]")
    console.print(f"[dim]Files written: {result.written_files}[/]")


@cli.command("install")
@click.option(
    "--target",
    "target_name",
    type=click.Choice(_TARGET_CHOICES),
    required=True,
    help="Target bundle type to install.",
)
@click.option(
    "--preset",
    "-p",
    type=click.Choice(["starter", "standard", "full"]),
    default="standard",
    show_default=True,
    help="Preset used to build the installation bundle.",
)
@click.option(
    "--dest",
    type=click.Path(path_type=Path),
    required=True,
    help="Explicit destination root. OhMyClaude never infers real user home targets here.",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Required safety flag acknowledging the explicit destination write.",
)
@click.option(
    "--backup",
    is_flag=True,
    help="Back up existing managed files before writing.",
)
@click.option(
    "--restore-on-failure",
    is_flag=True,
    help="Attempt to restore backed-up files if installation fails.",
)
def install_bundle(
    target_name: str,
    preset: str,
    dest: Path,
    confirm: bool,
    backup: bool,
    restore_on_failure: bool,
) -> None:
    """Install a rendered bundle into an explicit destination."""
    if not confirm:
        console.print("[red]Refusing to install without --confirm.[/]")
        console.print(
            "[dim]Use `omc render` first if you want to inspect the output "
            "before installing.[/]"
        )
        raise SystemExit(1)

    target = HarnessTarget(target_name)
    builder = HarnessBundleBuilder()
    bundle = builder.render_bundle(target, preset)
    try:
        result = builder.install_bundle(
            bundle,
            dest,
            backup=backup,
            restore_on_failure=restore_on_failure,
        )
    except Exception as e:
        console.print(f"[red]Install failed: {e}[/]")
        raise SystemExit(1)

    console.print(f"[green]Installed {target.value} bundle to: {result.destination}[/]")
    console.print(f"[dim]Files written: {result.written_files}[/]")
    if result.backup_path is not None:
        console.print(f"[dim]Backup created: {result.backup_path}[/]")


@cli.command("export")
@click.argument("output", type=click.Path())
def export_config(output: str) -> None:
    """Export current configuration to a file.

    Creates a backup of your Claude Code configuration that can be
    imported on another machine or shared with team members.
    """
    output_path = Path(output)

    # Normalize to .tar.gz suffix (avoid character-level rstrip)
    if output_path.suffix == ".tgz":
        pass  # Keep .tgz as-is
    elif output_path.suffixes == [".tar", ".gz"]:
        pass  # Already has .tar.gz
    else:
        # Remove any partial suffix and add .tar.gz
        stem = output_path.stem
        if stem.endswith(".tar"):
            stem = stem[:-4]
        output_path = output_path.parent / f"{stem}.tar.gz"

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
        console.print("[dim]Archive contains: settings.json, CLAUDE.md, commands/[/]")
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/]")
        raise SystemExit(1)
    finally:
        # Always clean up temporary backup
        backup_mgr.delete_backup(backup_path.name)


def _safe_extract_tar(tar: tarfile.TarFile, dest: Path) -> None:
    """Safely extract tar archive with comprehensive security checks.

    This function provides protection against:
    - Path traversal attacks (../)
    - Symbolic link attacks
    - Device file attacks
    - TOCTOU attacks (extract individually)

    Args:
        tar: Open tarfile object
        dest: Destination directory

    Raises:
        ValueError: If security checks fail
    """
    dest = dest.resolve()

    # Phase 1: Validate ALL members before extraction
    for member in tar.getmembers():
        # Normalize and resolve path
        member_path = (dest / member.name).resolve()

        # Path traversal check (must be under dest)
        try:
            member_path.relative_to(dest)
        except ValueError:
            raise ValueError(f"Path traversal detected: {member.name}")

        # Absolute path check
        if member.name.startswith("/"):
            raise ValueError(f"Absolute paths not allowed: {member.name}")

        # Reject symlinks and other dangerous file types
        if member.issym() or member.islnk():
            raise ValueError(f"Symbolic/hard links not allowed: {member.name}")

        # Device file check
        if member.isdev() or member.ischr() or member.isblk() or member.isfifo():
            raise ValueError(f"Special files not allowed: {member.name}")

        # Size check (100MB limit per file)
        if member.size > 100 * 1024 * 1024:
            raise ValueError(f"File too large: {member.name} ({member.size} bytes)")

    # Phase 2: Extract individually to avoid TOCTOU
    for member in tar.getmembers():
        if member.isfile() or member.isdir():
            # Use data filter if available (Python 3.12+)
            if hasattr(tarfile, "data_filter"):
                tar.extract(member, dest, filter="data")
            else:
                tar.extract(member, dest)


def _rollback_import(backup_name: str | None, mgr: BackupManager) -> None:
    """Attempt to rollback to a previous backup after failed import.

    Args:
        backup_name: Name of the backup to restore, or None to skip
        mgr: BackupManager instance
    """
    if not backup_name:
        return

    console.print("[yellow]Rolling back to previous configuration...[/]")
    try:
        mgr.restore_backup(backup_name, confirm=False)
        console.print("[dim]Rollback complete.[/]")
    except (OSError, ValueError) as e:
        console.print(f"[red]Rollback failed: {e}[/]")
        console.print("[red]Manual recovery may be needed from backup:[/]")
        console.print(f"[dim]  {mgr.backups_dir / backup_name}[/]")


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

            # Safely extract archive using security.py's safe_tar_extract
            try:
                safe_tar_extract(input_path, tmpdir_path, allow_symlinks=False)
            except SecurityValidationError as e:
                console.print(f"[red]Security check failed: {e}[/]")
                raise SystemExit(1) from e

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

    except (tarfile.TarError, ValueError, OSError) as e:
        # Expected errors - show user-friendly message
        console.print(f"[red]Error: {e}[/]")
        _rollback_import(pre_backup_name, backup_mgr)
        raise SystemExit(1)
    except Exception:
        # Unexpected errors - show full traceback for debugging
        console.print("[red]Unexpected error during import:[/]")
        console.print_exception()
        _rollback_import(pre_backup_name, backup_mgr)
        raise SystemExit(1)


@cli.command()
@click.option("--check", is_flag=True, help="Only check for updates, don't apply.")
def update(check: bool) -> None:
    """Check for OhMyClaude updates.

    Checks PyPI for new versions and shows update instructions.

    \b
    Examples:
        omc update              Check and show update instructions
        omc update --check      Same as above (explicit check mode)
    """
    from ohmyclaude.core.version import check_version, get_update_command

    console.print("[blue]Checking for updates...[/]\n")

    result = check_version()

    if result.error:
        console.print(f"[yellow]Warning: {result.error}[/]")
        return

    console.print(f"  Current version: [cyan]{result.current}[/]")
    console.print(f"  Latest version:  [cyan]{result.latest}[/]")
    console.print()

    if result.is_outdated:
        console.print("[yellow]A new version is available![/]")
        console.print()
        console.print("[bold]To update, run:[/]")
        console.print(f"  [cyan]{get_update_command()}[/]")
        if result.release_url:
            console.print()
            console.print(f"[dim]Release notes: {result.release_url}[/]")
    else:
        console.print("[green]You are using the latest version.[/]")


if __name__ == "__main__":
    cli()
