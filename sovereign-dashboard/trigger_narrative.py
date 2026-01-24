import asyncio
import json
import websockets
import sys

async def trigger_narrative(topic="The Sovereignty of Cold Azirem"):
    uri = "ws://localhost:8082/ws/stream"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🚀 Connected to Sovereign Command Center")
            print(f"🎭 Triggering Cinematic Narrative: {topic}")
            
            payload = {
                "type": "veo3_narrative",
                "topic": topic
            }
            
            await websocket.send(json.dumps(payload))
            print("✅ Narrative production request sent!")
            
            # Listen for progress
            print("\n📡 Monitoring production stream...")
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=60)
                    data = json.loads(message)
                    if data.get("type") == "activity":
                        event = data["data"]
                        print(f"[{event['icon']} {event['agent_name']}] {event['message']}")
                        
                        if "Production Complete" in event['message']:
                            break
                except asyncio.TimeoutError:
                    print("⚠️ Timeout waiting for updates.")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "The Sovereignty of Cold Azirem"
    asyncio.run(trigger_narrative(topic))
