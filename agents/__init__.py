"""
Cover Letter Agent - Core Modules
================================

This package contains the core modules for the cover letter agent:
- hybrid_case_study_selection: Two-stage case study selection
- work_history_context: Work history context enhancement
- end_to_end_testing: Comprehensive testing and validation
"""

__version__ = "1.0.0"
__author__ = "Cover Letter Agent Team"

from .hybrid_case_study_selection import HybridCaseStudySelector, HybridSelectionResult, CaseStudyScore
from .work_history_context import WorkHistoryContextEnhancer, EnhancedCaseStudy
from .end_to_end_testing import EndToEndTester, TestScenario, TestResult

__all__ = [
    'HybridCaseStudySelector',
    'HybridSelectionResult', 
    'CaseStudyScore',
    'WorkHistoryContextEnhancer',
    'EnhancedCaseStudy',
    'EndToEndTester',
    'TestScenario',
    'TestResult'
] 