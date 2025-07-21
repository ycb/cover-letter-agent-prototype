#!/usr/bin/env python3
"""
Test Phase 7A: Core Gap Detection

Tests the gap detection system with real job descriptions
and user case studies to validate gap identification.
"""

import sys
import os
import yaml

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.gap_detection import GapDetector
from agents.hybrid_case_study_selection import HybridCaseStudySelector
from agents.work_history_context import WorkHistoryContextEnhancer


def test_gap_detection_with_real_data():
    """Test gap detection with real job descriptions and user data."""
    print("🧪 Testing Phase 7A: Core Gap Detection with Real Data...")
    
    # Initialize components
    detector = GapDetector()
    enhancer = WorkHistoryContextEnhancer()
    selector = HybridCaseStudySelector()
    
    # Load Peter's real case study data
    peter_blurbs_path = "users/peter/blurbs.yaml"
    
    try:
        with open(peter_blurbs_path, 'r') as f:
            peter_blurbs = yaml.safe_load(f)
        
        # Extract real case studies
        real_case_studies = []
        for case_study in peter_blurbs.get('examples', []):
            real_case_studies.append({
                'id': case_study['id'],
                'name': f"{case_study['id'].upper()} Case Study",
                'tags': case_study['tags'],
                'text': case_study['text'],
                'description': case_study['text'][:100] + "..."
            })
        
        print(f"✅ Loaded {len(real_case_studies)} real case studies")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'L5 Cleantech PM',
                'jd_tags': ['ai_ml', 'platform', 'enterprise', 'leadership', 'growth', 'cleantech', 'energy'],
                'job_description': 'Senior Product Manager at cleantech startup focusing on energy management'
            },
            {
                'name': 'L4 AI/ML PM',
                'jd_tags': ['ai_ml', 'machine_learning', 'platform', 'data_analysis', 'enterprise', 'leadership'],
                'job_description': 'AI/ML Product Manager at tech company'
            },
            {
                'name': 'L3 Consumer PM',
                'jd_tags': ['b2c', 'mobile', 'growth', 'user_experience', 'analytics', 'engagement'],
                'job_description': 'Consumer Product Manager at mobile app company'
            },
            {
                'name': 'L5 Fintech PM',
                'jd_tags': ['fintech', 'payments', 'compliance', 'regtech', 'banking', 'enterprise', 'leadership'],
                'job_description': 'Senior PM at fintech company focusing on payments and compliance'
            },
            {
                'name': 'L4 Healthcare PM',
                'jd_tags': ['healthtech', 'medtech', 'digital_health', 'telemedicine', 'compliance', 'enterprise'],
                'job_description': 'Healthcare Product Manager at digital health company'
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            print(f"Job Description: {scenario['job_description']}")
            print(f"Required Tags: {scenario['jd_tags']}")
            
            # Enhance case studies with work history context
            enhanced_case_studies = enhancer.enhance_case_studies_batch(real_case_studies)
            
            # Extract all user tags from enhanced case studies
            user_tags = set()
            for enhanced in enhanced_case_studies:
                user_tags.update(enhanced.enhanced_tags)
            
            print(f"User Experience Tags: {len(user_tags)} total")
            print(f"Sample Tags: {list(user_tags)[:10]}...")
            
            # Detect gaps
            gaps = detector.detect_gaps(scenario['jd_tags'], list(user_tags))
            
            print(f"\n📊 Gap Detection Results:")
            print(f"  Total gaps: {len(gaps)}")
            
            # Show top gaps
            for i, gap in enumerate(gaps[:3], 1):
                print(f"  {i}. {gap.tag} ({gap.category}) - {gap.priority} priority")
                print(f"     Coverage: {gap.user_coverage} (confidence: {gap.confidence:.2f})")
            
            # Generate summary
            summary = detector.get_gap_summary(gaps)
            print(f"\n📈 Gap Summary:")
            print(f"  High priority: {summary['high_priority']}")
            print(f"  Medium priority: {summary['medium_priority']}")
            print(f"  Low priority: {summary['low_priority']}")
            print(f"  Categories: {summary['categories']}")
            
            # Test content matching for top gap
            if gaps:
                top_gap = gaps[0]
                print(f"\n🔍 Content Matching for '{top_gap.tag}':")
                
                # Convert enhanced case studies to dict format
                enhanced_dicts = []
                for enhanced in enhanced_case_studies:
                    enhanced_dict = {
                        'id': enhanced.case_study_id,
                        'name': enhanced.case_study_id.upper() + ' Case Study',
                        'tags': enhanced.enhanced_tags
                    }
                    enhanced_dicts.append(enhanced_dict)
                
                matches = detector.match_existing_content(top_gap, enhanced_dicts)
                
                if matches:
                    for match in matches[:3]:  # Show top 3 matches
                        print(f"  - {match.case_study_name}: {match.match_type} match")
                        print(f"    Confidence: {match.confidence:.2f}")
                        print(f"    Rationale: {match.rationale}")
                else:
                    print(f"  No existing content matches found for '{top_gap.tag}'")
                    print(f"  This gap would need new story creation")
        
        print(f"\n✅ Phase 7A: Core Gap Detection test completed!")
        print(f"  Tested {len(test_scenarios)} job scenarios")
        print(f"  Used {len(real_case_studies)} real case studies")
        print(f"  Gap detection working correctly")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find Peter's blurbs file at {peter_blurbs_path}")
        print("Running with mock data instead...")
        test_gap_detection_mock()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Running with mock data instead...")
        test_gap_detection_mock()


def test_gap_detection_mock():
    """Test gap detection with mock data."""
    print("🧪 Testing Phase 7A: Core Gap Detection (Mock Data)...")
    
    detector = GapDetector()
    
    # Mock test data
    jd_tags = ['ai_ml', 'platform', 'enterprise', 'leadership', 'growth']
    user_tags = ['mobile', 'b2c', 'ux', 'data_analysis', 'team_lead']
    
    print(f"Job Description Tags: {jd_tags}")
    print(f"User Experience Tags: {user_tags}")
    
    # Detect gaps
    gaps = detector.detect_gaps(jd_tags, user_tags)
    
    print(f"\n📊 Gap Detection Results:")
    print(f"  Total gaps detected: {len(gaps)}")
    
    for gap in gaps:
        print(f"  - {gap.tag} ({gap.category}) - {gap.priority} priority")
        print(f"    Coverage: {gap.user_coverage} (confidence: {gap.confidence:.2f})")
    
    # Generate summary
    summary = detector.get_gap_summary(gaps)
    print(f"\n📈 Gap Summary:")
    print(f"  High priority: {summary['high_priority']}")
    print(f"  Medium priority: {summary['medium_priority']}")
    print(f"  Low priority: {summary['low_priority']}")
    print(f"  Categories: {summary['categories']}")
    
    print(f"\n✅ Phase 7A: Core Gap Detection (Mock) test completed!")


if __name__ == "__main__":
    test_gap_detection_with_real_data() 