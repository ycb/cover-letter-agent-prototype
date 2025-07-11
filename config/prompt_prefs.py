#!/usr/bin/env python3
"""
LLM Prompt Preferences for Cover Letter Enhancement
==================================================

Defines style, voice, and enhancement goals for LLM-powered cover letter improvement.
"""

from typing import Dict, List


def get_llm_prompt_preferences() -> Dict:
    """
    Get LLM prompt preferences for cover letter enhancement.
    
    Returns:
        Dict with style, voice, and enhancement goals
    """
    return {
        "style": "Direct, data-driven, high-impact",
        "voice": "Confident and precise. No fluff.",
        "goals": [
            "Preserve approved blurbs unless explicitly asked",
            "Clarify, simplify, and energize writing",
            "Fix logic gaps vs job description",
            "Ensure strategic alignment to role goals",
            "Avoid redundant phrasing",
            "Respect human edits unless clearly worse"
        ],
        "tone_guidelines": [
            "Professional but not corporate",
            "Confident without being arrogant",
            "Specific and measurable",
            "Story-driven with clear outcomes"
        ],
        "structural_preferences": [
            "Strong opening that hooks the reader",
            "Clear progression from experience to value",
            "Quantified achievements prominently featured",
            "Strategic closing that ties to company mission"
        ],
        "content_priorities": [
            "Job description alignment",
            "Relevant case study emphasis",
            "Metrics and quantifiable impact",
            "Cultural and mission fit"
        ]
    }


def get_role_specific_preferences(role_type: str) -> Dict:
    """
    Get role-specific prompt preferences.
    
    Args:
        role_type: Type of role (e.g., 'ai_ml', 'growth', 'founding_pm')
    
    Returns:
        Dict with role-specific preferences
    """
    base_prefs = get_llm_prompt_preferences()
    
    role_specific = {
        "ai_ml": {
            "style": "Technical yet accessible, innovation-focused",
            "voice": "Technical confidence with business acumen",
            "additional_goals": [
                "Emphasize technical depth and AI/ML experience",
                "Highlight trust-building in AI systems",
                "Show understanding of AI product challenges"
            ]
        },
        "growth": {
            "style": "Metrics-driven, scaling-focused, high-energy",
            "voice": "Results-oriented and ambitious",
            "additional_goals": [
                "Emphasize growth metrics and scaling experience",
                "Show understanding of growth challenges",
                "Highlight data-driven decision making"
            ]
        },
        "founding_pm": {
            "style": "Entrepreneurial, 0-to-1 focused, strategic",
            "voice": "Founder mindset with execution focus",
            "additional_goals": [
                "Emphasize 0-to-1 experience and startup mindset",
                "Show ability to wear multiple hats",
                "Highlight strategic thinking and resourcefulness"
            ]
        },
        "enterprise": {
            "style": "Structured, stakeholder-aware, process-oriented",
            "voice": "Professional and collaborative",
            "additional_goals": [
                "Emphasize cross-functional collaboration",
                "Show understanding of enterprise sales cycles",
                "Highlight stakeholder management skills"
            ]
        }
    }
    
    if role_type in role_specific:
        base_prefs.update(role_specific[role_type])
    
    return base_prefs


def get_company_specific_preferences(company_type: str) -> Dict:
    """
    Get company-specific prompt preferences.
    
    Args:
        company_type: Type of company (e.g., 'startup', 'enterprise', 'public')
    
    Returns:
        Dict with company-specific preferences
    """
    base_prefs = get_llm_prompt_preferences()
    
    company_specific = {
        "startup": {
            "style": "Agile, fast-paced, impact-focused",
            "voice": "Entrepreneurial and hands-on",
            "additional_goals": [
                "Emphasize agility and fast execution",
                "Show comfort with ambiguity and change",
                "Highlight impact on company trajectory"
            ]
        },
        "enterprise": {
            "style": "Structured, scalable, stakeholder-aware",
            "voice": "Professional and collaborative",
            "additional_goals": [
                "Emphasize process and stakeholder management",
                "Show understanding of enterprise complexity",
                "Highlight cross-functional collaboration"
            ]
        },
        "public": {
            "style": "Mature, stable, compliance-aware",
            "voice": "Professional and measured",
            "additional_goals": [
                "Emphasize stability and proven track record",
                "Show understanding of public company dynamics",
                "Highlight compliance and governance awareness"
            ]
        }
    }
    
    if company_type in company_specific:
        base_prefs.update(company_specific[company_type])
    
    return base_prefs 