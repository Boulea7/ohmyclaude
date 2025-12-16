"""Atomic file write operations to prevent corruption.

This module provides context managers for safe file operations that ensure
files are either fully written or left unchanged in case of errors.
"""

import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any


@contextmanager
def atomic_write(
    path: Path | str,
    mode: str = "w",
    encoding: str = "utf-8",
    *,
    file_mode: int | None = None,
    preserve_mode: bool = True,
) -> Generator[IO[str], None, None]:
    """Context manager for atomic file writes.

    Writes to a temporary file first, then atomically replaces the target.
    If an exception occurs, the original file remains unchanged.

    Args:
        path: Target file path
        mode: File open mode ('w' for text, 'wb' for binary)
        encoding: Text encoding (ignored for binary mode)
        file_mode: Optional POSIX mode (e.g., 0o600) to apply to the final file.
        preserve_mode: If True, preserve existing file mode on overwrite (POSIX only).

    Yields:
        File handle for writing

    Example:
        >>> with atomic_write(Path("config.json"), file_mode=0o600) as f:
        ...     json.dump(data, f, indent=2)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    original_mode: int | None = None
    if preserve_mode and os.name != "nt":
        try:
            if path.exists():
                original_mode = path.stat().st_mode & 0o777
        except OSError:
            original_mode = None

    # Determine encoding based on mode
    file_encoding = encoding if "b" not in mode else None

    tmp = tempfile.NamedTemporaryFile(
        mode=mode,
        encoding=file_encoding,
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    )
    try:
        yield tmp
        # Handle case where caller may have closed the file early
        if not tmp.closed:
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
        # Set file permissions before atomic replace (POSIX only)
        if os.name != "nt":
            desired_mode = file_mode if file_mode is not None else original_mode
            if desired_mode is not None:
                try:
                    os.chmod(tmp.name, desired_mode)
                except OSError:
                    pass
        os.replace(tmp.name, path)
    except Exception:
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


def save_json(
    path: Path | str, data: dict[str, Any], indent: int = 2, *, file_mode: int | None = None
) -> None:
    """Save dictionary as JSON file atomically.

    Args:
        path: Target file path
        data: Dictionary to save
        indent: JSON indentation level
        file_mode: Optional POSIX mode for the file (e.g., 0o600).
    """
    import json

    with atomic_write(path, file_mode=file_mode) as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def save_text(path: Path | str, content: str, *, file_mode: int | None = None) -> None:
    """Save text content to file atomically.

    Args:
        path: Target file path
        content: Text content to save
        file_mode: Optional POSIX mode for the file (e.g., 0o600).
    """
    with atomic_write(path, file_mode=file_mode) as f:
        f.write(content)
