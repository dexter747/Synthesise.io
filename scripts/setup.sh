#!/bin/bash

# Synthesize.io Development Setup Script

set -e

echo "🚀 Setting up Synthesize.io development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20.x or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version must be 20 or higher. Current: $(node -v)"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm@9.15.2
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION < 3.11" | bc)" -eq 1 ]; then
    echo "❌ Python version must be 3.11 or higher. Current: $(python3 --version)"
    exit 1
fi

echo "✅ All prerequisites are installed"

# Copy environment files
echo "📝 Setting up environment files..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please update .env with your API keys before running the app"
fi

if [ ! -f apps/web/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > apps/web/.env.local
    echo "NEXT_PUBLIC_APP_URL=http://localhost:3000" >> apps/web/.env.local
    echo "✅ Created apps/web/.env.local"
fi

if [ ! -f apps/admin/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > apps/admin/.env.local
    echo "NEXT_PUBLIC_APP_URL=http://localhost:3001" >> apps/admin/.env.local
    echo "✅ Created apps/admin/.env.local"
fi

if [ ! -f apps/api/.env ]; then
    cp .env apps/api/.env
    echo "✅ Created apps/api/.env"
fi

# Install dependencies
echo "📦 Installing Node.js dependencies..."
pnpm install

# Create directories
echo "📁 Creating required directories..."
mkdir -p data/generated
mkdir -p data/backups
mkdir -p logs
echo "✅ Created directories"

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL & Redis)..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0
until docker exec synthesize-postgres pg_isready -U synthesize > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ PostgreSQL failed to start after $max_attempts attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
attempt=0
until docker exec synthesize-redis redis-cli ping > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Redis failed to start after $max_attempts attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done
echo "✅ Redis is ready"

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
cd apps/api
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head
deactivate
cd ../..
echo "✅ Database migrations completed"

echo ""
echo "✨ Setup complete! ✨"
echo ""
echo "📖 Quick start:"
echo "   Run: pnpm dev"
echo "   This will start:"
echo "   - PostgreSQL (Docker)"
echo "   - Redis (Docker)"
echo "   - User Web App (http://localhost:3000)"
echo "   - Admin Portal (http://localhost:3001)"
echo "   - FastAPI Backend (http://localhost:8000)"
echo ""
echo "🌐 Access points:"
echo "   - User Web App: http://localhost:3000"
echo "   - Admin Portal: http://localhost:3001"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "⚠️  Remember to update .env with your API keys!"
echo ""
