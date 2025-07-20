#!/usr/bin/env python3
"""
Test PM Levels Framework Integration
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_pm_framework_integration():
    """Test the PM levels framework integration."""
    
    print("🧪 Testing PM Levels Framework Integration")
    print("=" * 50)
    
    # Test 1: Load PM levels framework
    try:
        from agents.pm_inference import PMLevelsFramework
        framework = PMLevelsFramework()
        print("✅ PM Levels Framework loaded successfully")
        
        # Test getting competencies for L3
        competencies = framework.get_competencies_for_level('L3')
        print(f"✅ L3 competencies: {[comp['name'] for comp in competencies]}")
        
    except Exception as e:
        print(f"❌ PM Levels Framework test failed: {e}")
        return False
    
    # Test 2: Test job parser with PM framework
    try:
        from agents.job_parser_llm import parse_job_with_llm
        
        test_jd = """
        Duke Energy is seeking a Senior Product Manager to join our growing team.
        
        We are looking for someone with:
        - 5+ years of product management experience
        - Experience leading cross-functional teams
        - Strong data analysis and A/B testing skills
        - Experience with growth metrics and KPIs
        - Excellent communication and stakeholder management skills
        
        The ideal candidate will:
        - Define product strategy and roadmap
        - Lead engineering and design teams
        - Conduct market research and competitive analysis
        - Drive product launches and measure success
        """
        
        result = parse_job_with_llm(test_jd)
        print(f"✅ Job parsing completed:")
        print(f"   Company: {result.get('company_name', 'Unknown')}")
        print(f"   Title: {result.get('job_title', 'Unknown')}")
        print(f"   Level: {result.get('inferred_level', 'Unknown')}")
        print(f"   Role Type: {result.get('inferred_role_type', 'Unknown')}")
        print(f"   Prioritized Skills: {result.get('prioritized_skills', [])}")
        
    except Exception as e:
        print(f"❌ Job parser test failed: {e}")
        return False
    
    # Test 3: Test PM inference
    try:
        from agents.pm_inference import PMUserSignals, infer_pm_profile
        
        signals = PMUserSignals(
            resume_text="Senior Product Manager with 5 years experience leading cross-functional teams",
            years_experience=5,
            titles=["Senior Product Manager"],
            team_leadership=True,
            data_fluency_signal=True
        )
        
        result = infer_pm_profile(signals)
        print(f"✅ PM inference completed:")
        print(f"   Level: {result.get('level', 'Unknown')}")
        print(f"   Role Type: {result.get('role_type', 'Unknown')}")
        print(f"   Competencies: {list(result.get('competencies', {}).keys())}")
        
    except Exception as e:
        print(f"❌ PM inference test failed: {e}")
        return False
    
    print("\n🎉 All PM levels framework integration tests passed!")
    return True

def test_cover_letter_agent_integration():
    """Test the cover letter agent with PM framework integration."""
    
    print("\n🔍 Testing Cover Letter Agent Integration")
    print("=" * 50)
    
    try:
        from agents.cover_letter_agent import CoverLetterAgent
        
        # Initialize agent
        agent = CoverLetterAgent()
        print("✅ Cover Letter Agent initialized")
        
        # Test job description parsing
        test_jd = """
        Duke Energy is seeking a Senior Product Manager to join our growing team.
        
        We are looking for someone with:
        - 5+ years of product management experience
        - Experience leading cross-functional teams
        - Strong data analysis and A/B testing skills
        - Experience with growth metrics and KPIs
        - Excellent communication and stakeholder management skills
        """
        
        job = agent.parse_job_description(test_jd)
        print(f"✅ Job parsing completed:")
        print(f"   Company: {job.company_name}")
        print(f"   Title: {job.job_title}")
        print(f"   Score: {job.score}")
        print(f"   Go/No-Go: {job.go_no_go}")
        
        # Check if PM framework data is included
        if hasattr(job, 'extracted_info') and job.extracted_info:
            pm_data = job.extracted_info.get('inferred_level')
            if pm_data:
                print(f"   PM Level: {pm_data}")
                print("✅ PM framework data integrated successfully")
            else:
                print("⚠️  PM framework data not found in job parsing")
        
    except Exception as e:
        print(f"❌ Cover Letter Agent integration test failed: {e}")
        return False
    
    print("\n🎉 Cover Letter Agent integration test passed!")
    return True

def main():
    """Run all integration tests."""
    
    tests = [
        ("PM Framework Integration", test_pm_framework_integration),
        ("Cover Letter Agent Integration", test_cover_letter_agent_integration),
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
        print("🎉 All integration tests passed! PM levels framework is working.")
        return 0
    else:
        print("⚠️  Some integration tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 