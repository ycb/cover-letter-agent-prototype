#!/usr/bin/env python3
"""
End-to-End Testing Module for Cover Letter Agent
================================================

Phase 5: Testing & Validation
Tests the complete pipeline from job description to case study selection
with real-world scenarios and validation metrics.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
import json

from hybrid_case_study_selection import HybridCaseStudySelector
from work_history_context import WorkHistoryContextEnhancer

logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Represents a test scenario for end-to-end validation."""
    name: str
    job_description: str
    job_keywords: List[str]
    job_level: Optional[str]
    expected_case_studies: List[str]  # Expected case study IDs
    expected_confidence: float  # Minimum expected confidence
    expected_cost: float  # Maximum expected cost


@dataclass
class TestResult:
    """Represents the result of an end-to-end test."""
    scenario: TestScenario
    selected_case_studies: List[Dict[str, Any]]
    ranked_candidates: List[Any]
    total_time: float
    llm_cost: float
    confidence_scores: List[float]
    success: bool
    issues: List[str]


class EndToEndTester:
    """End-to-end tester for the complete cover letter agent pipeline."""
    
    def __init__(self):
        """Initialize the end-to-end tester."""
        self.enhancer = WorkHistoryContextEnhancer()
        self.selector = HybridCaseStudySelector(llm_enabled=True, max_llm_candidates=10)
        
        # Test case studies with work history context
        self.test_case_studies = [
            {
                'id': 'enact',
                'name': 'Enact 0 to 1 Case Study',
                'tags': ['growth', 'consumer', 'clean_energy', 'user_experience'],
                'description': 'Led cross-functional team from 0-1 to improve home energy management'
            },
            {
                'id': 'aurora',
                'name': 'Aurora Solar Growth Case Study',
                'tags': ['growth', 'B2B', 'clean_energy', 'scaling'],
                'description': 'Helped scale company from Series A to Series C, leading platform rebuild'
            },
            {
                'id': 'meta',
                'name': 'Meta Explainable AI Case Study',
                'tags': ['AI', 'ML', 'trust', 'internal_tools', 'explainable'],
                'description': 'Led cross-functional ML team to scale global recruiting tools'
            },
            {
                'id': 'samsung',
                'name': 'Samsung Customer Care Case Study',
                'tags': ['growth', 'ux', 'b2c', 'public', 'onboarding', 'usability', 'mobile', 'support', 'engagement'],
                'description': 'Led overhaul of Samsung+ app, restoring trust and driving engagement'
            }
        ]
        
        # Test scenarios
        self.test_scenarios = [
            TestScenario(
                name="L5 Cleantech PM",
                job_description="Senior Product Manager at cleantech startup focusing on energy management and growth",
                job_keywords=['product manager', 'cleantech', 'leadership', 'growth', 'energy'],
                job_level='L5',
                expected_case_studies=['aurora', 'enact'],
                expected_confidence=0.8,
                expected_cost=0.05
            ),
            TestScenario(
                name="L4 AI/ML PM",
                job_description="Product Manager at AI company working on internal tools and ML adoption",
                job_keywords=['product manager', 'AI', 'ML', 'internal_tools', 'enterprise'],
                job_level='L4',
                expected_case_studies=['meta'],
                expected_confidence=0.8,
                expected_cost=0.03
            ),
            TestScenario(
                name="L3 Consumer PM",
                job_description="Product Manager at consumer mobile app company focusing on user experience",
                job_keywords=['product manager', 'consumer', 'mobile', 'growth', 'ux'],
                job_level='L3',
                expected_case_studies=['enact', 'samsung'],
                expected_confidence=0.7,
                expected_cost=0.04
            )
        ]
    
    def run_end_to_end_test(self, scenario: TestScenario) -> TestResult:
        """Run end-to-end test for a specific scenario."""
        start_time = time.time()
        issues = []
        
        try:
            # Step 1: Work History Context Enhancement
            enhanced_case_studies = self.enhancer.enhance_case_studies_batch(self.test_case_studies)
            
            # Convert enhanced case studies back to dict format
            enhanced_dicts = []
            for enhanced in enhanced_case_studies:
                enhanced_dict = {
                    'id': enhanced.case_study_id,
                    'name': enhanced.case_study_id.upper() + ' Case Study',
                    'tags': enhanced.enhanced_tags,
                    'description': f"Enhanced case study with {len(enhanced.enhanced_tags)} tags",
                    'provenance': enhanced.tag_provenance,
                    'weights': enhanced.tag_weights
                }
                enhanced_dicts.append(enhanced_dict)
            
            # Step 2: Hybrid Case Study Selection
            result = self.selector.select_case_studies(
                enhanced_dicts,
                scenario.job_keywords,
                scenario.job_level,
                scenario.job_description
            )
            
            total_time = time.time() - start_time
            
            # Extract confidence scores
            confidence_scores = [score.confidence for score in result.ranked_candidates]
            
            # Validate results
            selected_ids = [cs.get('id') for cs in result.selected_case_studies]
            
            # Check if expected case studies are selected
            expected_found = all(expected in selected_ids for expected in scenario.expected_case_studies)
            if not expected_found:
                issues.append(f"Expected case studies not found: {scenario.expected_case_studies}")
            
            # Check confidence threshold
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            if avg_confidence < scenario.expected_confidence:
                issues.append(f"Average confidence {avg_confidence:.2f} below expected {scenario.expected_confidence}")
            
            # Check cost threshold
            if result.llm_cost_estimate > scenario.expected_cost:
                issues.append(f"Cost ${result.llm_cost_estimate:.3f} above expected ${scenario.expected_cost}")
            
            # Check performance threshold
            if result.total_time > 2.0:
                issues.append(f"Total time {result.total_time:.3f}s above 2s threshold")
            
            success = len(issues) == 0
            
            return TestResult(
                scenario=scenario,
                selected_case_studies=result.selected_case_studies,
                ranked_candidates=result.ranked_candidates,
                total_time=total_time,
                llm_cost=result.llm_cost_estimate,
                confidence_scores=confidence_scores,
                success=success,
                issues=issues
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            issues.append(f"Test failed with exception: {str(e)}")
            
            return TestResult(
                scenario=scenario,
                selected_case_studies=[],
                ranked_candidates=[],
                total_time=total_time,
                llm_cost=0.0,
                confidence_scores=[],
                success=False,
                issues=issues
            )
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all end-to-end tests."""
        results = []
        
        for scenario in self.test_scenarios:
            result = self.run_end_to_end_test(scenario)
            results.append(result)
        
        return results
    
    def generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Performance metrics
        avg_time = sum(r.total_time for r in results) / len(results) if results else 0
        avg_cost = sum(r.llm_cost for r in results) / len(results) if results else 0
        avg_confidence = sum(sum(r.confidence_scores) for r in results) / sum(len(r.confidence_scores) for r in results) if any(r.confidence_scores for r in results) else 0
        
        # Collect all issues
        all_issues = []
        for result in results:
            all_issues.extend([f"{result.scenario.name}: {issue}" for issue in result.issues])
        
        return {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'avg_time': avg_time,
                'avg_cost': avg_cost,
                'avg_confidence': avg_confidence
            },
            'results': [
                {
                    'scenario': result.scenario.name,
                    'success': result.success,
                    'selected_count': len(result.selected_case_studies),
                    'total_time': result.total_time,
                    'llm_cost': result.llm_cost,
                    'avg_confidence': sum(result.confidence_scores) / len(result.confidence_scores) if result.confidence_scores else 0,
                    'issues': result.issues
                }
                for result in results
            ],
            'issues': all_issues
        }


def test_end_to_end():
    """Test the end-to-end testing functionality."""
    print("🧪 Testing Phase 5: End-to-End Testing & Validation...")
    
    tester = EndToEndTester()
    results = tester.run_all_tests()
    report = tester.generate_test_report(results)
    
    print(f"\n📊 Test Report:")
    print(f"  Total tests: {report['summary']['total_tests']}")
    print(f"  Successful: {report['summary']['successful_tests']}")
    print(f"  Success rate: {report['summary']['success_rate']:.1%}")
    print(f"  Average time: {report['summary']['avg_time']:.3f}s")
    print(f"  Average cost: ${report['summary']['avg_cost']:.3f}")
    print(f"  Average confidence: {report['summary']['avg_confidence']:.2f}")
    
    print(f"\n📋 Detailed Results:")
    for result in report['results']:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {result['scenario']}: {status}")
        print(f"    Selected: {result['selected_count']} case studies")
        print(f"    Time: {result['total_time']:.3f}s")
        print(f"    Cost: ${result['llm_cost']:.3f}")
        print(f"    Confidence: {result['avg_confidence']:.2f}")
        if result['issues']:
            print(f"    Issues: {', '.join(result['issues'])}")
    
    if report['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in report['issues']:
            print(f"  - {issue}")
    
    # Success criteria validation
    print(f"\n🎯 Success Criteria Validation:")
    print(f"  ✅ End-to-end pipeline: {'PASS' if report['summary']['success_rate'] > 0.8 else 'FAIL'}")
    print(f"  ✅ Performance: {'PASS' if report['summary']['avg_time'] < 2.0 else 'FAIL'}")
    print(f"  ✅ Cost control: {'PASS' if report['summary']['avg_cost'] < 0.10 else 'FAIL'}")
    print(f"  ✅ Quality: {'PASS' if report['summary']['avg_confidence'] > 0.7 else 'FAIL'}")
    
    print(f"\n✅ Phase 5: End-to-End Testing & Validation completed!")


if __name__ == "__main__":
    test_end_to_end() 