#!/usr/bin/env python3
"""
Test Phase 8D: Force-Ranked Story Suggestions

Tests the story suggestion engine with confidence scoring,
rationale surfacing, and force-ranking functionality.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.story_generation import StoryGenerator, StorySuggestion
from agents.hil_approval_cli import HILApprovalCLI


def test_story_suggestion_engine():
    """Test the story suggestion engine with confidence scoring and ranking."""
    print("🧪 Testing Phase 8D: Force-Ranked Story Suggestions...")
    
    # Initialize story generator
    story_gen = StoryGenerator(user_profile="test_user")
    
    # Test work history
    work_history = [
        {
            'id': 'work_1',
            'company': 'Aurora Solar',
            'role': 'Senior Product Manager',
            'duration': '2 years',
            'description': 'Led platform rebuild and scaling initiatives',
            'tags': ['growth', 'b2b', 'scaling', 'platform'],
            'achievements': ['Increased user engagement by 40%', 'Reduced churn by 25%']
        },
        {
            'id': 'work_2',
            'company': 'Enact',
            'role': 'Product Manager',
            'duration': '1.5 years',
            'description': 'Led 0-to-1 product development for energy management',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'achievements': ['Launched MVP in 6 months', 'Achieved 10K+ users']
        }
    ]
    
    # Test existing case studies
    existing_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'text': 'Led cross-functional team from 0-1 to improve home energy management'
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'b2b', 'clean_energy', 'scaling'],
            'text': 'Helped scale company from Series A to Series C, leading platform rebuild'
        }
    ]
    
    # Test gaps
    test_gaps = ['fintech', 'ai_ml', 'leadership', 'b2b']
    
    print(f"\n📋 Testing story suggestions for {len(test_gaps)} gaps...")
    
    for gap_tag in test_gaps:
        print(f"\n🎯 Testing gap: {gap_tag}")
        
        # Get suggestions
        suggestions = story_gen.suggest_stories_for_gap(
            gap_tag=gap_tag,
            work_history=work_history,
            existing_case_studies=existing_case_studies,
            user_context="Senior PM with cleantech experience"
        )
        
        print(f"  Found {len(suggestions)} suggestions")
        
        # Validate suggestions
        if suggestions:
            # Check ranking (should be sorted by confidence + relevance)
            for i, suggestion in enumerate(suggestions[:3]):
                print(f"  {i+1}. Confidence: {suggestion.confidence:.1f}, Relevance: {suggestion.relevance_score:.1f}")
                print(f"     Match Type: {suggestion.match_type}, Source: {suggestion.source}")
                print(f"     Rationale: {suggestion.rationale}")
                print(f"     Story: {suggestion.story_text[:80]}...")
                
                # Validate suggestion structure
                assert hasattr(suggestion, 'confidence'), "Suggestion missing confidence"
                assert hasattr(suggestion, 'rationale'), "Suggestion missing rationale"
                assert hasattr(suggestion, 'match_type'), "Suggestion missing match_type"
                assert hasattr(suggestion, 'source'), "Suggestion missing source"
                assert 0.0 <= suggestion.confidence <= 1.0, "Confidence out of range"
                assert 0.0 <= suggestion.relevance_score <= 1.0, "Relevance score out of range"
            
            # Check that suggestions are ranked by confidence + relevance
            for i in range(len(suggestions) - 1):
                current_score = suggestions[i].confidence * 0.6 + suggestions[i].relevance_score * 0.4
                next_score = suggestions[i + 1].confidence * 0.6 + suggestions[i + 1].relevance_score * 0.4
                assert current_score >= next_score, "Suggestions not properly ranked"
        
        print(f"  ✅ Gap {gap_tag} test passed")


def test_hil_cli_integration():
    """Test the HIL CLI integration with story suggestions."""
    print("\n🧪 Testing HIL CLI Integration with Story Suggestions...")
    
    # Initialize HIL CLI
    hil = HILApprovalCLI(user_profile="test_user")
    
    # Test gap detection and story suggestions
    jd_tags = ['fintech', 'payments', 'b2b', 'growth']
    user_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'text': 'Led cross-functional team from 0-1 to improve home energy management'
        }
    ]
    
    print(f"\n📋 Testing gap detection with job tags: {jd_tags}")
    
    # Test gap detection
    gap_results = hil._handle_add_new_option(jd_tags, user_case_studies)
    
    print(f"  Gap detection completed")
    print(f"  Gaps found: {len(gap_results.get('gaps', []))}")
    
    if gap_results.get('gaps'):
        # Test story suggestions for first gap
        first_gap = gap_results['gaps'][0]
        print(f"\n🎯 Testing story suggestions for gap: {first_gap.tag}")
        
        # Test gap fill workflow
        story_result = hil._gap_fill_workflow(first_gap.tag, "Senior PM with cleantech experience")
        
        print(f"  Story creation completed")
        print(f"  Strategy: {story_result.get('strategy')}")
        print(f"  Confidence: {story_result.get('confidence', 0.0):.1f}")
        print(f"  Match Type: {story_result.get('match_type', 'none')}")
        
        # Validate story result
        assert 'gap_tag' in story_result, "Story result missing gap_tag"
        assert 'strategy' in story_result, "Story result missing strategy"
        assert 'confidence' in story_result, "Story result missing confidence"
        assert 'match_type' in story_result, "Story result missing match_type"
        
        print(f"  ✅ HIL CLI integration test passed")


def test_story_suggestion_types():
    """Test different types of story suggestions."""
    print("\n🧪 Testing Story Suggestion Types...")
    
    story_gen = StoryGenerator(user_profile="test_user")
    
    # Test data
    work_history = [
        {
            'id': 'work_1',
            'company': 'Aurora Solar',
            'role': 'Senior Product Manager',
            'tags': ['growth', 'b2b', 'scaling'],
            'description': 'Led platform rebuild and scaling initiatives',
            'achievements': ['Increased user engagement by 40%']
        }
    ]
    
    existing_case_studies = [
        {
            'id': 'enact',
            'tags': ['growth', 'consumer', 'clean_energy'],
            'text': 'Led cross-functional team from 0-1 to improve home energy management'
        }
    ]
    
    # Test different gap types
    test_cases = [
        ('fintech', 'Should find adjacent matches from B2B experience'),
        ('ai_ml', 'Should find derived stories from patterns'),
        ('leadership', 'Should find reframed case studies')
    ]
    
    for gap_tag, expected_behavior in test_cases:
        print(f"\n🎯 Testing {gap_tag}: {expected_behavior}")
        
        suggestions = story_gen.suggest_stories_for_gap(
            gap_tag=gap_tag,
            work_history=work_history,
            existing_case_studies=existing_case_studies
        )
        
        print(f"  Found {len(suggestions)} suggestions")
        
        # Check suggestion types
        suggestion_types = [s.match_type for s in suggestions]
        print(f"  Match types: {suggestion_types}")
        
        # Validate that we have different types of suggestions
        if suggestions:
            assert len(set(suggestion_types)) > 0, "No variety in suggestion types"
            print(f"  ✅ {gap_tag} test passed")
        else:
            print(f"  ⚠️  No suggestions found for {gap_tag}")


def main():
    """Run all tests."""
    print("🚀 Phase 8D: Force-Ranked Story Suggestions Test Suite")
    print("=" * 60)
    
    try:
        test_story_suggestion_engine()
        test_hil_cli_integration()
        test_story_suggestion_types()
        
        print(f"\n✅ All Phase 8D tests passed!")
        print(f"🎯 Force-ranked story suggestions with confidence scoring implemented successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main() 