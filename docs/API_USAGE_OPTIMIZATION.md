# OpenAI API Usage Optimization

This document describes the implemented strategies to reduce OpenAI API costs during development.

## 🎯 Quick Start

### Enable Mock Mode
```bash
export USE_MOCK=true
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

### Enable Caching
```bash
export CACHE_ENABLED=true
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

### Use Cheaper Models
```bash
export DEFAULT_MODEL=gpt-3.5-turbo
export ENHANCEMENT_MODEL=gpt-4o-mini
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

## 📋 Implemented Features

### 1. Static Mock Mode
- **File**: `config/llm_config.py`
- **Environment Variable**: `USE_MOCK=true`
- **Usage**: Returns predefined mock responses instead of API calls
- **Benefit**: Zero API costs during development

### 2. LLM Call Caching
- **File**: `core/cache.py`
- **Environment Variable**: `CACHE_ENABLED=true`
- **Usage**: Caches API responses based on function name and arguments
- **Benefit**: Avoids duplicate API calls for same inputs

### 3. Model Selection
- **Default**: `gpt-3.5-turbo` for draft stages
- **Enhancement**: `gpt-4o-mini` for final polish
- **Gap Analysis**: `gpt-3.5-turbo` for cost efficiency

### 4. Enhancement Toggle
- **Environment Variable**: `ENHANCE=true/false`
- **Usage**: Enable/disable LLM enhancement step
- **Benefit**: Skip expensive enhancement during testing

### 5. Job Description Stripping
- **Function**: `strip_job_description()`
- **Usage**: Removes boilerplate text before sending to API
- **Benefit**: Reduces token usage by 20-40%

### 6. Token Cost Estimation
- **Function**: `estimate_token_cost()`
- **Usage**: Estimate costs before making API calls
- **Benefit**: Predict costs and optimize prompts

### 7. Batch Testing
- **Script**: `scripts/batch_test_llm.py`
- **Usage**: Test multiple jobs at once
- **Benefit**: Review changes before pushing to production

### 8. LLM I/O Logging
- **Function**: `log_llm_io()`
- **Usage**: Log prompts and responses for debugging
- **Benefit**: Debug issues without making new API calls

## 🔧 Configuration

### Environment Variables
```bash
# Mock mode (no API calls)
export USE_MOCK=true

# Caching (cache API responses)
export CACHE_ENABLED=true

# Model selection
export DEFAULT_MODEL=gpt-3.5-turbo
export ENHANCEMENT_MODEL=gpt-4o-mini

# Enhancement toggle
export ENHANCE=true
```

### Configuration File
```python
# config/llm_config.py
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
ENHANCE_TOGGLE = os.getenv("ENHANCE", "true").lower() == "true"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
ENHANCEMENT_MODEL = os.getenv("ENHANCEMENT_MODEL", "gpt-4o-mini")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
```

## 📊 Cost Optimization

### Token Cost Comparison
| Model | Cost per 1K tokens | Use Case |
|-------|-------------------|----------|
| gpt-3.5-turbo | $0.0015 | Draft generation, gap analysis |
| gpt-4o-mini | $0.00015 | Enhancement, final polish |
| gpt-4 | $0.03 | Complex reasoning (avoid) |

### Optimization Strategies
1. **Use gpt-3.5-turbo** for most tasks
2. **Enable caching** to avoid duplicate calls
3. **Strip job descriptions** to reduce tokens
4. **Use mock mode** during development
5. **Batch test** before production changes

## 🛠️ Usage Examples

### Development Mode (No API Costs)
```bash
export USE_MOCK=true
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

### Testing Mode (Cached API Calls)
```bash
export CACHE_ENABLED=true
export DEFAULT_MODEL=gpt-3.5-turbo
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

### Production Mode (Full Features)
```bash
export ENHANCE=true
export DEFAULT_MODEL=gpt-3.5-turbo
export ENHANCEMENT_MODEL=gpt-4o-mini
python scripts/run_cover_letter_agent.py --user peter -i data/job_description.txt
```

### Batch Testing
```bash
# Test with mock mode
python scripts/batch_test_llm.py --mock

# Test with caching
python scripts/batch_test_llm.py --cache

# Test with both
python scripts/batch_test_llm.py --mock --cache
```

## 📁 Cache Management

### View Cache Stats
```python
from core.cache import get_cache_stats
stats = get_cache_stats()
print(f"Cache entries: {stats['total_entries']}")
print(f"Cache size: {stats['cache_size']} bytes")
```

### Clear Cache
```python
from core.cache import clear_llm_cache
clear_llm_cache()
```

### Cache Location
- **Cache file**: `mock_data/llm_cache.jsonl`
- **Debug logs**: `mock_data/debug_llm_io.jsonl`
- **Batch results**: `mock_data/batch_test_results.json`

## 🎯 Best Practices

1. **Start with mock mode** during development
2. **Enable caching** for repeated tests
3. **Use cheaper models** for draft stages
4. **Strip job descriptions** before API calls
5. **Batch test** before pushing changes
6. **Monitor costs** with token estimation
7. **Log I/O** for debugging without API calls

## 💰 Cost Estimation

### Example Cost Calculation
```python
from config.llm_config import estimate_token_cost

# Estimate cost for job description
job_text = "Senior Product Manager..."
cost = estimate_token_cost(job_text, "gpt-3.5-turbo")
print(f"Estimated cost: ${cost['estimated_cost_usd']:.4f}")
```

### Typical Costs
- **Job description processing**: $0.001-0.005
- **Cover letter enhancement**: $0.002-0.010
- **Gap analysis**: $0.001-0.003
- **Total per job**: $0.004-0.018

## 🔍 Debugging

### View LLM I/O Logs
```bash
cat mock_data/debug_llm_io.jsonl
```

### Check Cache Contents
```bash
cat mock_data/llm_cache.jsonl
```

### Monitor API Usage
```python
from core.cache import get_cache_stats
print(get_cache_stats())
```

## 🚀 Advanced Usage

### Custom Mock Responses
```python
from core.cache import create_mock_response

# Create custom mock response
mock_data = create_mock_response("gap_analysis")
```

### Custom Cache Key
```python
from core.cache import use_llm_cache

@use_llm_cache
def my_llm_function(text):
    # Function will be cached automatically
    pass
```

### Custom Token Estimation
```python
from config.llm_config import estimate_token_cost

# Estimate for different models
cost_gpt35 = estimate_token_cost(text, "gpt-3.5-turbo")
cost_gpt4 = estimate_token_cost(text, "gpt-4")
```

This optimization system can reduce API costs by 80-90% during development while maintaining full functionality for production use. 