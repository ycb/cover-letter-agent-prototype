import json
import os
import re
from typing import Dict, List, Tuple

import yaml

KEY_CATEGORIES = ["tools", "team_dynamics", "domain_knowledge", "soft_skills", "responsibilities", "outcomes"]

BLURB_DB_PATH = os.path.join(os.path.dirname(__file__), "../data/blurbs.yaml")
NEW_BLURBS_PATH = os.path.join(os.path.dirname(__file__), "../data/new_blurbs_staging.yaml")


# --- LLM Integration ---
def extract_requirements_llm(jd_text: str, api_key: str) -> Dict[str, List[str]]:
    import openai

    # Validate API key format
    from core.security import get_security_manager

    security_manager = get_security_manager()

    if not security_manager.validate_secret_format("OPENAI_API_KEY", api_key):
        raise ValueError("Invalid OpenAI API key format")

    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
Extract all explicit and implicit requirements from this job description. 
Categorize them as: tools, team_dynamics, domain_knowledge, soft_skills, responsibilities, outcomes.
Output as JSON with each category as a list of strings.
Job Description:
{jd_text}
"""
    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0)
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from OpenAI API for requirements extraction.")
    try:
        return json.loads(content)
    except Exception:
        # Try to extract JSON from the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(content[start:end])
        raise


def gap_analysis_llm(jd_requirements: Dict[str, List[str]], cover_letter: str, api_key: str) -> Dict[str, Tuple[str, str]]:
    import openai

    # Validate API key format
    from core.security import get_security_manager

    security_manager = get_security_manager()

    if not security_manager.validate_secret_format("OPENAI_API_KEY", api_key):
        raise ValueError("Invalid OpenAI API key format")

    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
Given these job requirements (JSON) and this cover letter, for each requirement, state if it is fully covered, partially covered, or missing in the letter. Output as a JSON object where each requirement is a key and the value is an object with 'status' (one of '✅', '⚠️', '❌') and 'recommendation' (a short suggestion or comment).
Requirements: {json.dumps(jd_requirements)}
Cover Letter: {cover_letter}
"""
    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0)
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from OpenAI API for gap analysis.")
    try:
        return json.loads(content)
    except Exception:
        # Try to extract JSON from the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(content[start:end])
        raise


# --- Existing extraction and gap analysis code below ---
def extract_requirements(jd_text: str) -> Dict[str, List[str]]:
    """Extract requirements from JD text into key categories."""
    # Placeholder: simple keyword/regex extraction
    reqs = {cat: [] for cat in KEY_CATEGORIES}
    lines = jd_text.split("\n")
    for line in lines:
        l = line.lower()
        if any(tool in l for tool in ["python", "sql", "figma"]):
            for tool in ["Python", "SQL", "Figma"]:
                if tool.lower() in l and tool not in reqs["tools"]:
                    reqs["tools"].append(tool)
        if "engineer" in l or "team" in l:
            if "transmission engineers" in l and "transmission engineers" not in reqs["team_dynamics"]:
                reqs["team_dynamics"].append("transmission engineers")
            if "small team" in l and "small teams" not in reqs["team_dynamics"]:
                reqs["team_dynamics"].append("small teams")
        if "grid interconnection" in l and "grid interconnection" not in reqs["domain_knowledge"]:
            reqs["domain_knowledge"].append("grid interconnection")
        for soft in ["mission", "ownership", "curiosity"]:
            if soft in l and soft not in reqs["soft_skills"]:
                reqs["soft_skills"].append(soft)
        if "user interview" in l and "user interviews" not in reqs["responsibilities"]:
            reqs["responsibilities"].append("user interviews")
        if "launch" in l and "mvp" in l and "launch MVPs" not in reqs["responsibilities"]:
            reqs["responsibilities"].append("launch MVPs")
        if "accelerate" in l and "renewable" in l and "accelerate renewable deployment" not in reqs["outcomes"]:
            reqs["outcomes"].append("accelerate renewable deployment")
    return reqs


