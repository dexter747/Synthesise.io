#!/bin/bash
# Safe development script that cleans up ports before and after running

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLEANUP_SCRIPT="$PROJECT_ROOT/scripts/cleanup-ports.sh"

# Make cleanup script executable
chmod +x "$CLEANUP_SCRIPT"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    "$CLEANUP_SCRIPT"
    exit 0
}

# Trap exit signals
trap cleanup EXIT INT TERM

# Cleanup before starting
echo "🚀 Starting Synthesize.io Development Environment"
"$CLEANUP_SCRIPT"

# Start development servers
cd "$PROJECT_ROOT"
pnpm dev
