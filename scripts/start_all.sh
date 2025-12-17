#!/bin/bash

# Start All Services Script
# This script starts both backend and frontend servers

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Starting AgentUniverse Application..."
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend may already be running."
fi

if check_port 3001; then
    echo "⚠️  Port 3001 is already in use. Frontend may already be running."
fi

echo ""
echo "Starting services in separate terminals..."
echo ""

# Start backend in background
echo "🌟 Starting backend server..."
"$SCRIPT_DIR/start_backend.sh" &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo "🌟 Starting frontend server..."
"$SCRIPT_DIR/start_frontend.sh" &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📍 Frontend: http://localhost:3001"
echo "📍 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
