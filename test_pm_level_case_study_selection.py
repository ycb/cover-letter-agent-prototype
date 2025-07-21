#!/usr/bin/env python3
"""
Test PM Level Integration with Case Study Selection
==================================================

Tests the full integration of PM level scoring with case study selection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.pm_level_integration import PMLevelIntegration
from agents.cover_letter_agent import CoverLetterAgent
from pathlib import Path

def test_pm_level_case_study_selection():
    """Test PM level integration with actual case study selection."""
    print("🧪 Testing PM Level Integration with Case Study Selection...")
    
    # Initialize components
    data_dir = Path("data")
    pm_integration = PMLevelIntegration(data_dir)
    agent = CoverLetterAgent(data_dir="data")
    
    # Test job descriptions
    test_jobs = [
        {
            "title": "Senior Product Manager",
            "keywords": ["internal_tools", "utility", "L5", "org_leadership", "strategic_alignment", "people_development", "cross_org_influence", "portfolio_management"],
            "expected_level": "L4"
        },
        {
            "title": "Staff Product Manager", 
            "keywords": ["org_leadership", "strategic_alignment", "cross_org_influence", "portfolio_management", "people_development"],
            "expected_level": "L5"
        },
        {
            "title": "Principal Product Manager",
            "keywords": ["company_strategy", "board_communication", "industry_thought_leadership", "org_leadership", "strategic_alignment"],
            "expected_level": "L6"
        }
    ]
    
    for job in test_jobs:
        print(f"\n📋 Testing {job['title']}:")
        
        # Get base case studies
        base_case_studies = agent.get_case_studies(job['keywords'])
        print(f"  Base case studies: {[cs['id'] for cs in base_case_studies[:3]]}")
        
        # Apply PM level enhancement
        enhanced_case_studies = pm_integration.enhance_case_studies_with_pm_levels(
            base_case_studies, job['title'], job['keywords']
        )
        
        # Show results
        print(f"  Job level: {enhanced_case_studies[0]['pm_level']} (expected: {job['expected_level']})")
        print("  Enhanced selection:")
        for cs in enhanced_case_studies[:3]:
            print(f"    {cs['id']}: {cs['base_score']:.1f} -> {cs['score']:.1f} (bonus: {cs['pm_level_bonus']:.1f})")
        
        # Verify level-appropriate competencies are prioritized
        top_cs = enhanced_case_studies[0]
        level_competencies = pm_integration.get_level_competencies(top_cs['pm_level'])
        matching_competencies = set(top_cs['tags']).intersection(set(level_competencies))
        
        if matching_competencies:
            print(f"    ✅ Top case study has {len(matching_competencies)} level-appropriate competencies: {list(matching_competencies)[:3]}")
        else:
            print(f"    ⚠️  Top case study has no level-appropriate competencies")
    
    print("\n✅ PM Level Case Study Selection test completed!")

if __name__ == "__main__":
    test_pm_level_case_study_selection() 