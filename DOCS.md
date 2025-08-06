# pyLocalEngine Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Development](#development)
8. [Performance](#performance)
9. [Migration](#migration)
10. [Contributing](#contributing)

## Overview

pyLocalEngine is the official Python implementation of the LocalEngine localization framework. It provides a complete, specification-compliant solution for internationalization (i18n) and localization (l10n) in Python applications.

### Key Features

- **Specification Compliant**: Follows the [LocalEngine Architecture](architecture.md)
- **Multi-Format Support**: JSON, YAML, and XML locale files
- **Automatic Detection**: System locale auto-detection
- **Dynamic Switching**: Runtime locale changes without restart
- **Fallback System**: Robust fallback chain for missing translations
- **Caching**: Intelligent caching with TTL and background updates
- **Thread Safety**: Safe for multi-threaded applications
- **Remote Loading**: Support for CDN and remote locale files
- **High Performance**: Sub-millisecond translation lookups

## Installation

### From PyPI (Recommended)

```bash
pip install pyLocalEngine
```

### From Source

```bash
git clone https://github.com/EnvOpen/pyLocalEngine.git
cd pyLocalEngine
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/EnvOpen/pyLocalEngine.git
cd pyLocalEngine
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from localengine import LocalEngine

# Create engine with auto-detection
engine = LocalEngine()

# Get translations
greeting = engine.get_text('greeting')
welcome = engine.get_text('welcome_message')

# Use nested keys with dot notation
button_ok = engine.get_text('button_labels.ok')

# Handle missing keys gracefully
safe_text = engine.get_text('missing_key', default='Fallback')

# Switch locales dynamically
engine.set_locale('es-ES')
spanish_greeting = engine.get_text('greeting')

# Clean up (or use context manager)
engine.stop()
```

### Context Manager

```python
with LocalEngine(auto_detect=True) as engine:
    text = engine.get_text('greeting')
    # Automatically cleaned up
```

### Configuration

```python
engine = LocalEngine(
    base_path="./locales",              # Custom locale directory
    default_locale="en-US",             # Fallback locale
    auto_detect=True,                   # Auto-detect system locale
    cache_timeout=300,                  # 5-minute cache TTL
    check_updates_interval=300          # Check for updates every 5 minutes
)
```

## Architecture

### Core Components

The library consists of four main components:

1. **LocalEngine** (`localengine.core.engine`) - Main orchestrator
2. **FileManager** (`localengine.core.file_manager`) - File loading and caching
3. **LocaleDetector** (`localengine.core.locale_detector`) - System locale detection
4. **Exceptions** (`localengine.core.exceptions`) - Custom exception hierarchy

### Design Patterns

#### Thread Safety
All operations are thread-safe using internal locking mechanisms. The engine runs a background daemon thread for hot-reloading.

#### Fallback Chain
Locale resolution follows a sophisticated fallback chain:
1. Requested locale (e.g., 'es-MX')
2. Language-only variant (e.g., 'es')
3. Common language variants (e.g., 'es-ES')
4. Default locale (e.g., 'en-US')

#### Caching Strategy
- 5-minute TTL by default
- Background cache expiry checking
- Atomic cache operations
- Force reload capability

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

**Parameters:**
- `base_path`: Directory or URL containing locale files
- `default_locale`: Fallback locale identifier
- `auto_detect`: Whether to auto-detect system locale
- `cache_timeout`: Cache timeout in seconds
- `check_updates_interval`: Background update check interval

#### Core Methods

##### `get_text(key, default=None, locale=None)`
Get localized text for a translation key.

```python
# Basic usage
text = engine.get_text('greeting')

# With fallback
text = engine.get_text('missing_key', default='Default text')

# Specific locale
text = engine.get_text('greeting', locale='es-ES')

# Nested keys
text = engine.get_text('button_labels.ok')
```

##### `set_locale(locale)`
Change the current locale.

```python
engine.set_locale('fr-FR')
```

##### `get_current_locale()`
Get the currently active locale.

```python
current = engine.get_current_locale()
```

##### `has_key(key, locale=None)`
Check if a translation key exists.

```python
if engine.has_key('greeting'):
    text = engine.get_text('greeting')
```

##### `get_available_locales()`
Get list of available locales.

```python
locales = engine.get_available_locales()
```

##### `get_metadata(locale=None)`
Get metadata for a locale file.

```python
meta = engine.get_metadata()
print(f"Version: {meta['version']}")
```

#### Cache Management

##### `clear_cache(locale=None)`
Clear translation cache.

```python
# Clear all
engine.clear_cache()

# Clear specific locale
engine.clear_cache('es-ES')
```

##### `reload_locale(locale=None)`
Force reload from source.

```python
# Reload current locale
engine.reload_locale()

# Reload specific locale
engine.reload_locale('fr-FR')
```

#### Callbacks

##### `add_locale_change_callback(callback)`
Register locale change callback.

```python
def on_change(old_locale, new_locale):
    print(f"Changed from {old_locale} to {new_locale}")

engine.add_locale_change_callback(on_change)
```

##### `remove_locale_change_callback(callback)`
Unregister locale change callback.

```python
engine.remove_locale_change_callback(on_change)
```

#### Cleanup

##### `stop()`
Stop engine and cleanup resources.

```python
engine.stop()
```

### Exception Classes

#### `LocalEngineError`
Base exception for all LocalEngine errors.

#### `LocaleNotFoundError`
Raised when a locale file cannot be found.

```python
try:
    engine.set_locale('xx-XX')
except LocaleNotFoundError as e:
    print(f"Locale not found: {e.locale}")
```

#### `LocaleFileError`
Raised when a locale file cannot be loaded or parsed.

```python
try:
    engine.reload_locale()
except LocaleFileError as e:
    print(f"File error: {e.file_path}")
```

#### `TranslationKeyError`
Raised when a translation key is not found.

```python
try:
    text = engine.get_text('missing_key')
except TranslationKeyError as e:
    print(f"Key not found: {e.key}")
```

## Examples

The `examples/` directory contains comprehensive examples:

### Basic Usage (`examples/basic_usage.py`)
Demonstrates core functionality, locale switching, and error handling.

### Advanced Usage (`examples/advanced_usage.py`)
Shows callbacks, context managers, and advanced configuration.

### Remote Loading (`examples/remote_loading.py`)
Demonstrates loading from GitHub, CDNs, and fallback strategies.

### Performance Benchmark (`examples/benchmark.py`)
Performance testing and optimization guidance.

## Development

### Setup

```bash
git clone https://github.com/EnvOpen/pyLocalEngine.git
cd pyLocalEngine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make install-dev
```

### Development Commands

```bash
make test              # Run tests
make test-cov         # Run tests with coverage
make format           # Format code
make lint             # Check code style
make type-check       # Run type checking
make example          # Run basic example
make clean            # Clean build artifacts
```

### Testing

The test suite uses pytest with comprehensive coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=localengine --cov-report=html

# Run specific test class
pytest tests/test_localengine.py::TestLocalEngine -v
```

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **flake8** for linting

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Performance

### Benchmarks

Based on benchmark results:

- **Engine Creation**: ~1ms
- **Locale Loading**: 2-4ms per file
- **Translation Lookup**: <0.01ms (cached)
- **Cache Speedup**: ~850x faster than uncached
- **Locale Switching**: <0.01ms (cached), ~1ms (fresh)

### Optimization Tips

1. **Use Caching**: Keep default cache settings for best performance
2. **Minimize Locale Files**: Smaller files load faster
3. **JSON Format**: Fastest parsing among supported formats
4. **Pre-load Locales**: Load common locales at startup
5. **Batch Operations**: Group translation calls when possible

## Migration

The `tools/migrate.py` script helps migrate from other localization libraries:

### Supported Source Formats

- **i18next**: JSON/YAML format
- **gettext**: .po files
- **Django**: .po and JSON formats
- **React Intl**: JSON format

### Usage

```bash
# Migrate single file
python tools/migrate.py source.json output/ --source-format i18next --locale en-US

# Migrate directory
python tools/migrate.py ./source_locales ./output --source-format gettext --target-format json
```

### Example Migration

```bash
# From i18next to LocalEngine JSON
python tools/migrate.py ./i18next_locales ./locales \
    --source-format i18next --target-format json

# From gettext to LocalEngine YAML
python tools/migrate.py ./gettext_locales ./locales \
    --source-format gettext --target-format yaml
```

## Contributing

### Guidelines

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Check type annotations

### Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
make test
make format
make type-check

# Commit and push
git commit -m "Add new feature"
git push origin feature/new-feature

# Create pull request
```

### Testing Requirements

- All new code must have tests
- Coverage should not decrease
- Tests must pass on all supported Python versions
- Examples should run without errors

## License

This project is licensed under the GNU Lesser General Public License v2.1 (LGPL-2.1).

## Support

- **Documentation**: [User Guide](USER.md) | [Architecture](architecture.md)
- **Issues**: [GitHub Issues](https://github.com/EnvOpen/pyLocalEngine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EnvOpen/pyLocalEngine/discussions)
- **Email**: [code@envopen.org](mailto:code@envopen.org)

---

For more information about the LocalEngine specification, see the [Architecture Document](architecture.md).
