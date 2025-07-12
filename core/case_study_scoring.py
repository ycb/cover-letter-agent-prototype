#!/usr/bin/env python3
"""
Case Study Scoring Module
=========================

Customizable scoring system for case study selection based on user-defined weights.
Supports role-based, industry-specific, and seniority-aware scoring.
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CaseStudyScore:
    """Represents a scored case study with detailed breakdown."""
    case_study_id: str
    total_score: float
    category_scores: Dict[str, float]
    matched_tags: List[str]
    multipliers: List[str]
    penalties: List[str]
    explanations: List[str]


class CaseStudyScorer:
    """Customizable case study scoring system."""
    
    def __init__(self, user_id: Optional[str] = None, weights_path: Optional[str] = None):
        """Initialize the scorer with user-specific weights."""
        self.user_id = user_id
        self.weights = self._load_weights(weights_path)
        self.penalties = self.weights.get('penalties', {})
        
    def _load_weights(self, weights_path: Optional[str] = None) -> Dict[str, Any]:
        """Load user-specific or default scoring weights."""
        if weights_path and os.path.exists(weights_path):
            with open(weights_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Try user-specific weights
        if self.user_id:
            user_weights_path = f"users/{self.user_id}/user_weights.yaml"
            if os.path.exists(user_weights_path):
                with open(user_weights_path, 'r') as f:
                    return yaml.safe_load(f)
        
        # Fall back to default weights
        default_weights_path = "data/user_weights.yaml"
        if os.path.exists(default_weights_path):
            with open(default_weights_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Return minimal default weights
        return {
            'scoring_weights': {
                'role': {'growth': 3, 'platform': 2, 'founding_pm': 3, 'leadership': 4},
                'industry': {'cleantech': 4, 'infra': 3, 'analytics': 2},
                'maturity': {'startup': 3, 'scaleup': 2, 'public': 1},
                'business_model': {'b2b': 2, 'b2c': 2, 'b2b2c': 3},
                'key_qualities': {'xfn': 4, 'usability': 4, 'data_driven': 3}
            },
            'penalties': {
                'role_mismatch': -2,
                'redundant_themes': -3,
                'low_impact': -2
            }
        }
    
    def score_case_study(
        self, 
        case_study: Dict[str, Any], 
        job_keywords: List[str],
        job_title: str = "",
        selected_case_studies: Optional[List[Dict]] = None
    ) -> CaseStudyScore:
        """
        Score a case study based on customizable weights and job context.
        
        Args:
            case_study: The case study dictionary with tags and text
            job_keywords: Keywords extracted from job description
            job_title: Job title for role-based scoring
            selected_case_studies: Already selected case studies for diversity logic
            
        Returns:
            CaseStudyScore with detailed breakdown
        """
        case_study_id = case_study.get('id', 'unknown')
        tags = case_study.get('tags', [])
        text = case_study.get('text', '')
        
        # Initialize scoring
        category_scores = {}
        matched_tags = []
        multipliers = []
        penalties = []
        explanations = []
        
        # Get scoring weights
        weights = self.weights.get('scoring_weights', {})
        
        # Score by category
        for category, category_weights in weights.items():
            category_score = 0
            category_matches = []
            
            for tag, weight in category_weights.items():
                if tag in tags:
                    category_score += weight
                    category_matches.append(tag)
                    matched_tags.append(tag)
            
            if category_score > 0:
                category_scores[category] = category_score
                explanations.append(f"{category}: {category_score} points")
        
        # Calculate base score
        base_score = sum(category_scores.values())
        
        # Apply multipliers
        final_score = base_score
        
        # 1. Public company multiplier
        if 'public' in tags:
            multiplier = 1.2
            final_score *= multiplier
            multipliers.append(f"public_company: {multiplier:.1f}x")
            explanations.append("public company")
        
        # 2. Impressive metrics multiplier
        impressive_metrics = ['210%', '876%', '853%', '169%', '90%', '4B', '130%', '10x', '160%', '200%', '4.3', '20x', '60%', '80%']
        has_impressive_metrics = any(metric in text for metric in impressive_metrics)
        if has_impressive_metrics:
            multiplier = 1.3
            final_score *= multiplier
            multipliers.append(f"impressive_metrics: {multiplier:.1f}x")
            explanations.append("impressive metrics")
        
        # 3. Role-based adjustments
        role_multiplier = self._calculate_role_multiplier(job_title, tags)
        if role_multiplier != 1.0:
            final_score *= role_multiplier
            multipliers.append(f"role_alignment: {role_multiplier:.1f}x")
            explanations.append("role alignment")
        
        # 4. Credibility anchor multiplier
        credibility_anchors = ['meta', 'samsung', 'salesforce', 'aurora', 'enact']
        if case_study_id in credibility_anchors:
            multiplier = 1.2
            final_score *= multiplier
            multipliers.append(f"credibility_anchor: {multiplier:.1f}x")
            explanations.append("credible brand")
        
        # Apply penalties
        penalty_score = self._calculate_penalties(
            case_study, job_keywords, selected_case_studies
        )
        final_score += penalty_score
        
        if penalty_score < 0:
            penalties.append(f"penalties: {penalty_score:.1f}")
        
        return CaseStudyScore(
            case_study_id=case_study_id,
            total_score=final_score,
            category_scores=category_scores,
            matched_tags=matched_tags,
            multipliers=multipliers,
            penalties=penalties,
            explanations=explanations
        )
    
    def _calculate_role_multiplier(self, job_title: str, tags: List[str]) -> float:
        """Calculate role-based multiplier based on job title and case study tags."""
        job_title_lower = job_title.lower()
        
        # Staff/Principal PM: favor scale, impact, XFN leadership
        if any(word in job_title_lower for word in ['staff', 'principal', 'senior', 'lead']):
            if any(tag in tags for tag in ['scaleup', 'platform', 'xfn', 'leadership']):
                return 1.2
        
        # Startup PM: bias toward 0_to_1 and scrappy execution
        elif any(word in job_title_lower for word in ['startup', 'early', 'founding', '0-1']):
            if any(tag in tags for tag in ['founding_pm', '0_to_1', 'startup']):
                return 1.2
        
        # Growth PM: favor growth metrics and scaling
        elif 'growth' in job_title_lower:
            if any(tag in tags for tag in ['growth', 'plg', 'activation', 'engagement']):
                return 1.2
        
        # AI/ML PM: favor AI/ML experience
        elif any(word in job_title_lower for word in ['ai', 'ml', 'artificial', 'machine']):
            if any(tag in tags for tag in ['ai_ml', 'genai', 'nlp']):
                return 1.2
        
        return 1.0
    
    def _calculate_penalties(
        self, 
        case_study: Dict[str, Any], 
        job_keywords: List[str],
        selected_case_studies: Optional[List[Dict]] = None
    ) -> float:
        """Calculate penalties for mismatches and redundancy."""
        penalty_score = 0.0
        tags = case_study.get('tags', [])
        
        # Penalty for B2B-only if B2C/consumer present in JD
        if 'b2b' in tags and ('b2c' in job_keywords or 'consumer' in job_keywords):
            penalty_score += self.penalties.get('business_model_mismatch', -1)
        
        # Penalty for redundant themes
        if selected_case_studies:
            redundant_penalty = self.penalties.get('redundant_themes', -3)
            
            # Check for redundant founding PM stories
            if case_study['id'] in ['enact', 'spatialthink']:
                for other_cs in selected_case_studies:
                    if other_cs['id'] in ['enact', 'spatialthink']:
                        penalty_score += redundant_penalty
                        break
            
            # Check for redundant startup themes
            startup_tags = ['founding_pm', '0_to_1', 'startup']
            if any(tag in tags for tag in startup_tags):
                for other_cs in selected_case_studies:
                    if any(tag in other_cs.get('tags', []) for tag in startup_tags):
                        penalty_score += redundant_penalty
                        break
        
        return penalty_score
    
    def select_case_studies(
        self, 
        case_studies: List[Dict[str, Any]], 
        job_keywords: List[str],
        job_title: str = "",
        max_selections: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select top case studies using customizable scoring.
        
        Args:
            case_studies: List of case study dictionaries
            job_keywords: Keywords from job description
            job_title: Job title for role-based scoring
            max_selections: Maximum number of case studies to select
            
        Returns:
            List of selected case studies
        """
        # Score all case studies
        scored_case_studies = []
        for cs in case_studies:
            score = self.score_case_study(cs, job_keywords, job_title)
            scored_case_studies.append((cs, score))
        
        # Sort by score (descending)
        scored_case_studies.sort(key=lambda x: x[1].total_score, reverse=True)
        
        # Apply diversity logic
        selected = []
        used_themes = set()
        samsung_selected = False
        
        logger.info(f"[DEBUG] Scoring {len(scored_case_studies)} case studies:")
        for cs, score in scored_case_studies:
            logger.info(f"  {score.case_study_id}: {score.total_score:.1f}")
            if score.multipliers:
                logger.info(f"    Multipliers: {', '.join(score.multipliers)}")
            if score.penalties:
                logger.info(f"    Penalties: {', '.join(score.penalties)}")
        
        for cs, score in scored_case_studies:
            cs_id = score.case_study_id
            tags = cs.get('tags', [])
            
            logger.info(f"  Considering {cs_id} (score: {score.total_score:.1f})")
            
            # Samsung logic: only one allowed
            if cs_id in ['samsung', 'samsung_chatbot']:
                if samsung_selected:
                    logger.info(f"    Skipping {cs_id} - Samsung already selected")
                    continue
                
                # Prefer chatbot for AI/ML, NLP, or customer success
                if cs_id == 'samsung_chatbot' and any(tag in job_keywords for tag in ['ai_ml', 'nlp', 'customer_success']):
                    logger.info(f"    Selecting {cs_id} - preferred for AI/ML/NLP")
                    selected.append(cs)
                    samsung_selected = True
                elif cs_id == 'samsung' and not any(tag in job_keywords for tag in ['ai_ml', 'nlp', 'customer_success']):
                    logger.info(f"    Selecting {cs_id} - preferred for non-AI/ML")
                    selected.append(cs)
                    samsung_selected = True
                else:
                    logger.info(f"    Selecting {cs_id} - first Samsung found")
                    selected.append(cs)
                    samsung_selected = True
            
            # Check for redundant themes
            elif any(theme in tags for theme in ['founding_pm', '0_to_1', 'startup']):
                if any(theme in used_themes for theme in ['founding_pm', '0_to_1', 'startup']):
                    logger.info(f"    Skipping {cs_id} - redundant founding/startup theme")
                    continue
                else:
                    logger.info(f"    Selecting {cs_id} - unique founding/startup story")
                    selected.append(cs)
                    used_themes.update(['founding_pm', '0_to_1', 'startup'])
            
            # Check for scale/growth themes
            elif any(theme in tags for theme in ['scaleup', 'growth', 'platform']):
                if any(theme in used_themes for theme in ['scaleup', 'growth', 'platform']):
                    logger.info(f"    Skipping {cs_id} - redundant scale/growth theme")
                    continue
                else:
                    logger.info(f"    Selecting {cs_id} - unique scale/growth story")
                    selected.append(cs)
                    used_themes.update(['scaleup', 'growth', 'platform'])
            
            # Default selection
            else:
                logger.info(f"    Selecting {cs_id} - diverse theme")
                selected.append(cs)
            
            if len(selected) >= max_selections:
                logger.info(f"    Reached {max_selections} case studies, stopping")
                break
        
        logger.info(f"[DEBUG] Final selection: {[cs['id'] for cs in selected]}")
        return selected


