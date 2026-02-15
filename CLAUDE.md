# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **monorepo** containing 6 modular AI agent services + web application for job outreach automation:

- **extraction-agent** - Universal content extraction using GPT-4o Vision (images, PDFs, URLs, text)
- **email-agent** - Gmail API email sending service
- **research-agent** - AI-powered web research and company analysis
- **content-agent** - AI content generation (emails, messages)
- **linkedin-agent** - LinkedIn messaging guidance (placeholder - no public API)
- **job-outreach-agent** - Orchestrator that intelligently coordinates all 5 agents above
- **web-app** - 🆕 Full-stack web application with async processing (Flask, Celery, PostgreSQL, Docker)

Each agent is an independent Python package that can be used standalone or together. The web app provides a UI for all agents.

## Purpose & Use Case

This system is built for **personal job search automation** to ease the process of reaching out to recruiters.

### Target User
- Currently a Tech Lead at Convin.ai
- Looking for new roles in Tech and Engineering
- Open to both IC (Individual Contributor) and Lead opportunities
- User profile data is stored in `job-outreach-agent/data/` (resume, portfolio content)

### Typical Workflow
1. **Input**: User provides job posting in any format:
   - Screenshot (LinkedIn post, WhatsApp message, email)
   - Text file with job description
   - URL to job posting
   - Any other content containing job info

2. **Optional Context**: After extraction, user can provide additional notes:
   - What specifically interests them about the role
   - Points they want emphasized (e.g., cost optimization, scalability)
   - Personal connections or custom instructions

