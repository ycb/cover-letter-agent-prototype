# 📄 Cover Letter Agent

## 🚀 Getting Started (Multi-User Setup)

### 1. Create a New User

```bash
python3 init_user.py <user_id>
```
- This creates a new folder under `users/<user_id>/` with all the necessary template files.

### 2. Add Your Resume and Customize
- Place your resume as `resume.pdf` in your user folder.
- Edit `config.yaml` with your personal info and preferences.
- Edit `blurbs.yaml` with your stories, intros, closings, etc.
- Optionally, update `blurb_logic.yaml` and `job_targeting.yaml`.

### 3. Generate a Cover Letter

```bash
python3 scripts/run_cover_letter_agent.py --user <user_id> -i data/job_description.txt
```
- Replace `<user_id>` with your username.
- You can also use `--text "Job description here..."` for quick tests.

### 4. See All Users

```bash
python3 init_user.py --list
```

---

## 🗂 Project Structure

```
cover-letter-agent/
├── users/
│   ├── alice/
│   └── bob/
├── core/
│   └── user_context.py
├── scripts/
│   └── run_cover_letter_agent.py
├── init_user.py
└── templates/
    ├── config_template.yaml
    ├── blurbs_template.yaml
    ├── blurb_logic_template.yaml
    └── job_targeting_template.yaml
```

---

## 📝 Notes
- Each user is fully isolated: their config, blurbs, logic, and resume are private.
- No global or hardcoded user data.
- To add a new user, just run the onboarding script and follow the README in your user folder.
- **Sensitive files** (like resumes or credentials) are not committed to GitHub if `.gitignore` is set up correctly.

---

# 📄 Cover Letter Agent

An intelligent agent that generates customized, accurate, and high-impact cover letters using structured "blurb" modules and a logic-based scoring system.

## 🎯 Features

- **Smart Job Evaluation**: Automatically evaluates job descriptions using keyword matching and scoring logic
- **Go/No-Go Decision**: Determines whether a job is worth applying to based on configurable criteria
- **Blurb-Based Generation**: Uses pre-approved paragraph modules that can be mixed and matched
- **Intelligent Matching**: Selects the most appropriate blurbs based on job requirements and company type
- **LLM Enhancement**: Post-processes drafts with AI to improve clarity, tone, and JD alignment
- **Enhancement Suggestions**: Provides actionable feedback to improve cover letter quality
- **Enhancement Tracking**: Logs and tracks enhancement suggestions with status management
- **Google Drive Integration**: Automatically saves all cover letter drafts to Google Drive with metadata

## 📁 Project Structure

```
project/
├── agents/
│   └── cover_letter_agent.py      # Main agent implementation
├── data/
│   ├── resume.pdf                 # Your resume (for future parsing)
│   ├── job_description.txt        # Sample job description
│   ├── blurbs.yaml               # Pre-approved paragraph modules
│   ├── blurb_logic.yaml          # Scoring and matching logic
│   └── enhancement_log.csv       # Enhancement suggestion tracking
├── scripts/
│   └── run_cover_letter_agent.py # Command-line interface
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pyyaml
```

### 2. Run the Agent

```bash
# Process a job description file
python scripts/run_cover_letter_agent.py -i data/job_description.txt

# Process job description text directly
python scripts/run_cover_letter_agent.py -t "Senior Product Manager at TechCorp..."

# Save output to file
python scripts/run_cover_letter_agent.py -i data/job_description.txt -o cover_letter.txt
```

### 3. View Enhancement Log

```bash
# View all enhancement suggestions
python scripts/run_cover_letter_agent.py --log

# View only open suggestions
python scripts/run_cover_letter_agent.py --log --log-status open
```

## 🔧 Configuration

### Blurbs (`data/blurbs.yaml`)

Pre-approved paragraph modules organized by type:

```yaml
intro:
  - id: standard
    tags: [all]
    text: "I'm a product leader with 15+ years..."
  
  - id: ai_variant
    tags: [AI, ML]
    text: "I focus on clarifying ambiguity and building trust in AI..."

paragraph2:
  - id: growth
    tags: [growth]
    text: "I build systems that align teams around measurable outcomes..."
```

### Logic (`data/blurb_logic.yaml`)

Scoring rules and matching criteria:

```yaml
scoring_rules:
  keyword_weights:
    AI: 3.0
    startup: 2.5
    growth: 2.0

go_no_go:
  minimum_keywords: 3
  minimum_total_score: 5.0
```

