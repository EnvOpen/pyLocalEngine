"""
File management functionality for loading and parsing locale files.
"""

import json
import xml.etree.ElementTree as ET
import yaml
import os
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urlparse
import requests

from .exceptions import LocaleFileError, LocaleNotFoundError


class FileManager:
    """Manages loading, parsing, and caching of locale files."""
    
    def __init__(self, base_path: Union[str, Path], cache_timeout: int = 300):
        """
        Initialize the FileManager.
        
        Args:
            base_path: Base directory or URL for locale files
            cache_timeout: Cache timeout in seconds (default: 5 minutes)
        """
        self.base_path = Path(base_path) if isinstance(base_path, str) else base_path
        self.cache_timeout = cache_timeout
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._is_remote = self._check_if_remote(str(base_path))
    
    @staticmethod
    def _check_if_remote(path: str) -> bool:
        """Check if the base path is a remote URL."""
        try:
            result = urlparse(path)
            return result.scheme in ('http', 'https')
        except Exception:
            return False
    
    def load_locale_file(self, locale: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load a locale file from disk or remote location.
        
        Args:
            locale: The locale identifier (e.g., 'en-US')
            force_reload: Whether to force reload from disk/remote
            
        Returns:
            Dict containing the parsed locale data
            
        Raises:
            LocaleFileError: If the file cannot be loaded or parsed
            LocaleNotFoundError: If the locale file is not found
        """
        with self._lock:
            # Check cache first
            if not force_reload and self._is_cache_valid(locale):
                return self._cache[locale]
            
            # Try to load the file
            locale_data = self._load_from_source(locale)
            
            # Cache the result
            self._cache[locale] = locale_data
            self._cache_timestamps[locale] = time.time()
            
            return locale_data
    
    def _is_cache_valid(self, locale: str) -> bool:
        """Check if cached data is still valid."""
        if locale not in self._cache or locale not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[locale]
        return age < self.cache_timeout
    
    def _load_from_source(self, locale: str) -> Dict[str, Any]:
        """Load locale data from the actual source (file or URL)."""
        file_paths = self._get_possible_file_paths(locale)
        
        for file_path in file_paths:
            try:
                if self._is_remote:
                    return self._load_remote_file(str(file_path))
                else:
                    return self._load_local_file(Path(file_path))
            except (FileNotFoundError, requests.RequestException):
                continue
            except Exception as e:
                raise LocaleFileError(str(file_path), f"Error parsing file: {str(e)}")
        
        raise LocaleNotFoundError(locale, f"No locale file found for '{locale}' in any supported format")
    
    def _get_possible_file_paths(self, locale: str) -> List[Union[str, Path]]:
        """Get list of possible file paths for a locale."""
        file_paths = []
        
        # Method 1: locales/filename.json (required)
        for ext in ['json', 'yaml', 'yml', 'xml']:
            if self._is_remote:
                file_paths.append(f"{self.base_path}/locales/{locale}.{ext}")
            else:
                file_paths.append(self.base_path / "locales" / f"{locale}.{ext}")
        
        # Method 2: locales/localename/filename.json (optional)
        for ext in ['json', 'yaml', 'yml', 'xml']:
            for filename in [locale, 'locale', 'translations']:
                if self._is_remote:
                    file_paths.append(f"{self.base_path}/locales/{locale}/{filename}.{ext}")
                else:
                    file_paths.append(self.base_path / "locales" / locale / f"{filename}.{ext}")
        
        return file_paths
    
    def _load_local_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a local file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_content(content, file_path.suffix.lower())
    
    def _load_remote_file(self, url: str) -> Dict[str, Any]:
        """Load and parse a remote file."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Determine file type from URL
        file_ext = Path(url).suffix.lower()
        
        return self._parse_content(response.text, file_ext)
    
    def _parse_content(self, content: str, file_ext: str) -> Dict[str, Any]:
        """Parse file content based on extension."""
        try:
            if file_ext == '.json':
                return json.loads(content)
            elif file_ext in ['.yaml', '.yml']:
                return yaml.safe_load(content) or {}
            elif file_ext == '.xml':
                return self._parse_xml(content)
            else:
                raise LocaleFileError("", f"Unsupported file format: {file_ext}")
        except json.JSONDecodeError as e:
            raise LocaleFileError("", f"Invalid JSON: {str(e)}")
        except yaml.YAMLError as e:
            raise LocaleFileError("", f"Invalid YAML: {str(e)}")
        except ET.ParseError as e:
            raise LocaleFileError("", f"Invalid XML: {str(e)}")
    
    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """Parse XML content into a dictionary."""
        root = ET.fromstring(content)
        result = {}
        
        # Parse metadata section
        meta_elem = root.find('meta')
        if meta_elem is not None:
            result['meta'] = {}
            for child in meta_elem:
                result['meta'][child.tag] = child.text
        
        # Parse locale section
        locale_elem = root.find('locale')
        if locale_elem is not None:
            for child in locale_elem:
                if len(child) > 0:  # Has sub-elements (nested structure)
                    result[child.tag] = {}
                    for subchild in child:
                        result[child.tag][subchild.tag] = subchild.text
                else:
                    result[child.tag] = child.text
        else:
            # If no locale section, parse all non-meta elements
            for child in root:
                if child.tag != 'meta':
                    if len(child) > 0:
                        result[child.tag] = {}
                        for subchild in child:
                            result[child.tag][subchild.tag] = subchild.text
                    else:
                        result[child.tag] = child.text
        
        return result
    
    def clear_cache(self, locale: Optional[str] = None) -> None:
        """
        Clear the cache for a specific locale or all locales.
        
        Args:
            locale: Specific locale to clear, or None to clear all
        """
        with self._lock:
            if locale:
                self._cache.pop(locale, None)
                self._cache_timestamps.pop(locale, None)
            else:
                self._cache.clear()
                self._cache_timestamps.clear()
    
    def get_cached_locales(self) -> List[str]:
        """Get list of currently cached locales."""
        with self._lock:
            return list(self._cache.keys())
    
    def is_locale_cached(self, locale: str) -> bool:
        """Check if a locale is currently cached and valid."""
        with self._lock:
            return self._is_cache_valid(locale)
    
    def validate_locale_file(self, locale: str) -> bool:
        """
        Validate that a locale file exists and is parseable.
        
        Args:
            locale: The locale to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.load_locale_file(locale, force_reload=True)
            return True
        except (LocaleFileError, LocaleNotFoundError):
            return False
