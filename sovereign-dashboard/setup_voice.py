#!/usr/bin/env python3
"""
🎤 Voice Reference Setup Helper
================================
This script helps you set up your voice reference for aSiReM speaking.

Usage:
    python3 setup_voice.py /path/to/your/voice.mp3 "Transcription of what you said"
    
Example:
    python3 setup_voice.py ~/Downloads/my_voice.mp3 "Hello, this is my voice sample for cloning"
"""

import sys
import shutil
from pathlib import Path

def setup_voice_reference(source_audio: str, transcription: str = ""):
    """Set up voice reference for aSiReM speaking."""
    
    source_path = Path(source_audio).expanduser()
    
    if not source_path.exists():
        print(f"❌ Error: Audio file not found at {source_path}")
        return False
    
    # Target directory
    target_dir = Path(__file__).parent / "assets/voice"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy audio file
    target_audio = target_dir / "reference.mp3"
    shutil.copy2(source_path, target_audio)
    print(f"✅ Voice reference copied to: {target_audio}")
    
    # Save transcription
    if transcription:
        target_text = target_dir / "reference.txt"
        target_text.write_text(transcription)
        print(f"✅ Transcription saved to: {target_text}")
        print(f"   Text: \"{transcription}\"")
    else:
        print("ℹ️  No transcription provided. F5-TTS will use auto-detection.")
        print("   For best results, provide the exact text spoken in the audio.")
    
    print("\n🎉 Voice reference setup complete!")
    print("\n📝 Next steps:")
    print("   1. The speaking engine will now use YOUR voice")
    print("   2. Test it by clicking 'aSiReM Speak' in the dashboard")
    print("   3. For better quality, provide the exact transcription")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n❌ Error: Please provide path to your voice audio file")
        print("\nUsage:")
        print("  python3 setup_voice.py /path/to/voice.mp3 \"What you said in the audio\"")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    transcription = sys.argv[2] if len(sys.argv) > 2 else ""
    
    success = setup_voice_reference(audio_path, transcription)
    sys.exit(0 if success else 1)
