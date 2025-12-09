"""Shell environment integration with sentinel block management.

This module provides utilities for managing shell RC file modifications
using sentinel blocks to ensure idempotent operations.
"""

import os
import re
import shlex
from pathlib import Path

# Sentinel markers for idempotent injection
SENTINEL_START = "# >>> ohmyclaude initialize >>>"
SENTINEL_END = "# <<< ohmyclaude initialize <<<"

# Default environment file path
DEFAULT_ENV_FILE = Path.home() / ".ohmyclaude" / "env.sh"

# Characters that could enable shell injection if present in paths
_UNSAFE_PATH_CHARS = frozenset('"\'`$\\;|&<>(){}[]!#')


def _validate_env_file_path(path: Path) -> bool:
    """Validate that env_file path is safe for shell injection.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False if it contains dangerous characters
    """
    path_str = str(path)
    return not any(c in path_str for c in _UNSAFE_PATH_CHARS)


class ShellIntegration:
    """Manage shell RC file modifications with sentinel blocks.

    Supports bash, zsh, and fish shells. All modifications are idempotent -
    calling inject_source multiple times produces the same result.

    Example:
        >>> shell = ShellIntegration()
        >>> print(f"Detected shell: {shell.shell}")
        >>> shell.inject_source(Path("~/.ohmyclaude/env.sh"))
    """

    def __init__(self):
        """Initialize shell integration with auto-detection."""
        self.shell = self._detect_shell()
        self.rc_path = self._get_rc_path()

    def _detect_shell(self) -> str:
        """Detect current shell type.

        Returns:
            Shell name: 'zsh', 'fish', or 'bash' (default)
        """
        shell = os.environ.get("SHELL", "/bin/bash")
        if "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        return "bash"

    def _get_rc_path(self) -> Path:
        """Get RC file path for current shell.

        Returns:
            Path to the shell's RC file
        """
        home = Path.home()
        if self.shell == "zsh":
            return home / ".zshrc"
        elif self.shell == "fish":
            config_dir = home / ".config" / "fish"
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                # Still return intended path; caller will handle IO errors
                pass
            return config_dir / "config.fish"
        return home / ".bashrc"

    def inject_source(self, env_file: Path | None = None) -> bool:
        """Inject source command into RC file using sentinel blocks.

        This operation is idempotent - safe to call multiple times.

        Args:
            env_file: Path to environment file to source (default: ~/.ohmyclaude/env.sh)

        Returns:
            True if injection was successful, False if path is unsafe or IO error
        """
        if env_file is None:
            env_file = DEFAULT_ENV_FILE

        env_file = Path(env_file).expanduser()

        # Validate path to prevent shell injection
        if not _validate_env_file_path(env_file):
            return False

        # Validate RC path and read content
        try:
            if self.rc_path.exists() and self.rc_path.is_dir():
                return False
            if not self.rc_path.exists():
                self.rc_path.touch()
            content = self.rc_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False

        # Remove existing sentinel block if present
        pattern = rf"{re.escape(SENTINEL_START)}.*?{re.escape(SENTINEL_END)}\n?"
        content = re.sub(pattern, "", content, flags=re.DOTALL)

        # Generate new block based on shell type
        if self.shell == "fish":
            block = self._generate_fish_block(env_file)
        else:
            block = self._generate_posix_block(env_file)

        # Append block (ensure single trailing newline)
        content = content.rstrip() + "\n\n" + block + "\n"
        try:
            self.rc_path.write_text(content, encoding="utf-8")
        except OSError:
            return False

        return True

    def remove(self) -> bool:
        """Remove sentinel block from RC file.

        Returns:
            True if removal was successful
        """
        if not self.rc_path.exists():
            return True

        try:
            content = self.rc_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False

        # Remove sentinel block
        pattern = rf"\n*{re.escape(SENTINEL_START)}.*?{re.escape(SENTINEL_END)}\n?"
        new_content = re.sub(pattern, "", content, flags=re.DOTALL)

        if new_content != content:
            try:
                self.rc_path.write_text(new_content.rstrip() + "\n", encoding="utf-8")
            except OSError:
                return False

        return True

    def is_installed(self) -> bool:
        """Check if sentinel block is present in RC file.

        Returns:
            True if sentinel block is found
        """
        if not self.rc_path.exists():
            return False

        try:
            content = self.rc_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return SENTINEL_START in content and SENTINEL_END in content

    def _generate_posix_block(self, env_file: Path) -> str:
        """Generate POSIX shell (bash/zsh) block.

        Args:
            env_file: Path to environment file (must be pre-validated)

        Returns:
            Shell block string
        """
        # Use shlex.quote for safe shell escaping
        quoted_path = shlex.quote(str(env_file))
        return f"""{SENTINEL_START}
#!! Contents within this block are managed by 'ohmyclaude init' !!
export OHMYCLAUDE_ROOT="$HOME/.ohmyclaude"
[ -f {quoted_path} ] && source {quoted_path}
{SENTINEL_END}"""

    def _generate_fish_block(self, env_file: Path) -> str:
        """Generate Fish shell block.

        Args:
            env_file: Path to environment file (must be pre-validated for safe chars)

        Returns:
            Shell block string
        """
        # Fish uses different quoting; path is pre-validated in inject_source()
        return f"""{SENTINEL_START}
#!! Contents within this block are managed by 'ohmyclaude init' !!
set -gx OHMYCLAUDE_ROOT "$HOME/.ohmyclaude"
test -f '{env_file}'; and source '{env_file}'
{SENTINEL_END}"""


def get_shell_info() -> dict:
    """Get information about the current shell environment.

    Returns:
        Dictionary with shell type, RC path, and installation status
    """
    shell = ShellIntegration()
    return {
        "shell": shell.shell,
        "rc_path": str(shell.rc_path),
        "is_installed": shell.is_installed(),
    }
