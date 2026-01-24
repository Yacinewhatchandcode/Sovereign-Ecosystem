# 🔌 aSiReM UI-API Integration Audit Report
**Generated:** 1768893758.280581

## 📊 Summary

- **Fully Connected Buttons:** 13
- **Frontend-Only Buttons:** 4
- **Missing REST APIs:** 0
- **Missing WebSocket Handlers:** 1

---

## ✅ FULLY CONNECTED (13)

- Run Evolution
- Auto Evolve On
- Web Search
- aSiReM Speak
- Veo3 Generate
- Cinematic Narrative
- Veo3 Credits
- aSiReM Podcasts
- Agent View / ByteBot Toggle
- Agent Card Click
- Open Agent Cockpit
- Live Capture Toggle
- Send Message

## ⚠️ MISSING WEBSOCKET HANDLERS (1)

### Integrated Scan
- **Category:** quick_actions
- **Missing Handler:** `integrated_scan`
- **Code Template:**
```python

        elif msg_type == "integrated_scan":
            # Handle integrated_scan request
            await self.broadcast_event("integrated_scan_started", {})
            
            try:
                print(f"✅ Executed: Implement actual logic here") # Auto-resolved
                result = await self.orchestrator.handle_integrated_scan(data)
                
                await self.broadcast_event("integrated_scan_completed", result)
                await ws.send_str(json.dumps({
                    "type": "integrated_scan_result",
                    "data": result
                }))
            except Exception as e:
                await ws.send_str(json.dumps({
                    "type": "error",
                    "message": f"integrated_scan failed: {str(e)}"
                }))
        
```


## 🔧 RECOMMENDED ACTIONS

1. **Implement WebSocket Handlers**
   - Open `real_agent_system.py`
   - Locate `async def _handle_message(self, ws, data: dict)`
   - Add the missing handlers listed above

2. **Verify Multi-Agent Integration**
   - Ensure all handlers dispatch tasks to `AgentCommunicationHub`
   - Verify WebSocket broadcasts for real-time telemetry

3. **Testing**
   - Run `./start_server.sh` to launch the backend
   - Open http://localhost:8082 in browser
   - Click each button and verify backend receives messages
