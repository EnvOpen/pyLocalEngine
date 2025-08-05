"""
Test suite for the pyLocalEngine library.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from localengine import FileManager, LocaleDetector, LocalEngine
from localengine.core.exceptions import (
    LocaleFileError,
    LocaleNotFoundError,
    TranslationKeyError,
)


class TestLocaleDetector:
    """Test cases for LocaleDetector class."""

    def test_normalize_locale(self):
        """Test locale normalization."""
        assert LocaleDetector._normalize_locale("en_US") == "en-US"
        assert LocaleDetector._normalize_locale("fr_FR.UTF-8") == "fr-FR"
        assert LocaleDetector._normalize_locale("de") == "de-DE"
        assert LocaleDetector._normalize_locale("zh_CN@euro") == "zh-CN"
        assert LocaleDetector._normalize_locale("") == "en-US"
        assert LocaleDetector._normalize_locale(None) == "en-US"

    def test_get_fallback_locales(self):
        """Test fallback locale generation."""
        fallbacks = LocaleDetector.get_fallback_locales("en-US")
        assert "en" in fallbacks
        assert "en-US" not in fallbacks  # Primary locale not in fallbacks

        fallbacks = LocaleDetector.get_fallback_locales("es-MX")
        assert "es" in fallbacks
        assert "es-ES" in fallbacks
        assert "en-US" in fallbacks

    def test_detect_system_locale(self):
        """Test system locale detection."""
        # Test with explicit environment variable patching
        # We need to ensure that only LANG is set and all higher-priority
        # locale variables (LC_ALL, LC_MESSAGES) are cleared

        # Store original values to restore later if needed
        original_env = {}
        locale_vars = ["LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"]

        for var in locale_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]

        try:
            # Clear all locale environment variables first
            for var in locale_vars:
                if var in os.environ:
                    del os.environ[var]

            # Set only LANG to our test value
            os.environ["LANG"] = "fr_FR.UTF-8"

            # Verify our setup
            assert os.environ.get("LANG") == "fr_FR.UTF-8"
            assert "LC_ALL" not in os.environ
            assert "LC_MESSAGES" not in os.environ

            locale = LocaleDetector.detect_system_locale()
            # Should normalize the environment variable
            assert locale == "fr-FR", (
                f"Expected 'fr-FR', got '{locale}'. Environment check - "
                f"LANG: {os.environ.get('LANG')}, "
                f"LC_ALL: {os.environ.get('LC_ALL', 'NOT SET')}, "
                f"LC_MESSAGES: {os.environ.get('LC_MESSAGES', 'NOT SET')}"
            )

        finally:
            # Restore original environment
            for var in locale_vars:
                if var in os.environ:
                    del os.environ[var]
            for var, value in original_env.items():
                os.environ[var] = value


class TestFileManager:
    """Test cases for FileManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.locales_dir = Path(self.temp_dir) / "locales"
        self.locales_dir.mkdir()

        # Create test locale files
        self._create_test_files()

        self.file_manager = FileManager(self.temp_dir)

    def _create_test_files(self):
        """Create test locale files in various formats."""
        # JSON file
        json_data = {
            "meta": {"version": "1.0.0", "locale": "en-US"},
            "greeting": "Hello",
            "nested": {"key": "Nested value"},
        }
        with open(self.locales_dir / "en-US.json", "w") as f:
            json.dump(json_data, f)

        # YAML file
        yaml_data = {
            "meta": {"version": "1.0.0", "locale": "fr-FR"},
            "greeting": "Bonjour",
            "nested": {"key": "Valeur imbriquée"},
        }
        with open(self.locales_dir / "fr-FR.yaml", "w") as f:
            yaml.dump(yaml_data, f)

        # XML file
        xml_content = """<?xml version="1.0"?>
        <root>
            <meta>
                <version>1.0.0</version>
                <locale>de-DE</locale>
            </meta>
            <locale>
                <greeting>Hallo</greeting>
                <nested>
                    <key>Verschachtelter Wert</key>
                </nested>
            </locale>
        </root>"""
        with open(self.locales_dir / "de-DE.xml", "w") as f:
            f.write(xml_content)

    def test_load_json_locale(self):
        """Test loading JSON locale file."""
        data = self.file_manager.load_locale_file("en-US")
        assert data["greeting"] == "Hello"
        assert data["nested"]["key"] == "Nested value"
        assert data["meta"]["locale"] == "en-US"

    def test_load_yaml_locale(self):
        """Test loading YAML locale file."""
        data = self.file_manager.load_locale_file("fr-FR")
        assert data["greeting"] == "Bonjour"
        assert data["nested"]["key"] == "Valeur imbriquée"

    def test_load_xml_locale(self):
        """Test loading XML locale file."""
        data = self.file_manager.load_locale_file("de-DE")
        assert data["greeting"] == "Hallo"
        assert data["nested"]["key"] == "Verschachtelter Wert"
        assert data["meta"]["locale"] == "de-DE"

    def test_cache_functionality(self):
        """Test caching of locale files."""
        # First load
        data1 = self.file_manager.load_locale_file("en-US")
        assert self.file_manager.is_locale_cached("en-US")

        # Second load should come from cache
        data2 = self.file_manager.load_locale_file("en-US")
        assert data1 == data2

        # Force reload
        data3 = self.file_manager.load_locale_file("en-US", force_reload=True)
        assert data1 == data3

    def test_cache_clearing(self):
        """Test cache clearing functionality."""
        self.file_manager.load_locale_file("en-US")
        assert self.file_manager.is_locale_cached("en-US")

        self.file_manager.clear_cache("en-US")
        assert not self.file_manager.is_locale_cached("en-US")

    def test_locale_not_found(self):
        """Test handling of non-existent locale."""
        with pytest.raises(LocaleNotFoundError):
            self.file_manager.load_locale_file("xx-XX")

    def test_validate_locale_file(self):
        """Test locale file validation."""
        assert self.file_manager.validate_locale_file("en-US")
        assert not self.file_manager.validate_locale_file("xx-XX")


