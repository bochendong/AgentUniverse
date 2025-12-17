#!/bin/bash

# Stop All Services Script
# This script stops both backend and frontend servers

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛑 Stopping AgentUniverse Application..."
echo ""

# Stop backend
echo "🔴 Stopping backend server..."
"$SCRIPT_DIR/stop_backend.sh"

echo ""

# Stop frontend
echo "🔴 Stopping frontend server..."
"$SCRIPT_DIR/stop_frontend.sh"

echo ""
echo "✅ All services stopped!"
