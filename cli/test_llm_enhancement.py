#!/usr/bin/env python3
"""
CLI Tool for Testing LLM Enhancement
====================================

Test LLM enhancement in isolation with job description and cover letter files.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from features.enhance_with_contextual_llm import enhance_with_contextual_llm, EnhancementResult


def load_file_content(file_path: str) -> str:
    """Load content from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        sys.exit(1)


def create_test_metadata(jd_content: str, cl_content: str) -> Dict:
    """Create test metadata from job description and cover letter content."""
    # Extract basic info from content
    lines = jd_content.split('\n')
    company_name = "Unknown"
    position_title = "Unknown"
    
    # Try to extract company name from first few lines
    for line in lines[:5]:
        if '·' in line and line.strip():
            parts = line.split('·')
            if len(parts) > 0:
                company_name = parts[0].strip()
                break
    
    # Try to extract position from first line
    if lines and lines[0].strip():
        position_title = lines[0].strip()
    
    return {
        'company_name': company_name,
        'position_title': position_title,
        'job_type': 'general',
        'job_score': 10.0,
        'case_study_tags': ['growth', 'founding_pm'],
        'role_alignment': 'strong',
        'targeting_score': 15.0,
        'go_no_go': True
    }


def print_enhancement_results(result: EnhancementResult):
    """Print enhancement results in a formatted way."""
    print("\n" + "="*60)
    print("LLM ENHANCEMENT RESULTS")
    print("="*60)
    
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Changes Made: {len(result.changes_made)}")
    
    if result.changes_made:
        print("\nChanges:")
        for change in result.changes_made:
            print(f"  • {change}")
    
    print(f"\nAnalysis Summary:")
    print(f"  {result.analysis_summary}")
    
    print("\n" + "-"*60)
    print("ORIGINAL DRAFT")
    print("-"*60)
    print(result.original_draft)
    
    print("\n" + "-"*60)
    print("ENHANCED DRAFT")
    print("-"*60)
    print(result.enhanced_draft)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Test LLM Enhancement")
    parser.add_argument("--jd", required=True, help="Job description file path")
    parser.add_argument("--cl", required=True, help="Cover letter draft file path")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")
    parser.add_argument("--temperature", type=float, default=0.3, help="Creativity level (0.0-1.0)")
    parser.add_argument("--output", help="Output file for enhanced draft")
    parser.add_argument("--no-enhancement", action="store_true", help="Skip LLM enhancement")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY") and not args.no_enhancement:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Load files
    print(f"📄 Loading job description from: {args.jd}")
    jd_content = load_file_content(args.jd)
    
    print(f"📄 Loading cover letter draft from: {args.cl}")
    cl_content = load_file_content(args.cl)
    
    # Create test metadata
    metadata = create_test_metadata(jd_content, cl_content)
    print(f"🏢 Company: {metadata['company_name']}")
    print(f"💼 Position: {metadata['position_title']}")
    
    if args.no_enhancement:
        print("\n⏭️  Skipping LLM enhancement (--no-enhancement flag)")
        print("\n" + "-"*60)
        print("ORIGINAL DRAFT")
        print("-"*60)
        print(cl_content)
        return
    
    # Test LLM enhancement
    print(f"\n🤖 Testing LLM enhancement with model: {args.model}")
    print(f"🌡️  Temperature: {args.temperature}")
    
    try:
        result = enhance_with_contextual_llm(
            jd_text=jd_content,
            cl_text=cl_content,
            metadata=metadata,
            model=args.model,
            temperature=args.temperature
        )
        
        # Print results
        print_enhancement_results(result)
        
        # Save output if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.enhanced_draft)
            print(f"\n💾 Enhanced draft saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error during LLM enhancement: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 