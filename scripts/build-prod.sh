#!/bin/bash

# Production build script

set -e

echo "🏗️  Building Synthesize.io for production..."

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install --frozen-lockfile

# Build all packages and apps
echo "🔨 Building packages and applications..."
pnpm build

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose -f docker-compose.yml build

echo "✅ Build complete!"
echo ""
echo "To deploy:"
echo "  docker-compose up -d"
