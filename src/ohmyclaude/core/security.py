"""Security utilities for input validation and sanitization.

This module provides centralized security functions for:
- Path traversal prevention
- URL validation
- Token format validation
- Environment variable sanitization
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Literal

# Allowed URL schemes for API base URLs
ALLOWED_URL_SCHEMES = frozenset({"https", "http"})

# Localhost identifiers for HTTP exception
LOCALHOST_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

# Token format patterns for known providers
TOKEN_PATTERNS = {
    "anthropic": re.compile(r"^sk-ant-[a-zA-Z0-9_-]{40,}$"),
    "openai": re.compile(r"^sk-[a-zA-Z0-9_-]{40,}$"),
    "generic": re.compile(r"^[a-zA-Z0-9_-]{20,200}$"),
}


class ValidationError(ValueError):
    """Raised when validation fails."""

    pass


def validate_path_segment(value: str, label: str = "name") -> str:
    """Validate a path segment to prevent path traversal attacks.

    This function performs comprehensive validation including:
    - Empty value check
    - URL-encoded traversal detection
    - Null byte detection
    - Path separator detection
    - Whitelist character validation

    Args:
        value: User-supplied segment (template name, command name, etc.)
        label: Human-readable label for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If the value contains dangerous patterns
    """
    if not value:
        raise ValidationError(f"Invalid {label}: empty value")

    # Decode URL encoding to detect bypass attempts
    try:
        decoded = urllib.parse.unquote(value)
    except Exception:
        decoded = value

    # Check for null bytes (string truncation attack)
    if "\x00" in value or "\x00" in decoded:
        raise ValidationError(f"Invalid {label}: null byte detected")

    # Check for path traversal patterns in both original and decoded
    dangerous_patterns = ["..", "/", "\\"]
    for pattern in dangerous_patterns:
        if pattern in value or pattern in decoded:
            raise ValidationError(f"Invalid {label}: path traversal pattern detected")

    # Check for leading dot (hidden files)
    if value.startswith(".") or decoded.startswith("."):
        raise ValidationError(f"Invalid {label}: cannot start with dot")

    # Whitelist approach: only allow safe characters
    if not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValidationError(
            f"Invalid {label}: only alphanumeric, underscore, and dash allowed"
        )

    return value


def validate_api_url(url: str, allow_http_localhost: bool = True) -> str:
    """Validate an API base URL.

    Ensures the URL:
    - Has a valid scheme (HTTPS required, HTTP only for localhost)
    - Has a valid host
    - Does not contain dangerous characters

    Args:
        url: URL to validate
        allow_http_localhost: Whether to allow HTTP for localhost

    Returns:
        The validated URL

    Raises:
        ValidationError: If the URL is invalid or potentially dangerous
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")

    # Check scheme
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        raise ValidationError(
            f"Invalid URL scheme '{parsed.scheme}': only HTTPS/HTTP allowed"
        )

    # HTTP only allowed for localhost
    if parsed.scheme == "http":
        if not allow_http_localhost:
            raise ValidationError("HTTP not allowed: use HTTPS")
        if parsed.hostname not in LOCALHOST_HOSTS:
            raise ValidationError(
                f"HTTP only allowed for localhost, not '{parsed.hostname}'"
            )

    # Must have a host
    if not parsed.hostname:
        raise ValidationError("URL must have a hostname")

    # Check for suspicious patterns in URL
    suspicious_patterns = ["<", ">", '"', "'", "{", "}", "|", "^", "`"]
    for pattern in suspicious_patterns:
        if pattern in url:
            raise ValidationError(f"URL contains suspicious character: '{pattern}'")

    return url


def validate_api_token(
    token: str,
    provider: Literal["anthropic", "openai", "generic"] = "generic",
) -> str:
    """Validate an API token format.

    Performs basic format validation without checking if the token is actually valid.

    Args:
        token: Token to validate
        provider: Provider type for specific pattern matching

    Returns:
        The validated token

    Raises:
        ValidationError: If the token format is invalid
    """
    if not token:
        raise ValidationError("Token cannot be empty")

    # Length check
    if len(token) < 20:
        raise ValidationError("Token too short (minimum 20 characters)")

    if len(token) > 500:
        raise ValidationError("Token too long (maximum 500 characters)")

    # Check for whitespace
    if token != token.strip():
        raise ValidationError("Token cannot have leading/trailing whitespace")

    # Provider-specific pattern
    pattern = TOKEN_PATTERNS.get(provider, TOKEN_PATTERNS["generic"])
    if not pattern.match(token):
        # For generic, just ensure safe characters
        if not re.match(r"^[a-zA-Z0-9_.-]+$", token):
            raise ValidationError("Token contains invalid characters")

    return token


