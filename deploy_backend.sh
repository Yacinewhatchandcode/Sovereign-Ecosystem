#!/bin/bash
# === Sovereign Backend VPS Deploy Script ===
# Run this directly on VPS: bash deploy_backend.sh
# Or trigger remotely: ssh root@31.97.52.22 "bash /opt/sovereign-backend/deploy_backend.sh"

set -e

REPO="https://github.com/Yacinewhatchandcode/Sovereign-Ecosystem.git"
DEPLOY_DIR="/opt/sovereign-backend"
PORT=8082
LOG="$DEPLOY_DIR/backend.log"

echo "=== SOVEREIGN BACKEND DEPLOY ==="
echo "Target: $DEPLOY_DIR"
echo "Port:   $PORT"

# 1. Clone or pull
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "[GIT] Pulling latest..."
    cd "$DEPLOY_DIR" && git pull origin main
else
    echo "[GIT] Cloning fresh..."
    mkdir -p "$DEPLOY_DIR"
    git clone "$REPO" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# 2. Venv
echo "[VENV] Setting up Python env..."
cd "$DEPLOY_DIR"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate

# 3. Install deps
echo "[PIP] Installing core dependencies..."
pip install -q aiohttp aiofiles python-dotenv openai requests colorama websockets 2>&1 | tail -5

# 4. Kill any existing backend
echo "[KILL] Stopping existing backend on port $PORT..."
kill $(lsof -t -i:$PORT) 2>/dev/null || true
sleep 1

# 5. Start backend
echo "[START] Launching backend..."
nohup python backend.py > "$LOG" 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 6. Wait and verify
sleep 4
if curl -sf http://localhost:$PORT/api/status > /dev/null 2>&1; then
    echo "✅ BACKEND ONLINE at http://31.97.52.22:$PORT"
    curl -s http://localhost:$PORT/api/status
else
    echo "❌ Backend failed to start. Logs:"
    tail -20 "$LOG"
fi