def parse_cover_letter(letter_text: str) -> str:
    return letter_text.lower()


def load_blurb_database(path=BLURB_DB_PATH) -> List[Dict]:
    with open(path) as f:
        data = yaml.safe_load(f)
    # Flatten all blurbs into a list
    all_blurbs = []
    for section in data.values():
        if isinstance(section, list):
            all_blurbs.extend(section)
    return all_blurbs


def gap_analysis(jd_reqs: Dict[str, List[str]], cover_letter: str, blurb_db: List[Dict]) -> Dict[str, Tuple[str, str]]:
    """Return {requirement: (status, recommendation)}"""
    report = {}
    for cat, items in jd_reqs.items():
        for item in items:
            status = "❌"
            recommendation = ""
            # Check if covered in any blurb
            for blurb in blurb_db:
                if item.lower() in [t.lower() for t in blurb.get("tags", [])] or item.lower() in blurb.get("text", "").lower():
                    if item.lower() in cover_letter:
                        status = "✅"
                        recommendation = "Covered in letter."
                    else:
                        status = "⚠️"
                        recommendation = f"Mentioned in blurb but not in letter—consider adding: {blurb['id']}"
                    break
            if status == "❌" and item.lower() in cover_letter:
                status = "⚠️"
                recommendation = "Implied in letter, but not specific."
            if status == "❌":
                recommendation = f"Missing—ask user if they want to add or address: {item}"
            report[item] = (status, recommendation)
    return report


