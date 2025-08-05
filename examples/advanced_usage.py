#!/usr/bin/env python3
"""
Advanced usage example with callbacks and dynamic switching.
"""

import time

from localengine import LocalEngine


def locale_change_callback(old_locale, new_locale):
    """Callback function for locale changes."""
    print(f"Locale changed from {old_locale} to {new_locale}")


def main():
    """Demonstrate advanced LocalEngine functionality."""

    print("Advanced LocalEngine Example")
    print("=" * 40)

    # Create engine with custom settings
    engine = LocalEngine(
        default_locale="en-US",
        auto_detect=False,
        cache_timeout=60,  # 1 minute cache
        check_updates_interval=30,  # Check every 30 seconds
    )

    # Add locale change callback
    engine.add_locale_change_callback(locale_change_callback)

    # Test various locales
    locales_to_test = ["en-US", "es-ES", "fr-FR", "de-DE"]

    print("\nTesting dynamic locale switching:")
    for locale in locales_to_test:
        try:
            print(f"\nSwitching to {locale}...")
            engine.set_locale(locale)

            # Display various translations
            print(f"  Greeting: {engine.get_text('greeting')}")
            print(f"  Navigation - Home: {engine.get_text('navigation.home')}")
            print(f"  Navigation - Settings: {engine.get_text('navigation.settings')}")
            print(f"  Button - Save: {engine.get_text('button_labels.save')}")

            # Show metadata
            meta = engine.get_metadata()
            if meta:
                print(f"  File version: {meta.get('version', 'unknown')}")

            time.sleep(1)  # Brief pause between switches

        except Exception as e:
            print(f"  Error with {locale}: {e}")

    # Test cache functionality
    print("\nTesting cache functionality:")
    print(f"Cached locales: {engine.file_manager.get_cached_locales()}")

    # Test key existence
    print("\nTesting key existence:")
    test_keys = ["greeting", "nonexistent_key", "button_labels.ok", "deep.nested.key"]
    for key in test_keys:
        exists = engine.has_key(key)
        print(f"  Key '{key}': {'exists' if exists else 'not found'}")

    # Test error handling with missing keys
    print("\nTesting error handling:")
    try:
        engine.get_text("definitely_missing_key")
    except Exception as e:
        print(f"  Expected error: {type(e).__name__}: {e}")

    # Test clearing cache
    print("\nClearing cache and reloading...")
    engine.clear_cache()
    engine.reload_locale()
    print(f"Cache cleared. Current locale: {engine.get_current_locale()}")

    # Final test with context manager
    print("\nTesting context manager:")
    with LocalEngine(default_locale="fr-FR") as temp_engine:
        greeting = temp_engine.get_text("greeting")
        print(f"  French greeting: {greeting}")

    print("\nAdvanced example completed!")
    engine.stop()


if __name__ == "__main__":
    main()
