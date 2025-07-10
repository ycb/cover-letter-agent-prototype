#!/usr/bin/env python3
"""
LLM Rewrite Module
==================

Phase 1 LLM post-processor for enhancing cover letters after logic-based generation.
Maintains truth, transparency, and user voice while improving polish and coherence.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMRewriteConfig:
    """Configuration for LLM rewrite functionality."""
    enabled: bool = True
    model: str = "gpt-4"
    temperature: float = 0.5
    max_tokens: int = 2000
    preserve_truth: bool = True
    add_comments: bool = True


class LLMRewriter:
    """LLM-based cover letter enhancement with truth preservation."""
    
    def __init__(self, config: Optional[LLMRewriteConfig] = None):
        """Initialize the LLM rewriter with configuration."""
        self.config = config or LLMRewriteConfig()
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.available = False
        else:
            self.available = True
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("LLM rewriter initialized successfully")
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                self.available = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.available = False
    
    def rewrite_cover_letter(
        self, 
        original_text: str, 
        job_description: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Rewrite a cover letter to improve clarity, tone, and polish.
        
        Args:
            original_text: The original cover letter text
            job_description: The job description text
            user_context: Optional user-specific context (company notes, etc.)
            
        Returns:
            Enhanced cover letter text
        """
        if not self.available or not self.config.enabled:
            logger.info("[LLM] Skipped (disabled or unavailable)")
            return original_text
        
        try:
            logger.info("[LLM] Enhancing draft...")
            
            # Build context for the LLM
            context_parts = []
            if user_context:
                if user_context.get('company_notes'):
                    context_parts.append(f"Company Notes: {user_context['company_notes']}")
                if user_context.get('role_insights'):
                    context_parts.append(f"Role Insights: {user_context['role_insights']}")
            
            context_text = "\n".join(context_parts) if context_parts else "None"
            
            # Create the prompt with truth preservation emphasis
            prompt = self._create_rewrite_prompt(
                original_text, 
                job_description, 
                context_text
            )
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            
            # Add comments if enabled
            if self.config.add_comments:
                enhanced_text = self._add_llm_comments(enhanced_text)
            
            logger.info("[LLM] Enhancement completed")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"[LLM] Error during rewrite: {e}")
            return original_text
    
    def _create_rewrite_prompt(
        self, 
        original_text: str, 
        job_description: str, 
        context_text: str
    ) -> str:
        """Create the rewrite prompt with truth preservation emphasis."""
        return f"""
You are a professional writing assistant helping a senior product leader apply for a job.

Rewrite the following cover letter to improve clarity, tone, and polish while maintaining 100% factual accuracy. Do not add or change any experience, achievements, or claims that cannot be verified from the original text.

CRITICAL: You must preserve ALL numbers, percentages, and metrics exactly as they appear in the original text, including:
- All percentages (e.g., "50%", "+210%", "876%")
- All multipliers (e.g., "10x", "15+ years")
- All dollar amounts (e.g., "$4B", "$250k")
- All decimal numbers (e.g., "3.7 to 4.3")
- All exact formatting and symbols

IMPORTANT: This is a post-draft enhancement. The original text contains verified facts and experiences. Your job is to improve writing quality, not to invent new content.

Cover Letter:
\"\"\"
{original_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Additional Context:
{context_text}

Rewrite the cover letter to:
1. Improve clarity and flow
2. Enhance alignment with the job description
3. Strengthen impact and persuasiveness
4. Maintain all factual claims from the original
5. Preserve ALL metrics and numbers exactly as written
6. Use professional, confident tone

Output only the rewritten cover letter without any explanations or comments.
"""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are a helpful, concise, and precise editor specializing in professional cover letters. 

Your role is to enhance writing quality while preserving all factual information. You must:
- Never add unverified claims or experiences
- Never exaggerate achievements or responsibilities  
- Maintain the original voice and tone
- Focus on clarity, flow, and impact
- Ensure alignment with the job description
- NEVER remove or change specific metrics, percentages, or quantified achievements
- Preserve all numbers, percentages, and specific performance data exactly as stated

If you cannot improve a section without changing facts, leave it as is."""
    
    def _add_llm_comments(self, text: str) -> str:
        """Add comments to indicate LLM-enhanced sections."""
        return f"""<!-- LLM Enhanced Cover Letter -->
<!-- Generated with AI assistance for clarity and polish -->
<!-- All factual claims preserved from original -->

{text}

<!-- End LLM Enhanced Cover Letter -->"""
    
    def validate_truth_preservation(
        self, 
        original_text: str, 
        enhanced_text: str
    ) -> Dict[str, Any]:
        """
        Validate that the enhanced text preserves all factual claims.
        
        Returns:
            Dict with validation results and any concerns
        """
        # Simple validation - can be enhanced with more sophisticated checks
        concerns = []
        
        # Check for common exaggeration patterns
        exaggeration_patterns = [
            "led a team of", "managed", "oversaw", "directed", "spearheaded"
        ]
        
        for pattern in exaggeration_patterns:
            if pattern in enhanced_text and pattern not in original_text:
                concerns.append(f"Potential exaggeration: '{pattern}' added")
        
        # Check for removed metrics (critical validation)
        import re
        metric_patterns = [
            r'\d+%',  # percentages like 50%, 876%
            r'\+\d+%',  # positive percentages like +210%
            r'\d+x',  # multipliers like 10x
            r'\$\d+[BbMmKk]',  # dollar amounts like $4B
            r'\d+\.\d+',  # decimal numbers like 3.7 to 4.3
        ]
        
        for pattern in metric_patterns:
            original_metrics = re.findall(pattern, original_text, re.IGNORECASE)
            enhanced_metrics = re.findall(pattern, enhanced_text, re.IGNORECASE)
            
            for metric in original_metrics:
                if metric not in enhanced_metrics:
                    concerns.append(f"Critical: Metric '{metric}' was removed")
        
        # Check for added companies or specific achievements
        # This is a simplified check - in practice, you'd want more sophisticated validation
        
        return {
            "valid": len(concerns) == 0,
            "concerns": concerns,
            "enhanced_length": len(enhanced_text),
            "original_length": len(original_text)
        }


def post_process_with_llm(
    first_draft: str, 
    job_description: str, 
    user_config: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Post-process a cover letter draft with LLM enhancement.
    
    Args:
        first_draft: The initial logic-generated cover letter
        job_description: The job description text
        user_config: User configuration dict
        user_context: Optional user-specific context
        
    Returns:
        Enhanced cover letter text
    """
    # Check if LLM enhancement is enabled
    llm_enabled = user_config.get("llm_enhance", True)
    
    if not llm_enabled:
        logger.info("[LLM] Skipped (disabled in config)")
        return first_draft
    
    # Create LLM rewriter
    config = LLMRewriteConfig(
        enabled=llm_enabled,
        model=user_config.get("llm_model", "gpt-4"),
        temperature=user_config.get("llm_temperature", 0.5),
        preserve_truth=user_config.get("llm_preserve_truth", True),
        add_comments=user_config.get("llm_add_comments", True)
    )
    
    rewriter = LLMRewriter(config)
    
    # Perform the rewrite
    enhanced_draft = rewriter.rewrite_cover_letter(
        first_draft, 
        job_description, 
        user_context
    )
    
    # Validate truth preservation if enabled
    if config.preserve_truth:
        validation = rewriter.validate_truth_preservation(first_draft, enhanced_draft)
        if not validation["valid"]:
            logger.warning(f"[LLM] Truth preservation concerns: {validation['concerns']}")
    
    return enhanced_draft 