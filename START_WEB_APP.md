# Starting the Job Outreach Web Application

This guide will help you start the web application for the first time.

## Prerequisites

### 1. Install Docker Desktop

**macOS**:
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### 2. Prepare Credentials

Ensure you have:
- `credentials.json` in the root directory (Gmail API credentials)
- OpenAI API key ready
- Your email and name for sending emails

## Setup Steps

### Step 1: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.docker .env

# Edit .env with your actual values
nano .env  # or use any text editor
```

Update these values in `.env`:
```bash
OPENAI_API_KEY=sk-...your-actual-key...
USER_EMAIL=your.actual.email@example.com
USER_NAME=Your Full Name
```

### Step 2: Verify Gmail Credentials

Ensure `credentials.json` exists in the repository root:
```bash
ls -la credentials.json
```

If not present, follow the Gmail API setup in the main README.md.

### Step 3: Start All Services

```bash
# From repository root directory
docker-compose up -d
```

This will:
- Pull Docker images (PostgreSQL, Redis, RabbitMQ)
- Build the Flask app image
- Start all services
- Run database migrations automatically

### Step 4: Monitor Startup

Watch the logs to ensure everything starts correctly:
```bash
docker-compose logs -f
```

Wait for these messages:
- `web_1` - "Booting worker with pid..."
- `celery_1` - "celery@... ready"
- `db_1` - "database system is ready to accept connections"

Press `Ctrl+C` to stop following logs (services keep running).

### Step 5: Verify Services

Check that all services are running:
```bash
docker-compose ps
```

You should see:
- `web` - Up and running on port 5000
- `celery` - Up and running
- `db` - Up and running on port 5432
- `redis` - Up and running on port 6379
- `rabbitmq` - Up and running on ports 5672, 15672

### Step 6: Access the Application

Open your browser and navigate to:
- **Web UI**: http://localhost:5000
- **RabbitMQ Management**: http://localhost:15672 (username: guest, password: guest)

## Usage

### Upload a Job Posting

1. Go to http://localhost:5000
2. Select source type:
   - **Image/PDF**: Upload a screenshot or document
   - **Text**: Paste job posting text directly
   - **URL**: Provide a link to job posting
3. Optionally add context notes (what interests you about the role)
4. Click "Process Job Posting"

### Monitor Processing

After upload, you'll be redirected to the job detail page where you can:
- See real-time status updates (extracting → researching → generating → drafted)
- Watch as the system processes your job posting

### Review and Send

Once status shows "Ready to Send":
1. Review the generated email draft
2. Edit subject or body if needed
3. Click "Save Changes" if you made edits
4. Click "Send Email" to send via Gmail
5. Confirm the action

The email will be sent to the recruiter and BCC'd to you for records.

### View All Jobs

Click "Jobs" in the navigation to see:
- All job applications
- Filter by status (Drafted, Sent, Failed)
- Search by company or role

## Stopping the Application

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop, remove containers AND delete all data (reset)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use (5000)

If port 5000 is already in use:

1. Edit `docker-compose.yml`
2. Change web service ports:
   ```yaml
   web:
     ports:
       - "5001:5000"  # Use 5001 instead
   ```
3. Restart: `docker-compose up -d`
4. Access at http://localhost:5001

### Cannot Connect to Database

```bash
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Celery Not Processing Tasks

```bash
# Check Celery logs
docker-compose logs celery

# Restart Celery worker
docker-compose restart celery

# Check RabbitMQ
open http://localhost:15672
```

### "No module named 'extraction_agent'"

The agents need to be installed. Rebuild the containers:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reset Everything

If something goes wrong and you want to start fresh:
```bash
# WARNING: This deletes all data (jobs, drafts, etc.)
docker-compose down -v
docker-compose up -d
```

## Development Mode

To make code changes and see them immediately without rebuilding:

1. Edit `docker-compose.yml` to mount web-app code:
   ```yaml
   web:
     volumes:
       - ./web-app:/app  # Add this line
       # ... other volumes
   ```

2. Restart:
   ```bash
   docker-compose restart web celery
   ```

## Next Steps

- Explore the web UI
- Upload a test job posting
- Review the generated content
- Check the job history
- Try editing drafts
- Send a test email

## Support

For issues or questions:
- Check `web-app/README.md` for detailed documentation
- View logs: `docker-compose logs`
- Check main repository README.md
- Review agent-specific documentation in each agent's directory
