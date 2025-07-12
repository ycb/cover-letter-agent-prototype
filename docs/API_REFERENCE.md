# Cover Letter Agent API Reference

## Overview

The Cover Letter Agent is a Python library that generates customized cover letters using structured content modules and intelligent matching algorithms. This document provides a comprehensive reference for all public APIs.

## Core Classes

### CoverLetterAgent

The main agent class for generating customized cover letters.

#### Constructor

```python
def __init__(self, user_id: Optional[str] = None, data_dir: str = "data") -> None
```

**Parameters:**
- `user_id`: Optional user identifier for multi-user mode
- `data_dir`: Directory containing configuration files (legacy mode)

**Example:**
```python
# Multi-user mode
agent = CoverLetterAgent(user_id="john_doe")

# Legacy mode
agent = CoverLetterAgent(data_dir="data")
```

#### Main Methods

##### `process_job_description()`

Processes a job description and generates a cover letter.

```python
def process_job_description(
    self, 
    job_text: str, 
    debug: bool = False, 
    explain: bool = False, 
    track_enhance: bool = False, 
    interactive: bool = False
) -> JobProcessingResult
```

**Parameters:**
- `job_text`: Raw job description text
- `debug`: Enable debug output
- `explain`: Provide detailed explanations
- `track_enhance`: Track enhancement suggestions
- `interactive`: Enable interactive mode

**Returns:**
- `JobProcessingResult`: Tuple containing job description, cover letter, and suggestions

**Example:**
```python
job, cover_letter, suggestions = agent.process_job_description(job_text)
```

##### `parse_job_description()`

Parses and analyzes a job description.

```python
def parse_job_description(self, job_text: str) -> JobDescription
```

**Parameters:**
- `job_text`: Raw job description text

**Returns:**
- `JobDescription`: Parsed job information

**Example:**
```python
job = agent.parse_job_description(job_text)
print(f"Company: {job.company_name}")
print(f"Position: {job.job_title}")
print(f"Score: {job.score}")
```

##### `select_blurbs()`

Selects appropriate blurbs for a job description.

```python
def select_blurbs(
    self, 
    job: JobDescription, 
    debug: bool = False, 
    explain: bool = False
) -> BlurbSelectionResult
```

**Parameters:**
- `job`: Parsed job description
- `debug`: Enable debug output
- `explain`: Provide detailed explanations

**Returns:**
- `BlurbSelectionResult`: Selected blurbs and optional debug info

**Example:**
```python
selected_blurbs = agent.select_blurbs(job)
```

##### `generate_cover_letter()`

Generates a cover letter from selected blurbs.

```python
def generate_cover_letter(
    self, 
    job: JobDescription, 
    selected_blurbs: Dict[str, BlurbMatch], 
    missing_requirements: Optional[List[str]] = None
) -> str
```

**Parameters:**
- `job`: Parsed job description
- `selected_blurbs`: Selected blurb matches
- `missing_requirements`: Optional list of missing requirements

**Returns:**
- `str`: Generated cover letter text

**Example:**
```python
cover_letter = agent.generate_cover_letter(job, selected_blurbs)
```

#### Analysis Methods

##### `analyze_contextual_data()`

Analyzes contextual data to inform cover letter strategy.

```python
def analyze_contextual_data(self, job_description: str) -> ContextualAnalysisDict
```

**Parameters:**
- `job_description`: Job description text

**Returns:**
- `ContextualAnalysisDict`: Analysis results including achievements, insights, etc.

##### `review_draft()`

Reviews a cover letter draft and suggests improvements.

```python
def review_draft(
    self, 
    cover_letter: str, 
    job: JobDescription
) -> List[EnhancementSuggestion]
```

**Parameters:**
- `cover_letter`: Cover letter text to review
- `job`: Parsed job description

**Returns:**
- `List[EnhancementSuggestion]`: List of enhancement suggestions

#### Utility Methods

##### `get_case_studies()`

Retrieves relevant case studies for a job.

```python
def get_case_studies(
    self, 
    job_keywords: Optional[List[str]] = None, 
    force_include: Optional[List[str]] = None
) -> List[CaseStudyDict]
```

