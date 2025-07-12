#!/usr/bin/env python3
"""
Contextual LLM Enhancement for Cover Letters
============================================

Enhances cover letter quality using OpenAI LLM post-blurb assembly to:
- Detect weaknesses
- Elevate storytelling
- Refine tone and structure
- Preserve user-authored content unless explicitly rewritten
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

logger = logging.getLogger(__name__)


@dataclass
class EnhancementResult:
    """Result of LLM enhancement process."""

    enhanced_draft: str
    original_draft: str
    changes_made: List[str]
    confidence_score: float
    analysis_summary: str
    metadata_used: Dict


def enhance_with_contextual_llm(
    jd_text: str, cl_text: str, metadata: Dict, model: str = "gpt-4o-mini", temperature: float = 0.3
) -> EnhancementResult:
    """
    Enhance cover letter using contextual LLM analysis.

    Args:
        jd_text: Job description text
        cl_text: Cover letter draft text
        metadata: Dict with case study tags, scoring, role alignment, etc.
        model: OpenAI model to use
        temperature: Creativity level (0.0-1.0)

    Returns:
        EnhancementResult with improved draft and analysis
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI not available for enhancement")
        return EnhancementResult(
            enhanced_draft=cl_text,
            original_draft=cl_text,
            changes_made=[],
            confidence_score=0.0,
            analysis_summary="OpenAI not available",
            metadata_used=metadata,
        )

    try:
        # Get prompt preferences
        from config.prompt_prefs import get_llm_prompt_preferences

        prompt_prefs = get_llm_prompt_preferences()

        # Build system prompt
        system_prompt = _build_system_prompt(prompt_prefs, metadata)

        # Build user message
        user_message = _build_user_message(jd_text, cl_text, metadata)

        # Call OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=temperature,
            max_tokens=2000,
        )

        enhanced_content = response.choices[0].message.content

        # Parse response and extract analysis
        enhanced_draft, analysis = _parse_enhancement_response(enhanced_content)

        # Generate changes summary
        changes_made = _analyze_changes(cl_text, enhanced_draft)

        # Calculate confidence score based on response quality
        confidence_score = _calculate_confidence_score(enhanced_draft, analysis)

        return EnhancementResult(
            enhanced_draft=enhanced_draft,
            original_draft=cl_text,
            changes_made=changes_made,
            confidence_score=confidence_score,
            analysis_summary=analysis,
            metadata_used=metadata,
        )

    except Exception as e:
        logger.error(f"Error in LLM enhancement: {e}")
        return EnhancementResult(
            enhanced_draft=cl_text,
            original_draft=cl_text,
            changes_made=[],
            confidence_score=0.0,
            analysis_summary=f"Enhancement failed: {str(e)}",
            metadata_used=metadata,
        )


def _build_system_prompt(preferences: Dict, metadata: Dict) -> str:
    """Build structured system prompt with preferences and metadata."""

    # Extract key metadata
    case_study_tags = metadata.get("case_study_tags", [])
    role_alignment = metadata.get("role_alignment", "")
    job_score = metadata.get("job_score", 0.0)

    # Build tag-specific instructions
    tag_instructions = ""
    if "ai_ml" in case_study_tags:
        tag_instructions += "\n- Emphasize AI/ML experience and technical depth"
    if "trust" in case_study_tags:
        tag_instructions += "\n- Highlight trust-building and explainable AI experience"
    if "growth" in case_study_tags:
        tag_instructions += "\n- Focus on growth metrics and scaling experience"
    if "founding_pm" in case_study_tags:
        tag_instructions += "\n- Emphasize 0-to-1 experience and startup mindset"

    return f"""You are an expert cover letter editor specializing in product management roles.

STYLE PREFERENCES:
{preferences.get('style', 'Direct, data-driven, high-impact')}

VOICE:
{preferences.get('voice', 'Confident and precise. No fluff.')}

ENHANCEMENT GOALS:
{chr(10).join(f"- {goal}" for goal in preferences.get('goals', []))}

CONTEXT:
- Job Score: {job_score:.1f}
- Role Alignment: {role_alignment}
- Case Study Focus: {', '.join(case_study_tags) if case_study_tags else 'None'}

TAG-SPECIFIC INSTRUCTIONS:
{tag_instructions}

CRITICAL RULES:
1. Preserve all factual claims, metrics, and achievements exactly as stated
2. Only improve clarity, flow, and strategic alignment
3. Maintain the original voice and tone
4. Focus on job description alignment
5. Avoid adding unverified claims or experiences
6. Respect user-authored content unless clearly problematic

Output format:
ENHANCED DRAFT:
[Your improved cover letter here]

ANALYSIS:
[Brief summary of key improvements made]
"""


