"""Runtime tests for the skill activation hook."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


def _tsx_available() -> bool:
    """Return True when tsx can run without downloading packages."""
    if shutil.which("npx") is None:
        return False

    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


@pytest.mark.skipif(not _tsx_available(), reason="tsx is not available locally")
def test_project_skill_rules_override_bundle_defaults(tmp_path: Path) -> None:
    """Project-level skill rules should override bundle-local defaults."""
    repo_root = Path(__file__).resolve().parents[2]
    source_script = (
        repo_root
        / "src"
        / "ohmyclaude"
        / "templates"
        / "hooks"
        / "skill-activation-prompt.ts"
    )

    bundle_root = tmp_path / "bundle"
    hooks_dir = bundle_root / "hooks"
    skills_dir = bundle_root / "skills"
    project_dir = tmp_path / "project"
    project_rules_dir = project_dir / ".claude" / "skills"
    home_dir = tmp_path / "home"

    hooks_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)
    project_rules_dir.mkdir(parents=True)
    home_dir.mkdir()

    script_path = hooks_dir / "skill-activation-prompt.ts"
    script_path.write_text(source_script.read_text(encoding="utf-8"), encoding="utf-8")

    bundle_rules = {
        "version": "1.0",
        "skills": {
            "search-first": {
                "type": "domain",
                "enforcement": "suggest",
                "priority": "high",
                "promptTriggers": {"keywords": ["compare"]},
            }
        },
    }
    project_rules = {
        "version": "1.0",
        "skills": {
            "deep-research": {
                "type": "domain",
                "enforcement": "suggest",
                "priority": "high",
                "promptTriggers": {"keywords": ["compare"]},
            }
        },
    }

    (skills_dir / "skill-rules.json").write_text(
        json.dumps(bundle_rules),
        encoding="utf-8",
    )
    (project_rules_dir / "skill-rules.json").write_text(
        json.dumps(project_rules),
        encoding="utf-8",
    )

    hook_input = {
        "session_id": "test-session",
        "transcript_path": str(tmp_path / "session.jsonl"),
        "cwd": str(project_dir),
        "permission_mode": "default",
        "prompt": "Please compare these options before implementation",
    }
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["HOME"] = str(home_dir)

    result = subprocess.run(
        ["npx", "--no-install", "tsx", str(script_path)],
        input=json.dumps(hook_input),
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=project_dir,
    )

    assert result.returncode == 0, result.stderr
    assert "deep-research" in result.stdout
    assert "search-first" not in result.stdout
