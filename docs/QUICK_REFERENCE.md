# ⚡ Cover Letter Agent Quick Reference

> Quick commands, configuration snippets, and troubleshooting tips for the Cover Letter Agent.

## 🚀 Quick Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create new user
python init_user.py your_name

# Set up environment (optional)
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Basic Usage
```bash
# Process job description file
python scripts/run_cover_letter_agent.py --user your_name -i job.txt

# Process text directly
python scripts/run_cover_letter_agent.py --user your_name -t "Senior PM at TechCorp..."

# Save to file
python scripts/run_cover_letter_agent.py --user your_name -i job.txt -o cover_letter.txt
```

### Advanced Options
```bash
# Debug mode (shows scoring details)
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --debug

# Explain mode (detailed explanations)
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --explain

# Interactive mode
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --interactive

# Track enhancements
python scripts/run_cover_letter_agent.py --user your_name -i job.txt --track-enhance
```

### Enhancement Management
```bash
# View all suggestions
python scripts/run_cover_letter_agent.py --user your_name --log

# View open suggestions only
python scripts/run_cover_letter_agent.py --user your_name --log --log-status open

# Mark suggestion as accepted
python scripts/run_cover_letter_agent.py --user your_name --update-status JOB_001 content_improvement accepted
```

### Development
```bash
# Run tests
make test

# Run with coverage
make coverage

# Format code
make format

# Lint code
make lint

# Type checking
make typecheck

# All quality checks
make all
```

## ⚙️ Configuration Snippets

### User Config (`users/[user_id]/config.yaml`)
```yaml
name: "Your Name"
role: "Product Manager"
location: "San Francisco, CA"
industry_focus: ["AI/ML", "SaaS", "Growth"]

google_drive:
  enabled: true
  folder_id: "your_google_drive_folder_id"
  credentials_file: "credentials.json"

profile:
  linkedin_url: "https://linkedin.com/in/yourusername"
  achievements:
    - "Led product team of 15 engineers"
    - "Increased user engagement by 40%"

cover_letter:
  personal_brand:
    tagline: "Product leader focused on AI/ML and growth"
  tone:
    default: "professional"
    startup: "conversational"
```

### Blurbs (`users/[user_id]/blurbs.yaml`)
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
```yaml
scoring_rules:
  keyword_weights:
    AI: 3.0
    ML: 3.0
    startup: 2.5
    growth: 2.0
    leadership: 2.0

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

### Job Targeting (`users/[user_id]/job_targeting.yaml`)
```yaml
titles:
  leadership:
    - "product manager"
    - "product director"
    - "head of product"
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

## 🔧 Troubleshooting

### Common Issues

#### "User not found" Error
```bash
# Check available users
python init_user.py --list

# Create new user
python init_user.py your_name
```

#### Configuration Errors
```bash
# Validate configuration
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

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt
```

### Debug Mode Output

When using `--debug`, you'll see:
```
[DEBUG] Job Score: 7.5
[DEBUG] Selected blurbs:
  - intro: ai_variant (score: 8.2)
  - paragraph2: growth (score: 7.8)
  - closing: standard (score: 6.5)
[DEBUG] Enhancement suggestions: 2
```

### Explain Mode Output

When using `--explain`, you'll see:
```
EXPLANATION:
- Job classified as: startup (AI/ML focus)
- Go/No-Go: GO (score: 7.5 > 5.0)
- Blurb selection reasoning:
  - AI variant intro selected due to AI/ML keywords
  - Growth paragraph selected for startup context
  - Standard closing for general applicability
```

## 📊 Performance Tips

### Optimizing Blurbs
- **Be Specific**: Include concrete achievements and metrics
- **Use Placeholders**: `[COMPANY]`, `[POSITION]`, `[INDUSTRY]`
- **Tag Appropriately**: Add relevant tags for better matching
- **Keep Concise**: 2-3 sentences per blurb

### Optimizing Logic
- **Keyword Weights**: Adjust based on target roles
- **Minimum Scores**: Set realistic thresholds
- **Job Classification**: Define clear criteria
- **Go/No-Go**: Balance selectivity with opportunities

### Testing Your Setup
```bash
# Test with sample job
echo "Senior Product Manager at AI Startup" > test_job.txt
python scripts/run_cover_letter_agent.py --user your_name -i test_job.txt

# Test with different job types
echo "Enterprise Product Director" > enterprise_job.txt
python scripts/run_cover_letter_agent.py --user your_name -i enterprise_job.txt
```

## 🔍 File Locations

### User Files
```
users/[user_id]/
├── config.yaml          # Personal information
├── blurbs.yaml          # Content modules
├── blurb_logic.yaml     # Scoring logic
├── job_targeting.yaml   # Job preferences
├── resume.pdf           # Your resume
└── enhancement_log.csv  # Enhancement tracking
```

### System Files
```
cover-letter-agent/
├── agents/              # Core business logic
├── core/                # Shared utilities
├── scripts/             # Command-line tools
├── templates/           # Configuration templates
├── docs/                # Documentation
└── tests/               # Test files
```

## 🎯 Best Practices

### Writing Effective Blurbs
1. **Include Metrics**: "Increased engagement by 40%"
2. **Use Action Verbs**: "Led", "Built", "Scaled"
3. **Be Specific**: "Led team of 15 engineers"
4. **Match Job Type**: Different blurbs for startup vs enterprise
5. **Maintain Tone**: Consistent professional voice

### Configuration Management
1. **Backup Regularly**: Keep copies of your config files
2. **Version Control**: Track changes to your blurbs
3. **Test Iteratively**: Refine based on results
4. **Document Changes**: Note what works and what doesn't

### AI Enhancement
1. **Start Conservative**: Use lower temperature for consistency
2. **Monitor Quality**: Check enhancement suggestions
3. **Preserve Truth**: Never let AI add unverified claims
4. **Test Thoroughly**: Validate with various job types

## 📞 Getting Help

### Documentation
- **[User Guide](USER_GUIDE.md)**: Complete setup guide
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Technical details
- **[API Reference](API_REFERENCE.md)**: Code documentation

### Support
- **GitHub Issues**: Report bugs or request features
- **Debug Mode**: Use `--debug` for detailed output
- **Test Files**: Run individual test files to isolate issues

### Community
- **Contributing**: See [Developer Guide](DEVELOPER_GUIDE.md)
- **Code Review**: Follow the checklist in the developer guide
- **Testing**: Add tests for new features

---

**Quick Tip**: Use `--debug` and `--explain` flags to understand how the system works and make better configuration decisions. 