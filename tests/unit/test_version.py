"""Tests for version checking module."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from ohmyclaude.core.version import (
    VersionInfo,
    check_version,
    fetch_latest_version,
    get_update_command,
    parse_version_safe,
)

if TYPE_CHECKING:
    pass


class TestParseVersionSafe:
    """Tests for parse_version_safe function."""

    def test_valid_version(self) -> None:
        """Test parsing valid version string."""
        ver = parse_version_safe("1.0.0")
        assert str(ver) == "1.0.0"

    def test_valid_version_with_prerelease(self) -> None:
        """Test parsing version with prerelease."""
        ver = parse_version_safe("1.0.0a1")
        assert "1.0.0" in str(ver)

    def test_invalid_version_fallback(self) -> None:
        """Test fallback for invalid version."""
        ver = parse_version_safe("invalid")
        assert str(ver) == "0.0.0"

    def test_empty_string_fallback(self) -> None:
        """Test fallback for empty string."""
        ver = parse_version_safe("")
        assert str(ver) == "0.0.0"


class TestFetchLatestVersion:
    """Tests for fetch_latest_version function."""

    @patch("ohmyclaude.core.version.urlopen")
    def test_successful_fetch(self, mock_urlopen: MagicMock) -> None:
        """Test successful version fetch."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"info": {"version": "1.0.0", "project_url": "https://github.com/..."}}
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        # Clear cache
        fetch_latest_version.cache_clear()

        result = fetch_latest_version()
        assert result is not None
        assert result["info"]["version"] == "1.0.0"

    @patch("ohmyclaude.core.version.urlopen")
    def test_network_error(self, mock_urlopen: MagicMock) -> None:
        """Test handling of network error."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Network error")

        fetch_latest_version.cache_clear()
        result = fetch_latest_version()
        assert result is None

    @patch("ohmyclaude.core.version.urlopen")
    def test_timeout_error(self, mock_urlopen: MagicMock) -> None:
        """Test handling of timeout error."""
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        fetch_latest_version.cache_clear()
        result = fetch_latest_version()
        assert result is None

    @patch("ohmyclaude.core.version.urlopen")
    def test_json_decode_error(self, mock_urlopen: MagicMock) -> None:
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetch_latest_version.cache_clear()
        result = fetch_latest_version()
        assert result is None


class TestCheckVersion:
    """Tests for check_version function."""

    @patch("ohmyclaude.core.version.fetch_latest_version")
    @patch("ohmyclaude.core.version.__version__", "1.0.0")
    def test_outdated_version(self, mock_fetch: MagicMock) -> None:
        """Test detection of outdated version."""
        mock_fetch.return_value = {
            "info": {"version": "1.1.0", "project_url": "https://..."}
        }

        result = check_version()
        assert result.is_outdated is True
        assert result.current == "1.0.0"
        assert result.latest == "1.1.0"
        assert result.error is None

    @patch("ohmyclaude.core.version.fetch_latest_version")
    @patch("ohmyclaude.core.version.__version__", "1.1.0")
    def test_latest_version(self, mock_fetch: MagicMock) -> None:
        """Test when already on latest version."""
        mock_fetch.return_value = {
            "info": {"version": "1.1.0", "project_url": "https://..."}
        }

        result = check_version()
        assert result.is_outdated is False
        assert result.current == "1.1.0"
        assert result.latest == "1.1.0"

    @patch("ohmyclaude.core.version.fetch_latest_version")
    @patch("ohmyclaude.core.version.__version__", "2.0.0")
    def test_newer_than_latest(self, mock_fetch: MagicMock) -> None:
        """Test when local version is newer than PyPI."""
        mock_fetch.return_value = {
            "info": {"version": "1.1.0", "project_url": "https://..."}
        }

        result = check_version()
        assert result.is_outdated is False

    @patch("ohmyclaude.core.version.fetch_latest_version")
    def test_fetch_error(self, mock_fetch: MagicMock) -> None:
        """Test handling of fetch error."""
        mock_fetch.return_value = None

        result = check_version()
        assert result.is_outdated is False
        assert result.error is not None
        assert "network" in result.error.lower()

    @patch("ohmyclaude.core.version.fetch_latest_version")
    def test_invalid_response_missing_info(self, mock_fetch: MagicMock) -> None:
        """Test handling of response missing 'info' key."""
        mock_fetch.return_value = {"data": {}}

        result = check_version()
        assert result.is_outdated is False
        assert result.error is not None

    @patch("ohmyclaude.core.version.fetch_latest_version")
    def test_invalid_response_missing_version(self, mock_fetch: MagicMock) -> None:
        """Test handling of response missing 'version' key."""
        mock_fetch.return_value = {"info": {"project_url": "https://..."}}

        result = check_version()
        assert result.is_outdated is False
        assert result.error is not None


class TestGetUpdateCommand:
    """Tests for get_update_command function."""

    def test_returns_pip_command(self) -> None:
        """Test that correct pip command is returned."""
        cmd = get_update_command()
        assert "pip install --upgrade ohmyclaude" in cmd


class TestVersionInfo:
    """Tests for VersionInfo dataclass."""

    def test_create_basic(self) -> None:
        """Test creating basic VersionInfo."""
        info = VersionInfo(
            current="1.0.0",
            latest="1.1.0",
            is_outdated=True,
        )
        assert info.current == "1.0.0"
        assert info.latest == "1.1.0"
        assert info.is_outdated is True
        assert info.release_url is None
        assert info.error is None

    def test_create_with_all_fields(self) -> None:
        """Test creating VersionInfo with all fields."""
        info = VersionInfo(
            current="1.0.0",
            latest="1.1.0",
            is_outdated=True,
            release_url="https://github.com/...",
            error=None,
        )
        assert info.release_url == "https://github.com/..."

    def test_create_with_error(self) -> None:
        """Test creating VersionInfo with error."""
        info = VersionInfo(
            current="1.0.0",
            latest="unknown",
            is_outdated=False,
            error="Network error",
        )
        assert info.error == "Network error"
