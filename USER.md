# LocalEngine User Guide

This is the official user guide for the LocalEngine localization framework. This guide covers the basic usage, file layout, versioning, and hosting of locale files.

## Quick Start

### Installation

```bash
pip install pyLocalEngine
```

### Basic Usage

```python
from localengine import LocalEngine

# Create engine with auto-detection
engine = LocalEngine(auto_detect=True)

# Get translations
greeting = engine.get_text('greeting')
welcome = engine.get_text('welcome_message')

# Switch locales dynamically
engine.set_locale('es-ES')
spanish_greeting = engine.get_text('greeting')

# Use nested keys
button_text = engine.get_text('button_labels.ok')

# Clean up
engine.stop()
```

## File Layout

### Directory Structure

LocalEngine expects locale files to be organized in one of these structures:

**Method 1 (Required):**
```
your_app/
├── locales/
│   ├── en-US.json
│   ├── es-ES.json
│   ├── fr-FR.yaml
│   └── de-DE.xml
└── your_code.py
```

**Method 2 (Optional):**
```
your_app/
├── locales/
│   ├── en-US/
│   │   └── locale.json
│   ├── es-ES/
│   │   └── translations.yaml
│   └── fr-FR/
│       └── locale.xml
└── your_code.py
```

### Supported File Formats

LocalEngine supports three file formats:

#### JSON Format
```json
{
    "meta": {
        "version": "1.0.0",
        "last_updated": "2025-08-04",
        "description": "Locale file for English (United States)",
        "locale": "en-US"
    },
    "greeting": "Hello",
    "farewell": "Goodbye",
    "button_labels": {
        "ok": "OK",
        "cancel": "Cancel"
    }
}
```

#### YAML Format
```yaml
meta:
  version: "1.0.0"
  last_updated: "2025-08-04"
  description: "Locale file for English (United States)"
  locale: "en-US"

greeting: "Hello"
farewell: "Goodbye"
button_labels:
  ok: "OK"
  cancel: "Cancel"
```

#### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <meta>
        <version>1.0.0</version>
        <last_updated>2025-08-04</last_updated>
        <description>Locale file for English (United States)</description>
        <locale>en-US</locale>
    </meta>
    <locale>
        <greeting>Hello</greeting>
        <farewell>Goodbye</farewell>
        <button_labels>
            <ok>OK</ok>
            <cancel>Cancel</cancel>
        </button_labels>
    </locale>
</root>
```

## Advanced Usage

### Configuration Options

```python
from localengine import LocalEngine

engine = LocalEngine(
    base_path="./my_locales",           # Custom locales directory
    default_locale="en-US",             # Fallback locale
    auto_detect=True,                   # Auto-detect system locale
    cache_timeout=300,                  # Cache timeout in seconds
    check_updates_interval=300          # Update check interval
)
```

### Locale Change Callbacks

```python
def on_locale_change(old_locale, new_locale):
    print(f"Locale changed from {old_locale} to {new_locale}")

engine.add_locale_change_callback(on_locale_change)
```

### Error Handling

```python
from localengine.core.exceptions import TranslationKeyError, LocaleNotFoundError

try:
    text = engine.get_text('some_key')
except TranslationKeyError:
    text = "Default text"
except LocaleNotFoundError:
    print("Locale not available")
```

### Context Manager Usage

```python
with LocalEngine(auto_detect=True) as engine:
    greeting = engine.get_text('greeting')
    # Engine automatically stops when exiting context
```

## Versioning

LocalEngine follows semantic versioning for both the library and locale files:

### Library Versioning
- **Major version**: Breaking API changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

### Locale File Versioning
Include version information in your locale files:

```json
{
    "meta": {
        "version": "1.2.3",
        "last_updated": "2025-08-04"
    }
}
```

## Hosting Locale Files via GitHub

You can host your locale files on GitHub and load them remotely:

### Setup GitHub Repository

1. Create a repository for your locale files
2. Organize files in the `locales/` directory
3. Commit and push your files

### Repository Structure
```
my-app-locales/
├── locales/
│   ├── en-US.json
│   ├── es-ES.json
│   ├── fr-FR.json
│   └── de-DE.json
└── README.md
```

### Loading Remote Locales

```python
from localengine import LocalEngine

