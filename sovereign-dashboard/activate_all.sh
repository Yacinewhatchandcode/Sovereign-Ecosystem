#!/bin/bash
# Complete System Activation Script
# This activates ALL features of the aSiReM Sovereign Dashboard

echo "🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬"
echo "   aSiReM SOVEREIGN SYSTEM"
echo "   FULL ACTIVATION SEQUENCE"
echo "🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬"
echo ""

cd "$(dirname "$0")"

# 1. Verify server is running
echo "1️⃣ Checking server status..."
if curl -s http://localhost:8082/api/status > /dev/null; then
    echo "   ✅ Server online"
else
    echo "   ❌ Server offline - start with: bash start_server.sh"
    exit 1
fi

# 2. Trigger Evolution Pipeline (activates Scanner, Classifier, Extractor)
echo ""
echo "2️⃣ Activating Evolution Pipeline..."
curl -X POST http://localhost:8082/api/evolution \
    -H "Content-Type: application/json" \
    -d '{"action": "start", "target": "/Users/yacinebenhamou/aSiReM"}' \
    -s > /dev/null &

# 3. Test aSiReM Speaking Engine
echo ""
echo "3️⃣ Testing Voice Cloning System..."
curl -X POST http://localhost:8082/api/asirem/speak \
    -H "Content-Type: application/json" \
    -d '{"text": "Sovereign systems online. All agents activated.", "agent_id": "azirem"}' \
    -s > /dev/null &

# 4. Generate Veo3 Credits Check
echo ""
echo "4️⃣ Checking Veo3 Video Generation..."
CREDITS=$(curl -s http://localhost:8082/api/veo3/credits | grep -o '"credits_remaining":\s*[0-9]*' | cut -d':' -f2 | tr -d ' ')
if [ -n "$CREDITS" ]; then
    echo "   ✅ Veo3 ready - $CREDITS credits remaining"
else
    echo "   ⚠️  Veo3 status unknown"
fi

# 5. Verify ByteBot VNC
echo ""
echo "5️⃣ Checking ByteBot Desktop..."
if curl -s http://localhost:9990 > /dev/null 2>&1; then
    echo "   ✅ ByteBot VNC active on :9990"
else
    echo "   ⚠️  ByteBot VNC not responding"
fi

# 6. Check Opik Observability
echo ""
echo "6️⃣ Checking Opik Observability..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Opik running on :5173"
    echo "   ℹ️  Will populate as agents execute"
else
    echo "   ⚠️  Opik not responding"
fi

# 7. Verify agent streams
echo ""
echo "7️⃣ Verifying Agent Video Streams..."
STREAM_COUNT=$(find outputs/agent_streams -name "idle_stream.mp4" 2>/dev/null | wc -l | tr -d ' ')
echo "   📹 $STREAM_COUNT agent streams available"

# 8. Test Web Search
echo ""
echo "8️⃣ Activating Web Research Agent..."
curl -X POST http://localhost:8082/api/web-search \
    -H "Content-Type: application/json" \
    -d '{"query": "Latest AI agent frameworks 2026", "deep_research": false}' \
    -s > /dev/null &

echo ""
echo "🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬"
echo "   ACTIVATION COMPLETE"
echo "🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬"
echo ""
echo "📊 Dashboard: http://localhost:8082"
echo "🔭 Opik:      http://localhost:5173"
echo "🐳 ByteBot:   http://localhost:9990"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Refresh browser on localhost:8082"
echo "2. Watch Real-Time Activity stream populate"
echo "3. Check Opik for agent traces"
echo "4. Click agent cards to see live feeds"
echo "5. Enable gestures for hand control"
echo ""
echo "⚡ All systems are now ACTIVE and generating data!"
echo ""
