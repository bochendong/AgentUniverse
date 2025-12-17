#!/bin/bash

# Stop Backend Server Script
# This script stops the FastAPI backend server running on port 8000

set -e

echo "🛑 Stopping Backend Server..."

# Find processes using port 8000
PIDS=$(lsof -ti :8000 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "ℹ️  No backend server found running on port 8000"
    exit 0
fi

# Also try to find uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn.*backend.main:app" 2>/dev/null || true)

# Combine and get unique PIDs
ALL_PIDS=$(echo "$PIDS $UVICORN_PIDS" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    echo "ℹ️  No backend server process found"
    exit 0
fi

echo "📋 Found backend processes: $ALL_PIDS"

# Kill the processes
for PID in $ALL_PIDS; do
    if ps -p $PID > /dev/null 2>&1; then
        echo "   Stopping process $PID..."
        kill $PID 2>/dev/null || true
    fi
done

# Wait a moment for graceful shutdown
sleep 2

# Check if any processes are still running and force kill if necessary
REMAINING=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$REMAINING" ]; then
    echo "⚠️  Some processes are still running, force killing..."
    for PID in $REMAINING; do
        kill -9 $PID 2>/dev/null || true
    done
fi

# Final check
if lsof -ti :8000 >/dev/null 2>&1; then
    echo "❌ Failed to stop all backend processes"
    exit 1
else
    echo "✅ Backend server stopped successfully"
fi
