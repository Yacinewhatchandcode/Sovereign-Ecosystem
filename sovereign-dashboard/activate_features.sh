#!/bin/bash
# aSiReM Feature Activation Diagnostic
# Run this to check which features are ready

echo "🧬 aSiReM FEATURE ACTIVATION STATUS"
echo "===================================="
echo ""

# 1. Dashboard
echo "📊 1. DASHBOARD"
if curl -s http://localhost:8082 > /dev/null; then
    echo "   ✅ Server running on :8082"
    if curl -s http://localhost:8082 | grep -q "fetchAgentsConfig"; then
        echo "   ✅ Updated HTML with agent loading"
    else
        echo "   ❌ OLD HTML - needs hard refresh in browser"
    fi
else
    echo "   ❌ Server not responding"
fi
echo ""

# 2. Opik
echo "🔭 2. OPIK OBSERVABILITY"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Opik running on :5173"
    echo "   ℹ️  Empty until agents execute (normal)"
else
    echo "   ❌ Opik not running"
fi
echo ""

# 3. ByteBot VNC
echo "🐳 3. BYTEBOT VNC"
if curl -s http://localhost:9990 > /dev/null 2>&1; then
    echo "   ✅ ByteBot VNC on :9990"
else
    echo "   ❌ ByteBot container not running"
    echo "   💡 Start with: docker-compose up -d"
fi
echo ""

# 4. Voice Cloning
echo "🗣️ 4. VOICE CLONING (XTTS)"
if [ -d "/Users/yacinebenhamou/venv-xtts" ]; then
    echo "   ✅ XTTS venv exists"
    if [ -f "MyVoice.wav" ]; then
        echo "   ✅ MyVoice.wav found"
    else
        echo "   ⚠️  MyVoice.wav not in current directory"
    fi
else
    echo "   ❌ XTTS venv not found"
fi
echo ""

# 5. Gesture Control
echo "🖐️ 5. GESTURE CONTROL"
if grep -q "MediaPipe" index.html 2>/dev/null; then
    echo "   ✅ MediaPipe integrated in HTML"
    echo "   ℹ️  Needs webcam permission from browser"
else
    echo "   ❌ MediaPipe not found in HTML"
fi
echo ""

# 6. Agent System
echo "🤖 6. AGENT SYSTEM"
AGENT_COUNT=$(curl -s http://localhost:8082/api/status 2>/dev/null | grep -o '"agents_spawned":[0-9]*' | grep -o '[0-9]*')
if [ -n "$AGENT_COUNT" ]; then
    echo "   ✅ $AGENT_COUNT agents spawned"
else
    echo "   ❌ Cannot reach agent API"
fi
echo ""

echo "===================================="
echo "🎯 NEXT STEPS:"
echo "1. Hard refresh browser on localhost:8082 (Cmd+Shift+R)"
echo "2. Click 'Run Evolution' to activate agents"
echo "3. Click agent cards to open viewer with gesture control"
echo "4. Click '🎥 LIVE' to enable webcam avatar"
echo "5. Click 'aSiReM Speak' to test voice cloning"
echo ""
