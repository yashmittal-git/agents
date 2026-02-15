#!/bin/bash
# Job Outreach Web App Startup Script

set -e

echo "=========================================="
echo "Job Outreach Web App Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo ""
    echo "Please install Docker Desktop:"
    echo "1. Go to: https://www.docker.com/products/docker-desktop/"
    echo "2. Download and install Docker Desktop for Mac"
    echo "3. Start Docker Desktop"
    echo "4. Run this script again"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is installed and running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please copy .env.docker to .env and configure it:"
    echo "  cp .env.docker .env"
    echo "  nano .env  # Add your credentials"
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Check if credentials.json exists
if [ ! -f credentials.json ]; then
    echo "⚠️  Warning: credentials.json not found!"
    echo "   Email sending will not work without Gmail credentials."
    echo ""
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Web App Started!"
echo "=========================================="
echo ""
echo "Access URLs:"
echo "  • Web UI: http://localhost:5001"
echo "  • RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""
echo "Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop: docker-compose stop"
echo "  • Restart: docker-compose restart"
echo ""
echo "Opening web browser..."
sleep 2
open http://localhost:5001 2>/dev/null || echo "Please open http://localhost:5001 in your browser"
