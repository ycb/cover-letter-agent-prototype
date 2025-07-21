#!/usr/bin/env python3
"""
Test Phase 6: Human-in-the-Loop (HIL) CLI System
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.hil_approval_cli import HILApprovalCLI
from agents.cover_letter_agent import CoverLetterAgent

def test_phase6_hil_system():
    """Test the complete Phase 6 HIL system."""
    print("🧪 Testing Phase 6: Human-in-the-Loop (HIL) CLI System...")
    
    # Initialize the cover letter agent
    agent = CoverLetterAgent()
    
    # Test job description
    jd_text = """
    Senior Product Manager - Cleantech
    We're looking for a Senior Product Manager to lead our cleantech platform.
    Requirements:
    - 5+ years product management experience
    - Experience with energy markets and DER
    - Strong analytical and strategic thinking
    - Experience with B2B SaaS products
    """
    
    print("\n📋 Step 1: Job Description Parsing")
    jd_data = agent.parse_job_description(jd_text)
    print(f"  Parsed {len(jd_data.get('tags', []))} job tags")
    
    print("\n📋 Step 2: Case Study Selection")
    result = agent.select_case_studies(jd_data)
    print(f"  Selected {len(result.selected_case_studies)} case studies for HIL review")
    
    # Add LLM scores to case studies for HIL
    for case_study in result.selected_case_studies:
        case_study['llm_score'] = 8.5  # Simulated LLM score
        case_study['llm_reasoning'] = "Strong cleantech match; highlights post-sale engagement and DER"
    
    print("\n📋 Step 3: HIL Approval Workflow (Simulated)")
    
    # Simulate HIL approval workflow
    approved_case_studies, feedback_list = agent.hil_approval_cli(
        result.selected_case_studies,
        jd_data.get('tags', [])
    )
    
    print(f"\n📊 HIL Results:")
    print(f"  Approved: {len(approved_case_studies)} case studies")
    print(f"  Feedback collected: {len(feedback_list)} feedback entries")
    
    # Test variant saving
    print("\n📋 Step 4: Variant Management")
    for case_study in approved_case_studies[:1]:  # Test with first case study
        agent.save_case_study_variant(
            case_study['id'],
            case_study,
            "user_approved",
            jd_data.get('tags', [])
        )
    
    # Test refinement suggestions
    print("\n📋 Step 5: Refinement Suggestions")
    for case_study in approved_case_studies[:1]:
        suggestions = agent.suggest_refinements(case_study, jd_data.get('tags', []))
        print(f"  Generated {len(suggestions)} refinement suggestions")
    
    # Test variant retrieval
    print("\n📋 Step 6: Variant Retrieval")
    for case_study in approved_case_studies[:1]:
        variants = agent.get_approved_variants(case_study['id'])
        print(f"  Retrieved {len(variants)} variants for case study {case_study['id']}")
    
    # Validate results
    print("\n📋 Step 7: Validation")
    feedback_collected = len(feedback_list) > 0
    variants_saved = any(len(agent.get_approved_variants(cs['id'])) > 0 for cs in result.selected_case_studies)
    
    print(f"  Feedback collected: {'✅' if feedback_collected else '❌'}")
    print(f"  Variants saved: {'✅' if variants_saved else '❌'}")
    
    # Overall success
    success = feedback_collected and variants_saved
    print(f"\n✅ Phase 6: HIL CLI System test completed!")
    print(f"  Overall success: {'✅' if success else '❌'}")
    
    return success

if __name__ == "__main__":
    test_phase6_hil_system() 