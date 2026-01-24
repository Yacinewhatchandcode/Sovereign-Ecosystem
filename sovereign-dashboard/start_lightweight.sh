#!/bin/bash
# LIGHTWEIGHT Sovereign Dashboard Startup Script
# Starts the server without triggering heavy autonomous loops

cd "$(dirname "$0")"

export PYTHONPATH="./venv-speaking/lib/python3.14/site-packages:$PYTHONPATH"
# Disable autonomous mission loops
export ASIREM_LIGHTWEIGHT_MODE=1

echo "🚀 Starting LIGHTWEIGHT Sovereign Dashboard..."
echo "   📂 Directory: $(pwd)"
echo "   🌐 Starting on http://localhost:8082"

pkill -f real_agent_system.py 2>/dev/null
sleep 1

python3 real_agent_system.py --port 8082
