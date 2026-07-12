#!/bin/bash

# Start all development servers concurrently

echo "🚀 Starting Synthesize.io development servers..."

# Check if Docker services are running
if ! docker ps | grep -q synthesize-postgres; then
    echo "Starting Docker services..."
    docker-compose up -d postgres redis
    sleep 3
fi

# Start all services with turbo
pnpm dev
