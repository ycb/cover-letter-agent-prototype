#!/usr/bin/env python3
"""
LLM Refinement Script for Approved STAR Stories
Refines approved STAR stories into high-impact format reflective of user's voice.
"""

import yaml
import openai
import os
from typing import List, Dict, Any
import json
import re

def load_config():
    """Load configuration from config.yaml"""
    with open('data/agent_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_blurbs():
    """Load approved examples from blurbs.yaml to calculate target length"""
    with open('data/blurbs.yaml', 'r') as f:
        blurbs = yaml.safe_load(f)
    
    # Get approved examples
    approved_examples = blurbs.get('examples', [])
    
    if not approved_examples:
        return 400  # Default if no examples
    
    # Calculate average character count
    total_chars = sum(len(example['text']) for example in approved_examples)
    avg_chars = total_chars // len(approved_examples)
    
    print(f"Found {len(approved_examples)} approved examples")
    print(f"Average character count: {avg_chars}")
    print(f"Character count range: {min(len(ex['text']) for ex in approved_examples)} - {max(len(ex['text']) for ex in approved_examples)}")
    
    return avg_chars

def detect_story_format(story_text: str) -> str:
    """Detect the format of a STAR story (STAR, SAR, SA, SR, AR, or mixed)"""
    if not story_text or not story_text.strip():
        return "empty"
    
    # Check for Results-only format
    if re.search(r'\b(results?|outcomes?|impact|delivered|achieved|drove|increased|improved|reduced|grew|scaled)\b', story_text.lower()):
        if not re.search(r'\b(situation|context|background|challenge|problem)\b', story_text.lower()):
            return "results_only"
    
    # Check for STAR format
    has_situation = re.search(r'\b(situation|context|background|challenge|problem)\b', story_text.lower())
    has_task = re.search(r'\b(task|objective|goal|responsibility|role)\b', story_text.lower())
    has_action = re.search(r'\b(action|approach|method|strategy|implemented|developed|created|built|led|managed)\b', story_text.lower())
    has_result = re.search(r'\b(result|outcome|impact|delivered|achieved|drove|increased|improved|reduced|grew|scaled)\b', story_text.lower())
    
    if has_situation and has_task and has_action and has_result:
        return "STAR"
    elif has_situation and has_action and has_result:
        return "SAR"
    elif has_situation and has_action:
        return "SA"
    elif has_situation and has_result:
        return "SR"
    elif has_action and has_result:
        return "AR"
    else:
        return "mixed"

def get_company_and_role(story, resume_path):
    company = story.get('company')
    role = story.get('role')
    if company and role:
        return company, role
    # Fallback: try to look up from resume
    try:
        with open(resume_path, 'r') as f:
            resume_data = yaml.safe_load(f)
        experiences = resume_data.get('resume', {}).get('experience', [])
        # Try to match by keywords in text or tags
        story_text = story.get('text', '').lower()
        story_tags = [t.lower() for t in story.get('tags', [])]
        for exp in experiences:
            exp_company = exp.get('company', '')
            exp_title = exp.get('title', '')
            exp_desc = exp.get('description', '').lower()
            # Match if company or title appears in text or tags
            if exp_company.lower() in story_text or exp_title.lower() in story_text:
                return exp_company, exp_title
            if any(tag in exp_company.lower() or tag in exp_title.lower() for tag in story_tags):
                return exp_company, exp_title
            if any(tag in exp_desc for tag in story_tags):
                return exp_company, exp_title
        # Fallback: just return first experience
        if experiences:
            return experiences[0].get('company', 'Unknown Company'), experiences[0].get('title', 'Unknown Role')
    except Exception as e:
        print(f"Warning: Could not look up company/role from resume: {e}")
    return 'Unknown Company', 'Unknown Role'

def get_example_text(example):
    # Prefer 'text' if present, else concatenate situation, action, result
    if example.get('text'):
        return example['text']
    parts = []
    for key in ['situation', 'action', 'result']:
        val = example.get(key, '')
        if val:
            parts.append(val.strip())
    return '\n'.join(parts)

def refine_star_story(story: Dict[str, Any], target_length: int, resume_path: str) -> str:
    """Refine a single STAR story using OpenAI"""
    config = load_config()
    
    # Detect story format
    story_text = get_example_text(story)
    format_type = detect_story_format(story_text)
    
    # Get company and role
    company, role = get_company_and_role(story, resume_path)
    
    # Adapt prompt based on format
    if format_type == "empty":
        return "Story has no content to refine."
    elif format_type == "results_only":
        format_instruction = "This story appears to focus mainly on results. Expand it to include the situation, your actions, and approach while maintaining the strong results focus."
    elif format_type == "STAR":
        format_instruction = "This story follows the STAR format. Maintain this structure while making it more concise and impactful."
    elif format_type == "SAR":
        format_instruction = "This story follows the SAR format (Situation-Action-Result). Maintain this structure while making it more concise and impactful."
    elif format_type == "SA":
        format_instruction = "This story includes situation and actions but lacks clear results. Add specific, measurable results while maintaining the existing structure."
    elif format_type == "SR":
        format_instruction = "This story includes situation and results but lacks actions. Add specific actions and approaches while maintaining the existing structure."
    elif format_type == "AR":
        format_instruction = "This story includes actions and results but lacks context. Add brief situation context while maintaining the existing structure."
    else:
        format_instruction = "This story has mixed elements. Structure it clearly with situation, actions, and results while making it more concise and impactful."
    
    prompt = f"""You are a professional cover letter writer helping to refine STAR stories into a single, polished, cohesive paragraph suitable for direct insertion into a cover letter.

IMPORTANT CONSTRAINTS:
- Be 100% truthful. Only include verified facts and avoid any speculation or unverified claims
- Do not make assumptions about technologies, methodologies, or outcomes not explicitly stated
- If information is missing or unclear, acknowledge the gap rather than filling it with assumptions
- Focus on concrete, measurable results and specific actions taken
- Maintain the user's authentic voice and experience level

REQUIRED STRUCTURE:
- Combine all information into a single, flowing paragraph (not bullet points or separate sentences)
- Start with: \"As {role} at {company}, I [summary of scope]...\"
- Then include: situation, actions, and measurable results, all woven together

EXAMPLE FINAL PARAGRAPH:
"As Senior Product Manager at Aurora Solar, I led a two-year platform rebuild that unified our product for enterprise use, navigating a rapidly evolving team and competitive landscape. By establishing cross-functional priorities, mapping dependencies, and coordinating with engineering and product leadership, I ensured seamless integration between product modes and delivered a comprehensive roadmap. This effort resulted in a robust design system and consistent, on-time delivery across multiple quarters, significantly improving team health and cross-pod collaboration."

TARGET LENGTH: {target_length} characters (range: {target_length-100}-{target_length+100})

STORY FORMAT: {format_instruction}

USER'S VOICE PREFERENCES:
- Concise and direct
- Strategic and business-focused
- Emphasize measurable impact and results
- Use active voice and strong action verbs
- Avoid jargon and unnecessary complexity
- Focus on outcomes and value delivered

REFINE THIS STAR STORY INTO A SINGLE, POLISHED PARAGRAPH:

{story_text}

Output only the refined paragraph, no JSON or structured formatting."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer. Output only the refined paragraph text, no JSON or structured formatting. Be 100% truthful and avoid unverified claims."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        refined_text = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        
        # Clean up any JSON formatting if the model still outputs it
        if refined_text.startswith('{') or refined_text.startswith('['):
            try:
                parsed = json.loads(refined_text)
                if isinstance(parsed, dict) and 'text' in parsed:
                    refined_text = parsed['text']
                elif isinstance(parsed, list) and len(parsed) > 0:
                    refined_text = parsed[0].get('text', refined_text)
            except:
                pass
        
        return refined_text
        
    except Exception as e:
        print(f"Error refining story {story.get('id', 'unknown')}: {e}")
        return f"Error: {e}"

def main():
    """Main function to refine examples"""
    config = load_config()
    
    # Set OpenAI API key from environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Get current user from config
    current_user = config.get('current_user', 'default')
    user_staging_dir = f"users/{current_user}/staging"
    input_path = f"{user_staging_dir}/examples_to_refine.yaml"
    output_path = f"{user_staging_dir}/refined_examples.yaml"
    resume_path = f"users/{current_user}/resume_contents.yaml"
    
    # Load target length from approved examples
    target_length = load_blurbs()
    
    # Load examples to refine
    try:
        with open(input_path, 'r') as f:
            examples_to_refine = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return
    
    print(f"Refining {len(examples_to_refine)} examples with target length: {target_length} characters")
    print("=" * 60)
    
    refined_examples = []
    
    for i, example in enumerate(examples_to_refine, 1):
        print(f"\n{i}. Refining example: {example.get('id', 'unknown')}")
        print(f"Original length: {len(example.get('title', '')) + len(example.get('situation', '')) + len(example.get('action', '')) + len(example.get('result', ''))} characters")
        
        company, role = get_company_and_role(example, resume_path)
        refined_text = refine_star_story(example, target_length, resume_path)
        
        print(f"Refined text: {refined_text[:100]}...")
        
        refined_examples.append({
            'id': example['id'],
            'company': company,
            'role': role,
            'title': example.get('title', ''),
            'situation': example.get('situation', ''),
            'action': example.get('action', ''),
            'result': example.get('result', ''),
            'text': refined_text,
            'tags': example.get('tags', []),
            'importance_score': example.get('importance_score', 0)
        })
    
    # Save refined examples
    with open(output_path, 'w') as f:
        yaml.dump(refined_examples, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n" + "=" * 60)
    print(f"Refined {len(refined_examples)} examples")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main() 