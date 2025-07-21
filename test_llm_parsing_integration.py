#!/usr/bin/env python3
"""
Test LLM Parsing Integration

This test suite verifies that the cover letter agent correctly uses LLM parsing
instead of manual parsing, with proper fallback handling.
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_llm_parser_basic_functionality():
    """Test basic LLM parser functionality."""
    
    print("🧪 Testing LLM Parser Basic Functionality")
    print("=" * 50)
    
    try:
        from agents.job_parser_llm import JobParserLLM
        
        # Test with a simple job description
        test_jd = """
        Duke Energy
        Product Manager
        
        We are seeking a Product Manager to join our team.
        Requirements:
        - 5+ years product management experience
        - Experience with data analysis
        - Cross-functional leadership skills
        """
        
        parser = JobParserLLM()
        result = parser.parse_job_description(test_jd)
        
        # Verify required fields are present
        required_fields = ['company_name', 'job_title', 'inferred_level', 'inferred_role_type']
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        print(f"✅ LLM Parser basic functionality:")
        print(f"   Company: {result.get('company_name')}")
        print(f"   Title: {result.get('job_title')}")
        print(f"   Level: {result.get('inferred_level')}")
        print(f"   Role Type: {result.get('inferred_role_type')}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Parser basic functionality test failed: {e}")
        return False

def test_cover_letter_agent_llm_parsing():
    """Test that cover letter agent uses LLM parsing."""
    
    print("\n🔍 Testing Cover Letter Agent LLM Parsing")
    print("=" * 50)
    
    try:
        from agents.cover_letter_agent import CoverLetterAgent
        
        # Initialize agent
        agent = CoverLetterAgent()
        print("✅ Cover Letter Agent initialized")
        
        # Test job description parsing
        test_jd = """
        Duke Energy
        Product Manager
        
        We are seeking a Product Manager to join our team.
        Requirements:
        - 5+ years product management experience
        - Experience with data analysis
        - Cross-functional leadership skills
        """
        
        job = agent.parse_job_description(test_jd)
        
        # Verify LLM parsing was used (should extract "Duke Energy" not "Position")
        assert job.company_name == "Duke Energy", f"Expected 'Duke Energy', got '{job.company_name}'"
        assert job.job_title == "Product Manager", f"Expected 'Product Manager', got '{job.job_title}'"
        
        # Check if PM framework data is included
        if hasattr(job, 'extracted_info') and job.extracted_info:
            pm_level = job.extracted_info.get('inferred_level')
            pm_role_type = job.extracted_info.get('inferred_role_type')
            
            if pm_level:
                print(f"✅ PM Level extracted: {pm_level}")
            if pm_role_type:
                print(f"✅ PM Role Type extracted: {pm_role_type}")
        
        print(f"✅ Cover Letter Agent LLM parsing:")
        print(f"   Company: {job.company_name}")
        print(f"   Title: {job.job_title}")
        print(f"   Score: {job.score}")
        print(f"   Go/No-Go: {job.go_no_go}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cover Letter Agent LLM parsing test failed: {e}")
        return False

def test_llm_parser_fallback():
    """Test LLM parser fallback when LLM fails."""
    
    print("\n🔄 Testing LLM Parser Fallback")
    print("=" * 50)
    
    try:
        from agents.job_parser_llm import JobParserLLM
        
        # Mock the LLM call to fail
        with patch('agents.job_parser_llm.call_openai') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            
            parser = JobParserLLM()
            test_jd = "Duke Energy\nProduct Manager"
            
            result = parser.parse_job_description(test_jd)
            
            # Should fall back to manual parsing
            assert 'company_name' in result, "Fallback should still return company_name"
            assert 'job_title' in result, "Fallback should still return job_title"
            
            print("✅ LLM Parser fallback working correctly")
            print(f"   Company: {result.get('company_name')}")
            print(f"   Title: {result.get('job_title')}")
            
            return True
            
    except Exception as e:
        print(f"❌ LLM Parser fallback test failed: {e}")
        return False

def test_cover_letter_agent_fallback():
    """Test cover letter agent fallback when LLM parsing fails."""
    
    print("\n🔄 Testing Cover Letter Agent Fallback")
    print("=" * 50)
    
    try:
        from agents.cover_letter_agent import CoverLetterAgent
        
        # Mock the LLM parser to fail
        with patch('agents.job_parser_llm.JobParserLLM') as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser.parse_job_description.side_effect = Exception("LLM Error")
            mock_parser_class.return_value = mock_parser
            
            agent = CoverLetterAgent()
            test_jd = "Duke Energy\nProduct Manager"
            
            job = agent.parse_job_description(test_jd)
            
            # Should fall back to manual parsing
            assert job.company_name, "Fallback should extract company name"
            assert job.job_title, "Fallback should extract job title"
            
            print("✅ Cover Letter Agent fallback working correctly")
            print(f"   Company: {job.company_name}")
            print(f"   Title: {job.job_title}")
            
            return True
            
    except Exception as e:
        print(f"❌ Cover Letter Agent fallback test failed: {e}")
        return False

def test_pm_levels_integration():
    """Test that PM levels framework is properly integrated with LLM parsing."""
    
    print("\n📊 Testing PM Levels Integration")
    print("=" * 50)
    
    try:
        from agents.cover_letter_agent import CoverLetterAgent
        
        agent = CoverLetterAgent()
        
        # Test with a job description that should trigger specific PM level inference
        test_jd = """
        Duke Energy
        Senior Product Manager
        
        We are seeking a Senior Product Manager with:
        - 8+ years of product management experience
        - Experience leading multiple product teams
        - Strategic planning and roadmap development
        - Executive stakeholder management
        - Experience with large-scale product launches
        """
        
        job = agent.parse_job_description(test_jd)
        
        # Check if PM framework data is properly integrated
        if hasattr(job, 'extracted_info') and job.extracted_info:
            pm_level = job.extracted_info.get('inferred_level')
            pm_role_type = job.extracted_info.get('inferred_role_type')
            competencies = job.extracted_info.get('required_competencies', {})
            
            print(f"✅ PM Levels Integration:")
            print(f"   Level: {pm_level}")
            print(f"   Role Type: {pm_role_type}")
            print(f"   Competencies: {list(competencies.keys())}")
            
            # Verify that PM data is being used in keywords
            if pm_level in job.keywords:
                print(f"✅ PM Level '{pm_level}' included in keywords")
            if pm_role_type in job.keywords:
                print(f"✅ PM Role Type '{pm_role_type}' included in keywords")
        
        return True
        
    except Exception as e:
        print(f"❌ PM Levels integration test failed: {e}")
        return False

def test_real_job_description():
    """Test with the actual Duke Energy job description."""
    
    print("\n📄 Testing Real Job Description")
    print("=" * 50)
    
    try:
        from agents.cover_letter_agent import CoverLetterAgent
        
        # Load the actual job description
        with open('data/job_description.txt', 'r') as f:
            real_jd = f.read()
        
        agent = CoverLetterAgent()
        job = agent.parse_job_description(real_jd)
        
        # Verify correct extraction
        assert job.company_name == "Duke Energy", f"Expected 'Duke Energy', got '{job.company_name}'"
        assert "Product" in job.job_title, f"Expected job title to contain 'Product', got '{job.job_title}'"
        
        print(f"✅ Real job description parsing:")
        print(f"   Company: {job.company_name}")
        print(f"   Title: {job.job_title}")
        print(f"   Score: {job.score}")
        print(f"   Go/No-Go: {job.go_no_go}")
        
        # Check PM framework integration
        if hasattr(job, 'extracted_info') and job.extracted_info:
            pm_level = job.extracted_info.get('inferred_level')
            pm_role_type = job.extracted_info.get('inferred_role_type')
            
            if pm_level:
                print(f"   PM Level: {pm_level}")
            if pm_role_type:
                print(f"   PM Role Type: {pm_role_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real job description test failed: {e}")
        return False

def main():
    """Run all LLM parsing integration tests."""
    
    tests = [
        ("LLM Parser Basic Functionality", test_llm_parser_basic_functionality),
        ("Cover Letter Agent LLM Parsing", test_cover_letter_agent_llm_parsing),
        ("LLM Parser Fallback", test_llm_parser_fallback),
        ("Cover Letter Agent Fallback", test_cover_letter_agent_fallback),
        ("PM Levels Integration", test_pm_levels_integration),
        ("Real Job Description", test_real_job_description),
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
        print("🎉 All LLM parsing integration tests passed!")
        print("✅ LLM parsing is working correctly with proper fallback handling")
        return 0
    else:
        print("⚠️  Some LLM parsing integration tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 