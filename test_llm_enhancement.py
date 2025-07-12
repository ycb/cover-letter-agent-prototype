#!/usr/bin/env python3
"""
Test LLM Enhancement
===================

Simple test script to verify LLM enhancement functionality.
"""

import sys
import os
from pathlib import Path

# --- Ensure .env is always loaded ---
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Fail fast if API key is missing ---
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not found.\nPlease create a .env file in the project root with the line: OPENAI_API_KEY=sk-...\nSee .env.example for details.\n")
    sys.exit(1)
else:
    print(f"[DEBUG] OPENAI_API_KEY loaded: ...{api_key[-4:]}")

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_llm_enhancement():
    """Test the LLM enhancement functionality."""

    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return False

    # Test job description
    job_description = """
Senior Product Manager - AI/ML
AudioEye · Remote · Full-time

We're looking for a Senior Product Manager to lead our AI/ML initiatives. You'll work on cutting-edge accessibility technology and help millions of people access digital content.

Requirements:
- 5+ years product management experience
- Experience with AI/ML products
- Strong technical background
- Excellent communication skills
"""

    # Test cover letter draft
    cover_letter_draft = """
Dear Hiring Manager,

I'm excited to apply for the Senior Product Manager role at AudioEye. With my experience in AI/ML product development and passion for accessibility, I believe I can make a significant impact.

In my previous role, I led the development of an AI-powered accessibility tool that improved digital access for over 1 million users. I worked closely with engineering teams to build scalable solutions and collaborated with accessibility experts to ensure our products met WCAG guidelines.

I'm particularly drawn to AudioEye's mission of making digital content accessible to everyone. My experience in AI/ML product management, combined with my understanding of accessibility challenges, positions me well to contribute to your team.

I look forward to discussing how I can help AudioEye continue to innovate in the accessibility space.

Best regards,
[Your Name]
"""

    # Test metadata
    metadata = {
        "company_name": "AudioEye",
        "position_title": "Senior Product Manager - AI/ML",
        "job_type": "ai_ml",
        "job_score": 9.0,
        "case_study_tags": ["ai_ml", "accessibility"],
        "role_alignment": "strong",
        "targeting_score": 15.0,
        "go_no_go": True,
    }

    try:
        # Import and test LLM enhancement
        from features.enhance_with_contextual_llm import enhance_with_contextual_llm

        print("🤖 Testing LLM enhancement...")
        print(f"📄 Job Description: {len(job_description)} characters")
        print(f"📝 Cover Letter Draft: {len(cover_letter_draft)} characters")
        print(f"🏢 Company: {metadata['company_name']}")

        result = enhance_with_contextual_llm(jd_text=job_description, cl_text=cover_letter_draft, metadata=metadata)

        print(f"\n✅ LLM Enhancement Results:")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Changes Made: {len(result.changes_made)}")

        if result.changes_made:
            print("\nChanges:")
            for change in result.changes_made:
                print(f"  • {change}")

        print(f"\nAnalysis: {result.analysis_summary}")

        print(f"\nOriginal Length: {len(result.original_draft)} characters")
        print(f"Enhanced Length: {len(result.enhanced_draft)} characters")

        if result.confidence_score > 0.5:
            print("\n✅ Enhancement successful!")
            return True
        else:
            print("\n⚠️ Enhancement confidence too low")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during LLM enhancement: {e}")
        return False


if __name__ == "__main__":
    success = test_llm_enhancement()
    sys.exit(0 if success else 1)
