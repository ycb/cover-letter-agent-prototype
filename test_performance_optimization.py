#!/usr/bin/env python3
"""
Test Performance Optimization and Caching
========================================

Tests the performance optimization system including caching, memoization,
and performance monitoring.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from core.performance import (
    CacheManager,
    FileCache,
    LLMCache,
    PerformanceMonitor,
    get_file_cache,
    get_llm_cache,
    get_performance_monitor,
    memoize,
)
from core.exceptions import PerformanceError


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""

    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        monitor = PerformanceMonitor()
        assert monitor.metrics == {}
        assert monitor.start_times == {}

    def test_timer_functionality(self):
        """Test timer start and end functionality."""
        monitor = PerformanceMonitor()

        # Start timer
        monitor.start_timer("test_operation")
        time.sleep(0.1)  # Simulate work
        duration = monitor.end_timer("test_operation")

        assert duration > 0.1
        assert "test_operation" in monitor.metrics
        assert len(monitor.metrics["test_operation"]) == 1

    def test_multiple_timings(self):
        """Test multiple timing operations."""
        monitor = PerformanceMonitor()

        for i in range(3):
            monitor.start_timer("repeated_operation")
            time.sleep(0.01)
            monitor.end_timer("repeated_operation")

        assert len(monitor.metrics["repeated_operation"]) == 3
        assert monitor.get_average_time("repeated_operation") > 0.01

    def test_metrics_summary(self):
        """Test metrics summary generation."""
        monitor = PerformanceMonitor()

        monitor.start_timer("operation1")
        time.sleep(0.01)
        monitor.end_timer("operation1")

        monitor.start_timer("operation2")
        time.sleep(0.02)
        monitor.end_timer("operation2")

        summary = monitor.get_metrics_summary()

        assert "operation1" in summary
        assert "operation2" in summary
        assert summary["operation1"]["count"] == 1
        assert summary["operation2"]["count"] == 1
        assert summary["operation1"]["total_time"] > 0.01
        assert summary["operation2"]["total_time"] > 0.02

    def test_end_timer_without_start(self):
        """Test ending timer without starting it."""
        monitor = PerformanceMonitor()
        duration = monitor.end_timer("nonexistent_operation")
        assert duration == 0.0


class TestCacheManager:
    """Test cache management functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_initialization(self):
        """Test cache manager initialization."""
        assert self.cache_manager.memory_cache == {}
        assert self.cache_manager.cache_metadata == {}
        assert self.cache_manager.max_size == 1000

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        test_data = {"key": "value", "number": 42}

        # Set cache
        self.cache_manager.set("test_key", test_data)

        # Get cache
        result = self.cache_manager.get("test_key")
        assert result == test_data

    def test_cache_with_metadata(self):
        """Test cache with metadata."""
        test_data = {"key": "value"}
        metadata = {"source": "test", "version": "1.0"}

        self.cache_manager.set("test_key", test_data, metadata)
        result = self.cache_manager.get("test_key")

        assert result == test_data
        assert "test_key" in self.cache_manager.cache_metadata

    def test_cache_expiration(self):
        """Test cache expiration functionality."""
        test_data = {"key": "value"}

        # Set cache with short expiration
        self.cache_manager.set("test_key", test_data)

        # Should be valid immediately
        result = self.cache_manager.get("test_key", max_age_hours=1)
        assert result == test_data

        # Should be invalid with very short expiration
        result = self.cache_manager.get("test_key", max_age_hours=0)
        assert result is None

    def test_cache_eviction(self):
        """Test cache eviction when size limit is exceeded."""
        # Create a small cache
        small_cache = CacheManager(Path(self.temp_dir), max_size=5)

        # Add more items than the limit
        for i in range(10):
            small_cache.set(f"key_{i}", f"value_{i}")

        # Should have evicted some items
        assert len(small_cache.memory_cache) < 10

    def test_cache_clear(self):
        """Test cache clearing functionality."""
        # Add some cache entries
        for i in range(5):
            self.cache_manager.set(f"key_{i}", f"value_{i}")

        # Clear all cache
        self.cache_manager.clear()
        assert len(self.cache_manager.memory_cache) == 0
        assert len(self.cache_manager.cache_metadata) == 0

    def test_cache_clear_with_pattern(self):
        """Test cache clearing with pattern matching."""
        # Add cache entries with different patterns
        self.cache_manager.set("test_key_1", "value1")
        self.cache_manager.set("other_key", "value2")
        self.cache_manager.set("test_key_2", "value3")

        # Clear only test keys
        self.cache_manager.clear(pattern="test_key")

        # Should only have other_key remaining
        assert "other_key" in self.cache_manager.memory_cache
        assert "test_key_1" not in self.cache_manager.memory_cache
        assert "test_key_2" not in self.cache_manager.memory_cache

    def test_cache_stats(self):
        """Test cache statistics generation."""
        # Add some cache entries
        for i in range(3):
            self.cache_manager.set(f"key_{i}", f"value_{i}")

        stats = self.cache_manager.get_stats()

        assert stats["memory_cache_size"] == 3
        assert stats["metadata_size"] == 3
        assert stats["max_size"] == 1000
        assert "performance_metrics" in stats


