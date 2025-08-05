#!/usr/bin/env python3
"""
Example usage of the pyLocalEngine library.
"""

from localengine import LocalEngine


def main():
    """Demonstrate basic LocalEngine functionality."""

    # Create engine instance with auto-detection
    print("Creating LocalEngine instance...")
    engine = LocalEngine(auto_detect=True)

    print(f"Detected locale: {engine.get_current_locale()}")
    print(f"Available locales: {engine.get_available_locales()}")

    # Get some translations
    print("\nBasic translations:")
    print(f"Greeting: {engine.get_text('greeting')}")
    print(f"Farewell: {engine.get_text('farewell')}")
    print(f"Welcome: {engine.get_text('welcome_message')}")

    # Get nested translations
    print("\nNested translations:")
    print(f"OK button: {engine.get_text('button_labels.ok')}")
    print(f"Cancel button: {engine.get_text('button_labels.cancel')}")
    print(f"Success message: {engine.get_text('messages.success')}")

    # Test fallback behavior
    print("\nTesting fallback:")
    try:
        missing = engine.get_text("nonexistent_key", default="Default value")
        print(f"Missing key with default: {missing}")
    except Exception as e:
        print(f"Error: {e}")

    # Test locale switching
    print("\nTesting locale switching:")
    for locale in ["es-ES", "fr-FR", "de-DE", "en-US"]:
        try:
            engine.set_locale(locale)
            greeting = engine.get_text("greeting")
            welcome = engine.get_text("welcome_message")
            print(f"{locale}: {greeting} - {welcome}")
        except Exception as e:
            print(f"Could not load {locale}: {e}")

    # Test metadata
    print("\nMetadata:")
    metadata = engine.get_metadata()
    if metadata:
        print(f"Version: {metadata.get('version')}")
        print(f"Last updated: {metadata.get('last_updated')}")
        print(f"Description: {metadata.get('description')}")

    # Clean up
    engine.stop()
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
