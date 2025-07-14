# 📄 Cover Letter Agent

> An intelligent, AI-powered cover letter generation system that creates customized, high-impact cover letters using structured content modules and advanced matching algorithms.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked: MyPy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

## 🎯 What is the Cover Letter Agent?

The Cover Letter Agent is a sophisticated system that generates personalized, high-quality cover letters by combining **structured content management** with **intelligent job matching** and **AI-powered enhancement**.

### How It Works

1. **Content Management**: You create a library of pre-approved paragraph modules (blurbs) that represent your experience, achievements, and skills
2. **Smart Matching**: The system analyzes job descriptions and intelligently selects the most relevant content modules
3. **Intelligent Assembly**: Blurbs are assembled into coherent cover letters using configurable logic and scoring rules
4. **AI Enhancement**: Optional LLM-powered post-processing improves clarity, tone, and alignment while preserving all factual claims
5. **Quality Control**: Built-in gap analysis identifies missing requirements and suggests improvements

### Key Benefits

- **Consistency**: Pre-approved content ensures all cover letters maintain your professional voice
- **Efficiency**: Generate high-quality cover letters in minutes, not hours
- **Customization**: Each letter is tailored to specific job requirements and company context
- **Quality**: AI enhancement improves clarity and impact while preserving accuracy
- **Organization**: Automatic Google Drive integration keeps all drafts organized

### Perfect For

- **Job seekers** who want to apply to many positions efficiently
- **Professionals** who need to maintain consistent personal branding
- **Career changers** who want to highlight transferable skills
- **Busy professionals** who need high-quality cover letters quickly

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cover-letter-agent.git
cd cover-letter-agent

# Install dependencies
pip install -r requirements.txt

# Set up your environment
cp .env.example .env
# Edit .env with your OpenAI API key (optional)
```

### 2. Create Your Profile

```bash
# Initialize a new user profile
python init_user.py your_name

# This creates: users/your_name/ with all configuration files
```

### 3. Customize Your Content

Edit the files in `users/your_name/`:
- **`config.yaml`** - Your personal information and preferences
- **`blurbs.yaml`** - Your cover letter content modules
- **`blurb_logic.yaml`** - Scoring and matching rules
- **`job_targeting.yaml`** - Job filtering criteria
- **`resume.pdf`** - Your resume (add this file)

### 4. Generate Your First Cover Letter

```bash
# Process a job description file
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt

# Or process text directly
python scripts/run_cover_letter_agent.py --user your_name -t "Senior Product Manager at TechCorp..."
```

## 📚 Documentation

- **[Quick Reference](docs/QUICK_REFERENCE.md)**: Commands, configs, and troubleshooting
- **[User Guide](docs/USER_GUIDE.md)**: Complete setup and usage guide
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Architecture and contribution guide
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Testing Guide](TESTING.md)**: How to run tests and contribute
- **[LLM Integration Results](LLM_INTEGRATION_TEST_RESULTS.md)**: AI enhancement validation
- **[Performance Demo](scripts/performance_demo.py)**: Performance optimization demonstration

## ✨ Key Features

### 🎯 **Smart Job Evaluation**
- Automatically analyzes job descriptions using keyword matching and scoring logic
- Provides go/no-go decisions based on configurable criteria
- Extracts company information, requirements, and responsibilities

### 📝 **Blurb-Based Generation**
- Uses pre-approved paragraph modules that can be mixed and matched
- Intelligent selection based on job requirements and company type
- Maintains consistency while allowing customization

### 🤖 **AI-Powered Enhancement**
- Post-processes drafts with GPT-4 to improve clarity, tone, and alignment
- **Strict truth preservation** - never adds or changes factual claims
- Preserves all metrics, percentages, and quantified achievements
- Optional enhancement that can be disabled

### 🔍 **Interactive Gap Analysis**
- Identifies missing requirements in your content
- Suggests new blurbs to fill gaps
- Interactive approval workflow for new content
- Saves approved blurbs for future reuse

### 📊 **Enhancement Tracking**
- Logs and tracks improvement suggestions with status management
- Provides actionable feedback to improve cover letter quality
- Supports status tracking: open, accepted, rejected

### ☁️ **Google Drive Integration**
- Automatically saves all cover letter drafts with rich metadata
- Access supporting materials from Google Drive
- Organized storage with company and position information

### 🧪 **Comprehensive Testing**
- Full test suite with pytest
- Type checking with MyPy
- Code quality with flake8, black, and isort
- CI/CD integration with GitHub Actions

### ⚡ **Performance Optimization**
- Intelligent caching for file I/O operations
- Job description parsing optimization
- Blurb selection performance improvements
- LLM API call caching and memoization
- Comprehensive performance monitoring and metrics

## 🏗️ Architecture

### Core Components

```
cover-letter-agent/
├── agents/
│   ├── cover_letter_agent.py      # Main agent implementation
│   ├── context_analyzer.py        # Job analysis and insights
│   ├── gap_analysis.py           # Requirement gap analysis
│   ├── google_drive_integration.py # Google Drive integration
│   └── resume_parser.py          # Resume parsing (future)
├── core/
│   ├── config_manager.py         # Centralized configuration
│   ├── user_context.py           # User data management
│   ├── types.py                  # Type definitions
│   ├── logging_config.py         # Logging setup
│   └── performance.py            # Performance optimization and caching
├── users/
│   └── [user_id]/               # Per-user configuration
├── scripts/
│   └── run_cover_letter_agent.py # Command-line interface
└── docs/
    └── API_REFERENCE.md          # Complete API documentation
