#!/usr/bin/env python3
"""
Demo script to showcase real-time agent visual streaming.
"""

import asyncio
import websockets
import json
import time

async def demo_visual_streaming():
    """Connect to dashboard and trigger visual streaming demo."""
    uri = "ws://localhost:8082/ws/stream"
    
    print("🎬 Starting Agent Visual Streaming Demo")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Sovereign Command Center")
            
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"📡 {json.loads(welcome)['data']['message']}")
            
            print("\n🚀 Triggering Evolution Pipeline...")
            print("   Watch the browser dashboard to see:")
            print("   - Scanner's video showing file discovery")
            print("   - Classifier's video showing categorization")
            print("   - Researcher's video showing web search")
            print()
            
            # Trigger pipeline
            await websocket.send(json.dumps({
                "type": "run_pipeline"
            }))
            
            print("📹 Monitoring visual stream events...\n")
            
            # Monitor events for 60 seconds
            start_time = time.time()
            visual_updates = 0
            
            while time.time() - start_time < 60:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2)
                    data = json.loads(message)
                    
                    event_type = data.get("type")
                    event_data = data.get("data", {})
                    
                    # Highlight visual stream updates
                    if event_type == "agent_stream_update":
                        visual_updates += 1
                        print(f"🎥 [{event_data.get('agent_name')}] {event_data.get('message')}")
                        print(f"   Status: {event_data.get('status')}")
                        print(f"   Stream: {event_data.get('stream_url')}")
                        print()
                        
                    elif event_type == "activity":
                        icon = event_data.get('icon', '📍')
                        agent = event_data.get('agent_name', 'System')
                        msg = event_data.get('message', '')
                        print(f"{icon} [{agent}] {msg}")
                        
                    elif event_type == "pipeline_completed":
                        print("\n✅ Pipeline Complete!")
                        print(f"   Files Scanned: {event_data.get('files_scanned')}")
                        print(f"   Patterns Found: {event_data.get('patterns_found')}")
                        print(f"   Visual Stream Updates: {visual_updates}")
                        break
                        
                except asyncio.TimeoutError:
                    continue
                    
            print(f"\n📊 Demo completed. Visual updates captured: {visual_updates}")
            print("🎬 Check the browser dashboard to see the agent video streams!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure the server is running at http://localhost:8082")

if __name__ == "__main__":
    asyncio.run(demo_visual_streaming())
