"""
Custom exceptions for the LocalEngine framework.
"""

from typing import Optional


class LocalEngineError(Exception):
    """Base exception class for all LocalEngine errors."""

    pass


class LocaleNotFoundError(LocalEngineError):
    """Raised when a requested locale is not found."""

    def __init__(self, locale: str, message: Optional[str] = None):
        self.locale = locale
        if message is None:
            message = f"Locale '{locale}' not found"
        super().__init__(message)


class LocaleFileError(LocalEngineError):
    """Raised when there's an error loading or parsing a locale file."""

    def __init__(self, file_path: str, message: Optional[str] = None):
        self.file_path = file_path
        if message is None:
            message = f"Error loading locale file '{file_path}'"
        super().__init__(message)


class TranslationKeyError(LocalEngineError):
    """Raised when a translation key is not found."""

    def __init__(self, key: str, locale: Optional[str] = None, message: Optional[str] = None):
        self.key = key
        self.locale = locale
        if message is None:
            if locale:
                message = f"Translation key '{key}' not found for locale '{locale}'"
            else:
                message = f"Translation key '{key}' not found"
        super().__init__(message)
