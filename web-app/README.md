# Job Outreach Web Application

Web-based interface for the job outreach automation system. Provides async processing, database persistence, and a rich UI for managing job applications.

## Features

- **Upload Job Postings**: Support for images, PDFs, text, and URLs
- **Async Processing**: Celery workers handle extraction, research, and content generation
- **Database Persistence**: PostgreSQL stores jobs, drafts, and company research cache
- **Real-time Updates**: Status polling shows job processing progress
- **Draft Editor**: Edit and review generated content before sending
- **One-click Sending**: Send emails directly from the web UI
- **Job History**: Track all applications with status filters

## Architecture

```
Flask Web App (port 5000)
    ↓
RabbitMQ (message queue)
    ↓
Celery Workers (process jobs async)
    ↓
Existing Agents (extraction → research → content → email)
    ↓
PostgreSQL (store jobs, drafts, company cache)
Redis (sessions, cache, real-time status)
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Gmail credentials (`credentials.json` in root directory)

### Setup

1. **Copy environment file**:
   ```bash
   cd web-app
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```bash
   OPENAI_API_KEY=your-key-here
   USER_EMAIL=your.email@example.com
   USER_NAME=Your Name
   ```

3. **Start all services**:
   ```bash
   cd ..  # Back to repository root
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f web celery
   ```

5. **Access the application**:
   - Web UI: http://localhost:5000
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

### Database Migrations

Migrations run automatically on container startup. To manually manage migrations:

```bash
# Enter web container
docker-compose exec web bash

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

## Usage

### Upload Job Posting

1. Navigate to http://localhost:5000
2. Choose source type (image, text, or URL)
3. Upload/paste job posting content
4. Optionally add context notes
5. Click "Process Job Posting"

### Review and Send

1. Job is processed asynchronously (extraction → research → content generation)
2. View real-time status updates on job detail page
3. Once drafted, review and edit the generated content
4. Save changes if needed
5. Click "Send Email" to send via Gmail API

### Job List

- View all jobs with status filters (Drafted, Sent, Failed)
- Search by company name or role
- Click any job to view details

## Development

### Local Development (without Docker)

**Note**: For production, always use Docker. This is for development only.

1. **Activate venv**:
   ```bash
   source ../venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup services** (PostgreSQL, Redis, RabbitMQ):
   ```bash
   # Start only infrastructure services
   docker-compose up -d db redis rabbitmq
   ```

4. **Setup database**:
   ```bash
   export FLASK_APP=wsgi.py
   export DATABASE_URL=postgresql://joboutreach:password@localhost:5432/joboutreach
   flask db upgrade
   ```

5. **Run Flask app**:
   ```bash
   python wsgi.py
   ```

6. **Run Celery worker** (in another terminal):
   ```bash
   celery -A celery_app.celery_app worker --loglevel=info
   ```

### Project Structure

```
web-app/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # SQLAlchemy models
│   ├── tasks.py              # Celery tasks
│   ├── database.py           # DB setup
│   ├── routes/
│   │   ├── main.py          # Upload routes
│   │   ├── jobs.py          # Job list/detail
│   │   └── api.py           # API endpoints
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS/JS
├── migrations/              # Alembic migrations
├── config.py               # Flask configuration
├── celery_app.py          # Celery initialization
├── wsgi.py                # WSGI entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image
└── README.md            # This file
```

## API Endpoints

### Job Status
```
GET /api/jobs/<id>/status
```
Returns job processing status and details.

### Update Draft
```
POST /api/drafts/<id>/update
Content-Type: application/json

{
  "subject": "Updated subject",
  "body_text": "Updated body"
}
```

### Send Email
```
POST /api/drafts/<id>/send
```
Queues email for sending via Celery task.

### Preview Draft
```
GET /api/drafts/<id>/preview
```
Returns HTML preview of draft email.

## Database Schema

### Job
- Tracks job applications
- Stores extracted information (company, role, recruiter)
- Processing status and task ID

### Draft
- Email/message drafts
- Subject and body (HTML + text)
- Channel recommendation (email/LinkedIn)
- Edit history and send status

### CompanyResearch
- Cached company research data
- 7-day expiration
- Shared across multiple jobs for same company

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up -d
docker-compose logs
```

### Database issues
```bash
# Reset database
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```

### Celery tasks not processing
```bash
# Check Celery logs
docker-compose logs celery

# Check RabbitMQ
open http://localhost:15672
```

### Port already in use
```bash
# Change ports in docker-compose.yml
ports:
  - "5001:5000"  # Use port 5001 instead of 5000
```

## Production Deployment

For production deployment:

1. Use environment-specific `.env` file
2. Set strong `SECRET_KEY`
3. Use production PostgreSQL (not Docker)
4. Configure reverse proxy (nginx/Traefik)
5. Enable HTTPS
6. Set `FLASK_ENV=production`
7. Use multiple Celery workers
8. Setup monitoring (Sentry, Prometheus)

## Contributing

This is part of the job-outreach-agent monorepo. See main README.md for contribution guidelines.