3. **Processing**: System automatically:
   - Extracts job information (company, role, requirements, contact info)
   - Researches the company
   - Generates personalized outreach content (incorporating user's context)
   - Intelligently recommends communication channel (email/LinkedIn/WhatsApp)

4. **Human-in-the-loop**: System always:
   - Shows draft content for review
   - Asks for user confirmation before sending
   - Provides manual instructions for channels requiring manual action (LinkedIn, WhatsApp)

5. **Output**: Based on recommendation:
   - **Email**: Creates formatted email → user confirms → auto-sends via Gmail API (always BCCs user for record keeping)
   - **LinkedIn**: Generates message → provides step-by-step manual instructions
   - **WhatsApp**: Generates message → tells user to manually send

### Key Design Principle
**Semi-automated with human approval** - The system generates content and recommends actions, but the user always reviews and confirms before anything is sent. This maintains personal touch and prevents automated mistakes.

## Web Application

**Full-stack web UI** providing async job processing with database persistence. Accessible at http://localhost:5001 (port changed from 5000 to avoid macOS Control Center conflict).

**Key Features**:
- Upload interface for images, PDFs, text, URLs
- Async processing via Celery workers (background tasks)
- Real-time status updates (polls every 2 seconds)
- Draft editor with save functionality
- One-click email sending
- Job history with search and filters
- Company research caching (7-day TTL for cost optimization)

**Architecture**:
```
Flask (5001) → RabbitMQ → Celery Workers (4) → Agents → PostgreSQL + Redis
```

**Services** (managed by docker-compose.yml):
- **web**: Flask app (Gunicorn with 4 workers)
- **celery**: Celery workers (4 workers for async tasks)
- **celery-beat**: Celery scheduler (optional)
- **db**: PostgreSQL 15 (job/draft persistence, company cache)
- **redis**: Redis 7 (sessions, caching)
- **rabbitmq**: RabbitMQ 3 (message broker + management UI on port 15672)

**Starting the web app**:
```bash
docker-compose up -d                    # Start all services
docker-compose logs -f web celery       # View logs
docker-compose ps                       # Check status
docker-compose down -v                  # Stop and reset
```

**Database tables** (SQLAlchemy models in `web-app/app/models.py`):
- `job`: Tracks applications (source, extracted info, status, task_id, error_message)
- `draft`: Email/message drafts (channel, content, edit tracking, send status)
- `company_research`: Cached research data (expires after 7 days)

**Key implementation details**:
- Zero modifications to existing agents - web app imports them directly
- Tables created with `db.create_all()` (Flask-Migrate setup pending)
- DATABASE_URL uses `?sslmode=disable` for PostgreSQL Alpine compatibility
- Celery tasks in `web-app/app/tasks.py`: `process_job_task()`, `send_email_task()`
- Real-time updates via `/api/jobs/<id>/status` polling endpoint
- Dockerfile copies all agents during build and installs them in image

**Common operations**:
```bash
# Modify web app code
docker-compose build web celery
docker-compose restart web celery

# Recreate database tables
docker-compose exec web python -c "from app import create_app; from app.database import db; app=create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# View specific logs
docker-compose logs -f web
docker-compose logs -f celery
```

**Documentation**: See `web-app/.claude/README.md` for detailed web app context.

## Development Environment

### Virtual Environment - CRITICAL

**IMPORTANT: Always run ALL commands within the virtual environment. NEVER install packages or run Python globally.**

All agents share a single virtual environment at `venv/`. You MUST activate it before any work:

```bash
source venv/bin/activate
```

**Before running ANY Python command, pip command, or test:**
1. Ensure you're in the repository root: `/Users/yash/Documents/agents`
2. Activate venv: `source venv/bin/activate`
3. Verify activation: You should see `(venv)` in your prompt

**Why this matters:**
- All agent dependencies are installed in this shared venv
- Installing globally will cause version conflicts and missing dependencies
- Running tests outside venv will fail with import errors
- The monorepo architecture depends on the shared venv

### Environment Variables
- Configuration is in `.env` (gitignored)
- Template is in `.env.example`
- Required: `OPENAI_API_KEY` for AI services
- Gmail setup: Place `credentials.json` in root directory (see README.md Quick Start section 3)

### Package Installation
Agents are installed in editable mode in the shared venv. To reinstall after changes:

```bash
# ALWAYS activate venv first
source venv/bin/activate

# Then install packages
pip install -e extraction-agent
pip install -e email-agent
pip install -e research-agent
pip install -e content-agent
pip install -e linkedin-agent
pip install -e job-outreach-agent
```

## Running Tests

**ALWAYS activate venv before running tests:**

```bash
source venv/bin/activate
```

Each agent has its own test directory:

```bash
# Extraction agent
cd extraction-agent && python tests/test_extraction.py

# Email agent
cd email-agent && python tests/test_email.py

# Research agent
cd research-agent && python tests/test_research.py

# Content agent
cd content-agent && python tests/test_content.py

# LinkedIn agent
cd linkedin-agent && python tests/test_linkedin.py

# Job outreach orchestrator
cd job-outreach-agent && python example_usage.py
```

**Note:** All tests assume venv is activated. They will fail with import errors otherwise.

## Job Outreach Usage

There are **two ways** to use the job outreach system:

### Option 1: Web Application (Recommended)
Use the web UI at http://localhost:5001 (see "Web Application" section above). Provides async processing, job history, and better UX.

### Option 2: CLI
The CLI (`job-outreach-agent/job_outreach_cli.py`) processes jobs synchronously and saves drafts as JSON files. It can process screenshots, text files, or URLs:

```bash
# Activate venv first
source venv/bin/activate

# Then run CLI
cd job-outreach-agent
python job_outreach_cli.py <screenshot.png>
python job_outreach_cli.py <job_posting.txt>
python job_outreach_cli.py <url>
```

This CLI:
1. Uses **extraction-agent** to extract job info
2. Orchestrates research, content generation, and sending
3. Intelligently recommends email vs LinkedIn based on available contact info

## Architecture Patterns

### Service Independence
Each agent is a standalone service with:
- `{agent_name}/{agent_name}/` - Python package
- `{agent_name}/tests/` - Tests
- `{agent_name}/setup.py` - Package definition
- `{agent_name}/requirements.txt` - Dependencies
- `{agent_name}/README.md` - User documentation
- `{agent_name}/.claude/README.md` - Claude context

### Orchestrator Pattern
**job-outreach-agent** demonstrates orchestration:
- Does NOT implement extraction, research, content generation, or email sending itself
- Delegates to specialized agents via their public APIs
- Adds intelligence layer: channel selection (email vs LinkedIn), workflow coordination
- Located in `job-outreach-agent/job_outreach_agent/job_orchestrator.py`

Key method: `JobOrchestrator.process_job()` which:
1. Researches company (delegates to research-agent)
2. Generates personalized content (delegates to content-agent)
3. Recommends channel (email/LinkedIn) with confidence score
4. Sends or provides manual instructions

### Extraction Service
The extraction-agent uses GPT-4o Vision to extract structured data from any content type:
- Images: Screenshots, photos
- PDFs: Documents with text/images
- URLs: Web scraping + AI extraction
- Text: Direct text processing

Key method: `ExtractionService.extract(content, content_type, schema, instructions)`
- `schema` defines desired output fields as dict
- Returns structured JSON matching the schema

### Monorepo Benefits
- Shared virtual environment and credentials
- Consistent package structure across all agents
- Easy inter-agent integration
- Individual agents remain independently usable

## Common Workflows

### Testing a single agent
```bash
# Activate venv first (always!)
source venv/bin/activate

# Then run tests
cd {agent-name}
python -m {agent_name}.{service_name}  # Direct module execution
# or
python tests/test_{agent}.py
```

### Using agents programmatically
```python
# Individual agent usage
from extraction_agent import ExtractionService
from research_agent import ResearchService
from content_agent import ContentService
from email_agent import EmailService

# Orchestrator usage
from job_outreach_agent import JobOrchestrator
```

### Adding a new agent
1. Activate venv: `source venv/bin/activate`
2. Create directory: `mkdir new-agent`
3. Follow the standard package structure (see Architecture Patterns above)
4. Install in venv: `pip install -e new-agent`
5. Update monorepo README.md

## Important File Locations

- Shared credentials: `credentials.json`, `token.json` (root directory)
- Environment config: `.env` (root directory)
- Draft outputs (CLI): `job-outreach-agent/outreach_drafts/`
- Draft outputs (web): Database (PostgreSQL) + `uploads/` directory
- Example usage: `job-outreach-agent/example_usage.py`
- Web app: `web-app/` directory (separate Flask application)
- Docker config: `docker-compose.yml` (root directory)

## Documentation Maintenance

### When to Update Documentation

Each agent and the web app have their own documentation:
- **CLAUDE.md** / **.claude/README.md**: For future Claude instances (architecture, development workflows, critical context)
- **README.md**: For human users (API reference, usage examples, setup instructions)

**When making changes, always consider:**
1. Does this affect user-facing behavior? → Update relevant README.md files
2. Does this change architecture/workflows? → Update relevant CLAUDE.md files
3. Does this impact multiple agents? → Update both root and agent-specific docs

**Which files to update:**
- Root-level changes → Update `/CLAUDE.md` and/or `/README.md`
- Agent-specific changes → Update `{agent}/.claude/README.md` and/or `{agent}/README.md`
- Web app changes → Update `web-app/.claude/README.md` and/or `web-app/README.md`
- Cross-cutting features → Update root + affected agents/web-app

### Documentation Quality Standards

**CRITICAL: Never bloat documentation files**
- Keep content concise and focused
- Remove outdated or redundant information when updating
- Avoid repeating what's obvious from code or file structure
- Don't document every minor detail - focus on what future Claude/users need to know
- Examples: Good if they clarify complex concepts; bloat if they repeat obvious patterns

**When editing docs:**
1. Add only relevant, non-obvious information
2. Remove any outdated sections you encounter
3. Consolidate redundant information
4. Ask: "Does a future Claude/user actually need this to be effective?"
5. If unsure whether to document something, err on the side of less documentation

**Documentation anti-patterns to avoid:**
- ❌ Listing every file in the project (use tree structure sparingly)
- ❌ Documenting standard Python patterns everyone knows
- ❌ Repeating what's in code docstrings
- ❌ Adding "just in case" sections that aren't actually needed
- ❌ Creating documentation that duplicates README.md in CLAUDE.md or vice versa

**Good documentation:**
- ✅ Architecture decisions and patterns
- ✅ Non-obvious workflows and dependencies
- ✅ Critical context that impacts multiple files
- ✅ Common pitfalls and their solutions
- ✅ Integration points between services