## 🤖 LLM Integration

The agent now includes AI-powered enhancement that improves cover letter quality while preserving factual accuracy.

### Configuration

Add LLM settings to your `agent_config.yaml`:

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
2. **LLM Post-Processing**: The draft is then enhanced by an LLM that:
   - Improves clarity and flow
   - Enhances alignment with the job description
   - Strengthens impact and persuasiveness
   - Maintains all factual claims from the original
   - **Preserves all metrics and quantified achievements**
3. **Truth Preservation**: The system includes validation to prevent exaggeration or hallucination
4. **Optional Enhancement**: Can be disabled via configuration if preferred

### Setup

1. **Install OpenAI**: `pip install openai`
2. **Set API Key**: 
   ```bash
   # Option A: Create .env file (recommended)
   cp .env.example .env
   # Edit .env and add your actual API key
   
   # Option B: Set environment variable
   export OPENAI_API_KEY='your-api-key'
   ```
3. **Test Integration**: `python scripts/test_llm_integration.py`

### Safety Features

- **Truth Preservation**: LLM cannot add unverified claims or experiences
- **Metrics Protection**: All percentages, numbers, and quantified achievements are preserved
- **Configurable**: Can be enabled/disabled per user
- **Transparent**: Adds comments to indicate LLM-enhanced sections
- **Fallback**: Returns original draft if LLM enhancement fails

### Validation Features

The system includes comprehensive validation to ensure quality:

- **Exaggeration Detection**: Flags potential overstatements like "spearheaded" or "managed"
- **Metrics Preservation**: Ensures all numbers, percentages, and achievements remain intact
- **Fact Verification**: Validates that all claims are verifiable from the original
- **Structure Maintenance**: Preserves professional cover letter format

### Future Enhancements

**Phase 2** (Planned):
- **Authentic Individual Tone**: Balance personal voice with professionalism
- **Context-Aware Blurb Selection**: Use LLM to augment blurb logic
- **Custom Prompting**: Generate role-specific content
- **Active Feedback Loop**: User-guided refinement

**Phase 3** (Planned):
- **Success Tracking**: Monitor interview outcomes
- **Learning System**: Improve based on user feedback
- **Advanced Personalization**: Tailor to individual writing style

---

## 📊 How It Works

### 1. Job Description Parsing

The agent extracts:
- Company name and job title
- Relevant keywords from the description
- Job type classification (startup, enterprise, AI/ML, etc.)
- Requirements and responsibilities
- Company information

### 2. Scoring & Evaluation

Each job is scored based on:
- **Keyword matching**: Relevant terms get positive scores
- **Strong match keywords**: Product management terms get bonus points
- **Poor match keywords**: Non-relevant terms get negative scores
- **Minimum thresholds**: Jobs must meet criteria to proceed

### 3. Blurb Selection

The agent selects the best blurbs for each section:
- **Intro paragraph**: Matches job type and company size
- **Main paragraph**: Aligns with key responsibilities
- **Examples**: Highlights relevant experience
- **Closing**: Tailored to company and role

### 4. Cover Letter Generation

Combines selected blurbs into a coherent cover letter:
- Replaces placeholders with actual company names
- Maintains consistent tone and flow
- Includes proper formatting and structure

### 5. Enhancement Suggestions

The agent reviews the draft and suggests improvements:
- **Low score issues**: Add more specific keywords
- **Missing examples**: Include concrete experience
- **Weak closing**: Strengthen with company research
- **Generic content**: Make more specific to the role

## 🎛️ Command Line Options

```bash
python scripts/run_cover_letter_agent.py [OPTIONS]

Options:
  -i, --input-file FILE     Input job description file
  -t, --text TEXT          Job description text
  -o, --output-file FILE   Output cover letter file
  -d, --data-dir DIR       Data directory (default: data)
  --log                    Show enhancement log
  --log-status STATUS      Filter log by status (open/accepted/rejected)
  --update-status JOB_ID ENHANCEMENT_TYPE STATUS
                           Update enhancement suggestion status
  -v, --verbose           Verbose output
```

## 📈 Enhancement Tracking

The system tracks enhancement suggestions with:

- **Status**: `open`, `accepted`, `rejected`
- **Priority**: `high`, `medium`, `low`
- **Category**: `content_improvement`, `keyword_optimization`, etc.
- **Notes**: Additional context and implementation details

### Managing Enhancements

