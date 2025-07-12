# 📖 Cover Letter Agent User Guide

> A comprehensive guide to setting up and using the Cover Letter Agent for creating personalized, high-impact cover letters.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **OpenAI API key** (optional, for AI enhancement)
- **Google Drive account** (optional, for cloud storage)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cover-letter-agent.git
   cd cover-letter-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment** (optional, for AI enhancement):
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## 👤 Setting Up Your Profile

### Step 1: Create Your User Profile

```bash
python init_user.py your_name
```

This creates a new user directory at `users/your_name/` with all necessary configuration files.

### Step 2: Add Your Resume

Place your resume in the user directory:
```bash
cp your_resume.pdf users/your_name/resume.pdf
```

### Step 3: Customize Your Configuration

Edit the files in `users/your_name/`:

#### Personal Information (`config.yaml`)

```yaml
name: "Your Name"
role: "Product Manager"
location: "San Francisco, CA"
industry_focus: ["AI/ML", "SaaS", "Growth"]
resume_path: "resume.pdf"

# Google Drive Integration (optional)
google_drive:
  enabled: true
  folder_id: "your_google_drive_folder_id"
  credentials_file: "credentials.json"

# Profile Information
profile:
  linkedin_url: "https://linkedin.com/in/yourusername"
  portfolio_url: "https://yourwebsite.com"
  achievements:
    - "Led product team of 15 engineers"
    - "Increased user engagement by 40%"
    - "Scaled product from 0 to 100K users"

# Cover Letter Preferences
cover_letter:
  personal_brand:
    tagline: "Product leader focused on AI/ML and growth"
    key_strengths:
      - "Data-driven decision making"
      - "Cross-functional leadership"
      - "User-centric product development"
  tone:
    default: "professional"
    startup: "conversational"
    enterprise: "professional"
```

#### Your Content Modules (`blurbs.yaml`)

Create your personalized content modules:

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
  
  - id: leadership
    tags: [leadership]
    text: "I have experience leading cross-functional teams and driving strategic initiatives. At [COMPANY], I [SPECIFIC ACHIEVEMENT]."

closing:
  - id: standard
    tags: [all]
    text: "I am excited about the opportunity to contribute to [COMPANY]'s mission and would welcome the chance to discuss how my experience aligns with your needs."
```

#### Scoring Logic (`blurb_logic.yaml`)

Define how jobs are evaluated and blurbs are selected:

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

#### Job Targeting (`job_targeting.yaml`)

Define your job preferences:

```yaml
titles:
  leadership:
    - "product manager"
    - "product director"
    - "head of product"
    - "senior product manager"
  IC:
    - "product analyst"
    - "product specialist"

comp_target: 150000
locations:
  preferred: ["San Francisco", "New York", "Seattle"]
  open_to: ["Remote", "Austin", "Boston"]

company_stages:
  startup: ["seed", "series a", "series b"]
  growth: ["series c", "series d", "public"]
  enterprise: ["public", "fortune 500"]

business_models:
  b2b: ["saas", "enterprise", "platform"]
  b2c: ["consumer", "marketplace", "mobile"]
```

## 📝 Generating Cover Letters

### Basic Usage

#### From a Job Description File

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt
```

#### From Text Input

```bash
python scripts/run_cover_letter_agent.py --user your_name -t "Senior Product Manager at TechCorp..."
```

#### Save to File

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job_description.txt -o cover_letter.txt
```

### Advanced Options

#### Debug Mode

See detailed scoring and selection logic:

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --debug
```

#### Explain Mode

Get detailed explanations of decisions:

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --explain
```

#### Interactive Mode

Step-by-step confirmation for extraction and gap-filling:

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --interactive
```

#### Track Enhancements

Log improvement suggestions for future reference:

```bash
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --track-enhance
```

## 🤖 AI Enhancement

### Setup

1. **Get OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Create an API key

2. **Configure API Key**:
   ```bash
   # Option A: Create .env file (recommended)
   cp .env.example .env
   # Edit .env and add: OPENAI_API_KEY=sk-your-key-here
   
   # Option B: Set environment variable
   export OPENAI_API_KEY='sk-your-key-here'
   ```

3. **Test Integration**:
   ```bash
   python test_metrics_preservation.py
   ```

### How AI Enhancement Works

1. **Traditional Generation**: The agent first generates a cover letter using your blurbs and logic
2. **AI Post-Processing**: GPT-4 then enhances the draft to:
   - Improve clarity and flow
   - Enhance alignment with the job description
   - Strengthen impact and persuasiveness
   - **Preserve all factual claims and metrics**
3. **Safety Validation**: The system ensures no exaggeration or hallucination

### Safety Features

- **Truth Preservation**: AI cannot add unverified claims
- **Metrics Protection**: All numbers and percentages are preserved
- **Configurable**: Can be enabled/disabled per user
- **Transparent**: Enhanced sections are clearly marked
- **Fallback**: Returns original draft if enhancement fails

## 📊 Enhancement Tracking

### View Enhancement Suggestions

```bash
# View all suggestions
python scripts/run_cover_letter_agent.py --user your_name --log

# View only open suggestions
python scripts/run_cover_letter_agent.py --user your_name --log --log-status open

# View accepted suggestions
python scripts/run_cover_letter_agent.py --user your_name --log --log-status accepted
```

