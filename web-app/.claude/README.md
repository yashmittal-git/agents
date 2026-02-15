# Web App - Claude Context

Full-stack web application for job outreach automation with async processing.

## Architecture

```
Flask Web App (port 5001)
    ↓
RabbitMQ (message broker)
    ↓
Celery Workers (4 workers)
    ↓
Existing Agents (extraction → research → content → email)
    ↓
PostgreSQL + Redis
```

## Key Components

### Models (app/models.py)
- **Job**: Tracks applications (source, extracted info, status, relationships)
- **Draft**: Email/message drafts (channel, content, edit tracking, send status)
- **CompanyResearch**: Cached research data (7-day TTL)

### Tasks (app/tasks.py)
**Celery async tasks:**
- `process_job_task(job_id)`: Extract → Research → Generate → Save draft
- `send_email_task(draft_id)`: Send via email-agent with BCC to user

### Routes
- **main.py**: Upload interface (/, /upload)
- **jobs.py**: Job list and detail pages (/jobs, /jobs/<id>)
- **api.py**: JSON endpoints for AJAX (/api/jobs/<id>/status, /api/drafts/<id>/update|send)

### Templates
- **base.html**: Layout with Tailwind CSS + Alpine.js
- **index.html**: Upload form (image/text/URL + context)
- **jobs.html**: List with filters and search
- **job_detail.html**: Draft editor with real-time polling

## Database Setup

**Current approach**: Using `db.create_all()` (tables created manually)

**TODO**: Set up Flask-Migrate properly:
```bash
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

Then update Dockerfile CMD to run migrations on startup.

## Development Workflow

### Local changes
1. Edit files in `web-app/`
2. Rebuild: `docker-compose build web celery`
3. Restart: `docker-compose up -d`

### Database changes
1. Modify models in `app/models.py`
2. Recreate tables: `docker-compose exec web python -c "from app import create_app; from app.database import db; app=create_app(); app.app_context().push(); db.drop_all(); db.create_all()"`

### View logs
```bash
docker-compose logs -f web celery
```

## Integration with Agents

**Zero modifications to agents** - web app imports them directly:
```python
from extraction_agent import ExtractionService
from research_agent import ResearchService
from content_agent import ContentService
from email_agent import EmailService
```

All agents work via their existing APIs.

## Configuration

### Environment Variables (docker-compose.yml)
- `DATABASE_URL`: PostgreSQL connection (with `?sslmode=disable`)
- `REDIS_URL`: Redis connection
- `CELERY_BROKER_URL`: RabbitMQ connection
- `OPENAI_API_KEY`: For AI services
- `USER_EMAIL`, `USER_NAME`: For email sending

### Volumes Mounted
- `./uploads`: Uploaded job postings
- `./credentials.json`: Gmail OAuth (read-only)
- `./token.json`: Gmail OAuth token

## Common Issues

### Port 5000 conflict
macOS Control Center uses port 5000. Changed to 5001 in docker-compose.yml.

### Database SSL issues
PostgreSQL Alpine image rejects connections without SSL config.
Fixed by adding `?sslmode=disable` to DATABASE_URL and updating pg_hba.conf.

### Agent imports failing
Dockerfile copies agents during build:
```dockerfile
COPY extraction-agent /agents/extraction-agent
RUN pip install -e /agents/extraction-agent
```

### Migrations not found
Migrations folder doesn't persist in container. Need to either:
- Mount `./migrations` as volume, or
- Initialize migrations in entrypoint script, or
- Use `db.create_all()` approach (current)

## File Structure

```
web-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── tasks.py             # Celery tasks
│   ├── database.py          # DB setup
│   ├── routes/              # Blueprints
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS/JS
├── config.py                # Flask config
├── celery_app.py           # Celery initialization
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Python deps
├── Dockerfile              # Docker image
└── .claude/README.md       # This file
```

## Testing Workflow

1. Upload job posting at http://localhost:5001
2. Watch real-time status updates (polling `/api/jobs/<id>/status`)
3. Review generated draft
4. Edit if needed (saves via `/api/drafts/<id>/update`)
5. Send email (triggers `send_email_task`)

## Next Steps (Future Improvements)

- Proper Flask-Migrate setup with automatic migrations
- User authentication and multi-user support
- Email templates library
- Analytics dashboard
- Batch upload support
- Webhook notifications (Slack/Discord)
