#!/usr/bin/env python3
"""
Human-in-the-Loop (HLI) CLI System
===================================

CLI-based approval and refinement workflow for case study selection.
Focuses on quick mode approval with structured feedback collection.
"""

import sys
import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config_manager import ConfigManager
from utils.error_handler import ErrorHandler, safe_execute

logger = logging.getLogger(__name__)


@dataclass
class HLIApproval:
    """Represents a user approval decision for a case study."""
    job_id: str
    case_study_id: str
    approved: bool
    user_score: int  # 1-10
    comments: Optional[str] = None
    llm_score: Optional[float] = None
    llm_reason: Optional[str] = None
    timestamp: Optional[str] = None
    # Enhanced feedback fields
    ranking_discrepancy: Optional[float] = None  # Difference between user and LLM scores
    llm_rank: Optional[int] = None  # LLM's ranking position
    user_rank: Optional[int] = None  # User's ranking position
    discrepancy_type: Optional[str] = None  # "user_higher", "llm_higher", "aligned"
    discrepancy_reasoning: Optional[str] = None  # User's explanation for different rating
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        # Calculate ranking discrepancy if both scores are available
        if self.llm_score is not None and self.user_score is not None:
            self.ranking_discrepancy = self.user_score - (self.llm_score * 10 / 10)  # Normalize LLM score to 1-10 scale
            
            # Determine discrepancy type
            if abs(self.ranking_discrepancy) <= 1.0:
                self.discrepancy_type = "aligned"
            elif self.ranking_discrepancy > 1.0:
                self.discrepancy_type = "user_higher"
            else:
                self.discrepancy_type = "llm_higher"


