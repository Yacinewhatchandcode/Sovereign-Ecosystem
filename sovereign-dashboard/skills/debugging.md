---
name: "Debug System Issues"
category: "Debugging"
triggers: ["debug", "error", "fix", "troubleshoot", "issue"]
tools: ["terminal", "logs", "browser_console"]
priority: "high"
---

# Debug System Issues

Systematic approach to debugging aSiReM Sovereign System issues.

## Quick Diagnostics

### 1. Check Backend Status
```bash
# Is backend running?
ps aux | grep backend.py

# Check recent logs
tail -n 50 server_production.log

# Look for errors
grep -i "error\|exception\|traceback" server_production.log | tail -20
```

### 2. Check Frontend
- Open browser console (F12)
- Look for JavaScript errors
- Check Network tab for failed requests
- Verify WebSocket connection

### 3. Check Database
```bash
# Check if database exists
ls -lh sovereign-dashboard/agent_communications.db

# Check database size (should be > 0)
du -h sovereign-dashboard/agent_communications.db
```

## Common Issues & Solutions

### Issue: Dashboard Not Loading

**Symptoms**: Blank page or "Cannot connect"

**Diagnosis**:
```bash
# Check if backend is running
ps aux | grep backend.py

# Check if port 8082 is in use
lsof -i :8082

# Check logs for startup errors
tail -n 100 server_production.log | grep -i error
```

**Solution**:
```bash
# Restart backend
pkill -f "python.*backend.py"
python3 backend.py > server_production.log 2>&1 &

# Wait 5 seconds for startup
sleep 5

# Verify
curl http://localhost:8082/api/status
```

---

### Issue: Voice Not Working

**Symptoms**: Microphone doesn't capture or no audio output

**Diagnosis**:
```bash
# Check if Whisper is installed
pip list | grep whisper

# Check logs for STT/TTS errors
grep -i "whisper\|tts\|audio" server_production.log | tail -20
```

**Solution**:
```bash
# Install Whisper if missing
pip install openai-whisper

# Check browser microphone permissions
# (Browser settings -> Site permissions -> Microphone)

# Test audio endpoint
curl -X POST http://localhost:8082/api/podcast/message \
  -H "Content-Type: application/json" \
  -d '{"question":"test","use_voice":false}'
```

---

### Issue: ByteBot Not Showing

**Symptoms**: ByteBot tab shows error or blank

**Diagnosis**:
```bash
# Check if Docker container is running
docker ps | grep bytebot

# Check VNC process
docker exec bytebot-desktop ps aux | grep vnc
```

**Solution**:
```bash
# Restart ByteBot container
docker restart bytebot-desktop

# Wait for VNC to start
sleep 10

# Verify VNC is accessible
docker exec bytebot-desktop ps aux | grep vnc
```

---

### Issue: WebSocket Disconnecting

**Symptoms**: "Reconnecting..." message, no real-time updates

**Diagnosis**:
- Check browser console for WebSocket errors
- Check if backend is overloaded (high CPU/memory)
- Look for connection timeout errors in logs

**Solution**:
```bash
# Check backend resource usage
top -p $(pgrep -f backend.py)

# Restart backend if needed
pkill -f "python.*backend.py"
python3 backend.py > server_production.log 2>&1 &
```

---

### Issue: Autonomy Loop Fails

**Symptoms**: "Run Evolution" button doesn't work

**Diagnosis**:
```bash
# Check if autonomy_loop.py exists
ls -l sovereign-dashboard/autonomy_loop.py

# Check logs for autonomy errors
grep -i "autonomy\|evolution" server_production.log | tail -20
```

**Solution**:
```bash
# Verify all factory modules exist
ls sovereign-dashboard/autonomous_factory.py
ls sovereign-dashboard/sub_agent_factory.py
ls sovereign-dashboard/rpa_bot_generator.py

# Check for import errors in logs
grep -i "importerror\|modulenotfounderror" server_production.log
```

---

## Advanced Debugging

### Enable Debug Mode
```python
# In backend.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Trace WebSocket Messages
```javascript
// In browser console:
const ws = new WebSocket('ws://localhost:8082/ws/stream');
ws.onmessage = (event) => {
    console.log('WS Message:', JSON.parse(event.data));
};
```

### Monitor Agent Activity
```bash
# Watch agent communications database
watch -n 2 'sqlite3 sovereign-dashboard/agent_communications.db "SELECT COUNT(*) FROM messages"'
```

## Performance Issues

### High CPU Usage
```bash
# Check which process is using CPU
top -o cpu

# If backend is high, check for infinite loops in logs
grep -i "loop\|while" server_production.log | tail -50
```

### High Memory Usage
```bash
# Check memory usage
ps aux | grep backend.py | awk '{print $6}'

# Restart if memory is > 1GB
pkill -f "python.*backend.py"
python3 backend.py > server_production.log 2>&1 &
```

## Logging Best Practices

### Increase Log Verbosity
```python
# Add to backend.py
print(f"🔍 DEBUG: {variable_name} = {value}")
```

### Rotate Logs
```bash
# Archive old logs
mv server_production.log server_production_$(date +%Y%m%d).log

# Start fresh
python3 backend.py > server_production.log 2>&1 &
```

## Success Criteria

After debugging:
- ✅ No errors in browser console
- ✅ Backend logs show normal operation
- ✅ All API endpoints respond
- ✅ WebSocket stays connected
- ✅ Voice system works
- ✅ ByteBot displays correctly
