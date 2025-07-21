#!/usr/bin/env python3
"""
Test script to verify case study selection fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cover_letter_agent import CoverLetterAgent

def test_case_study_selection():
    """Test that Enact is selected for Duke Energy job."""
    
    # Initialize agent
    agent = CoverLetterAgent(user_id="peter")
    
    # Duke Energy job keywords
    job_keywords = [
        "internal_tools", "utility", "L5", "org_leadership", 
        "strategic_alignment", "people_development", "cross_org_influence", 
        "portfolio_management"
    ]
    
    print("Testing case study selection for Duke Energy job...")
    print(f"Job keywords: {job_keywords}")
    print()
    
    # Get case studies
    case_studies = agent.get_case_studies(job_keywords=job_keywords)
    
    print("Selected case studies:")
    for i, cs in enumerate(case_studies, 1):
        print(f"{i}. {cs['id']}")
        print(f"   Tags: {cs.get('tags', [])}")
        print(f"   Text: {cs.get('text', '')[:100]}...")
        print()
    
    # Check if Enact is selected
    selected_ids = [cs['id'] for cs in case_studies]
    print(f"Selected IDs: {selected_ids}")
    
    if 'enact' in selected_ids:
        print("✅ SUCCESS: Enact is selected!")
        return True
    else:
        print("❌ FAILURE: Enact is NOT selected!")
        print("Expected: Enact, Aurora, Meta")
        print(f"Actual: {selected_ids}")
        return False

if __name__ == "__main__":
    success = test_case_study_selection()
    sys.exit(0 if success else 1) 