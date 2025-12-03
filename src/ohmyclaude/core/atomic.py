"""Atomic file write operations to prevent corruption.

This module provides context managers for safe file operations that ensure
files are either fully written or left unchanged in case of errors.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator
import os
import tempfile


@contextmanager
def atomic_write(
    path: Path | str,
    mode: str = "w",
    encoding: str = "utf-8",
) -> Generator[IO, None, None]:
    """Context manager for atomic file writes.

    Writes to a temporary file first, then atomically replaces the target.
    If an exception occurs, the original file remains unchanged.

    Args:
        path: Target file path
        mode: File open mode ('w' for text, 'wb' for binary)
        encoding: Text encoding (ignored for binary mode)

    Yields:
        File handle for writing

    Example:
        >>> with atomic_write(Path("config.json")) as f:
        ...     json.dump(data, f, indent=2)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

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
        os.replace(tmp.name, path)
    except Exception:
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


def save_json(path: Path | str, data: dict, indent: int = 2) -> None:
    """Save dictionary as JSON file atomically.

    Args:
        path: Target file path
        data: Dictionary to save
        indent: JSON indentation level
    """
    import json

    with atomic_write(path) as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def save_text(path: Path | str, content: str) -> None:
    """Save text content to file atomically.

    Args:
        path: Target file path
        content: Text content to save
    """
    with atomic_write(path) as f:
        f.write(content)
