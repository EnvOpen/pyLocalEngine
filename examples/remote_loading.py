#!/usr/bin/env python3
"""
Remote locale loading example for pyLocalEngine.

This example demonstrates loading locale files from remote sources
such as GitHub, CDNs, or web servers with proper error handling
and fallback strategies.
"""

import os
import time

from localengine import LocalEngine
from localengine.core.exceptions import LocaleFileError, LocaleNotFoundError


def demo_github_loading():
    """Demonstrate loading locales from GitHub."""
    print("=== GitHub Remote Loading Demo ===")

    # Example GitHub repository with locale files
    github_base = "https://raw.githubusercontent.com/EnvOpen/pyLocalEngine/main"

    try:
        print(f"Loading locales from: {github_base}")
        engine = LocalEngine(
            base_path=github_base,
            default_locale="en-US",
            cache_timeout=60,  # 1 minute cache for demo
            auto_detect=False,
        )

        print(f"Current locale: {engine.get_current_locale()}")
        print(f"Available locales: {engine.get_available_locales()}")

        # Test basic translations
        greeting = engine.get_text("greeting")
        welcome = engine.get_text("welcome_message")
        print(f"Greeting: {greeting}")
        print(f"Welcome: {welcome}")

        # Test locale switching
        for locale in ["es-ES", "fr-FR"]:
            try:
                engine.set_locale(locale)
                greeting = engine.get_text("greeting")
                print(f"{locale} greeting: {greeting}")
            except LocaleNotFoundError as e:
                print(f"Locale {locale} not available: {e}")

        engine.stop()
        print("GitHub loading demo completed successfully!")

    except Exception as e:
        print(f"Error loading from GitHub: {e}")


def demo_fallback_strategy():
    """Demonstrate robust fallback strategy for production use."""
    print("\n=== Fallback Strategy Demo ===")

    def create_engine_with_fallback():
        """Create engine with multiple fallback options."""

        # Option 1: Try remote CDN/GitHub
        remote_sources = [
            "https://cdn.example.com/locales",  # Primary CDN
            "https://raw.githubusercontent.com/user/repo/main",  # GitHub backup
        ]

        for remote_base in remote_sources:
            try:
                print(f"Trying remote source: {remote_base}")
                engine = LocalEngine(
                    base_path=remote_base,
                    cache_timeout=300,
                    check_updates_interval=600,
                    auto_detect=True,
                )
                # Test if it works
                engine.get_text("greeting")
                print(f"Successfully connected to: {remote_base}")
                return engine
            except Exception as e:
                print(f"Failed to connect to {remote_base}: {e}")
                continue

        # Option 2: Fallback to local files
        if os.path.exists("./locales"):
            print("Using local locale files as fallback")
            return LocalEngine(base_path=".", auto_detect=True)

        # Option 3: Ultimate fallback - minimal embedded locales
        print("Using minimal embedded fallback")
        return LocalEngine(
            base_path=".",  # Will use default if no files found
            default_locale="en-US",
            auto_detect=False,
        )

    engine = create_engine_with_fallback()

    try:
        # Test the engine
        greeting = engine.get_text("greeting", default="Hello")
        print(f"Final greeting: {greeting}")

        # Test error handling
        try:
            missing = engine.get_text("definitely_missing_key")
        except Exception:
            missing = engine.get_text("definitely_missing_key", default="Fallback text")
        print(f"Missing key fallback: {missing}")

    finally:
        engine.stop()

    print("Fallback strategy demo completed!")


def demo_caching_behavior():
    """Demonstrate caching and update behavior."""
    print("\n=== Caching Behavior Demo ===")

    # Use local files for predictable behavior
    engine = LocalEngine(
        base_path=".",
        cache_timeout=5,  # Very short cache for demo
        check_updates_interval=10,
        auto_detect=False,
        default_locale="en-US",
    )

    try:
        print("Initial load...")
        start_time = time.time()
        greeting1 = engine.get_text("greeting", default="Hello")
        load_time1 = time.time() - start_time
        print(f"First load: '{greeting1}' (took {load_time1:.4f}s)")

        print("Cached load...")
        start_time = time.time()
        greeting2 = engine.get_text("greeting", default="Hello")
        load_time2 = time.time() - start_time
        print(f"Cached load: '{greeting2}' (took {load_time2:.4f}s)")

        print("Cache status:")
        print(f"  Cached locales: {engine.file_manager.get_cached_locales()}")
        print(
            f"  Current locale cached: "
            f"{engine.file_manager.is_locale_cached(engine.get_current_locale())}"
        )

        print("Forcing reload...")
        start_time = time.time()
        engine.reload_locale()
        greeting3 = engine.get_text("greeting", default="Hello")
        load_time3 = time.time() - start_time
        print(f"Force reload: '{greeting3}' (took {load_time3:.4f}s)")

        print("Clearing cache...")
        engine.clear_cache()
        start_time = time.time()
        greeting4 = engine.get_text("greeting", default="Hello")
        load_time4 = time.time() - start_time
        print(f"After clear: '{greeting4}' (took {load_time4:.4f}s)")

    finally:
        engine.stop()

    print("Caching demo completed!")


def demo_metadata_and_validation():
    """Demonstrate metadata access and file validation."""
    print("\n=== Metadata and Validation Demo ===")

    engine = LocalEngine(base_path=".", auto_detect=False, default_locale="en-US")

    try:
        # Get metadata for current locale
        metadata = engine.get_metadata()
        if metadata:
            print("Current locale metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        else:
            print("No metadata available for current locale")

        # Test validation
        print("\nValidating locale files:")
        test_locales = ["en-US", "es-ES", "fr-FR", "de-DE", "xx-XX"]
        for locale in test_locales:
            is_valid = engine.file_manager.validate_locale_file(locale)
            status = "✓ Valid" if is_valid else "✗ Invalid/Missing"
            print(f"  {locale}: {status}")

        # Show available vs cached
        print(f"\nAvailable locales: {engine.get_available_locales()}")
        print(f"Cached locales: {engine.file_manager.get_cached_locales()}")

    finally:
        engine.stop()

    print("Metadata demo completed!")


def main():
    """Run all remote loading demos."""
    print("pyLocalEngine Remote Loading Examples")
    print("=" * 50)

    # Run demos in sequence
    demo_github_loading()
    demo_fallback_strategy()
    demo_caching_behavior()
    demo_metadata_and_validation()

    print("\n" + "=" * 50)
    print("All remote loading examples completed!")


if __name__ == "__main__":
    main()
