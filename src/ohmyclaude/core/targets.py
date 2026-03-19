"""Multi-target bundle rendering and installation for OhMyClaude.

This module provides explicit, destination-based rendering for Claude, Codex,
and Gemini-compatible assets. All writes are scoped to caller-provided paths.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ohmyclaude.core.atomic import atomic_write
from ohmyclaude.core.config import ConfigEngine
from ohmyclaude.core.paths import get_project_templates_dir
from ohmyclaude.models.presets import PresetConfig

_TIMESTAMP_FMT = "%Y%m%d-%H%M%S"
_HOOK_PRESET_SCRIPTS: dict[str, tuple[str, ...]] = {
    "basic": (),
    "standard": (),
    "full": (
        "skill-activation-prompt.ts",
        "skill-activation-prompt.sh",
        "post-tool-use-tracker.sh",
        "tsc-check.sh",
        "stop-build-check-enhanced.sh",
        "trigger-build-resolver.sh",
        "error-handling-reminder.ts",
        "error-handling-reminder.sh",
    ),
}
_PORTABLE_SKILLS: tuple[str, ...] = (
    "api-design",
    "deep-research",
    "git-workflow",
    "performance",
    "search-first",
    "security-review",
    "verification-loop",
)
_PORTABLE_GEMINI_AGENTS: tuple[str, ...] = (
    "code-reviewer",
    "debugger",
    "plan-reviewer",
)


class HarnessTarget(str, Enum):
    """Supported output targets."""

    CLAUDE_HOME = "claude-home"
    CLAUDE_PLUGIN = "claude-plugin"
    CODEX_PROJECT = "codex-project"
    GEMINI_EXTENSION = "gemini-extension"


@dataclass(frozen=True)
class RenderedFile:
    """A single rendered file entry."""

    relative_path: str
    content: str
    executable: bool = False

    @property
    def path(self) -> Path:
        """Return the path relative to the target root."""
        return Path(self.relative_path)


@dataclass(frozen=True)
class RenderedBundle:
    """Rendered output for a specific target."""

    target: HarnessTarget
    preset_name: str
    files: tuple[RenderedFile, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class TargetPaths:
    """Resolved paths for a target installation root."""

    root: Path
    settings_file: Path | None = None
    context_file: Path | None = None
    commands_dir: Path | None = None
    hooks_dir: Path | None = None
    agents_dir: Path | None = None
    skills_dir: Path | None = None
    metadata_file: Path | None = None


@dataclass(frozen=True)
class InstallTransactionResult:
    """Result for an explicit destination-based installation."""

    target: HarnessTarget
    destination: Path
    written_files: int
    backup_path: Path | None = None
    restored: bool = False


def resolve_target_paths(target: HarnessTarget, destination: Path) -> TargetPaths:
    """Resolve conventional paths for a target rooted at destination."""
    root = destination.resolve()

    if target == HarnessTarget.CLAUDE_HOME:
        return TargetPaths(
            root=root,
            settings_file=root / "settings.json",
            context_file=root / "CLAUDE.md",
            commands_dir=root / "commands",
            hooks_dir=root / "hooks",
            agents_dir=root / "agents",
            skills_dir=root / "skills",
        )

    if target == HarnessTarget.CLAUDE_PLUGIN:
        return TargetPaths(
            root=root,
            commands_dir=root / "commands",
            hooks_dir=root / "hooks",
            agents_dir=root / "agents",
            skills_dir=root / "skills",
            metadata_file=root / ".claude-plugin" / "plugin.json",
        )

    if target == HarnessTarget.CODEX_PROJECT:
        return TargetPaths(
            root=root,
            context_file=root / "AGENTS.md",
            agents_dir=root / ".codex" / "agents",
            skills_dir=root / ".agents" / "skills",
            metadata_file=root / ".codex" / "config.toml",
        )

    return TargetPaths(
        root=root,
        context_file=root / "GEMINI.md",
        commands_dir=root / "commands",
        hooks_dir=root / "hooks",
        agents_dir=root / "agents",
        skills_dir=root / "skills",
        metadata_file=root / "gemini-extension.json",
    )


class HarnessBundleBuilder:
    """Render reusable bundles for multiple agent harnesses."""

    def __init__(self, engine: ConfigEngine | None = None) -> None:
        """Initialize the bundle builder."""
        self.engine = engine or ConfigEngine()
        self.templates_dir = get_project_templates_dir()

    def render_bundle(self, target: HarnessTarget, preset_name: str) -> RenderedBundle:
        """Render a bundle for the selected target and preset."""
        preset = self.engine.load_preset(preset_name)

        if target == HarnessTarget.CLAUDE_HOME:
            files = self._render_claude_home(preset)
        elif target == HarnessTarget.CLAUDE_PLUGIN:
            files = self._render_claude_plugin(preset)
        elif target == HarnessTarget.CODEX_PROJECT:
            files = self._render_codex_project(preset)
        else:
            files = self._render_gemini_extension(preset)

        return RenderedBundle(
            target=target,
            preset_name=preset.name,
            files=tuple(files),
        )

    def install_bundle(
        self,
        bundle: RenderedBundle,
        destination: Path,
        *,
        backup: bool = False,
        restore_on_failure: bool = False,
    ) -> InstallTransactionResult:
        """Write a bundle into an explicit destination.

        Existing files are backed up individually when backup=True.
        """
        root = destination.resolve()
        root.mkdir(parents=True, exist_ok=True)

        if restore_on_failure:
            backup = True

        backup_root: Path | None = None
        existing_files: set[Path] = set()
        written_files: list[Path] = []
        restored = False

        stamp = datetime.now().strftime(_TIMESTAMP_FMT)
        manifest_path = self._manifest_path(root, bundle.target)
        previous_paths = self._load_manifest(manifest_path)
        current_paths = {str(rendered.path.as_posix()) for rendered in bundle.files}
        stale_paths = previous_paths - current_paths

        try:
            for relative_name in sorted(stale_paths):
                stale_path = root / relative_name
                if not stale_path.exists() or not stale_path.is_file():
                    continue
                existing_files.add(stale_path)
                if backup and backup_root is None:
                    backup_root = (
                        root.parent
                        / f".ohmyclaude-backup-{bundle.target.value}-{stamp}"
                    )
                if backup_root is not None:
                    backup_path = backup_root / relative_name
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(stale_path, backup_path)
                stale_path.unlink()
                self._prune_empty_parents(stale_path.parent, root)

            for rendered in bundle.files:
                target_path = root / rendered.path
                if target_path.exists():
                    existing_files.add(target_path)
                    if backup and backup_root is None:
                        backup_root = (
                            root.parent
                            / f".ohmyclaude-backup-{bundle.target.value}-{stamp}"
                        )
                    if backup_root is not None:
                        backup_path = backup_root / rendered.path
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target_path, backup_path)

            for rendered in bundle.files:
                target_path = root / rendered.path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with atomic_write(target_path) as file_obj:
                    file_obj.write(rendered.content)
                if rendered.executable:
                    target_path.chmod(0o755)
                written_files.append(target_path)

            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with atomic_write(manifest_path) as file_obj:
                json.dump(
                    {"files": sorted(current_paths)},
                    file_obj,
                    indent=2,
                    ensure_ascii=False,
                )
            written_files.append(manifest_path)

        except Exception:
            if restore_on_failure:
                self._restore_from_backup(
                    root=root,
                    backup_root=backup_root,
                    existing_files=existing_files,
                    written_files=written_files,
                )
                restored = True
            raise

        return InstallTransactionResult(
            target=bundle.target,
            destination=root,
            written_files=len(written_files),
            backup_path=backup_root,
            restored=restored,
        )

    def _restore_from_backup(
        self,
        *,
        root: Path,
        backup_root: Path | None,
        existing_files: set[Path],
        written_files: list[Path],
    ) -> None:
        """Best-effort rollback for a failed installation."""
        for path in written_files:
            if path not in existing_files and path.exists():
                path.unlink()

        if backup_root is None or not backup_root.exists():
            return

        for backup_file in backup_root.rglob("*"):
            if not backup_file.is_file():
                continue
            relative = backup_file.relative_to(backup_root)
            restore_path = root / relative
            restore_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, restore_path)

    def _manifest_path(self, root: Path, target: HarnessTarget) -> Path:
        """Return the manifest path used to track managed files for a target."""
        if target == HarnessTarget.CLAUDE_PLUGIN:
            return root / ".claude-plugin" / "ohmyclaude-manifest.json"
        if target == HarnessTarget.CODEX_PROJECT:
            return root / ".codex" / "ohmyclaude-manifest.json"
        return root / ".ohmyclaude-manifest.json"

    def _load_manifest(self, manifest_path: Path) -> set[str]:
        """Load previously managed relative file paths."""
        if not manifest_path.exists():
            return set()
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return set()

        files = data.get("files", [])
        if not isinstance(files, list):
            return set()

        return {
            value
            for value in files
            if isinstance(value, str) and value and not value.startswith("../")
        }

    def _prune_empty_parents(self, directory: Path, root: Path) -> None:
        """Remove empty parent directories after deleting stale files."""
        current = directory
        while current != root and current.exists():
            try:
                current.rmdir()
            except OSError:
                return
            current = current.parent

    def _render_claude_home(self, preset: PresetConfig) -> list[RenderedFile]:
        files = [
            RenderedFile(
                "settings.json",
                self._render_settings_json(preset),
            ),
            RenderedFile(
                "CLAUDE.md",
                self._render_claude_md(preset),
            ),
        ]
        files.extend(self._render_commands(preset, "commands"))
        files.extend(self._render_markdown_agents(preset.agents, "agents"))
        files.extend(self._render_hook_scripts(preset, "hooks"))
        files.extend(self._render_skills(preset.skills, "skills"))
        return files

    def _render_claude_plugin(self, preset: PresetConfig) -> list[RenderedFile]:
        plugin_manifest = self.engine.render_template(
            "claude_plugin/plugin.json.j2",
            {
                "preset": preset,
            },
        )
        files = [RenderedFile(".claude-plugin/plugin.json", plugin_manifest)]
        files.extend(self._render_commands(preset, "commands"))
        files.extend(self._render_markdown_agents(preset.agents, "agents"))
        files.extend(self._render_hook_scripts(preset, "hooks"))
        files.extend(self._render_skills(preset.skills, "skills"))
        hooks_json = json.dumps(
            {
                "$schema": "https://json.schemastore.org/claude-code-settings.json",
                "hooks": self._render_bundle_hooks_config(
                    HarnessTarget.CLAUDE_PLUGIN,
                    preset,
                ),
            },
            indent=2,
            ensure_ascii=False,
        )
        files.append(RenderedFile("hooks/hooks.json", hooks_json + "\n"))
        return files

    def _render_codex_project(self, preset: PresetConfig) -> list[RenderedFile]:
        portable_skills = self._portable_skills(preset)
        files = [
            RenderedFile(
                "AGENTS.md",
                self.engine.render_template(
                    "codex/AGENTS.md.j2",
                    {
                        "preset": preset,
                        "portable_skills": portable_skills,
                    },
                ),
            ),
            RenderedFile(
                ".codex/config.toml",
                self.engine.render_template(
                    "codex/config.toml.j2",
                    {
                        "preset": preset,
                    },
                ),
            ),
            RenderedFile(
                ".codex/agents/explorer.toml",
                self.engine.render_template("codex/agents/explorer.toml.j2", {}),
            ),
            RenderedFile(
                ".codex/agents/reviewer.toml",
                self.engine.render_template("codex/agents/reviewer.toml.j2", {}),
            ),
            RenderedFile(
                ".codex/agents/docs_researcher.toml",
                self.engine.render_template("codex/agents/docs_researcher.toml.j2", {}),
            ),
        ]
        files.extend(self._render_skills(portable_skills, ".agents/skills"))
        return files

    def _render_gemini_extension(self, preset: PresetConfig) -> list[RenderedFile]:
        portable_skills = self._portable_skills(preset)
        manifest = self.engine.render_template(
            "gemini/gemini-extension.json.j2",
            {
                "preset": preset,
            },
        )
        files = [
            RenderedFile("gemini-extension.json", manifest),
            RenderedFile(
                "GEMINI.md",
                self.engine.render_template(
                    "gemini/GEMINI.md.j2",
                    {
                        "preset": preset,
                        "portable_skills": portable_skills,
                    },
                ),
            ),
        ]
        files.extend(self._render_gemini_commands(preset))
        files.extend(self._render_hook_scripts(preset, "hooks"))
        files.extend(self._render_skills(portable_skills, "skills"))
        files.extend(self._render_markdown_agents(_PORTABLE_GEMINI_AGENTS, "agents"))
        hooks_json = json.dumps(
            {
                "hooks": self._render_bundle_hooks_config(
                    HarnessTarget.GEMINI_EXTENSION,
                    preset,
                )
            },
            indent=2,
            ensure_ascii=False,
        )
        files.append(RenderedFile("hooks/hooks.json", hooks_json + "\n"))
        return files

    def _settings_dict(self, preset: PresetConfig) -> dict[str, object]:
        """Return settings as a JSON-serializable dict."""
        return self.engine.generate_settings(preset).model_dump(exclude_none=True)

    def _render_settings_json(self, preset: PresetConfig) -> str:
        """Render Claude settings.json."""
        return json.dumps(
            self._settings_dict(preset),
            indent=2,
            ensure_ascii=False,
        ) + "\n"

    def _render_claude_md(self, preset: PresetConfig) -> str:
        """Render CLAUDE.md using the configured template."""
        template_key = self._safe_segment(preset.claude_md_template, "template")
        template_name = f"claude_md/{template_key}.md.j2"
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            template_name = "claude_md/general.md.j2"
        return self.engine.render_template(
            template_name,
            {
                "config": preset,
                "user_name": "User",
            },
        )

    def _render_commands(self, preset: PresetConfig, prefix: str) -> list[RenderedFile]:
        """Render markdown commands for Claude-oriented targets."""
        commands_dir = self.templates_dir / "commands"
        rendered: list[RenderedFile] = []

        for command_name in preset.commands:
            safe_name = self._safe_segment(command_name, "command")
            template_file = commands_dir / f"{safe_name}.md.j2"
            static_file = commands_dir / f"{safe_name}.md"

            if template_file.exists():
                content = self.engine.render_template(
                    f"commands/{safe_name}.md.j2",
                    {"config": preset},
                )
            elif static_file.exists():
                content = static_file.read_text(encoding="utf-8")
            else:
                continue

            rendered.append(RenderedFile(f"{prefix}/{safe_name}.md", content))

        return rendered

    def _render_gemini_commands(self, preset: PresetConfig) -> list[RenderedFile]:
        """Render Gemini custom commands from existing command templates."""
        rendered: list[RenderedFile] = []
        for command_file in self._render_commands(preset, "commands"):
            command_name = command_file.path.stem
            prompt = command_file.content.replace('"""', '\\"""')
            toml_content = (
                f'description = "OhMyClaude generated {command_name} workflow"\n'
                f'prompt = """\n{prompt}\n"""\n'
            )
            rendered.append(
                RenderedFile(
                    f"commands/{command_name}.toml",
                    toml_content,
                )
            )
        return rendered

    def _render_markdown_agents(
        self,
        agent_names: tuple[str, ...] | list[str],
        prefix: str,
    ) -> list[RenderedFile]:
        """Render markdown agents from bundled templates."""
        source_dir = self.templates_dir / "agents-showcase"
        rendered: list[RenderedFile] = []
        for agent_name in agent_names:
            safe_name = self._safe_segment(agent_name, "agent")
            source_file = source_dir / f"{safe_name}.md"
            if not source_file.exists():
                continue
            rendered.append(
                RenderedFile(
                    f"{prefix}/{safe_name}.md",
                    source_file.read_text(encoding="utf-8"),
                )
            )
        return rendered

    def _render_hook_scripts(self, preset: PresetConfig, prefix: str) -> list[RenderedFile]:
        """Render hook scripts for targets that support them."""
        hooks_dir = self.templates_dir / "hooks"
        rendered: list[RenderedFile] = []
        script_names = _HOOK_PRESET_SCRIPTS.get(preset.hooks_preset, ())
        for script_name in script_names:
            source_file = hooks_dir / script_name
            if not source_file.exists():
                continue
            rendered.append(
                RenderedFile(
                    f"{prefix}/{script_name}",
                    source_file.read_text(encoding="utf-8"),
                    executable=script_name.endswith(".sh"),
                )
            )
        return rendered

    def _render_bundle_hooks_config(
        self,
        target: HarnessTarget,
        preset: PresetConfig,
    ) -> dict[str, list[dict[str, Any]]]:
        """Render self-contained hook configuration for portable bundles."""
        script_names = set(_HOOK_PRESET_SCRIPTS.get(preset.hooks_preset, ()))
        if target == HarnessTarget.CLAUDE_PLUGIN:
            root_expr = "${CLAUDE_PLUGIN_ROOT}"
        else:
            root_expr = "${extensionPath}"

        hooks: dict[str, list[dict[str, Any]]] = {}

        if "skill-activation-prompt.sh" in script_names:
            hooks["UserPromptSubmit"] = [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f'bash "{root_expr}/hooks/skill-activation-prompt.sh"',
                            "timeout": 5000,
                        }
                    ]
                }
            ]

        post_tool_hooks: list[dict[str, Any]] = []
        if "post-tool-use-tracker.sh" in script_names:
            post_tool_hooks.append(
                {
                    "type": "command",
                    "command": f'bash "{root_expr}/hooks/post-tool-use-tracker.sh"',
                    "timeout": 3000,
                }
            )
        if "tsc-check.sh" in script_names:
            post_tool_hooks.append(
                {
                    "type": "command",
                    "command": f'bash "{root_expr}/hooks/tsc-check.sh"',
                    "timeout": 30000,
                }
            )
        if post_tool_hooks:
            hooks["PostToolUse"] = [
                {
                    "matcher": "Edit|Write|MultiEdit",
                    "hooks": post_tool_hooks,
                }
            ]

        if "stop-build-check-enhanced.sh" in script_names:
            hooks["Stop"] = [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                f'bash "{root_expr}/hooks/stop-build-check-enhanced.sh"'
                            ),
                            "timeout": 60000,
                        }
                    ]
                }
            ]

        return hooks

    def _render_skills(
        self,
        skill_names: tuple[str, ...] | list[str],
        prefix: str,
    ) -> list[RenderedFile]:
        """Render full skill directories."""
        source_root = self.templates_dir / "skills"
        rendered: list[RenderedFile] = []
        seen: set[str] = set()

        for skill_name in skill_names:
            if skill_name in seen:
                continue
            seen.add(skill_name)
            safe_name = self._safe_segment(skill_name, "skill")
            source_dir = source_root / safe_name
            if not source_dir.exists() or not source_dir.is_dir():
                continue

            for source_file in sorted(source_dir.rglob("*")):
                if not source_file.is_file():
                    continue
                relative = source_file.relative_to(source_dir)
                rendered.append(
                    RenderedFile(
                        str(Path(prefix) / safe_name / relative),
                        source_file.read_text(encoding="utf-8"),
                        executable=source_file.suffix == ".sh",
                    )
                )

        return rendered

    def _portable_skills(self, preset: PresetConfig) -> tuple[str, ...]:
        """Return a portable baseline skill set for non-Claude targets."""
        if preset.skills:
            merged = list(preset.skills)
            for skill_name in _PORTABLE_SKILLS:
                if skill_name not in merged:
                    merged.append(skill_name)
            return tuple(merged)
        return _PORTABLE_SKILLS

    @staticmethod
    def _safe_segment(value: str, label: str) -> str:
        """Validate a filesystem-safe segment."""
        if not value:
            raise ValueError(f"Invalid {label} name: empty value")

        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if any(char not in allowed for char in value):
            raise ValueError(f"Invalid {label} name: {value!r}")

        if value.startswith(".") or "/" in value or "\\" in value or ".." in value:
            raise ValueError(f"Invalid {label} name: {value!r}")

        return value
