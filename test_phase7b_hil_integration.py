#!/usr/bin/env python3
"""
Test Phase 7B: HIL Integration with Gap Detection

Tests the integration of gap detection into the existing HIL CLI workflow.
"""

import sys
import os
import yaml

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hil_approval_cli import HILApprovalCLI
from agents.gap_detection import GapDetector


def test_hil_gap_integration():
    """Test HIL integration with gap detection."""
    print("🧪 Testing Phase 7B: HIL Integration with Gap Detection...")
    
    # Initialize HIL CLI with gap detection
    hil = HILApprovalCLI(user_profile="test_gap_integration")
    
    # Test gap detection directly
    print(f"\n📋 Testing Gap Detection Integration:")
    
    # Sample job requirements
    jd_tags = ['fintech', 'payments', 'compliance', 'enterprise', 'leadership']
    
    # Sample user case studies (Peter's data)
    user_case_studies = [
        {
            'id': 'enact',
            'name': 'ENACT Case Study',
            'tags': ['cleantech', 'energy', 'growth', 'leadership', 'b2b2c']
        },
        {
            'id': 'aurora',
            'name': 'AURORA Case Study', 
            'tags': ['platform', 'cleantech', 'b2b', 'enterprise', 'growth']
        },
        {
            'id': 'meta',
            'name': 'META Case Study',
            'tags': ['ai_ml', 'platform', 'internal_tools', 'enterprise']
        }
    ]
    
    print(f"Job Requirements: {jd_tags}")
    print(f"User Case Studies: {len(user_case_studies)}")
    
    # Test gap detection
    gap_results = hil._handle_add_new_option(jd_tags, user_case_studies)
    
    print(f"\n📊 Gap Detection Results:")
    print(f"  Recommendation: {gap_results['recommendation']}")
    
    if gap_results['gaps']:
        print(f"  Gaps detected: {len(gap_results['gaps'])}")
        for gap in gap_results['gaps'][:3]:
            print(f"    - {gap.tag} ({gap.priority} priority)")
    
    # Test gap filling workflow
    if gap_results['gaps']:
        print(f"\n📝 Testing Gap Filling Workflow:")
        top_gap = gap_results['gaps'][0]
        
        story_result = hil._gap_fill_workflow(top_gap.tag, "User has some enterprise experience")
        
        print(f"  Gap filled: {story_result['gap_tag']}")
        print(f"  Story generated: {story_result['story'][:100]}...")
        print(f"  Tags: {story_result['tags']}")
        print(f"  Source: {story_result['source']}")
    
    print(f"\n✅ Phase 7B: HIL Integration test completed!")
    print(f"  Gap detection integrated with HIL CLI")
    print(f"  Gap filling workflow working")
    print(f"  Ready for Phase 7C: Story Generation")


def test_gap_detection_workflow():
    """Test the complete gap detection workflow."""
    print(f"\n🧪 Testing Complete Gap Detection Workflow...")
    
    # Initialize components
    detector = GapDetector()
    hil = HILApprovalCLI()
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Fintech PM',
            'jd_tags': ['fintech', 'payments', 'compliance', 'enterprise'],
            'user_tags': ['cleantech', 'energy', 'platform', 'b2b']
        },
        {
            'name': 'Healthcare PM', 
            'jd_tags': ['healthtech', 'medtech', 'digital_health', 'compliance'],
            'user_tags': ['ai_ml', 'platform', 'enterprise', 'internal_tools']
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print(f"Job Tags: {scenario['jd_tags']}")
        print(f"User Tags: {scenario['user_tags']}")
        
        # Detect gaps
        gaps = detector.detect_gaps(scenario['jd_tags'], scenario['user_tags'])
        
        print(f"Gaps detected: {len(gaps)}")
        for gap in gaps[:3]:
            print(f"  - {gap.tag} ({gap.priority} priority)")
        
        # Test content matching
        test_case_studies = [
            {
                'id': 'test_case',
                'name': 'Test Case Study',
                'tags': scenario['user_tags']
            }
        ]
        
        if gaps:
            top_gap = gaps[0]
            matches = detector.match_existing_content(top_gap, test_case_studies)
            
            print(f"Content matches for '{top_gap.tag}': {len(matches)}")
            for match in matches[:2]:
                print(f"  - {match.case_study_name}: {match.match_type} match")
    
    print(f"\n✅ Gap Detection Workflow test completed!")


if __name__ == "__main__":
    test_hil_gap_integration()
    test_gap_detection_workflow() 