#!/usr/bin/env python3
"""
CLI wrapper for running onboarding analysis with flexible user configuration.
"""

import argparse
import sys
import os
from pathlib import Path

def run_analysis_for_user(user_name):
    """Run analysis for a specific user."""
    # Set up environment for the user
    os.environ['USER_CONFIG'] = user_name
    
    # Import and run the analysis
    try:
        from scripts.onboarding_analysis_peter import main as run_analysis
        run_analysis()
    except ImportError as e:
        print(f"❌ Error importing analysis script: {e}")
        print("Make sure you're in the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return False
    
    return True

def list_available_users():
    """List available user configurations."""
    users_dir = Path("users")
    if not users_dir.exists():
        print("No users directory found")
        return []
    
    users = []
    for user_dir in users_dir.iterdir():
        if user_dir.is_dir() and (user_dir / "config.yaml").exists():
            users.append(user_dir.name)
    
    return users

def main():
    parser = argparse.ArgumentParser(description="Run onboarding analysis for any user")
    parser.add_argument("--user", default="peter", help="User name (default: peter)")
    parser.add_argument("--list-users", action="store_true", help="List available users")
    parser.add_argument("--configure", action="store_true", help="Run Drive configuration")
    
    args = parser.parse_args()
    
    if args.list_users:
        users = list_available_users()
        if users:
            print("Available users:")
            for user in users:
                print(f"  - {user}")
        else:
            print("No user configurations found")
        return
    
    if args.configure:
        # Run Drive configuration
        try:
            from scripts.configure_drive import configure_drive_setup
            configure_drive_setup()
        except ImportError:
            print("❌ Configuration script not found")
        return
    
    # Check if user config exists
    user_config_path = Path(f"users/{args.user}/config.yaml")
    if not user_config_path.exists():
        print(f"❌ User configuration not found: {user_config_path}")
        print("Available users:")
        users = list_available_users()
        for user in users:
            print(f"  - {user}")
        print(f"\nTo create a new user, run:")
        print(f"  python scripts/run_analysis.py --configure")
        return
    
    print(f"🚀 Running analysis for user: {args.user}")
    success = run_analysis_for_user(args.user)
    
    if success:
        print(f"\n✅ Analysis completed for {args.user}")
    else:
        print(f"\n❌ Analysis failed for {args.user}")
        sys.exit(1)

if __name__ == "__main__":
    main() 