def _build_user_message(jd_text: str, cl_text: str, metadata: Dict) -> str:
    """Build user message with job description and cover letter."""

    return f"""Please enhance this cover letter for better alignment with the job description.

JOB DESCRIPTION:
{jd_text}

COVER LETTER DRAFT:
{cl_text}

METADATA:
- Company: {metadata.get('company_name', 'Unknown')}
- Position: {metadata.get('position_title', 'Unknown')}
- Job Type: {metadata.get('job_type', 'Unknown')}
- Case Studies: {', '.join(metadata.get('case_study_tags', []))}

Please provide the enhanced draft and analysis as specified in the system prompt."""


def _parse_enhancement_response(response_content: str) -> Tuple[str, str]:
    """Parse LLM response to extract enhanced draft and analysis."""

    # Look for ENHANCED DRAFT section
    draft_start = response_content.find("ENHANCED DRAFT:")
    analysis_start = response_content.find("ANALYSIS:")

    if draft_start == -1:
        # Fallback: return entire content as draft
        return response_content.strip(), "No analysis provided"

    # Extract draft
    if analysis_start != -1:
        enhanced_draft = response_content[draft_start + len("ENHANCED DRAFT:") : analysis_start].strip()
        analysis = response_content[analysis_start + len("ANALYSIS:") :].strip()
    else:
        enhanced_draft = response_content[draft_start + len("ENHANCED DRAFT:") :].strip()
        analysis = "No analysis provided"

    return enhanced_draft, analysis


def _analyze_changes(original: str, enhanced: str) -> List[str]:
    """Analyze what changes were made between original and enhanced drafts."""
    changes = []

    # Simple word count comparison
    orig_words = len(original.split())
    enh_words = len(enhanced.split())

    if enh_words > orig_words * 1.2:
        changes.append("Significantly expanded content")
    elif enh_words < orig_words * 0.8:
        changes.append("Condensed and streamlined content")

    # Check for key improvements
    if "Dear" in enhanced and "Dear" in original:
        changes.append("Maintained professional greeting")

    if any(metric in enhanced for metric in ["%", "x", "$"]) and any(metric in original for metric in ["%", "x", "$"]):
        changes.append("Preserved key metrics and achievements")

    # Check for structure improvements
    if enhanced.count("\n\n") > original.count("\n\n"):
        changes.append("Improved paragraph structure")

    return changes


def _calculate_confidence_score(enhanced_draft: str, analysis: str) -> float:
    """Calculate confidence score based on enhancement quality."""
    score = 0.5  # Base score

    # Check for proper structure
    if "Dear" in enhanced_draft and "Best regards" in enhanced_draft:
        score += 0.2

    # Check for metrics preservation
    if any(metric in enhanced_draft for metric in ["%", "x", "$"]):
        score += 0.1

    # Check for analysis quality
    if len(analysis) > 50:
        score += 0.1

    # Check for appropriate length
    word_count = len(enhanced_draft.split())
    if 200 <= word_count <= 400:
        score += 0.1

    return min(score, 1.0)