```

### Multi-User Architecture

Each user has their own isolated environment:
- **Personal configuration** in `users/[user_id]/`
- **Private blurbs and logic** specific to their experience
- **Secure data handling** with no cross-user data sharing
- **Customizable scoring** and targeting rules

## 🎛️ Configuration

### User Configuration (`users/[user_id]/config.yaml`)

```yaml
name: "John Doe"
role: "Product Manager"
location: "San Francisco, CA"
industry_focus: ["AI/ML", "SaaS", "Growth"]
resume_path: "resume.pdf"

google_drive:
  enabled: true
  folder_id: "your_google_drive_folder_id"
  credentials_file: "credentials.json"

profile:
  linkedin_url: "https://linkedin.com/in/johndoe"
  portfolio_url: "https://johndoe.com"
  achievements:
    - "Led product team of 15 engineers"
    - "Increased user engagement by 40%"

cover_letter:
  personal_brand:
    tagline: "Product leader focused on AI/ML and growth"
    key_strengths:
      - "Data-driven decision making"
      - "Cross-functional leadership"
  tone:
    default: "professional"
    startup: "conversational"
    enterprise: "professional"
```

### Blurbs (`users/[user_id]/blurbs.yaml`)

Pre-approved paragraph modules organized by type:

```yaml
intro:
  - id: standard
    tags: [all]
    text: "I'm a product leader with 15+ years of experience in [INDUSTRY]. I am excited to apply for the [POSITION] role at [COMPANY]."
  
  - id: ai_variant
    tags: [AI, ML]
    text: "I focus on clarifying ambiguity and building trust in AI systems. I am excited to apply for the [POSITION] role at [COMPANY]."

paragraph2:
  - id: growth
    tags: [growth]
    text: "I build systems that align teams around measurable outcomes. At [COMPANY], I [SPECIFIC ACHIEVEMENT]."

closing:
  - id: standard
    tags: [all]
    text: "I am excited about the opportunity to contribute to [COMPANY]'s mission and would welcome the chance to discuss how my experience aligns with your needs."
```

### Logic (`users/[user_id]/blurb_logic.yaml`)

Scoring rules and matching criteria:

```yaml
scoring_rules:
  keyword_weights:
    AI: 3.0
    ML: 3.0
    startup: 2.5
    growth: 2.0
    leadership: 2.0
    clean_tech: 2.0

go_no_go:
  minimum_keywords: 3
  minimum_total_score: 5.0
  strong_match_keywords: ["AI", "ML", "growth", "startup"]
  poor_match_keywords: ["junior", "entry-level", "intern"]

