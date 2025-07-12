#!/usr/bin/env python3
"""
LLM Cache Utilities
==================

Provides caching mechanisms to reduce OpenAI API usage during development.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from functools import wraps

# Cache configuration
CACHE_PATH = Path("mock_data/llm_cache.jsonl")
MOCK_DATA_PATH = Path("mock_data")

# Ensure mock data directory exists
MOCK_DATA_PATH.mkdir(exist_ok=True)


def use_llm_cache(func: Callable) -> Callable:
    """
    Decorator to cache LLM function calls.
    
    Args:
        func: Function that makes LLM calls
        
    Returns:
        Wrapped function with caching
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key from function name and arguments
        cache_key = hashlib.sha256(
            json.dumps((func.__name__, args, kwargs), sort_keys=True).encode()
        ).hexdigest()
        
        # Check cache for existing response
        if CACHE_PATH.exists():
            with open(CACHE_PATH, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("key") == cache_key:
                            print(f"🎯 Cache hit for {func.__name__}")
                            return entry["response"]
                    except json.JSONDecodeError:
                        continue
        
        # Call original function
        print(f"🔄 Cache miss for {func.__name__}, calling API...")
        response = func(*args, **kwargs)
        
        # Cache the response
        cache_entry = {
            "key": cache_key,
            "function": func.__name__,
            "response": response,
            "timestamp": str(Path().stat().st_mtime)
        }
        
        with open(CACHE_PATH, "a") as f:
            f.write(json.dumps(cache_entry) + "\n")
        
        print(f"💾 Cached response for {func.__name__}")
        return response
    
    return wrapper


def clear_llm_cache() -> None:
    """Clear the LLM cache."""
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
        print("🗑️ LLM cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    if not CACHE_PATH.exists():
        return {"total_entries": 0, "cache_size": 0}
    
    entries = []
    with open(CACHE_PATH, "r") as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    return {
        "total_entries": len(entries),
        "cache_size": CACHE_PATH.stat().st_size,
        "functions": list(set(entry.get("function", "unknown") for entry in entries))
    }


def log_llm_io(prompt: str, response: str, filename: str = "debug_llm_io.jsonl") -> None:
    """
    Log LLM input/output for debugging.
    
    Args:
        prompt: The prompt sent to the LLM
        response: The response from the LLM
        filename: Log file name
    """
    log_path = MOCK_DATA_PATH / filename
    
    log_entry = {
        "prompt": prompt,
        "response": response,
        "timestamp": str(Path().stat().st_mtime)
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def create_mock_response(response_type: str) -> Dict[str, Any]:
    """
    Create mock responses for development.
    
    Args:
        response_type: Type of mock response to create
        
    Returns:
        Mock response dictionary
    """
    mock_responses = {
        "gap_analysis": {
            "digital accessibility expertise": {"status": "❌", "recommendation": "Missing - not mentioned in cover letter"},
            "accessibility compliance knowledge": {"status": "❌", "recommendation": "Missing - not mentioned in cover letter"},
            "accessibility community engagement": {"status": "❌", "recommendation": "Missing - only general customer discovery mentioned"},
            "accessibility testing tools": {"status": "❌", "recommendation": "Missing - not mentioned in cover letter"},
            "AudioEye-specific market understanding": {"status": "❌", "recommendation": "Missing - only general PM experience mentioned"}
        },
        "requirements_extraction": {
            "domain_knowledge": ["digital accessibility expertise", "accessibility compliance knowledge"],
            "team_dynamics": ["accessibility community engagement"],
            "tools": ["accessibility testing tools"],
            "responsibilities": ["AudioEye-specific market understanding"]
        },
        "enhancement": {
            "enhanced_draft": "Enhanced cover letter content...",
            "confidence_score": 0.85,
            "changes_made": ["Improved tone", "Added metrics"],
            "analysis_summary": "Enhanced for better impact"
        }
    }
    
    return mock_responses.get(response_type, {}) 