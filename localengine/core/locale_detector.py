"""
Locale detection functionality for the LocalEngine framework.
"""

import locale
import os
import platform
from typing import List, Optional
import sys


class LocaleDetector:
    """Handles automatic detection of user's locale based on system settings."""

    @staticmethod
    def detect_system_locale() -> str:
        """
        Detect the system locale based on environment variables and system settings.

        Returns:
            str: The detected locale in the format 'language-country' (e.g., 'en-US')
        """
        try:
            # Try to get locale from environment variables first
            for env_var in ["LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"]:
                if env_var in os.environ:
                    env_locale = os.environ[env_var]
                    if env_locale and env_locale != "C" and env_locale != "POSIX":
                        return LocaleDetector._normalize_locale(env_locale)

            # Try using Python's locale module
            try:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    return LocaleDetector._normalize_locale(system_locale)
            except (ValueError, TypeError):
                pass

            # Platform-specific detection
            if platform.system() == "Windows":
                return LocaleDetector._detect_windows_locale()
            elif platform.system() == "Darwin":  # macOS
                return LocaleDetector._detect_macos_locale()

            # Default fallback
            return "en-US"

        except Exception:
            # If all detection methods fail, return default
            return "en-US"

    @staticmethod
    def _normalize_locale(locale_string: Optional[str]) -> str:
        """
        Normalize a locale string to the standard format 'language-country'.

        Args:
            locale_string: The raw locale string from system

        Returns:
            str: Normalized locale in format 'language-country'
        """
        if not locale_string:
            return "en-US"

        # Remove encoding and other suffixes (e.g., 'en_US.UTF-8' -> 'en_US')
        locale_parts = locale_string.split(".")[0].split("@")[0]

        # Convert underscore to dash and ensure proper case
        if "_" in locale_parts:
            lang, country = locale_parts.split("_", 1)
            return f"{lang.lower()}-{country.upper()}"
        elif "-" in locale_parts:
            lang, country = locale_parts.split("-", 1)
            return f"{lang.lower()}-{country.upper()}"
        else:
            # Only language provided, try to infer common country
            lang = locale_parts.lower()
            country_mapping = {
                "en": "US",
                "es": "ES",
                "fr": "FR",
                "de": "DE",
                "it": "IT",
                "pt": "PT",
                "ru": "RU",
                "ja": "JP",
                "ko": "KR",
                "zh": "CN",
            }
            country = country_mapping.get(lang, "US")
            return f"{lang}-{country}"

    @staticmethod
    def _detect_windows_locale() -> str:
        """Detect locale on Windows systems."""
        assert sys.platform == "win32", "This method should only be called on Windows"
        try:
            import winreg

            # Try to get locale from Windows registry
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\International",
            ) as key:
                locale_name = winreg.QueryValueEx(key, "LocaleName")[  # type: ignore[attr-defined]
                    0
                ]
                return LocaleDetector._normalize_locale(locale_name)
        except (ImportError, OSError, FileNotFoundError):
            pass

        return "en-US"

    @staticmethod
    def _detect_macos_locale() -> str:
        assert sys.platform == "darwin", "This method should only be called on macOS"
        """Detect locale on macOS systems."""
        try:
            import subprocess

            # Use defaults command to get locale
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleLocale"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                locale_str = result.stdout.strip()
                return LocaleDetector._normalize_locale(locale_str)
        except (Exception,):  # Catch all subprocess and other exceptions
            pass

        return "en-US"

    @staticmethod
    def get_fallback_locales(primary_locale: str) -> List[str]:
        """
        Get a list of fallback locales for the given primary locale.

        Args:
            primary_locale: The primary locale (e.g., 'en-US')

        Returns:
            List[str]: List of fallback locales in order of preference
        """
        fallbacks = []

        if "-" in primary_locale:
            # Add language-only version (e.g., 'en-US' -> 'en')
            language = primary_locale.split("-")[0]
            fallbacks.append(language)

            # Add common variants for the language
            common_variants = {
                "en": ["en-US", "en-GB"],
                "es": ["es-ES", "es-MX"],
                "fr": ["fr-FR", "fr-CA"],
                "de": ["de-DE", "de-AT"],
                "pt": ["pt-PT", "pt-BR"],
                "zh": ["zh-CN", "zh-TW"],
            }

            if language in common_variants:
                for variant in common_variants[language]:
                    if variant != primary_locale and variant not in fallbacks:
                        fallbacks.append(variant)

        # Always include English as final fallback
        if "en-US" not in fallbacks and primary_locale != "en-US":
            fallbacks.append("en-US")
        if "en" not in fallbacks and primary_locale != "en":
            fallbacks.append("en")

        return fallbacks
