#!/bin/bash

# Start Backend Server Script
# This script starts the FastAPI backend server

set -e

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🚀 Starting Backend Server..."
echo "📍 Project Root: $PROJECT_ROOT"
echo "📍 Backend Dir: $BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ] && [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    cd "$PROJECT_ROOT"
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
cd "$PROJECT_ROOT"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if backend API file exists
if [ -f "$BACKEND_DIR/main.py" ]; then
    API_MODULE="backend.main:app"
elif [ -f "$BACKEND_DIR/app.py" ]; then
    API_MODULE="backend.app:app"
elif [ -f "$BACKEND_DIR/server.py" ]; then
    API_MODULE="backend.server:app"
else
    echo "❌ Error: Backend API file not found!"
    echo "   Expected one of: main.py, app.py, or server.py in backend/ directory"
    exit 1
fi

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "   API module: $API_MODULE"
echo ""

cd "$PROJECT_ROOT"
python -m uvicorn "$API_MODULE" --host 0.0.0.0 --port 8000 --reload
