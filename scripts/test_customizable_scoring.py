#!/usr/bin/env python3
"""
Test Customizable Case Study Scoring
===================================

Demonstrates the new multi-user, role-based, customizable case study scoring system.
Tests different job types and user profiles to show how scoring adapts.
"""

import os
import sys
import yaml
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.case_study_scoring import CaseStudyScorer, create_user_weights_template, get_job_type_weights


def load_test_case_studies() -> List[Dict[str, Any]]:
    """Load case studies from blurbs.yaml for testing."""
    try:
        with open("data/blurbs.yaml", 'r') as f:
            data = yaml.safe_load(f)
        return data.get('examples', [])
    except FileNotFoundError:
        print("Error: data/blurbs.yaml not found")
        return []


def test_job_types():
    """Test scoring with different job types."""
    print("=" * 60)
    print("TESTING JOB TYPE SCORING")
    print("=" * 60)
    
    case_studies = load_test_case_studies()
    if not case_studies:
        print("No case studies found!")
        return
    
    # Test job types
    test_jobs = [
        {
            "title": "Senior Product Manager, Growth",
            "keywords": ["growth", "acquisition", "activation", "plg", "metrics", "data_driven"],
            "description": "Growth PM focused on user acquisition and activation"
        },
        {
            "title": "AI Product Manager",
            "keywords": ["ai_ml", "artificial_intelligence", "machine_learning", "genai", "nlp", "trust"],
            "description": "AI/ML PM focused on AI-powered products"
        },
        {
            "title": "Founding Product Manager",
            "keywords": ["founding_pm", "startup", "0_to_1", "early_stage", "gtm", "discovery"],
            "description": "Founding PM at early-stage startup"
        },
        {
            "title": "Director of Product, Enterprise",
            "keywords": ["enterprise", "b2b", "leadership", "xfn", "strategy", "scale"],
            "description": "Enterprise PM with leadership responsibilities"
        },
        {
            "title": "Product Manager, ClimateTech",
            "keywords": ["cleantech", "climate", "energy", "solar", "b2b2c", "mission"],
            "description": "ClimateTech PM focused on clean energy"
        }
    ]
    
    for job in test_jobs:
        print(f"\n--- {job['title']} ---")
        print(f"Description: {job['description']}")
        print(f"Keywords: {', '.join(job['keywords'])}")
        
        # Get job-specific weights
        job_weights = get_job_type_weights(job['title'], job['keywords'])
        print(f"Job-specific weights: {job_weights}")
        
        # Test with default scorer
        scorer = CaseStudyScorer()
        selected = scorer.select_case_studies(
            case_studies, 
            job['keywords'], 
            job['title'], 
            max_selections=3
        )
        
        print(f"Selected case studies: {[cs['id'] for cs in selected]}")
        print("-" * 40)