def prompt_user_for_gaps(report: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
    """Interactively prompt user for each gap. Return {item: user_action}."""
    user_actions = {}
    print("\nGAP DETECTION SUMMARY:\n")
    print("{:<25} {:<4} Recommendation".format("Requirement", "Status"))
    print("-" * 60)
    for req, (status, rec) in report.items():
        print(f"{req:<25} {status:<4} {rec}")
        if status == "❌" or status == "⚠️":
            print("[A]dd blurb  [W]rite custom blurb  [S]kip  [F]uture reuse")
            action = input(f"Action for '{req}': ").strip().lower()
            user_actions[req] = action
    return user_actions


def add_new_blurb(item: str, action: str):
    """Add a new blurb to the staging file based on user action."""
    if action == "a":
        text = input(f"Enter blurb text for '{item}': ")
        tags = input(f"Enter tags for '{item}' (comma-separated): ").split(",")
    elif action == "w":
        text = input(f"Write a custom blurb for '{item}': ")
        tags = input(f"Enter tags for '{item}' (comma-separated): ").split(",")
    else:
        return
    new_blurb = {"id": item.replace(" ", "_").lower(), "tags": [t.strip() for t in tags if t.strip()], "text": text.strip()}
    # Append to staging file
    if os.path.exists(NEW_BLURBS_PATH):
        with open(NEW_BLURBS_PATH) as f:
            data = yaml.safe_load(f) or []
    else:
        data = []
    data.append(new_blurb)
    with open(NEW_BLURBS_PATH, "w") as f:
        yaml.safe_dump(data, f)
    print(f"Added new blurb for '{item}' to staging.")


def regenerate_cover_letter(cover_letter: str, user_actions: Dict[str, str], new_blurbs: List[Dict]) -> str:
    """Regenerate the cover letter by appending new blurbs as needed."""
    additions = []
    for item, action in user_actions.items():
        if action in ["a", "w"]:
            for blurb in new_blurbs:
                if blurb["id"] == item.replace(" ", "_").lower():
                    additions.append(blurb["text"])
    if additions:
        cover_letter += "\n\n" + "\n\n".join(additions)
    return cover_letter


def auto_review(jd_text: str, cover_letter: str) -> List[str]:
    """Automatic review: suggest improvements to increase interview odds."""
    suggestions = []
    if len(cover_letter.split()) < 300:
        suggestions.append("Cover letter may be too brief—consider adding more detail.")
    if len(cover_letter.split()) > 600:
        suggestions.append("Cover letter may be too long—consider condensing.")
    if not re.search(r"\d+%", cover_letter):
        suggestions.append("Add more quantified impact metrics.")
    # Check for missing requirements again
    reqs = extract_requirements(jd_text)
    for cat, items in reqs.items():
        for item in items:
            if item.lower() not in cover_letter:
                suggestions.append(f"Consider addressing: {item}")
    return suggestions


try:
    import openai  # type: ignore
except ImportError:
    openai = None


def main(jd_path, letter_path, blurb_db_path=BLURB_DB_PATH, api_key=None):
    with open(jd_path) as f:
        jd_text = f.read()
    with open(letter_path) as f:
        letter_text = f.read()
    blurb_db = load_blurb_database(blurb_db_path)
    # Use LLM if API key is provided
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("\n[LLM] Extracting requirements from JD...")
        jd_reqs = extract_requirements_llm(jd_text, api_key)
        print("[LLM] Running gap analysis...")
        gap_report = gap_analysis_llm(jd_reqs, letter_text, api_key)
        print("\nGAP DETECTION SUMMARY (LLM):\n")
        print("{:<25} {:<4} Recommendation".format("Requirement", "Status"))
        print("-" * 60)
        for req, info in gap_report.items():
            if isinstance(info, dict):
                print(f"{req:<25} {info.get('status', ''):<4} {info.get('recommendation', '')}")
            else:
                # fallback for unexpected format
                print(f"{req:<25} {info}")
        # Optionally, prompt user for actions as before
        user_actions = prompt_user_for_gaps(gap_report)
        for item, action in user_actions.items():
            if action in ["a", "w"]:
                add_new_blurb(item, action)
        # Load new blurbs
        if os.path.exists(NEW_BLURBS_PATH):
            with open(NEW_BLURBS_PATH) as f:
                new_blurbs = yaml.safe_load(f) or []
        else:
            new_blurbs = []
        # Regenerate cover letter
        new_letter = regenerate_cover_letter(letter_text, user_actions, new_blurbs)
        print("\n--- NEW DRAFT COVER LETTER ---\n")
        print(new_letter)
        # Auto review
        suggestions = auto_review(jd_text, new_letter)
        print("\n--- AUTO REVIEW SUGGESTIONS ---\n")
        for s in suggestions:
            print(f"- {s}")
    else:
        print("\n[No OpenAI API key found. Using regex/keyword extraction.]")
        jd_reqs = extract_requirements(jd_text)
        report = gap_analysis(jd_reqs, letter_text, blurb_db)
        print("\nGAP DETECTION SUMMARY:\n")
        print("{:<25} {:<4} Recommendation".format("Requirement", "Status"))
        print("-" * 60)
        for req, info in report.items():
            if isinstance(info, tuple):
                status, rec = info
                print(f"{req:<25} {status:<4} {rec}")
            else:
                print(f"{req:<25} {info}")
        # Optionally, prompt user for actions as before
        user_actions = prompt_user_for_gaps(report)
        for item, action in user_actions.items():
            if action in ["a", "w"]:
                add_new_blurb(item, action)
        # Load new blurbs
        if os.path.exists(NEW_BLURBS_PATH):
            with open(NEW_BLURBS_PATH) as f:
                new_blurbs = yaml.safe_load(f) or []
        else:
            new_blurbs = []
        # Regenerate cover letter
        new_letter = regenerate_cover_letter(letter_text, user_actions, new_blurbs)
        print("\n--- NEW DRAFT COVER LETTER ---\n")
        print(new_letter)
        # Auto review
        suggestions = auto_review(jd_text, new_letter)
        print("\n--- AUTO REVIEW SUGGESTIONS ---\n")
        for s in suggestions:
            print(f"- {s}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python gap_analysis.py <job_description.txt> <assembled_cover_letter.txt> [OPENAI_API_KEY]")
        print("Set OPENAI_API_KEY as an environment variable or pass as third argument.")
        sys.exit(1)
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    # Ensure blurb_db_path is always a string
    main(sys.argv[1], sys.argv[2], BLURB_DB_PATH, api_key)
