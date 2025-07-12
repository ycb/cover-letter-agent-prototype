#!/usr/bin/env python3
"""
Type Definitions for Cover Letter Agent
======================================

Defines comprehensive type aliases and custom types for better type safety.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

# Type aliases for common patterns
ConfigDict = Dict[str, Any]
BlurbDict = Dict[str, Any]
LogicDict = Dict[str, Any]
TargetingDict = Dict[str, Any]
EnhancementLogEntry = Dict[str, Any]
CaseStudyDict = Dict[str, Any]
ResumeDataDict = Dict[str, Any]
ContextualAnalysisDict = Dict[str, Any]


@dataclass
class BlurbConfig:
    """Configuration for a single blurb."""

    id: str
    text: str
    tags: List[str]
    priority: Optional[int] = None
    blurb_type: Optional[str] = None


@dataclass
class JobInfo:
    """Basic job information."""

    company_name: str
    job_title: str
    job_type: str
    score: float
    go_no_go: bool


@dataclass
class TargetingCriteria:
    """Job targeting criteria."""

    title_match: bool
    comp_match: bool
    location_match: bool
    company_stage_match: bool
    business_model_match: bool
    targeting_score: float
    targeting_go_no_go: bool


@dataclass
class EnhancementSuggestion:
    """Enhancement suggestion for cover letter."""

    timestamp: str
    job_id: str
    enhancement_type: str
    category: str
    description: str
    status: str  # open, accepted, rejected
    priority: str  # high, medium, low
    notes: str = ""


@dataclass
class StrategicInsight:
    """Strategic insight for cover letter generation."""

    description: str
    source: str
    confidence: float
    recommended_action: str
    insight_type: str


@dataclass
class Achievement:
    """Achievement with context."""

    description: str
    company: str
    role: str
    year: str
    impact_level: str
    metrics: Dict[str, Any]
    tags: List[str]


@dataclass
class PastCoverLetter:
    """Past cover letter analysis."""

    content: str
    company: str
    position: str
    date: str
    outcome: str
    key_phrases: List[str]
    tone: str
    strengths: List[str]
    weaknesses: List[str]


# TypedDict definitions for structured data
class GoogleDriveConfig(TypedDict):
    enabled: bool
    folder_id: str
    credentials_file: str
    materials: Dict[str, str]


class ProfileConfig(TypedDict):
    resume_file: str
    linkedin_url: str
    portfolio_url: str
    github_url: str
    achievements: List[str]


class CoverLetterConfig(TypedDict):
    personal_brand: Dict[str, Any]
    tone: Dict[str, str]


class UserConfig(TypedDict):
    name: str
    role: str
    location: str
    industry_focus: List[str]
    resume_path: str
    preferred_examples: List[str]
    google_drive: GoogleDriveConfig
    profile: ProfileConfig
    cover_letter: CoverLetterConfig


class LLMConfig(TypedDict):
    enabled: bool
    model: str
    temperature: float
    max_tokens: int
    preserve_truth: bool
    add_comments: bool


# Function type aliases
BlurbScoringFunction = callable
JobParsingFunction = callable
CoverLetterGenerator = callable
EnhancementAnalyzer = callable


# Complex type aliases
BlurbSelectionResult = Union[Dict[str, Any], Tuple[Dict[str, Any], List[Dict[str, Any]]]]
JobProcessingResult = Union[
    Tuple[Any, str, List[EnhancementSuggestion]], Tuple[Any, str, List[EnhancementSuggestion], Dict[str, Any]]
]
ContextualDataResult = Dict[str, Any]
