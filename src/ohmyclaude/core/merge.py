"""Deep merge algorithm for configuration files.

This module provides utilities for merging nested configuration dictionaries
with support for array deduplication and custom merge strategies.
"""

from typing import Any

from deepmerge import Merger  # type: ignore[attr-defined]


def _merge_arrays_append(
    merger: Merger,
    path: list[Any],
    base: list[Any],
    nxt: list[Any],
) -> list[Any]:
    """Append strategy: combine arrays without duplicates.

    Preserves order from base, then appends unique items from nxt.

    Args:
        merger: Deepmerge Merger instance
        path: Current path in the config tree
        base: Base array
        nxt: Override array

    Returns:
        Merged array with duplicates removed
    """
    seen = set()
    result = []

    for item in base + nxt:
        # Create a hashable key for deduplication
        if isinstance(item, dict):
            # For dicts, use sorted items tuple as key
            key = tuple(sorted(item.items())) if item else ()
        else:
            key = item

        try:
            if key not in seen:
                seen.add(key)
                result.append(item)
        except TypeError:
            # Unhashable items (nested lists, etc.) - just append
            result.append(item)

    return result


# Create custom merger with our strategies
_config_merger = Merger(
    # Type-specific merge strategies
    type_strategies=[
        (list, _merge_arrays_append),
        (dict, ["merge"]),
    ],
    # Fallback strategies for other types
    fallback_strategies=["override"],
    # Type conflict strategies (e.g., dict vs list)
    type_conflict_strategies=["override"],
)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two configuration dictionaries.

    Rules:
    - Nested dicts are recursively merged
    - Arrays are combined with deduplication
    - Scalar values are overridden by the override dict

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary

    Returns:
        New merged dictionary (original dicts are not modified)

    Example:
        >>> base = {"a": {"b": 1, "c": 2}, "items": [1, 2]}
        >>> override = {"a": {"b": 10}, "items": [2, 3]}
        >>> result = deep_merge(base, override)
        >>> result
        {"a": {"b": 10, "c": 2}, "items": [1, 2, 3]}
    """
    # Create copies to avoid mutating originals
    base_copy = _deep_copy(base)
    override_copy = _deep_copy(override)

    return _config_merger.merge(base_copy, override_copy)


def _deep_copy(obj: Any) -> Any:
    """Create a deep copy of nested dicts and lists.

    Args:
        obj: Object to copy

    Returns:
        Deep copy of the object
    """
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(item) for item in obj]
    else:
        return obj
