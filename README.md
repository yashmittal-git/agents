# Agents Monorepo

**Modular AI Agent Services** - A collection of standalone, reusable AI agent services for extraction, email, research, content generation, LinkedIn, and intelligent job outreach orchestration.

## Structure

```
agents/
├── extraction-agent/         # Universal content extraction (AI-powered)
├── email-agent/              # Gmail API email sending
├── research-agent/           # AI-powered web research
├── content-agent/            # AI content generation
├── linkedin-agent/           # LinkedIn messaging (placeholder)
├── job-outreach-agent/       # Intelligent orchestrator (uses all 5)
├── web-app/                  # 🆕 Web UI with async processing (Docker)
├── venv/                     # Shared virtual environment
├── docker-compose.yml        # 🆕 Full-stack Docker orchestration
├── .env                      # Environment variables (gitignored)
├── .env.example              # Template for .env
├── credentials.json          # Gmail OAuth credentials (gitignored)
├── token.json                # Gmail OAuth token (gitignored)
└── README.md                 # This file
```

## Quick Start

### Option 1: Web Application (Recommended) 🆕

**Full-featured web UI with async processing, database persistence, and real-time status updates.**

```bash
# 1. Install Docker Desktop (if not installed)
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Configure environment
cp .env.docker .env
# Edit .env with your OPENAI_API_KEY, USER_EMAIL, USER_NAME

# 3. Start all services (Flask, Celery, PostgreSQL, Redis, RabbitMQ)
docker-compose up -d

# 4. Access the web UI
open http://localhost:5000
```

**Features**:
- Upload job postings (images, PDFs, text, URLs)
- Async processing with real-time status updates
- Draft editor with one-click email sending
- Job history and search
- Company research caching

See [START_WEB_APP.md](START_WEB_APP.md) for detailed instructions.

### Option 2: CLI (Traditional)

**Python CLI for job outreach via terminal.**

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Set Up Environment

```bash
# Copy and edit .env
cp .env.example .env
# Edit .env with your API keys

# Or set environment variables
export OPENAI_API_KEY="your-key"
```

### 3. Gmail Setup (for email-agent)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `credentials.json` and place in this directory
5. Set OAuth consent screen to "External"
6. Add your email as test user

### 4. Test Agents

```bash
# Test extraction agent
cd extraction-agent
python tests/test_extraction.py

# Test email agent
cd email-agent
python -m email_agent.email_service

# Test research agent
cd research-agent
python -m research_agent.research_service

# Test content agent
cd content-agent
python -m content_agent.content_service

# Test LinkedIn agent
cd linkedin-agent
python -m linkedin_agent.linkedin_service

# Test job orchestrator
cd job-outreach-agent
python example_usage.py
```

## Web Application 🆕

The **web-app** provides a full-featured web interface for the job outreach system:

### Architecture
- **Flask** - Web framework
- **Celery + RabbitMQ** - Async task processing
- **PostgreSQL** - Job/draft persistence & company research cache
- **Redis** - Sessions and caching
- **Docker Compose** - One-command deployment

### Key Features
1. **Upload Interface**: Support for images, PDFs, text, URLs
2. **Async Processing**: Background workers handle extraction, research, content generation
3. **Real-time Status**: Live updates as job is processed
4. **Draft Editor**: Edit generated content before sending
5. **One-click Sending**: Send emails directly from the UI
6. **Job History**: Track all applications with status filters
7. **Company Cache**: Research data cached for 7 days

### Quick Start
```bash
# Configure and start
cp .env.docker .env
# Edit .env with your credentials
docker-compose up -d

# Access
open http://localhost:5000
```

See **[web-app/README.md](web-app/README.md)** for full documentation.

---

## Agent Services

### Extraction Agent

**Purpose**: Universal content extraction using AI

```python
from extraction_agent import ExtractionService

extractor = ExtractionService(api_key=api_key)

# Define what you want to extract
schema = {
    "company_name": "Company name",
    "role": "Job title",
    "email": "Contact email (or null)"
}

# Extract from any content type
result = extractor.extract(
    content="screenshot.png",
    content_type="image",
    schema=schema,
    instructions="Extract job information"
)
```

**Supported Content Types**: Images (GPT-4o Vision), Text, URLs, PDFs

**Use Cases**: Job posting extraction, resume parsing, document analysis, message extraction from screenshots, Notion page parsing, WhatsApp message extraction

### Email Agent

**Purpose**: Generic Gmail API email sending

```python
from email_agent import EmailService

email = EmailService(credentials_path="../credentials.json")
email.send(to="someone@company.com", subject="Hello", body="...")
```

**Use Cases**: Job outreach, marketing, notifications, automation

### Research Agent

**Purpose**: AI-powered web research and analysis

```python
from research_agent import ResearchService

research = ResearchService(api_key=api_key)
company_info = research.research_company("Anthropic")
topic_insights = research.research_topic("AI safety")
```

**Use Cases**: Company research, market analysis, competitive intelligence

### Content Agent

**Purpose**: AI content generation (emails, messages, posts)

```python
from content_agent import ContentService

content = ContentService(api_key=api_key)
email = content.generate_email(to_info={...}, context={...})
linkedin_msg = content.generate_linkedin_message(...)
```

**Use Cases**: Email writing, LinkedIn outreach, social media, cover letters

### LinkedIn Agent

**Purpose**: LinkedIn messaging (placeholder - provides manual guidance)

**Status**: Placeholder (LinkedIn has no public messaging API)

