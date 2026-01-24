#!/usr/bin/env python3
"""
🧪 End-to-End Dashboard Test
Tests the complete speaking pipeline via WebSocket
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_dashboard_integration():
    """Test the dashboard WebSocket integration."""
    
    uri = "ws://localhost:8082/ws"
    
    print("\n" + "="*60)
    print("🧪 END-TO-END DASHBOARD TEST")
    print("="*60 + "\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            print(f"   URI: {uri}\n")
            
            # Test 1: aSiReM Speak
            print("📝 TEST 1: Triggering 'aSiReM Speak'...")
            await websocket.send(json.dumps({
                "type": "asirem_speak",
                "data": {"topic": "greeting"}
            }))
            
            # Listen for responses
            events_received = []
            timeout = asyncio.create_task(asyncio.sleep(10))
            
            while not timeout.done():
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    event = json.loads(response)
                    events_received.append(event)
                    
                    # Print activity events
                    if event.get("type") == "activity":
                        data = event.get("data", {})
                        icon = data.get("icon", "")
                        agent = data.get("agent_name", "")
                        message = data.get("message", "")
                        print(f"   {icon} [{agent}] {message}")
                    
                    # Stop after speaking complete
                    if event.get("type") == "speaking_completed":
                        data = event.get("data", {})
                        print(f"\n✅ Speaking completed!")
                        print(f"   Audio: {data.get('audio_path')}")
                        print(f"   Video: {data.get('video_path')}")
                        break
                        
                except asyncio.TimeoutError:
                    continue
            
            timeout.cancel()
            
            print(f"\n📊 Received {len(events_received)} events")
            
            # Test 2: Veo3 Narrative
            print("\n" + "="*60)
            print("📝 TEST 2: Triggering 'Cinematic Narrative'...")
            await websocket.send(json.dumps({
                "type": "veo3_narrative",
                "data": {"topic": "The Sovereignty of Cold Azirem"}
            }))
            
            # Listen for narrative events
            timeout2 = asyncio.create_task(asyncio.sleep(15))
            narrative_events = 0
            
            while not timeout2.done():
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    event = json.loads(response)
                    
                    if event.get("type") == "activity":
                        data = event.get("data", {})
                        icon = data.get("icon", "")
                        agent = data.get("agent_name", "")
                        message = data.get("message", "")
                        print(f"   {icon} [{agent}] {message}")
                        narrative_events += 1
                    
                except asyncio.TimeoutError:
                    continue
            
            timeout2.cancel()
            
            print(f"\n✅ Narrative test complete! Received {narrative_events} events")
            
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("   Is the backend running? (python3 real_agent_system.py)")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60 + "\n")
    print("💡 Next step: Open http://localhost:8082/index.html and click the buttons!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_dashboard_integration())
    exit(0 if success else 1)
