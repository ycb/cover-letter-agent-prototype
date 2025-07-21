#!/usr/bin/env python3
"""
Debug script to understand case study scoring issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cover_letter_agent import CoverLetterAgent

def debug_keyword_matching():
    """Debug why keyword matching is failing."""
    
    # Initialize agent
    agent = CoverLetterAgent(user_id="peter")
    
    # Duke Energy job keywords
    job_keywords = [
        "internal_tools", "utility", "L5", "org_leadership", 
        "strategic_alignment", "people_development", "cross_org_influence", 
        "portfolio_management"
    ]
    
    print("=== DEBUGGING KEYWORD MATCHING ===")
    print(f"Job keywords: {job_keywords}")
    print()
    
    # Load case studies
    case_studies = agent.blurbs.get('examples', [])
    
    print("=== CASE STUDY TAGS ANALYSIS ===")
    for cs in case_studies:
        cs_id = cs.get('id', 'unknown')
        tags = cs.get('tags', [])
        
        print(f"\n{cs_id}:")
        print(f"  Tags: {tags}")
        
        # Check for matches
        matches = []
        for tag in tags:
            if tag.lower() in [kw.lower() for kw in job_keywords]:
                matches.append(tag)
        
        if matches:
            print(f"  ✅ MATCHES: {matches}")
        else:
            print(f"  ❌ NO MATCHES")
            
        # Check for partial matches
        partial_matches = []
        for tag in tags:
            for kw in job_keywords:
                if tag.lower() in kw.lower() or kw.lower() in tag.lower():
                    partial_matches.append(f"{tag} ~ {kw}")
        
        if partial_matches:
            print(f"  🔍 PARTIAL MATCHES: {partial_matches}")
    
    print("\n=== SCORING LOGIC DEBUG ===")
    print("Testing the actual scoring logic:")
    
    # Test the scoring logic directly
    maturity_tags = ['startup', 'scaleup', 'public', 'enterprise']
    business_model_tags = ['b2b', 'b2c', 'marketplace', 'saas']
    role_type_tags = ['founding_pm', 'staff_pm', 'principal_pm', 'group_pm']
    key_skill_tags = ['ai_ml', 'data', 'product', 'growth', 'platform']
    industry_tags = ['fintech', 'healthtech', 'ecommerce', 'social']
    
    for cs in case_studies:
        cs_id = cs.get('id', 'unknown')
        tags = cs.get('tags', [])
        
        print(f"\n{cs_id} scoring:")
        initial_score = 0
        tag_matches = set()
        
        for tag in tags:
            if tag.lower() in [kw.lower() for kw in job_keywords]:
                print(f"  ✅ {tag} matches job keyword")
                # Strong weighting for certain tag categories
                if tag.lower() in maturity_tags or tag.lower() in business_model_tags or tag.lower() in role_type_tags:
                    initial_score += 3
                    print(f"    +3 points (maturity/business/role tag)")
                elif tag.lower() in key_skill_tags or tag.lower() in industry_tags:
                    initial_score += 1
                    print(f"    +1 point (skill/industry tag)")
                else:
                    print(f"    +0 points (no category match)")
                tag_matches.add(tag.lower())
            else:
                print(f"  ❌ {tag} does not match any job keyword")
        
        print(f"  Final initial score: {initial_score}")

if __name__ == "__main__":
    debug_keyword_matching() 