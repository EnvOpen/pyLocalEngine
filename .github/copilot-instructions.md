# pyLocalEngine Copilot Instructions

## Project Overview

pyLocalEngine is a specification-compliant Python implementation of the LocalEngine localization framework. It provides automatic locale detection, dynamic switching, and multi-format support (JSON/XML/YAML) with intelligent caching and fallback mechanisms.

## Architecture

### Core Components (localengine/core/)
- **LocalEngine** (`engine.py`) - Main orchestrator with thread-safe state management
- **FileManager** (`file_manager.py`) - Handles loading/parsing/caching of locale files  
- **LocaleDetector** (`locale_detector.py`) - Auto-detects system locale with platform-specific logic
- **Exceptions** (`exceptions.py`) - Custom exception hierarchy for error handling

### Key Design Patterns

**Threaded Architecture**: Engine runs background thread for hot-reloading (5min intervals). Always use `engine.stop()` or context manager to clean up threads.

**Dot Notation Access**: Translation keys support nested access via dots (`button_labels.ok`). Use `_get_nested_value()` for safe traversal.

**Fallback Chain**: Locale resolution follows: requested → language-only → common variants → default locale. See `LocaleDetector.get_fallback_locales()`.

**Multi-Format Support**: File extensions auto-detected (.json/.yaml/.xml). XML uses special `<meta>` and `<locale>` structure.

## Development Workflow

### Setup & Testing
```bash
make install-dev    # Install with dev dependencies  
make test          # Run pytest suite
make test-cov      # Run with coverage
make format        # Black + isort formatting
make example       # Run basic example
```

### Common Operations

**Adding New Locale Support**: Place files in `locales/` following pattern: `{locale}.{json|yaml|xml}`. FileManager auto-discovers via `_get_possible_file_paths()`.

**Testing Locale Files**: Use `FileManager.validate_locale_file()` for syntax checking. Test files go in `tests/` with temporary directories.

**Remote Locale Loading**: Engine supports URLs as base_path. FileManager detects via `_check_if_remote()` and uses requests library.

## File Structure Conventions

### Locale Files (locales/)
```json
{
  "meta": {"version": "1.0.0", "locale": "en-US", "last_updated": "2025-08-04"},
  "key": "value",
  "nested": {"subkey": "value"}
}
```

### Test Organization (tests/)
- Class-based tests (`TestLocalEngine`, `TestFileManager`)
- Use `tempfile.mkdtemp()` for isolated test directories
- Mock system calls with `@patch.dict('os.environ')`

### Examples (examples/)
- `basic_usage.py` - Core functionality demo
- `advanced_usage.py` - Callbacks, context managers, error handling

## Critical Implementation Details

**Thread Safety**: All state mutations use `self._lock`. Cache operations are atomic via FileManager's internal locking.

**Cache Management**: 5-minute TTL with background expiry checking. Use `force_reload=True` to bypass cache. Clear on locale changes.

**Error Handling**: Custom exceptions inherit from `LocalEngineError`. Always provide locale context in error messages.

**XML Parsing**: Uses ElementTree with special handling for `<meta>` vs `<locale>` sections. See `_parse_xml()` method.

**Type Safety**: Uses `Optional[str]` for locale parameters, `Union[str, Path]` for paths. Import from `typing` for compatibility.

## Integration Points

**System Locale Detection**: Platform-specific via environment vars (Linux/macOS) or Windows registry. Falls back to "en-US".

**Remote Loading**: Uses requests library with 30s timeout. Supports HTTP caching headers.

**Background Tasks**: Daemon threads for update checking. Must call `stop()` or use context manager for cleanup.

When modifying core components, run full test suite and both examples to verify specification compliance.
