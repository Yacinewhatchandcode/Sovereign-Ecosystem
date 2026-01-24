#!/bin/bash
# ============================================
# 🧬 SOVEREIGN COMMAND CENTER - QUICK START
# ============================================
# Starts the real-time multi-agent streaming dashboard

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬${NC}"
echo -e "${CYAN}   SOVEREIGN COMMAND CENTER${NC}"
echo -e "${CYAN}   Autonomous Self-Evolving Multi-Agent Dashboard${NC}"
echo -e "${PURPLE}🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬${NC}"
echo ""

# Check for aiohttp
python3 -c "import aiohttp" 2>/dev/null || {
    echo "📦 Installing aiohttp..."
    pip install aiohttp --quiet
}

# Kill any existing process on port 8082
lsof -ti:8082 | xargs kill -9 2>/dev/null || true

# Start server
echo -e "${GREEN}🚀 Starting Sovereign Command Center...${NC}"
echo ""
echo -e "🌐 Dashboard: ${CYAN}http://localhost:8082/${NC}"
echo -e "📡 WebSocket: ${CYAN}ws://localhost:8082/ws/stream${NC}"
echo -e "📊 API:       ${CYAN}http://localhost:8082/api/status${NC}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 streaming_server.py --port 8082