```bash
# View open suggestions
python scripts/run_cover_letter_agent.py --log --log-status open

# Mark suggestion as accepted
python scripts/run_cover_letter_agent.py --update-status JOB_001 content_improvement accepted

# Add notes to suggestion
python scripts/run_cover_letter_agent.py --update-status JOB_001 keyword_optimization accepted "Added AI/ML keywords"
```

## 🔍 Job Types Supported

The agent recognizes and optimizes for:

- **Startup**: Early-stage, fast-paced, growth-focused
- **Enterprise**: Large-scale, B2B, corporate environment
- **AI/ML**: Artificial intelligence and machine learning focus
- **Cleantech**: Climate, energy, sustainability focus
- **Internal Tools**: Productivity, efficiency, operations focus

## 📝 Customizing Blurbs

To add new blurbs or modify existing ones:

1. Edit `data/blurbs.yaml`
2. Add new blurb entries with appropriate tags
3. Update scoring logic in `data/blurb_logic.yaml` if needed
4. Test with sample job descriptions

### Blurb Structure

```yaml
intro:
  - id: your_new_blurb
    tags: [relevant, keywords, here]
    text: "Your blurb text here..."
```

## 🎯 Scoring Logic

### Keyword Weights

- **AI/ML terms**: 3.0 points
- **Startup terms**: 2.5 points
- **Growth/Scaling**: 2.0 points
- **Enterprise/B2B**: 2.0 points
- **Trust/Explainable**: 1.5 points

### Minimum Scores

- **AI variant intro**: 2.0 points required
- **Startup variant intro**: 1.5 points required
- **Growth paragraph**: 1.5 points required
- **Cleantech paragraph**: 2.0 points required

### Go/No-Go Criteria

- **Minimum keywords**: 3 relevant terms
- **Minimum total score**: 5.0 points
- **Strong match bonus**: +2.0 for product management terms
- **Poor match penalty**: -1.0 for non-relevant terms

## 🔮 Future Enhancements

- **Resume parsing**: Extract experience from PDF resume
- **Company research**: Auto-research company for better customization
- **A/B testing**: Test different blurb combinations
- **Learning system**: Improve scoring based on application outcomes
- **Template expansion**: Add more specialized blurb types
- **Multi-language support**: Generate cover letters in different languages

## 📁 Google Drive Integration

The agent can access supporting materials from Google Drive and automatically saves all cover letter drafts with metadata.

### Features

- **Automatic Draft Saving**: Every cover letter is automatically uploaded to Google Drive
- **Rich Metadata**: Includes company name, position, job score, and timestamp
- **Organized Storage**: Files are saved in a dedicated `drafts/` subfolder
- **Easy Access**: All drafts are available in your Google Drive folder under `drafts/`
- **Separation**: Drafts are kept separate from approved/submitted cover letters

### Setup Google Drive Integration

1. **Install required packages:**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Run the setup script:**
   ```bash
   python setup_google_drive.py
   ```

2. **Follow the interactive setup:**
   - Create Google Cloud project
   - Enable Google Drive API
   - Create service account
   - Download credentials
   - Share your Google Drive folder
   - Update configuration

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Supported Materials

- **Presentations**: Slides and decks
- **Spreadsheets**: Metrics and data
- **Past Cover Letters**: Previous applications
- **Case Studies**: Portfolio materials

### Configuration

Edit `data/agent_config.yaml`:

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

### Testing Drive Upload

Test the Google Drive upload functionality:

```bash
python scripts/test_drive_upload.py
```

This will verify that your credentials and folder permissions are working correctly.

## 📚 Case Study Management

### URL-Based Case Studies

Add case study URLs to `data/agent_config.yaml`:

```yaml
case_studies:
  urls:
    - name: "Aurora Solar Growth Case Study"
      url: "https://example.com/aurora-solar-case-study"
      description: "Scaling B2B platform from 10 to 10,000+ customers"
      tags: [growth, B2B, clean_energy, scaling]
```

### Local Case Study Files

Add local files to the configuration:

```yaml
case_studies:
  local_files:
    - name: "Aurora Solar Metrics"
      file_path: "case_studies/aurora_metrics.pdf"
      description: "Detailed metrics and KPIs from Aurora Solar growth"
      tags: [growth, metrics, B2B]
```

### Google Drive Case Studies

Materials in your Google Drive folder are automatically detected and matched to job keywords.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new blurbs or improve logic
4. Test with sample job descriptions
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This agent is designed for product management roles but can be easily adapted for other positions by modifying the blurbs and logic configuration. 