**Parameters:**
- `job_keywords`: Optional keywords to match against
- `force_include`: Optional list of case studies to force include

**Returns:**
- `List[CaseStudyDict]`: List of relevant case studies

##### `get_enhancement_suggestions()`

Retrieves enhancement suggestions.

```python
def get_enhancement_suggestions(
    self, 
    status: Optional[str] = None
) -> List[EnhancementLogEntry]
```

**Parameters:**
- `status`: Optional status filter ('open', 'accepted', 'rejected')

**Returns:**
- `List[EnhancementLogEntry]`: List of enhancement suggestions

## Data Classes

### JobDescription

Represents a parsed job description with extracted information.

```python
@dataclass
class JobDescription:
    raw_text: str
    company_name: str
    job_title: str
    keywords: List[str]
    job_type: str
    score: float
    go_no_go: bool
    extracted_info: Dict[str, Any]
    targeting: Optional[JobTargeting] = None
```

### JobTargeting

Represents job targeting criteria and evaluation results.

```python
@dataclass
class JobTargeting:
    title_match: bool
    title_category: str  # leadership or IC
    comp_match: bool
    location_match: bool
    location_type: str  # preferred or open_to
    role_type_matches: List[str]
    company_stage_match: bool
    business_model_match: bool
    targeting_score: float
    targeting_go_no_go: bool
```

### BlurbMatch

Represents a blurb with its match score and metadata.

```python
@dataclass
class BlurbMatch:
    blurb_id: str
    blurb_type: str
    text: str
    tags: List[str]
    score: float
    selected: bool = False
```

### EnhancementSuggestion

Represents an enhancement suggestion for the cover letter.

```python
@dataclass
class EnhancementSuggestion:
    timestamp: str
    job_id: str
    enhancement_type: str
    category: str
    description: str
    status: str  # open, accepted, rejected
    priority: str  # high, medium, low
    notes: str = ""
```

## User Context Management

### UserContext

Manages user-specific configuration and data.

#### Constructor

```python
def __init__(self, user_id: str) -> None
```

**Parameters:**
- `user_id`: User identifier

**Example:**
```python
user_context = UserContext("john_doe")
```

#### Methods

##### `get_user_name()`

```python
def get_user_name(self) -> str
```

Returns the user's name.

##### `get_user_role()`

```python
def get_user_role(self) -> str
```

Returns the user's role.

##### `get_user_location()`

```python
def get_user_location(self) -> str
```

Returns the user's location.

##### `get_industry_focus()`

```python
def get_industry_focus(self) -> List[str]
```

Returns the user's industry focus areas.

## Type Definitions

### ConfigDict

Type alias for configuration dictionaries.

```python
ConfigDict = Dict[str, Any]
```

### BlurbDict

Type alias for blurb dictionaries.

```python
BlurbDict = Dict[str, Any]
```

### LogicDict

Type alias for logic configuration dictionaries.

```python
LogicDict = Dict[str, Any]
```

### TargetingDict

Type alias for targeting configuration dictionaries.

```python
TargetingDict = Dict[str, Any]
```

### EnhancementLogEntry

Type alias for enhancement log entries.

```python
EnhancementLogEntry = Dict[str, Any]
```

### CaseStudyDict

Type alias for case study dictionaries.

```python
CaseStudyDict = Dict[str, Any]
```

### ResumeDataDict

Type alias for resume data dictionaries.

```python
ResumeDataDict = Dict[str, Any]
```

### ContextualAnalysisDict

Type alias for contextual analysis results.

```python
ContextualAnalysisDict = Dict[str, Any]
```

## Error Handling

### Custom Exceptions

The library defines several custom exception types:

- `CoverLetterAgentError`: Base exception for all agent errors
- `ConfigurationError`: Raised for configuration issues
- `FileLoadError`: Raised for file loading issues
- `UserContextError`: Raised for user context issues
- `LLMError`: Raised for LLM integration issues
- `ValidationError`: Raised for data validation failures
- `GoogleDriveError`: Raised for Google Drive integration issues
- `JobParsingError`: Raised for job parsing issues
- `BlurbSelectionError`: Raised for blurb selection issues
- `CoverLetterGenerationError`: Raised for cover letter generation issues

