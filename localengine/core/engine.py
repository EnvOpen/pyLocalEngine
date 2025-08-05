"""
Main LocalEngine implementation following the LocalEngine specification.
"""

import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import LocalEngineError, LocaleNotFoundError, TranslationKeyError
from .file_manager import FileManager
from .locale_detector import LocaleDetector


class LocalEngine:
    """
    Main LocalEngine class providing localization functionality.

    This implementation follows the LocalEngine specification and provides:
    - Automatic locale detection
    - Dynamic locale switching
    - Offline support with caching
    - Support for JSON, XML, and YAML locale files
    - Fallback mechanism
    - Hot reloading capability
    """

    def __init__(
        self,
        base_path: Union[str, Path] = ".",
        default_locale: str = "en-US",
        auto_detect: bool = True,
        cache_timeout: int = 300,
        check_updates_interval: int = 300,
    ):
        """
        Initialize the LocalEngine.

        Args:
            base_path: Base directory or URL for locale files
            default_locale: Default/fallback locale to use
            auto_detect: Whether to auto-detect system locale
            cache_timeout: Cache timeout in seconds (default: 5 minutes)
            check_updates_interval: Interval to check for file updates in seconds
        """
        self.base_path = base_path
        self.default_locale = default_locale
        self.cache_timeout = cache_timeout
        self.check_updates_interval = check_updates_interval

        # Initialize components
        self.file_manager = FileManager(base_path, cache_timeout)
        self.locale_detector = LocaleDetector()

        # State management
        self._current_locale: Optional[str] = None
        self._fallback_locales: List[str] = []
        self._lock = threading.Lock()
        self._update_thread: Optional[threading.Thread] = None
        self._stop_update_thread = threading.Event()
        self._change_callbacks: List[Callable[[Optional[str], str], None]] = []

        # Initialize locale
        if auto_detect:
            detected_locale = self.locale_detector.detect_system_locale()
            self.set_locale(detected_locale)
        else:
            self.set_locale(default_locale)

        # Start update checker thread
        self._start_update_checker()

    def set_locale(self, locale: str) -> None:
        """
        Set the current locale and load its translations.

        Args:
            locale: The locale to set (e.g., 'en-US')

        Raises:
            LocaleNotFoundError: If the locale cannot be loaded
        """
        old_locale = self._current_locale

        try:
            # Try to load the requested locale
            self.file_manager.load_locale_file(locale)

            with self._lock:
                self._current_locale = locale
                self._fallback_locales = self._get_fallback_locales(locale)

            # Notify callbacks of locale change
            if old_locale != locale:
                self._notify_locale_change(old_locale, locale)

        except LocaleNotFoundError:
            # If requested locale fails, try fallbacks
            fallbacks = self._get_fallback_locales(locale)

            for fallback in fallbacks:
                try:
                    self.file_manager.load_locale_file(fallback)
                    with self._lock:
                        self._current_locale = fallback
                        self._fallback_locales = self._get_fallback_locales(fallback)

                    if old_locale != fallback:
                        self._notify_locale_change(old_locale, fallback)
                    return
                except LocaleNotFoundError:
                    continue

            # If all fallbacks fail, raise error
            raise LocaleNotFoundError(locale)

    def get_current_locale(self) -> str:
        """Get the currently active locale."""
        with self._lock:
            return self._current_locale or self.default_locale

    def get_text(
        self, key: str, default: Optional[str] = None, locale: Optional[str] = None
    ) -> str:
        """
        Get localized text for a given key.

        Args:
            key: The translation key to look up
            default: Default value to return if key is not found
            locale: Specific locale to use (uses current locale if None)

        Returns:
            str: The localized text

        Raises:
            TranslationKeyError: If key is not found and no default is provided
        """
        target_locale = locale or self.get_current_locale()

        # Try current/specified locale first
        try:
            locale_data = self.file_manager.load_locale_file(target_locale)
            value = self._get_nested_value(locale_data, key)
            if value is not None:
                return str(value)
        except LocaleNotFoundError:
            pass

        # Try fallback locales
        if not locale:  # Only use fallbacks if no specific locale was requested
            with self._lock:
                fallbacks = self._fallback_locales.copy()

            for fallback_locale in fallbacks:
                try:
                    locale_data = self.file_manager.load_locale_file(fallback_locale)
                    value = self._get_nested_value(locale_data, key)
                    if value is not None:
                        return str(value)
                except LocaleNotFoundError:
                    continue

        # Return default if provided
        if default is not None:
            return default

        # Raise error if no translation found
        raise TranslationKeyError(key, target_locale)

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[Any]:
        """
        Get a value from nested dictionary using dot notation.

        Args:
            data: The dictionary to search
            key: The key, potentially with dots for nesting

        Returns:
            The value if found, None otherwise
        """
        # Handle simple keys first
        if "." not in key:
            return data.get(key)

        # Handle nested keys
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current

    def has_key(self, key: str, locale: Optional[str] = None) -> bool:
        """
        Check if a translation key exists.

        Args:
            key: The translation key to check
            locale: Specific locale to check (uses current locale if None)

        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            self.get_text(key, locale=locale)
            return True
        except TranslationKeyError:
            return False

    def get_available_locales(self) -> List[str]:
        """Get list of available locales from the file system."""
        available = []

        # This is a simplified implementation - in a real system you might
        # want to scan the directory structure or maintain a manifest
        locales_to_check = [
            self.get_current_locale(),
            self.default_locale,
            "en-US",
            "en-GB",
            "es-ES",
            "fr-FR",
            "de-DE",
        ]

        for locale in locales_to_check:
            if self.file_manager.validate_locale_file(locale):
                if locale not in available:
                    available.append(locale)

        return available

    def reload_locale(self, locale: Optional[str] = None) -> None:
        """
        Force reload of a locale from disk/remote.

        Args:
            locale: Specific locale to reload (current locale if None)
        """
        target_locale = locale or self.get_current_locale()
        self.file_manager.load_locale_file(target_locale, force_reload=True)

    def clear_cache(self, locale: Optional[str] = None) -> None:
        """
        Clear the translation cache.

        Args:
            locale: Specific locale to clear (all locales if None)
        """
        self.file_manager.clear_cache(locale)

    def add_locale_change_callback(self, callback: Callable[[Optional[str], str], None]) -> None:
        """
        Add a callback to be called when the locale changes.

        Args:
            callback: Function to call with (old_locale, new_locale) parameters
        """
        self._change_callbacks.append(callback)

    def remove_locale_change_callback(self, callback: Callable[[Optional[str], str], None]) -> None:
        """
        Remove a locale change callback.

        Args:
            callback: The callback function to remove
        """
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def _notify_locale_change(self, old_locale: Optional[str], new_locale: str) -> None:
        """Notify all registered callbacks of a locale change."""
        for callback in self._change_callbacks:
            try:
                callback(old_locale, new_locale)
            except Exception:
                # Don't let callback errors break the engine
                pass

    def _get_fallback_locales(self, locale: str) -> List[str]:
        """Get fallback locales for the given locale."""
        fallbacks = self.locale_detector.get_fallback_locales(locale)

        # Ensure default locale is in the fallbacks
        if self.default_locale not in fallbacks and self.default_locale != locale:
            fallbacks.append(self.default_locale)

        return fallbacks

    def _start_update_checker(self) -> None:
        """Start the background thread that checks for locale file updates."""
        if self.check_updates_interval > 0:
            self._update_thread = threading.Thread(target=self._update_checker_loop, daemon=True)
            self._update_thread.start()

    def _update_checker_loop(self) -> None:
        """Background loop to check for locale file updates."""
        while not self._stop_update_thread.wait(self.check_updates_interval):
            try:
                # Check if current locale file needs updating
                current_locale = self.get_current_locale()
                if not self.file_manager.is_locale_cached(current_locale):
                    # Cache expired, reload will happen automatically on next access
                    pass
            except Exception:
                # Don't let update checker errors break the engine
                pass

    def stop(self) -> None:
        """Stop the LocalEngine and clean up resources."""
        self._stop_update_thread.set()
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)

        self.clear_cache()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def get_metadata(self, locale: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a locale file.

        Args:
            locale: The locale to get metadata for (current locale if None)

        Returns:
            Dictionary containing metadata or None if not available
        """
        target_locale = locale or self.get_current_locale()

        try:
            locale_data = self.file_manager.load_locale_file(target_locale)
            return locale_data.get("meta")
        except LocaleNotFoundError:
            return None
