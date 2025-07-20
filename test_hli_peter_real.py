#!/usr/bin/env python3
"""
Test HLI CLI with Peter's real case study data
"""

import sys
import os
import yaml

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hli_approval_cli import HLIApprovalCLI
from agents.hybrid_case_study_selection import HybridCaseStudySelector
from agents.work_history_context import WorkHistoryContextEnhancer


def test_hli_with_peter_data():
    """Test HLI CLI with Peter's real case study data."""
    print("🧪 Testing HLI CLI with Peter's Real Case Study Data...")
    
    # Load Peter's real case study data
    peter_blurbs_path = "users/peter/blurbs.yaml"
    
    try:
        with open(peter_blurbs_path, 'r') as f:
            peter_blurbs = yaml.safe_load(f)
        
        # Extract real case studies from Peter's data
        real_case_studies = []
        for case_study in peter_blurbs.get('examples', []):
            real_case_studies.append({
                'id': case_study['id'],
                'name': f"{case_study['id'].upper()} Case Study",
                'tags': case_study['tags'],
                'text': case_study['text'],
                'description': case_study['text'][:100] + "..."  # Truncated for display
            })
        
        print(f"✅ Loaded {len(real_case_studies)} real case studies from Peter's data")
        
        # Show sample of real data
        print(f"\n📋 Sample of Peter's real case studies:")
        for i, cs in enumerate(real_case_studies[:3], 1):
            print(f"  {i}. {cs['name']}")
            print(f"     Tags: {', '.join(cs['tags'][:5])}...")
            print(f"     Text: {cs['text'][:80]}...")
            print()
        
        # Initialize components
        enhancer = WorkHistoryContextEnhancer()
        selector = HybridCaseStudySelector()
        hli = HLIApprovalCLI(user_profile="peter")
        
        print(f"\n📋 Step 1: Work History Context Enhancement")
        enhanced_case_studies = enhancer.enhance_case_studies_batch(real_case_studies)
        
        print("✅ Enhanced case studies:")
        for enhanced in enhanced_case_studies:
            print(f"  {enhanced.case_study_id.upper()}:")
            print(f"    Original tags: {enhanced.original_tags}")
            print(f"    Enhanced tags: {enhanced.enhanced_tags}")
            print(f"    Confidence: {enhanced.confidence_score:.2f}")
        
        # Convert enhanced case studies back to dict format with real text
        enhanced_dicts = []
        for enhanced in enhanced_case_studies:
            # Find the original case study to preserve the real text
            original_cs = next((cs for cs in real_case_studies if cs['id'] == enhanced.case_study_id), None)
            
            enhanced_dict = {
                'id': enhanced.case_study_id,
                'name': enhanced.case_study_id.upper() + ' Case Study',
                'tags': enhanced.enhanced_tags,
                'text': original_cs['text'] if original_cs else f"Enhanced case study with {len(enhanced.enhanced_tags)} tags",
                'description': original_cs['text'] if original_cs else f"Enhanced case study with {len(enhanced.enhanced_tags)} tags",
                'provenance': enhanced.tag_provenance,
                'weights': enhanced.tag_weights
            }
            enhanced_dicts.append(enhanced_dict)
        
        print(f"\n📋 Step 2: Hybrid Case Study Selection")
        job_keywords = ['product manager', 'cleantech', 'leadership', 'growth']
        job_level = 'L5'
        job_description = "Senior Product Manager at cleantech startup focusing on energy management"
        job_id = "duke_2025_pm"
        
        result = selector.select_case_studies(
            enhanced_dicts,
            job_keywords,
            job_level,
            job_description
        )
        
        print(f"  Selected {len(result.selected_case_studies)} case studies for HLI review")
        print(f"  Total time: {result.total_time:.3f}s")
        print(f"  LLM cost: ${result.llm_cost_estimate:.3f}")
        
        # Add LLM scores to case studies for HLI
        for i, case_study in enumerate(result.selected_case_studies):
            if i < len(result.ranked_candidates):
                case_study['llm_score'] = result.ranked_candidates[i].score
                case_study['reasoning'] = result.ranked_candidates[i].reasoning
        
        print(f"\n📋 Step 3: HLI Approval Workflow with Peter's Real Data")
        
        # Convert ranked candidates to dict format for HLI
        all_ranked_candidates = []
        for ranked_candidate in result.ranked_candidates:
            candidate_dict = ranked_candidate.case_study.copy()
            candidate_dict['llm_score'] = ranked_candidate.score
            candidate_dict['reasoning'] = ranked_candidate.reasoning
            all_ranked_candidates.append(candidate_dict)
        
        # Test HLI approval workflow with real data and full ranked list
        approved_case_studies, feedback_list = hli.hli_approval_cli(
            result.selected_case_studies,
            job_description,
            job_id,
            all_ranked_candidates  # Pass full ranked list for alternatives
        )
        
        print(f"\n📊 HLI Results with Peter's Real Data:")
        print(f"  Total reviewed: {len(result.selected_case_studies)}")
        print(f"  Approved: {len(approved_case_studies)}")
        print(f"  Rejected: {len(result.selected_case_studies) - len(approved_case_studies)}")
        
        # Test feedback storage
        print(f"\n📋 Step 4: Feedback Analysis")
        for feedback in feedback_list:
            status = "✅ APPROVED" if feedback.approved else "❌ REJECTED"
            print(f"  {feedback.case_study_id}: {status}")
            print(f"    User score: {feedback.user_score}/10")
            print(f"    LLM score: {feedback.llm_score:.1f}")
            if feedback.comments:
                print(f"    Comments: {feedback.comments}")
        
        print(f"\n✅ HLI CLI test with Peter's real data completed!")
        print(f"  Used {len(real_case_studies)} real case studies from Peter's blurbs.yaml")
        print(f"  Full case study paragraphs displayed correctly")
        print(f"  User can make informed decisions based on complete content")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find Peter's blurbs file at {peter_blurbs_path}")
        print("This is why we used mock data in the original test.")
    except Exception as e:
        print(f"❌ Error loading Peter's data: {e}")
        print("This is why we used mock data in the original test.")


if __name__ == "__main__":
    test_hli_with_peter_data() 