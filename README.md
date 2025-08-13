# pyLocalEngine

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-LGPL--2.1-green.svg)](LICENSE)
[![CI/CD Pipeline](https://github.com/EnvOpen/pyLocalEngine/actions/workflows/ci.yml/badge.svg)](https://github.com/EnvOpen/pyLocalEngine/actions/workflows/ci.yml)

The official Python implementation of the LocalEngine localization framework.

!! UNTESTED BETA VERSION !!

## Overview

pyLocalEngine provides a complete, specification-compliant implementation of the LocalEngine localization framework. It offers automatic locale detection, dynamic locale switching, offline support, and comprehensive file format support (JSON, XML, YAML).

## Key Features

✅ **Specification Compliant**: Fully implements the [LocalEngine Architecture](architecture.md)  
✅ **Auto-Detection**: Automatically detects user's system locale  
✅ **Dynamic Switching**: Change locales at runtime without restart  
✅ **Offline Support**: Cached translations work without internet  
✅ **Multiple Formats**: JSON, XML, and YAML locale files  
✅ **Fallback System**: Graceful handling of missing translations  
✅ **Hot Reloading**: Automatic detection of locale file updates  
✅ **Thread Safe**: Safe for use in multi-threaded applications  
✅ **Remote Loading**: Load locale files from URLs or CDNs  

## Quick Start

### Installation

```bash
pip install pyLocalEngine
```

### Basic Usage

```python
from localengine import LocalEngine

# Create engine with auto-detection
engine = LocalEngine()

# Get translations
greeting = engine.get_text('greeting')
print(greeting)  # "Hello" (or your system locale)

# Dynamic locale switching
engine.set_locale('es-ES')
spanish_greeting = engine.get_text('greeting')
print(spanish_greeting)  # "Hola"

# Nested translations
button_text = engine.get_text('button_labels.ok')

# With fallback
safe_text = engine.get_text('missing_key', default='Fallback text')

# Clean up
engine.stop()
```

### Context Manager

```python
with LocalEngine(auto_detect=True) as engine:
    text = engine.get_text('welcome_message')
    # Automatically cleaned up
```

## File Organization

Place your locale files in a `locales/` directory:

```
your_project/
├── locales/
│   ├── en-US.json
│   ├── es-ES.json
│   ├── fr-FR.yaml
│   └── de-DE.xml
└── main.py
```

### Example Locale File (JSON)

```json
{
    "meta": {
        "version": "1.0.0",
        "last_updated": "2025-08-04",
        "description": "English (United States)",
        "locale": "en-US"
    },
    "greeting": "Hello",
    "farewell": "Goodbye",
    "button_labels": {
        "ok": "OK",
        "cancel": "Cancel",
        "save": "Save"
    },
    "messages": {
        "welcome": "Welcome to our application!",
        "error": "An error occurred"
    }
}
```

## Advanced Configuration

```python
from localengine import LocalEngine

engine = LocalEngine(
    base_path="./my_locales",           # Custom directory
    default_locale="en-US",             # Fallback locale
    auto_detect=True,                   # Auto-detect system locale
    cache_timeout=300,                  # Cache for 5 minutes
    check_updates_interval=300          # Check updates every 5 minutes
)
```

## Remote Locale Loading

Load locale files from remote sources:

```python
# From GitHub
github_url = "https://raw.githubusercontent.com/user/repo/main"
engine = LocalEngine(base_path=github_url)

# From CDN
cdn_url = "https://cdn.example.com/locales"
engine = LocalEngine(base_path=cdn_url)
```

## Error Handling

```python
from localengine.core.exceptions import TranslationKeyError, LocaleNotFoundError

try:
    text = engine.get_text('some_key')
except TranslationKeyError:
    text = "Default text"
except LocaleNotFoundError as e:
    print(f"Locale {e.locale} not available")
```

## Callbacks and Events

```python
def on_locale_change(old_locale, new_locale):
    print(f"Switched from {old_locale} to {new_locale}")

engine.add_locale_change_callback(on_locale_change)
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=localengine --cov-report=html
```

## Examples

See the `examples/` directory for complete working examples:

- [`basic_usage.py`](examples/basic_usage.py) - Basic functionality demo
- [`advanced_usage.py`](examples/advanced_usage.py) - Advanced features demo

## Documentation

- **[User Guide](USER.md)** - Complete usage documentation
- **[Architecture](architecture.md)** - LocalEngine specification
- **[API Reference](USER.md#api-reference)** - Detailed API documentation

## Performance

- **Fast**: JSON parsing with intelligent caching
- **Memory Efficient**: Only loads requested locales
- **Network Optimized**: HTTP caching for remote files
- **Thread Safe**: Concurrent access supported

## Compatibility

- **Python**: 3.8+
- **Formats**: JSON, YAML, XML
- **Platforms**: Windows, macOS, Linux
- **Deployment**: Local files, remote URLs, CDNs

## LocalEngine Ecosystem

This implementation is part of the LocalEngine ecosystem:

- ✅ **Specification Compliant**: Follows official LocalEngine architecture
- ✅ **Drop-in Replacement**: Compatible with other LocalEngine implementations
- ✅ **Ecosystem Ready**: Ready for endorsement and ecosystem inclusion

## Contributing

We welcome contributions! Please see our contributing guidelines:

```bash
# Development setup
git clone https://github.com/EnvOpen/pyLocalEngine.git
cd pyLocalEngine
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Code style
black localengine/
isort localengine/
mypy localengine/

# Submit PR
```

## License

Licensed under the GNU Lesser General Public License v2.1 (LGPL-2.1).  
See [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/EnvOpen/pyLocalEngine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EnvOpen/pyLocalEngine/discussions)  
- **Email**: [code@envopen.org](mailto:code@envopen.org)

## Why not Python 9?
Python 9.x is hitting End of life in just 2 months from the initial beta release of this package, for this reason we developed this with versions 3.10+ in mind, while the package still may work we do not recommend using anything before 3.10.x as it will no longer recieve security updates from us or python.

---

**Made with ❤️ by [Env Open](https://envopen.org)**
