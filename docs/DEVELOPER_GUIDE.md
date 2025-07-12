# 🛠️ Cover Letter Agent Developer Guide

> A comprehensive guide for developers who want to understand, extend, or contribute to the Cover Letter Agent codebase.

## 🏗️ Architecture Overview

### Core Design Principles

1. **Modular Architecture**: Each component has a single responsibility
2. **Type Safety**: Comprehensive type hints throughout the codebase
3. **Error Handling**: Robust error handling with custom exceptions
4. **Configuration Management**: Centralized configuration with validation
5. **Testing**: Comprehensive test coverage with pytest
6. **Code Quality**: Linting, formatting, and type checking

### System Architecture

```
cover-letter-agent/
├── agents/                    # Core business logic
│   ├── cover_letter_agent.py  # Main agent implementation
│   ├── context_analyzer.py    # Job analysis and insights
│   ├── gap_analysis.py        # Requirement gap analysis
│   ├── google_drive_integration.py # Google Drive integration
│   └── resume_parser.py       # Resume parsing (future)
├── core/                      # Shared utilities and types
│   ├── config_manager.py      # Centralized configuration
│   ├── user_context.py        # User data management
│   ├── types.py               # Type definitions
│   ├── exceptions.py          # Custom exceptions
│   ├── logging_config.py      # Logging setup
│   └── performance.py         # Performance optimization and caching
├── scripts/                   # Command-line interfaces
│   └── run_cover_letter_agent.py
├── users/                     # Per-user configuration
│   └── [user_id]/
├── docs/                      # Documentation
├── tests/                     # Test files
└── templates/                 # Configuration templates
```

## 🔧 Development Setup

### Prerequisites

- **Python 3.8+**
- **Git**
- **Make** (for build commands)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cover-letter-agent.git
cd cover-letter-agent

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Development Commands

```bash
# Run all tests
make test

# Run tests with coverage
make coverage

# Format code
make format

# Lint code
make lint

# Type checking
make typecheck

# Run all quality checks
make all
```

## 🧪 Testing

### Test Structure

```
tests/
├── test_config_management.py  # Configuration tests
├── test_error_handling.py     # Error handling tests
├── test_type_hints.py         # Type hint validation
└── test_metrics_preservation.py # AI enhancement tests
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_config_management.py -v

# Run with coverage
python -m pytest --cov=agents --cov=core

# Run tests in parallel
python -m pytest -n auto
```

### Writing Tests

Follow these patterns for writing tests:

```python
import pytest
from unittest.mock import Mock, patch
from agents.cover_letter_agent import CoverLetterAgent

class TestCoverLetterAgent:
    """Test cases for CoverLetterAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = CoverLetterAgent(user_id="test_user")
    
    def test_parse_job_description(self):
        """Test job description parsing."""
        job_text = "Senior Product Manager at TechCorp..."
        job = self.agent.parse_job_description(job_text)
        
        assert job.company_name == "TechCorp"
        assert job.job_title == "Senior Product Manager"
        assert job.score > 0
    
    @patch('agents.cover_letter_agent.openai.ChatCompletion.create')
    def test_llm_enhancement(self, mock_openai):
        """Test LLM enhancement functionality."""
        # Mock OpenAI response
        mock_openai.return_value.choices[0].message.content = "Enhanced text"
        
        result = self.agent._apply_llm_enhancement("Original text")
        assert "Enhanced text" in result
```

## 🔍 Code Quality

### Type Hints

All functions should have comprehensive type hints:

```python
from typing import Dict, List, Optional, Tuple
from core.types import JobDescription, BlurbMatch

def select_blurbs(
    self, 
    job: JobDescription, 
    debug: bool = False
) -> Dict[str, BlurbMatch]:
    """Select appropriate blurbs for a job description."""
    pass
```

### Error Handling

Use custom exceptions for specific error cases:

```python
from core.exceptions import ConfigurationError, FileLoadError

def load_config(self, config_type: str) -> ConfigDict:
    """Load configuration with proper error handling."""
    try:
        config = self._load_user_config(config_type)
    except yaml.YAMLError as e:
        raise FileLoadError(f"Invalid YAML in config: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load config: {e}")
```

### Logging

Use structured logging throughout:

