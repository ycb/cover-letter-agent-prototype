#!/usr/bin/env python3
"""
Mock Test for LLM Enhancement
============================

Test the LLM enhancement structure without requiring an API key.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_llm_structure():
    """Test the LLM enhancement structure without API calls."""

    print("🧪 Testing LLM enhancement structure...")

    # Test imports
    try:
        from features.enhance_with_contextual_llm import enhance_with_contextual_llm, EnhancementResult

        print("✅ LLM enhancement module imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Test prompt preferences
    try:
        from config.prompt_prefs import get_llm_prompt_preferences

        prefs = get_llm_prompt_preferences()
        print(f"✅ Prompt preferences loaded: {len(prefs)} keys")
    except ImportError as e:
        print(f"❌ Prompt preferences import error: {e}")
        return False

    # Test draft agent
    try:
        from agents.draft_cover_letter import DraftCoverLetterAgent

        agent = DraftCoverLetterAgent()
        print("✅ Draft cover letter agent created successfully")
    except ImportError as e:
        print(f"❌ Draft agent import error: {e}")
        return False

    # Test CLI tool
    try:
        from cli.test_llm_enhancement import load_file_content, create_test_metadata

        print("✅ CLI test module imported successfully")
    except ImportError as e:
        print(f"❌ CLI test import error: {e}")
        return False

    # Test configuration
    try:
        import yaml

        with open("data/agent_config.yaml", "r") as f:
            config = yaml.safe_load(f)

        llm_config = config.get("llm_enhancement", {})
        print(f"✅ LLM config loaded: enabled={llm_config.get('enabled', False)}")
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

    print("\n✅ All LLM enhancement components are properly structured!")
    print("\nTo test with real API calls:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("2. Run: python test_llm_enhancement.py")
    print("3. Or test with CLI: python cli/test_llm_enhancement.py --jd job.txt --cl draft.txt")

    return True


if __name__ == "__main__":
    success = test_llm_structure()
    sys.exit(0 if success else 1)