def create_user_weights_template(user_id: str) -> Optional[str]:
    """Create a user-specific weights template."""
    template_path = f"users/{user_id}/user_weights.yaml"
    
    if not os.path.exists(f"users/{user_id}"):
        os.makedirs(f"users/{user_id}")
    
    # Copy default weights as template
    default_weights_path = "data/user_weights.yaml"
    if os.path.exists(default_weights_path):
        with open(default_weights_path, 'r') as f:
            template_content = f.read()
        
        with open(template_path, 'w') as f:
            f.write(template_content)
        
        return template_path
    
    return None


def get_job_type_weights(job_title: str, job_keywords: List[str]) -> Dict[str, Any]:
    """Get job-type-specific weights based on job title and keywords."""
    job_title_lower = job_title.lower()
    keywords_lower = [kw.lower() for kw in job_keywords]
    
    # Determine job type
    if any(word in job_title_lower for word in ['growth', 'acquisition', 'activation']):
        return {
            'role': {'growth': 5, 'data_driven': 4, 'metrics': 4},
            'impact': {'revenue': 5, 'users': 4, 'engagement': 4}
        }
    elif any(word in job_title_lower for word in ['ai', 'ml', 'artificial', 'machine']):
        return {
            'role': {'ai_ml': 5, 'data_driven': 4},
            'technical': {'ai_ml': 5, 'genai': 4, 'nlp': 4},
            'key_qualities': {'trust': 4, 'explainability': 4}
        }
    elif any(word in job_title_lower for word in ['founding', 'startup', 'early']):
        return {
            'role': {'founding_pm': 5, 'leadership': 4, 'strategy': 4},
            'maturity': {'startup': 5, 'pilot': 4},
            'key_qualities': {'gtm': 4, 'discovery': 4}
        }
    elif any(word in job_title_lower for word in ['enterprise', 'b2b', 'corporate']):
        return {
            'business_model': {'enterprise': 5, 'b2b': 4},
            'key_qualities': {'xfn': 5, 'strategy': 4},
            'maturity': {'public': 3, 'scaleup': 4}
        }
    elif any(word in keywords_lower for word in ['climate', 'energy', 'solar', 'renewable']):
        return {
            'industry': {'cleantech': 5},
            'business_model': {'b2b2c': 4},
            'key_qualities': {'mission': 4, 'impact': 4}
        }
    
    # Default weights
    return {} 