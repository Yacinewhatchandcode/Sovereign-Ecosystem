import asyncio
import websockets
import json
import time

async def run_sovereign_cycle():
    uri = "ws://localhost:8082/ws/stream"
    print(f"🚀 INITIATING SOVEREIGN NARRATIVE CYCLE")
    print(f"🔗 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri, open_timeout=30) as websocket:
            # 1. Pipeline Run (Option 1)
            print("\n🔄 Step 1: Triggering Sovereign Mesh Scan (Option 1)")
            scan_command = {
                "type": "run_pipeline",
                "data": {
                    "reason": "Sovereign Narrative Cycle Demonstration",
                    "path": "/Users/yacinebenhamou/aSiReM"
                }
            }
            await websocket.send(json.dumps(scan_command))
            
            # 2. Cinematic Narrative (Option 2)
            print("\n🎭 Step 2: Orchestrating Cinematic Narrative (Option 2)")
            narrative_command = {
                "type": "veo3_narrative",
                "data": {
                    "topic": "The Dawn of Sovereign Autonomy: aSiReM 2026 Roadmap"
                }
            }
            await websocket.send(json.dumps(narrative_command))
            
            # 3. Monitor Activity for 30 seconds
            print("\n🛰️ Monitoring Live Activity Stream...")
            start_time = time.time()
            while time.time() - start_time < 30:
                try:
                    message_raw = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message = json.loads(message_raw)
                    msg_type = message.get("type")
                    data = message.get("data", {})
                    
                    if msg_type == "activity":
                        icon = data.get("icon", "🔹")
                        name = data.get("agent_name", "Unknown")
                        msg = data.get("message", "")
                        print(f"{icon} [{name}] {msg}")
                    elif msg_type == "pipeline_started":
                        print(f"✅ Pipeline Started: {data.get('message')}")
                    elif msg_type == "asirem_state":
                        print(f"🧬 [aSiReM State] {data.get('state')}: {data.get('message')}")
                        
                except asyncio.TimeoutError:
                    continue
                    
            print("\n🏁 Initial Orchestration Complete. The agents are now operating autonomously.")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_sovereign_cycle())