class TestFileCache:
    """Test file caching functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.file_cache = FileCache(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_yaml_file_loading(self):
        """Test YAML file loading with caching."""
        # Create a test YAML file
        test_data = {"key": "value", "list": [1, 2, 3]}
        yaml_file = Path(self.temp_dir) / "test.yaml"

        with open(yaml_file, "w") as f:
            yaml.dump(test_data, f)

        # Load the file
        result = self.file_cache.load_yaml_file(yaml_file)
        assert result == test_data

        # Load again (should be cached)
        result2 = self.file_cache.load_yaml_file(yaml_file)
        assert result2 == test_data

    def test_yaml_file_loading_error(self):
        """Test YAML file loading error handling."""
        # Try to load non-existent file
        non_existent_file = Path(self.temp_dir) / "nonexistent.yaml"

        with pytest.raises(PerformanceError):
            self.file_cache.load_yaml_file(non_existent_file)

    def test_job_parsing_caching(self):
        """Test job description parsing caching."""
        job_text = "Senior Product Manager at TechCorp"

        # Parse job description
        result1 = self.file_cache.parse_job_description(job_text)
        assert isinstance(result1, dict)
        assert "company_name" in result1
        assert "job_title" in result1

        # Parse again (should be cached)
        result2 = self.file_cache.parse_job_description(job_text)
        assert result2 == result1

    def test_blurb_scoring_caching(self):
        """Test blurb scoring caching."""
        blurb = {"id": "test", "text": "test text", "tags": ["test"]}
        job_requirements = ["test", "product", "management"]

        # Score blurb
        score1 = self.file_cache.score_blurb(blurb, job_requirements)
        assert isinstance(score1, float)

        # Score again (should be cached)
        score2 = self.file_cache.score_blurb(blurb, job_requirements)
        assert score2 == score1


class TestLLMCache:
    """Test LLM caching functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.llm_cache = LLMCache(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_llm_enhancement_caching(self):
        """Test LLM enhancement caching."""
        draft = "I am excited to apply for this position."
        job_description = "Senior Product Manager role"

        # Enhance cover letter
        result1 = self.llm_cache.enhance_cover_letter(draft, job_description)
        assert isinstance(result1, str)

        # Enhance again (should be cached)
        result2 = self.llm_cache.enhance_cover_letter(draft, job_description)
        assert result2 == result1

    def test_llm_requirements_extraction_caching(self):
        """Test LLM requirements extraction caching."""
        job_description = "Senior Product Manager role with AI/ML focus"

        # Extract requirements
        result1 = self.llm_cache.extract_requirements(job_description)
        assert isinstance(result1, dict)
        assert "tools" in result1
        assert "team_dynamics" in result1

        # Extract again (should be cached)
        result2 = self.llm_cache.extract_requirements(job_description)
        assert result2 == result1


class TestMemoizeDecorator:
    """Test memoization decorator functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_memoize_decorator(self):
        """Test memoization decorator."""
        call_count = 0

        @memoize(max_age_hours=1, cache_key_prefix="test")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call with same arguments (should be cached)
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not have been called again

        # Third call with different arguments
        result3 = expensive_function(3, 4)
        assert result3 == 7
        assert call_count == 2  # Should have been called again


class TestGlobalInstances:
    """Test global performance instances."""

    def test_global_instances(self):
        """Test global performance instances."""
        # Test performance monitor
        monitor = get_performance_monitor()
        assert isinstance(monitor, PerformanceMonitor)

        # Test file cache
        file_cache = get_file_cache()
        assert isinstance(file_cache, FileCache)

        # Test LLM cache
        llm_cache = get_llm_cache()
        assert isinstance(llm_cache, LLMCache)

    def test_global_instances_singleton(self):
        """Test that global instances are singletons."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        assert monitor1 is monitor2

        file_cache1 = get_file_cache()
        file_cache2 = get_file_cache()
        assert file_cache1 is file_cache2

        llm_cache1 = get_llm_cache()
        llm_cache2 = get_llm_cache()
        assert llm_cache1 is llm_cache2


class TestPerformanceIntegration:
    """Test performance optimization integration with existing code."""

    def test_file_cache_integration(self):
        """Test file cache integration with YAML loading."""
        # Create test YAML file
        test_data = {"test": "data", "nested": {"key": "value"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            yaml_file = Path(f.name)

        try:
            # Load using file cache
            file_cache = get_file_cache()
            result = file_cache.load_yaml_file(yaml_file)

            assert result == test_data

            # Load again (should be cached)
            result2 = file_cache.load_yaml_file(yaml_file)
            assert result2 == test_data

        finally:
            # Clean up
            yaml_file.unlink()

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        monitor = get_performance_monitor()

        # Simulate some operations
        monitor.start_timer("test_operation")
        time.sleep(0.01)
        monitor.end_timer("test_operation")

        # Check metrics
        summary = monitor.get_metrics_summary()
        assert "test_operation" in summary
        assert summary["test_operation"]["count"] == 1
        assert summary["test_operation"]["total_time"] > 0.01


if __name__ == "__main__":
    pytest.main([__file__])
