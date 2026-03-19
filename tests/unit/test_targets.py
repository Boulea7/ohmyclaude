"""Unit tests for explicit multi-target bundle rendering."""

from pathlib import Path

from ohmyclaude.core.targets import (
    HarnessBundleBuilder,
    HarnessTarget,
    RenderedBundle,
    RenderedFile,
)


class TestHarnessBundleBuilder:
    """Tests for explicit target bundle generation."""

    def test_render_codex_project_bundle(self) -> None:
        """Codex project bundles should include core project assets."""
        builder = HarnessBundleBuilder()

        bundle = builder.render_bundle(HarnessTarget.CODEX_PROJECT, "standard")
        paths = {file.relative_path for file in bundle.files}
        config_file = next(
            file for file in bundle.files if file.relative_path == ".codex/config.toml"
        )

        assert "AGENTS.md" in paths
        assert ".codex/config.toml" in paths
        assert ".codex/agents/explorer.toml" in paths
        assert ".codex/agents/reviewer.toml" in paths
        assert ".codex/agents/docs_researcher.toml" in paths
        assert ".codex/agents/security_reviewer.toml" in paths
        assert "[agents.security_reviewer]" in config_file.content
        assert any(path.startswith(".agents/skills/coding-standards/") for path in paths)
        assert any(path.startswith(".agents/skills/tdd-workflow/") for path in paths)
        assert any(path.startswith(".agents/skills/search-first/") for path in paths)

    def test_render_gemini_extension_bundle(self) -> None:
        """Gemini extension bundles should include manifest, context, and commands."""
        builder = HarnessBundleBuilder()

        bundle = builder.render_bundle(HarnessTarget.GEMINI_EXTENSION, "starter")
        paths = {file.relative_path for file in bundle.files}

        assert "gemini-extension.json" in paths
        assert "GEMINI.md" in paths
        assert any(path.startswith("commands/") and path.endswith(".toml") for path in paths)
        assert "agents/security-reviewer.md" in paths
        assert any(path.startswith("skills/coding-standards/") for path in paths)
        assert any(path.startswith("skills/tdd-workflow/") for path in paths)
        assert any(path.startswith("skills/search-first/") for path in paths)

    def test_portable_hooks_are_self_contained(self) -> None:
        """Portable bundle hooks should reference bundle-local paths instead of Claude home."""
        builder = HarnessBundleBuilder()

        claude_plugin = builder.render_bundle(HarnessTarget.CLAUDE_PLUGIN, "full")
        gemini_extension = builder.render_bundle(HarnessTarget.GEMINI_EXTENSION, "full")

        plugin_hooks = next(
            file for file in claude_plugin.files if file.relative_path == "hooks/hooks.json"
        )
        gemini_hooks = next(
            file for file in gemini_extension.files if file.relative_path == "hooks/hooks.json"
        )

        assert "OHMYCLAUDE_ROOT" not in plugin_hooks.content
        assert "~/.claude" not in plugin_hooks.content
        assert "${CLAUDE_PLUGIN_ROOT}" in plugin_hooks.content

        assert "OHMYCLAUDE_ROOT" not in gemini_hooks.content
        assert "~/.claude" not in gemini_hooks.content
        assert "${extensionPath}" in gemini_hooks.content

    def test_render_full_portable_bundles_include_skill_rules(self) -> None:
        """Portable full bundles should include the skill-rules file."""
        builder = HarnessBundleBuilder()

        claude_plugin = builder.render_bundle(HarnessTarget.CLAUDE_PLUGIN, "full")
        gemini_extension = builder.render_bundle(HarnessTarget.GEMINI_EXTENSION, "full")

        plugin_paths = {file.relative_path for file in claude_plugin.files}
        gemini_paths = {file.relative_path for file in gemini_extension.files}

        assert "skills/skill-rules.json" in plugin_paths
        assert "skills/skill-rules.json" in gemini_paths

    def test_render_codex_command_uses_bridge_wording(self) -> None:
        """Generated Codex commands should use bridge wording instead of legacy branding."""
        builder = HarnessBundleBuilder()

        bundle = builder.render_bundle(HarnessTarget.CLAUDE_HOME, "full")
        codex_command = next(
            file for file in bundle.files if file.relative_path == "commands/codex.md"
        )

        assert "Claude-side compatibility wrapper" in codex_command.content
        assert "CodexMCP" not in codex_command.content

    def test_install_bundle_writes_files(self, tmp_path: Path) -> None:
        """Installing a bundle should write all rendered files to the explicit destination."""
        builder = HarnessBundleBuilder()
        bundle = builder.render_bundle(HarnessTarget.CLAUDE_PLUGIN, "standard")

        result = builder.install_bundle(bundle, tmp_path)

        assert result.written_files == len(bundle.files) + 1
        assert (tmp_path / ".claude-plugin" / "plugin.json").exists()
        assert (tmp_path / ".claude-plugin" / "ohmyclaude-manifest.json").exists()
        assert (tmp_path / "commands").exists()

    def test_install_bundle_creates_targeted_backup(self, tmp_path: Path) -> None:
        """Backups should contain only managed files that existed before install."""
        builder = HarnessBundleBuilder()
        existing_file = tmp_path / "AGENTS.md"
        existing_file.parent.mkdir(parents=True, exist_ok=True)
        existing_file.write_text("old content", encoding="utf-8")

        bundle = RenderedBundle(
            target=HarnessTarget.CODEX_PROJECT,
            preset_name="standard",
            files=(RenderedFile("AGENTS.md", "new content\n"),),
        )

        result = builder.install_bundle(bundle, tmp_path, backup=True)

        assert result.backup_path is not None
        assert (result.backup_path / "AGENTS.md").exists()
        assert existing_file.read_text(encoding="utf-8") == "new content\n"

    def test_install_bundle_removes_stale_managed_files(self, tmp_path: Path) -> None:
        """Repeated installs should clean previously managed files that are no longer rendered."""
        builder = HarnessBundleBuilder()
        initial_bundle = RenderedBundle(
            target=HarnessTarget.CLAUDE_PLUGIN,
            preset_name="full",
            files=(
                RenderedFile("commands/old.md", "old\n"),
                RenderedFile("commands/new.md", "new\n"),
            ),
        )
        updated_bundle = RenderedBundle(
            target=HarnessTarget.CLAUDE_PLUGIN,
            preset_name="starter",
            files=(RenderedFile("commands/new.md", "newer\n"),),
        )

        builder.install_bundle(initial_bundle, tmp_path)
        builder.install_bundle(updated_bundle, tmp_path)

        assert not (tmp_path / "commands" / "old.md").exists()
        assert (tmp_path / "commands" / "new.md").read_text(encoding="utf-8") == "newer\n"
