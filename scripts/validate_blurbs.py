#!/usr/bin/env python3
"""
Blurb validation CLI tool.

Validates blurbs against JSON schema and provides detailed error reporting.
Can be used in CI/CD pipelines to ensure data quality.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from core.schema_validator import SchemaValidator, validate_user_blurbs, validate_all_user_blurbs


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Validate cover letter blurbs against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all users
  python scripts/validate_blurbs.py --all
  
  # Validate specific user
  python scripts/validate_blurbs.py --user peter
  
  # Validate specific file
  python scripts/validate_blurbs.py --file users/peter/blurbs.yaml
  
  # Show detailed errors
  python scripts/validate_blurbs.py --user peter --verbose
  
  # Export results to JSON
  python scripts/validate_blurbs.py --all --output results.json
        """
    )
    
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Validate blurbs for all users"
    )
    
    parser.add_argument(
        "--user", 
        type=str,
        help="Validate blurbs for specific user"
    )
    
    parser.add_argument(
        "--file", 
        type=str,
        help="Validate specific blurbs file"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed error information"
    )
    
    parser.add_argument(
        "--output", 
        type=str,
        help="Output results to JSON file"
    )
    
    parser.add_argument(
        "--exit-code", 
        action="store_true",
        help="Exit with non-zero code if validation fails"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.user, args.file]):
        parser.error("Must specify --all, --user, or --file")
    
    results = {}
    
    if args.file:
        # Validate specific file
        validator = SchemaValidator()
        results["file"] = validator.get_validation_summary(args.file, "blurb")
        
    elif args.user:
        # Validate specific user
        results[args.user] = validate_user_blurbs(args.user)
        
    elif args.all:
        # Validate all users
        results = validate_all_user_blurbs()
    
    # Display results
    display_results(results, args.verbose)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    if args.exit_code:
        all_valid = all(
            result.get("is_valid", False) 
            for result in results.values() 
            if isinstance(result, dict)
        )
        sys.exit(0 if all_valid else 1)


def display_results(results: Dict[str, Any], verbose: bool = False):
    """Display validation results in a user-friendly format."""
    print("🔍 Blurb Validation Results")
    print("=" * 50)
    
    total_files = 0
    valid_files = 0
    total_errors = 0
    
    for name, result in results.items():
        if not isinstance(result, dict):
            continue
            
        total_files += 1
        is_valid = result.get("is_valid", False)
        error_count = result.get("error_count", 0)
        file_path = result.get("file_path", "Unknown")
        
        if is_valid:
            valid_files += 1
            status = "✅ VALID"
        else:
            total_errors += error_count
            status = "❌ INVALID"
        
        print(f"\n{status} - {name}")
        print(f"  File: {file_path}")
        print(f"  Errors: {error_count}")
        
        if verbose and not is_valid:
            errors = result.get("errors", [])
            for i, error in enumerate(errors, 1):
                print(f"    {i}. {error}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Summary:")
    print(f"  Total files: {total_files}")
    print(f"  Valid files: {valid_files}")
    print(f"  Invalid files: {total_files - valid_files}")
    print(f"  Total errors: {total_errors}")
    
    if total_files > 0:
        success_rate = (valid_files / total_files) * 100
        print(f"  Success rate: {success_rate:.1f}%")
    
    if total_errors == 0 and total_files > 0:
        print("\n🎉 All blurbs are valid!")
    elif total_errors > 0:
        print(f"\n⚠️  Found {total_errors} validation errors")


if __name__ == "__main__":
    main() 