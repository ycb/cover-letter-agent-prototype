#!/usr/bin/env python3
"""
Test script for PM inference system
"""

import os
import sys
from agents.pm_inference import PMUserSignals, infer_pm_profile, PMLevelsFramework

def test_pm_framework_loading():
    """Test that the PM levels framework loads correctly."""
    try:
        framework = PMLevelsFramework()
        levels = framework.get_all_levels()
        print(f"✅ PM Framework loaded successfully with {len(levels)} levels")
        
        # Test getting specific level
        l3_level = framework.get_level('L3')
        if l3_level:
            print(f"✅ L3 level found: {l3_level['title']}")
            competencies = framework.get_competencies_for_level('L3')
            print(f"✅ L3 has {len(competencies)} competencies")
        
        return True
    except Exception as e:
        print(f"❌ PM Framework loading failed: {e}")
        return False

def test_pm_inference():
    """Test PM inference with sample data."""
    try:
        # Create sample user signals
        signals = PMUserSignals(
            resume_text="""
            Senior Product Manager at TechCorp (2020-2023)
            - Led cross-functional team of 8 engineers and designers
            - Delivered 3 major product launches with 40% user growth
            - Defined multi-quarter roadmap aligned to business goals
            - Conducted A/B testing that improved conversion by 25%
            
            Product Manager at StartupXYZ (2018-2020)
            - Owned end-to-end product lifecycle for mobile app
            - Worked closely with design and engineering teams
            - Iterated quickly based on user feedback
            """,
            years_experience=5,
            titles=["Senior Product Manager", "Product Manager"],
            org_size="500-1000",
            team_leadership=True,
            data_fluency_signal=True,
            ml_experience_signal=False,
            work_samples=[
                {
                    "title": "Growth Feature Launch",
                    "description": "Led launch of viral sharing feature that increased DAU by 40%",
                    "type": "shipped-product"
                }
            ],
            story_docs=[
                "Successfully managed cross-functional team to deliver major product launch on schedule"
            ]
        )
        
        # Run inference
        result = infer_pm_profile(signals)
        
        print(f"✅ PM Inference completed:")
        print(f"   Level: {result['level']}")
        print(f"   Role Type: {result['role_type']}")
        print(f"   Archetype: {result['archetype']}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Competencies: {list(result['competencies'].keys())}")
        print(f"   Notes: {result.get('notes', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ PM Inference failed: {e}")
        return False

def test_prioritized_skills():
    """Test getting prioritized skills for a job."""
    try:
        framework = PMLevelsFramework()
        
        # Test getting skills for L3 growth PM
        skills = framework.get_competencies_for_level('L3')
        print(f"✅ L3 competencies: {[comp['name'] for comp in skills]}")
        
        # Test role types for L3
        role_types = framework.get_role_types_for_level('L3')
        print(f"✅ L3 role types: {role_types}")
        
        return True
    except Exception as e:
        print(f"❌ Prioritized skills test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing PM Inference System")
    print("=" * 50)
    
    tests = [
        ("PM Framework Loading", test_pm_framework_loading),
        ("PM Inference", test_pm_inference),
        ("Prioritized Skills", test_prioritized_skills),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PM inference system is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 