job_classification:
  leadership:
    keywords: ["manager", "director", "lead", "head", "chief"]
    min_keyword_count: 1
  IC:
    keywords: ["analyst", "specialist", "coordinator"]
    min_keyword_count: 1
```

## 🤖 AI-Powered Enhancement

The agent includes intelligent LLM-powered enhancement that improves cover letter quality while preserving factual accuracy.

### Configuration

Add LLM settings to your `agent_config.yaml`:

```yaml
llm_enhancement:
  enabled: true
  model: "gpt-4o-mini"
  temperature: 0.3
  confidence_threshold: 0.5
  preserve_metrics: true
  preserve_user_voice: true
```

### LLM Enhancement Features

- **Post-Draft Enhancement**: Improves clarity, flow, and tone after blurb assembly
- **Truth Preservation**: Never changes factual claims, metrics, or achievements
- **Contextual Alignment**: Uses job description and metadata for targeted improvements
- **Confidence Scoring**: Only applies enhancements above a confidence threshold
- **Draft Comparison**: Saves both original and enhanced drafts for review
- **Safety Features**: Validates changes and warns about potential issues

```yaml
# LLM Enhancement Configuration
llm_enhance: true
llm_model: "gpt-4"
llm_temperature: 0.5
llm_preserve_truth: true
llm_add_comments: true
```

### How It Works

1. **Logic-Based Generation**: First, the agent generates a cover letter using the traditional blurb-based approach
2. **LLM Post-Processing**: The draft is then enhanced by GPT-4 that:
   - Improves clarity and flow
   - Enhances alignment with the job description
   - Strengthens impact and persuasiveness
   - Maintains all factual claims from the original
   - **Preserves all metrics and quantified achievements**
3. **Truth Preservation**: The system includes validation to prevent exaggeration or hallucination
4. **Optional Enhancement**: Can be disabled via configuration if preferred

### Safety Features

- **Truth Preservation**: LLM cannot add unverified claims or experiences
- **Metrics Protection**: All percentages, numbers, and quantified achievements are preserved
- **Configurable**: Can be enabled/disabled per user
- **Transparent**: Adds comments to indicate LLM-enhanced sections
- **Fallback**: Returns original draft if LLM enhancement fails

### Testing LLM Enhancement

Test the LLM enhancement functionality:

```bash
# Test with mock data (no API key required)
python test_llm_mock.py

# Test with real API calls (requires OpenAI API key)
python test_llm_enhancement.py

# Test with CLI tool
python cli/test_llm_enhancement.py --jd job.txt --cl draft.txt
```

### Setup

1. **Get OpenAI API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/)
2. **Configure API Key**:
   ```bash
   # Option A: Create .env file (recommended)
   cp .env.example .env
   # Edit .env and add your actual API key
   
   # Option B: Set environment variable
   export OPENAI_API_KEY='your-api-key'
   ```
3. **Test Integration**: `python test_metrics_preservation.py`

## 📊 Job Types Supported

The agent recognizes and optimizes for:

- **Startup**: Early-stage, fast-paced, growth-focused
- **Enterprise**: Large-scale, B2B, corporate environment
- **AI/ML**: Artificial intelligence and machine learning focus
- **Cleantech**: Climate, energy, sustainability focus
- **Internal Tools**: Productivity, efficiency, operations focus

## 🎛️ Command Line Interface

### Basic Usage

```bash
# Process a job description file
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt

# Process job description text directly
python scripts/run_cover_letter_agent.py --user your_name -t "Senior Product Manager at TechCorp..."

# Save output to file
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt -o cover_letter.txt
```

### Advanced Options

```bash
# Enable debug mode (shows scoring details)
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --debug

# Show detailed explanations
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --explain

# Track enhancement suggestions
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --track-enhance

# Interactive mode (step-by-step confirmation)
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --interactive
```

### Enhancement Management

```bash
# View all enhancement suggestions
python scripts/run_cover_letter_agent.py --user your_name --log

