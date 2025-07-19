import pytest
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from agents.cover_letter_agent import CoverLetterAgent, JobDescription

class DummyJob(JobDescription):
    def __init__(self):
        self.raw_text = "Test JD"
        self.company_name = "TestCo"
        self.job_title = "Test Title"
        self.keywords = ["growth", "ai_ml"]
        self.job_type = "ai_ml"
        self.score = 1.0
        self.go_no_go = True
        self.extracted_info = {}
        self.targeting = None

def test_select_blurbs_skips_malformed_blurbs(caplog, tmp_path):
    agent = CoverLetterAgent()
    agent.blurbs = {
        "intro": [
            {"id": "valid", "tags": ["growth"], "text": "Valid blurb."},
            "this is not a dict",  # Malformed blurb
            {"id": "also_valid", "tags": ["ai_ml"], "text": "Another valid blurb."},
            {"id": "missing_tags", "text": "Missing tags key."},  # Malformed
        ]
    }
    job = DummyJob()
    with caplog.at_level(logging.WARNING):
        # Should not raise any exception
        try:
            agent.select_blurbs(job)
        except Exception as e:
            pytest.fail(f"Exception was raised when processing malformed blurbs: {e}")
        # Should log warnings for malformed blurbs
        warnings = [r for r in caplog.records if "Malformed blurb" in r.getMessage()]
        assert len(warnings) == 2 