#!/bin/bash
# AZIREM Sovereign Dashboard Startup Script
# This script starts the server with correct Python environment

cd "$(dirname "$0")"

echo "🚀 Starting AZIREM Sovereign Dashboard..."
echo "   📂 Directory: $(pwd)"
echo "   🐍 Using: ./venv-speaking/bin/python3"

# Kill any existing server
pkill -f real_agent_system.py 2>/dev/null
sleep 1

# Start the server using venv Python directly  
# LIGHTWEIGHT MODE: Prevents desktop actuation hangs on startup
echo "   🌐 Starting on http://localhost:8082"
OPIK_DISABLED=true ASIREM_LIGHTWEIGHT_MODE=1 ./venv-speaking/bin/python3 real_agent_system.py --port 8082

