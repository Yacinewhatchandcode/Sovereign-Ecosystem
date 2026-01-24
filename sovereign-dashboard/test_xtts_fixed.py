#!/usr/bin/env python3
"""
🔧 XTTS Voice Cloning - FIXED VERSION
Properly handles PyTorch 2.6 safe globals
"""
import sys
import torch
from pathlib import Path

# Add ALL required safe globals for XTTS
from TTS.tts.configs.xtts_config import XttsConfig, XttsAudioConfig
from TTS.tts.models.xtts import XttsArgs

torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs])

# Now import TTS
from TTS.api import TTS

def test_voice_cloning():
    """Test XTTS voice cloning with your voice"""
    
    # Paths
    voice_ref = Path.home() / "aSiReM" / "sovereign-dashboard" / "assets" / "MyVoice.wav"
    output_file = Path.home() / "aSiReM" / "sovereign-dashboard" / "generated" / "test_xtts_clone.wav"
    
    print(f"🎤 Testing XTTS Voice Cloning (Fixed Version)")
    print(f"   Voice Reference: {voice_ref}")
    print(f"   Output: {output_file}\n")
    
    if not voice_ref.exists():
        print(f"❌ Voice file not found: {voice_ref}")
        return False
    
    try:
        # Initialize TTS model
        print("📦 Loading XTTS v2 model...")
        tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
        
        # Generate speech
        print("🎙️ Generating cloned speech with your voice...")
        tts.tts_to_file(
            text="Hello! This is aSiReM, speaking with your perfectly cloned voice using XTTS version 2. The voice cloning system is now fully operational and ready for production use.",
            speaker_wav=str(voice_ref),
            language='en',
            file_path=str(output_file)
        )
        
        print(f"\n✅ SUCCESS! Voice cloned and saved to:")
        print(f"   {output_file}\n")
        
        # Check file
        if output_file.exists():
            size = output_file.stat().st_size / 1024
            print(f"   File size: {size:.1f} KB")
            print(f"\n🔊 Play with: afplay {output_file}\n")
            return True
        else:
            print("❌ Output file not created")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_voice_cloning()
    sys.exit(0 if success else 1)
