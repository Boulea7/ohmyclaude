"""Tests for security utilities."""

import pytest

from ohmyclaude.core.security import (
    ValidationError,
    sanitize_error_message,
    validate_api_token,
    validate_api_url,
    validate_env_var_name,
    validate_path_segment,
)


class TestValidatePathSegment:
    """Tests for validate_path_segment function."""

    def test_valid_segment(self):
        """Test valid path segments pass validation."""
        assert validate_path_segment("test") == "test"
        assert validate_path_segment("my-command") == "my-command"
        assert validate_path_segment("template_name") == "template_name"
        assert validate_path_segment("Test123") == "Test123"

    def test_empty_value_raises(self):
        """Test empty value raises ValidationError."""
        with pytest.raises(ValidationError, match="empty value"):
            validate_path_segment("")

    def test_path_traversal_raises(self):
        """Test path traversal patterns raise ValidationError."""
        with pytest.raises(ValidationError, match="path traversal"):
            validate_path_segment("../etc/passwd")

        with pytest.raises(ValidationError, match="path traversal"):
            validate_path_segment("foo/bar")

        with pytest.raises(ValidationError, match="path traversal"):
            validate_path_segment("foo\\bar")

    def test_url_encoded_traversal_raises(self):
        """Test URL-encoded path traversal is detected."""
        with pytest.raises(ValidationError, match="path traversal"):
            validate_path_segment("%2e%2e%2f")  # ../

        with pytest.raises(ValidationError, match="path traversal"):
            validate_path_segment("..%2f")  # ../

    def test_null_byte_raises(self):
        """Test null byte injection is detected."""
        with pytest.raises(ValidationError, match="null byte"):
            validate_path_segment("test\x00.txt")

    def test_hidden_file_raises(self):
        """Test hidden files (starting with dot) are rejected."""
        with pytest.raises(ValidationError, match="cannot start with dot"):
            validate_path_segment(".hidden")

    def test_invalid_characters_raises(self):
        """Test invalid characters are rejected."""
        with pytest.raises(ValidationError, match="only alphanumeric"):
            validate_path_segment("test file")  # space

        with pytest.raises(ValidationError, match="only alphanumeric"):
            validate_path_segment("test@name")  # special char


class TestValidateApiUrl:
    """Tests for validate_api_url function."""

    def test_valid_https_url(self):
        """Test valid HTTPS URLs pass validation."""
        assert validate_api_url("https://api.example.com") == "https://api.example.com"
        assert validate_api_url("https://api.example.com/v1") == "https://api.example.com/v1"

    def test_valid_http_localhost(self):
        """Test HTTP is allowed for localhost."""
        assert validate_api_url("http://localhost:8080") == "http://localhost:8080"
        assert validate_api_url("http://127.0.0.1:8080") == "http://127.0.0.1:8080"

    def test_empty_url_raises(self):
        """Test empty URL raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_url("")

    def test_invalid_scheme_raises(self):
        """Test invalid schemes are rejected."""
        with pytest.raises(ValidationError, match="only HTTPS/HTTP"):
            validate_api_url("ftp://example.com")

        with pytest.raises(ValidationError, match="only HTTPS/HTTP"):
            validate_api_url("file:///etc/passwd")

    def test_http_non_localhost_raises(self):
        """Test HTTP for non-localhost is rejected."""
        with pytest.raises(ValidationError, match="only allowed for localhost"):
            validate_api_url("http://api.example.com")

    def test_missing_hostname_raises(self):
        """Test URL without hostname is rejected."""
        with pytest.raises(ValidationError, match="must have a hostname"):
            validate_api_url("https://")

    def test_suspicious_characters_raises(self):
        """Test suspicious characters are rejected."""
        with pytest.raises(ValidationError, match="suspicious character"):
            validate_api_url("https://api.example.com/<script>")

        with pytest.raises(ValidationError, match="suspicious character"):
            validate_api_url("https://api.example.com?foo='bar'")


class TestValidateApiToken:
    """Tests for validate_api_token function."""

    def test_valid_token(self):
        """Test valid tokens pass validation."""
        valid_token = "sk-ant-api03-" + "a" * 50
        assert validate_api_token(valid_token) == valid_token

        # Generic token
        generic_token = "abcdefghij1234567890"
        assert validate_api_token(generic_token) == generic_token

    def test_empty_token_raises(self):
        """Test empty token raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_token("")

    def test_short_token_raises(self):
        """Test short token raises ValidationError."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_token("short")

    def test_long_token_raises(self):
        """Test overly long token raises ValidationError."""
        with pytest.raises(ValidationError, match="too long"):
            validate_api_token("a" * 600)

    def test_whitespace_raises(self):
        """Test token with whitespace raises ValidationError."""
        with pytest.raises(ValidationError, match="whitespace"):
            validate_api_token("  " + "a" * 30)

        with pytest.raises(ValidationError, match="whitespace"):
            validate_api_token("a" * 30 + "  ")

    def test_invalid_characters_raises(self):
        """Test token with invalid characters raises ValidationError."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_api_token("token with spaces here")

        with pytest.raises(ValidationError, match="invalid characters"):
            validate_api_token("token<script>alert(1)")


class TestValidateEnvVarName:
    """Tests for validate_env_var_name function."""

    def test_valid_env_var(self):
        """Test valid environment variable names pass validation."""
        assert validate_env_var_name("ANTHROPIC_API_KEY") == "ANTHROPIC_API_KEY"
        assert validate_env_var_name("MY_TOKEN") == "MY_TOKEN"
        assert validate_env_var_name("API_KEY_123") == "API_KEY_123"

    def test_empty_name_raises(self):
        """Test empty name raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_env_var_name("")

    def test_lowercase_raises(self):
        """Test lowercase names are rejected."""
        with pytest.raises(ValidationError, match="must be uppercase"):
            validate_env_var_name("my_token")

    def test_starting_with_number_raises(self):
        """Test names starting with number are rejected."""
        with pytest.raises(ValidationError, match="must be uppercase"):
            validate_env_var_name("123_TOKEN")

    def test_dangerous_vars_raises(self):
        """Test dangerous environment variables are rejected."""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_env_var_name("LD_PRELOAD")

        with pytest.raises(ValidationError, match="dangerous"):
            validate_env_var_name("PATH")

        with pytest.raises(ValidationError, match="dangerous"):
            validate_env_var_name("PYTHONPATH")


class TestSanitizeErrorMessage:
    """Tests for sanitize_error_message function."""

    def test_redacts_anthropic_key(self):
        """Test Anthropic API keys are redacted."""
        msg = "Error with key sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890ABCD"
        result = sanitize_error_message(msg)
        assert "sk-ant-" not in result
        assert "[REDACTED]" in result

    def test_redacts_openai_key(self):
        """Test OpenAI API keys are redacted."""
        msg = "Error with key sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH"
        result = sanitize_error_message(msg)
        assert "sk-" not in result
        assert "[REDACTED]" in result

    def test_redacts_bearer_token(self):
        """Test Bearer tokens are redacted."""
        msg = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = sanitize_error_message(msg)
        assert "eyJ" not in result
        assert "[REDACTED]" in result

    def test_redacts_url_credentials(self):
        """Test URL credentials are redacted."""
        msg = "Connecting to https://user:password123@api.example.com"
        result = sanitize_error_message(msg)
        assert "password123" not in result
        assert "[REDACTED]" in result

    def test_preserves_normal_text(self):
        """Test normal error messages are preserved."""
        msg = "File not found: config.json"
        result = sanitize_error_message(msg)
        assert result == msg
