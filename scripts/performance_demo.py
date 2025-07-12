#!/usr/bin/env python3
"""
Performance Optimization Demo
============================

Demonstrates the performance improvements from caching and optimization.
"""

import time
from pathlib import Path

from core.performance import get_file_cache, get_performance_monitor
from agents.cover_letter_agent import CoverLetterAgent


def demo_file_caching():
    """Demonstrate file caching performance improvements."""
    print("=== File Caching Demo ===")

    # Create a test YAML file
    test_data = {
        "name": "Test User",
        "config": {"setting1": "value1", "setting2": "value2", "nested": {"key": "value"}},
        "list": [1, 2, 3, 4, 5],
    }

    test_file = Path("test_config.yaml")
    with open(test_file, "w") as f:
        import yaml

        yaml.dump(test_data, f)

    try:
        file_cache = get_file_cache()

        # First load (cache miss)
        start_time = time.time()
        result1 = file_cache.load_yaml_file(test_file)
        first_load_time = time.time() - start_time

        # Second load (cache hit)
        start_time = time.time()
        result2 = file_cache.load_yaml_file(test_file)
        second_load_time = time.time() - start_time

        print(f"First load (cache miss): {first_load_time:.4f}s")
        print(f"Second load (cache hit): {second_load_time:.4f}s")
        print(f"Speed improvement: {first_load_time / second_load_time:.1f}x")
        print(f"Results match: {result1 == result2}")

    finally:
        # Clean up
        test_file.unlink(missing_ok=True)


def demo_job_parsing_performance():
    """Demonstrate job parsing performance improvements."""
    print("\n=== Job Parsing Performance Demo ===")

    # Create a sample job description
    job_text = """
    Senior Product Manager
    TechCorp Inc.
    
    We are looking for a Senior Product Manager to join our growth team. 
    You will be responsible for:
    - Leading product strategy for user acquisition and retention
    - Working with cross-functional teams including engineering, design, and data science
    - Driving A/B testing and experimentation
    - Analyzing user behavior and metrics
    - Collaborating with stakeholders to define product requirements
    
    Requirements:
    - 5+ years of product management experience
    - Experience with data-driven decision making
    - Strong analytical skills
    - Experience with growth and user acquisition
    - Knowledge of A/B testing and experimentation
    """

    # Initialize agent
    agent = CoverLetterAgent()

    # First parse (no caching)
    start_time = time.time()
    job1 = agent.parse_job_description(job_text)
    first_parse_time = time.time() - start_time

    # Second parse (with caching)
    start_time = time.time()
    job2 = agent.parse_job_description(job_text)
    second_parse_time = time.time() - start_time

    print(f"First parse: {first_parse_time:.4f}s")
    print(f"Second parse: {second_parse_time:.4f}s")
    print(f"Speed improvement: {first_parse_time / second_parse_time:.1f}x")
    print(f"Results match: {job1.company_name == job2.company_name}")


def demo_blurb_selection_performance():
    """Demonstrate blurb selection performance improvements."""
    print("\n=== Blurb Selection Performance Demo ===")

    # Create a sample job
    job_text = "Senior Product Manager at GrowthCorp focusing on user acquisition and A/B testing"
    agent = CoverLetterAgent()
    job = agent.parse_job_description(job_text)

    # First selection
    start_time = time.time()
    result1 = agent.select_blurbs(job)
    first_selection_time = time.time() - start_time

    # Second selection (with caching)
    start_time = time.time()
    result2 = agent.select_blurbs(job)
    second_selection_time = time.time() - start_time

    print(f"First selection: {first_selection_time:.4f}s")
    print(f"Second selection: {second_selection_time:.4f}s")
    print(f"Speed improvement: {first_selection_time / second_selection_time:.1f}x")
    print(f"Results match: {len(result1) == len(result2)}")


def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("\n=== Performance Monitoring Demo ===")

    monitor = get_performance_monitor()

    # Simulate various operations
    operations = [("yaml_loading", 0.01), ("job_parsing", 0.02), ("blurb_selection", 0.015), ("file_io", 0.005)]

    for operation, duration in operations:
        monitor.start_timer(operation)
        time.sleep(duration)
        monitor.end_timer(operation)

    # Get performance summary
    summary = monitor.get_metrics_summary()

    print("Performance Summary:")
    for operation, metrics in summary.items():
        print(f"  {operation}:")
        print(f"    Count: {metrics['count']}")
        print(f"    Average: {metrics['average_time']:.4f}s")
        print(f"    Total: {metrics['total_time']:.4f}s")
        print(f"    Min: {metrics['min_time']:.4f}s")
        print(f"    Max: {metrics['max_time']:.4f}s")


def demo_cache_statistics():
    """Demonstrate cache statistics."""
    print("\n=== Cache Statistics Demo ===")

    file_cache = get_file_cache()

    # Load some files to populate cache
    test_files = []
    for i in range(5):
        test_file = Path(f"test_file_{i}.yaml")
        test_data = {"id": i, "data": f"content_{i}"}

        with open(test_file, "w") as f:
            import yaml

            yaml.dump(test_data, f)

        test_files.append(test_file)
        file_cache.load_yaml_file(test_file)

    try:
        # Get cache statistics
        stats = file_cache.cache_manager.get_stats()

        print("Cache Statistics:")
        print(f"  Memory cache size: {stats['memory_cache_size']}")
        print(f"  Metadata size: {stats['metadata_size']}")
        print(f"  Max size: {stats['max_size']}")

        print("\nPerformance Metrics:")
        for operation, metrics in stats["performance_metrics"].items():
            print(f"  {operation}: {metrics['count']} calls, {metrics['total_time']:.4f}s total")

    finally:
        # Clean up
        for test_file in test_files:
            test_file.unlink(missing_ok=True)


def main():
    """Run all performance demos."""
    print("Performance Optimization Demo")
    print("=" * 40)

    try:
        demo_file_caching()
        demo_job_parsing_performance()
        demo_blurb_selection_performance()
        demo_performance_monitoring()
        demo_cache_statistics()

        print("\n=== Demo Complete ===")
        print("The performance optimization system provides:")
        print("- File I/O caching for faster repeated loads")
        print("- Job parsing caching for identical job descriptions")
        print("- Blurb selection optimization")
        print("- Comprehensive performance monitoring")
        print("- Cache statistics and management")

    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
