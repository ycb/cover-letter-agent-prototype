#!/usr/bin/env python3
"""
Cover Letter Agent Runner
========================

Command-line interface for the cover letter agent.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional
import os

# --- Ensure .env is always loaded ---
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path)
except ImportError:
    pass

# --- Set API key directly to avoid tab character issue ---
import os
if not os.environ.get('OPENAI_API_KEY'):
    # Set the API key directly if not already set
    os.environ['OPENAI_API_KEY'] = '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'

# --- Fail fast if API key is missing ---
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not found.\nPlease create a .env file in the project root with the line: OPENAI_API_KEY=sk-...\nSee .env.example for details.\n")
    sys.exit(1)
else:
    print(f"[DEBUG] OPENAI_API_KEY loaded: ...{api_key[-4:]}")

# Add the agents directory to the path
sys.path.append(str(Path(__file__).parent.parent / "agents"))

from cover_letter_agent import CoverLetterAgent
# Import gap analysis LLM functions
from gap_analysis import gap_analysis_llm, extract_requirements_llm


def load_job_description(file_path: Optional[str] = None, text: Optional[str] = None) -> str:
    """Load job description from file or text input."""
    if file_path:
        with open(file_path, 'r') as f:
            return f.read()
    elif text:
        return text
    else:
        print("Enter job description (press Ctrl+D when finished):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines)


def save_cover_letter(cover_letter: str, output_file: str):
    """Save cover letter to file."""
    with open(output_file, 'w') as f:
        f.write(cover_letter)
    print(f"Cover letter saved to: {output_file}")


def print_job_analysis(job):
    """Print detailed job analysis."""
    print("\n" + "="*60)
    print("JOB ANALYSIS")
    print("="*60)
    print(f"Company: {job.company_name}")
    print(f"Position: {job.job_title}")
    print(f"Job Type: {job.job_type}")
    print(f"Score: {job.score:.2f}")
    print(f"Go/No-Go: {'✅ GO' if job.go_no_go else '❌ NO-GO'}")
    print(f"Keywords Found: {', '.join(job.keywords)}")
    
    if job.extracted_info['requirements']:
        print(f"\nRequirements Found: {len(job.extracted_info['requirements'])}")
        for req in job.extracted_info['requirements'][:3]:  # Show first 3
            print(f"  - {req}")
    
    if job.extracted_info['company_info']:
        print(f"\nCompany Info:")
        for key, value in job.extracted_info['company_info'].items():
            print(f"  - {key}: {value}")


def print_cover_letter(cover_letter: str):
    """Print formatted cover letter."""
    print("\n" + "="*60)
    print("GENERATED COVER LETTER")
    print("="*60)
    print(cover_letter)


def print_enhancement_suggestions(suggestions):
    """Print enhancement suggestions."""
    if not suggestions:
        print("\n✅ No enhancement suggestions - cover letter looks good!")
        return
    
    print("\n" + "="*60)
    print("ENHANCEMENT SUGGESTIONS")
    print("="*60)
    
    for i, suggestion in enumerate(suggestions, 1):
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        print(f"{i}. {priority_emoji.get(suggestion.priority, '⚪')} {suggestion.description}")
        print(f"   Category: {suggestion.category}")
        print(f"   Priority: {suggestion.priority}")
        print()


def print_enhancement_log(agent, status: Optional[str] = None):
    """Print enhancement log."""
    suggestions = agent.get_enhancement_suggestions(status)
    
    if not suggestions:
        print("No enhancement suggestions found.")
        return
    
    print("\n" + "="*60)
    print("ENHANCEMENT LOG")
    print("="*60)
    
    for suggestion in suggestions:
        status_emoji = {
            'open': '⏳',
            'accepted': '✅',
            'rejected': '❌'
        }
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        
        print(f"{status_emoji.get(suggestion['status'], '❓')} {priority_emoji.get(suggestion['priority'], '⚪')} {suggestion['description']}")
        print(f"   Job ID: {suggestion['job_id']}")
        print(f"   Category: {suggestion['category']}")
        print(f"   Status: {suggestion['status']}")
        if suggestion['notes']:
            print(f"   Notes: {suggestion['notes']}")
        print()


def print_job_targeting(targeting):
    """Print job targeting evaluation results."""
    print("\n" + "-"*60)
    print("JOB TARGETING EVALUATION")
    print("-"*60)
    if not targeting:
        print("No targeting criteria loaded.")
        return
    print(f"Targeting Score: {targeting.targeting_score:.2f}")
    print(f"Targeting Go/No-Go: {'✅ GO' if targeting.targeting_go_no_go else '❌ NO-GO'}")
    print(f"Title Match: {'✅' if targeting.title_match else '❌'} ({targeting.title_category})")
    print(f"Comp Match: {'✅' if targeting.comp_match else '❌'}")
    print(f"Location Match: {'✅' if targeting.location_match else '❌'} ({targeting.location_type})")
    print(f"Role Type Matches: {', '.join(targeting.role_type_matches) if targeting.role_type_matches else 'None'}")
    print(f"Company Stage Match: {'✅' if targeting.company_stage_match else '❌'}")
    print(f"Business Model Match: {'✅' if targeting.business_model_match else '❌'}")


def print_case_studies(case_studies):
    """Print relevant case studies for the job."""
    if not case_studies:
        print("\n📚 No relevant case studies found.")
        return
    
    print("\n" + "-"*60)
    print("RELEVANT CASE STUDIES")
    print("-"*60)
    
    for i, case_study in enumerate(case_studies, 1):
        print(f"{i}. {case_study['name']}")
        print(f"   Type: {case_study['type']}")
        print(f"   Description: {case_study['description']}")
        
        if case_study['type'] == 'url':
            print(f"   URL: {case_study['url']}")
        elif case_study['type'] == 'file':
            print(f"   File: {case_study['file_path']}")
        elif case_study['type'] == 'google_drive':
            print(f"   Material Type: {case_study['material_type']}")
        
        if 'tags' in case_study:
            print(f"   Tags: {', '.join(case_study['tags'])}")
        print()


def print_strategic_insights(insights):
    """Print strategic insights for cover letter generation."""
    if not insights:
        return
    
    print("\n" + "-"*60)
    print("STRATEGIC INSIGHTS")
    print("-"*60)
    
    for i, insight in enumerate(insights, 1):
        confidence_emoji = "🟢" if insight.confidence > 0.8 else "🟡" if insight.confidence > 0.6 else "🔴"
        print(f"{i}. {confidence_emoji} {insight.description}")
        print(f"   Source: {insight.source}")
        print(f"   Action: {insight.recommended_action}")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Cover Letter Agent")
    parser.add_argument("--user", "-u", required=True, help="User ID (matches users/[id]/)")
    parser.add_argument("--input-file", "-i", help="Input job description file")
    parser.add_argument("--jd", help="Input job description file (alias for --input-file)")
    parser.add_argument("--text", "-t", help="Job description text")
    parser.add_argument("--output-file", "-o", help="Output cover letter file")
    parser.add_argument("--data-dir", "-d", default="data", help="Data directory")
    parser.add_argument("--log", action="store_true", help="Show enhancement log")
    parser.add_argument("--log-status", choices=["open", "accepted", "rejected"], 
                       help="Filter enhancement log by status")
    parser.add_argument("--update-status", nargs=3, 
                       metavar=("JOB_ID", "ENHANCEMENT_TYPE", "STATUS"),
                       help="Update enhancement suggestion status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--explain", action="store_true", help="Show go/no-go reasoning and blurbs selected")
    parser.add_argument("--track-enhance", action="store_true", help="Log enhancement suggestions")
    parser.add_argument("--debug", action="store_true", help="Print matching scores and filtering steps")
    parser.add_argument('--interactive', action='store_true', help='Enable step-by-step user confirmation for extraction and gap-filling')
    args = parser.parse_args()

    # Support --jd as alias for --input-file
    input_file = args.input_file or args.jd

    # Validate user exists
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from core.user_context import validate_user_exists, list_available_users
    
    if not validate_user_exists(args.user):
        print(f"❌ User '{args.user}' not found.")
        print("Available users:")
        for user in list_available_users():
            print(f"  - {user}")
        print(f"\nTo create a new user: python3 init_user.py {args.user}")
        return
    
    # Initialize agent with user context
    agent = CoverLetterAgent(user_id=args.user)

    # Handle enhancement log commands
    if args.log:
        print_enhancement_log(agent, args.log_status)
        return

    if args.update_status:
        job_id, enhancement_type, status = args.update_status
        agent.update_enhancement_status(job_id, enhancement_type, status)
        print(f"Updated {enhancement_type} for job {job_id} to status: {status}")
        return

    # Load job description
    job_text = load_job_description(input_file, args.text)

    if not job_text.strip():
        print("Error: No job description provided.")
        return

    # Use interactive mode if requested
    interactive = getattr(args, 'interactive', False)

    # Process job description with debug/explain/track flags
    if any([args.debug, args.explain, args.track_enhance]):
        result = agent.process_job_description(
            job_text,
            debug=args.debug,
            explain=args.explain,
            track_enhance=args.track_enhance,
            interactive=interactive
        )
        if len(result) == 4:
            job, cover_letter, suggestions, debug_info = result
        else:
            job, cover_letter, suggestions = result
            debug_info = None
    else:
        job, cover_letter, suggestions = agent.process_job_description(job_text)
        debug_info = None

    # Print results
    print_job_analysis(job)
    if job.targeting:
        print_job_targeting(job.targeting)

    # Get and display relevant case studies
    case_studies = agent.get_case_studies(job.keywords)
    print_case_studies(case_studies)

    # Get and display strategic insights
    if hasattr(agent, 'context_analyzer') and agent.context_analyzer:
        contextual_analysis = agent.analyze_contextual_data(job_text)
        if contextual_analysis.get('strategic_insights'):
            print_strategic_insights(contextual_analysis['strategic_insights'])

    if args.explain or args.debug:
        # Print go/no-go reasoning, blurb selection, and filtering steps
        if debug_info:
            print("\n--- DEBUG/EXPLAIN INFO ---")
            if 'go_no_go_reasoning' in debug_info:
                print(f"Go/No-Go Reasoning: {debug_info['go_no_go_reasoning']}")
            if 'blurb_selection' in debug_info:
                print(f"Blurb Selection: {debug_info['blurb_selection']}")
            if 'blurb_filtering' in debug_info:
                print(f"Blurb Filtering Steps: {debug_info['blurb_filtering']}")

    if cover_letter:
        print_cover_letter(cover_letter)
        print_enhancement_suggestions(suggestions)
        
        # Check if uploaded to Google Drive
        if hasattr(agent, 'google_drive') and agent.google_drive and agent.google_drive.available:
            print("\n📁 Cover letter draft automatically saved to Google Drive drafts folder")
        
        # Save to file if requested
        if args.output_file:
            save_cover_letter(cover_letter, args.output_file)
    else:
        print("\n❌ No cover letter generated - job does not meet criteria.")
        print(f"   Score: {job.score:.2f} (minimum: {agent.logic['go_no_go']['minimum_total_score']})")
        print(f"   Keywords: {len(job.keywords)} (minimum: {agent.logic['go_no_go']['minimum_keywords']})")
        return

    # --- LLM-powered gap analysis and regeneration ---
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        try:
            print("\n[LLM] Running gap analysis and regenerating cover letter with gap-filling blurbs...\n")
            jd_reqs = extract_requirements_llm(job_text, api_key)
            gap_report = gap_analysis_llm(jd_reqs, cover_letter, api_key)
            # Extract missing/partial requirements
            missing_requirements = [req for req, info in gap_report.items() if isinstance(info, dict) and info.get('status') in ['❌', '⚠️']]
            if missing_requirements:
                improved_cover_letter = agent.generate_cover_letter(job, agent.select_blurbs(job), missing_requirements)
                print("\n============================================================")
                print("IMPROVED COVER LETTER WITH GAP-FILLING BLURBS")
                print("============================================================")
                print(improved_cover_letter)
                if args.output_file:
                    save_cover_letter(improved_cover_letter, args.output_file)
            else:
                print("\nNo additional gaps detected by LLM. No further blurbs added.")
        except Exception as e:
            print(f"[LLM GAP ANALYSIS ERROR] {e}")
    else:
        print("\n[No OpenAI API key found. Skipping LLM-powered gap analysis and regeneration.]")

if __name__ == "__main__":
    main() 