#!/usr/bin/env python3
"""
Check Paragraph Lengths
Quick script to check character counts of refined paragraphs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml

USER_ID = "peter"
USER_DIR = f"users/{USER_ID}"
REFINED_STORIES_PATH = f"{USER_DIR}/refined_star_stories.yaml"

def check_paragraph_lengths():
    """Check character counts of refined paragraphs."""
    try:
        with open(REFINED_STORIES_PATH, 'r') as f:
            data = yaml.safe_load(f)
        
        refined_stories = data.get('refined_stories', [])
        
        print(f"📊 Refined Paragraph Length Analysis:")
        print(f"  📝 Total paragraphs: {len(refined_stories)}")
        print(f"  🎯 Target length: 430 characters")
        print(f"  📏 Range: 150-650 characters")
        print()
        
        total_chars = 0
        for story in refined_stories:
            if story.get('status') == 'refined':
                paragraph = story.get('refined_paragraph', '')
                char_count = len(paragraph)
                total_chars += char_count
                format_type = story.get('detected_format', 'unknown')
                
                status = "✅" if 150 <= char_count <= 650 else "⚠️"
                print(f"  {status} {story['original_story']['title']}: {char_count} chars ({format_type})")
        
        if refined_stories:
            avg_length = total_chars / len(refined_stories)
            print(f"\n📏 Average length: {avg_length:.0f} characters")
            print(f"📏 Total characters: {total_chars}")
            
    except FileNotFoundError:
        print(f"❌ Refined stories file not found: {REFINED_STORIES_PATH}")
    except Exception as e:
        print(f"❌ Error checking lengths: {e}")

if __name__ == "__main__":
    check_paragraph_lengths() 