```python
from linkedin_agent import LinkedInService

linkedin = LinkedInService()
# Provides step-by-step manual instructions
linkedin.send_connection_request(url, message)
```

### Job Outreach Agent (Orchestrator)

**Purpose**: Intelligent job outreach using all 5 agents above

**Key Feature**: Intelligently recommends email vs LinkedIn based on context

```python
from job_outreach_agent import JobOrchestrator

orchestrator = JobOrchestrator(
    openai_api_key=api_key,
    gmail_credentials_path="../credentials.json",
    user_profile={...}
)

result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Software Engineer",
    "recruiter_email": "careers@anthropic.com",
    "requirements": "..."
})
```

**Output**: Intelligent recommendation with reasoning:
- Email available → "Use EMAIL (90% confidence)"
- LinkedIn only → "Use LINKEDIN (85% confidence) - here are manual instructions"
- Both available + senior role → "Use LINKEDIN (80% confidence) - senior roles respond better"

## Installation

All agents are already installed in the shared `venv/`. To reinstall:

```bash
source venv/bin/activate

# Install all agents
pip install -e extraction-agent
pip install -e email-agent
pip install -e research-agent
pip install -e content-agent
pip install -e linkedin-agent
pip install -e job-outreach-agent
```

## Dependencies

### Required
- Python 3.9+
- OpenAI API key (for research and content agents)
- Gmail credentials (for email agent)

### Installed
- `extraction-agent`: openai, requests, PyPDF2
- `email-agent`: google-api-python-client, google-auth, google-auth-oauthlib
- `research-agent`: openai, requests, beautifulsoup4
- `content-agent`: openai
- `linkedin-agent`: (no dependencies - placeholder)
- `job-outreach-agent`: python-dotenv + all 5 agents above

## Usage Examples

### Example 1: Email Outreach

```python
from job_outreach_agent import JobOrchestrator

orchestrator = JobOrchestrator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    gmail_credentials_path="../credentials.json",
    user_profile={
        "name": "Your Name",
        "email": "your@email.com",
        "highlights": ["Achievement 1", "Achievement 2"],
        "skills": ["Python", "AI/ML"]
    }
)

# Process job - will recommend email since email is available
result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Engineer",
    "recruiter_email": "careers@anthropic.com",
    "requirements": "Python, AI/ML"
})

# Send later
orchestrator.send_draft(result['draft_file'])
```

### Example 2: LinkedIn Outreach (Manual Guidance)

```python
# Process job - will recommend LinkedIn and provide instructions
result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Senior Engineer",
    "recruiter_linkedin": "linkedin.com/in/jane",
    "requirements": "Python, AI"
})

# Output:
# Channel: LINKEDIN
# Confidence: 85%
# Reason: Senior role - LinkedIn preferred
#
# Instructions:
#   1. Go to: linkedin.com/in/jane
#   2. Click 'Message'
#   3. Copy this message: [content]
#   ...
```

### Example 3: Using Individual Agents

```python
# Use research agent standalone
from research_agent import ResearchService
research = ResearchService(api_key=api_key)
company = research.research_company("OpenAI")

# Use content agent standalone
from content_agent import ContentService
content = ContentService(api_key=api_key)
email = content.generate_email(to_info={...}, context={...})

# Use email agent standalone
from email_agent import EmailService
email_service = EmailService(credentials_path="../credentials.json")
email_service.send(to="...", subject="...", body="...")
```

## Testing

### Test All Agents

```bash
source venv/bin/activate

# Extraction agent
cd extraction-agent && python tests/test_extraction.py && cd ..

# Email agent
cd email-agent && python tests/test_email.py && cd ..

# Research agent
cd research-agent && python tests/test_research.py && cd ..

# Content agent
cd content-agent && python tests/test_content.py && cd ..

# LinkedIn agent
cd linkedin-agent && python tests/test_linkedin.py && cd ..

# Job outreach agent
cd job-outreach-agent && python example_usage.py && cd ..
```

## Development

### Adding New Agent

1. Create new directory: `mkdir new-agent`
2. Create package structure:
   ```
   new-agent/
   ├── new_agent/
   │   ├── __init__.py
   │   └── service.py
   ├── tests/
   ├── README.md
   ├── .claude/README.md
   ├── setup.py
   └── requirements.txt
   ```
3. Install in venv: `pip install -e new-agent`
4. Add to documentation

### Modifying Existing Agent

1. Edit files in `{agent}-agent/`
2. Test changes: `python tests/test_{agent}.py`
3. Update documentation in `README.md` and `.claude/README.md`

## Monorepo Benefits

1. **Shared venv**: One virtual environment for all agents
2. **Shared credentials**: credentials.json and .env in root
3. **Easy development**: Edit and test agents together
4. **Consistent structure**: All agents follow same pattern
5. **Reusability**: Use agents independently or together

## Documentation

Each agent has:
- `README.md` - User documentation
- `.claude/README.md` - Claude Code context

## Support

For issues or questions:
- Check agent-specific README.md
- Review .claude/README.md for context
- See /Users/yash/Documents/COMPLETE_REFACTORING_SUMMARY.md

## Version

- extraction-agent: 1.0.0
- email-agent: 1.0.0
- research-agent: 1.0.0
- content-agent: 1.0.0
- linkedin-agent: 1.0.0 (placeholder)
- job-outreach-agent: 2.0.0

## License

MIT

## Author

Yash Mittal (with Claude Sonnet 4.5)

---

**This monorepo demonstrates modular AI agent architecture with intelligent orchestration.**
