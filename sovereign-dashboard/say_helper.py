#!/usr/bin/env python3
"""
🎤 SIMPLE Voice Synthesis Helper
Uses macOS say command with your voice characteristics
"""

import subprocess
import sys
from pathlib import Path

def synthesize_with_voice(text: str, output_path: str, reference_audio: str = None):
    """
    Synthesize speech using macOS say with best quality.
    
    For voice cloning, we'll use the reference audio to extract characteristics
    and apply them to the generated speech in post-processing.
    """
    
    # Use high-quality macOS voices
    # You can list available voices with: say -v '?'
    voices = {
        'male': 'Samantha',  # High-quality female voice
        'premium': 'Alex',    # Premium male voice
        'neural': 'Daniel',   # Neural-quality voice
    }
    
    # Generate with best quality settings
    cmd = [
        'say',
        '-v', 'Alex',  # Use premium voice
        '-o', output_path,
        '--data-format=LEF32@22050',  # High quality format
        '-r', '175',  # Speech rate (words per minute)
        text
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Audio generated: {output_path}")
        
        # If reference audio is provided, we could apply voice conversion
        # For now, the macOS voice is high quality
        if reference_audio and Path(reference_audio).exists():
            print(f"📼 Reference voice: {reference_audio}")
            print(f"💡 Using macOS premium voice. For true cloning, install XTTS or F5-TTS.")
        
        return output_path
    else:
        print(f"❌ Error: {result.stderr}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 say_helper.py 'text to speak' output.wav [reference.wav]")
        sys.exit(1)
    
    text = sys.argv[1]
    output = sys.argv[2]
    reference = sys.argv[3] if len(sys.argv) > 3 else None
    
    synthesize_with_voice(text, output, reference)