@dataclass
class CaseStudyVariant:
    """Represents a versioned case study variant."""
    version: str
    summary: str
    tags: List[str]
    approved_for: List[str]
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class HLIApprovalCLI:
    """CLI-based human-in-the-loop approval system."""
    
    def __init__(self, user_profile: str = "default"):
        """Initialize the HLI CLI system."""
        self.config_manager = ConfigManager()
        self.error_handler = ErrorHandler()
        self.user_profile = user_profile
        self.feedback_file = f"users/{user_profile}/hli_feedback.jsonl"
        self.variants_file = f"users/{user_profile}/case_study_variants.yaml"
        
        # Ensure user directory exists
        os.makedirs(f"users/{user_profile}", exist_ok=True)
    
    def hli_approval_cli(
        self, 
        selected_case_studies: List[Dict[str, Any]], 
        job_description: str,
        job_id: str,
        all_ranked_candidates: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Dict[str, Any]], List[HLIApproval]]:
        """
        Presents selected case studies via CLI for user approval.
        When user rejects a case study, shows the next highest scored alternative.
        
        Args:
            selected_case_studies: Initial list of case studies to review
            job_description: Job description for context
            job_id: Unique job identifier
            all_ranked_candidates: Full ranked list of all candidates for alternatives
            
        Returns:
            Tuple of (approved_case_studies, feedback_list)
        """
        print(f"\n🎯 Human-in-the-Loop Approval")
        print(f"Job: {job_id}")
        print(f"Description: {job_description[:100]}...")
        print(f"Initial case studies to review: {len(selected_case_studies)}")
        if all_ranked_candidates:
            print(f"Total ranked candidates available: {len(all_ranked_candidates)}")
        print("=" * 50)
        
        approved_case_studies = []
        feedback_list = []
        reviewed_case_studies = set()
        
        # Track rankings for discrepancy analysis
        llm_rankings = {}
        user_rankings = {}
        
        # Track for feedback prompting
        rejected_ai_suggestions = set()
        approved_alternatives = set()
        
        # Build LLM rankings from all_ranked_candidates
        if all_ranked_candidates:
            for i, candidate in enumerate(all_ranked_candidates):
                candidate_id = candidate.get('id', candidate.get('name', 'unknown'))
                llm_rankings[candidate_id] = i + 1
        
        # Start with the initial selected case studies
        current_candidates = selected_case_studies.copy()
        candidate_index = 0
        user_rank_counter = 1
        rejection_count = 0
        
        while candidate_index < len(current_candidates):
            case_study = current_candidates[candidate_index]
            case_study_id = case_study.get('id', case_study.get('name', 'unknown'))
            
            # Skip if already reviewed
            if case_study_id in reviewed_case_studies:
                candidate_index += 1
                continue
            
            # Show progress
            print(f"\n📋 Case Study {len(feedback_list) + 1}")
            print(f"Progress: {len(approved_case_studies)}/3 case studies added")
            print(f"Name: {case_study.get('name', case_study.get('id', 'Unknown'))}")
            print(f"Tags: {', '.join(case_study.get('tags', []))}")
            
            # Show complete case study content (the actual paragraph text)
            print(f"\n📄 Full Case Study Paragraph:")
            case_study_text = case_study.get('text', case_study.get('description', 'No case study content available'))
            print(f"{case_study_text}")
            
            # Show LLM score if available
            if 'llm_score' in case_study:
                print(f"\n🤖 LLM Score: {case_study['llm_score']:.1f}")
                if case_study_id in llm_rankings:
                    print(f"LLM Rank: #{llm_rankings[case_study_id]}")
            if 'reasoning' in case_study:
                print(f"LLM Reason: {case_study['reasoning']}")
            
            # Get user approval
            approved = self._get_user_approval()
            user_score = self._get_user_score()
            comments = None  # Set to None for MVP
            
            # Track user ranking
            user_rankings[case_study_id] = user_rank_counter
            user_rank_counter += 1
            
            # Track for feedback prompting
            if not approved:
                # This was an AI suggestion that was rejected
                if case_study_id in llm_rankings and llm_rankings[case_study_id] <= 3:
                    rejected_ai_suggestions.add(case_study_id)
            else:
                # This was approved - check if it was an alternative
                if case_study_id not in llm_rankings or llm_rankings[case_study_id] > 3:
                    approved_alternatives.add(case_study_id)
            
            # Create feedback object with enhanced tracking
            feedback = HLIApproval(
                job_id=job_id,
                case_study_id=case_study_id,
                approved=approved,
                user_score=user_score,
                comments=comments,
                llm_score=case_study.get('llm_score'),
                llm_reason=case_study.get('reasoning'),
                llm_rank=llm_rankings.get(case_study_id),
                user_rank=user_rankings.get(case_study_id)
            )
            
            feedback_list.append(feedback)
            reviewed_case_studies.add(case_study_id)
            
            if approved:
                approved_case_studies.append(case_study)
                print(f"✅ Approved case study: {case_study.get('name', case_study.get('id'))}")
                
                # Prompt for feedback if user rejected AI suggestion and approved alternative
                if len(rejected_ai_suggestions) > 0 and case_study_id in approved_alternatives:
                    feedback_reasoning = self._get_discrepancy_reasoning(feedback)
                    feedback.discrepancy_reasoning = feedback_reasoning
                
                candidate_index += 1
                
                # Check if we have 3 approved case studies
                if len(approved_case_studies) >= 3:
                    print(f"\n🎉 All 3 case studies selected!")
                    break
                    
            else:
                print(f"❌ Rejected case study: {case_study.get('name', case_study.get('id'))}")
                rejection_count += 1
                
                # Check if we should ask about adding new vs continuing search
                if rejection_count % 3 == 0:
                    choice = self._ask_search_or_add_new()
                    if choice == "add_new":
                        print(f"\n📝 Add New Case Study")
                        print(f"   (This will be implemented in Gap Detection phase)")
                        # For now, just continue with search
                        pass
                
                # If we have more ranked candidates, show the next best one
                if all_ranked_candidates:
                    next_candidate = self._get_next_best_candidate(
                        all_ranked_candidates, 
                        reviewed_case_studies,
                        approved_case_studies
                    )
                    
                    if next_candidate:
                        print(f"\n🔄 Showing next best alternative...")
                        # Replace current candidate with next best
                        current_candidates[candidate_index] = next_candidate
                        continue  # Review the new candidate
                    else:
                        print(f"\n⚠️  No more high-scoring alternatives available.")
                        candidate_index += 1
                else:
                    candidate_index += 1
        
        # Save feedback
        self._save_feedback(feedback_list)
        
        # Generate session insights
        self._generate_session_insights(feedback_list, job_id)
        
        print(f"\n📊 Approval Summary:")
        print(f"  Total reviewed: {len(feedback_list)}")
        print(f"  Approved: {len(approved_case_studies)}")
        print(f"  Rejected: {len(feedback_list) - len(approved_case_studies)}")
        
        return approved_case_studies, feedback_list
    
    def _get_user_approval(self) -> bool:
        """Get user approval decision."""
        while True:
            response = input("\nDo you want to use this case study? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def _get_user_score(self) -> int:
        """Get user relevance score (1-10)."""
        while True:
            try:
                score = int(input("Rate the relevance (1-10): "))
                if 1 <= score <= 10:
                    return score
                else:
                    print("Please enter a number between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_user_comments(self) -> Optional[str]:
        """Get optional user comments."""
        comments = input("Any improvement notes? (optional): ").strip()
        return comments if comments else None
    
    def _save_feedback(self, feedback_list: List[HLIApproval]) -> None:
        """Save feedback to JSONL file."""
        try:
            with open(self.feedback_file, 'a') as f:
                for feedback in feedback_list:
                    f.write(json.dumps(asdict(feedback)) + '\n')
            logger.info(f"Saved {len(feedback_list)} feedback entries to {self.feedback_file}")
        except Exception as e:
            self.error_handler.handle_error(e, "save_feedback", {"feedback_count": len(feedback_list)})
    
    def save_case_study_variant(
        self, 
        case_study_id: str, 
        summary: str, 
        tags: List[str], 
        approved_for: List[str]
    ) -> None:
        """Save a case study variant for future reuse."""
        try:
            # Load existing variants
            variants = self._load_case_study_variants()
            
            if case_study_id not in variants:
                variants[case_study_id] = []
            
            # Create new variant
            variant = CaseStudyVariant(
                version=f"1.{len(variants[case_study_id]) + 1}",
                summary=summary,
                tags=tags,
                approved_for=approved_for
            )
            
            variants[case_study_id].append(asdict(variant))
            
            # Save variants
            with open(self.variants_file, 'w') as f:
                yaml.dump(variants, f, default_flow_style=False)
            
            logger.info(f"Saved variant {variant.version} for {case_study_id}")
            
        except Exception as e:
            self.error_handler.handle_error(e, "save_case_study_variant", {
                "case_study_id": case_study_id,
                "approved_for": approved_for
            })
    
    def _load_case_study_variants(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load existing case study variants."""
        try:
            if os.path.exists(self.variants_file):
                with open(self.variants_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            self.error_handler.handle_error(e, "load_case_study_variants")
            return {}
    
    def get_approved_variants(self, case_study_id: str) -> List[CaseStudyVariant]:
        """Get approved variants for a case study."""
        variants = self._load_case_study_variants()
        if case_study_id in variants:
            return [CaseStudyVariant(**v) for v in variants[case_study_id]]
        return []
    
    def suggest_refinements(self, case_study: Dict[str, Any], jd_tags: List[str]) -> List[str]:
        """Suggest refinements for a case study based on job description tags."""
        suggestions = []
        
        # Check for missing metrics
        if 'growth' in jd_tags and 'revenue_growth' not in case_study.get('tags', []):
            suggestions.append("Consider adding specific revenue growth metrics")
        
        # Check for missing customer insights
        if 'customer' in jd_tags and 'customer_success' not in case_study.get('tags', []):
            suggestions.append("Consider highlighting customer success metrics")
        
        # Check for missing leadership details
        if 'leadership' in jd_tags and 'leadership' not in case_study.get('tags', []):
            suggestions.append("Consider emphasizing leadership and team management")
        
        # Check for missing technical details
        if 'technical' in jd_tags and 'technical' not in case_study.get('tags', []):
            suggestions.append("Consider adding technical implementation details")
        
        return suggestions

    def _get_next_best_candidate(
        self, 
        all_ranked_candidates: List[Dict[str, Any]], 
        reviewed_case_studies: set,
        approved_case_studies: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get the next best candidate that hasn't been reviewed yet."""
        for candidate in all_ranked_candidates:
            candidate_id = candidate.get('id', candidate.get('name', 'unknown'))
            if candidate_id not in reviewed_case_studies:
                return candidate
        return None

    def _show_ranking_insight(self, feedback: HLIApproval) -> None:
        """Show insights about ranking discrepancies."""
        if feedback.ranking_discrepancy is None:
            return
            
        if feedback.discrepancy_type == "user_higher":
            print(f"💡 Insight: You rated this {abs(feedback.ranking_discrepancy):.1f} points higher than the AI")
            print(f"   This suggests the AI may be undervaluing certain aspects of this case study")
        elif feedback.discrepancy_type == "llm_higher":
            print(f"💡 Insight: The AI rated this {abs(feedback.ranking_discrepancy):.1f} points higher than you")
            print(f"   This suggests the AI may be overvaluing certain aspects of this case study")
        else:
            print(f"✅ Alignment: Your rating closely matches the AI's assessment")
    
    def _ask_search_or_add_new(self) -> str:
        """Ask user if they want to keep searching or add a new case study."""
        while True:
            print(f"\n🤔 Keep searching library or add new case study?")
            response = input("(search/add_new): ").strip().lower()
            if response in ['search', 's']:
                return "search"
            elif response in ['add_new', 'add', 'new', 'a']:
                return "add_new"
            else:
                print("Please enter 'search' or 'add_new'")
    
    def _get_discrepancy_reasoning(self, feedback: HLIApproval) -> Optional[str]:
        """Get user's reasoning for ranking discrepancy - only when rejecting AI suggestion and approving alternative."""
        print(f"\n🤔 Why is this story the best fit?")
        print(f"   (You rejected our suggestion but approved this alternative)")
        print(f"   (This helps improve the system's understanding of what matters to you)")
        
        reasoning = input("Your reasoning (optional, press Enter to skip): ").strip()
        return reasoning if reasoning else None

    def _generate_session_insights(self, feedback_list: List[HLIApproval], job_id: str) -> None:
        """Generate insights from the entire session."""
        if not feedback_list:
            return
        
        # Calculate session statistics
        total_discrepancies = [f.ranking_discrepancy for f in feedback_list if f.ranking_discrepancy is not None]
        user_higher_count = len([f for f in feedback_list if f.discrepancy_type == "user_higher"])
        llm_higher_count = len([f for f in feedback_list if f.discrepancy_type == "llm_higher"])
        aligned_count = len([f for f in feedback_list if f.discrepancy_type == "aligned"])
        
        if total_discrepancies:
            avg_discrepancy = sum(total_discrepancies) / len(total_discrepancies)
            
            print(f"\n📈 Session Insights:")
            print(f"  Average ranking discrepancy: {avg_discrepancy:.1f} points")
            print(f"  User rated higher: {user_higher_count} cases")
            print(f"  AI rated higher: {llm_higher_count} cases")
            print(f"  Aligned ratings: {aligned_count} cases")
            
            # Save session insights
            session_insights = {
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "total_reviewed": len(feedback_list),
                "avg_discrepancy": avg_discrepancy,
                "user_higher_count": user_higher_count,
                "llm_higher_count": llm_higher_count,
                "aligned_count": aligned_count,
                "feedback_details": [asdict(f) for f in feedback_list]
            }
            
            insights_file = f"users/{self.user_profile}/session_insights.jsonl"
            try:
                with open(insights_file, 'a') as f:
                    f.write(json.dumps(session_insights) + '\n')
                logger.info(f"Saved session insights to {insights_file}")
            except Exception as e:
                self.error_handler.handle_error(e, "save_session_insights", {"job_id": job_id})


def test_hli_approval_cli():
    """Test the HLI approval CLI functionality."""
    print("🧪 Testing HLI Approval CLI...")
    
    # Test case studies
    test_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'description': 'Led cross-functional team from 0-1 to improve home energy management',
            'llm_score': 8.9,
            'reasoning': 'Strong cleantech match; highlights post-sale engagement and DER'
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'B2B', 'clean_energy', 'scaling'],
            'description': 'Helped scale company from Series A to Series C, leading platform rebuild',
            'llm_score': 7.5,
            'reasoning': 'Good B2B scaling experience in cleantech'
        }
    ]
    
    # Initialize HLI system
    hli = HLIApprovalCLI(user_profile="test_user")
    
    # Test approval workflow (simulated)
    print("\n📋 Simulating approval workflow...")
    job_description = "Senior Product Manager at cleantech startup focusing on energy management"
    job_id = "duke_2025_pm"
    
    # Note: In real usage, this would prompt for user input
    # For testing, we'll simulate the workflow
    print("(Simulating user approval - in real usage this would prompt for input)")
    
    # Test feedback saving
    test_feedback = [
        HLIApproval(
            job_id=job_id,
            case_study_id="enact",
            approved=True,
            user_score=9,
            comments="Add more detail on customer analytics",
            llm_score=8.9,
            llm_reason="Strong cleantech match"
        ),
        HLIApproval(
            job_id=job_id,
            case_study_id="aurora",
            approved=False,
            user_score=6,
            comments="Too focused on B2B, need more consumer experience",
            llm_score=7.5,
            llm_reason="Good B2B scaling experience"
        )
    ]
    
    # Save test feedback
    hli._save_feedback(test_feedback)
    
    # Test variant saving
    hli.save_case_study_variant(
        case_study_id="enact",
        summary="At Enact, I led cross-functional team from 0-1 to improve home energy management",
        tags=['cleantech', 'DER', 'customer_success'],
        approved_for=[job_id, 'southern_2025_vpp']
    )
    
    # Test refinement suggestions
    suggestions = hli.suggest_refinements(
        test_case_studies[0], 
        ['growth', 'customer', 'leadership']
    )
    
    print(f"\n📊 Test Results:")
    print(f"  Feedback saved: {len(test_feedback)} entries")
    print(f"  Variant saved: enact v1.1")
    print(f"  Refinement suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"    - {suggestion}")
    
    print("\n✅ HLI Approval CLI test completed!")


if __name__ == "__main__":
    test_hli_approval_cli() 