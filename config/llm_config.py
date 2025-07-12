#!/usr/bin/env python3
"""
LLM Configuration for API Usage Optimization
==========================================

Configuration settings to optimize OpenAI API usage and reduce costs.
"""

import os
from typing import Dict, Any


# Environment-based configuration
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
ENHANCE_TOGGLE = os.getenv("ENHANCE", "true").lower() == "true"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
ENHANCEMENT_MODEL = os.getenv("ENHANCEMENT_MODEL", "gpt-4o-mini")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"


def get_llm_config() -> Dict[str, Any]:
    """
    Get LLM configuration settings.
    
    Returns:
        Dictionary with LLM configuration
    """
    return {
        "use_mock": USE_MOCK,
        "enhance_toggle": ENHANCE_TOGGLE,
        "default_model": DEFAULT_MODEL,
        "enhancement_model": ENHANCEMENT_MODEL,
        "cache_enabled": CACHE_ENABLED,
        "temperature": {
            "draft": 0.3,
            "enhancement": 0.2,
            "gap_analysis": 0.0
        },
        "max_tokens": {
            "draft": 1000,
            "enhancement": 1500,
            "gap_analysis": 500
        }
    }


def should_use_mock() -> bool:
    """Check if mock mode is enabled."""
    return USE_MOCK


def should_enhance() -> bool:
    """Check if enhancement is enabled."""
    return ENHANCE_TOGGLE


def get_model_for_task(task: str) -> str:
    """
    Get appropriate model for task.
    
    Args:
        task: Task type (draft, enhancement, gap_analysis)
        
    Returns:
        Model name to use
    """
    if task == "enhancement":
        return ENHANCEMENT_MODEL
    else:
        return DEFAULT_MODEL


def get_temperature_for_task(task: str) -> float:
    """
    Get appropriate temperature for task.
    
    Args:
        task: Task type
        
    Returns:
        Temperature value
    """
    config = get_llm_config()
    return config["temperature"].get(task, 0.3)


def get_max_tokens_for_task(task: str) -> int:
    """
    Get appropriate max tokens for task.
    
    Args:
        task: Task type
        
    Returns:
        Max tokens value
    """
    config = get_llm_config()
    return config["max_tokens"].get(task, 1000)


def strip_job_description(jd_text: str) -> str:
    """
    Strip job description to reduce token usage.
    
    Args:
        jd_text: Original job description
        
    Returns:
        Stripped job description
    """
    lines = jd_text.split("\n")
    stripped_lines = []
    
    # Keep essential parts, remove boilerplate
    for line in lines:
        line = line.strip()
        
        # Skip common boilerplate
        if any(skip in line.lower() for skip in [
            "equal opportunity employer",
            "diversity and inclusion",
            "benefits package",
            "health insurance",
            "dental insurance",
            "vision insurance",
            "401k",
            "paid time off",
            "remote work",
            "competitive salary",
            "salary range",
            "bonus",
            "equity",
            "stock options",
            "perks",
            "free lunch",
            "gym membership",
            "commuter benefits"
        ]):
            continue
            
        # Skip empty lines and repetitive sections
        if not line or line.startswith("---") or line.startswith("=="):
            continue
            
        stripped_lines.append(line)
    
    return "\n".join(stripped_lines)


def estimate_token_cost(text: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """
    Estimate token cost for text.
    
    Args:
        text: Text to estimate
        model: Model to use for estimation
        
    Returns:
        Dictionary with cost estimates
    """
    # Rough estimation: 1 token ≈ 4 characters for English text
    estimated_tokens = len(text) // 4
    
    # Cost per 1K tokens (approximate)
    costs = {
        "gpt-3.5-turbo": 0.0015,  # $0.0015 per 1K tokens
        "gpt-4o-mini": 0.00015,   # $0.00015 per 1K tokens
        "gpt-4": 0.03,            # $0.03 per 1K tokens
    }
    
    cost_per_1k = costs.get(model, 0.0015)
    estimated_cost = (estimated_tokens / 1000) * cost_per_1k
    
    return {
        "estimated_tokens": estimated_tokens,
        "estimated_cost_usd": estimated_cost,
        "model": model
    } 