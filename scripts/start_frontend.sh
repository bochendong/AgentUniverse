#!/bin/bash

# Start Frontend Development Server Script
# This script starts the Vite frontend development server

set -e

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🚀 Starting Frontend Development Server..."
echo "📍 Project Root: $PROJECT_ROOT"
echo "📍 Frontend Dir: $FRONTEND_DIR"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "   Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Check if package.json exists
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

# Check if node_modules exists, install if not
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo ""
    echo "📦 Frontend dependencies not found. Installing..."
    echo "   This may take a few minutes on first run..."
    cd "$FRONTEND_DIR"
    npm install
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
    echo ""
else
    echo "✅ Frontend dependencies already installed"
fi

# Check if .env file exists, create one if not
if [ ! -f "$FRONTEND_DIR/.env" ] && [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo "📝 Creating .env file..."
    cat > "$FRONTEND_DIR/.env" << EOF
# Backend API URL
VITE_API_URL=http://localhost:8000
EOF
    echo "✅ .env file created with default API URL: http://localhost:8000"
fi

# Start the development server
echo "🌟 Starting Vite development server on http://localhost:3001"
echo "   Frontend will proxy /api requests to http://localhost:8000"
echo ""

cd "$FRONTEND_DIR"
npm run dev