def validate_env_var_name(name: str) -> str:
    """Validate an environment variable name.

    Args:
        name: Environment variable name

    Returns:
        The validated name

    Raises:
        ValidationError: If the name is invalid
    """
    if not name:
        raise ValidationError("Environment variable name cannot be empty")

    # Standard env var naming: uppercase letters, digits, underscore
    if not re.match(r"^[A-Z][A-Z0-9_]*$", name):
        raise ValidationError(
            f"Invalid environment variable name '{name}': "
            "must be uppercase with letters, digits, underscore"
        )

    # Prevent dangerous env vars
    dangerous_vars = {
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "PYTHONPATH",
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH",
    }
    if name in dangerous_vars:
        raise ValidationError(f"Cannot set dangerous environment variable: {name}")

    return name


def sanitize_error_message(message: str) -> str:
    """Sanitize error message to remove potentially sensitive information.

    Removes patterns that look like:
    - API keys/tokens
    - File paths containing sensitive directories
    - URLs with credentials

    Args:
        message: Original error message

    Returns:
        Sanitized message
    """
    # Redact API keys/tokens
    message = re.sub(r"sk-ant-[a-zA-Z0-9_-]{40,}", "[REDACTED]", message)
    message = re.sub(r"sk-[a-zA-Z0-9_-]{40,}", "[REDACTED]", message)
    message = re.sub(
        r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9_-]+",
        "api_key=[REDACTED]",
        message,
        flags=re.I,
    )

    # Redact bearer tokens
    message = re.sub(r"Bearer\s+[a-zA-Z0-9_.-]+", "Bearer [REDACTED]", message)

    # Redact URLs with embedded credentials
    message = re.sub(r"://[^:]+:[^@]+@", "://[REDACTED]@", message)

    return message


def safe_tar_extract(
    tar_path: Path,
    dest: Path,
    *,
    allow_symlinks: bool = False,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
) -> list[Path]:
    """Safely extract a tar archive with comprehensive security checks.

    This function provides protection against:
    - Path traversal attacks (../)
    - Symbolic link attacks
    - Device file attacks
    - Zip bomb attacks (size limits)
    - TOCTOU attacks (extract individually)

    Args:
        tar_path: Path to the tar archive
        dest: Destination directory
        allow_symlinks: Whether to allow symlinks (default: False)
        max_file_size: Maximum allowed file size in bytes

    Returns:
        List of extracted file paths

    Raises:
        ValidationError: If security checks fail
        tarfile.TarError: If archive is invalid
    """
    import tarfile

    dest = dest.resolve()
    extracted_files: list[Path] = []

    with tarfile.open(tar_path, "r:*") as tar:
        # Phase 1: Validate ALL members before extraction
        for member in tar.getmembers():
            # Check file size (zip bomb protection)
            if member.size > max_file_size:
                raise ValidationError(
                    f"File too large: {member.name} ({member.size} bytes > {max_file_size})"
                )

            # Normalize and resolve path
            member_path = (dest / member.name).resolve()

            # Path traversal check (must be under dest)
            try:
                member_path.relative_to(dest)
            except ValueError:
                raise ValidationError(f"Path traversal detected: {member.name}")

            # Absolute path check
            if member.name.startswith("/"):
                raise ValidationError(f"Absolute paths not allowed: {member.name}")

            # Link checks
            if member.issym() or member.islnk():
                if not allow_symlinks:
                    raise ValidationError(f"Symbolic/hard links not allowed: {member.name}")
                # If allowing symlinks, verify link target is safe
                link_target = (dest / member.linkname).resolve()
                try:
                    link_target.relative_to(dest)
                except ValueError:
                    raise ValidationError(
                        f"Link target escapes destination: {member.name} -> {member.linkname}"
                    )

            # Device file check
            if member.isdev() or member.ischr() or member.isblk() or member.isfifo():
                raise ValidationError(f"Special files not allowed: {member.name}")

        # Phase 2: Extract individually to avoid TOCTOU
        for member in tar.getmembers():
            if member.isfile() or member.isdir():
                # Use data filter if available (Python 3.12+)
                if hasattr(tarfile, "data_filter"):
                    tar.extract(member, dest, filter="data")
                else:
                    tar.extract(member, dest)

                extracted_path = dest / member.name
                extracted_files.append(extracted_path)

    return extracted_files
