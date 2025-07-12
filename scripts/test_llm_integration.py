#!/usr/bin/env python3
"""
Test LLM Integration
===================

Test script to verify LLM enhancement functionality works correctly.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.cover_letter_agent import CoverLetterAgent
from core.llm_rewrite import LLMRewriteConfig, LLMRewriter


def test_llm_rewriter():
    """Test the LLM rewriter functionality."""
    print("🧪 Testing LLM Rewriter...")

    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return False

    # Test LLM rewriter initialization
    try:
        config = LLMRewriteConfig(enabled=True, model="gpt-4", temperature=0.5, preserve_truth=True, add_comments=True)
        rewriter = LLMRewriter(config)

        if not rewriter.available:
            print("❌ LLM rewriter not available")
            return False

        print("✅ LLM rewriter initialized successfully")

        # Test with a sample cover letter
        sample_letter = """
Dear Hiring Team,

I am excited to apply for the Product Manager position at your company. With my experience in product management and user research, I believe I can contribute to your team's success.

In my previous role, I led a team that increased user engagement by 50% through data-driven product decisions. I conducted user interviews and used analytics to identify key improvement opportunities.

I am particularly interested in your company's mission and believe my background in product strategy aligns well with your needs.

Best regards,
Peter Spannagle
"""

        sample_jd = """
We are looking for a Product Manager to join our team. The ideal candidate will have:
- Experience with user research and data analysis
- Strong product strategy skills
- Experience leading cross-functional teams
- Background in B2B or SaaS products
"""

        print("🔄 Testing LLM enhancement...")
        enhanced = rewriter.rewrite_cover_letter(sample_letter, sample_jd)

        if enhanced and enhanced != sample_letter:
            print("✅ LLM enhancement completed successfully")
            print(f"Original length: {len(sample_letter)} characters")
            print(f"Enhanced length: {len(enhanced)} characters")
            return True
        else:
            print("❌ LLM enhancement failed or returned unchanged text")
            return False

    except Exception as e:
        print(f"❌ Error testing LLM rewriter: {e}")
        return False


def test_cover_letter_agent_integration():
    """Test LLM integration with the main cover letter agent."""
    print("\n🧪 Testing Cover Letter Agent Integration...")

    try:
        # Initialize agent
        agent = CoverLetterAgent()

        # Create a sample job description
        sample_jd_text = """
Product Manager - Growth Team

We are seeking a Product Manager to join our growth team. You will be responsible for:
- Leading product strategy for user acquisition and retention
- Conducting user research and data analysis
- Working with cross-functional teams including engineering and design
- Driving product decisions based on metrics and user feedback

Requirements:
- 3+ years of product management experience
- Experience with user research and data analysis
- Strong analytical skills
- Experience with B2B or SaaS products preferred

About our company: We are a fast-growing SaaS company focused on helping businesses scale efficiently.
"""

        # Process the job description
        print("🔄 Processing job description...")
        result = agent.process_job_description(
            sample_jd_text, debug=False, explain=False, track_enhance=False, interactive=False
        )

        # Handle different return types
        if len(result) == 3:
            job, cover_letter, suggestions = result
        elif len(result) == 4:
            job, cover_letter, suggestions, debug_info = result
        else:
            raise ValueError(f"Unexpected return type from process_job_description: {len(result)} items")

        print("✅ Cover letter generated successfully")
        print(f"Company: {job.company_name}")
        print(f"Position: {job.job_title}")
        print(f"Cover letter length: {len(cover_letter)} characters")

        # Check if LLM enhancement was applied
        if "<!-- LLM Enhanced Cover Letter -->" in cover_letter:
            print("✅ LLM enhancement detected in output")
        else:
            print("ℹ️  LLM enhancement not detected (may be disabled in config)")

        return True

    except Exception as e:
        print(f"❌ Error testing cover letter agent integration: {e}")
        return False


def test_configuration():
    """Test LLM configuration loading."""
    print("\n🧪 Testing Configuration...")

    try:
        agent = CoverLetterAgent()

        # Check if LLM config is loaded
        llm_enabled = agent.config.get("llm_enhance", False)
        llm_model = agent.config.get("llm_model", "gpt-4")

        print(f"LLM Enhancement: {'✅ Enabled' if llm_enabled else '❌ Disabled'}")
        print(f"LLM Model: {llm_model}")
        print(f"LLM Temperature: {agent.config.get('llm_temperature', 0.5)}")
        print(f"Preserve Truth: {'✅ Yes' if agent.config.get('llm_preserve_truth', True) else '❌ No'}")

        return True

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing LLM Integration for Cover Letter Agent")
    print("=" * 50)

    tests = [
        ("Configuration", test_configuration),
        ("LLM Rewriter", test_llm_rewriter),
        ("Agent Integration", test_cover_letter_agent_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! LLM integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
