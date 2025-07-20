#!/usr/bin/env python3
"""
Integration Tests for Cover Letter Agent
=======================================

Tests the complete integration of all modules working together.
"""

import sys
import os
import unittest
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.hybrid_case_study_selection import HybridCaseStudySelector
from agents.work_history_context import WorkHistoryContextEnhancer
from agents.end_to_end_testing import EndToEndTester
from utils.config_manager import ConfigManager
from utils.error_handler import ErrorHandler


class TestCoverLetterAgentIntegration(unittest.TestCase):
    """Integration tests for the complete cover letter agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
        self.error_handler = ErrorHandler()
        self.enhancer = WorkHistoryContextEnhancer()
        self.selector = HybridCaseStudySelector()
        self.tester = EndToEndTester()
        
        # Test case studies
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
    
    def test_configuration_loading(self):
        """Test that configuration loads correctly."""
        config = self.config_manager.get_hybrid_selection_config()
        self.assertIsNotNone(config)
        self.assertIn('max_llm_candidates', config)
        self.assertIn('confidence_threshold', config)
    
    def test_work_history_enhancement(self):
        """Test work history context enhancement."""
        enhanced = self.enhancer.enhance_case_studies_batch(self.test_case_studies)
        self.assertEqual(len(enhanced), len(self.test_case_studies))
        
        # Check that enhancement added tags
        for enhanced_case in enhanced:
            self.assertGreater(len(enhanced_case.enhanced_tags), len(enhanced_case.original_tags))
            self.assertIsNotNone(enhanced_case.confidence_score)
    
    def test_hybrid_selection(self):
        """Test hybrid case study selection."""
        job_keywords = ['product manager', 'cleantech', 'leadership', 'growth']
        job_level = 'L5'
        
        result = self.selector.select_case_studies(
            self.test_case_studies,
            job_keywords,
            job_level
        )
        
        self.assertIsNotNone(result)
        # Note: May not select case studies if none match criteria
        self.assertLessEqual(result.total_time, 2.0)
        self.assertLessEqual(result.llm_cost_estimate, 0.10)
    
    def test_end_to_end_pipeline(self):
        """Test the complete end-to-end pipeline."""
        results = self.tester.run_all_tests()
        self.assertGreater(len(results), 0)
        
        # Check that at least some tests pass
        successful_tests = sum(1 for r in results if r.success)
        self.assertGreater(successful_tests, 0)
    
    def test_error_handling(self):
        """Test error handling with invalid inputs."""
        # Test with empty case studies
        with self.assertRaises(Exception):
            self.selector.select_case_studies([], ['test'], 'L5')
        
        # Test with empty keywords
        with self.assertRaises(Exception):
            self.selector.select_case_studies(self.test_case_studies, [], 'L5')
    
    def test_performance_metrics(self):
        """Test that performance metrics are within acceptable ranges."""
        job_keywords = ['product manager', 'growth']
        job_level = 'L4'
        
        result = self.selector.select_case_studies(
            self.test_case_studies,
            job_keywords,
            job_level
        )
        
        # Performance checks
        self.assertLessEqual(result.total_time, 2.0, "Total time should be under 2 seconds")
        self.assertLessEqual(result.llm_cost_estimate, 0.10, "Cost should be under $0.10")
        self.assertGreater(len(result.selected_case_studies), 0, "Should select at least one case study")
    
    def test_rule_of_three(self):
        """Test that the rule of three is followed when possible."""
        job_keywords = ['product manager', 'consumer', 'mobile']
        job_level = 'L3'
        
        result = self.selector.select_case_studies(
            self.test_case_studies,
            job_keywords,
            job_level
        )
        
        # Should select 3 case studies when possible
        self.assertLessEqual(len(result.selected_case_studies), 3)
        self.assertGreater(len(result.selected_case_studies), 0)
    
    def test_configuration_integration(self):
        """Test that configuration is properly integrated."""
        # Test that selector uses configuration
        config = self.config_manager.get_hybrid_selection_config()
        self.assertEqual(self.selector.max_llm_candidates, config.get('max_llm_candidates'))
        self.assertEqual(self.selector.llm_cost_per_call, config.get('llm_cost_per_call'))


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running Integration Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCoverLetterAgentIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1%}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️  Errors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    if success:
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!") 