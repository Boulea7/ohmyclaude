"""Version checking and update management."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from packaging.version import Version, parse

from ohmyclaude import __version__

PYPI_URL = "https://pypi.org/pypi/ohmyclaude/json"
TIMEOUT = 10  # seconds


@dataclass
class VersionInfo:
    """Version check result."""

    current: str
    latest: str
    is_outdated: bool
    release_url: str | None = None
    error: str | None = None


def parse_version_safe(version_str: str) -> Version:
    """Safely parse version string.

    Args:
        version_str: Version string to parse.

    Returns:
        Parsed Version object, or Version("0.0.0") on error.
    """
    try:
        return parse(version_str)
    except Exception:
        # Fallback for non-standard versions
        return parse("0.0.0")


@lru_cache(maxsize=1)
def fetch_latest_version() -> dict[str, Any] | None:
    """Fetch latest version info from PyPI.

    Returns:
        dict with version info, or None on error.
    """
    try:
        req = Request(
            PYPI_URL,
            headers={
                "Accept": "application/json",
                "User-Agent": f"ohmyclaude/{__version__}",
            },
        )
        with urlopen(req, timeout=TIMEOUT) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
            return data
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def check_version() -> VersionInfo:
    """Check if a newer version is available.

    Returns:
        VersionInfo with comparison result.
    """
    current = __version__

    data = fetch_latest_version()
    if data is None:
        return VersionInfo(
            current=current,
            latest="unknown",
            is_outdated=False,
            error="Unable to fetch version info from PyPI. Check your network connection.",
        )

    try:
        latest = data["info"]["version"]
        release_url = data["info"].get("project_url") or data["info"].get("home_page")

        current_ver = parse_version_safe(current)
        latest_ver = parse_version_safe(latest)

        return VersionInfo(
            current=current,
            latest=latest,
            is_outdated=latest_ver > current_ver,
            release_url=release_url,
        )
    except (KeyError, TypeError) as e:
        return VersionInfo(
            current=current,
            latest="unknown",
            is_outdated=False,
            error=f"Invalid response from PyPI: {e}",
        )


def get_update_command() -> str:
    """Return the appropriate update command.

    Returns:
        pip install command string.
    """
    return "pip install --upgrade ohmyclaude"
