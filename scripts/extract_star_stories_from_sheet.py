#!/usr/bin/env python3
"""
Extract STAR stories from a Google Sheet using LLM parsing.
Reads all rows from the specified sheet, sends to LLM for STAR extraction, and writes results to a YAML file in staging.
"""
import os
import sys
import argparse
import yaml
from dotenv import load_dotenv
import openai
from pathlib import Path
import time

# Google Sheets API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("Google Sheets API dependencies not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]

PROMPT = '''Extract all distinct STAR stories from the following spreadsheet content. A STAR story should describe a specific professional challenge, project, or achievement, and include as much detail as possible for each of the four elements:

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

Here is the spreadsheet content to analyze (each row is a list of cell values):
"""
{sheet_content}
"""
'''

def get_args():
    parser = argparse.ArgumentParser(description="Extract STAR stories from a Google Sheet using LLM parsing.")
    parser.add_argument('--user', '-u', required=True, help='User ID (matches users/[id]/)')
    parser.add_argument('--sheet_id', required=True, help='Google Sheet ID')
    parser.add_argument('--sheet_name', required=False, help='Sheet/tab name(s), comma-separated (default: config or first tab)')
    parser.add_argument('--output', required=False, help='Output YAML file (default: users/{user}/staging/star_stories_to_refine.yaml)')
    parser.add_argument('--credentials', required=False, default='credentials.json', help='Google API credentials file')
    return parser.parse_args()

def load_star_tabs_from_config(user_dir):
    config_path = os.path.join(user_dir, 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Try the expected path
        tabs = config.get('google_drive', {}).get('spreadsheet_parsing', {}).get('star_stories', {}).get('tabs', [])
        if tabs:
            return tabs
        # Fallback: search for any 'tabs' key in the config
        def find_tabs(d):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k == 'tabs' and isinstance(v, list):
                        return v
                    found = find_tabs(v)
                    if found:
                        return found
            return []
        return find_tabs(config)
    except Exception:
        return []

def get_sheets_service(credentials_file):
    creds = None
    token_file = 'token.json'
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def read_sheet(sheet_id, sheet_name, credentials_file):
    service = get_sheets_service(credentials_file)
    # Get sheet metadata to find the first tab if not specified
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    if not sheet_name:
        sheet_name = meta['sheets'][0]['properties']['title']
    # Always use full column range
    range_name = f'{sheet_name}!A:Z'
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def extract_star_stories(sheet_content):
    # Format as a string for the LLM
    formatted = yaml.safe_dump(sheet_content, allow_unicode=True)
    prompt = PROMPT.format(sheet_content=formatted)
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career coach and content analyst. Your job is to extract STAR stories (Situation, Task, Action, Result) from any professional spreadsheet, regardless of format or structure. Output only structured YAML as specified."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
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
        # Try to parse as multiple YAML documents
        all_stories = []
        try:
            for doc in yaml.safe_load_all(content):
                if isinstance(doc, list):
                    for s in doc:
                        if isinstance(s, dict) and any(s.get(k) for k in ['situation','task','action','result']):
                            all_stories.append(s)
                elif isinstance(doc, dict) and any(doc.get(k) for k in ['situation','task','action','result']):
                    all_stories.append(doc)
        except Exception as e:
            print(f"[YAML ERROR] {e}\nRaw LLM output was:\n{content}\n---")
        return all_stories
    except Exception as e:
        print(f"[ERROR] LLM extraction failed: {e}")
        return []

def save_yaml_list(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def batch_rows(rows, batch_size):
    for i in range(0, len(rows), batch_size):
        yield rows[i:i+batch_size]

def main():
    args = get_args()
    user_dir = f"users/{args.user}"
    staging_dir = f"{user_dir}/staging"
    os.makedirs(staging_dir, exist_ok=True)
    output_path = args.output or f"{staging_dir}/star_stories_to_refine.yaml"
    # Determine tabs to process
    if args.sheet_name:
        tab_names = [t.strip() for t in args.sheet_name.split(',') if t]
    else:
        tab_names = load_star_tabs_from_config(user_dir)
    if not tab_names:
        print("[ERROR] No sheet/tab names provided or found in config.")
        sys.exit(1)
    all_stories = []
    batch_size = 15
    for tab in tab_names:
        print(f"[INFO] Reading sheet: {args.sheet_id} (tab: {tab})")
        sheet_content = read_sheet(args.sheet_id, tab, args.credentials)
        print(f"[INFO] Read {len(sheet_content)} rows from tab '{tab}'.")
        headers = sheet_content[0] if sheet_content else []
        for batch_num, batch in enumerate(batch_rows(sheet_content[1:], batch_size), 1):
            batch_rows_with_headers = [headers] + batch
            print(f"[INFO] Processing batch {batch_num} ({len(batch)} rows) from tab '{tab}'...")
            try:
                stories = extract_star_stories(batch_rows_with_headers)
                print(f"[INFO] Extracted {len(stories)} STAR stories from batch {batch_num}.")
                all_stories.extend(stories)
            except Exception as e:
                print(f"[ERROR] Batch {batch_num} failed: {e}")
            time.sleep(1.5)
    save_yaml_list(output_path, all_stories)
    print(f"[SUMMARY] Extracted {len(all_stories)} STAR stories from {len(tab_names)} tabs. Saved to {output_path}.")

if __name__ == "__main__":
    main() 