```python
from core.logging_config import get_logger

logger = get_logger(__name__)

def process_job_description(self, job_text: str) -> JobProcessingResult:
    """Process job description with logging."""
    logger.info("Processing job description")
    logger.debug(f"Job text length: {len(job_text)}")
    
    try:
        result = self._process(job_text)
        logger.info("Job processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Job processing failed: {e}")
        raise
```

## ⚡ Performance Optimization

### Caching System

The system includes a comprehensive caching layer for expensive operations:

```python
from core.performance import get_file_cache, get_performance_monitor

# File caching for YAML operations
file_cache = get_file_cache()
config = file_cache.load_yaml_file("config.yaml")

# Performance monitoring
monitor = get_performance_monitor()
monitor.start_timer("expensive_operation")
# ... perform operation ...
monitor.end_timer("expensive_operation")
```

### Cache Types

1. **File Cache**: Caches YAML file loading operations
2. **LLM Cache**: Caches expensive LLM API calls
3. **Job Parsing Cache**: Caches job description analysis
4. **Blurb Scoring Cache**: Caches blurb selection calculations

### Performance Monitoring

Track performance metrics throughout the application:

```python
from core.performance import get_performance_monitor

monitor = get_performance_monitor()

# Start timing an operation
monitor.start_timer("job_parsing")
job = agent.parse_job_description(job_text)
monitor.end_timer("job_parsing")

# Get performance summary
summary = monitor.get_metrics_summary()
print(f"Job parsing took {summary['job_parsing']['average_time']:.3f}s")
```

### Memoization Decorator

Use the memoization decorator for expensive functions:

```python
from core.performance import memoize

@memoize(max_age_hours=24, cache_key_prefix="job_parse")
def parse_job_description(self, job_text: str) -> JobDescription:
    """Parse job description with caching."""
    # Expensive parsing logic here
    pass
```

### Cache Management

Manage cache size and expiration:

```python
from core.performance import get_file_cache

file_cache = get_file_cache()

# Get cache statistics
stats = file_cache.cache_manager.get_stats()
print(f"Cache size: {stats['memory_cache_size']}")

# Clear specific cache entries
file_cache.cache_manager.clear(pattern="yaml_load")
```
```

## 🏗️ Extending the System

### Adding New Agents

Create a new agent by extending the base pattern:

```python
# agents/new_agent.py
from typing import Dict, Any
from core.types import AgentResult
from core.logging_config import get_logger

logger = get_logger(__name__)

class NewAgent:
    """New agent for specific functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the agent."""
        self.config = config
        logger.info("NewAgent initialized")
    
    def process(self, input_data: str) -> AgentResult:
        """Process input data."""
        logger.info("Processing with NewAgent")
        # Your processing logic here
        return AgentResult(success=True, data="processed_data")
```

### Adding New Configuration Types

Extend the configuration system:

```python
# core/config_manager.py
def _get_defaults(self, config_type: str) -> ConfigDict:
    """Get default configuration for specified type."""
    if config_type == "new_config":
        return {
            "enabled": False,
            "settings": {
                "param1": "default_value",
                "param2": 100
            }
        }
    # ... existing code
```

### Adding New Blurb Types

Extend the blurb system:

```python
# In your blurbs.yaml
new_type:
  - id: custom_blurb
    tags: [custom, feature]
    text: "Your custom blurb text with [PLACEHOLDER]"
    metadata:
      priority: "high"
      category: "custom"
```

### Adding New Job Types

Extend job classification:

```python
# In your blurb_logic.yaml
job_classification:
  custom_role:
    keywords: ["custom", "specialized", "unique"]
    min_keyword_count: 1
    scoring_multiplier: 1.5
```

## 🔧 Configuration Management

### Configuration Hierarchy

1. **Defaults**: Built-in default values
2. **Global Config**: `data/config.yaml`
3. **User Config**: `users/[user_id]/config.yaml`
4. **Runtime Overrides**: Command-line arguments

### Adding Configuration Validation

```python
# core/config_manager.py
def _validate_new_config(self, config: ConfigDict) -> None:
    """Validate new configuration type."""
    required_fields = ["enabled", "settings"]
    
    for field in required_fields:
        if field not in config:
            raise ConfigurationError(f"Missing required field: {field}")
    
    if not isinstance(config.get("enabled"), bool):
        raise ConfigurationError("enabled must be a boolean")
