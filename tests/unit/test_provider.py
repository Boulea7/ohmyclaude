"""Unit tests for provider switching engine."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ohmyclaude.core.provider import ProviderSwitcher
from ohmyclaude.models.provider import ProviderConfig


class TestProviderSwitcher:
    """Tests for ProviderSwitcher class."""

    @pytest.fixture
    def switcher(self, tmp_path: Path):
        """Create a ProviderSwitcher with mocked paths."""
        settings_file = tmp_path / "settings.json"
        providers_file = tmp_path / "providers.yaml"
        codex_auth_file = tmp_path / "codex" / "auth.json"

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", providers_file):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", codex_auth_file):
                    yield ProviderSwitcher()

    @pytest.fixture
    def setup_settings(self, tmp_path: Path):
        """Set up a mock settings.json file."""
        settings_file = tmp_path / "settings.json"

        def _setup(data: dict):
            settings_file.write_text(json.dumps(data))
            return settings_file

        return _setup

    def test_init(self, tmp_path: Path):
        """Test ProviderSwitcher initialization."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            assert switcher._custom_providers == {}

    def test_init_with_custom_providers(self, tmp_path: Path):
        """Test initialization loads custom providers from YAML."""
        providers_file = tmp_path / "providers.yaml"
        providers_file.write_text("""
providers:
  my_provider:
    display_name: My Custom Provider
    anthropic_base_url: https://api.example.com/v1
    anthropic_token_env: MY_TOKEN
""")

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", providers_file):
            switcher = ProviderSwitcher()

            assert "my_provider" in switcher._custom_providers
            assert switcher._custom_providers["my_provider"].display_name == "My Custom Provider"

    def test_get_all_providers(self, switcher: ProviderSwitcher):
        """Test get_all_providers returns built-in and custom providers."""
        providers = switcher.get_all_providers()

        # Should include built-in providers
        assert "official" in providers
        assert "glm" in providers

    def test_get_provider_builtin(self, switcher: ProviderSwitcher):
        """Test get_provider returns built-in provider."""
        provider = switcher.get_provider("official")

        assert provider is not None
        assert provider.name == "official"
        assert provider.is_builtin is True

    def test_get_provider_not_found(self, switcher: ProviderSwitcher):
        """Test get_provider returns None for unknown provider."""
        provider = switcher.get_provider("nonexistent")

        assert provider is None

    def test_get_current_official(self, tmp_path: Path):
        """Test get_current detects official provider."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"env": {}}))

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                switcher = ProviderSwitcher()
                current = switcher.get_current()

                assert current == "official"

    def test_get_current_from_marker(self, tmp_path: Path):
        """Test get_current reads provider marker."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({
            "env": {"_OHMYCLAUDE_PROVIDER": "glm"}
        }))

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                switcher = ProviderSwitcher()
                current = switcher.get_current()

                assert current == "glm"

    def test_get_current_no_settings(self, tmp_path: Path):
        """Test get_current when settings.json doesn't exist."""
        settings_file = tmp_path / "settings.json"
        # Don't create the file

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                switcher = ProviderSwitcher()
                current = switcher.get_current()

                assert current == "official"

    def test_switch_unknown_provider(self, tmp_path: Path):
        """Test switch fails for unknown provider without base_url."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                switcher = ProviderSwitcher()
                result = switcher.switch("unknown_provider")

                assert result.success is False
                assert "Unknown provider" in result.message

    def test_switch_missing_token(self, tmp_path: Path):
        """Test switch fails when token is missing."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch.dict(os.environ, {}, clear=True):
                    switcher = ProviderSwitcher()
                    result = switcher.switch("glm")

                    assert result.success is False
                    assert "Token not found" in result.message

    def test_switch_success_with_token(self, tmp_path: Path):
        """Test successful switch with explicit token."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", tmp_path / "codex" / "auth.json"):
                    switcher = ProviderSwitcher()
                    result = switcher.switch("glm", token="test-token")

                    assert result.success is True
                    assert result.provider_name == "glm"
                    assert "Successfully switched" in result.message

    def test_switch_updates_settings(self, tmp_path: Path):
        """Test switch updates settings.json correctly."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"model": "sonnet"}))

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", tmp_path / "codex" / "auth.json"):
                    switcher = ProviderSwitcher()
                    switcher.switch("glm", token="test-token")

                    # Verify settings were updated
                    updated = json.loads(settings_file.read_text())
                    assert "env" in updated
                    assert updated["env"]["_OHMYCLAUDE_PROVIDER"] == "glm"

    def test_switch_creates_backup(self, tmp_path: Path):
        """Test switch creates backup of settings.json."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"original": True}))

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", tmp_path / "codex" / "auth.json"):
                    switcher = ProviderSwitcher()
                    result = switcher.switch("official")

                    assert result.settings_backup is not None
                    backup_path = Path(result.settings_backup)
                    assert backup_path.exists()
                    assert json.loads(backup_path.read_text())["original"] is True

    def test_switch_skip_codex(self, tmp_path: Path):
        """Test switch with skip_codex option."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", tmp_path / "codex" / "auth.json"):
                    switcher = ProviderSwitcher()
                    result = switcher.switch("glm", token="test-token", skip_codex=True)

                    assert result.success is True
                    assert result.codex_updated is False

    def test_switch_to_official(self, tmp_path: Path):
        """Test switch to official doesn't require token."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}")

        with patch("ohmyclaude.core.provider.SETTINGS_FILE", settings_file):
            with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
                with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", tmp_path / "codex" / "auth.json"):
                    with patch.dict(os.environ, {}, clear=True):
                        switcher = ProviderSwitcher()
                        result = switcher.switch("official")

                        assert result.success is True


class TestProviderSwitcherCodex:
    """Tests for Codex auth.json updates."""

    def test_update_codex_no_openai_url(self, tmp_path: Path):
        """Test _update_codex returns early if no OpenAI URL."""
        provider = ProviderConfig(
            name="test",
            display_name="Test",
            anthropic_base_url="https://api.example.com",
            anthropic_token_env="TEST_TOKEN",
            openai_base_url=None,
        )

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            result = switcher._update_codex(provider)

            assert result["updated"] is False
            assert result["reason"] == "no_openai_url"

    def test_update_codex_missing_token(self, tmp_path: Path):
        """Test _update_codex fails without token."""
        provider = ProviderConfig(
            name="test",
            display_name="Test",
            anthropic_base_url="https://api.example.com",
            anthropic_token_env="TEST_TOKEN",
            openai_base_url="https://openai.example.com",
            openai_token_env="TEST_OPENAI_TOKEN",
        )

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            with patch.dict(os.environ, {}, clear=True):
                switcher = ProviderSwitcher()
                result = switcher._update_codex(provider)

                assert result["updated"] is False
                assert result["reason"] == "missing_token"

    def test_update_codex_success(self, tmp_path: Path):
        """Test _update_codex successfully updates auth.json."""
        codex_auth = tmp_path / "codex" / "auth.json"

        provider = ProviderConfig(
            name="test",
            display_name="Test",
            anthropic_base_url="https://api.example.com",
            anthropic_token_env="TEST_TOKEN",
            openai_base_url="https://openai.example.com",
            openai_token_env="TEST_OPENAI_TOKEN",
        )

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            with patch("ohmyclaude.core.provider.CODEX_AUTH_FILE", codex_auth):
                with patch.dict(os.environ, {"TEST_OPENAI_TOKEN": "my-openai-token"}):
                    switcher = ProviderSwitcher()
                    result = switcher._update_codex(provider)

                    assert result["updated"] is True
                    assert codex_auth.exists()

                    auth_data = json.loads(codex_auth.read_text())
                    assert auth_data["OPENAI_API_KEY"] == "my-openai-token"
                    assert auth_data["OPENAI_BASE_URL"] == "https://openai.example.com"


class TestProviderSwitcherHelpers:
    """Tests for helper methods."""

    def test_load_json_nonexistent(self, tmp_path: Path):
        """Test _load_json with nonexistent file."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            result = switcher._load_json(tmp_path / "nonexistent.json")

            assert result == {}

    def test_load_json_valid(self, tmp_path: Path):
        """Test _load_json with valid JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            result = switcher._load_json(json_file)

            assert result == {"key": "value"}

    def test_load_json_corrupt(self, tmp_path: Path):
        """Test _load_json with corrupt JSON creates backup."""
        json_file = tmp_path / "test.json"
        json_file.write_text("invalid json {{{")

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            result = switcher._load_json(json_file)

            assert result == {}
            # Backup should be created
            backups = list(tmp_path.glob("test.json.corrupt-*"))
            assert len(backups) == 1

    def test_backup_file_nonexistent(self, tmp_path: Path):
        """Test _backup_file with nonexistent file."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            result = switcher._backup_file(tmp_path / "nonexistent.json")

            assert result is None

    def test_backup_file_success(self, tmp_path: Path):
        """Test _backup_file creates backup successfully."""
        original = tmp_path / "test.json"
        original.write_text('{"original": true}')

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            backup_path = switcher._backup_file(original)

            assert backup_path is not None
            assert backup_path.exists()
            assert json.loads(backup_path.read_text())["original"] is True

    def test_apply_env_add_keys(self, tmp_path: Path):
        """Test _apply_env adds new keys."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            data = {"env": {"existing": "value"}}
            env_updates = {"new_key": "new_value"}

            result = switcher._apply_env(data, env_updates)

            assert result["env"]["existing"] == "value"
            assert result["env"]["new_key"] == "new_value"

    def test_apply_env_delete_keys(self, tmp_path: Path):
        """Test _apply_env deletes keys marked with None."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            data = {"env": {"to_delete": "value", "keep": "this"}}
            env_updates = {"to_delete": None}

            result = switcher._apply_env(data, env_updates)

            assert "to_delete" not in result["env"]
            assert result["env"]["keep"] == "this"

    def test_apply_env_empty_env(self, tmp_path: Path):
        """Test _apply_env with no existing env section."""
        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", tmp_path / "providers.yaml"):
            switcher = ProviderSwitcher()
            data = {}
            env_updates = {"key": "value"}

            result = switcher._apply_env(data, env_updates)

            assert result["env"]["key"] == "value"


