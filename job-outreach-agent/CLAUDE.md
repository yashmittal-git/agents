# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**job-outreach-agent** is an intelligent orchestrator that coordinates 5 specialized agents (extraction, email, research, content, LinkedIn) to automate personalized job application outreach.

## Core Architecture

### Main Service: `job_outreach_agent/job_orchestrator.py`

The `JobOrchestrator` class coordinates all 5 agents:

```python
class JobOrchestrator:
    def __init__(openai_api_key, gmail_credentials_path, user_profile)
    def process_job(job_info, auto_send=False) -> Dict
    def send_draft(draft_file_path) -> bool
```

### Orchestration Pattern

**Key principle: Delegates everything to specialized agents**
- Does NOT implement extraction, research, content, email, or LinkedIn itself
- Coordinates workflow across 5 independent services
- Adds intelligence layer: channel selection, experience matching
- Located in `job_outreach_agent/job_orchestrator.py`

### 5 Agent Services

1. **extraction-agent** - Extracts job info from screenshots/text/URLs
2. **email-agent** - Sends emails via Gmail API
3. **research-agent** - Researches companies with web scraping + AI
4. **content-agent** - Generates personalized emails/messages
5. **linkedin-agent** - Provides LinkedIn manual guidance

## Development Workflow

### Virtual Environment - REQUIRED
Always activate the shared venv from repository root:
```bash
cd /Users/yash/Documents/agents
source venv/bin/activate
```

### Testing
```bash
# From agent directory
cd job-outreach-agent

# Run example
python example_usage.py

# Run CLI
python job_outreach_cli.py screenshot.png
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e job-outreach-agent
```

## Dependencies

- `python-dotenv` - Environment variable management
- All 5 agent services (extraction, email, research, content, linkedin)

## Key Components

### `JobOrchestrator.process_job()` - Main workflow

**Input:** Job info dict with:
- `company_name`: Company name
- `role`: Job role/title
- `recruiter_email`: Optional email address
- `recruiter_linkedin`: Optional LinkedIn URL
- `requirements`: Job requirements/description
- `user_context`: Optional user notes (what interests them, what to emphasize)

**Important:** All emails automatically BCC the sender's email (from user_profile) for record keeping.

**Workflow:**
1. **Research** company (delegates to research-agent)
2. **Match** experience with job requirements (internal logic)
3. **Recommend channel** (email vs LinkedIn) with confidence score
4. **Generate content** (delegates to content-agent)
5. **Send or save draft** (delegates to email-agent or linkedin-agent)

**Output:** Dict with:
- `channel`: "EMAIL" or "LINKEDIN"
- `confidence`: Percentage confidence in recommendation
- `reasoning`: Why this channel was chosen
- `draft_file`: Path to saved draft
- `sent`: Boolean if auto-send was successful

### Channel Recommendation Logic

**Current channels supported:**
- **EMAIL** - Automated sending via Gmail API
- **LINKEDIN** - Manual guidance with step-by-step instructions

**Future channels:**
- **WhatsApp** - Would provide message + manual instructions (similar to LinkedIn)
- **Direct message** - For company career portals

**Intelligent decision-making:**
- Email available → Prefer EMAIL (90% confidence)
- Only LinkedIn → Use LINKEDIN (85% confidence)
- Both available + senior role → Prefer LINKEDIN (80% confidence)
- Both available + junior role → Prefer EMAIL (75% confidence)

**Factors considered:**
- Contact info availability
- Role seniority
- Company size/culture
- Response rate optimization

### Draft Management

**Draft directory:** `outreach_drafts/`
- Saves all drafts before sending
- Filename: `{company}_{role}_{timestamp}.json`
- Contains: Full job info, research, content, metadata
- Can review and send later with `send_draft()`

## CLI: `job_outreach_cli.py`

**Command-line interface for easy usage:**

```bash
python job_outreach_cli.py <input_file>
```

**Supported inputs:**
- Images: `.png`, `.jpg`, `.jpeg` (screenshots)
- Text: `.txt` (job descriptions)
- URLs: Web page with job posting

**CLI Workflow:**
1. Extracts job info using extraction-agent
2. Runs full orchestration workflow
3. Shows draft preview
4. Asks for user approval
5. Sends or saves based on user choice

**User profile:** Loaded from `.env` file or `example_usage.py`

## Example Usage Patterns

### Example 1: Email outreach
```python
orchestrator = JobOrchestrator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    gmail_credentials_path="../credentials.json",
    user_profile={...}
)

result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Software Engineer",
    "recruiter_email": "careers@anthropic.com",
    "requirements": "Python, AI/ML, 5+ years"
})
# Recommends EMAIL, generates content, sends or saves draft
```

### Example 2: LinkedIn outreach
```python
result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Senior Engineer",
    "recruiter_linkedin": "linkedin.com/in/jane",
    "requirements": "Python, AI"
})
# Recommends LINKEDIN, generates message, provides manual instructions
```

### Example 3: CLI usage
```bash
# From screenshot
python job_outreach_cli.py job_screenshot.png

# From text file
python job_outreach_cli.py job_description.txt
```

## User Profile Data

User-specific data is stored in `data/` directory:
- `Yash_Mittal_Resume.pdf` - Full resume (PDF format)
- `resume_content.txt` - Resume in text format for AI processing
- `portfolio_content.txt` - Portfolio/project details

This data is used by the orchestrator to:
- Personalize outreach content
- Match user experience with job requirements
- Generate relevant highlights and skills
- Provide contact information in signatures

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_key
USER_NAME=Your Name
USER_EMAIL=your@email.com
USER_PHONE=+1234567890
USER_LINKEDIN=linkedin.com/in/yourprofile
USER_PORTFOLIO=https://yourportfolio.com
```

### User Profile
Passed to orchestrator init:
```python
user_profile = {
    "name": "Your Name",
    "email": "your@email.com",
    "linkedin": "linkedin.com/in/yourprofile",
    "portfolio": "https://yourportfolio.com",
    "phone": "+1234567890",
    "highlights": ["Achievement 1", "Achievement 2"],
    "skills": ["Python", "AI/ML", "Kubernetes"],
    "strengths": "Brief summary of strengths"
}
```

## Integration Points

**Uses these agents:**
- extraction-agent: Job info extraction
- email-agent: Email sending
- research-agent: Company research
- content-agent: Content generation
- linkedin-agent: LinkedIn guidance

**Can be used by:**
- CLI applications
- Web services
- Automation workflows
- Other orchestrators

## Important Notes

- **Orchestrator only** - Doesn't implement core functionality itself
- **Intelligent recommendations** - Uses AI + heuristics for channel selection
- **Draft management** - Always saves before sending
- **Manual LinkedIn** - LinkedIn actions require manual user intervention
- **User profile required** - Needs user info for personalization
- **Cost consideration** - Multiple API calls per job (research + content)
- **Gmail setup** - Requires credentials.json for email functionality
