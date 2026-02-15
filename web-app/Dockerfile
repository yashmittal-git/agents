FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Build context is now the repository root, so specify web-app/
COPY web-app/requirements.txt .

# Install Python dependencies (excluding local agent packages for now)
RUN grep -v "^-e " requirements.txt > requirements-base.txt && \
    pip install --no-cache-dir -r requirements-base.txt

# Copy all agent packages
# Build context is repository root, so paths are relative to that
COPY extraction-agent /agents/extraction-agent
COPY email-agent /agents/email-agent
COPY research-agent /agents/research-agent
COPY content-agent /agents/content-agent
COPY linkedin-agent /agents/linkedin-agent
COPY job-outreach-agent /agents/job-outreach-agent

# Install all agents
RUN pip install -e /agents/extraction-agent && \
    pip install -e /agents/email-agent && \
    pip install -e /agents/research-agent && \
    pip install -e /agents/content-agent && \
    pip install -e /agents/linkedin-agent && \
    pip install -e /agents/job-outreach-agent

# Copy app code
COPY web-app/ .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Default command (can be overridden in docker-compose)
# Only run migrations if migrations folder exists, otherwise just start the app
CMD ["sh", "-c", "if [ -f migrations/env.py ]; then flask db upgrade; fi && gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - --log-level info wsgi:app"]
