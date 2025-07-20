#!/usr/bin/env python3
"""
Test Phase 3 Integration
========================

Tests the integration of work history context enhancement with the main agent.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.cover_letter_agent import CoverLetterAgent
from agents.work_history_context import WorkHistoryContextEnhancer


def test_phase3_integration():
    """Test the integration of Phase 3 work history context enhancement."""
    print("🧪 Testing Phase 3 Integration...")
    
    # Test work history context enhancement standalone
    print("\n📋 Testing Work History Context Enhancement:")
    enhancer = WorkHistoryContextEnhancer()
    
    test_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience']
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'B2B', 'clean_energy', 'scaling']
        }
    ]
    
    enhanced = enhancer.enhance_case_studies_batch(test_case_studies)
    
    print("✅ Work History Context Enhancement Results:")
    for enhanced_case_study in enhanced:
        print(f"  {enhanced_case_study.case_study_id.upper()}:")
        print(f"    Original tags: {enhanced_case_study.original_tags}")
        print(f"    Enhanced tags: {enhanced_case_study.enhanced_tags}")
        print(f"    Confidence: {enhanced_case_study.confidence_score:.2f}")
    
    # Test agent initialization with work history enhancement
    print("\n📋 Testing Agent Integration:")
    try:
        agent = CoverLetterAgent()
        print("✅ Agent initialized successfully")
        
        # Test case study selection with enhanced context
        print("\n📋 Testing Case Study Selection with Enhanced Context:")
        job_keywords = ['product manager', 'growth', 'leadership']
        case_studies = agent.get_case_studies(job_keywords)
        
        print(f"✅ Found {len(case_studies)} case studies")
        for case_study in case_studies:
            print(f"  - {case_study.get('name', case_study.get('id', 'Unknown'))}")
        
        print("\n✅ Phase 3 Integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Agent integration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_phase3_integration() 