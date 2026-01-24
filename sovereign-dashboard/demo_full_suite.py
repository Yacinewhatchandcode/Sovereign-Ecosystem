#!/usr/bin/env python3
"""
Comprehensive Demo Suite for Sovereign Command Center
Demonstrates all three visual streaming features.
"""

import asyncio
import websockets
import json
import time

class SovereignDemo:
    def __init__(self):
        self.uri = "ws://localhost:8082/ws/stream"
        self.ws = None
        
    async def connect(self):
        """Connect to the Sovereign Command Center."""
        print("🔌 Connecting to Sovereign Command Center...")
        self.ws = await websockets.connect(self.uri)
        welcome = await self.ws.recv()
        print(f"✅ {json.loads(welcome)['data']['message']}\n")
        
    async def monitor_events(self, duration=30, keywords=None):
        """Monitor WebSocket events for specified duration."""
        keywords = keywords or []
        start_time = time.time()
        events_captured = []
        
        while time.time() - start_time < duration:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=1)
                data = json.loads(message)
                
                event_type = data.get("type")
                event_data = data.get("data", {})
                
                # Capture relevant events
                if any(kw in str(data).lower() for kw in keywords) or event_type == "agent_stream_update":
                    events_captured.append({
                        "type": event_type,
                        "data": event_data,
                        "time": time.time() - start_time
                    })
                    
                # Display important events
                if event_type == "agent_stream_update":
                    agent = event_data.get('agent_name', 'Unknown')
                    status = event_data.get('status', 'unknown')
                    msg = event_data.get('message', '')
                    print(f"   🎥 [{agent}] {status.upper()}: {msg}")
                    
                elif event_type == "activity":
                    icon = event_data.get('icon', '📍')
                    agent = event_data.get('agent_name', 'System')
                    msg = event_data.get('message', '')
                    if any(kw in msg.lower() for kw in keywords):
                        print(f"   {icon} [{agent}] {msg}")
                        
            except asyncio.TimeoutError:
                continue
                
        return events_captured
        
    async def demo_1_speaking(self):
        """Demo 1: aSiReM Speaking with Voice Cloning"""
        print("=" * 70)
        print("🎤 DEMO 1: aSiReM Speaking with Voice Cloning")
        print("=" * 70)
        print("📋 Features:")
        print("   • F5-TTS Zero-Shot Voice Cloning")
        print("   • MuseTalk Lip-Sync Video Generation")
        print("   • Real-time Visual Stream Update")
        print()
        
        print("🚀 Triggering aSiReM Speak...")
        await self.ws.send(json.dumps({
            "type": "asirem_speak",
            "topic": "greeting"
        }))
        
        print("📡 Monitoring speaking pipeline...\n")
        events = await self.monitor_events(
            duration=25,
            keywords=['tts', 'speaking', 'voice', 'lip', 'azirem', 'narrative']
        )
        
        print(f"\n✅ Demo 1 Complete! Captured {len(events)} events")
        print("   Check the dashboard: aSiReM's avatar should show lip-synced video!\n")
        await asyncio.sleep(2)
        
    async def demo_2_pipeline(self):
        """Demo 2: Full Evolution Pipeline with Multi-Agent Streaming"""
        print("=" * 70)
        print("📡 DEMO 2: Evolution Pipeline - Multi-Agent Visual Streaming")
        print("=" * 70)
        print("📋 Features:")
        print("   • Scanner: Real-time file discovery visualization")
        print("   • Classifier: Pattern categorization display")
        print("   • Extractor: Knowledge graph building")
        print("   • Researcher: Web search activity")
        print()
        
        print("🚀 Triggering Full Evolution Pipeline...")
        await self.ws.send(json.dumps({
            "type": "run_pipeline"
        }))
        
        print("📡 Monitoring multi-agent execution...\n")
        events = await self.monitor_events(
            duration=60,
            keywords=['scanner', 'classifier', 'extractor', 'researcher', 'pipeline']
        )
        
        print(f"\n✅ Demo 2 Complete! Captured {len(events)} events")
        print("   Check the dashboard: Watch agents light up sequentially!\n")
        await asyncio.sleep(2)
        
    async def demo_3_cinematic(self):
        """Demo 3: Cinematic Narrative Production (9-Expert Team)"""
        print("=" * 70)
        print("🎭 DEMO 3: Cinematic Narrative Production")
        print("=" * 70)
        print("📋 Features:")
        print("   • 9-Expert Narrative Factory Deliberation")
        print("   • Multi-Scene Story Generation")
        print("   • Voice Cloning for Each Scene")
        print("   • Veo3 Video Prompt Generation")
        print("   • Real-time Credit Tracking")
        print()
        
        print("🚀 Triggering Cinematic Narrative Production...")
        await self.ws.send(json.dumps({
            "type": "veo3_narrative",
            "topic": "The Sovereignty of Digital Intelligence"
        }))
        
        print("📡 Monitoring cinematic production...\n")
        events = await self.monitor_events(
            duration=40,
            keywords=['narrative', 'cinematic', 'scene', 'story', 'veo3', 'voice', 'analyst', 'architect']
        )
        
        print(f"\n✅ Demo 3 Complete! Captured {len(events)} events")
        print("   Check the dashboard: Multi-scene production with visual streams!\n")
        
    async def run_full_demo(self):
        """Run all three demos in sequence."""
        try:
            await self.connect()
            
            print("🎬" * 35)
            print("   SOVEREIGN COMMAND CENTER - VISUAL STREAMING DEMO SUITE")
            print("🎬" * 35)
            print()
            print("📺 Open http://localhost:8082/index.html to watch live!")
            print("⏰ Starting demos in 3 seconds...\n")
            await asyncio.sleep(3)
            
            # Demo 1: Speaking
            await self.demo_1_speaking()
            
            # Demo 2: Pipeline
            await self.demo_2_pipeline()
            
            # Demo 3: Cinematic Narrative
            await self.demo_3_cinematic()
            
            print("=" * 70)
            print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("\n📊 Summary:")
            print("   ✅ aSiReM Speaking with Voice Cloning")
            print("   ✅ Multi-Agent Evolution Pipeline")
            print("   ✅ Cinematic Narrative Production")
            print("\n🎥 Check the browser dashboard for:")
            print("   • Individual agent video streams")
            print("   • Real-time activity updates")
            print("   • LIVE indicators on active agents")
            print("   • Dynamic visual stream switching")
            print("\n💎 Veo3 Credit Status:")
            print("   Click the 'Veo3 Credits' button to see usage!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Make sure the server is running at http://localhost:8082")
        finally:
            if self.ws:
                await self.ws.close()

async def main():
    demo = SovereignDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main())
