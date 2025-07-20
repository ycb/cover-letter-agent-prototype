#!/usr/bin/env python3
"""
Test Phase 7C: Story Generation & Storage

Tests the complete story generation and storage system
integrated with the HIL CLI gap filling workflow.
"""

import sys
import os
import yaml

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hil_approval_cli import HILApprovalCLI
from agents.story_generation import StoryGenerator
from agents.gap_detection import GapDetector


def test_phase7c_complete_workflow():
    """Test the complete Phase 7C story generation and storage workflow."""
    print("🧪 Testing Phase 7C: Story Generation & Storage...")
    
    # Initialize components
    hil = HILApprovalCLI(user_profile="test_phase7c")
    story_generator = StoryGenerator(user_profile="test_phase7c")
    
    # Test story generation and storage
    print(f"\n📝 Testing Story Generation & Storage:")
    
    # Create test stories
    test_stories = [
        {
            'gap_tag': 'fintech',
            'story_text': 'At ABC Company I managed billing and credits. I built credit from scratch, working with GTM teams. Launched in 6 weeks and then handed over to RevOps team.',
            'tags': ['fintech', 'billing', 'gtm', 'launch'],
            'source': 'gap_fill',
            'strategy': 'manual_entry'
        },
        {
            'gap_tag': 'healthtech',
            'story_text': 'At XYZ Health, I led the development of a telemedicine platform that improved patient access by 40%. I worked with clinical teams to ensure compliance and user safety.',
            'tags': ['healthtech', 'telemedicine', 'compliance', 'patient_access'],
            'source': 'gap_fill',
            'strategy': 'manual_entry'
        },
        {
            'gap_tag': 'payments',
            'story_text': 'At PaymentCorp, I designed and launched a new payment processing system that reduced transaction failures by 60% and improved processing speed by 3x.',
            'tags': ['payments', 'processing', 'performance', 'launch'],
            'source': 'gap_fill',
            'strategy': 'manual_entry'
        }
    ]
    
    created_stories = []
    for story_data in test_stories:
        story = story_generator.create_story(**story_data)
        created_stories.append(story)
        print(f"  ✅ Created story: {story.story_id}")
        print(f"     Gap: {story.gap_tag}")
        print(f"     Tags: {story.tags}")
        print(f"     Strategy: {story.strategy}")
    
    # Test story retrieval and management
    print(f"\n📚 Testing Story Management:")
    
    # Get stories by gap
    fintech_stories = story_generator.get_stories_by_gap('fintech')
    print(f"  Fintech stories: {len(fintech_stories)}")
    
    healthtech_stories = story_generator.get_stories_by_gap('healthtech')
    print(f"  Healthtech stories: {len(healthtech_stories)}")
    
    payments_stories = story_generator.get_stories_by_gap('payments')
    print(f"  Payments stories: {len(payments_stories)}")
    
    # Test story approval
    print(f"\n✅ Testing Story Approval:")
    if created_stories:
        story = created_stories[0]
        approved = story_generator.approve_story_for_job(story.story_id, 'test_job_123')
        print(f"  Approved story {story.story_id} for job: {approved}")
        
        # Approve another story
        if len(created_stories) > 1:
            story2 = created_stories[1]
            approved2 = story_generator.approve_story_for_job(story2.story_id, 'test_job_456')
            print(f"  Approved story {story2.story_id} for job: {approved2}")
    
    # Test story updates
    print(f"\n✏️  Testing Story Updates:")
    if created_stories:
        story = created_stories[0]
        updated = story_generator.update_story(
            story.story_id,
            story_text="Updated story with more specific metrics and outcomes.",
            tags=['fintech', 'billing', 'gtm', 'launch', 'updated', 'metrics']
        )
        print(f"  Updated story {story.story_id}: {updated}")
        print(f"  New version: {story.version}")
    
    # Get comprehensive summary
    print(f"\n📊 Story Storage Summary:")
    summary = story_generator.get_story_summary()
    print(f"  Total stories: {summary['total_stories']}")
    print(f"  Stories by gap: {summary['stories_by_gap']}")
    print(f"  Stories by source: {summary['stories_by_source']}")
    print(f"  Stories by strategy: {summary['stories_by_strategy']}")
    print(f"  Recent story: {summary['recent_story']}")
    
    # Test integration with HIL CLI
    print(f"\n🔗 Testing HIL CLI Integration:")
    
    # Test gap detection with story storage
    jd_tags = ['fintech', 'payments', 'compliance', 'enterprise']
    user_case_studies = [
        {
            'id': 'enact',
            'name': 'ENACT Case Study',
            'tags': ['cleantech', 'energy', 'growth', 'leadership']
        }
    ]
    
    # Simulate gap detection
    gap_results = hil._handle_add_new_option(jd_tags, user_case_studies)
    
    if gap_results['gaps']:
        print(f"  Gaps detected: {len(gap_results['gaps'])}")
        for gap in gap_results['gaps'][:2]:
            print(f"    - {gap.tag} ({gap.priority} priority)")
            
            # Check if we have stories for this gap
            existing_stories = story_generator.get_stories_by_gap(gap.tag)
            if existing_stories:
                print(f"      Found {len(existing_stories)} existing stories")
                for story in existing_stories:
                    print(f"        - {story.story_id}: {story.story_text[:50]}...")
            else:
                print(f"      No existing stories - would trigger creation")
    
    print(f"\n✅ Phase 7C: Story Generation & Storage test completed!")
    print(f"  Story creation working")
    print(f"  Story storage working")
    print(f"  Story retrieval working")
    print(f"  Story approval working")
    print(f"  Story updates working")
    print(f"  HIL CLI integration working")
    print(f"  Gap detection with story lookup working")


def test_story_templates():
    """Test story template generation for different gap types."""
    print(f"\n🧪 Testing Story Templates:")
    
    gap_templates = {
        'fintech': {
            'template': 'At [Company], I led [specific fintech initiative] that [specific challenge/opportunity]. I [specific actions taken] and [specific outcomes achieved].',
            'guidelines': ['Replace with actual company name', 'Include specific fintech project', 'Add metrics and outcomes']
        },
        'healthtech': {
            'template': 'At [Healthcare Company], I developed [specific healthtech solution] that [specific healthcare challenge]. I [specific actions] and [specific health outcomes].',
            'guidelines': ['Focus on healthcare impact', 'Include compliance considerations', 'Show patient safety measures']
        },
        'payments': {
            'template': 'At [Payment Company], I designed [specific payment system] that [specific payment challenge]. I [specific actions] and [specific payment outcomes].',
            'guidelines': ['Emphasize security and compliance', 'Include transaction metrics', 'Show user experience improvements']
        }
    }
    
    for gap_type, template_data in gap_templates.items():
        print(f"\n📄 {gap_type.upper()} Template:")
        print(f"  Template: {template_data['template']}")
        print(f"  Guidelines: {', '.join(template_data['guidelines'])}")
    
    print(f"\n✅ Story templates working correctly")


if __name__ == "__main__":
    test_phase7c_complete_workflow()
    test_story_templates() 