#!/bin/bash
# Start full stack with Celery workers for production

echo "🚀 Starting Synthesize.io Full Stack..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Starting all services with Celery workers..."
docker-compose --profile full up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Services Status:"
docker-compose ps

echo ""
echo "📊 Service URLs:"
echo "  - Web App:       http://localhost:3000"
echo "  - Admin Portal:  http://localhost:3001"
echo "  - API:           http://localhost:8000"
echo "  - API Docs:      http://localhost:8000/docs"
echo "  - Flower:        http://localhost:5555 (Celery monitoring)"
echo "  - pgAdmin:       http://localhost:5050 (DB management)"
echo "  - PostgreSQL:    localhost:5432"
echo "  - Redis:         localhost:6379"
echo ""

echo "🔍 Check Celery Workers:"
echo "  docker logs -f synthesize-celery-worker"
echo ""Services:"
echo "  - Celery tasks/workers: http://localhost:5555 (Flower)"
echo "  - Database queries:     http://localhost:5050 (pgAdmin)
echo "  pip install flower"
echo "  celery -A app.celery_app flower --port=5555"
echo ""

echo "🛑 To stop all services:"
echo "  docker-compose --profile full down"
echo ""
