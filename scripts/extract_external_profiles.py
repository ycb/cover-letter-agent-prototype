#!/usr/bin/env python3
"""
Extract summaries from external profiles (LinkedIn, portfolio, blog, GitHub) for a user.
"""
import sys
import os
import yaml
from agents.external_profiles import fetch_public_profile, extract_linkedin_summary

USER_ID = "peter"
CONFIG_PATH = f"users/{USER_ID}/config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

urls = config.get("external_profiles", {})
summaries = {}

for key, url in urls.items():
    if not url:
        continue
    print(f"Fetching {key}: {url}")
    raw_text = fetch_public_profile(url)
    if raw_text:
        if "linkedin" in key:
            summaries[key] = extract_linkedin_summary(raw_text)
        else:
            summaries[key] = raw_text[:1500]

print("\n--- External Summaries Extracted ---")
for k, v in summaries.items():
    print(f"\n[{k.upper()}]\n{v[:300]}...") 