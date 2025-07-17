#!/usr/bin/env python3
"""
LLM-powered STAR story extraction from staged artifacts.
Reads users/{user}/staging/private_artifacts.yaml, sends each artifact's text to OpenAI, parses YAML output, and writes extracted stories to users/{user}/staging/extracted_stories.yaml.
"""
import os
import sys
import yaml
import openai
from dotenv import load_dotenv
from pathlib import Path
import argparse
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT = '''Extract all distinct STAR stories from the following text. A STAR story should describe a specific professional challenge, project, or achievement, and include as much detail as possible for each of the four elements:

- situation: The context or challenge faced
- task: The specific responsibility or goal
- action: What was done to address the situation
- result: The measurable or meaningful outcome

If any element is missing or unclear, leave it blank but do not invent details. If multiple stories are present, extract each as a separate YAML object in a list.

Output ONLY valid YAML in the following format:

---
- situation: ...
  task: ...
  action: ...
  result: ...
- situation: ...
  task: ...
  action: ...
  result: ...
---

Here is the text to analyze:
"""
{artifact_text}
"""
'''

def get_user_id():
    parser = argparse.ArgumentParser(description="STAR extraction for any user")
    parser.add_argument("--user", "-u", required=False, help="User ID (matches users/[id]/)")
    args, _ = parser.parse_known_args()
    user_id = args.user or os.environ.get("USER_ID", "peter")
    return user_id

USER_ID = get_user_id()
USER_DIR = f"users/{USER_ID}"
STAGING_DIR = f"{USER_DIR}/staging"
ARTIFACTS_PATH = f"{STAGING_DIR}/private_artifacts.yaml"
OUTPUT_PATH = f"{STAGING_DIR}/extracted_stories.yaml"

# Load artifacts
def load_yaml_list(path):
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data if data is not None else []
    except FileNotFoundError:
        return []

def save_yaml_list(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def extract_star_stories(text):
    prompt = PROMPT.format(artifact_text=text)
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career coach and content analyst. Your job is to extract STAR stories (Situation, Task, Action, Result) from any professional document, regardless of format or structure. Output only structured YAML as specified."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        # Remove any leading/trailing code block markers
        if content.startswith('```yaml'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        # Parse YAML
        stories = yaml.safe_load(content)
        if not isinstance(stories, list):
            return []
        # Filter out empty stories
        return [s for s in stories if any(s.get(k) for k in ['situation','task','action','result'])]
    except Exception as e:
        print(f"[ERROR] LLM extraction failed: {e}")
        return []

def main():
    artifacts = load_yaml_list(ARTIFACTS_PATH)
    all_stories = []
    for i, artifact in enumerate(artifacts):
        text = artifact.get('text')
        if not text or not text.strip():
            continue
        print(f"\n[INFO] Extracting STAR stories from artifact {i+1}/{len(artifacts)}: {artifact.get('file_name','(no name)')}")
        stories = extract_star_stories(text)
        if stories:
            for s in stories:
                s['source_file'] = artifact.get('file_name','')
                s['source_url'] = artifact.get('source_url','')
                s['company'] = artifact.get('company','')
            all_stories.extend(stories)
            print(f"  -> Extracted {len(stories)} stories.")
        else:
            print("  -> No stories found.")
        time.sleep(1.5)  # avoid rate limits
    save_yaml_list(OUTPUT_PATH, all_stories)
    print(f"\n[SUMMARY] Extracted {len(all_stories)} STAR stories from {len(artifacts)} artifacts. Saved to {OUTPUT_PATH}.")

if __name__ == "__main__":
    main() 