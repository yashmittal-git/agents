# Job Outreach Agent v2.0 - Context for Claude Code

## Project Overview

**Job Outreach Agent v2.0** is an orchestrator service that uses 5 external agent services for intelligent job application outreach.

## Architecture

### Orchestrator Pattern

This agent **does NOT implement** core functionality. Instead, it **orchestrates** 5 external agents:

1. **extraction-agent** (`/agents/extraction-agent/`) - Universal content extraction (AI-powered)
2. **email-agent** (`/agents/email-agent/`) - Email sending via Gmail API
3. **research-agent** (`/agents/research-agent/`) - Company research
4. **content-agent** (`/agents/content-agent/`) - Content generation
5. **linkedin-agent** (`/agents/linkedin-agent/`) - LinkedIn guidance

### Responsibilities

**What this agent DOES**:
- Orchestrates the 5 external agents
- Matches candidate experience with requirements
- Recommends best outreach channel (email vs LinkedIn)
- Manages draft workflow
- Provides intelligent guidance

**What this agent does NOT do** (delegates to agents):
- ❌ Content extraction → extraction-agent
- ❌ Email sending → email-agent
- ❌ Company research → research-agent
- ❌ Content generation → content-agent
- ❌ LinkedIn messaging → linkedin-agent

## Key Components

### JobOrchestrator Class

Main orchestrator in `job_orchestrator.py`:

```python
class JobOrchestrator:
    def __init__(openai_api_key, gmail_credentials_path, user_profile)
    def process_job(job_info, auto_send=False) -> Dict
    def send_draft(draft_file) -> bool

    # Private methods
    def _match_experience(...)
    def _recommend_channel(...)  # Intelligent channel recommendation
    def _create_strategy(...)
    def _execute_strategy(...)
    def _display_strategy(...)
    def _save_draft(...)
```

### Channel Recommendation Logic

**Key feature**: Intelligently recommends email vs LinkedIn

```python
def _recommend_channel(job_info, company_research):
    has_email = bool(job_info.get('recruiter_email'))
    has_linkedin = bool(job_info.get('recruiter_linkedin'))
    is_senior = 'senior' in role or 'lead' in role
    is_startup = stage in ['startup', 'growth']

    # Logic:
    if has_email and not has_linkedin:
        return "email", 0.90, "Direct email available"

    if has_linkedin and not has_email:
        return "linkedin", 0.85, "LinkedIn available, no email"

    if has_both and (is_senior or is_startup):
        return "linkedin", 0.80-0.85, "Senior role/startup prefer LinkedIn"

    return "email", 0.85, "Professional email preferred"
```

## Usage Patterns

### Pattern 1: Email Outreach (Auto-send)

```python
orchestrator = JobOrchestrator(api_key, gmail_creds, profile)

result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Engineer",
    "recruiter_email": "jane@anthropic.com",
    "requirements": "..."
})

# Recommends: Email (90% confidence)
# Creates: Email content via content-agent
# Action: Can auto-send via email-agent

orchestrator.send_draft(result['draft_file'])
```

### Pattern 2: LinkedIn Outreach (Manual)

```python
result = orchestrator.process_job({
    "company_name": "Anthropic",
    "role": "Senior Engineer",  # Senior role
    "recruiter_linkedin": "linkedin.com/in/jane",
    "requirements": "..."
})

# Recommends: LinkedIn (85% confidence)
# Creates: LinkedIn message via content-agent
# Action: Provides manual instructions via linkedin-agent
```

## External Agent Usage

### Email Agent

```python
from email_agent import EmailService

self.email_agent = EmailService(
    credentials_path=gmail_credentials_path,
    sender_email=user_profile['email']
)

# Send email
success = self.email_agent.send(
    to=recruiter_email,
    subject=content['subject'],
    body=content['body']
)
```

### Research Agent

```python
from research_agent import ResearchService

self.research_agent = ResearchService(api_key=openai_api_key)

# Research company
company_info = self.research_agent.research_company(
    company_name="Anthropic",
    context="for job application as Software Engineer"
)
# Returns: {what_they_build, tech_stack, stage, relevant_context}
```

### Content Agent

```python
from content_agent import ContentService

self.content_agent = ContentService(api_key=openai_api_key)

# Generate email
email = self.content_agent.generate_email(
    to_info={"name": "Jane", "company": "Anthropic"},
    context={"purpose": "job application", ...},
    sender_info=user_profile
)

# Generate LinkedIn message
message = self.content_agent.generate_linkedin_message(
    to_info={...},
    context={...},
    max_chars=300
)
```

