#!/usr/bin/env python3
"""
User Onboarding Script
======================

Creates new user directories with default templates and configuration.
"""

import os
import shutil
import yaml
from pathlib import Path


def create_template_files():
    """Create template files if they don't exist."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create config template
    config_template = {
        "name": "[USER_NAME]",
        "role": "product leader",
        "location": "San Francisco, CA",
        "industry_focus": ["clean tech", "growth", "AI/ML"],
        "resume_path": "resume.pdf",
        "preferred_examples": ["example1", "example2"],
        
        # Google Drive Integration
        "google_drive": {
            "enabled": False,
            "folder_id": "",
            "credentials_file": "credentials.json",
            "materials": {
                "presentations": "presentations/",
                "spreadsheets": "spreadsheets/",
                "cover_letters": "cover_letters/",
                "case_studies": "case_studies/",
                "drafts": "drafts/"
            }
        },
        
        # Profile Information
        "profile": {
            "resume_file": "resume.pdf",
            "linkedin_url": "https://linkedin.com/in/[username]",
            "portfolio_url": "https://[username].com/",
            "github_url": "https://github.com/[username]",
            "achievements": [
                "Add your key achievements here",
                "Quantify your impact with metrics",
                "Focus on leadership and growth"
            ]
        },
        
        # Cover Letter Customization
        "cover_letter": {
            "personal_brand": {
                "tagline": "Product leader focused on [your focus area]",
                "key_strengths": [
                    "Add your key strengths",
                    "Focus on measurable outcomes",
                    "Highlight unique value proposition"
                ]
            },
            "tone": {
                "default": "professional",
                "startup": "conversational",
                "enterprise": "professional",
                "AI_ML": "technical"
            }
        }
    }
    
    with open(templates_dir / "config_template.yaml", 'w') as f:
        yaml.dump(config_template, f, default_flow_style=False, sort_keys=False)
    
    # Create blurbs template
    blurbs_template = {
        "intro": [
            {
                "id": "standard",
                "tags": ["all"],
                "text": "I am a [ROLE] with [X] years of experience in [INDUSTRY]. I am excited to apply for the [POSITION] role at [COMPANY]."
            },
            {
                "id": "ai_variant",
                "tags": ["AI", "ML"],
                "text": "I focus on clarifying ambiguity and building trust in AI systems. I am excited to apply for the [POSITION] role at [COMPANY]."
            }
        ],
        "paragraph2": [
            {
                "id": "growth",
                "tags": ["growth"],
                "text": "I build systems that align teams around measurable outcomes. At [COMPANY], I [SPECIFIC ACHIEVEMENT]."
            }
        ],
        "leadership": [
            {
                "id": "leadership",
                "tags": ["leadership", "management"],
                "text": "I have experience leading teams of [X] people and managing [Y] projects. I focus on developing talent and scaling processes."
            }
        ],
        "closing": [
            {
                "id": "standard",
                "tags": ["all"],
                "text": "I am excited about the opportunity to contribute to [COMPANY]'s mission and would welcome the chance to discuss how my experience aligns with your needs."
            }
        ]
    }
    
    with open(templates_dir / "blurbs_template.yaml", 'w') as f:
        yaml.dump(blurbs_template, f, default_flow_style=False, sort_keys=False)
    
    # Create blurb logic template
    logic_template = {
        "scoring_rules": {
            "keyword_weights": {
                "AI": 3.0,
                "startup": 2.5,
                "growth": 2.0,
                "enterprise": 2.0,
                "trust": 1.5
            }
        },
        "go_no_go": {
            "minimum_keywords": 3,
            "minimum_total_score": 5.0
        }
    }
    
    with open(templates_dir / "blurb_logic_template.yaml", 'w') as f:
        yaml.dump(logic_template, f, default_flow_style=False, sort_keys=False)
    
    # Create job targeting template
    targeting_template = {
        "title_keywords": {
            "leadership": ["senior", "lead", "manager", "director", "head", "vp", "chief"],
            "IC": ["engineer", "developer", "analyst", "specialist", "coordinator"]
        },
        "company_stages": {
            "startup": ["startup", "early-stage", "seed", "series a", "series b"],
            "scaleup": ["scaleup", "growth", "series c", "series d"],
            "enterprise": ["enterprise", "fortune", "large", "established"]
        }
    }
    
    with open(templates_dir / "job_targeting_template.yaml", 'w') as f:
        yaml.dump(targeting_template, f, default_flow_style=False, sort_keys=False)


def init_new_user(user_id: str):
    """Initialize a new user directory with templates."""
    if not user_id or user_id.strip() == "":
        print("❌ Error: User ID cannot be empty")
        return False
    
    user_id = user_id.strip().lower()
    
    # Create templates if they don't exist
    create_template_files()
    
    # Create user directory
    user_dir = Path("users") / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template files
    templates_dir = Path("templates")
    
    template_files = [
        ("config_template.yaml", "config.yaml"),
        ("blurbs_template.yaml", "blurbs.yaml"),
        ("blurb_logic_template.yaml", "blurb_logic.yaml"),
        ("job_targeting_template.yaml", "job_targeting.yaml")
    ]
    
    for template_file, user_file in template_files:
        template_path = templates_dir / template_file
        user_path = user_dir / user_file
        
        if template_path.exists():
            shutil.copy(template_path, user_path)
            print(f"✅ Created {user_file}")
        else:
            print(f"❌ Template {template_file} not found")
    
    # Create examples directory
    examples_dir = user_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    # Create README for the user
    readme_content = f"""# User Directory for {user_id}

## Files to Update:

1. **config.yaml** - Your personal information and preferences
2. **blurbs.yaml** - Your cover letter content modules
3. **blurb_logic.yaml** - Scoring and matching rules
4. **job_targeting.yaml** - Job filtering criteria
5. **resume.pdf** - Your resume (add this file)

## Next Steps:

1. Add your resume as `resume.pdf`
2. Update `config.yaml` with your personal information
3. Customize `blurbs.yaml` with your stories and examples
4. Test with: `python3 scripts/run_cover_letter_agent.py --user {user_id} -i job_description.txt`

## Google Drive Setup (Optional):

1. Update `config.yaml` with your Google Drive folder ID
2. Add credentials file to your user directory
3. Enable Google Drive integration in config
"""
    
    with open(user_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"\n🎉 User '{user_id}' initialized successfully!")
    print(f"📁 User directory: {user_dir}")
    print(f"📝 Next steps: Update config.yaml and add your resume.pdf")
    print(f"🧪 Test with: python3 scripts/run_cover_letter_agent.py --user {user_id} -i job_description.txt")
    
    return True


def list_users():
    """List all existing users."""
    users_dir = Path("users")
    if not users_dir.exists():
        print("No users found.")
        return
    
    users = [d.name for d in users_dir.iterdir() if d.is_dir()]
    if users:
        print("Existing users:")
        for user in sorted(users):
            print(f"  - {user}")
    else:
        print("No users found.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("Usage:")
        print("  python3 init_user.py <user_id>  # Create new user")
        print("  python3 init_user.py --list     # List existing users")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_users()
    else:
        user_id = sys.argv[1]
        init_new_user(user_id) 