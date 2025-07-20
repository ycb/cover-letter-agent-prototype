#!/usr/bin/env python3
"""
Test script to verify scoring fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cover_letter_agent import CoverLetterAgent

def test_scoring_fix():
    """Test that case studies get proper scores."""
    
    # Initialize agent
    agent = CoverLetterAgent(user_id="peter")
    
    # Duke Energy job keywords
    job_keywords = [
        "internal_tools", "utility", "L5", "org_leadership", 
        "strategic_alignment", "people_development", "cross_org_influence", 
        "portfolio_management"
    ]
    
    print("=== TESTING SCORING FIX ===")
    print(f"Job keywords: {job_keywords}")
    print()
    
    # Test the scoring logic directly
    maturity_tags = ['startup', 'scaleup', 'public', 'enterprise']
    business_model_tags = ['b2b', 'b2c', 'marketplace', 'saas']
    role_type_tags = ['founding_pm', 'staff_pm', 'principal_pm', 'group_pm']
    key_skill_tags = ['ai_ml', 'data', 'product', 'growth', 'platform']
    industry_tags = ['fintech', 'healthtech', 'ecommerce', 'social']
    
    # Load case studies
    case_studies = agent.blurbs.get('examples', [])
    
    print("=== EXPECTED SCORES ===")
    for cs in case_studies:
        cs_id = cs.get('id', 'unknown')
        tags = cs.get('tags', [])
        
        initial_score = 0
        tag_matches = []
        
        for tag in tags:
            if tag.lower() in [kw.lower() for kw in job_keywords]:
                # Strong weighting for certain tag categories
                if tag.lower() in maturity_tags or tag.lower() in business_model_tags or tag.lower() in role_type_tags:
                    initial_score += 3
                elif tag.lower() in key_skill_tags or tag.lower() in industry_tags:
                    initial_score += 1
                else:
                    # Default scoring for other matches
                    initial_score += 2
                tag_matches.append(tag)
        
        if initial_score > 0:
            print(f"{cs_id}: {initial_score} points (matches: {tag_matches})")
        else:
            print(f"{cs_id}: 0 points (no matches)")
    
    print("\n=== EXPECTED SELECTION ===")
    print("Enact should have highest score (6 points: org_leadership + strategic_alignment + people_development)")
    print("Aurora should have good score (6 points: internal_tools + cross_org_influence + portfolio_management)")
    print("Meta should have moderate score (2 points: internal_tools)")

if __name__ == "__main__":
    test_scoring_fix() 