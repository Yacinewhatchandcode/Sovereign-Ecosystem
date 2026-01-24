#!/usr/bin/env python3
"""Test XTTS voice cloning with workaround"""
import sys
import torch
from pathlib import Path

# Add safe globals to allow model loading
from TTS.tts.configs.xtts_config import XttsConfig
torch.serialization.add_safe_globals([XttsConfig])

# Now import and use TTS
from TTS.api import TTS

# Paths
voice_ref = Path.home() / "aSiReM" / "sovereign-dashboard" / "assets" / "MyVoice.wav"
output_file = Path.home() / "aSiReM" / "sovereign-dashboard" / "generated" / "test_xtts_clone.wav"

print(f"🎤 Testing XTTS Voice Cloning...")
print(f"   Voice Reference: {voice_ref}")
print(f"   Output: {output_file}")

try:
    # Initialize TTS model
    print("\n📦 Loading XTTS v2 model...")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    
    # Generate speech
    print("🎙️ Generating cloned speech...")
    tts.tts_to_file(
        text="Hello! This is aSiReM, speaking with your cloned voice using XTTS version 2. The voice cloning system is now fully operational.",
        speaker_wav=str(voice_ref),
        language='en',
        file_path=str(output_file)
    )
    
    print(f"\n✅ SUCCESS! Voice cloned and saved to:")
    print(f"   {output_file}")
    
    # Check file size
    if output_file.exists():
        size = output_file.stat().st_size / 1024  # KB
        print(f"   File size: {size:.1f} KB")
    
    print("\n🔊 Play with: afplay ~/aSiReM/sovereign-dashboard/generated/test_xtts_clone.wav")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
