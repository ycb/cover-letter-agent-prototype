#!/usr/bin/env python3
"""
OpenAI-powered onboarding and effectiveness analysis for any user.
Enhanced with proper data model: Sources of Truth vs Staging Areas.
Refactored for multi-user, per-job examples, public/private links, and additive knowledge management.
"""
import sys
import os
import argparse
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml
from datetime import datetime
from agents.resume_parser import ResumeParser
from agents.external_profiles import fetch_public_profile, extract_linkedin_summary
import openai
import re
import dataclasses

# --- User Setup ---
def get_user_id():
    parser = argparse.ArgumentParser(description="Onboarding analysis for any user")
    parser.add_argument("--user", "-u", required=False, help="User ID (matches users/[id]/)")
    args, _ = parser.parse_known_args()
    user_id = args.user or os.environ.get("USER_ID", "peter")
    return user_id

USER_ID = get_user_id()
USER_DIR = f"users/{USER_ID}"
WORK_HISTORY_PATH = f"{USER_DIR}/work_history.yaml"
CONFIG_PATH = f"{USER_DIR}/config.yaml"
TMP_OUT_PATH = f"{USER_DIR}/onboarding_analysis_tmp.yaml"

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Load Data ---
def load_yaml_dict(path):
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except FileNotFoundError:
        return {}

def load_yaml_list(path):
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data if data is not None else []
    except FileNotFoundError:
        return []

def load_work_history():
    return load_yaml_list(WORK_HISTORY_PATH)

def save_work_history(data):
    with open(WORK_HISTORY_PATH, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

# --- Sources of Truth ---
def load_sources_of_truth():
    sources = {}
    work_history = load_work_history()
    sources['work_history'] = work_history
    config = load_yaml_dict(CONFIG_PATH)
    sources['config'] = config
    return sources

def extract_source_of_truth_content(sources):
    existing_content = set()
    work_history = sources.get('work_history', [])
    for job in work_history:
        for example in job.get('examples', []):
            for field in ['text', 'title', 'description', 'content']:
                if example.get(field):
                    existing_content.add(str(example[field]).lower().strip())
            # Expanded case study
            ecs = example.get('expanded_case_study')
            if ecs and ecs.get('url'):
                existing_content.add(ecs['url'].lower().strip())
            # Supporting artifacts
            for art in example.get('supporting_artifacts', []):
                if art.get('url'):
                    existing_content.add(art['url'].lower().strip())
    return existing_content

# --- Staging Areas (placeholder, should be replaced with Drive/Sheets integration) ---
def load_staging_areas():
    # Load from the new private artifacts file
    staging_path = f"{USER_DIR}/staging/private_artifacts.yaml"
    return load_yaml_list(staging_path)

def detect_net_new_content(sources_of_truth, staging_areas):
    existing_content = extract_source_of_truth_content(sources_of_truth)
    net_new_items = []
    for item in staging_areas:
        item_texts = []
        for field in ['text', 'title', 'description', 'content']:
            if item.get(field):
                item_texts.append(str(item[field]).lower().strip())
        is_new = True
        for text in item_texts:
            if text in existing_content or any(existing in text for existing in existing_content):
                is_new = False
                break
        if is_new:
            net_new_items.append(item)
    return net_new_items

# --- Additive Knowledge Management ---
def add_examples_to_work_history(work_history, net_new_items):
    updated = False
    for new_example in net_new_items:
        company = new_example.get('company')
        if not company:
            continue
        # Find job entry
        job = next((j for j in work_history if j.get('company') == company), None)
        if not job:
            continue
        # De-duplication: only add if not near-verbatim repeat for this job/type
        existing_texts = [e.get('text', '').lower().strip() for e in job.get('examples', [])]
        if new_example.get('text', '').lower().strip() in existing_texts:
            continue
        # Ensure schema fields
        example = {
            'id': new_example.get('id', f"{company.lower().replace(' ', '_')}_{len(job.get('examples', []))+1}"),
            'type': new_example.get('type', 'summary'),
            'text': new_example.get('text', ''),
            'expanded_case_study': new_example.get('expanded_case_study', None),
            'supporting_artifacts': new_example.get('supporting_artifacts', []),
            'tags': new_example.get('tags', []),
        }
        job.setdefault('examples', []).append(example)
        updated = True
    return updated, work_history

# --- Main Analysis ---
def main():
    print(f"\n=== ONBOARDING ANALYSIS FOR USER: {USER_ID} ===")
    work_history = load_work_history()
    print(f"Loaded work history: {len(work_history)} jobs")
    sources_of_truth = load_sources_of_truth()
    staging_areas = load_staging_areas()
    print(f"Loaded {len(staging_areas)} staged net-new items")
    net_new_items = detect_net_new_content(sources_of_truth, staging_areas)
    print(f"Detected {len(net_new_items)} net-new items")
    updated, updated_work_history = add_examples_to_work_history(work_history, net_new_items)
    if updated:
        save_work_history(updated_work_history)
        print(f"Added {len(net_new_items)} new examples to work_history.yaml")
    else:
        print("No new examples added (all were duplicates or missing company)")
    # Output summary
    for job in updated_work_history:
        print(f"\nCompany: {job.get('company')}")
        for ex in job.get('examples', []):
            print(f"  - {ex.get('id')}: {ex.get('type')} | {ex.get('text')[:60]}...")
            ecs = ex.get('expanded_case_study')
            if ecs:
                print(f"    Expanded Case Study: {ecs.get('url')} ({ecs.get('visibility')})")
            for art in ex.get('supporting_artifacts', []):
                print(f"    Artifact: {art.get('title')} ({art.get('visibility')}) -> {art.get('url')}")
    # --- Cover Letters Summary ---
    import os
    cover_letters_path = f"users/{USER_ID}/cover_letters.yaml"
    if os.path.exists(cover_letters_path):
        import yaml
        with open(cover_letters_path, 'r') as f:
            cover_letters = yaml.safe_load(f) or []
        print(f"\n=== COVER LETTERS ({len(cover_letters)}) ===")
        for cl in cover_letters:
            print(f"- {cl.get('company', 'Unknown')} | {cl.get('url', '')}")
    print("\n=== ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    main() 