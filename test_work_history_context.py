#!/usr/bin/env python3
"""
Test Work History Context Enhancement
===================================

Tests the work history context enhancement functionality to ensure
parent-child relationships are preserved and tag inheritance works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.work_history_context import WorkHistoryContextEnhancer


def test_work_history_context_enhancement():
    """Test the work history context enhancement functionality."""
    print("🧪 Testing Work History Context Enhancement...")
    
    enhancer = WorkHistoryContextEnhancer()
    
    # Test case studies with known parent relationships
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
        },
        {
            'id': 'meta',
            'name': 'Meta Explainable AI Case Study',
            'tags': ['AI', 'ML', 'trust', 'internal_tools', 'explainable']
        },
        {
            'id': 'samsung',
            'name': 'Samsung Customer Care Case Study',
            'tags': ['growth', 'ux', 'b2c', 'public', 'onboarding', 'usability', 'mobile', 'support', 'engagement']
        }
    ]
    
    print("\n📋 Testing case study enhancement:")
    enhanced = enhancer.enhance_case_studies_batch(test_case_studies)
    
    print("\n📊 Results:")
    for enhanced_case_study in enhanced:
        print(f"\n  {enhanced_case_study.case_study_id.upper()}:")
        print(f"    Original tags: {enhanced_case_study.original_tags}")
        print(f"    Inherited tags: {enhanced_case_study.inherited_tags}")
        print(f"    Semantic tags: {enhanced_case_study.semantic_tags}")
        print(f"    Enhanced tags: {enhanced_case_study.enhanced_tags}")
        print(f"    Confidence: {enhanced_case_study.confidence_score:.2f}")
        print(f"    Tag provenance: {enhanced_case_study.tag_provenance}")
        print(f"    Tag weights: {enhanced_case_study.tag_weights}")
        
        if enhanced_case_study.parent_context:
            print(f"    Parent: {enhanced_case_study.parent_context['company']}")
            print(f"    Role: {enhanced_case_study.parent_context['role']}")
    
    # Test specific scenarios
    print("\n🎯 Testing specific scenarios:")
    
    # Test 1: Enact should inherit cleantech context
    enact_enhanced = next(e for e in enhanced if e.case_study_id == 'enact')
    print(f"\n  Test 1 - Enact cleantech inheritance:")
    print(f"    Expected: cleantech in inherited tags")
    print(f"    Actual: {'cleantech' in enact_enhanced.inherited_tags}")
    print(f"    Inherited tags: {enact_enhanced.inherited_tags}")
    
    # Test 2: Aurora should inherit startup context
    aurora_enhanced = next(e for e in enhanced if e.case_study_id == 'aurora')
    print(f"\n  Test 2 - Aurora startup inheritance:")
    print(f"    Expected: startup in inherited tags")
    print(f"    Actual: {'startup' in aurora_enhanced.inherited_tags}")
    print(f"    Inherited tags: {aurora_enhanced.inherited_tags}")
    
    # Test 3: Meta should inherit enterprise context
    meta_enhanced = next(e for e in enhanced if e.case_study_id == 'meta')
    print(f"\n  Test 3 - Meta enterprise inheritance:")
    print(f"    Expected: enterprise in inherited tags")
    print(f"    Actual: {'enterprise' in meta_enhanced.inherited_tags}")
    print(f"    Inherited tags: {meta_enhanced.inherited_tags}")
    
    # Test 4: Samsung should inherit consumer context
    samsung_enhanced = next(e for e in enhanced if e.case_study_id == 'samsung')
    print(f"\n  Test 4 - Samsung consumer inheritance:")
    print(f"    Expected: consumer in inherited tags")
    print(f"    Actual: {'consumer' in samsung_enhanced.inherited_tags}")
    print(f"    Inherited tags: {samsung_enhanced.inherited_tags}")
    
    # Test 5: Semantic tag matching
    print(f"\n  Test 5 - Semantic tag matching:")
    print(f"    Meta semantic tags: {meta_enhanced.semantic_tags}")
    print(f"    Expected: platform, enterprise_systems in semantic tags")
    print(f"    Actual: {'platform' in meta_enhanced.semantic_tags or 'enterprise_systems' in meta_enhanced.semantic_tags}")
    
    # Test 6: Confidence scores
    print(f"\n  Test 6 - Confidence scores:")
    for enhanced_case_study in enhanced:
        print(f"    {enhanced_case_study.case_study_id}: {enhanced_case_study.confidence_score:.2f}")
        print(f"      Expected: > 0.5 for cases with parent context")
        print(f"      Actual: {enhanced_case_study.confidence_score > 0.5}")
    
    # Test 7: Tag provenance and weighting
    print(f"\n  Test 7 - Tag provenance and weighting:")
    for enhanced_case_study in enhanced:
        print(f"    {enhanced_case_study.case_study_id}:")
        print(f"      Direct tags: {[tag for tag, source in enhanced_case_study.tag_provenance.items() if source == 'direct']}")
        print(f"      Inherited tags: {[tag for tag, source in enhanced_case_study.tag_provenance.items() if source == 'inherited']}")
        print(f"      Semantic tags: {[tag for tag, source in enhanced_case_study.tag_provenance.items() if source == 'semantic']}")
        print(f"      Average weight: {sum(enhanced_case_study.tag_weights.values()) / len(enhanced_case_study.tag_weights):.2f}")
    
    # Test 8: Tag suppression rules
    print(f"\n  Test 8 - Tag suppression rules:")
    suppressed_tags = ['frontend', 'backend', 'mobile', 'web', 'marketing', 'sales']
    for enhanced_case_study in enhanced:
        inherited_suppressed = [tag for tag in enhanced_case_study.inherited_tags if tag in suppressed_tags]
        print(f"    {enhanced_case_study.case_study_id}: {len(inherited_suppressed)} suppressed tags inherited")
        print(f"      Expected: 0 suppressed tags inherited")
        print(f"      Actual: {len(inherited_suppressed) == 0}")
    
    # Summary
    print("\n📈 Summary:")
    total_enhanced = len(enhanced)
    with_parent_context = len([e for e in enhanced if e.parent_context])
    with_inherited_tags = len([e for e in enhanced if e.inherited_tags])
    with_semantic_tags = len([e for e in enhanced if e.semantic_tags])
    
    print(f"  Total case studies: {total_enhanced}")
    print(f"  With parent context: {with_parent_context}")
    print(f"  With inherited tags: {with_inherited_tags}")
    print(f"  With semantic tags: {with_semantic_tags}")
    print(f"  Average confidence: {sum(e.confidence_score for e in enhanced) / len(enhanced):.2f}")
    
    print("\n✅ Work History Context Enhancement test completed!")


if __name__ == "__main__":
    test_work_history_context_enhancement() 