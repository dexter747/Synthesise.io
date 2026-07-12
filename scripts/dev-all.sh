#!/bin/bash
# Start all services for development

set -e

echo "🚀 Starting Synthesize.io Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Starting Docker services (postgres, redis, celery workers, flower, pgadmin)..."
docker-compose --profile full up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 8

echo ""
echo "✅ Docker Services Status:"
docker-compose ps

echo ""
echo "📊 Service URLs:"
echo "  - PostgreSQL:    localhost:5432"
echo "  - Redis:         localhost:6379"
echo "  - Flower:        http://localhost:5555 (Celery monitoring)"
echo "  - pgAdmin:       http://localhost:5050 (DB management)"
echo ""
echo "  Frontend services will start next..."
echo "  - Web App:       http://localhost:3000"
echo "  - Admin Portal:  http://localhost:3001"
echo "  - API:           http://localhost:8000"
echo "  - API Docs:      http://localhost:8000/docs"
echo ""

echo "🔍 To view logs:"
echo "  docker-compose logs -f"
echo ""

echo "✅ Docker services ready! Backend API and frontend will start in development mode..."
echo ""