def test_user_profiles():
    """Test scoring with different user profiles."""
    print("\n" + "=" * 60)
    print("TESTING USER PROFILE SCORING")
    print("=" * 60)
    
    case_studies = load_test_case_studies()
    if not case_studies:
        print("No case studies found!")
        return
    
    # Create test user profiles
    test_users = [
        {
            "user_id": "growth_focused",
            "weights": {
                "scoring_weights": {
                    "role": {"growth": 5, "data_driven": 4, "metrics": 4},
                    "impact": {"revenue": 5, "users": 4, "engagement": 4},
                    "key_qualities": {"plg": 4, "activation": 4}
                }
            },
            "description": "Growth-focused PM who values metrics and user acquisition"
        },
        {
            "user_id": "ai_expert",
            "weights": {
                "scoring_weights": {
                    "role": {"ai_ml": 5, "data_driven": 4},
                    "technical": {"ai_ml": 5, "genai": 4, "nlp": 4},
                    "key_qualities": {"trust": 4, "explainability": 4}
                }
            },
            "description": "AI/ML expert who values technical depth and trust"
        },
        {
            "user_id": "startup_founder",
            "weights": {
                "scoring_weights": {
                    "role": {"founding_pm": 5, "leadership": 4, "strategy": 4},
                    "maturity": {"startup": 5, "pilot": 4},
                    "key_qualities": {"gtm": 4, "discovery": 4}
                }
            },
            "description": "Startup founder who values 0-to-1 experience and GTM"
        },
        {
            "user_id": "enterprise_leader",
            "weights": {
                "scoring_weights": {
                    "business_model": {"enterprise": 5, "b2b": 4},
                    "key_qualities": {"xfn": 5, "strategy": 4},
                    "maturity": {"public": 3, "scaleup": 4}
                }
            },
            "description": "Enterprise leader who values cross-functional leadership"
        }
    ]
    
    # Test job
    test_job = {
        "title": "Senior Product Manager",
        "keywords": ["growth", "ai_ml", "founding_pm", "enterprise", "cleantech"],
        "description": "Generic senior PM role"
    }
    
    for user in test_users:
        print(f"\n--- {user['user_id']} ---")
        print(f"Description: {user['description']}")
        
        # Create user weights file
        user_dir = f"users/{user['user_id']}"
        os.makedirs(user_dir, exist_ok=True)
        user_weights_path = f"{user_dir}/user_weights.yaml"
        
        with open(user_weights_path, 'w') as f:
            yaml.dump(user['weights'], f)
        
        # Test with user-specific scorer
        scorer = CaseStudyScorer(user_id=user['user_id'])
        selected = scorer.select_case_studies(
            case_studies, 
            test_job['keywords'], 
            test_job['title'], 
            max_selections=3
        )
        
        print(f"Selected case studies: {[cs['id'] for cs in selected]}")
        print("-" * 40)


def test_scoring_breakdown():
    """Test detailed scoring breakdown for a specific case."""
    print("\n" + "=" * 60)
    print("TESTING DETAILED SCORING BREAKDOWN")
    print("=" * 60)
    
    case_studies = load_test_case_studies()
    if not case_studies:
        print("No case studies found!")
        return
    
    # Test case: Growth PM job
    job_title = "Senior Product Manager, Growth"
    job_keywords = ["growth", "acquisition", "activation", "plg", "metrics", "data_driven"]
    
    print(f"Job: {job_title}")
    print(f"Keywords: {', '.join(job_keywords)}")
    print()
    
    # Score each case study
    scorer = CaseStudyScorer()
    for cs in case_studies:
        score = scorer.score_case_study(cs, job_keywords, job_title)
        
        print(f"Case Study: {score.case_study_id}")
        print(f"  Total Score: {score.total_score:.2f}")
        print(f"  Category Scores: {score.category_scores}")
        print(f"  Matched Tags: {score.matched_tags}")
        if score.multipliers:
            print(f"  Multipliers: {score.multipliers}")
        if score.penalties:
            print(f"  Penalties: {score.penalties}")
        print(f"  Explanations: {score.explanations}")
        print()


def test_user_weights_template():
    """Test creating user weights templates."""
    print("\n" + "=" * 60)
    print("TESTING USER WEIGHTS TEMPLATE CREATION")
    print("=" * 60)
    
    test_user_id = "test_user"
    template_path = create_user_weights_template(test_user_id)
    
    if template_path:
        print(f"Created template at: {template_path}")
        
        # Load and display the template
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
        
        print("\nTemplate structure:")
        for category, weights in template.get('scoring_weights', {}).items():
            print(f"  {category}: {len(weights)} weights")
        
        # Clean up
        os.remove(template_path)
        os.rmdir(f"users/{test_user_id}")
        print("Template cleaned up")
    else:
        print("Failed to create template")


def main():
    """Run all tests."""
    print("CUSTOMIZABLE CASE STUDY SCORING TESTS")
    print("=" * 60)
    
    # Test job type scoring
    test_job_types()
    
    # Test user profile scoring
    test_user_profiles()
    
    # Test detailed scoring breakdown
    test_scoring_breakdown()
    
    # Test template creation
    test_user_weights_template()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("1. Role-based scoring (Growth PM vs AI PM vs Founding PM)")
    print("2. User-specific weights (different priorities per user)")
    print("3. Industry-specific scoring (Enterprise vs Startup vs Cleantech)")
    print("4. Detailed scoring breakdown with multipliers and penalties")
    print("5. Template creation for new users")


if __name__ == "__main__":
    main() 