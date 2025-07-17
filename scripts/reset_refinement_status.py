#!/usr/bin/env python3
"""
Reset Refinement Status Script
Resets all refined STAR stories back to pending refinement status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml

USER_ID = "peter"
USER_DIR = f"users/{USER_ID}"
APPROVED_STORIES_PATH = f"{USER_DIR}/approved_star_stories.yaml"

def reset_refinement_status():
    """Reset all refined or moved-to-source stories back to pending refinement status."""
    try:
        with open(APPROVED_STORIES_PATH, 'r') as f:
            data = yaml.safe_load(f)
        
        approved_stories = data.get('approved_stories', [])
        reset_count = 0
        
        for story in approved_stories:
            if story.get('status') in ['refined', 'moved_to_source']:
                story['status'] = 'pending_refinement'
                # Remove the previous LLM refinement and move date
                if 'llm_refined_version' in story:
                    del story['llm_refined_version']
                if 'moved_to_source_date' in story:
                    del story['moved_to_source_date']
                reset_count += 1
        
        # Save the updated data
        with open(APPROVED_STORIES_PATH, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Reset {reset_count} stories to pending refinement status")
        print(f"📁 Updated file: {APPROVED_STORIES_PATH}")
        
        return reset_count
        
    except FileNotFoundError:
        print(f"❌ Approved stories file not found: {APPROVED_STORIES_PATH}")
        return 0
    except Exception as e:
        print(f"❌ Error resetting refinement status: {e}")
        return 0

if __name__ == "__main__":
    reset_count = reset_refinement_status()
    if reset_count > 0:
        print(f"\n🔄 Ready to re-refine {reset_count} stories with updated voice preferences") 