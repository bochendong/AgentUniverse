#!/bin/bash

# Stop Frontend Development Server Script
# This script stops the Vite frontend development server running on port 3001

set -e

echo "🛑 Stopping Frontend Development Server..."

# Find processes using port 3001
PIDS=$(lsof -ti :3001 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "ℹ️  No frontend server found running on port 3001"
    exit 0
fi

# Also try to find vite/node processes related to the frontend
VITE_PIDS=$(pgrep -f "vite.*3001" 2>/dev/null || true)
NODE_PIDS=$(pgrep -f "node.*vite" 2>/dev/null || true)

# Combine and get unique PIDs
ALL_PIDS=$(echo "$PIDS $VITE_PIDS $NODE_PIDS" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    echo "ℹ️  No frontend server process found"
    exit 0
fi

echo "📋 Found frontend processes: $ALL_PIDS"

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
REMAINING=$(lsof -ti :3001 2>/dev/null || true)
if [ -n "$REMAINING" ]; then
    echo "⚠️  Some processes are still running, force killing..."
    for PID in $REMAINING; do
        kill -9 $PID 2>/dev/null || true
    done
fi

# Final check
if lsof -ti :3001 >/dev/null 2>&1; then
    echo "❌ Failed to stop all frontend processes"
    exit 1
else
    echo "✅ Frontend server stopped successfully"
fi