class TestAddCustomProvider:
    """Tests for add_custom_provider method."""

    def test_add_custom_provider_success(self, tmp_path: Path):
        """Test adding a custom provider successfully."""
        providers_file = tmp_path / "providers.yaml"

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", providers_file):
            with patch("ohmyclaude.core.provider.ensure_ohmyclaude_dirs"):
                switcher = ProviderSwitcher()
                result = switcher.add_custom_provider(
                    name="my_custom",
                    display_name="My Custom Provider",
                    base_url="https://api.custom.com/v1",
                    token_env="MY_CUSTOM_TOKEN",
                    description="A custom provider",
                )

                assert result is True
                assert providers_file.exists()

                # Verify provider was added
                assert "my_custom" in switcher._custom_providers

    def test_add_custom_provider_with_openai(self, tmp_path: Path):
        """Test adding a custom provider with OpenAI config."""
        providers_file = tmp_path / "providers.yaml"

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", providers_file):
            with patch("ohmyclaude.core.provider.ensure_ohmyclaude_dirs"):
                switcher = ProviderSwitcher()
                result = switcher.add_custom_provider(
                    name="hybrid",
                    display_name="Hybrid Provider",
                    base_url="https://api.hybrid.com/v1",
                    token_env="HYBRID_TOKEN",
                    openai_base_url="https://openai.hybrid.com/v1",
                    openai_token_env="HYBRID_OPENAI_TOKEN",
                )

                assert result is True

                provider = switcher._custom_providers["hybrid"]
                assert provider.openai_base_url == "https://openai.hybrid.com/v1"

    def test_add_custom_provider_updates_existing(self, tmp_path: Path):
        """Test adding to existing providers.yaml."""
        providers_file = tmp_path / "providers.yaml"
        providers_file.write_text("""
providers:
  existing:
    display_name: Existing Provider
    anthropic_base_url: https://api.existing.com
    anthropic_token_env: EXISTING_TOKEN
""")

        with patch("ohmyclaude.core.provider.PROVIDERS_FILE", providers_file):
            with patch("ohmyclaude.core.provider.ensure_ohmyclaude_dirs"):
                switcher = ProviderSwitcher()
                switcher.add_custom_provider(
                    name="new_provider",
                    display_name="New Provider",
                    base_url="https://api.new.com/v1",
                    token_env="NEW_TOKEN",
                )

                # Both providers should exist
                assert "existing" in switcher._custom_providers
                assert "new_provider" in switcher._custom_providers
