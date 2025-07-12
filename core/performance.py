#!/usr/bin/env python3
"""
Performance Optimization and Caching
===================================

Provides caching, memoization, and performance monitoring for the cover letter agent.
"""

import functools
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta

import yaml

from .exceptions import PerformanceError
from .logging_config import get_logger
from .types import ConfigDict

logger = get_logger(__name__)


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.start_times:
            logger.warning(f"Timer not started for operation: {operation}")
            return 0.0

        duration = time.time() - self.start_times[operation]
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)

        logger.debug(f"Operation '{operation}' took {duration:.3f}s")
        return duration

    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation."""
        if operation not in self.metrics:
            return 0.0
        return sum(self.metrics[operation]) / len(self.metrics[operation])

    def get_total_time(self, operation: str) -> float:
        """Get total time for an operation."""
        if operation not in self.metrics:
            return 0.0
        return sum(self.metrics[operation])

    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all performance metrics."""
        summary = {}
        for operation, times in self.metrics.items():
            summary[operation] = {
                "count": len(times),
                "total_time": sum(times),
                "average_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
            }
        return summary


class CacheManager:
    """Manages caching for expensive operations."""

    def __init__(self, cache_dir: Optional[Path] = None, max_size: int = 1000):
        """Initialize cache manager."""
        self.cache_dir = cache_dir or Path(".cache")
        self.max_size = max_size
        self.memory_cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.monitor = PerformanceMonitor()

        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)

    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create a hash of the arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else []
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def _is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self.cache_metadata:
            return False

        metadata = self.cache_metadata[cache_key]
        cache_time = datetime.fromisoformat(metadata["timestamp"])
        max_age = timedelta(hours=max_age_hours)

        return datetime.now() - cache_time < max_age

    def get(self, cache_key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get a value from cache."""
        self.monitor.start_timer("cache_get")

        # Check memory cache first
        if cache_key in self.memory_cache:
            if self._is_cache_valid(cache_key, max_age_hours):
                self.monitor.end_timer("cache_get")
                return self.memory_cache[cache_key]

        # Check file cache
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                
                if self._is_cache_valid(cache_key, max_age_hours):
                    # Load into memory cache
                    self.memory_cache[cache_key] = data["value"]
                    self.monitor.end_timer("cache_get")
                    return data["value"]
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {e}")

        self.monitor.end_timer("cache_get")
        return None

    def set(self, cache_key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set a value in cache."""
        self.monitor.start_timer("cache_set")

        # Store in memory cache
        self.memory_cache[cache_key] = value

        # Store metadata
        self.cache_metadata[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # Store in file cache
        cache_file = self._get_cache_file_path(cache_key)
        try:
            with open(cache_file, "w") as f:
                json.dump({
                    "value": value,
                    "metadata": self.cache_metadata[cache_key]
                }, f)
        except Exception as e:
            logger.warning(f"Error writing cache file {cache_file}: {e}")

        # Implement LRU eviction if cache is too large
        if len(self.memory_cache) > self.max_size:
            self._evict_oldest()

        self.monitor.end_timer("cache_set")

    def _evict_oldest(self) -> None:
        """Evict the oldest cache entries."""
        # Remove oldest entries from memory cache
        keys_to_remove = list(self.memory_cache.keys())[:len(self.memory_cache) // 4]
        for key in keys_to_remove:
            del self.memory_cache[key]
            if key in self.cache_metadata:
                del self.cache_metadata[key]

    def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries, optionally matching a pattern."""
        if pattern:
            # Clear matching entries
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
        else:
            # Clear all entries
            keys_to_remove = list(self.memory_cache.keys())

        for key in keys_to_remove:
            del self.memory_cache[key]
            if key in self.cache_metadata:
                del self.cache_metadata[key]

        logger.info(f"Cleared {len(keys_to_remove)} cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "memory_cache_size": len(self.memory_cache),
            "metadata_size": len(self.cache_metadata),
            "max_size": self.max_size,
            "performance_metrics": self.monitor.get_metrics_summary()
        }


def memoize(max_age_hours: int = 24, cache_key_prefix: str = ""):
    """Decorator for memoizing expensive function calls."""
    def decorator(func: Callable) -> Callable:
        cache_manager = CacheManager()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{cache_key_prefix}_{func.__name__}_{cache_manager._generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_manager.get(key, max_age_hours)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache_manager.set(key, result)
            return result

        return wrapper
    return decorator


class FileCache:
    """Specialized cache for file-based operations."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize file cache."""
        self.cache_manager = CacheManager(cache_dir)
        self.monitor = PerformanceMonitor()

    @memoize(max_age_hours=1, cache_key_prefix="yaml_load")
    def load_yaml_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load and cache YAML file content."""
        self.monitor.start_timer("yaml_load")
        
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if data is None:
                    data = {}
            
            self.monitor.end_timer("yaml_load")
            return data
        except Exception as e:
            self.monitor.end_timer("yaml_load")
            raise PerformanceError(f"Failed to load YAML file {file_path}: {e}")

    @memoize(max_age_hours=24, cache_key_prefix="job_parse")
    def parse_job_description(self, job_text: str) -> Dict[str, Any]:
        """Parse and cache job description analysis."""
        self.monitor.start_timer("job_parse")
        
        # This would contain the actual job parsing logic
        # For now, return a simple structure
        result = {
            "company_name": "",
            "job_title": "",
            "requirements": [],
            "score": 0.0,
            "parsed_at": datetime.now().isoformat()
        }
        
        self.monitor.end_timer("job_parse")
        return result

    @memoize(max_age_hours=12, cache_key_prefix="blurb_score")
    def score_blurb(self, blurb: Dict[str, Any], job_requirements: List[str]) -> float:
        """Score a blurb against job requirements."""
        self.monitor.start_timer("blurb_score")
        
        # Simple scoring logic
        score = 0.0
        blurb_text = blurb.get("text", "").lower()
        blurb_tags = [tag.lower() for tag in blurb.get("tags", [])]
        
        for requirement in job_requirements:
            req_lower = requirement.lower()
            if req_lower in blurb_text:
                score += 1.0
            if req_lower in blurb_tags:
                score += 0.5
        
        self.monitor.end_timer("blurb_score")
        return score


class LLMCache:
    """Specialized cache for LLM API calls."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize LLM cache."""
        self.cache_manager = CacheManager(cache_dir)
        self.monitor = PerformanceMonitor()

    @memoize(max_age_hours=168, cache_key_prefix="llm_enhance")  # 1 week cache
    def enhance_cover_letter(self, draft: str, job_description: str) -> str:
        """Cache LLM cover letter enhancement."""
        self.monitor.start_timer("llm_enhance")
        
        # This would contain the actual LLM enhancement logic
        # For now, return the draft as-is
        result = draft
        
        self.monitor.end_timer("llm_enhance")
        return result

    @memoize(max_age_hours=168, cache_key_prefix="llm_requirements")
    def extract_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Cache LLM requirement extraction."""
        self.monitor.start_timer("llm_requirements")
        
        # This would contain the actual LLM requirement extraction
        result = {
            "tools": [],
            "team_dynamics": [],
            "domain_knowledge": [],
            "soft_skills": [],
            "responsibilities": [],
            "outcomes": []
        }
        
        self.monitor.end_timer("llm_requirements")
        return result


# Global instances
performance_monitor = PerformanceMonitor()
file_cache = FileCache()
llm_cache = LLMCache()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor


def get_file_cache() -> FileCache:
    """Get the global file cache instance."""
    return file_cache


def get_llm_cache() -> LLMCache:
    """Get the global LLM cache instance."""
    return llm_cache 