class TestLocalEngine:
    """Test cases for LocalEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.locales_dir = Path(self.temp_dir) / "locales"
        self.locales_dir.mkdir()

        # Create test locale files
        self._create_test_files()

        self.engine = LocalEngine(
            base_path=self.temp_dir, default_locale="en-US", auto_detect=False
        )

    def _create_test_files(self):
        """Create test locale files."""
        # English
        en_data = {
            "meta": {"version": "1.0.0", "locale": "en-US"},
            "greeting": "Hello",
            "farewell": "Goodbye",
            "nested": {"message": "Nested message"},
            "button": {"ok": "OK", "cancel": "Cancel"},
        }
        with open(self.locales_dir / "en-US.json", "w") as f:
            json.dump(en_data, f)

        # Spanish
        es_data = {
            "meta": {"version": "1.0.0", "locale": "es-ES"},
            "greeting": "Hola",
            "farewell": "Adiós",
            "nested": {"message": "Mensaje anidado"},
            "button": {"ok": "Aceptar", "cancel": "Cancelar"},
        }
        with open(self.locales_dir / "es-ES.json", "w") as f:
            json.dump(es_data, f)

    def test_get_text_basic(self):
        """Test basic text retrieval."""
        assert self.engine.get_text("greeting") == "Hello"
        assert self.engine.get_text("farewell") == "Goodbye"

    def test_get_text_nested(self):
        """Test nested key retrieval."""
        assert self.engine.get_text("nested.message") == "Nested message"
        assert self.engine.get_text("button.ok") == "OK"
        assert self.engine.get_text("button.cancel") == "Cancel"

    def test_get_text_with_default(self):
        """Test text retrieval with default value."""
        assert self.engine.get_text("nonexistent", default="Default") == "Default"

    def test_get_text_missing_key(self):
        """Test handling of missing translation keys."""
        with pytest.raises(TranslationKeyError):
            self.engine.get_text("definitely_missing_key")

    def test_locale_switching(self):
        """Test dynamic locale switching."""
        # Start with English
        assert self.engine.get_text("greeting") == "Hello"

        # Switch to Spanish
        self.engine.set_locale("es-ES")
        assert self.engine.get_text("greeting") == "Hola"
        assert self.engine.get_current_locale() == "es-ES"

        # Switch back to English
        self.engine.set_locale("en-US")
        assert self.engine.get_text("greeting") == "Hello"

    def test_has_key(self):
        """Test key existence checking."""
        assert self.engine.has_key("greeting")
        assert self.engine.has_key("nested.message")
        assert not self.engine.has_key("nonexistent_key")

    def test_fallback_mechanism(self):
        """Test fallback to default locale."""
        # Switch to Spanish
        self.engine.set_locale("es-ES")

        # Add a key that only exists in English
        en_data = {
            "meta": {"version": "1.0.0", "locale": "en-US"},
            "greeting": "Hello",
            "farewell": "Goodbye",
            "nested": {"message": "Nested message"},
            "button": {"ok": "OK", "cancel": "Cancel"},
            "english_only": "English only text",
        }
        with open(self.locales_dir / "en-US.json", "w") as f:
            json.dump(en_data, f)

        # Force reload of cache
        self.engine.clear_cache()

        # Should fall back to English for missing key
        result = self.engine.get_text("english_only")
        assert result == "English only text"

    def test_locale_change_callbacks(self):
        """Test locale change callbacks."""
        callback_called = []

        def test_callback(old_locale, new_locale):
            callback_called.append((old_locale, new_locale))

        self.engine.add_locale_change_callback(test_callback)
        self.engine.set_locale("es-ES")

        assert len(callback_called) == 1
        assert callback_called[0] == ("en-US", "es-ES")

    def test_get_metadata(self):
        """Test metadata retrieval."""
        metadata = self.engine.get_metadata()
        assert metadata is not None
        assert metadata["version"] == "1.0.0"
        assert metadata["locale"] == "en-US"

    def test_context_manager(self):
        """Test using LocalEngine as context manager."""
        with LocalEngine(base_path=self.temp_dir, auto_detect=False) as engine:
            greeting = engine.get_text("greeting")
            assert greeting == "Hello"

        # Engine should be stopped after context exit
        # (We can't easily test this without exposing internal state)

    def test_cache_operations(self):
        """Test cache-related operations."""
        # Load a locale to populate cache
        self.engine.get_text("greeting")

        # Clear cache
        self.engine.clear_cache()

        # Reload locale
        self.engine.reload_locale()

        # Should still work
        assert self.engine.get_text("greeting") == "Hello"

    def teardown_method(self):
        """Clean up after tests."""
        self.engine.stop()


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_locale_not_found_error(self):
        """Test LocaleNotFoundError."""
        error = LocaleNotFoundError("xx-XX")
        assert error.locale == "xx-XX"
        assert "xx-XX" in str(error)

        custom_error = LocaleNotFoundError("yy-YY", "Custom message")
        assert custom_error.locale == "yy-YY"
        assert str(custom_error) == "Custom message"

    def test_locale_file_error(self):
        """Test LocaleFileError."""
        error = LocaleFileError("/path/to/file")
        assert error.file_path == "/path/to/file"
        assert "/path/to/file" in str(error)

    def test_translation_key_error(self):
        """Test TranslationKeyError."""
        error = TranslationKeyError("missing_key", "en-US")
        assert error.key == "missing_key"
        assert error.locale == "en-US"
        assert "missing_key" in str(error)
        assert "en-US" in str(error)


if __name__ == "__main__":
    pytest.main([__file__])
