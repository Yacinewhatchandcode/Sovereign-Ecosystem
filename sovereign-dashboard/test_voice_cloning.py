#!/usr/bin/env python3
"""
🎤 Quick Voice Cloning Test
Test the F5-TTS voice cloning with your voice
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from asirem_speaking_engine import ASiREMSpeakingEngine

async def test_voice_cloning():
    """Test voice cloning with a simple phrase."""
    print("\n" + "="*60)
    print("🎤 VOICE CLONING TEST")
    print("="*60 + "\n")
    
    # Initialize engine
    engine = ASiREMSpeakingEngine()
    await engine.initialize()
    
    # Test phrase
    test_text = "Hello! I'm aSiReM, speaking with your cloned voice using F5-TTS."
    
    print(f"\n📝 Test phrase: \"{test_text}\"\n")
    print("🔄 Generating speech with your voice...\n")
    
    # Synthesize
    result = await engine.speak(test_text)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Audio file: {result['audio_path']}")
    print(f"   Video file: {result['video_path']}")
    
    print("\n💡 To hear the result:")
    print(f"   afplay {result['audio_path']}")
    
    print("\n🎬 To see the lip-synced video:")
    print(f"   open {result['video_path']}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_voice_cloning())
