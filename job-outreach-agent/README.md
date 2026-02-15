# Job Outreach Agent v2.0

**Intelligent job outreach orchestrator** that uses 5 external agent services for personalized job applications.

## Architecture

This is an **orchestrator** that delegates to:

1. **extraction-agent**: Universal content extraction (AI-powered)
2. **email-agent**: Gmail API email sending
3. **research-agent**: Company research and analysis
4. **content-agent**: AI-powered content generation
5. **linkedin-agent**: LinkedIn messaging guidance

## Features

- Intelligent channel recommendation (email vs LinkedIn)
- Company research and analysis
- Experience matching
- Personalized content generation
- Gmail API integration for email
- Manual guidance for LinkedIn
- Draft management
- Auto-send support (for email)

## Installation

```bash
# Install all dependencies (including 5 agents)
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Setup

### 1. Environment Variables

```bash
export OPENAI_API_KEY="your-key"
```

### 2. Gmail Credentials (for email outreach)

Place `credentials.json` in your working directory.

## Usage

### Quick Start (Recommended)

The easiest way to use the agent is via the CLI:

```bash
# With a screenshot (LinkedIn, WhatsApp, email, etc.)
python job_outreach_cli.py /path/to/job_screenshot.png

# With a text file
python job_outreach_cli.py /path/to/job_posting.txt
```

The CLI will:
1. ✅ Extract job info using extraction-agent (GPT-4o Vision for images)
2. ✅ Research the company
3. ✅ Match with your profile
4. ✅ Intelligently recommend email vs LinkedIn
5. ✅ Generate personalized content
6. ✅ Show you the draft
7. ✅ Ask for your approval
8. ✅ Send email (or provide LinkedIn instructions)

**Supported Input Formats**:
- `.png`, `.jpg`, `.jpeg` - Screenshots from any source
- `.txt` - Text files with job descriptions

See [QUICK_START.md](QUICK_START.md) for detailed walkthrough.

### Programmatic Usage

```python
from job_outreach_agent import JobOrchestrator

# Initialize
orchestrator = JobOrchestrator(
    openai_api_key="your-key",
    gmail_credentials_path="credentials.json",
    user_profile={
        "name": "Your Name",
        "email": "your@email.com",
        "highlights": ["Achievement 1", "Achievement 2"],
        "skills": ["Python", "AI/ML"]
    }
)

# Process job application
result = orchestrator.process_job(
    job_info={
        "company_name": "Anthropic",
        "role": "Software Engineer",
        "recruiter_email": "recruiter@anthropic.com",  # Optional
        "recruiter_linkedin": "linkedin.com/in/recruiter",  # Optional
        "requirements": "Python, AI/ML, distributed systems"
    },
    auto_send=False  # Set True to auto-send if email
)

# Draft saved to outreach_drafts/
print(f"Draft: {result['draft_file']}")

# Send draft later
orchestrator.send_draft(result['draft_file'])
```

### Channel Recommendation

The orchestrator intelligently recommends:

- **Email** if direct email available (90% confidence)
- **LinkedIn** if no email but LinkedIn available (85% confidence)
- **LinkedIn** for senior roles or startups, even if email available (80-85% confidence)

### Email Outreach (Auto-sendable)

```python
result = orchestrator.process_job(
    job_info={
        "company_name": "Anthropic",
        "role": "Engineer",
        "recruiter_email": "jane@anthropic.com",
        "requirements": "..."
    }
)

# Review draft
# Then send:
orchestrator.send_draft(result['draft_file'])
```

Output:
```
==============================================
OUTREACH STRATEGY
==============================================

Channel: EMAIL
Confidence: 90%
Reason: Direct email address available

✓ This channel supports automatic sending

Subject: Application for Engineer at Anthropic

Body:
----------------------------------------------
[Personalized email content]
----------------------------------------------
```

### LinkedIn Outreach (Manual Guidance)

```python
result = orchestrator.process_job(
    job_info={
        "company_name": "Anthropic",
        "role": "Engineer",
        "recruiter_linkedin": "linkedin.com/in/jane",
        "requirements": "..."
    }
)
```

Output:
```
========================================
OUTREACH STRATEGY
==============================================

Channel: LINKEDIN
Confidence: 85%
Reason: LinkedIn available, no email found

⚠ This channel requires manual action

Follow these steps:
  1. Open LinkedIn and go to: linkedin.com/in/jane
  2. Click the 'Connect' or 'Message' button
  3. If connecting, click 'Add a note'
  4. Copy and paste the message below:
  5. Review and personalize if needed
  6. Click 'Send'!

==============================================
MESSAGE TO SEND:
==============================================
Hi Jane,

I came across the Engineer role at Anthropic...
[Personalized LinkedIn message]
==============================================

Tips:
  • LinkedIn messages work best 9-11 AM on weekdays
  • Connection notes are limited to 300 characters
  • Follow up after 3-5 days if no response
```

## How It Works

### Flow

```
1. Extract job info (via extraction-agent) - from screenshots, text, URLs, PDFs
2. Research company (via research-agent)
3. Match experience
4. Recommend channel (email vs LinkedIn)
5. Generate content (via content-agent)
6. Execute:
   - Email: Send via email-agent
   - LinkedIn: Provide manual instructions via linkedin-agent
7. Save draft
8. Display strategy
```

### Content Extraction

The orchestrator uses **extraction-agent** to extract job information from:
- Screenshots (LinkedIn, WhatsApp, email)
- Text files (job descriptions)
- URLs (career pages)
- PDFs (job postings)

This makes it flexible to accept job information in any format.

### Intelligent Decision Making

**Channel Recommendation Logic**:
- Email available → Email (90%)
- LinkedIn only → LinkedIn (85%)
- Both + senior role → LinkedIn (80%)
- Both + startup → LinkedIn (85%)
- Both + regular → Email (85%)

## API Reference

### JobOrchestrator

```python
JobOrchestrator(
    openai_api_key: str,
    gmail_credentials_path: str = "credentials.json",
    user_profile: Optional[Dict] = None
)
```

#### Methods

**`process_job(job_info, auto_send=False) -> Dict`**

Process job application with intelligent channel recommendation.

**Parameters:**
- `job_info`: Job details
- `auto_send`: Auto-send if channel supports it

**Returns:**
```python
{
    "draft_file": "outreach_drafts/20260215_120000_Company.json",
    "strategy": {...},
    "sent": bool
}
```

**`send_draft(draft_file) -> bool`**

Send a saved draft.

## Draft Format

```json
{
  "generated_at": "2026-02-15T12:00:00",
  "job_info": {...},
  "company_research": {...},
  "experience_match": {...},
  "channel_recommendation": {
    "primary_channel": "email",
    "confidence": 0.90,
    "reason": "...",
    "alternatives": [...]
  },
  "strategy": {
    "channel": "email",
    "content": {...},
    "can_auto_send": true,
    "instructions": null
  },
  "status": "draft"
}
```

## Dependencies

- **extraction-agent**: Universal content extraction
- **email-agent**: Email sending
- **research-agent**: Company research
- **content-agent**: Content generation
- **linkedin-agent**: LinkedIn guidance
- **python-dotenv**: Environment variables

## Testing

```bash
# Test the orchestrator
python -m job_outreach_agent.job_orchestrator
```

## Version

2.0.0 - Modular architecture with external agents

## Author

Yash Mittal

## License

MIT
