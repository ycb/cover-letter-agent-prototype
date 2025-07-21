# Cover Letter Agent API Documentation

## Overview

This document provides comprehensive API documentation for the Cover Letter Agent modules.

## Core Modules

### Hybrid Case Study Selection

#### `HybridCaseStudySelector`

Main class for hybrid case study selection combining tag filtering with LLM semantic scoring.

```python
from agents.hybrid_case_study_selection import HybridCaseStudySelector

selector = HybridCaseStudySelector(
    llm_enabled=True,
    max_llm_candidates=10
)
```

**Methods:**

- `select_case_studies(case_studies, job_keywords, job_level=None, job_description=None) -> HybridSelectionResult`
  - Selects relevant case studies using hybrid approach
  - Returns comprehensive result with performance metrics

#### `HybridSelectionResult`

Result object containing selection results and metrics.

```python
@dataclass
class HybridSelectionResult:
    selected_case_studies: List[Dict[str, Any]]
    ranked_candidates: List[CaseStudyScore]
    stage1_candidates: int
    stage2_scored: int
    llm_cost_estimate: float
    total_time: float
    stage1_time: float
    stage2_time: float
    fallback_used: bool = False
    confidence_threshold: float = 1.0
```

#### `CaseStudyScore`

Scored case study with explanation and confidence.

```python
@dataclass
class CaseStudyScore:
    case_study: Dict[str, Any]
    score: float
    confidence: float
    reasoning: str
    stage1_score: int
    level_bonus: float = 0.0
    industry_bonus: float = 0.0
```

### Work History Context Enhancement

#### `WorkHistoryContextEnhancer`

Enhances case studies with work history context and tag inheritance.

```python
from agents.work_history_context import WorkHistoryContextEnhancer

enhancer = WorkHistoryContextEnhancer(
    work_history_file="users/peter/work_history.yaml"
)
```

**Methods:**

- `enhance_case_studies_batch(case_studies) -> List[EnhancedCaseStudy]`
  - Enhances multiple case studies with work history context
  - Returns list of enhanced case studies

- `enhance_case_study_context(case_study) -> EnhancedCaseStudy`
  - Enhances single case study with work history context
  - Returns enhanced case study with provenance tracking

#### `EnhancedCaseStudy`

Enhanced case study with work history context.

```python
@dataclass
class EnhancedCaseStudy:
    case_study_id: str
    original_tags: List[str]
    inherited_tags: List[str]
    semantic_tags: List[str]
    enhanced_tags: List[str]
    parent_context: Dict[str, Any]
    confidence_score: float
    tag_provenance: Dict[str, str]
    tag_weights: Dict[str, float]
```

### End-to-End Testing

#### `EndToEndTester`

Comprehensive testing for the complete pipeline.

```python
from agents.end_to_end_testing import EndToEndTester

tester = EndToEndTester()
```

**Methods:**

- `run_end_to_end_test(scenario) -> TestResult`
  - Runs end-to-end test for specific scenario
  - Returns detailed test result

- `run_all_tests() -> List[TestResult]`
  - Runs all configured test scenarios
  - Returns list of test results

- `generate_test_report(results) -> Dict[str, Any]`
  - Generates comprehensive test report
  - Returns summary statistics and detailed results

#### `TestScenario`

Test scenario configuration.

```python
@dataclass
class TestScenario:
    name: str
    job_description: str
    job_keywords: List[str]
    job_level: Optional[str]
    expected_case_studies: List[str]
    expected_confidence: float
    expected_cost: float
```

#### `TestResult`

Test result with detailed metrics.

```python
@dataclass
class TestResult:
    scenario: TestScenario
    selected_case_studies: List[Dict[str, Any]]
    ranked_candidates: List[Any]
    total_time: float
    llm_cost: float
    confidence_scores: List[float]
    success: bool
    issues: List[str]
```

## Utility Modules

### Configuration Management

#### `ConfigManager`

Manages configuration settings from YAML files.

```python
from utils.config_manager import ConfigManager

config_manager = ConfigManager("config/agent_config.yaml")
```

**Methods:**

- `get(key, default=None) -> Any`
  - Get configuration value by key (supports nested keys)
  - Returns value or default if not found

- `get_hybrid_selection_config() -> Dict[str, Any]`
  - Get hybrid selection configuration
  - Returns configuration dictionary

- `get_work_history_config() -> Dict[str, Any]`
  - Get work history configuration
  - Returns configuration dictionary

- `reload() -> None`
  - Reload configuration from file
  - Updates all configuration values

### Error Handling

#### `ErrorHandler`

Comprehensive error handling and logging.

```python
from utils.error_handler import ErrorHandler

error_handler = ErrorHandler()
```

**Methods:**

- `handle_error(error, component, context=None) -> ErrorInfo`
  - Handle error with logging and recovery
  - Returns error information object

- `register_recovery_strategy(component, strategy) -> None`
  - Register recovery strategy for component
  - Enables automatic error recovery

- `get_error_summary() -> Dict[str, Any]`
  - Get summary of all errors
  - Returns error statistics

#### Custom Exceptions

```python
from utils.error_handler import (
    CoverLetterAgentError,
    ConfigurationError,
    DataLoadError,
    CaseStudySelectionError,
    WorkHistoryError,
    LLMError
)
```

#### Utility Functions

