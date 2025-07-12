#!/usr/bin/env python3
"""
User Onboarding Script
======================

Creates new user directories with default templates and configuration.
"""

import shutil
import sys
from pathlib import Path
from typing import Optional

import yaml

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Import CLI utilities
from core.cli_utils import (
    CLIError,
    confirm_action,
    input_with_validation,
    print_error,
    print_header,
    print_info,
    print_section,
    print_success,
    print_warning,
    validate_user_id,
)


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
                "drafts": "drafts/",
            },
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
                "Focus on leadership and growth",
            ],
        },
        # Cover Letter Customization
        "cover_letter": {
            "personal_brand": {
                "tagline": "Product leader focused on [your focus area]",
                "key_strengths": [
                    "Add your key strengths",
                    "Focus on measurable outcomes",
                    "Highlight unique value proposition",
                ],
            },
            "tone": {
                "default": "professional",
                "startup": "conversational",
                "enterprise": "professional",
                "AI_ML": "technical",
            },
        },
    }

    with open(templates_dir / "config_template.yaml", "w") as f:
        yaml.dump(config_template, f, default_flow_style=False, sort_keys=False)

    # Create blurbs template
    blurbs_template = {
        "intro": [
            {
                "id": "standard",
                "tags": ["all"],
                "text": "I am a [ROLE] with [X] years of experience in [INDUSTRY]. I am excited to apply for the [POSITION] role at [COMPANY].",
            },
            {
                "id": "ai_variant",
                "tags": ["AI", "ML"],
                "text": "I focus on clarifying ambiguity and building trust in AI systems. I am excited to apply for the [POSITION] role at [COMPANY].",
            },
        ],
        "paragraph2": [
            {
                "id": "growth",
                "tags": ["growth"],
                "text": "I build systems that align teams around measurable outcomes. At [COMPANY], I [SPECIFIC ACHIEVEMENT].",
            }
        ],
        "leadership": [
            {
                "id": "leadership",
                "tags": ["leadership", "management"],
                "text": "I have experience leading teams of [X] people and managing [Y] projects. I focus on developing talent and scaling processes.",
            }
        ],
        "closing": [
            {
                "id": "standard",
                "tags": ["all"],
                "text": "I am excited about the opportunity to contribute to [COMPANY]'s mission and would welcome the chance to discuss how my experience aligns with your needs.",
            }
        ],
    }

    with open(templates_dir / "blurbs_template.yaml", "w") as f:
        yaml.dump(blurbs_template, f, default_flow_style=False, sort_keys=False)

    # Create blurb logic template
    logic_template = {
        "scoring_rules": {"keyword_weights": {"AI": 3.0, "startup": 2.5, "growth": 2.0, "enterprise": 2.0, "trust": 1.5}},
        "go_no_go": {"minimum_keywords": 3, "minimum_total_score": 5.0},
    }

    with open(templates_dir / "blurb_logic_template.yaml", "w") as f:
        yaml.dump(logic_template, f, default_flow_style=False, sort_keys=False)

    # Create job targeting template
    targeting_template = {
        "title_keywords": {
            "leadership": ["senior", "lead", "manager", "director", "head", "vp", "chief"],
            "IC": ["engineer", "developer", "analyst", "specialist", "coordinator"],
        },
        "company_stages": {
            "startup": ["startup", "early-stage", "seed", "series a", "series b"],
            "scaleup": ["scaleup", "growth", "series c", "series d"],
            "enterprise": ["enterprise", "fortune", "large", "established"],
        },
    }

    with open(templates_dir / "job_targeting_template.yaml", "w") as f:
        yaml.dump(targeting_template, f, default_flow_style=False, sort_keys=False)


