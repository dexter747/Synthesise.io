#!/bin/bash
# Cleanup script to kill processes on development ports
# Run this before starting dev servers or when ports are stuck

echo "🧹 Cleaning up development ports..."

# Ports used by the application
PORTS=(3000 3001 8000)

for port in "${PORTS[@]}"; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "   Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null
    fi
done

# Also kill any stuck pnpm/node processes related to this project
pkill -9 -f "pnpm.*dev" 2>/dev/null
pkill -9 -f "next-server" 2>/dev/null
pkill -9 -f "uvicorn.*app.main" 2>/dev/null
pkill -9 -f "celery.*app.celery_app" 2>/dev/null

echo "✅ Port cleanup complete!"
echo ""