**Example:**
```python
try:
    agent = CoverLetterAgent(user_id="john_doe")
    job, cover_letter, suggestions = agent.process_job_description(job_text)
except UserContextError as e:
    print(f"User context error: {e}")
except FileLoadError as e:
    print(f"File loading error: {e}")
```

## Configuration

### User Configuration

User configuration is stored in `users/{user_id}/config.yaml`:

```yaml
name: "John Doe"
role: "product leader"
location: "San Francisco, CA"
industry_focus:
  - clean tech
  - growth
  - AI/ML
resume_path: resume.pdf
preferred_examples:
  - example1
  - example2
google_drive:
  enabled: false
  folder_id: ''
  credentials_file: credentials.json
profile:
  resume_file: resume.pdf
  linkedin_url: https://linkedin.com/in/johndoe
  portfolio_url: https://johndoe.com
  github_url: https://github.com/johndoe
  achievements:
    - "Led team of 8 engineers"
    - "Increased revenue by 50%"
cover_letter:
  personal_brand:
    tagline: "Product leader focused on growth"
    key_strengths:
      - "Strategic thinking"
      - "Team leadership"
  tone:
    default: professional
    startup: conversational
    enterprise: professional
```

### Blurbs Configuration

Blurbs are stored in `users/{user_id}/blurbs.yaml`:

```yaml
intro:
  - id: standard
    tags: [all]
    text: "I am a [ROLE] with [X] years of experience..."
  - id: ai_variant
    tags: [AI, ML]
    text: "I focus on clarifying ambiguity and building trust..."

paragraph2:
  - id: growth
    tags: [growth]
    text: "I build systems that align teams around measurable outcomes..."

leadership:
  - id: leadership
    tags: [leadership, management]
    text: "I have experience leading teams of [X] people..."
```

### Logic Configuration

Logic rules are stored in `users/{user_id}/blurb_logic.yaml`:

```yaml
scoring_rules:
  keyword_weights:
    AI: 3.0
    startup: 2.5
    growth: 2.0

go_no_go:
  minimum_keywords: 3
  minimum_total_score: 5.0

enhancement_suggestions:
  triggers:
    low_score:
      threshold: 3.0
      message: "Consider adding more specific keywords"
```

## Examples

### Basic Usage

```python
from agents.cover_letter_agent import CoverLetterAgent

# Initialize agent
agent = CoverLetterAgent(user_id="john_doe")

# Process job description
job_text = """
Senior Product Manager at TechCorp
We're looking for a product leader with 5+ years of experience...
"""

job, cover_letter, suggestions = agent.process_job_description(job_text)

print(f"Company: {job.company_name}")
print(f"Position: {job.job_title}")
print(f"Score: {job.score}")
print(f"Go/No-Go: {job.go_no_go}")

print("\nCover Letter:")
print(cover_letter)

if suggestions:
    print("\nEnhancement Suggestions:")
    for suggestion in suggestions:
        print(f"- {suggestion.description}")
```

### Advanced Usage

```python
# Parse job description
job = agent.parse_job_description(job_text)

# Select blurbs with debug info
selected_blurbs, debug_info = agent.select_blurbs(job, debug=True, explain=True)

# Generate cover letter
cover_letter = agent.generate_cover_letter(job, selected_blurbs)

# Review draft
suggestions = agent.review_draft(cover_letter, job)

# Get case studies
case_studies = agent.get_case_studies(job.keywords)

# Analyze contextual data
analysis = agent.analyze_contextual_data(job_text)
```

### Interactive Mode

```python
# Process with interactive mode
job, cover_letter, suggestions = agent.process_job_description(
    job_text, 
    interactive=True
)
```

## Logging

The library uses structured logging with different levels:

```python
import logging
from core.logging_config import setup_logging

# Set up logging
logger = setup_logging(level="DEBUG")

# Log messages
logger.info("Processing job description...")
logger.debug("Selected blurbs: %s", selected_blurbs)
logger.warning("Low job score: %f", job.score)
logger.error("Failed to load config: %s", error)
```

## Testing

The library includes comprehensive tests:

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_error_handling.py

# Run with coverage
python -m pytest --cov=agents --cov=core
``` 