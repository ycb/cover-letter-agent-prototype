#!/usr/bin/env python3
"""
Analyze Blurb Lengths
Analyzes existing blurbs to determine average character count for refinement targets.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml

USER_ID = "peter"
USER_DIR = f"users/{USER_ID}"
BLURBS_PATH = f"{USER_DIR}/blurbs.yaml"

def analyze_blurb_lengths():
    """Analyze character counts of existing blurbs."""
    try:
        with open(BLURBS_PATH, 'r') as f:
            blurbs_data = yaml.safe_load(f)
        
        character_counts = []
        blurb_details = []
        
        # Analyze all sections
        for section_name, section_content in blurbs_data.items():
            if section_name == 'metadata':
                continue
                
            if isinstance(section_content, list):
                for blurb in section_content:
                    if 'text' in blurb:
                        char_count = len(blurb['text'])
                        character_counts.append(char_count)
                        blurb_details.append({
                            'section': section_name,
                            'id': blurb.get('id', 'unknown'),
                            'char_count': char_count,
                            'text': blurb['text'][:100] + "..." if len(blurb['text']) > 100 else blurb['text']
                        })
        
        if character_counts:
            avg_length = sum(character_counts) / len(character_counts)
            min_length = min(character_counts)
            max_length = max(character_counts)
            
            print(f"📊 Blurb Length Analysis:")
            print(f"  📝 Total blurbs analyzed: {len(character_counts)}")
            print(f"  📏 Average length: {avg_length:.0f} characters")
            print(f"  📏 Min length: {min_length} characters")
            print(f"  📏 Max length: {max_length} characters")
            print(f"  🎯 Target range: {min_length}-{max_length} characters")
            
            print(f"\n📋 Sample blurbs by length:")
            sorted_details = sorted(blurb_details, key=lambda x: x['char_count'])
            for detail in sorted_details[:5]:  # Show 5 shortest
                print(f"  • {detail['section']}/{detail['id']}: {detail['char_count']} chars")
            
            return int(avg_length)
        else:
            print("❌ No blurbs found to analyze")
            return 300  # Default fallback
            
    except FileNotFoundError:
        print(f"❌ Blurbs file not found: {BLURBS_PATH}")
        return 300  # Default fallback
    except Exception as e:
        print(f"❌ Error analyzing blurbs: {e}")
        return 300  # Default fallback

if __name__ == "__main__":
    target_length = analyze_blurb_lengths()
    print(f"\n🎯 Recommended target length: {target_length} characters") 