```

## 🤖 AI Integration

### Adding New LLM Providers

```python
# agents/llm_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def enhance_text(self, text: str, context: Dict[str, Any]) -> str:
        """Enhance text using the provider."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""
    
    def enhance_text(self, text: str, context: Dict[str, Any]) -> str:
        """Enhance text using OpenAI GPT."""
        # Implementation here
        pass

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""
    
    def enhance_text(self, text: str, context: Dict[str, Any]) -> str:
        """Enhance text using Anthropic Claude."""
        # Implementation here
        pass
```

### Custom Enhancement Prompts

```python
# agents/cover_letter_agent.py
def _get_enhancement_prompt(self, job: JobDescription) -> str:
    """Get custom enhancement prompt based on job type."""
    base_prompt = "Enhance this cover letter..."
    
    if "startup" in job.job_type.lower():
        return base_prompt + " with a more conversational tone."
    elif "enterprise" in job.job_type.lower():
        return base_prompt + " with a more formal tone."
    else:
        return base_prompt
```

## 📊 Performance Optimization

### Caching

Implement caching for expensive operations:

```python
from functools import lru_cache
from typing import Dict, Any

class CoverLetterAgent:
    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
    
    @lru_cache(maxsize=128)
    def _expensive_operation(self, input_data: str) -> str:
        """Cache expensive operations."""
        # Expensive computation here
        return result
```

### Async Operations

For I/O-bound operations:

```python
import asyncio
from typing import List

class AsyncCoverLetterAgent:
    async def process_multiple_jobs(self, job_texts: List[str]) -> List[str]:
        """Process multiple jobs concurrently."""
        tasks = [self.process_job(job_text) for job_text in job_texts]
        return await asyncio.gather(*tasks)
```

## 🔒 Security Considerations

### API Key Management

```python
import os
from typing import Optional

def get_api_key() -> Optional[str]:
    """Safely retrieve API key."""
    # Check environment variable first
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Check .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")
    except ImportError:
        return None
```

### Input Validation

```python
import re
from core.exceptions import ValidationError

def validate_job_description(text: str) -> str:
    """Validate job description input."""
    if not text or not text.strip():
        raise ValidationError("Job description cannot be empty")
    
    if len(text) > 10000:
        raise ValidationError("Job description too long (max 10,000 chars)")
    
    # Check for potentially malicious content
    suspicious_patterns = [
        r"<script>",
        r"javascript:",
        r"data:text/html"
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValidationError("Job description contains suspicious content")
    
    return text.strip()
```

## 🚀 Deployment

### Docker Support

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/run_cover_letter_agent.py"]
```

### Environment Configuration

```bash
# .env.example
OPENAI_API_KEY=your_openai_api_key
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
LOG_LEVEL=INFO
ENABLE_AI_ENHANCEMENT=true
```

## 📈 Monitoring and Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logging for better monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_job_processing(self, job_id: str, company: str, score: float):
        """Log job processing event."""
        event = {
            "event_type": "job_processing",
            "job_id": job_id,
            "company": company,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))
```

### Metrics Collection

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProcessingMetrics:
    """Metrics for job processing."""
    processing_time: float
    job_score: float
    blurbs_selected: int
    enhancement_applied: bool

class MetricsCollector:
    """Collect and report processing metrics."""
    
    def __init__(self):
        self.metrics: List[ProcessingMetrics] = []
    
    def record_metrics(self, metrics: ProcessingMetrics):
        """Record processing metrics."""
        self.metrics.append(metrics)
    
    def get_average_processing_time(self) -> float:
        """Get average processing time."""
        if not self.metrics:
            return 0.0
        return sum(m.processing_time for m in self.metrics) / len(self.metrics)
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `make test`
5. **Check code quality**: `make all`
6. **Submit a pull request**

### Code Review Checklist

- [ ] **Tests**: New code has comprehensive tests
- [ ] **Type Hints**: All functions have proper type hints
- [ ] **Documentation**: Code is well-documented
- [ ] **Error Handling**: Proper error handling implemented
- [ ] **Logging**: Appropriate logging added
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities introduced

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 📚 Additional Resources

- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[User Guide](USER_GUIDE.md)**: End-user documentation
- **[Testing Guide](../TESTING.md)**: Testing best practices
- **[LLM Integration Results](../LLM_INTEGRATION_TEST_RESULTS.md)**: AI enhancement validation

---

**Questions?** Open an issue on GitHub or reach out to the maintainers. 