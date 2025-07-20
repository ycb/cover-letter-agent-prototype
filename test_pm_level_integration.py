#!/usr/bin/env python3
"""
Test script for PM Level Integration
===================================

Tests the PM level scoring and selection functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.pm_level_integration import PMLevelIntegration
from pathlib import Path

def test_pm_level_integration():
    """Test PM level integration functionality."""
    print("🧪 Testing PM Level Integration...")
    
    # Initialize PM level integration
    data_dir = Path("data")
    pm_integration = PMLevelIntegration(data_dir)
    
    # Test job level determination
    print("\n📋 Testing job level determination:")
    
    test_cases = [
        ("Senior Product Manager", ["product_strategy", "team_leadership"], "L4"),
        ("Staff Product Manager", ["org_leadership", "strategic_alignment"], "L5"),
        ("Principal Product Manager", ["company_strategy", "board_communication"], "L6"),
        ("Product Manager", ["product_execution", "user_research"], "L3"),
        ("Associate Product Manager", ["data_analysis", "feature_development"], "L2"),
    ]
    
    for job_title, keywords, expected_level in test_cases:
        actual_level = pm_integration.determine_job_level(job_title, keywords)
        status = "✅" if actual_level == expected_level else "❌"
        print(f"  {status} {job_title} -> {actual_level} (expected: {expected_level})")
    
    # Test level competencies
    print("\n🎯 Testing level competencies:")
    for level in ["L2", "L3", "L4", "L5", "L6"]:
        competencies = pm_integration.get_level_competencies(level)
        print(f"  {level}: {len(competencies)} competencies")
        if level == "L5":
            print(f"    Sample L5 competencies: {competencies[:5]}")
    
    # Test PM level scoring
    print("\n📊 Testing PM level scoring:")
    
    # Sample case studies with different tags
    test_case_studies = [
        {
            "id": "meta",
            "tags": ["org_leadership", "strategic_alignment", "cross_org_influence", "platform"],
            "score": 4.4
        },
        {
            "id": "aurora", 
            "tags": ["internal_tools", "cross_org_influence", "portfolio_management", "ai_ml"],
            "score": 2.4
        },
        {
            "id": "enact",
            "tags": ["org_leadership", "strategic_alignment", "people_development", "startup"],
            "score": 0.0
        }
    ]
    
    # Test scoring for different levels
    for level in ["L4", "L5"]:
        print(f"\n  Level {level} scoring:")
        for cs in test_case_studies:
            base_score = cs["score"]
            enhanced_score = pm_integration.add_pm_level_scoring(base_score, cs, level)
            bonus = enhanced_score - base_score
            print(f"    {cs['id']}: {base_score:.1f} -> {enhanced_score:.1f} (+{bonus:.1f})")
    
    # Test full enhancement
    print("\n🚀 Testing full case study enhancement:")
    job_title = "Senior Product Manager"
    job_keywords = ["product_strategy", "team_leadership", "org_leadership"]
    
    enhanced_case_studies = pm_integration.enhance_case_studies_with_pm_levels(
        test_case_studies, job_title, job_keywords
    )
    
    print(f"  Job level determined: {enhanced_case_studies[0]['pm_level']}")
    print("  Enhanced case studies:")
    for cs in enhanced_case_studies:
        print(f"    {cs['id']}: {cs['base_score']:.1f} -> {cs['score']:.1f} (bonus: {cs['pm_level_bonus']:.1f})")
    
    print("\n✅ PM Level Integration test completed!")

if __name__ == "__main__":
    test_pm_level_integration() 