### LinkedIn Agent

```python
from linkedin_agent import LinkedInService

self.linkedin_agent = LinkedInService()

# Get manual instructions (placeholder implementation)
result = self.linkedin_agent.send_connection_request(
    profile_url="linkedin.com/in/jane",
    message=linkedin_message
)
# Returns: {"status": "manual_action_required", "instructions": "..."}
```

## Guidelines for Claude Code

### When Working on This Agent

1. **Orchestration Only**: Don't implement extraction/email/research/content logic here
2. **Use External Agents**: Always delegate to the 5 agents
3. **Smart Recommendations**: Focus on intelligent channel recommendation
4. **Draft Management**: Handle draft save/load/send workflow
5. **User Guidance**: Provide clear instructions for manual actions

### DON'Ts

- ❌ Don't implement content extraction (use extraction-agent)
- ❌ Don't implement email sending (use email-agent)
- ❌ Don't implement web scraping (use research-agent)
- ❌ Don't implement content generation (use content-agent)
- ❌ Don't implement LinkedIn automation (use linkedin-agent for guidance)
- ❌ Don't duplicate logic that exists in external agents

### DOs

- ✅ Orchestrate the 5 external agents
- ✅ Make intelligent channel recommendations
- ✅ Manage draft workflow
- ✅ Provide clear user guidance
- ✅ Handle errors from external agents gracefully

## Extension Points

### Adding New Channels

To add a new channel (e.g., WhatsApp):

1. Create `whatsapp-agent` in `/agents/whatsapp-agent/`
2. Import in orchestrator: `from whatsapp_agent import WhatsAppService`
3. Add to `_recommend_channel()` logic
4. Add to `_create_strategy()` for content generation
5. Add to `_execute_strategy()` for sending

### Improving Recommendations

Enhance `_recommend_channel()`:

```python
# Add more factors
is_technical_role = 'engineer' in role or 'developer' in role
company_culture = research.get('culture', '')
recruiter_activity = check_linkedin_activity()

# More sophisticated logic
if is_technical_role and has_github:
    return "github", 0.90, "Technical role - GitHub preferred"
```

### Adding Experience Matching

Currently placeholder. To implement:

```python
def _match_experience(job_info, company_research):
    # Load user resume from data/
    resume = load_resume()

    # Use AI to match (could use content-agent or separate matching logic)
    match = analyze_match(resume, job_requirements)

    return {
        "relevant_experience": [...],
        "matching_skills": [...],
        "relevance_score": 9
    }
```

## File Structure

```
job-outreach-agent/
├── .claude/
│   └── README.md            # This file
├── job_outreach_agent/
│   ├── __init__.py
│   └── job_orchestrator.py  # Main orchestrator
├── data/                    # User data (resume, portfolio)
│   ├── Yash_Mittal_Resume.pdf
│   ├── resume_content.txt
│   └── portfolio_content.txt
├── outreach_drafts/         # Generated drafts (created automatically)
├── tests/                   # Future: Tests
├── job_outreach_cli.py      # CLI interface
├── QUICK_START.md           # Quick start guide
├── README.md
├── requirements.txt
└── setup.py
```

## Development Workflow

1. **Make changes** to job_orchestrator.py
2. **Test locally**: Create test script
3. **Verify external agents** are installed
4. **Test integration** with real job data
5. **Update documentation**

## Integration with Other Agents

### Dependencies

- extraction-agent (required)
- email-agent (required)
- research-agent (required)
- content-agent (required)
- linkedin-agent (required)

### Used By

- User projects
- Other orchestrators
- Automation tools

## Key Differences from v1.0

| Aspect | v1.0 (Old) | v2.0 (New) |
|--------|------------|------------|
| Architecture | Monolithic | Modular orchestrator |
| Extraction | Implemented internally | Delegates to extraction-agent |
| Email | Implemented internally | Delegates to email-agent |
| Research | Implemented internally | Delegates to research-agent |
| Content | Implemented internally | Delegates to content-agent |
| Channel | Email only | Email + LinkedIn with smart recommendation |
| Input Formats | Limited | Any (images, text, URLs, PDFs) via extraction-agent |
| Reusability | Low (job-specific) | High (agents reusable) |

## Version History

- **2.0.0**: Modular architecture with external agents, intelligent channel recommendation

---

**This agent demonstrates the power of orchestration - combining specialized services to create intelligent workflows.**
