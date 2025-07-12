#!/usr/bin/env python3
"""
Test Metrics Preservation
========================

Test that the LLM enhancement preserves all metrics and quantified achievements.
"""

import sys
import os
from pathlib import Path

# --- Ensure .env is always loaded ---
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path)
except ImportError:
    pass

# --- Fail fast if API key is missing ---
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not found.\nPlease create a .env file in the project root with the line: OPENAI_API_KEY=sk-...\nSee .env.example for details.\n")
    sys.exit(1)
else:
    print(f"[DEBUG] OPENAI_API_KEY loaded: ...{api_key[-4:]}")

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.llm_rewrite import LLMRewriter, LLMRewriteConfig


def test_metrics_preservation():
    """Test that metrics are preserved in LLM enhancement."""
    
    # Sample draft with lots of metrics
    original_draft = """Dear Hiring Team,

I'm a product manager with 15+ years of experience building user-centric products that deliver business results. My background includes leading 0–1 at hypergrowth startups (Aurora Solar, FalconX) and driving impact at scale for global brands (Meta, Samsung, Salesforce).

At Enact Systems, I led a cross-functional team from 0–1 to improve home energy management. As part of the Series A management team, I owned P&L for the consumer line of business and defined product strategy based on customer insights and financial modeling. These efforts delivered +210% MAUs, +876% event growth, +853% time-in-app, and +169% revenue growth.

At Aurora Solar, I was a founding PM and helped scale the company from Series A to Series C. I led a platform rebuild that transformed a solar design tool into a full sales engine. These efforts helped Aurora reach 90% adoption among top U.S. EPCs and achieve a $4B valuation.

At Samsung, I led the overhaul of the Samsung+ app to restore trust after the Note7 crisis. These efforts drove a 160% increase in MAUs, 200% higher engagement, and improved our Play Store rating from 3.7 to 4.3.

I have 6+ years of experience leading and mentoring high-performing product teams.

Best regards,
Peter Spannagle"""
    
    job_description = """Senior Product Manager - Growth Team

We are seeking a Senior Product Manager to join our growth team. You will be responsible for:
- Leading product strategy for user acquisition and retention
- Conducting user research and data analysis to inform product decisions
- Working with cross-functional teams including engineering, design, and marketing
- Driving product decisions based on metrics and user feedback
- Building systems that align teams around measurable outcomes
- Managing and mentoring junior product managers

Requirements:
- 5+ years of product management experience
- Experience with user research and data analysis
- Strong analytical skills and ability to work with complex data
- Experience leading cross-functional teams
- Background in B2B or SaaS products preferred
- Experience with growth strategies and user acquisition

About our company: We are a fast-growing SaaS company focused on helping businesses scale efficiently through data-driven product decisions."""
    
    print("🧪 Testing Metrics Preservation")
    print("=" * 50)
    
    # Create LLM rewriter
    config = LLMRewriteConfig(
        enabled=True,
        model="gpt-4",
        temperature=0.5,
        preserve_truth=True,
        add_comments=True
    )
    rewriter = LLMRewriter(config)
    
    if not rewriter.available:
        print("❌ LLM rewriter not available")
        return
    
    print("📄 Original Draft (with metrics):")
    print("-" * 30)
    print(original_draft)
    print("\n" + "=" * 50)
    
    # Enhance the draft
    print("🔄 Enhancing with LLM...")
    enhanced_draft = rewriter.rewrite_cover_letter(original_draft, job_description)
    
    print("🔁 Enhanced Draft:")
    print("-" * 30)
    print(enhanced_draft)
    print("\n" + "=" * 50)
    
    # Validate metrics preservation
    print("🔍 Metrics Preservation Check:")
    validation = rewriter.validate_truth_preservation(original_draft, enhanced_draft)
    
    if validation["valid"]:
        print("✅ No truth preservation concerns detected")
    else:
        print("⚠️  Truth preservation concerns:")
        for concern in validation["concerns"]:
            print(f"   - {concern}")
    
    # Check specific metrics
    metrics_to_check = [
        "15+", "210%", "876%", "853%", "169%", "90%", "$4B", 
        "160%", "200%", "3.7", "4.3", "6+"
    ]
    
    print(f"\n📊 Specific Metrics Check:")
    for metric in metrics_to_check:
        if metric in enhanced_draft:
            print(f"   ✅ '{metric}' preserved")
        else:
            print(f"   ❌ '{metric}' missing")
    
    # Count preserved metrics
    preserved_count = sum(1 for metric in metrics_to_check if metric in enhanced_draft)
    total_count = len(metrics_to_check)
    
    print(f"\n📈 Metrics Preservation Score:")
    print(f"   Preserved: {preserved_count}/{total_count} metrics")
    print(f"   Success Rate: {(preserved_count/total_count)*100:.1f}%")
    
    if preserved_count == total_count:
        print("🎉 All metrics preserved successfully!")
    else:
        print("⚠️  Some metrics were lost - needs improvement")
    
    return preserved_count == total_count


if __name__ == "__main__":
    success = test_metrics_preservation()
    sys.exit(0 if success else 1) 