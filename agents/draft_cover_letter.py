#!/usr/bin/env python3
"""
Draft Cover Letter Agent with LLM Enhancement
============================================

Integrates LLM enhancement into the post-blurb assembly workflow.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add features directory to path
import sys

sys.path.append(str(Path(__file__).parent.parent / "features"))

from features.enhance_with_contextual_llm import enhance_with_contextual_llm, EnhancementResult

logger = logging.getLogger(__name__)


class DraftCoverLetterAgent:
    """Agent for generating and enhancing cover letter drafts."""

    def __init__(self, user_id: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize the draft cover letter agent."""
        self.user_id = user_id
        self.config = config or {}
        self.llm_enhancement_enabled = self.config.get("llm_enhancement", {}).get("enabled", True)

    def generate_enhanced_cover_letter(
        self, job_description: str, assembled_draft: str, metadata: Dict, enable_llm_enhancement: Optional[bool] = None
    ) -> Tuple[str, EnhancementResult]:
        """
        Generate enhanced cover letter with optional LLM enhancement.

        Args:
            job_description: Job description text
            assembled_draft: Cover letter draft from blurb assembly
            metadata: Dict with case study tags, scoring, role alignment, etc.
            enable_llm_enhancement: Override for LLM enhancement (defaults to config)

        Returns:
            Tuple of (enhanced_draft, enhancement_result)
        """
        # Determine if LLM enhancement should be used
        should_enhance = enable_llm_enhancement if enable_llm_enhancement is not None else self.llm_enhancement_enabled

        if not should_enhance:
            logger.info("LLM enhancement disabled, returning original draft")
            return assembled_draft, EnhancementResult(
                enhanced_draft=assembled_draft,
                original_draft=assembled_draft,
                changes_made=[],
                confidence_score=1.0,
                analysis_summary="LLM enhancement disabled",
                metadata_used=metadata,
            )

        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OpenAI API key not found, returning original draft")
            return assembled_draft, EnhancementResult(
                enhanced_draft=assembled_draft,
                original_draft=assembled_draft,
                changes_made=[],
                confidence_score=0.0,
                analysis_summary="OpenAI API key not available",
                metadata_used=metadata,
            )

        try:
            logger.info("Starting LLM enhancement of cover letter draft")

            # Prepare metadata for enhancement
            enhancement_metadata = self._prepare_enhancement_metadata(metadata)

            # Call LLM enhancement
            enhancement_result = enhance_with_contextual_llm(
                jd_text=job_description, cl_text=assembled_draft, metadata=enhancement_metadata
            )

            logger.info(f"LLM enhancement completed with confidence: {enhancement_result.confidence_score:.2f}")

            return enhancement_result.enhanced_draft, enhancement_result

        except Exception as e:
            logger.error(f"Error in LLM enhancement: {e}")
            return assembled_draft, EnhancementResult(
                enhanced_draft=assembled_draft,
                original_draft=assembled_draft,
                changes_made=[],
                confidence_score=0.0,
                analysis_summary=f"Enhancement failed: {str(e)}",
                metadata_used=metadata,
            )

    def _prepare_enhancement_metadata(self, metadata: Dict) -> Dict:
        """Prepare metadata for LLM enhancement."""
        enhancement_metadata = {
            "company_name": metadata.get("company_name", "Unknown"),
            "position_title": metadata.get("position_title", "Unknown"),
            "job_type": metadata.get("job_type", "Unknown"),
            "job_score": metadata.get("job_score", 0.0),
            "case_study_tags": metadata.get("case_study_tags", []),
            "role_alignment": metadata.get("role_alignment", ""),
            "targeting_score": metadata.get("targeting_score", 0.0),
            "go_no_go": metadata.get("go_no_go", False),
        }

        # Add role-specific preferences
        role_type = self._determine_role_type(metadata)
        if role_type:
            enhancement_metadata["role_type"] = role_type

        # Add company-specific preferences
        company_type = self._determine_company_type(metadata)
        if company_type:
            enhancement_metadata["company_type"] = company_type

        return enhancement_metadata

    def _determine_role_type(self, metadata: Dict) -> Optional[str]:
        """Determine role type from metadata."""
        case_study_tags = metadata.get("case_study_tags", [])

        if "ai_ml" in case_study_tags:
            return "ai_ml"
        elif "growth" in case_study_tags:
            return "growth"
        elif "founding_pm" in case_study_tags:
            return "founding_pm"
        elif "enterprise" in metadata.get("job_type", "").lower():
            return "enterprise"

        return None

    def _determine_company_type(self, metadata: Dict) -> Optional[str]:
        """Determine company type from metadata."""
        job_type = metadata.get("job_type", "").lower()

        if "startup" in job_type:
            return "startup"
        elif "enterprise" in job_type:
            return "enterprise"
        elif "public" in job_type:
            return "public"

        return None

    def save_draft_comparison(
        self, original_draft: str, enhanced_draft: str, enhancement_result: EnhancementResult, output_dir: str = "drafts"
    ) -> str:
        """
        Save both original and enhanced drafts for comparison.

        Args:
            original_draft: Original cover letter draft
            enhanced_draft: Enhanced cover letter draft
            enhancement_result: Result from LLM enhancement
            output_dir: Directory to save drafts

        Returns:
            Path to saved comparison file
        """
        import datetime

        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        company = enhancement_result.metadata_used.get("company_name", "Unknown")
        filename = f"{company}_draft_comparison_{timestamp}.txt"
        filepath = Path(output_dir) / filename

        # Create comparison content
        comparison_content = f"""# Cover Letter Draft Comparison
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Company: {enhancement_result.metadata_used.get('company_name', 'Unknown')}
Position: {enhancement_result.metadata_used.get('position_title', 'Unknown')}
Confidence Score: {enhancement_result.confidence_score:.2f}

## ENHANCEMENT ANALYSIS
{enhancement_result.analysis_summary}

## CHANGES MADE
{chr(10).join(f"- {change}" for change in enhancement_result.changes_made)}

## ORIGINAL DRAFT
{original_draft}

## ENHANCED DRAFT
{enhanced_draft}

## METADATA USED
{json.dumps(enhancement_result.metadata_used, indent=2)}
"""

        # Save file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(comparison_content)

        logger.info(f"Saved draft comparison to: {filepath}")
        return str(filepath)
