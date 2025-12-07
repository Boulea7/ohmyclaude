"""Unit tests for atomic file operations."""

import json
from pathlib import Path

import pytest

from ohmyclaude.core.atomic import atomic_write, save_json, save_text


class TestAtomicWrite:
    """Tests for atomic_write context manager."""

    def test_atomic_write_creates_file(self, tmp_path: Path):
        """Test that atomic_write creates a new file."""
        target = tmp_path / "test.txt"

        with atomic_write(target) as f:
            f.write("Hello, World!")

        assert target.exists()
        assert target.read_text() == "Hello, World!"

    def test_atomic_write_creates_parent_dirs(self, tmp_path: Path):
        """Test that atomic_write creates parent directories."""
        target = tmp_path / "nested" / "dir" / "test.txt"

        with atomic_write(target) as f:
            f.write("content")

        assert target.exists()
        assert target.read_text() == "content"

    def test_atomic_write_overwrites_existing(self, tmp_path: Path):
        """Test that atomic_write overwrites existing file."""
        target = tmp_path / "test.txt"
        target.write_text("original")

        with atomic_write(target) as f:
            f.write("updated")

        assert target.read_text() == "updated"

    def test_atomic_write_preserves_original_on_error(self, tmp_path: Path):
        """Test that original file is preserved if write fails."""
        target = tmp_path / "test.txt"
        target.write_text("original")

        with pytest.raises(ValueError):
            with atomic_write(target) as f:
                f.write("partial")
                raise ValueError("Simulated error")

        assert target.read_text() == "original"

    def test_atomic_write_no_temp_file_on_error(self, tmp_path: Path):
        """Test that temp file is cleaned up on error."""
        target = tmp_path / "test.txt"

        with pytest.raises(ValueError):
            with atomic_write(target) as f:
                f.write("content")
                raise ValueError("Simulated error")

        # Only the target should not exist, no temp files
        files = list(tmp_path.iterdir())
        assert len(files) == 0

    def test_atomic_write_binary_mode(self, tmp_path: Path):
        """Test atomic_write in binary mode."""
        target = tmp_path / "test.bin"
        data = b"\x00\x01\x02\x03"

        with atomic_write(target, mode="wb") as f:
            f.write(data)

        assert target.read_bytes() == data

    def test_atomic_write_with_string_path(self, tmp_path: Path):
        """Test atomic_write with string path instead of Path."""
        target = str(tmp_path / "test.txt")

        with atomic_write(target) as f:
            f.write("content")

        assert Path(target).read_text() == "content"


class TestSaveJson:
    """Tests for save_json function."""

    def test_save_json_creates_file(self, tmp_path: Path):
        """Test that save_json creates a JSON file."""
        target = tmp_path / "config.json"
        data = {"key": "value", "number": 42}

        save_json(target, data)

        assert target.exists()
        loaded = json.loads(target.read_text())
        assert loaded == data

    def test_save_json_with_nested_data(self, tmp_path: Path):
        """Test save_json with nested dictionaries."""
        target = tmp_path / "config.json"
        data = {
            "level1": {
                "level2": {
                    "value": "deep"
                }
            },
            "list": [1, 2, 3]
        }

        save_json(target, data)

        loaded = json.loads(target.read_text())
        assert loaded == data

    def test_save_json_with_unicode(self, tmp_path: Path):
        """Test save_json with unicode characters."""
        target = tmp_path / "config.json"
        data = {"chinese": "中文", "emoji": "🎉"}

        save_json(target, data)

        loaded = json.loads(target.read_text())
        assert loaded == data

    def test_save_json_custom_indent(self, tmp_path: Path):
        """Test save_json with custom indentation."""
        target = tmp_path / "config.json"
        data = {"key": "value"}

        save_json(target, data, indent=4)

        content = target.read_text()
        assert "    " in content  # 4-space indent

    def test_save_json_preserves_original_on_error(self, tmp_path: Path, monkeypatch):
        """Test that save_json preserves original on serialization error."""
        target = tmp_path / "config.json"
        target.write_text('{"original": true}')

        # Try to save non-serializable data
        class NotSerializable:
            pass

        with pytest.raises(TypeError):
            save_json(target, {"obj": NotSerializable()})

        # Original should be preserved
        assert json.loads(target.read_text()) == {"original": True}


class TestSaveText:
    """Tests for save_text function."""

    def test_save_text_creates_file(self, tmp_path: Path):
        """Test that save_text creates a text file."""
        target = tmp_path / "test.txt"
        content = "Hello, World!"

        save_text(target, content)

        assert target.exists()
        assert target.read_text() == content

    def test_save_text_with_multiline(self, tmp_path: Path):
        """Test save_text with multiline content."""
        target = tmp_path / "test.txt"
        content = "line1\nline2\nline3"

        save_text(target, content)

        assert target.read_text() == content

    def test_save_text_with_unicode(self, tmp_path: Path):
        """Test save_text with unicode content."""
        target = tmp_path / "test.txt"
        content = "Hello, 世界! 🌍"

        save_text(target, content)

        assert target.read_text() == content

    def test_save_text_overwrites_existing(self, tmp_path: Path):
        """Test that save_text overwrites existing file."""
        target = tmp_path / "test.txt"
        target.write_text("original")

        save_text(target, "updated")

        assert target.read_text() == "updated"
