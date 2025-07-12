#!/usr/bin/env python3
"""
Enhanced CLI for Cover Letter Agent
===================================

Provides an improved command-line interface with better UX features.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from core.cli_utils import (
    CLIError,
    ProgressIndicator,
    check_dependencies,
    confirm_action,
    input_with_validation,
    print_debug,
    print_error,
    print_header,
    print_help_text,
    print_info,
    print_section,
    print_status_indicator,
    print_success,
    print_table,
    print_warning,
    select_from_list,
    validate_file_path,
    validate_user_id,
)
from core.user_context import list_available_users, validate_user_exists


class CoverLetterCLI:
    """Enhanced CLI wrapper for the Cover Letter Agent."""

    def __init__(self):
        self.agent = None
        self.user_id = None
        self.check_dependencies()

    def check_dependencies(self):
        """Check optional dependencies."""
        dependencies = check_dependencies()
        if not dependencies.get("colorama", True):
            print_warning("Colorama not available - using plain text output")

    def setup_parser(self) -> argparse.ArgumentParser:
        """Set up argument parser with enhanced help."""
        parser = argparse.ArgumentParser(
            description="Cover Letter Agent - Intelligent cover letter generation",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --user john -i job.txt                    # Process job file
  %(prog)s --user john -t "Senior PM at TechCorp"    # Process text directly
  %(prog)s --user john --interactive -i job.txt      # Interactive mode
  %(prog)s --user john --log                         # View enhancement log
  %(prog)s --user john --setup                       # Interactive setup
            """,
        )

        # User management
        parser.add_argument("--user", "-u", help="User ID (matches users/[id]/)")
        parser.add_argument("--list-users", action="store_true", help="List available users")
        parser.add_argument("--create-user", help="Create new user with given ID")

        # Input options
        parser.add_argument("--input-file", "-i", help="Input job description file")
        parser.add_argument("--jd", help="Input job description file (alias for --input-file)")
        parser.add_argument("--text", "-t", help="Job description text")

        # Output options
        parser.add_argument("--output-file", "-o", help="Output cover letter file")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

        # Processing options
        parser.add_argument("--debug", action="store_true", help="Show detailed scoring information")
        parser.add_argument("--explain", action="store_true", help="Show reasoning for decisions")
        parser.add_argument("--interactive", action="store_true", help="Step-by-step confirmation")
        parser.add_argument("--track-enhance", action="store_true", help="Log enhancement suggestions")

        # Enhancement management
        parser.add_argument("--log", action="store_true", help="Show enhancement log")
        parser.add_argument("--log-status", choices=["open", "accepted", "rejected"], help="Filter enhancement log by status")
        parser.add_argument(
            "--update-status",
            nargs=3,
            metavar=("JOB_ID", "ENHANCEMENT_TYPE", "STATUS"),
            help="Update enhancement suggestion status",
        )

        # Setup and configuration
        parser.add_argument("--setup", action="store_true", help="Interactive setup wizard")
        parser.add_argument("--config", action="store_true", help="Show user configuration")
        parser.add_argument("--test", action="store_true", help="Run system tests")

        return parser

    def run(self):
        """Main CLI entry point."""
        parser = self.setup_parser()
        args = parser.parse_args()

        try:
            # Handle special commands first
            if args.list_users:
                self.list_users()
                return

            if args.create_user:
                self.create_user(args.create_user)
                return

            if args.setup:
                self.interactive_setup()
                return

            if args.test:
                self.run_tests()
                return

            # Validate user ID
            if not args.user:
                print_error("User ID is required. Use --user <user_id> or --help for more options.")
                return

            self.user_id = validate_user_id(args.user)

            if not validate_user_exists(self.user_id):
                print_error(f"User '{self.user_id}' not found.")
                self.show_user_help()
                return

            # Initialize agent
            self.initialize_agent()

            # Handle different commands
            if args.config:
                self.show_config()
                return

            if args.log:
                self.show_enhancement_log(args.log_status)
                return

            if args.update_status:
                self.update_enhancement_status(*args.update_status)
                return

            # Process job description
            self.process_job_description(args)

        except CLIError as e:
            print_error(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    def initialize_agent(self):
        """Initialize the cover letter agent."""
        print_status_indicator("loading", "Initializing agent...")

        try:
            from agents.cover_letter_agent import CoverLetterAgent

            self.agent = CoverLetterAgent(user_id=self.user_id)
            print_success("Agent initialized successfully")
        except Exception as e:
            print_error(f"Failed to initialize agent: {e}")
            raise CLIError("Agent initialization failed")

    def list_users(self):
        """List available users."""
        print_header("Available Users")

        users = list_available_users()
        if not users:
            print_info("No users found.")
            print_info("Create a new user with: python init_user.py <user_id>")
            return

        user_data = []
        for user in users:
            user_dir = Path("users") / user
            config_file = user_dir / "config.yaml"

            if config_file.exists():
                try:
                    import yaml

                    with open(config_file, "r") as f:
                        config = yaml.safe_load(f)
                    name = config.get("name", "Not set")
                    role = config.get("role", "Not set")
                except:
                    name = "Error reading config"
                    role = "Unknown"
            else:
                name = "No config"
                role = "Unknown"

            user_data.append([user, name, role])

        print_table(headers=["User ID", "Name", "Role"], rows=user_data, title="User Directory")

    def create_user(self, user_id: str):
        """Create a new user."""
        try:
            validated_id = validate_user_id(user_id)

            if validate_user_exists(validated_id):
                if not confirm_action(f"User '{validated_id}' already exists. Overwrite?"):
                    return

            print_status_indicator("loading", f"Creating user '{validated_id}'...")

            # Import and run the init_user function
            import init_user

            if hasattr(init_user, "init_new_user"):
                success = init_user.init_new_user(validated_id)
                if success:
                    print_success(f"User '{validated_id}' created successfully")
                else:
                    print_error("Failed to create user")
            else:
                print_error("User creation function not found")

        except CLIError as e:
            print_error(str(e))

    def interactive_setup(self):
        """Run interactive setup wizard."""
        print_header("Cover Letter Agent Setup Wizard")

        # Step 1: Create user
        print_section("Step 1: User Setup")
        user_id = input_with_validation(
            "Enter your user ID (letters, numbers, hyphens, underscores only):", validator=validate_user_id
        )

        if not validate_user_exists(user_id):
            if confirm_action(f"User '{user_id}' doesn't exist. Create it?"):
                self.create_user(user_id)
            else:
                print_error("Setup cancelled - user must exist")
                return

        self.user_id = user_id

        # Step 2: Basic configuration
        print_section("Step 2: Basic Configuration")
        print_info("Let's set up your basic information...")

        # This would integrate with the config manager to update user config
        print_info("Configuration setup would go here...")

        # Step 3: Test setup
        print_section("Step 3: Test Setup")
        if confirm_action("Would you like to test your setup with a sample job?"):
            self.test_setup()

        print_success("Setup completed!")

    def test_setup(self):
        """Test the current setup."""
        print_section("Testing Setup")

        # Create a sample job description
        sample_job = """
Senior Product Manager at TechCorp

We're looking for a Senior Product Manager to join our growing team. 
You'll be responsible for leading product strategy, working with engineering teams, 
and driving growth initiatives.

Requirements:
- 5+ years of product management experience
- Experience with AI/ML products
- Strong analytical skills
- Leadership experience
        """.strip()

        print_info("Testing with sample job description...")

        try:
            self.initialize_agent()
            result = self.agent.process_job_description(sample_job, explain=True)

            if len(result) >= 3:
                job, cover_letter, suggestions = result[:3]

                if cover_letter:
                    print_success("✅ Setup test passed - cover letter generated successfully")
                    print_info("Sample cover letter preview:")
                    print(cover_letter[:200] + "..." if len(cover_letter) > 200 else cover_letter)
                else:
                    print_warning("⚠️ Setup test completed - no cover letter generated (this may be normal)")
            else:
                print_error("❌ Setup test failed - unexpected result format")

        except Exception as e:
            print_error(f"❌ Setup test failed: {e}")

    def run_tests(self):
        """Run system tests."""
        print_header("System Tests")

        tests = [
            ("User validation", self.test_user_validation),
            ("File system", self.test_file_system),
            ("Dependencies", self.test_dependencies),
            ("Configuration", self.test_configuration),
        ]

        results = []
        for test_name, test_func in tests:
            print_status_indicator("loading", f"Running {test_name}...")
            try:
                test_func()
                results.append((test_name, "PASS"))
                print_success(f"{test_name} passed")
            except Exception as e:
                results.append((test_name, "FAIL"))
                print_error(f"{test_name} failed: {e}")

        # Print summary
        print_section("Test Results")
        print_table(headers=["Test", "Result"], rows=results)

        passed = sum(1 for _, result in results if result == "PASS")
        total = len(results)

        if passed == total:
            print_success(f"All {total} tests passed!")
        else:
            print_warning(f"{passed}/{total} tests passed")

    def test_user_validation(self):
        """Test user validation."""
        # Test valid user IDs
        valid_ids = ["john", "john_doe", "john-doe", "user123"]
        for user_id in valid_ids:
            validate_user_id(user_id)

        # Test invalid user IDs
        invalid_ids = ["", "john@doe", "john.doe", "user 123"]
        for user_id in invalid_ids:
            try:
                validate_user_id(user_id)
                raise Exception(f"Should have failed: {user_id}")
            except CLIError:
                pass  # Expected

    def test_file_system(self):
        """Test file system operations."""
        # Test that required directories exist
        required_dirs = ["users", "agents", "core", "scripts"]
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                raise Exception(f"Required directory missing: {dir_name}")

    def test_dependencies(self):
        """Test dependency availability."""
        dependencies = check_dependencies()
        # Basic dependencies should always be available
        if not dependencies:
            raise Exception("Failed to check dependencies")

    def test_configuration(self):
        """Test configuration loading."""
        # Test that we can import core modules
        try:
            from core.user_context import list_available_users
            from core.config_manager import get_config_manager
        except ImportError as e:
            raise Exception(f"Failed to import core modules: {e}")

    def show_config(self):
        """Show user configuration."""
        print_header(f"Configuration for user '{self.user_id}'")

        try:
            from core.config_manager import get_config_manager

            config_manager = get_config_manager(self.user_id)
            config = config_manager.get_config()

            # Display key configuration sections
            sections = {
                "Personal Info": ["name", "role", "location", "industry_focus"],
                "Google Drive": ["google_drive"],
                "Profile": ["profile"],
                "Cover Letter": ["cover_letter"],
            }

            for section_name, keys in sections.items():
                print_section(section_name)
                for key in keys:
                    if key in config:
                        value = config[key]
                        if isinstance(value, dict):
                            print(f"  {key}: {len(value)} items")
                        elif isinstance(value, list):
                            print(f"  {key}: {len(value)} items")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: Not set")

        except Exception as e:
            print_error(f"Failed to load configuration: {e}")

    def show_enhancement_log(self, status: Optional[str] = None):
        """Show enhancement log."""
        if not self.agent:
            self.initialize_agent()

        suggestions = self.agent.get_enhancement_suggestions(status)

        if not suggestions:
            print_info("No enhancement suggestions found.")
            return

        print_header("Enhancement Log")

        # Group by status
        by_status = {}
        for suggestion in suggestions:
            status_key = suggestion.get("status", "unknown")
            if status_key not in by_status:
                by_status[status_key] = []
            by_status[status_key].append(suggestion)

        for status_key, status_suggestions in by_status.items():
            print_section(f"{status_key.title()} Suggestions ({len(status_suggestions)})")

            for suggestion in status_suggestions:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                priority = priority_emoji.get(suggestion.get("priority", "unknown"), "⚪")

                print(f"  {priority} {suggestion.get('description', 'No description')}")
                print(f"    Job ID: {suggestion.get('job_id', 'Unknown')}")
                print(f"    Category: {suggestion.get('category', 'Unknown')}")
                if suggestion.get("notes"):
                    print(f"    Notes: {suggestion['notes']}")
                print()

    def update_enhancement_status(self, job_id: str, enhancement_type: str, status: str):
        """Update enhancement suggestion status."""
        if not self.agent:
            self.initialize_agent()

        try:
            self.agent.update_enhancement_status(job_id, enhancement_type, status)
            print_success(f"Updated {enhancement_type} for job {job_id} to status: {status}")
        except Exception as e:
            print_error(f"Failed to update status: {e}")

    def process_job_description(self, args):
        """Process a job description."""
        # Load job description
        input_file = args.input_file or args.jd
        job_text = self.load_job_description(input_file, args.text)

        if not job_text.strip():
            print_error("No job description provided.")
            return

        # Process with progress indicator
        with ProgressIndicator("Processing job description", 4) as progress:
            progress.update(1, "Parsing job description...")
            result = self.agent.process_job_description(
                job_text,
                debug=args.debug,
                explain=args.explain,
                track_enhance=args.track_enhance,
                interactive=args.interactive,
            )
            progress.update(1, "Generating cover letter...")

            if len(result) == 4:
                job, cover_letter, suggestions, debug_info = result
            else:
                job, cover_letter, suggestions = result
                debug_info = None

            progress.update(1, "Analyzing context...")

            # Display results
            self.display_results(job, cover_letter, suggestions, debug_info, args)

            progress.update(1, "Saving results...")

            # Save to file if requested
            if args.output_file and cover_letter:
                self.save_cover_letter(cover_letter, args.output_file)

    def load_job_description(self, file_path: Optional[str], text: Optional[str]) -> str:
        """Load job description from file or text input."""
        if file_path:
            try:
                path = validate_file_path(file_path)
                with open(path, "r") as f:
                    return f.read()
            except CLIError as e:
                print_error(str(e))
                return ""
        elif text:
            return text
        else:
            print_info("Enter job description (press Ctrl+D when finished):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            return "\n".join(lines)

    def display_results(self, job, cover_letter, suggestions, debug_info, args):
        """Display processing results."""
        # Job analysis
        self.display_job_analysis(job)

        # Cover letter
        if cover_letter:
            self.display_cover_letter(cover_letter)
            self.display_enhancement_suggestions(suggestions)
        else:
            print_error("No cover letter generated - job does not meet criteria.")
            print_info(f"Score: {job.score:.2f}")
            print_info(f"Keywords: {len(job.keywords)}")

        # Debug/explain info
        if args.explain or args.debug:
            self.display_debug_info(debug_info)

    def display_job_analysis(self, job):
        """Display job analysis results."""
        print_header("Job Analysis")

        analysis_data = {
            "Company": job.company_name or "Not detected",
            "Position": job.job_title or "Not detected",
            "Job Type": job.job_type or "Unknown",
            "Score": f"{job.score:.2f}",
            "Go/No-Go": "✅ GO" if job.go_no_go else "❌ NO-GO",
            "Keywords": ", ".join(job.keywords) if job.keywords else "None",
        }

        print_key_value_pairs(analysis_data)

    def display_cover_letter(self, cover_letter: str):
        """Display the generated cover letter."""
        print_header("Generated Cover Letter")
        print(cover_letter)

    def display_enhancement_suggestions(self, suggestions):
        """Display enhancement suggestions."""
        if not suggestions:
            print_success("No enhancement suggestions - cover letter looks good!")
            return

        print_section("Enhancement Suggestions")

        for i, suggestion in enumerate(suggestions, 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            priority = priority_emoji.get(suggestion.priority, "⚪")

            print(f"{i}. {priority} {suggestion.description}")
            print(f"   Category: {suggestion.category}")
            print(f"   Priority: {suggestion.priority}")
            print()

    def display_debug_info(self, debug_info):
        """Display debug/explain information."""
        if not debug_info:
            return

        print_section("Debug/Explain Information")

        if "go_no_go_reasoning" in debug_info:
            print(f"Go/No-Go Reasoning: {debug_info['go_no_go_reasoning']}")

        if "blurb_selection" in debug_info:
            print(f"Blurb Selection: {debug_info['blurb_selection']}")

        if "blurb_filtering" in debug_info:
            print(f"Blurb Filtering Steps: {debug_info['blurb_filtering']}")

    def save_cover_letter(self, cover_letter: str, output_file: str):
        """Save cover letter to file."""
        try:
            with open(output_file, "w") as f:
                f.write(cover_letter)
            print_success(f"Cover letter saved to: {output_file}")
        except Exception as e:
            print_error(f"Failed to save cover letter: {e}")

    def show_user_help(self):
        """Show help for user management."""
        print_info("Available users:")
        users = list_available_users()
        for user in users:
            print(f"  - {user}")

        print_info("\nTo create a new user:")
        print("  python init_user.py <user_id>")

        print_info("\nFor more help:")
        print("  python scripts/cli.py --help")


def main():
    """Main entry point."""
    cli = CoverLetterCLI()
    cli.run()


if __name__ == "__main__":
    main()
