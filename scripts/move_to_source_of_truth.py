#!/usr/bin/env python3
"""
Move Refined Stories to Source of Truth (work_history.yaml, per-job, per-example, multi-user)
"""
import sys
import os
import argparse
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml
from datetime import datetime

def get_user_id():
    parser = argparse.ArgumentParser(description="Move refined stories to source of truth")
    parser.add_argument("--user", "-u", required=False, help="User ID (matches users/[id]/)")
    args, _ = parser.parse_known_args()
    user_id = args.user or os.environ.get("USER_ID", "peter")
    return user_id

USER_ID = get_user_id()
USER_DIR = f"users/{USER_ID}"
REFINED_PATH = f"{USER_DIR}/staging/refined_examples.yaml"
WORK_HISTORY_PATH = f"{USER_DIR}/work_history.yaml"

# --- Loaders ---
def load_work_history():
    try:
        with open(WORK_HISTORY_PATH, 'r') as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError:
        return []

def save_work_history(data):
    with open(WORK_HISTORY_PATH, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False)
    print(f"✅ work_history.yaml updated: {WORK_HISTORY_PATH}")

def load_refined():
    try:
        with open(REFINED_PATH, 'r') as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"❌ Refined examples file not found: {REFINED_PATH}")
        return []

def save_refined(refined):
    with open(REFINED_PATH, 'w') as f:
        yaml.safe_dump(refined, f, sort_keys=False)

# --- Main Logic ---
def move_refined_to_work_history():
    work_history = load_work_history()
    refined = load_refined()
    if not refined:
        print("No refined examples to move.")
        return
    added_count = 0
    for story in refined:
        if story.get('status') == 'moved_to_source':
            continue
        company = story.get('company')
        if not company:
            continue
        # Find job entry
        job = next((j for j in work_history if j.get('company') == company), None)
        if not job:
            continue
        # De-duplication: only add if not near-verbatim repeat for this job/type
        existing_texts = [e.get('text', '').lower().strip() for e in job.get('examples', [])]
        if story.get('text', '').lower().strip() in existing_texts:
            continue
        # Build example
        example = {
            'id': story.get('id', f"{company.lower().replace(' ', '_')}_{len(job.get('examples', []))+1}"),
            'type': story.get('type', 'summary'),
            'text': story.get('text', ''),
            'expanded_case_study': story.get('expanded_case_study', None),
            'supporting_artifacts': story.get('supporting_artifacts', []),
            'tags': story.get('tags', []),
        }
        job.setdefault('examples', []).append(example)
        story['status'] = 'moved_to_source'
        story['moved_to_source_date'] = datetime.now().isoformat()
        added_count += 1
        print(f"✅ Added to {company}: {example['id']}")
    save_work_history(work_history)
    save_refined(refined)
    print(f"\n🎉 Successfully moved {added_count} stories to work_history.yaml")

if __name__ == "__main__":
    move_refined_to_work_history() 