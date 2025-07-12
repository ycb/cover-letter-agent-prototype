#!/usr/bin/env python3
"""
Test Type Hints
===============

Tests that type hints are correctly implemented and don't cause issues.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, get_type_hints

import yaml

from agents.cover_letter_agent import BlurbMatch, CoverLetterAgent, EnhancementSuggestion, JobDescription, JobTargeting
from core.types import (
    BlurbDict,
    BlurbSelectionResult,
    CaseStudyDict,
    ConfigDict,
    ContextualAnalysisDict,
    ContextualDataResult,
    EnhancementLogEntry,
    JobProcessingResult,
    LogicDict,
    ResumeDataDict,
    TargetingDict,
)
from core.user_context import UserContext


class TestTypeHints(unittest.TestCase):
    """Test type hints implementation."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Create test user directory
        user_dir = Path("users") / "test_type_hints"
        user_dir.mkdir(exist_ok=True)

        # Create test config
        config_data = {
            "name": "Test User",
            "role": "product leader",
            "location": "San Francisco, CA",
            "industry_focus": ["clean tech", "growth"],
            "resume_path": "resume.pdf",
            "preferred_examples": ["example1", "example2"],
        }

        config_path = user_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Create test blurbs
        blurbs_data = {
            "intro": [{"id": "standard", "tags": ["all"], "text": "I am a [ROLE] with [X] years of experience..."}],
            "paragraph2": [
                {"id": "growth", "tags": ["growth"], "text": "I build systems that align teams around measurable outcomes..."}
            ],
        }

        blurbs_path = user_dir / "blurbs.yaml"
        with open(blurbs_path, "w") as f:
            yaml.dump(blurbs_data, f)

        # Create test logic
        logic_data = {
            "scoring_rules": {"keyword_weights": {"AI": 3.0, "startup": 2.5, "growth": 2.0}},
            "go_no_go": {
                "minimum_keywords": 3,
                "minimum_total_score": 5.0,
                "strong_match_keywords": ["AI", "growth", "startup"],
                "poor_match_keywords": ["junior", "entry-level"],
            },
            "job_classification": {
                "leadership": {"keywords": ["manager", "director", "lead"], "min_keyword_count": 1},
                "IC": {"keywords": ["analyst", "specialist"], "min_keyword_count": 1},
            },
        }

        logic_path = user_dir / "blurb_logic.yaml"
        with open(logic_path, "w") as f:
            yaml.dump(logic_data, f)

        # Create test targeting
        targeting_data = {
            "titles": {
                "leadership": ["product manager", "product director", "head of product"],
                "IC": ["product analyst", "product specialist"],
            },
            "comp_target": 150000,
            "locations": {"preferred": ["San Francisco", "New York"], "open_to": ["Remote", "Austin"]},
        }

        targeting_path = user_dir / "job_targeting.yaml"
        with open(targeting_path, "w") as f:
            yaml.dump(targeting_data, f)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        user_dir = Path("users") / "test_type_hints"
        if user_dir.exists():
            shutil.rmtree(user_dir)

    def test_type_aliases_are_defined(self):
        """Test that all type aliases are properly defined."""
        # Test that type aliases exist and are correct
        self.assertEqual(ConfigDict, Dict[str, Any])
        self.assertEqual(BlurbDict, Dict[str, Any])
        self.assertEqual(LogicDict, Dict[str, Any])
        self.assertEqual(TargetingDict, Dict[str, Any])
        self.assertEqual(EnhancementLogEntry, Dict[str, Any])
        self.assertEqual(CaseStudyDict, Dict[str, Any])
        self.assertEqual(ResumeDataDict, Dict[str, Any])
        self.assertEqual(ContextualAnalysisDict, Dict[str, Any])

    def test_agent_constructor_type_hints(self):
        """Test that CoverLetterAgent constructor has proper type hints."""
        hints = get_type_hints(CoverLetterAgent.__init__)

        # Check that type hints exist
        self.assertIn("user_id", hints)
        self.assertIn("data_dir", hints)

        # Check that user_id is Optional[str]
        self.assertEqual(hints["user_id"], Optional[str])

        # Check that data_dir is str
        self.assertEqual(hints["data_dir"], str)

    def test_user_context_constructor_type_hints(self):
        """Test that UserContext constructor has proper type hints."""
        hints = get_type_hints(UserContext.__init__)

        # Check that type hints exist
        self.assertIn("user_id", hints)

        # Check that user_id is str
        self.assertEqual(hints["user_id"], str)

    def test_agent_method_type_hints(self):
        """Test that CoverLetterAgent methods have proper type hints."""
        agent = CoverLetterAgent(user_id="test_type_hints")

        # Test process_job_description
        hints = get_type_hints(agent.process_job_description)
        self.assertIn("job_text", hints)
        self.assertIn("debug", hints)
        self.assertIn("explain", hints)
        self.assertIn("track_enhance", hints)
        self.assertIn("interactive", hints)
        self.assertIn("return", hints)

        self.assertEqual(hints["job_text"], str)
        self.assertEqual(hints["debug"], bool)
        self.assertEqual(hints["explain"], bool)
        self.assertEqual(hints["track_enhance"], bool)
        self.assertEqual(hints["interactive"], bool)
        self.assertEqual(hints["return"], JobProcessingResult)

    def test_user_context_method_type_hints(self):
        """Test that UserContext methods have proper type hints."""
        user_context = UserContext("test_type_hints")

        # Test get_user_name
        hints = get_type_hints(user_context.get_user_name)
        self.assertIn("return", hints)
        self.assertEqual(hints["return"], str)

        # Test get_industry_focus
        hints = get_type_hints(user_context.get_industry_focus)
        self.assertIn("return", hints)
        self.assertEqual(hints["return"], List[str])

        # Test load_enhancement_log
        hints = get_type_hints(user_context.load_enhancement_log)
        self.assertIn("return", hints)
        self.assertEqual(hints["return"], List[EnhancementLogEntry])

    def test_dataclass_type_hints(self):
        """Test that dataclasses have proper type hints."""
        # Test JobDescription
        hints = get_type_hints(JobDescription)
        self.assertIn("raw_text", hints)
        self.assertIn("company_name", hints)
        self.assertIn("job_title", hints)
        self.assertIn("keywords", hints)
        self.assertIn("job_type", hints)
        self.assertIn("score", hints)
        self.assertIn("go_no_go", hints)
        self.assertIn("extracted_info", hints)
        self.assertIn("targeting", hints)

        self.assertEqual(hints["raw_text"], str)
        self.assertEqual(hints["company_name"], str)
        self.assertEqual(hints["job_title"], str)
        self.assertEqual(hints["keywords"], List[str])
        self.assertEqual(hints["job_type"], str)
        self.assertEqual(hints["score"], float)
        self.assertEqual(hints["go_no_go"], bool)
        self.assertEqual(hints["extracted_info"], Dict[str, Any])
        self.assertEqual(hints["targeting"], Optional[JobTargeting])

    def test_type_safety_in_practice(self):
        """Test that type hints work correctly in practice."""
        agent = CoverLetterAgent(user_id="test_type_hints")

        # Test that we can call methods without type errors
        job_text = "Senior Product Manager at TestCorp"

        # This should work without type errors
        job, cover_letter, suggestions = agent.process_job_description(job_text)

        # Verify return types
        self.assertIsInstance(job, JobDescription)
        self.assertIsInstance(cover_letter, str)
        self.assertIsInstance(suggestions, list)

        # Test that we can access job attributes
        self.assertIsInstance(job.company_name, str)
        self.assertIsInstance(job.job_title, str)
        self.assertIsInstance(job.keywords, list)
        self.assertIsInstance(job.score, float)
        self.assertIsInstance(job.go_no_go, bool)

    def test_user_context_type_safety(self):
        """Test that UserContext type hints work correctly."""
        user_context = UserContext("test_type_hints")

        # Test that methods return correct types
        name = user_context.get_user_name()
        self.assertIsInstance(name, str)

        role = user_context.get_user_role()
        self.assertIsInstance(role, str)

        location = user_context.get_user_location()
        self.assertIsInstance(location, str)

        industry_focus = user_context.get_industry_focus()
        self.assertIsInstance(industry_focus, list)
        for item in industry_focus:
            self.assertIsInstance(item, str)

        enhancement_log = user_context.load_enhancement_log()
        self.assertIsInstance(enhancement_log, list)

    def test_type_aliases_usage(self):
        """Test that type aliases are used correctly."""
        # Test that we can use type aliases
        config: ConfigDict = {"test": "value"}
        self.assertIsInstance(config, dict)

        blurbs: Dict[str, List[BlurbDict]] = {"intro": [{"id": "test", "text": "test", "tags": []}]}
        self.assertIsInstance(blurbs, dict)

        logic: LogicDict = {"scoring_rules": {}}
        self.assertIsInstance(logic, dict)

        targeting: TargetingDict = {"titles": {}}
        self.assertIsInstance(targeting, dict)


if __name__ == "__main__":
    unittest.main()
