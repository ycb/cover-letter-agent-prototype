#!/usr/bin/env python3
"""
Custom Exceptions for Cover Letter Agent
========================================

Defines custom exception classes for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class CoverLetterAgentError(Exception):
    """Base exception for all cover letter agent errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(CoverLetterAgentError):
    """Raised when there's an issue with configuration files or settings."""

    pass


class FileLoadError(CoverLetterAgentError):
    """Raised when there's an issue loading required files."""

    pass


class PerformanceError(CoverLetterAgentError):
    """Raised when there's a performance-related error."""

    pass


class SecurityError(CoverLetterAgentError):
    """Raised when there's a security-related error."""

    pass


class UserContextError(CoverLetterAgentError):
    """Raised when there's an issue with user context or data."""

    pass


class LLMError(CoverLetterAgentError):
    """Raised when there's an issue with LLM integration."""

    pass


class ValidationError(CoverLetterAgentError):
    """Raised when data validation fails."""

    pass


class GoogleDriveError(CoverLetterAgentError):
    """Raised when there's an issue with Google Drive integration."""

    pass


class JobParsingError(CoverLetterAgentError):
    """Raised when there's an issue parsing job descriptions."""

    pass


class BlurbSelectionError(CoverLetterAgentError):
    """Raised when there's an issue selecting or processing blurbs."""

    pass


class CoverLetterGenerationError(CoverLetterAgentError):
    """Raised when there's an issue generating cover letters."""

    pass
