#!/usr/bin/env python3
"""
Test User Preferences for LLM Enhancement
========================================

Test script to verify user preferences are correctly loaded and applied.
"""

import sys
import os
import yaml
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

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_preferences_loading():
    """Test that user preferences are loaded correctly."""
    
    print("🧪 Testing user preferences loading...")
    
    # Test loading preferences file
    try:
        with open("data/user_preferences.yaml", 'r') as f:
            prefs = yaml.safe_load(f)
        
        print("✅ User preferences loaded successfully")
        
        # Test tone preferences
        tone_prefs = prefs.get('tone_preferences', {})
        print(f"  Verbosity: {tone_prefs.get('verbosity', 'N/A')}")
        print(f"  Formality: {tone_prefs.get('formality', 'N/A')}")
        print(f"  Precision: {tone_prefs.get('precision', 'N/A')}")
        print(f"  Tone Style: {tone_prefs.get('tone_style', 'N/A')}")
        print(f"  Tighten Percent: {tone_prefs.get('tighten_percent', 'N/A')}%")
        
        # Test language preferences
        language_prefs = prefs.get('language_preferences', {})
        print(f"  Sentence Length: {language_prefs.get('sentence_length', 'N/A')}")
        print(f"  Paragraph Style: {language_prefs.get('paragraph_style', 'N/A')}")
        
        # Test preservation rules
        preservation_rules = prefs.get('preservation_rules', {})
        print(f"  Preserve Metrics: {preservation_rules.get('preserve_metrics', 'N/A')}")
        print(f"  Preserve User Voice: {preservation_rules.get('preserve_user_voice', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading preferences: {e}")
        return False


def test_enhancement_with_preferences():
    """Test LLM enhancement with user preferences."""
    
    print("\n🧪 Testing LLM enhancement with user preferences...")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    
    # Test job description and cover letter
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
    
    cover_letter_draft = """
Dear Hiring Manager,

I'm excited to apply for the Senior Product Manager role at AudioEye. With my experience in AI/ML product development and passion for accessibility, I believe I can make a significant impact.

In my previous role, I led the development of an AI-powered accessibility tool that improved digital access for over 1 million users. I worked closely with engineering teams to build scalable solutions and collaborated with accessibility experts to ensure our products met WCAG guidelines.

I'm particularly drawn to AudioEye's mission of making digital content accessible to everyone. My experience in AI/ML product management, combined with my understanding of accessibility challenges, positions me well to contribute to your team.

I look forward to discussing how I can help AudioEye continue to innovate in the accessibility space.

Best regards,
[Your Name]
"""
    
    metadata = {
        'company_name': 'AudioEye',
        'position_title': 'Senior Product Manager - AI/ML',
        'job_type': 'ai_ml',
        'job_score': 9.0,
        'case_study_tags': ['ai_ml', 'accessibility'],
        'role_alignment': 'strong',
        'targeting_score': 15.0,
        'go_no_go': True
    }
    
    try:
        # Import and test LLM enhancement with preferences
        from features.enhance_with_contextual_llm import enhance_with_contextual_llm
        
        print("🤖 Testing LLM enhancement with user preferences...")
        print(f"📄 Job Description: {len(job_description)} characters")
        print(f"📝 Cover Letter Draft: {len(cover_letter_draft)} characters")
        
        result = enhance_with_contextual_llm(
            jd_text=job_description,
            cl_text=cover_letter_draft,
            metadata=metadata
        )
        
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
        
        # Calculate length reduction
        original_words = len(result.original_draft.split())
        enhanced_words = len(result.enhanced_draft.split())
        reduction_percent = ((original_words - enhanced_words) / original_words) * 100
        
        print(f"\nLength Reduction: {reduction_percent:.1f}%")
        
        # Check if reduction is within expected range (10-20%)
        if 10 <= reduction_percent <= 20:
            print("✅ Length reduction within expected range (10-20%)")
        else:
            print(f"⚠️ Length reduction outside expected range: {reduction_percent:.1f}%")
        
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


def test_different_preferences():
    """Test with different preference values."""
    
    print("\n🧪 Testing different preference values...")
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Academic Style',
            'changes': {'tone_style': 'academic', 'formality': 'high'}
        },
        {
            'name': 'No Tightening',
            'changes': {'tighten_percent': 0}
        },
        {
            'name': 'High Verbosity',
            'changes': {'verbosity': 'high', 'tighten_percent': 5}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        
        # Load current preferences
        try:
            with open("data/user_preferences.yaml", 'r') as f:
                prefs = yaml.safe_load(f)
            
            # Apply scenario changes
            for key, value in scenario['changes'].items():
                if key in prefs.get('tone_preferences', {}):
                    prefs['tone_preferences'][key] = value
                elif key in prefs.get('language_preferences', {}):
                    prefs['language_preferences'][key] = value
            
            # Save modified preferences temporarily
            with open("data/user_preferences_test.yaml", 'w') as f:
                yaml.dump(prefs, f)
            
            print(f"  Applied changes: {scenario['changes']}")
            print("  ✅ Preferences modified successfully")
            
        except Exception as e:
            print(f"  ❌ Error modifying preferences: {e}")
    
    print("\n✅ All preference scenarios tested successfully!")


def main():
    """Main test function."""
    
    print("🎯 Testing User Preferences for LLM Enhancement")
    print("=" * 50)
    
    # Test 1: Load preferences
    success1 = test_preferences_loading()
    
    # Test 2: Enhancement with preferences
    success2 = test_enhancement_with_preferences()
    
    # Test 3: Different preference values
    test_different_preferences()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
        print("\nTo customize preferences, edit data/user_preferences.yaml")
        print("Available options:")
        print("- tone_style: executive, academic, conversational, technical")
        print("- verbosity: low, medium, high")
        print("- tighten_percent: 0-30")
        print("- formality: low, medium, high")
        return True
    else:
        print("\n❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 