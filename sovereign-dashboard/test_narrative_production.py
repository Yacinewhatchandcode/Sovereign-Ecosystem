#!/usr/bin/env python3
"""
🎭 Test Cinematic Narrative Production
Direct test of the complete pipeline
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from asirem_speaking_engine import ASiREMSpeakingEngine

async def test_narrative():
    """Test the full cinematic narrative production."""
    
    print("\n" + "🎬" * 30)
    print("  CINEMATIC NARRATIVE TEST")
    print("🎬" * 30 + "\n")
   
    # Create engine
    engine = ASiREMSpeakingEngine()
    
    # Set up callback to print events
    async def print_events(event_type, data):
        if event_type == "activity":
            icon = data.get("icon", "")
            agent = data.get("agent_name", "")
            message = data.get("message", "")
            print(f"{icon} [{agent}] {message}")
        else:
            print(f"📡 [{event_type}] {data}")
    
    engine.set_callback(print_events)
    
    # Initialize
    await engine.initialize()
    
    # Test 1: Simple speaking
    print("\n" + "="*60)
    print("TEST 1: Simple Speaking")
    print("="*60 + "\n")
    
    result1 = await engine.speak_about("greeting")
    print(f"\n✅ Speaking test complete!")
    print(f"   Audio: {result1['audio_path']}")
    print(f"   Video: {result1['video_path']}")
    
    # Test 2: Cinematic narrative
    print("\n" + "="*60)
    print("TEST 2: Cinematic Narrative Production")
    print("="*60 + "\n")
    
    result2 = await engine.produce_cinematic_narrative("The Sovereignty of Cold Azirem")
    print(f"\n✅ Narrative production complete!")
    print(f"   Topic: {result2['topic']}")
    print(f"   Scenes: {len(result2['scenes'])}")
    print(f"   Remaining Veo3 credits: {result2['credits']}")
    
    # Play the first result
    print(f"\n🔊 To hear the result:")
    print(f"   afplay {result1['audio_path']}")
    
    return result2

if __name__ == "__main__":
    result = asyncio.run(test_narrative())
