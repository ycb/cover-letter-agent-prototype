#!/usr/bin/env python3
"""
Manual Correction Script
Corrects unverified claims in refined STAR stories with truthful information.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml

USER_ID = "peter"
USER_DIR = f"users/{USER_ID}"
REFINED_STORIES_PATH = f"{USER_DIR}/refined_star_stories.yaml"

def correct_enact_story():
    """Correct the Enact story with truthful information."""
    try:
        with open(REFINED_STORIES_PATH, 'r') as f:
            data = yaml.safe_load(f)
        
        refined_stories = data.get('refined_stories', [])
        
        for story in refined_stories:
            if story['original_story']['id'] == 'enact_key_metrics':
                # Correct the refined situation
                story['refined_content']['refined_situation'] = "In 2022, I led the product team at Enact, a home energy company, tasked with scaling our platform's market impact within a year."
                
                # Add a note about the correction
                story['refined_content']['refinement_notes'] = "CORRECTED: Updated to reflect that Enact is a home energy company, not an AI-powered product. This correction was made manually to ensure truthfulness."
                
                print("✅ Corrected Enact story with truthful information")
                break
        
        # Save the corrected data
        with open(REFINED_STORIES_PATH, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print(f"📁 Updated file: {REFINED_STORIES_PATH}")
        
    except FileNotFoundError:
        print(f"❌ Refined stories file not found: {REFINED_STORIES_PATH}")
    except Exception as e:
        print(f"❌ Error correcting story: {e}")

if __name__ == "__main__":
    correct_enact_story() 