# Load from GitHub raw URLs
github_base = "https://raw.githubusercontent.com/yourusername/my-app-locales/main"
engine = LocalEngine(base_path=github_base)
```

### GitHub Pages Hosting

For better performance, you can also use GitHub Pages:

1. Enable GitHub Pages in your repository settings
2. Use the GitHub Pages URL as your base path:

```python
pages_base = "https://yourusername.github.io/my-app-locales"
engine = LocalEngine(base_path=pages_base)
```

### Best Practices for Remote Hosting

1. **Use CDN**: Consider using a CDN for better global performance
2. **Cache Headers**: Set appropriate cache headers for your files
3. **Fallback Strategy**: Always include fallback locales locally
4. **Version Management**: Use Git tags for locale file versions

### Example with Fallback

```python
import os
from localengine import LocalEngine

# Try remote first, fallback to local
try:
    if os.path.exists('./locales'):
        # Local development
        engine = LocalEngine(base_path='.')
    else:
        # Production with remote locales
        remote_base = "https://yourdomain.com/locales"
        engine = LocalEngine(base_path=remote_base)
except Exception:
    # Ultimate fallback
    engine = LocalEngine(base_path='.', default_locale='en-US')
```

## API Reference

### LocalEngine Class

#### Constructor
```python
LocalEngine(
    base_path: Union[str, Path] = ".",
    default_locale: str = "en-US",
    auto_detect: bool = True,
    cache_timeout: int = 300,
    check_updates_interval: int = 300
)
```

#### Methods

- `get_text(key, default=None, locale=None)` - Get translated text
- `set_locale(locale)` - Change current locale
- `get_current_locale()` - Get current locale
- `has_key(key, locale=None)` - Check if translation key exists
- `get_available_locales()` - Get list of available locales
- `reload_locale(locale=None)` - Force reload locale from source
- `clear_cache(locale=None)` - Clear translation cache
- `get_metadata(locale=None)` - Get locale file metadata
- `stop()` - Stop engine and cleanup resources

### Exception Classes

- `LocalEngineError` - Base exception class
- `LocaleNotFoundError` - Locale file not found
- `LocaleFileError` - Error loading/parsing locale file
- `TranslationKeyError` - Translation key not found

## Performance Considerations

### Caching
- Locale files are automatically cached in memory
- Default cache timeout is 5 minutes
- Cache can be cleared manually when needed

### File Format Performance
- **JSON**: Fastest parsing, most widely supported
- **YAML**: Human-readable, slightly slower parsing
- **XML**: Most verbose, slowest parsing but good for complex structures

### Memory Usage
- Only requested locales are loaded into memory
- Metadata is loaded separately from translations
- Cache size depends on number of locales and file sizes

## Troubleshooting

### Common Issues

1. **Locale not found**: Check file paths and naming conventions
2. **Key not found**: Verify key exists and check for typos
3. **Parsing errors**: Validate JSON/YAML/XML syntax
4. **Permission errors**: Check file system permissions
5. **Network errors**: Verify remote URLs and connectivity

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

engine = LocalEngine()
# Debug output will show file loading and caching operations
```

### Validation

```python
# Validate a locale file before using
if engine.file_manager.validate_locale_file('en-US'):
    print("Locale file is valid")
else:
    print("Locale file has issues")
```

## Contributing

This LocalEngine implementation is open source. Contributions are welcome!

### Development Setup

```bash
git clone https://github.com/EnvOpen/pyLocalEngine.git
cd pyLocalEngine
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=localengine --cov-report=html
```

### Code Style

```bash
black localengine/
isort localengine/
mypy localengine/
```

## License

This project is licensed under the GNU Lesser General Public License v2.1 (LGPL-2.1).
See the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/EnvOpen/pyLocalEngine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EnvOpen/pyLocalEngine/discussions)
- **Email**: [code@envopen.org](mailto:code@envopen.org)

---

For more detailed information about the LocalEngine specification and architecture, see the [Architecture Document](architecture.md).
