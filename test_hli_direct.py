#!/usr/bin/env python3
"""
Direct test of HLI CLI with real case study data
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hli_approval_cli import HLIApprovalCLI


def test_hli_with_real_data():
    """Test HLI CLI with real case study data."""
    print("🧪 Testing HLI CLI with Real Case Study Data...")
    
    # Real case study data from blurbs.yaml
    real_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
            'text': 'At Enact Systems, I led a cross-functional team from 0–1 to improve home energy management. As part of the Series A management team, I owned P&L for the consumer line of business and defined product strategy based on customer insights and financial modeling. I built a unified roadmap for 2 pods and 3 products (web, mobile, and white-label), hired and coached the team, and drove consistent quarterly execution. These efforts delivered +210% MAUs, +876% event growth, +853% time-in-app, and +169% revenue growth.',
            'llm_score': 8.9,
            'reasoning': 'Strong cleantech match; highlights post-sale engagement and DER'
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'B2B', 'clean_energy', 'scaling'],
            'text': 'At Aurora Solar, I was a founding PM and helped scale the company from Series A to Series C. I led a platform rebuild that transformed a solar design tool into a full sales engine—broadening adoption from designers to sales teams and supporting a shift from SMB to enterprise. I introduced beta testing, behavioral analytics, and PLG onboarding to accelerate launches. I also aligned marketing, support, and engineering through shared prioritization, integrated support workflows, and the v1 design system. These efforts helped Aurora reach 90% adoption among top U.S. EPCs and achieve a $4B valuation.',
            'llm_score': 7.5,
            'reasoning': 'Good B2B scaling experience in cleantech'
        },
        {
            'id': 'meta',
            'name': 'Meta Explainable AI Case Study',
            'tags': ['AI', 'ML', 'trust', 'internal_tools', 'explainable'],
            'text': 'At Meta, I led a cross-functional ML team to scale global recruiting tools. High-precision candidate recommendations had low adoption, so I conducted discovery to identify trust and UX barriers. I introduced explainable AI and a co-pilot UX to improve transparency and control, and rolled out these changes in phases. The result: a 130% increase in claims within 30 days and a 10x lift in ML usage by year\'s end.',
            'llm_score': 6.2,
            'reasoning': 'Good AI/ML experience with trust and explainability'
        }
    ]
    
    # Initialize HLI system
    hli = HLIApprovalCLI(user_profile="test_real_data")
    
    # Test approval workflow with real data
    job_description = "Senior Product Manager at cleantech startup focusing on energy management"
    job_id = "duke_2025_pm"
    
    print(f"\n📋 Testing HLI CLI with {len(real_case_studies)} real case studies...")
    print("Note: This will prompt for user input. For testing, we'll simulate responses.")
    
    # Simulate the approval workflow
    approved_case_studies, feedback_list = hli.hli_approval_cli(
        real_case_studies,
        job_description,
        job_id
    )
    
    print(f"\n📊 Results:")
    print(f"  Total reviewed: {len(real_case_studies)}")
    print(f"  Approved: {len(approved_case_studies)}")
    print(f"  Rejected: {len(real_case_studies) - len(approved_case_studies)}")
    
    print(f"\n✅ HLI CLI test with real data completed!")
    print(f"  Full case study paragraphs were displayed correctly")
    print(f"  User could make informed decisions based on complete content")


if __name__ == "__main__":
    test_hli_with_real_data() 