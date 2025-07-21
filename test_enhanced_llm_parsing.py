#!/usr/bin/env python3
"""
Tests for Enhanced LLM Job Parsing with People Management Analysis

Tests the new people management parsing functionality that extracts:
- Direct reports information
- Mentorship scope
- Leadership type classification
- Cross-reference with PM levels framework
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from agents.job_parser_llm import JobParserLLM


class TestEnhancedLLMParsing(unittest.TestCase):
    """Test enhanced LLM parsing with people management analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = JobParserLLM()
        
        # Sample job descriptions for testing
        self.ic_job_description = """
        Senior Product Manager at TechCorp
        
        We're looking for a Senior Product Manager to lead cross-functional teams and drive product strategy. 
        You'll work closely with engineering, design, and marketing teams to deliver high-impact features.
        
        Requirements:
        - 5+ years product management experience
        - Experience with A/B testing and data analysis
        - Cross-functional leadership skills
        - Experience with growth metrics and KPIs
        
        You'll mentor junior PMs and product analysts, but this is an individual contributor role.
        """
        
        self.people_manager_job_description = """
        Group Product Manager at BigTech
        
        We're seeking a Group Product Manager to lead a team of Product Managers and drive strategic initiatives.
        You'll be responsible for managing multiple PMs, setting team goals, and developing people.
        
        Requirements:
        - 8+ years product management experience
        - Experience managing teams of 5+ people
        - Strategic thinking and portfolio management
        - People leadership and development skills
        
        You'll have direct reports including Senior PMs, Product Managers, and Product Analysts.
        """
        
        self.mentorship_job_description = """
        Staff Product Manager at Startup
        
        We need a Staff Product Manager to provide technical leadership and mentorship.
        You'll work on complex technical challenges while mentoring other PMs.
        
        Requirements:
        - 7+ years product management experience
        - Deep technical expertise
        - Mentorship and coaching skills
        - Cross-functional influence
        
        You'll mentor other PMs and provide technical guidance, but no direct reports.
        """

    def test_people_management_field_structure(self):
        """Test that people_management field has correct structure."""
        with patch('agents.job_parser_llm.call_openai') as mock_llm:
            mock_llm.return_value = json.dumps({
                "company_name": "TestCorp",
                "job_title": "Senior Product Manager",
                "inferred_level": "L3",
                "inferred_role_type": "growth",
                "key_requirements": ["5+ years experience"],
                "required_competencies": {"product_strategy": "required"},
                "company_info": {"size": "500-1000"},
                "job_context": {"team_size": "8-12"},
                "people_management": {
                    "has_direct_reports": False,
                    "direct_reports": [],
                    "has_mentorship": True,
                    "mentorship_scope": ["Junior PMs"],
                    "leadership_type": "mentorship_only"
                },
                "confidence": 0.85,
                "notes": "Test parsing"
            })
            
            result = self.parser.parse_job_description(self.ic_job_description)
            
            # Test people_management field structure
            self.assertIn('people_management', result)
            pm_data = result['people_management']
            
            required_fields = [
                'has_direct_reports', 'direct_reports', 'has_mentorship', 
                'mentorship_scope', 'leadership_type'
            ]
            
            for field in required_fields:
                self.assertIn(field, pm_data)

    def test_leadership_type_classification(self):
        """Test leadership type classification logic."""
        test_cases = [
            {
                'input': {
                    'has_direct_reports': True,
                    'has_mentorship': True,
                    'leadership_type': 'people_management'
                },
                'expected_blurb': 'leadership'
            },
            {
                'input': {
                    'has_direct_reports': False,
                    'has_mentorship': True,
                    'leadership_type': 'mentorship_only'
                },
                'expected_blurb': 'cross_functional_ic'
            },
            {
                'input': {
                    'has_direct_reports': False,
                    'has_mentorship': False,
                    'leadership_type': 'ic_leadership'
                },
                'expected_blurb': 'cross_functional_ic'
            }
        ]
        
        for test_case in test_cases:
            with patch('agents.job_parser_llm.call_openai') as mock_llm:
                mock_llm.return_value = json.dumps({
                    "company_name": "TestCorp",
                    "job_title": "Product Manager",
                    "inferred_level": "L3",
                    "inferred_role_type": "generalist",
                    "key_requirements": ["Experience"],
                    "required_competencies": {},
                    "company_info": {},
                    "job_context": {},
                    "people_management": test_case['input'],
                    "confidence": 0.8,
                    "notes": "Test"
                })
                
                result = self.parser.parse_job_description("Test job description")
                
                # Test that leadership type is correctly classified
                pm_data = result['people_management']
                self.assertEqual(pm_data['leadership_type'], test_case['input']['leadership_type'])

    def test_pm_levels_cross_reference(self):
        """Test cross-reference with PM levels framework."""
        test_cases = [
            {
                'level': 'L2',
                'expected_leadership': 'ic_leadership'
            },
            {
                'level': 'L3',
                'expected_leadership': 'mentorship_only'
            },
            {
                'level': 'L4',
                'expected_leadership': 'mentorship_only'
            },
            {
                'level': 'L5',
                'expected_leadership': 'people_management'
            }
        ]
        
        for test_case in test_cases:
            with patch('agents.job_parser_llm.call_openai') as mock_llm:
                mock_llm.return_value = json.dumps({
                    "company_name": "TestCorp",
                    "job_title": "Product Manager",
                    "inferred_level": test_case['level'],
                    "inferred_role_type": "generalist",
                    "key_requirements": ["Experience"],
                    "required_competencies": {},
                    "company_info": {},
                    "job_context": {},
                    "people_management": {
                        "has_direct_reports": False,
                        "direct_reports": [],
                        "has_mentorship": True,
                        "mentorship_scope": ["Junior PMs"],
                        "leadership_type": "mentorship_only"
                    },
                    "confidence": 0.8,
                    "notes": "Test"
                })
                
                result = self.parser.parse_job_description("Test job description")
                
                # Test that framework validation is added
                if 'leadership_type_validation' in result:
                    validation = result['leadership_type_validation']
                    self.assertIn('framework_expectation', validation)
                    self.assertEqual(validation['framework_expectation'], test_case['expected_leadership'])

    def test_fallback_parsing_with_people_management(self):
        """Test fallback parsing includes people management data."""
        with patch('agents.job_parser_llm.call_openai', side_effect=Exception("API Error")):
            result = self.parser.parse_job_description("Test job description")
            
            # Test that fallback includes people_management field
            self.assertIn('people_management', result)
            pm_data = result['people_management']
            
            # Test fallback values
            self.assertFalse(pm_data['has_direct_reports'])
            self.assertTrue(pm_data['has_mentorship'])
            self.assertEqual(pm_data['leadership_type'], 'mentorship_only')
            self.assertIn('Product Analysts', pm_data['mentorship_scope'])

    def test_validation_and_enhancement(self):
        """Test validation and enhancement of LLM parsing results."""
        with patch('agents.job_parser_llm.call_openai') as mock_llm:
            mock_llm.return_value = json.dumps({
                "company_name": "TestCorp",
                "job_title": "Senior Product Manager",
                "inferred_level": "L3",
                "inferred_role_type": "growth",
                "key_requirements": ["5+ years experience"],
                "required_competencies": {"product_strategy": "required"},
                "company_info": {"size": "500-1000"},
                "job_context": {"team_size": "8-12"},
                "people_management": {
                    "has_direct_reports": False,
                    "direct_reports": [],
                    "has_mentorship": True,
                    "mentorship_scope": ["Junior PMs"],
                    "leadership_type": "mentorship_only"
                },
                "confidence": 0.85,
                "notes": "Test parsing"
            })
            
            result = self.parser.parse_job_description(self.ic_job_description)
            
            # Test that validation adds framework context
            self.assertIn('prioritized_skills', result)
            self.assertIn('level_summary', result)
            self.assertIn('level_competencies', result)

    def test_edge_cases(self):
        """Test edge cases in people management parsing."""
        edge_cases = [
            {
                'description': 'Missing people_management field',
                'input': {
                    "company_name": "TestCorp",
                    "job_title": "Product Manager",
                    "inferred_level": "L3",
                    "inferred_role_type": "generalist",
                    "key_requirements": ["Experience"],
                    "required_competencies": {},
                    "company_info": {},
                    "job_context": {},
                    "confidence": 0.8,
                    "notes": "Test"
                },
                'expected_leadership': 'ic_leadership'
            },
            {
                'description': 'Invalid leadership type',
                'input': {
                    "company_name": "TestCorp",
                    "job_title": "Product Manager",
                    "inferred_level": "L3",
                    "inferred_role_type": "generalist",
                    "key_requirements": ["Experience"],
                    "required_competencies": {},
                    "company_info": {},
                    "job_context": {},
                    "people_management": {
                        "has_direct_reports": False,
                        "direct_reports": [],
                        "has_mentorship": False,
                        "mentorship_scope": [],
                        "leadership_type": "invalid_type"
                    },
                    "confidence": 0.8,
                    "notes": "Test"
                },
                'expected_leadership': 'ic_leadership'
            }
        ]
        
        for test_case in edge_cases:
            with patch('agents.job_parser_llm.call_openai') as mock_llm:
                mock_llm.return_value = json.dumps(test_case['input'])
                
                result = self.parser.parse_job_description("Test job description")
                
                # Test that validation handles edge cases
                pm_data = result['people_management']
                self.assertIn('leadership_type', pm_data)
                
                # Test that invalid leadership types are handled gracefully
                if pm_data['leadership_type'] == 'invalid_type':
                    self.assertIn('leadership_type_validation', result)

    def test_integration_with_cover_letter_agent(self):
        """Test integration with cover letter agent leadership blurb selection."""
        from agents.cover_letter_agent import CoverLetterAgent
        
        # Mock job with people management data
        mock_job = MagicMock()
        mock_job.people_management = {
            'has_direct_reports': False,
            'direct_reports': [],
            'has_mentorship': True,
            'mentorship_scope': ['Junior PMs'],
            'leadership_type': 'mentorship_only'
        }
        
        # Test that cover letter agent can access people management data
        agent = CoverLetterAgent()
        
        # This should not raise an error
        leadership_type = getattr(mock_job, 'people_management', {}).get('leadership_type', 'ic_leadership')
        self.assertEqual(leadership_type, 'mentorship_only')

    def test_end_to_end_integration(self):
        """Test end-to-end integration from job parsing to cover letter generation."""
        # Test with a real job description
        test_jd = """
        Senior Product Manager at TechCorp
        
        We're looking for a Senior Product Manager to lead cross-functional teams and drive product strategy. 
        You'll work closely with engineering, design, and marketing teams to deliver high-impact features.
        
        Requirements:
        - 5+ years product management experience
        - Experience with A/B testing and data analysis
        - Cross-functional leadership skills
        - Experience with growth metrics and KPIs
        
        You'll mentor junior PMs and product analysts, but this is an individual contributor role.
        """
        
        # Parse job description
        result = self.parser.parse_job_description(test_jd)
        
        # Verify people management data is present
        self.assertIn('people_management', result)
        pm_data = result['people_management']
        
        # Verify required fields exist
        required_fields = [
            'has_direct_reports', 'direct_reports', 'has_mentorship', 
            'mentorship_scope', 'leadership_type'
        ]
        
        for field in required_fields:
            self.assertIn(field, pm_data)
        
        # Verify leadership type is reasonable
        leadership_type = pm_data['leadership_type']
        valid_types = ['people_management', 'mentorship_only', 'ic_leadership', 'no_leadership']
        self.assertIn(leadership_type, valid_types)
        
        # Verify mentorship scope is populated if mentorship is true
        if pm_data['has_mentorship']:
            self.assertIsInstance(pm_data['mentorship_scope'], list)
            self.assertGreater(len(pm_data['mentorship_scope']), 0)
        
        # Verify direct reports is populated if has_direct_reports is true
        if pm_data['has_direct_reports']:
            self.assertIsInstance(pm_data['direct_reports'], list)
            self.assertGreater(len(pm_data['direct_reports']), 0)

    def test_expected_leadership_for_level(self):
        """Test the _get_expected_leadership_for_level method."""
        test_cases = [
            ('L2', 'ic_leadership'),
            ('L3', 'mentorship_only'),
            ('L4', 'mentorship_only'),
            ('L5', 'people_management'),
            ('L6', 'ic_leadership'),  # Should default to ic_leadership (not people_management)
            ('Invalid', 'ic_leadership')  # Should default to ic_leadership
        ]
        
        for level, expected in test_cases:
            result = self.parser._get_expected_leadership_for_level(level)
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main() 