#!/usr/bin/env python3
"""
Hybrid Case Study Selection Module
==================================

Implements two-stage case study selection:
1. Fast tag-based filtering for pre-selection
2. LLM semantic scoring for top candidates only

This provides the benefits of LLM intelligence while controlling costs and speed.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class CaseStudyScore:
    """Represents a scored case study with explanation."""
    case_study: Dict[str, Any]
    score: float
    confidence: float
    reasoning: str
    stage1_score: int
    level_bonus: float = 0.0
    industry_bonus: float = 0.0


@dataclass
class HybridSelectionResult:
    """Represents the result of hybrid case study selection."""
    selected_case_studies: List[Dict[str, Any]]
    ranked_candidates: List[CaseStudyScore]
    stage1_candidates: int
    stage2_scored: int
    llm_cost_estimate: float
    total_time: float
    stage1_time: float
    stage2_time: float
    fallback_used: bool = False
    confidence_threshold: float = 1.0  # Lower threshold for rule of three


class HybridCaseStudySelector:
    """Hybrid case study selector with tag filtering + LLM semantic scoring."""
    
    def __init__(self, llm_enabled: bool = True, max_llm_candidates: int = 10):
        """Initialize the hybrid selector."""
        self.llm_enabled = llm_enabled
        self.max_llm_candidates = max_llm_candidates
        self.llm_cost_per_call = 0.01  # Estimated cost per LLM call
        
    def select_case_studies(
        self, 
        case_studies: List[Dict[str, Any]], 
        job_keywords: List[str], 
        job_level: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> HybridSelectionResult:
        """Select case studies using hybrid approach."""
        start_time = time.time()
        
        # Stage 1: Fast tag-based filtering
        stage1_start = time.time()
        candidates = self._stage1_tag_filtering(case_studies, job_keywords)
        stage1_time = time.time() - stage1_start
        
        logger.info(f"Stage 1: {len(candidates)} candidates from {len(case_studies)} case studies")
        
        # Stage 2: LLM semantic scoring (if enabled and candidates available)
        stage2_start = time.time()
        if self.llm_enabled and candidates and len(candidates) > 1:
            try:
                selected, ranked_scores = self._stage2_llm_scoring(
                    candidates[:self.max_llm_candidates], 
                    job_keywords, 
                    job_level, 
                    job_description
                )
                fallback_used = False
            except Exception as e:
                logger.warning(f"LLM scoring failed, using fallback: {e}")
                selected = self._fallback_selection(candidates)
                fallback_used = True
        else:
            # Use fallback if LLM disabled or insufficient candidates
            selected = self._fallback_selection(candidates)
            fallback_used = True
        
        stage2_time = time.time() - stage2_start
        total_time = time.time() - start_time
        
        # Estimate LLM cost
        llm_cost = self._estimate_llm_cost(len(candidates[:self.max_llm_candidates]))
        
        return HybridSelectionResult(
            selected_case_studies=selected,
            ranked_candidates=ranked_scores, # Placeholder, will be populated by _stage2_llm_scoring
            stage1_candidates=len(candidates),
            stage2_scored=min(len(candidates), self.max_llm_candidates),
            llm_cost_estimate=llm_cost,
            total_time=total_time,
            stage1_time=stage1_time,
            stage2_time=stage2_time,
            fallback_used=fallback_used
        )
    
    def _stage1_tag_filtering(
        self, 
        case_studies: List[Dict[str, Any]], 
        job_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Stage 1: Fast tag-based filtering."""
        candidates = []
        job_kw_set = set([kw.lower() for kw in job_keywords])
        
        for case_study in case_studies:
            case_study_tags = case_study.get('tags', [])
            case_study_tags_lower = [tag.lower() for tag in case_study_tags]
            
            # Calculate tag match score
            tag_matches = sum(1 for kw in job_kw_set if any(kw in tag for tag in case_study_tags_lower))
            
            # Include if there are any tag matches
            if tag_matches > 0:
                case_study['stage1_score'] = tag_matches
                candidates.append(case_study)
        
        # Sort by stage1 score (descending)
        candidates.sort(key=lambda x: x.get('stage1_score', 0), reverse=True)
        
        return candidates
    
    def _stage2_llm_scoring(
        self, 
        candidates: List[Dict[str, Any]], 
        job_keywords: List[str], 
        job_level: Optional[str], 
        job_description: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], List[CaseStudyScore]]:
        """Stage 2: LLM semantic scoring for top candidates with explanations."""
        if not candidates:
            return [], []
        
        # Create semantic scoring prompt
        prompt = self._create_semantic_scoring_prompt(
            candidates, job_keywords, job_level, job_description
        )
        
        # TODO: Implement actual LLM call
        # For now, simulate LLM scoring with enhanced tag matching
        scored_candidates, ranked_scores = self._simulate_llm_scoring_with_explanations(
            candidates, job_keywords, job_level, job_description
        )
        
        # Apply confidence threshold and select top 3
        threshold_candidates = [r for r in ranked_scores if r.score >= 1.0][:3]  # Lower threshold for rule of three
        selected_case_studies = [score.case_study for score in threshold_candidates]
        
        return selected_case_studies, ranked_scores
    
    def _create_semantic_scoring_prompt(
        self, 
        candidates: List[Dict[str, Any]], 
        job_keywords: List[str], 
        job_level: Optional[str], 
        job_description: Optional[str]
    ) -> str:
        """Create semantic scoring prompt for LLM."""
        prompt = f"""
Job Analysis:
- Keywords: {', '.join(job_keywords)}
- Level: {job_level or 'Not specified'}
- Description: {job_description or 'Not provided'}

Case Studies to Score:
"""
        
        for i, case_study in enumerate(candidates):
            prompt += f"""
Case Study {i+1}: {case_study.get('name', case_study.get('id', 'Unknown'))}
- Tags: {', '.join(case_study.get('tags', []))}
- Description: {case_study.get('description', 'No description')}

Rate relevance (1-10) and explain why this case study fits this job.
Consider: role level, industry, skills, company stage, business model.
"""
        
        prompt += """
Provide your analysis in JSON format:
{
  "scores": [
    {"case_study_id": "id", "score": 8, "reasoning": "explanation"},
    ...
  ]
}
"""
        
        return prompt
    
    def _simulate_llm_scoring(
        self, 
        candidates: List[Dict[str, Any]], 
        job_keywords: List[str], 
        job_level: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Simulate LLM scoring with enhanced tag matching."""
        scored = []
        
        for case_study in candidates:
            # Enhanced scoring based on tag matches and job level
            base_score = case_study.get('stage1_score', 0)
            
            # Level-based scoring
            level_bonus = 0
            level_reasoning = ""
            if job_level:
                if job_level == 'L5' and 'leadership' in case_study.get('tags', []):
                    level_bonus = 2
                    level_reasoning = "Strong leadership experience matches L5 role requirements."
                elif job_level == 'L4' and 'growth' in case_study.get('tags', []):
                    level_bonus = 1.5
                    level_reasoning = "Growth experience aligns with L4 product manager role."
                elif job_level == 'L3' and 'product' in case_study.get('tags', []):
                    level_bonus = 1
                    level_reasoning = "Product experience suitable for L3 role."
            
            # Industry alignment bonus
            industry_bonus = 0
            industry_reasoning = ""
            case_study_tags = case_study.get('tags', [])
            if 'cleantech' in job_keywords and 'cleantech' in case_study_tags:
                industry_bonus = 1.5
                industry_reasoning = "Direct cleantech industry experience matches job requirements."
            elif 'ai_ml' in job_keywords and 'ai_ml' in case_study_tags:
                industry_bonus = 1.5
                industry_reasoning = "AI/ML experience directly relevant to job requirements."
            
            # Calculate final score
            final_score = base_score + level_bonus + industry_bonus
            
            # Generate comprehensive reasoning
            reasoning_parts = []
            if base_score > 0:
                reasoning_parts.append(f"Tag match score: {base_score}")
            if level_reasoning:
                reasoning_parts.append(level_reasoning)
            if industry_reasoning:
                reasoning_parts.append(industry_reasoning)
            
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Limited relevance to job requirements."
            
            # Calculate confidence based on score strength
            confidence = min(0.95, 0.5 + (final_score / 10.0))
            
            # Create CaseStudyScore object
            case_study_score = CaseStudyScore(
                case_study=case_study,
                score=final_score,
                confidence=confidence,
                reasoning=reasoning,
                stage1_score=base_score,
                level_bonus=level_bonus,
                industry_bonus=industry_bonus
            )
            
            case_study['llm_score'] = final_score
            case_study['level_bonus'] = level_bonus
            case_study['industry_bonus'] = industry_bonus
            scored.append(case_study)
        
        # Sort by LLM score (descending)
        scored.sort(key=lambda x: x.get('llm_score', 0), reverse=True)
        
        return scored
    
    def _simulate_llm_scoring_with_explanations(
        self, 
        candidates: List[Dict[str, Any]], 
        job_keywords: List[str], 
        job_level: Optional[str],
        job_description: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], List[CaseStudyScore]]:
        """Simulate LLM scoring with explanations and confidence tracking."""
        scored = []
        ranked_scores = []
        
        for case_study in candidates:
            # Enhanced scoring based on tag matches and job level
            base_score = case_study.get('stage1_score', 0)
            
            # Level-based scoring
            level_bonus = 0
            level_reasoning = ""
            if job_level:
                if job_level == 'L5' and 'leadership' in case_study.get('tags', []):
                    level_bonus = 2
                    level_reasoning = "Strong leadership experience matches L5 role requirements."
                elif job_level == 'L4' and 'growth' in case_study.get('tags', []):
                    level_bonus = 1.5
                    level_reasoning = "Growth experience aligns with L4 product manager role."
                elif job_level == 'L3' and 'product' in case_study.get('tags', []):
                    level_bonus = 1
                    level_reasoning = "Product experience suitable for L3 role."
            
            # Industry alignment bonus
            industry_bonus = 0
            industry_reasoning = ""
            case_study_tags = case_study.get('tags', [])
            if 'cleantech' in job_keywords and 'cleantech' in case_study_tags:
                industry_bonus = 1.5
                industry_reasoning = "Direct cleantech industry experience matches job requirements."
            elif 'ai_ml' in job_keywords and 'ai_ml' in case_study_tags:
                industry_bonus = 1.5
                industry_reasoning = "AI/ML experience directly relevant to job requirements."
            
            # Calculate final score
            final_score = base_score + level_bonus + industry_bonus
            
            # Generate comprehensive reasoning
            reasoning_parts = []
            if base_score > 0:
                reasoning_parts.append(f"Tag match score: {base_score}")
            if level_reasoning:
                reasoning_parts.append(level_reasoning)
            if industry_reasoning:
                reasoning_parts.append(industry_reasoning)
            
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Limited relevance to job requirements."
            
            # Calculate confidence based on score strength
            confidence = min(0.95, 0.5 + (final_score / 10.0))
            
            # Create CaseStudyScore object
            case_study_score = CaseStudyScore(
                case_study=case_study,
                score=final_score,
                confidence=confidence,
                reasoning=reasoning,
                stage1_score=base_score,
                level_bonus=level_bonus,
                industry_bonus=industry_bonus
            )
            
            case_study['llm_score'] = final_score
            case_study['level_bonus'] = level_bonus
            case_study['industry_bonus'] = industry_bonus
            scored.append(case_study)
            ranked_scores.append(case_study_score)
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x.get('llm_score', 0), reverse=True)
        ranked_scores.sort(key=lambda x: x.score, reverse=True)
        
        return scored, ranked_scores
    
    def _fallback_selection(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback selection using stage1 scores."""
        if not candidates:
            return []
        
        # Select top 3 based on stage1 scores
        return candidates[:3]
    
    def _estimate_llm_cost(self, num_candidates: int) -> float:
        """Estimate LLM cost for scoring."""
        return num_candidates * self.llm_cost_per_call


def test_hybrid_selection():
    """Test the hybrid case study selection functionality."""
    print("🧪 Testing Hybrid Case Study Selection...")
    
    # Test case studies
    test_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'description': 'Led cross-functional team from 0-1 to improve home energy management'
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'B2B', 'clean_energy', 'scaling', 'leadership'],
            'description': 'Helped scale company from Series A to Series C, leading platform rebuild'
        },
        {
            'id': 'meta',
            'name': 'Meta Explainable AI Case Study',
            'tags': ['AI', 'ML', 'trust', 'internal_tools', 'explainable'],
            'description': 'Led cross-functional ML team to scale global recruiting tools'
        },
        {
            'id': 'samsung',
            'name': 'Samsung Customer Care Case Study',
            'tags': ['growth', 'ux', 'b2c', 'public', 'onboarding', 'usability', 'mobile', 'support', 'engagement'],
            'description': 'Led overhaul of Samsung+ app, restoring trust and driving engagement'
        }
    ]
    
    # Test selector
    selector = HybridCaseStudySelector(llm_enabled=True, max_llm_candidates=10)
    
    # Test with different job scenarios
    test_scenarios = [
        {
            'name': 'L5 Cleantech PM',
            'keywords': ['product manager', 'cleantech', 'leadership', 'growth'],
            'level': 'L5',
            'description': 'Senior Product Manager role in cleantech startup'
        },
        {
            'name': 'L4 AI/ML PM',
            'keywords': ['product manager', 'AI', 'ML', 'internal_tools'],
            'level': 'L4',
            'description': 'Product Manager role in AI/ML company'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        
        result = selector.select_case_studies(
            test_case_studies,
            scenario['keywords'],
            scenario['level'],
            scenario['description']
        )
        
        print(f"  Stage 1 candidates: {result.stage1_candidates}")
        print(f"  Stage 2 scored: {result.stage2_scored}")
        print(f"  Selected: {len(result.selected_case_studies)} case studies")
        print(f"  Total time: {result.total_time:.3f}s")
        print(f"  LLM cost estimate: ${result.llm_cost_estimate:.3f}")
        print(f"  Fallback used: {result.fallback_used}")
        
        for i, case_study in enumerate(result.selected_case_studies):
            print(f"    {i+1}. {case_study.get('name', case_study.get('id'))}")
            print(f"       Score: {case_study.get('llm_score', case_study.get('stage1_score', 0))}")
            print(f"       Tags: {case_study.get('tags', [])}")
    
    print("\n✅ Hybrid Case Study Selection test completed!")


if __name__ == "__main__":
    test_hybrid_selection() 