### Manage Enhancement Status

```bash
# Mark suggestion as accepted
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 content_improvement accepted

# Mark suggestion as rejected
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 keyword_optimization rejected

# Add notes to suggestion
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 content_improvement accepted "Added AI/ML keywords"
```

## ☁️ Google Drive Integration

### Setup

1. **Run the setup script**:
   ```bash
   python setup_google_drive.py
   ```

2. **Follow the interactive setup**:
   - Create Google Cloud project
   - Enable Google Drive API
   - Create service account
   - Download credentials
   - Share your Google Drive folder
   - Update configuration

3. **Test integration**:
   ```bash
   python scripts/test_drive_upload.py
   ```

### Features

- **Automatic Draft Saving**: Every cover letter is saved to Google Drive
- **Rich Metadata**: Includes company, position, score, and timestamp
- **Organized Storage**: Files saved in `drafts/` subfolder
- **Easy Access**: All drafts available in your Google Drive

### Configuration

Edit your user config (`users/your_name/config.yaml`):

```yaml
google_drive:
  enabled: true
  folder_id: "your_google_drive_folder_id"
  credentials_file: "credentials.json"
  materials:
    presentations: "presentations/"
    spreadsheets: "spreadsheets/"
    cover_letters: "cover_letters/"
    case_studies: "case_studies/"
    drafts: "drafts/"
```

## 🎯 Best Practices

### Writing Effective Blurbs

1. **Be Specific**: Include concrete achievements and metrics
2. **Use Placeholders**: Use `[COMPANY]`, `[POSITION]`, `[INDUSTRY]` for customization
3. **Tag Appropriately**: Add relevant tags for better matching
4. **Keep it Concise**: Aim for 2-3 sentences per blurb
5. **Maintain Tone**: Ensure consistent professional tone

### Example Effective Blurbs

```yaml
intro:
  - id: ai_leader
    tags: [AI, ML, leadership]
    text: "I'm a product leader with 15+ years of experience building AI/ML products that users trust. I am excited to apply for the [POSITION] role at [COMPANY]."

paragraph2:
  - id: growth_achievement
    tags: [growth, scaling, metrics]
    text: "I build systems that align teams around measurable outcomes. At [COMPANY], I increased user engagement by 40% and scaled the product from 10K to 100K users."
```

### Optimizing Your Logic

1. **Keyword Weights**: Adjust based on your target roles
2. **Minimum Scores**: Set realistic thresholds
3. **Job Classification**: Define clear leadership vs IC criteria
4. **Go/No-Go**: Balance between being selective and not missing opportunities

### Testing Your Setup

1. **Test with Sample Jobs**: Use various job descriptions to test your setup
2. **Review Output**: Check that generated letters match your style
3. **Iterate**: Adjust blurbs and logic based on results
4. **Track Performance**: Monitor enhancement suggestions for patterns

## 🔧 Troubleshooting

### Common Issues

#### "User not found" Error

```bash
# Check available users
python init_user.py --list

# Create new user if needed
python init_user.py your_name
```

#### Configuration Errors

```bash
# Validate your configuration
python -c "from core.config_manager import get_config_manager; cm = get_config_manager('your_name'); print('Config valid')"
```

#### AI Enhancement Not Working

```bash
# Check API key
echo $OPENAI_API_KEY

# Test integration
python test_metrics_preservation.py
```

#### Google Drive Issues

```bash
# Test Google Drive integration
python scripts/test_drive_upload.py

# Check credentials
ls -la credentials.json
```

### Getting Help

1. **Check the logs**: Look for error messages in the output
2. **Run in debug mode**: Use `--debug` flag for detailed information
3. **Validate configuration**: Ensure all YAML files are properly formatted
4. **Test components**: Run individual test files to isolate issues

## 📈 Advanced Usage

### Custom Job Types

Add new job types to your logic:

```yaml
job_classification:
  data_science:
    keywords: ["data scientist", "machine learning", "analytics"]
    min_keyword_count: 1
  product_design:
    keywords: ["ux", "design", "user experience"]
    min_keyword_count: 1
```

### Custom Scoring Rules

Create role-specific scoring:

```yaml
scoring_rules:
  keyword_weights:
    # Your existing weights...
    data_science: 3.0
    ux_design: 2.5
    mobile: 2.0
```

### Batch Processing

Process multiple job descriptions:

```bash
# Create a script to process multiple files
for file in jobs/*.txt; do
  python scripts/run_cover_letter_agent.py --user your_name -i "$file" -o "outputs/$(basename "$file" .txt)_cover_letter.txt"
done
```

## 🎉 Success Tips

1. **Start Simple**: Begin with basic blurbs and gradually refine
2. **Test Regularly**: Use various job descriptions to test your setup
3. **Iterate**: Continuously improve based on results and feedback
4. **Stay Authentic**: Ensure your blurbs reflect your true experience
5. **Monitor Quality**: Use enhancement tracking to identify patterns
6. **Backup Regularly**: Keep copies of your configuration files

---

**Need more help?** Check out the [API Reference](API_REFERENCE.md) for technical details or the [Testing Guide](../TESTING.md) for development information. 