def init_new_user(user_id: str, interactive: bool = False) -> bool:
    """Initialize a new user directory with templates."""
    try:
        validated_id = validate_user_id(user_id)
    except CLIError as e:
        print_error(str(e))
        return False

    # Check if user already exists
    user_dir = Path("users") / validated_id
    if user_dir.exists():
        if not confirm_action(f"User '{validated_id}' already exists. Overwrite?"):
            print_info("User creation cancelled.")
            return False

    print_header("Creating New User")
    print_info(f"Setting up user: {validated_id}")

    # Create templates if they don't exist
    print_section("Creating Templates")
    create_template_files()

    # Create user directory
    print_section("Creating User Directory")
    user_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Created directory: {user_dir}")

    # Copy template files
    templates_dir = Path("templates")
    template_files = [
        ("config_template.yaml", "config.yaml"),
        ("blurbs_template.yaml", "blurbs.yaml"),
        ("blurb_logic_template.yaml", "blurb_logic.yaml"),
        ("job_targeting_template.yaml", "job_targeting.yaml"),
    ]

    print_section("Copying Configuration Files")
    for template_file, user_file in template_files:
        template_path = templates_dir / template_file
        user_path = user_dir / user_file

        if template_path.exists():
            shutil.copy(template_path, user_path)
            print_success(f"Created {user_file}")
        else:
            print_error(f"Template {template_file} not found")

    # Create examples directory
    examples_dir = user_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    print_success("Created examples directory")

    # Interactive setup if requested
    if interactive:
        setup_user_config_interactive(validated_id, user_dir)

    # Create README for the user
    create_user_readme(validated_id, user_dir)

    print_header("User Setup Complete")
    print_success(f"User '{validated_id}' initialized successfully!")
    print_info(f"📁 User directory: {user_dir}")
    print_info("📝 Next steps:")
    print_info("  1. Add your resume as resume.pdf")
    print_info("  2. Update config.yaml with your personal information")
    print_info("  3. Customize blurbs.yaml with your stories and examples")
    print_info(f"  4. Test with: python3 scripts/run_cover_letter_agent.py --user {validated_id} -i job_description.txt")

    return True


def setup_user_config_interactive(user_id: str, user_dir: Path):
    """Interactive setup for user configuration."""
    print_section("Interactive Configuration Setup")
    
    if not confirm_action("Would you like to set up your basic configuration now?"):
        return
    
    print_info("Let's set up your basic information...")
    
    # Basic information
    name = input_with_validation("Enter your full name:", default="[USER_NAME]")
    role = input_with_validation("Enter your current role:", default="product leader")
    location = input_with_validation("Enter your location:", default="San Francisco, CA")
    
    # Industry focus
    print_info("Enter your industry focus areas (comma-separated):")
    industry_input = input_with_validation("Industry focus:", default="clean tech, growth, AI/ML")
    industry_focus = [area.strip() for area in industry_input.split(",")]
    
    # Update config file
    config_file = user_dir / "config.yaml"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update basic info
            config['name'] = name
            config['role'] = role
            config['location'] = location
            config['industry_focus'] = industry_focus
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            print_success("Configuration updated successfully!")
            
        except Exception as e:
            print_error(f"Failed to update configuration: {e}")
    else:
        print_warning("Config file not found - skipping interactive setup")


def create_user_readme(user_id: str, user_dir: Path):
    """Create README for the user."""
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

    with open(user_dir / "README.md", "w") as f:
        f.write(readme_content)
    print_success("Created user README")


def list_users():
    """List all existing users."""
    print_header("Available Users")
    
    users_dir = Path("users")
    if not users_dir.exists():
        print_info("No users found.")
        print_info("Create a new user with: python init_user.py <user_id>")
        return

    users = [d.name for d in users_dir.iterdir() if d.is_dir()]
    if users:
        user_data = []
        for user in sorted(users):
            user_dir = Path("users") / user
            config_file = user_dir / "config.yaml"
            
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    name = config.get('name', 'Not set')
                    role = config.get('role', 'Not set')
                except:
                    name = "Error reading config"
                    role = "Unknown"
            else:
                name = "No config"
                role = "Unknown"
            
            user_data.append([user, name, role])
        
        print_table(
            headers=["User ID", "Name", "Role"],
            rows=user_data,
            title="User Directory"
        )
    else:
        print_info("No users found.")
        print_info("Create a new user with: python init_user.py <user_id>")


def print_table(headers, rows, title=None):
    """Print a formatted table."""
    if not rows:
        return
    
    # Calculate column widths
    col_widths = []
    for i in range(len(headers)):
        max_width = len(headers[i])
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width)
    
    # Print title
    if title:
        print_section(title)
    
    # Print header
    header_line = " | ".join(
        f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers))
    )
    print(f"  {header_line}")
    print(f"  {'-' * len(header_line)}")
    
    # Print rows
    for row in rows:
        row_line = " | ".join(
            f"{str(row[i]):<{col_widths[i]}}" if i < len(row) else " " * col_widths[i]
            for i in range(len(headers))
        )
        print(f"  {row_line}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print_header("User Management")
        print_info("Usage:")
        print_info("  python3 init_user.py <user_id>          # Create new user")
        print_info("  python3 init_user.py <user_id> --interactive  # Interactive setup")
        print_info("  python3 init_user.py --list             # List existing users")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_users()
    else:
        user_id = sys.argv[1]
        interactive = "--interactive" in sys.argv
        init_new_user(user_id, interactive=interactive)