```python
from utils.error_handler import (
    safe_execute,
    retry_on_error,
    validate_input
)

# Safe execution with error handling
result = safe_execute(func, "component", error_handler, *args, **kwargs)

# Retry on error
@retry_on_error(max_retries=3, delay=1.0)
def my_function():
    pass

# Input validation
validate_input(data, expected_type, field_name)
```

## Configuration

### Configuration File Structure

```yaml
# config/agent_config.yaml

# Hybrid Case Study Selection
hybrid_selection:
  max_llm_candidates: 10
  confidence_threshold: 1.0
  llm_cost_per_call: 0.01
  max_total_time: 2.0
  max_cost_per_application: 0.10

# Work History Context Enhancement
work_history:
  suppressed_inheritance_tags:
    - frontend
    - backend
    - marketing
    # ... more tags
  tag_weights:
    direct: 1.0
    inherited: 0.6
    semantic: 0.8

# Testing
testing:
  performance_threshold: 2.0
  cost_threshold: 0.10
  confidence_threshold: 0.7
  success_rate_threshold: 0.8

# Logging
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/cover_letter_agent.log"

# File Paths
paths:
  work_history: "users/peter/work_history.yaml"
  case_studies: "data/case_studies.yaml"
  logs: "logs/"
  config: "config/"
```

## Usage Examples

### Basic Case Study Selection

```python
from agents.hybrid_case_study_selection import HybridCaseStudySelector
from agents.work_history_context import WorkHistoryContextEnhancer

# Initialize components
enhancer = WorkHistoryContextEnhancer()
selector = HybridCaseStudySelector()

# Prepare case studies
case_studies = [
    {
        'id': 'example',
        'name': 'Example Case Study',
        'tags': ['growth', 'consumer'],
        'description': 'Led growth initiatives'
    }
]

# Enhance with work history context
enhanced_case_studies = enhancer.enhance_case_studies_batch(case_studies)

# Select relevant case studies
result = selector.select_case_studies(
    enhanced_case_studies,
    job_keywords=['product manager', 'growth'],
    job_level='L4'
)

# Access results
print(f"Selected {len(result.selected_case_studies)} case studies")
print(f"Total time: {result.total_time:.3f}s")
print(f"LLM cost: ${result.llm_cost_estimate:.3f}")

# Access ranked candidates with explanations
for score in result.ranked_candidates:
    print(f"{score.case_study['name']}: {score.score:.1f} ({score.confidence:.2f})")
    print(f"  Reasoning: {score.reasoning}")
```

### End-to-End Testing

```python
from agents.end_to_end_testing import EndToEndTester

# Initialize tester
tester = EndToEndTester()

# Run all tests
results = tester.run_all_tests()

# Generate report
report = tester.generate_test_report(results)

# Print summary
print(f"Success rate: {report['summary']['success_rate']:.1%}")
print(f"Average time: {report['summary']['avg_time']:.3f}s")
print(f"Average cost: ${report['summary']['avg_cost']:.3f}")

# Print detailed results
for result in report['results']:
    status = "✅ PASS" if result['success'] else "❌ FAIL"
    print(f"{result['scenario']}: {status}")
```

### Configuration Management

```python
from utils.config_manager import ConfigManager, setup_logging

# Initialize configuration
config_manager = ConfigManager()

# Setup logging
setup_logging(config_manager)

# Get configuration values
max_candidates = config_manager.get('hybrid_selection.max_llm_candidates')
confidence_threshold = config_manager.get('hybrid_selection.confidence_threshold')

# Get configuration sections
hybrid_config = config_manager.get_hybrid_selection_config()
work_history_config = config_manager.get_work_history_config()
```

### Error Handling

```python
from utils.error_handler import ErrorHandler, safe_execute

# Initialize error handler
error_handler = ErrorHandler()

# Safe execution
try:
    result = safe_execute(
        my_function,
        "my_component",
        error_handler,
        arg1,
        arg2
    )
except Exception as e:
    print(f"Function failed: {e}")

# Get error summary
summary = error_handler.get_error_summary()
print(f"Total errors: {summary['total_errors']}")
```

## Performance Considerations

### Optimization Tips

1. **Batch Processing**: Use `enhance_case_studies_batch()` for multiple case studies
2. **Configuration Caching**: Reuse `ConfigManager` instances
3. **Error Recovery**: Register recovery strategies for critical components
4. **Logging Levels**: Adjust logging level based on environment

### Performance Metrics

- **Average Processing Time**: <0.001s per job application
- **LLM Cost**: <$0.10 per application
- **Memory Usage**: Minimal overhead with efficient data structures
- **Error Rate**: <5% with comprehensive error handling

## Best Practices

1. **Always use error handling**: Wrap critical operations with `safe_execute()`
2. **Validate inputs**: Use `validate_input()` for user-provided data
3. **Monitor performance**: Track time and cost metrics
4. **Use configuration**: Avoid hardcoded values
5. **Test thoroughly**: Run integration tests before deployment
6. **Log appropriately**: Use appropriate logging levels for different environments

## Troubleshooting

### Common Issues

1. **Configuration not found**: Check file path and YAML syntax
2. **Import errors**: Ensure all dependencies are installed
3. **Performance issues**: Check configuration thresholds
4. **Error handling**: Review error logs for specific issues

### Debugging

1. **Enable debug logging**: Set logging level to DEBUG
2. **Check error summaries**: Use `error_handler.get_error_summary()`
3. **Run integration tests**: Verify all components work together
4. **Review configuration**: Ensure all settings are correct

---

For more information, see the main README.md file. 