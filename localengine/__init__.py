"""
pyLocalEngine - Python implementation of the LocalEngine localization framework.

This package provides a complete implementation of the LocalEngine specification,
offering automatic locale detection, dynamic locale switching, offline support,
and support for JSON, XML, and YAML locale files.
"""

__version__ = "1.0.0"
__author__ = "Argo Nickerson"
__email__ = "code@envopen.org"
__license__ = "LGPL-2.1"

from .core.engine import LocalEngine
from .core.exceptions import (
    LocaleFileError,
    LocalEngineError,
    LocaleNotFoundError,
    TranslationKeyError,
)
from .core.file_manager import FileManager
from .core.locale_detector import LocaleDetector

__all__ = [
    "LocalEngine",
    "LocaleDetector",
    "FileManager",
    "LocalEngineError",
    "LocaleNotFoundError",
    "LocaleFileError",
    "TranslationKeyError",
]
