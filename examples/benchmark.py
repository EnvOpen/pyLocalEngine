#!/usr/bin/env python3
"""
Performance benchmark script for pyLocalEngine.

This script measures the performance of various operations
to help identify bottlenecks and optimization opportunities.
"""

import json
import statistics
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

from localengine import LocalEngine


@contextmanager
def measure_time():
    """Context manager to measure execution time."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start
    end = time.perf_counter() - start


def create_test_locale_files(base_path: Path, num_keys: int = 1000):
    """Create test locale files with specified number of keys."""
    locales_dir = base_path / "locales"
    locales_dir.mkdir()

    # Create base translations
    translations: Dict[str, Any] = {
        "meta": {"version": "1.0.0", "locale": "en-US", "last_updated": "2025-08-04"}
    }

    # Add simple keys
    for i in range(num_keys // 2):
        translations[f"key_{i}"] = f"Translation {i}"

    # Add nested keys
    nested: Dict[str, Any] = {}
    for i in range(num_keys // 2):
        nested[f"nested_key_{i}"] = f"Nested translation {i}"
    translations["nested"] = nested

    # Create locale files
    locales = ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP"]
    for locale in locales:
        locale_data: Dict[str, Any] = translations.copy()
        locale_data["meta"]["locale"] = locale

        # Modify translations slightly for each locale
        for key in locale_data:
            if isinstance(locale_data[key], str):
                locale_data[key] = f"[{locale}] {locale_data[key]}"

        file_path = locales_dir / f"{locale}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(locale_data, f, indent=2)

    return locales


def benchmark_engine_creation():
    """Benchmark LocalEngine creation time."""
    print("Benchmarking engine creation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path)

        times = []
        for _ in range(10):
            with measure_time() as get_time:
                engine = LocalEngine(base_path=temp_path, auto_detect=False, default_locale="en-US")
                engine.stop()
            times.append(get_time())

        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times)
        print(f"  Engine creation: {avg_time:.4f}s ± {std_dev:.4f}s")

        return avg_time


def benchmark_locale_loading():
    """Benchmark locale file loading."""
    print("Benchmarking locale loading...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path, num_keys=5000)

        engine = LocalEngine(
            base_path=temp_path,
            auto_detect=False,
            default_locale="en-US",
            cache_timeout=0,  # Disable caching for pure load testing
        )

        try:
            for locale in locales:
                times = []
                for _ in range(5):
                    engine.clear_cache(locale)  # Ensure fresh load
                    with measure_time() as get_time:
                        engine.file_manager.load_locale_file(locale, force_reload=True)
                    times.append(get_time())

                avg_time = statistics.mean(times)
                print(f"  {locale}: {avg_time:.4f}s")

        finally:
            engine.stop()


def benchmark_translation_lookup():
    """Benchmark translation key lookup performance."""
    print("Benchmarking translation lookup...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path, num_keys=10000)

        engine = LocalEngine(base_path=temp_path, auto_detect=False, default_locale="en-US")

        try:
            # Test simple key lookup
            simple_times = []
            for _ in range(1000):
                with measure_time() as get_time:
                    engine.get_text("key_100")
                simple_times.append(get_time())

            # Test nested key lookup
            nested_times = []
            for _ in range(1000):
                with measure_time() as get_time:
                    engine.get_text("nested.nested_key_100")
                nested_times.append(get_time())

            # Test missing key (with default)
            missing_times = []
            for _ in range(1000):
                with measure_time() as get_time:
                    engine.get_text("missing_key", default="default")
                missing_times.append(get_time())

            print(
                f"  Simple key lookup: "
                f"{statistics.mean(simple_times)*1000:.2f}ms ± "
                f"{statistics.stdev(simple_times)*1000:.2f}ms"
            )
            print(
                f"  Nested key lookup: "
                f"{statistics.mean(nested_times)*1000:.2f}ms ± "
                f"{statistics.stdev(nested_times)*1000:.2f}ms"
            )
            print(
                f"  Missing key (default): "
                f"{statistics.mean(missing_times)*1000:.2f}ms ± "
                f"{statistics.stdev(missing_times)*1000:.2f}ms"
            )

        finally:
            engine.stop()


def benchmark_locale_switching():
    """Benchmark locale switching performance."""
    print("Benchmarking locale switching...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path)

        engine = LocalEngine(base_path=temp_path, auto_detect=False, default_locale="en-US")

        try:
            # Pre-load all locales
            for locale in locales:
                engine.set_locale(locale)

            # Benchmark switching between cached locales
            cached_times = []
            for _ in range(100):
                target_locale = locales[_ % len(locales)]
                with measure_time() as get_time:
                    engine.set_locale(target_locale)
                cached_times.append(get_time())

            # Benchmark switching with cache clearing
            engine.clear_cache()
            fresh_times = []
            for _ in range(len(locales)):
                target_locale = locales[_ % len(locales)]
                with measure_time() as get_time:
                    engine.set_locale(target_locale)
                fresh_times.append(get_time())

            print(
                f"  Cached locale switch: "
                f"{statistics.mean(cached_times)*1000:.2f}ms ± "
                f"{statistics.stdev(cached_times)*1000:.2f}ms"
            )
            print(
                f"  Fresh locale switch: "
                f"{statistics.mean(fresh_times)*1000:.2f}ms ± "
                f"{statistics.stdev(fresh_times)*1000:.2f}ms"
            )

        finally:
            engine.stop()


def benchmark_cache_performance():
    """Benchmark caching effectiveness."""
    print("Benchmarking cache performance...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path, num_keys=5000)

        # Test with caching enabled
        engine_cached = LocalEngine(
            base_path=temp_path, auto_detect=False, default_locale="en-US", cache_timeout=300
        )

        # Test without caching
        engine_uncached = LocalEngine(
            base_path=temp_path, auto_detect=False, default_locale="en-US", cache_timeout=0
        )

        try:
            # Benchmark cached access
            engine_cached.get_text("key_0")  # Prime cache
            cached_times = []
            for _ in range(1000):
                with measure_time() as get_time:
                    engine_cached.get_text("key_100")
                cached_times.append(get_time())

            # Benchmark uncached access
            uncached_times = []
            for _ in range(100):  # Fewer iterations due to slower performance
                engine_uncached.clear_cache()
                with measure_time() as get_time:
                    engine_uncached.get_text("key_100")
                uncached_times.append(get_time())

            cached_avg = statistics.mean(cached_times) * 1000
            uncached_avg = statistics.mean(uncached_times) * 1000
            speedup = uncached_avg / cached_avg

            print(f"  Cached access: {cached_avg:.2f}ms")
            print(f"  Uncached access: {uncached_avg:.2f}ms")
            print(f"  Cache speedup: {speedup:.1f}x")

        finally:
            engine_cached.stop()
            engine_uncached.stop()


def benchmark_concurrent_access():
    """Benchmark thread safety and concurrent access."""
    print("Benchmarking concurrent access...")

    import concurrent.futures
    import threading

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        locales = create_test_locale_files(temp_path)

        engine = LocalEngine(base_path=temp_path, auto_detect=False, default_locale="en-US")

        def worker_task(worker_id):
            """Worker function for concurrent testing."""
            times = []
            for i in range(100):
                locale = locales[i % len(locales)]
                with measure_time() as get_time:
                    engine.set_locale(locale)
                    text = engine.get_text("key_0", default="default")
                times.append(get_time())
            return times

        try:
            # Test with different numbers of threads
            for num_threads in [1, 2, 4, 8]:
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    with measure_time() as get_total_time:
                        futures = [executor.submit(worker_task, i) for i in range(num_threads)]
                        results = [future.result() for future in futures]

                    total_time = get_total_time()
                    all_times = [time for worker_times in results for time in worker_times]
                    avg_time = statistics.mean(all_times) * 1000

                    print(
                        f"  {num_threads} threads: {total_time:.2f}s total, "
                        f"{avg_time:.2f}ms avg per operation"
                    )

        finally:
            engine.stop()


def main():
    """Run all benchmarks."""
    print("pyLocalEngine Performance Benchmarks")
    print("=" * 50)

    # Run individual benchmarks
    benchmark_engine_creation()
    print()

    benchmark_locale_loading()
    print()

    benchmark_translation_lookup()
    print()

    benchmark_locale_switching()
    print()

    benchmark_cache_performance()
    print()

    benchmark_concurrent_access()
    print()

    print("=" * 50)
    print("Benchmark suite completed!")


if __name__ == "__main__":
    main()
