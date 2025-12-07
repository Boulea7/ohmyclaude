"""Unit tests for deep merge algorithm."""

import pytest

from ohmyclaude.core.merge import deep_merge, _deep_copy


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_merge_flat_dicts(self):
        """Test merging flat dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 20, "c": 3}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 20, "c": 3}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {"level1": {"a": 1, "b": 2}}
        override = {"level1": {"b": 20, "c": 3}}

        result = deep_merge(base, override)

        assert result == {"level1": {"a": 1, "b": 20, "c": 3}}

    def test_merge_deeply_nested(self):
        """Test merging deeply nested dictionaries."""
        base = {"l1": {"l2": {"l3": {"value": 1}}}}
        override = {"l1": {"l2": {"l3": {"value": 10, "new": "added"}}}}

        result = deep_merge(base, override)

        assert result == {"l1": {"l2": {"l3": {"value": 10, "new": "added"}}}}

    def test_merge_arrays_deduplication(self):
        """Test array merging with deduplication."""
        base = {"items": [1, 2, 3]}
        override = {"items": [3, 4, 5]}

        result = deep_merge(base, override)

        assert result == {"items": [1, 2, 3, 4, 5]}

    def test_merge_arrays_preserve_order(self):
        """Test that array merge preserves base order."""
        base = {"items": ["a", "b", "c"]}
        override = {"items": ["c", "d", "e"]}

        result = deep_merge(base, override)

        # Base items come first, then unique override items
        assert result["items"] == ["a", "b", "c", "d", "e"]

    def test_merge_arrays_with_dicts(self):
        """Test array merging with dictionary items."""
        base = {"items": [{"id": 1, "name": "a"}]}
        override = {"items": [{"id": 2, "name": "b"}]}

        result = deep_merge(base, override)

        # Both dict items should be present
        assert len(result["items"]) == 2
        assert {"id": 1, "name": "a"} in result["items"]
        assert {"id": 2, "name": "b"} in result["items"]

    def test_merge_does_not_mutate_originals(self):
        """Test that merge doesn't mutate original dicts."""
        base = {"a": 1, "nested": {"b": 2}}
        override = {"nested": {"c": 3}}

        original_base = {"a": 1, "nested": {"b": 2}}
        original_override = {"nested": {"c": 3}}

        deep_merge(base, override)

        assert base == original_base
        assert override == original_override

    def test_merge_empty_base(self):
        """Test merging with empty base dict."""
        base = {}
        override = {"a": 1, "b": 2}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 2}

    def test_merge_empty_override(self):
        """Test merging with empty override dict."""
        base = {"a": 1, "b": 2}
        override = {}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 2}

    def test_merge_both_empty(self):
        """Test merging two empty dicts."""
        base = {}
        override = {}

        result = deep_merge(base, override)

        assert result == {}

    def test_merge_type_conflict_override(self):
        """Test that type conflicts result in override."""
        base = {"key": {"nested": "value"}}
        override = {"key": "simple_value"}

        result = deep_merge(base, override)

        # Override value replaces base dict
        assert result == {"key": "simple_value"}

    def test_merge_complex_structure(self):
        """Test merging complex nested structure."""
        base = {
            "env": {
                "VAR1": "value1",
                "VAR2": "value2",
            },
            "permissions": {
                "allow": ["Read", "Write"],
                "deny": [],
            },
            "mcpServers": {
                "server1": {"command": "cmd1"},
            },
        }
        override = {
            "env": {
                "VAR2": "updated",
                "VAR3": "new",
            },
            "permissions": {
                "allow": ["Write", "Execute"],
            },
            "mcpServers": {
                "server2": {"command": "cmd2"},
            },
        }

        result = deep_merge(base, override)

        assert result["env"] == {"VAR1": "value1", "VAR2": "updated", "VAR3": "new"}
        assert "Read" in result["permissions"]["allow"]
        assert "Write" in result["permissions"]["allow"]
        assert "Execute" in result["permissions"]["allow"]
        assert "server1" in result["mcpServers"]
        assert "server2" in result["mcpServers"]


class TestDeepCopy:
    """Tests for _deep_copy function."""

    def test_deep_copy_flat_dict(self):
        """Test deep copy of flat dictionary."""
        original = {"a": 1, "b": 2}
        copy = _deep_copy(original)

        assert copy == original
        assert copy is not original

    def test_deep_copy_nested_dict(self):
        """Test deep copy of nested dictionary."""
        original = {"level1": {"level2": {"value": 1}}}
        copy = _deep_copy(original)

        assert copy == original
        assert copy["level1"] is not original["level1"]
        assert copy["level1"]["level2"] is not original["level1"]["level2"]

    def test_deep_copy_list(self):
        """Test deep copy of list."""
        original = [1, 2, [3, 4]]
        copy = _deep_copy(original)

        assert copy == original
        assert copy is not original
        assert copy[2] is not original[2]

    def test_deep_copy_mixed_structure(self):
        """Test deep copy of mixed dict/list structure."""
        original = {
            "items": [{"id": 1}, {"id": 2}],
            "nested": {"list": [1, 2, 3]}
        }
        copy = _deep_copy(original)

        assert copy == original
        assert copy["items"] is not original["items"]
        assert copy["items"][0] is not original["items"][0]

    def test_deep_copy_scalar_values(self):
        """Test deep copy with scalar values."""
        assert _deep_copy(42) == 42
        assert _deep_copy("string") == "string"
        assert _deep_copy(True) is True
        assert _deep_copy(None) is None