# View only open suggestions
python scripts/run_cover_letter_agent.py --user your_name --log --log-status open

# Mark suggestion as accepted
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 content_improvement accepted

# Add notes to suggestion
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 keyword_optimization accepted "Added AI/ML keywords"
```

## ☁️ Google Drive Integration

### Features

- **Automatic Draft Saving**: Every cover letter is automatically uploaded to Google Drive
- **Rich Metadata**: Includes company name, position, job score, and timestamp
- **Organized Storage**: Files are saved in a dedicated `drafts/` subfolder
- **Easy Access**: All drafts are available in your Google Drive folder under `drafts/`
- **Separation**: Drafts are kept separate from approved/submitted cover letters

### ⚠️ Important: OAuth Authentication

The integration uses OAuth 2.0 for regular Google accounts (no storage quota limitations). See **[Google Drive Setup Guide](docs/GOOGLE_DRIVE_FIX.md)** for setup instructions.

### Setup

1. **Run the setup script**:
   ```bash
   python setup_google_drive.py
   ```

2. **Follow the interactive setup**:
   - Create Google Cloud project
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download credentials.json
   - Create Google Drive folder
   - Update configuration

3. **First-time authentication**:
   ```bash
   # Run the agent - browser will open for Google authentication
   python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt
   ```

4. **Test integration**:
   ```bash
   python scripts/test_drive_upload.py
   ```

### Configuration

Edit your user config (`users/[user_id]/config.yaml`):

```yaml
google_drive:
  enabled: true
  folder_id: "your_google_drive_folder_id"
  credentials_file: "credentials.json"
  use_oauth: true
  token_file: "token.json"
  materials:
    presentations: "presentations/"
    spreadsheets: "spreadsheets/"
    cover_letters: "cover_letters/"
    case_studies: "case_studies/"
    drafts: "drafts/"
```

## 🧪 Testing & Quality

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
python -m pytest test_config_management.py -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make typecheck
```

### CI/CD

The project includes GitHub Actions workflows for:
- **Continuous Integration**: Tests on Python 3.8, 3.9, 3.10
- **Code Quality**: Linting with flake8, black, isort, mypy
- **Automated Testing**: Runs on every push and pull request

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `make test`
5. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install

# Run all quality checks
make all
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Uses OpenAI's GPT models for enhancement
- Integrates with Google Drive for storage
- Follows clean code principles and comprehensive testing

---

**Note**: This agent is designed for product management roles but can be easily adapted for other positions by modifying the blurbs and logic configuration. 

---

## 🚀 LLM Integration Setup (OpenAI API Key)

To use the LLM-powered enhancement features, you must provide your OpenAI API key. This is required for all CLI and test runs.

1. **Create a `.env` file in the project root:**

   Copy the following into a file named `.env`:
   
   ```env
   OPENAI_API_KEY=sk-...
   ```
   Replace `sk-...` with your actual OpenAI API key.

2. **No need to set environment variables in your shell.**
   - The agent and all test scripts will automatically load the `.env` file.
   - If the key is missing, you will see a clear error message and the script will exit.

3. **Do not commit your real `.env` file to version control.**
   - Use `.env.example` as a template for sharing setup instructions. 

## PM Role + Level Inference System (pm-levels branch)

This feature introduces a structured system for inferring a user's Product Manager (PM) role type, level, archetype, and core competencies using resume, LinkedIn, and work samples (STAR stories, case studies, shipped products, etc.).

- **Data Model:**
  - `pm_inference` section in user config stores the latest inference results.
  - `work_samples.yaml` stores structured STAR stories and case studies, each with metadata (title, type, source, role, tags, impact, etc.).
- **UserContext:**
  - Now loads and exposes `pm_inference` and `work_samples` for each user.
- **Inference Logic:**
  - `agents/pm_inference.py` scaffolds an LLM-based inference function to analyze user data and return a PM profile.
- **Next Steps:**
  - Integrate inference into onboarding and data upload flows.
  - Add user feedback and LLM prompt logic.

This system enables personalized cover letter generation, benchmarking, and gap analysis based on a user's real experience and strengths. 