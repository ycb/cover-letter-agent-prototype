"""
Cover Letter Agent - Utilities
=============================

This package contains utility modules for the cover letter agent:
- config_manager: Configuration management
- error_handler: Error handling and logging
"""

from .config_manager import ConfigManager, setup_logging
from .error_handler import (
    ErrorHandler, 
    safe_execute, 
    retry_on_error,
    validate_input,
    CoverLetterAgentError,
    ConfigurationError,
    DataLoadError,
    CaseStudySelectionError,
    WorkHistoryError,
    LLMError
)

__all__ = [
    'ConfigManager',
    'setup_logging',
    'ErrorHandler',
    'safe_execute',
    'retry_on_error', 
    'validate_input',
    'CoverLetterAgentError',
    'ConfigurationError',
    'DataLoadError',
    'CaseStudySelectionError',
    'WorkHistoryError',
    'LLMError'
] 