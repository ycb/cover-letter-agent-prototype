#!/usr/bin/env python3
"""
PM Level Integration Module
==========================

Provides PM level-based scoring and selection logic for case studies.
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.logging_config import get_logger

logger = get_logger(__name__)


class PMLevelIntegration:
    """Handles PM level-based scoring and selection logic."""
    
    def __init__(self, data_dir: Path):
        """Initialize with data directory."""
        self.data_dir = data_dir
        self.pm_levels = self._load_pm_levels()
    
    def _load_pm_levels(self) -> Dict[str, Any]:
        """Load PM levels configuration from YAML file."""
        try:
            pm_levels_path = self.data_dir / "pm_levels.yaml"
            if pm_levels_path.exists():
                with open(pm_levels_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"PM levels file not found: {pm_levels_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load PM levels: {e}")
            return {}
    
    def determine_job_level(self, job_title: str, job_keywords: List[str]) -> str:
        """Determine the PM level for a job based on title and keywords."""
        job_title_lower = job_title.lower()
        job_keywords_lower = [kw.lower() for kw in job_keywords]
        
        # Level detection logic
        if any(word in job_title_lower for word in ['principal', 'director', 'head']):
            return 'L6'
        elif any(word in job_title_lower for word in ['staff', 'senior staff']):
            return 'L5'
        elif any(word in job_title_lower for word in ['senior', 'lead']):
            return 'L4'
        elif any(word in job_title_lower for word in ['product manager', 'pm']):
            return 'L3'
        elif any(word in job_title_lower for word in ['associate', 'junior', 'entry']):
            return 'L2'
        else:
            # Default based on keywords
            if any(word in job_keywords_lower for word in ['org_leadership', 'strategic_alignment', 'cross_org_influence']):
                return 'L5'
            elif any(word in job_keywords_lower for word in ['team_leadership', 'mentoring', 'portfolio_management']):
                return 'L4'
            else:
                return 'L4'  # Default to Senior PM
    
    def get_level_competencies(self, job_level: str) -> List[str]:
        """Get the key competencies for a specific PM level."""
        level_data = self.pm_levels.get('pm_levels', {}).get(job_level, {})
        return level_data.get('key_competencies', [])
    
    def add_pm_level_scoring(self, base_score: float, case_study: Dict[str, Any], job_level: str) -> float:
        """Add PM level-based scoring bonus to case study score."""
        try:
            # Get level competencies
            level_competencies = self.get_level_competencies(job_level)
            if not level_competencies:
                logger.warning(f"No competencies found for level: {job_level}")
                return base_score
            
            # Count matching tags
            case_study_tags = set(case_study.get('tags', []))
            level_matches = len(case_study_tags.intersection(set(level_competencies)))
            
            # Get scoring multiplier for this level
            multiplier = self.pm_levels.get('level_scoring_multipliers', {}).get(job_level, 1.0)
            
            # Calculate bonus points
            bonus_points = level_matches * 2 * multiplier
            
            # Log the scoring
            logger.debug(f"PM Level Scoring for {case_study.get('id', 'unknown')} (Level {job_level}):")
            logger.debug(f"  Base score: {base_score}")
            logger.debug(f"  Level competencies: {level_competencies}")
            logger.debug(f"  Case study tags: {case_study_tags}")
            logger.debug(f"  Level matches: {level_matches}")
            logger.debug(f"  Level multiplier: {multiplier}")
            logger.debug(f"  Bonus points: {bonus_points}")
            logger.debug(f"  Final score: {base_score + bonus_points}")
            
            return base_score + bonus_points
            
        except Exception as e:
            logger.error(f"Error in PM level scoring: {e}")
            return base_score
    
    def track_selection_patterns(self, selected_case_studies: List[Dict[str, Any]], job_level: str) -> None:
        """Track which case studies are selected for each PM level."""
        try:
            # Create analytics entry
            analytics_entry = {
                'timestamp': datetime.now().isoformat(),
                'job_level': job_level,
                'selected_case_studies': [cs.get('id', 'unknown') for cs in selected_case_studies],
                'case_study_tags': [cs.get('tags', []) for cs in selected_case_studies]
            }
            
            # Save to analytics file
            analytics_path = self.data_dir / "pm_level_analytics.yaml"
            analytics_data = []
            
            if analytics_path.exists():
                with open(analytics_path, 'r') as f:
                    analytics_data = yaml.safe_load(f) or []
            
            analytics_data.append(analytics_entry)
            
            with open(analytics_path, 'w') as f:
                yaml.dump(analytics_data, f, default_flow_style=False)
            
            logger.info(f"Tracked selection pattern for level {job_level}: {[cs.get('id') for cs in selected_case_studies]}")
            
        except Exception as e:
            logger.error(f"Failed to track selection patterns: {e}")
    
    def enhance_case_studies_with_pm_levels(
        self, 
        case_studies: List[Dict[str, Any]], 
        job_title: str, 
        job_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Enhance case studies with PM level scoring."""
        
        # Determine job level
        job_level = self.determine_job_level(job_title, job_keywords)
        logger.info(f"Determined job level: {job_level} for title: {job_title}")
        
        # Apply PM level scoring
        enhanced_case_studies = []
        for cs in case_studies:
            # Get base score (assuming it's stored in the case study)
            base_score = cs.get('score', 0.0)
            
            # Apply PM level scoring
            enhanced_score = self.add_pm_level_scoring(base_score, cs, job_level)
            
            # Create enhanced case study with new score
            enhanced_cs = cs.copy()
            enhanced_cs['score'] = enhanced_score
            enhanced_cs['pm_level'] = job_level
            enhanced_cs['base_score'] = base_score
            enhanced_cs['pm_level_bonus'] = enhanced_score - base_score
            
            enhanced_case_studies.append(enhanced_cs)
        
        # Sort by enhanced score
        enhanced_case_studies.sort(key=lambda x: x['score'], reverse=True)
        
        # Track selection patterns
        self.track_selection_patterns(enhanced_case_studies[:3], job_level)
        
        return enhanced_case_studies 