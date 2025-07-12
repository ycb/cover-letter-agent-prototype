#!/usr/bin/env python3
"""
Batch Test LLM Enhancement
=========================

Generate multiple cover letters for review before pushing prompt changes.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.cover_letter_agent import CoverLetterAgent
from config.llm_config import estimate_token_cost, strip_job_description


def load_test_jobs() -> List[Dict[str, str]]:
    """Load test job descriptions."""
    test_jobs = [
        {
            "name": "AudioEye PM",
            "file": "data/job_description.txt",
            "user": "peter"
        },
        {
            "name": "Quantum Computing PM", 
            "file": "test_interactive_prompts.txt",
            "user": "peter"
        }
    ]
    
    # Add more test jobs as needed
    return test_jobs


def run_batch_test():
    """Run batch test of LLM enhancement."""
    print("🚀 Starting batch LLM test...")
    
    test_jobs = load_test_jobs()
    results = []
    
    for i, job in enumerate(test_jobs, 1):
        print(f"\n📋 Test {i}/{len(test_jobs)}: {job['name']}")
        
        try:
            # Load job description
            if not Path(job['file']).exists():
                print(f"⚠️  Job file not found: {job['file']}")
                continue
                
            with open(job['file'], 'r') as f:
                job_text = f.read()
            
            # Estimate token cost
            stripped_jd = strip_job_description(job_text)
            cost_estimate = estimate_token_cost(stripped_jd)
            
            print(f"📄 Job description: {len(job_text)} chars")
            print(f"🎯 Stripped to: {len(stripped_jd)} chars")
            print(f"💰 Estimated cost: ${cost_estimate['estimated_cost_usd']:.4f}")
            
            # Create agent
            agent = CoverLetterAgent(user_id=job['user'])
            
            # Process job
            result = agent.process_job_description(
                job_text, 
                interactive=False,  # Non-interactive for batch testing
                debug=True
            )
            
            # Extract results
            if hasattr(result, 'cover_letter'):
                cover_letter = result.cover_letter
            else:
                cover_letter = result[1] if len(result) > 1 else "No cover letter generated"
            
            job_result = {
                "job_name": job['name'],
                "job_file": job['file'],
                "user": job['user'],
                "cover_letter_length": len(cover_letter),
                "cost_estimate": cost_estimate,
                "success": True
            }
            
            print(f"✅ Generated cover letter: {len(cover_letter)} chars")
            
        except Exception as e:
            print(f"❌ Error processing {job['name']}: {e}")
            job_result = {
                "job_name": job['name'],
                "job_file": job['file'],
                "user": job['user'],
                "error": str(e),
                "success": False
            }
        
        results.append(job_result)
    
    # Print summary
    print("\n" + "="*60)
    print("BATCH TEST SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    total_cost = sum(r.get('cost_estimate', {}).get('estimated_cost_usd', 0) for r in successful)
    print(f"💰 Total estimated cost: ${total_cost:.4f}")
    
    # Save results
    results_file = Path("mock_data/batch_test_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Results saved to: {results_file}")
    
    return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch test LLM enhancement")
    parser.add_argument("--mock", action="store_true", help="Use mock mode")
    parser.add_argument("--cache", action="store_true", help="Enable caching")
    
    args = parser.parse_args()
    
    # Set environment variables
    if args.mock:
        os.environ["USE_MOCK"] = "true"
        print("🤖 Using mock mode")
    
    if args.cache:
        os.environ["CACHE_ENABLED"] = "true"
        print("💾 Caching enabled")
    
    results = run_batch_test()
    
    # Exit with error code if any tests failed
    failed_count = len([r for r in results if not r['success']])
    sys.exit(failed_count)


if __name__ == "__main__":
    import argparse
    main() 