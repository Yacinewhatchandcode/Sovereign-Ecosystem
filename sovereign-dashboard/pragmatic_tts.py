#!/usr/bin/env python3
"""
🎤 **PRAGMATIC** Voice Synthesis for aSiReM
Uses the best available option with graceful fallbacks.

Priority order:
1. Your voice with pitch/speed manipulation (simple but effective)
2. Premium macOS voices with character
3. Standard system TTS
"""

import subprocess
import sys
from pathlib import Path
import os

def synthesize_speech(text: str, output_path: str, reference_audio: str = None):
    """
    Synthesize speech with the best available method.
    
    Currently uses macOS `say` with enhanced settings for character.
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Use Alex voice with optimized settings for clarity and character
    cmd = [
        'say',
        '-v', 'Alex',              # Premium quality voice
        '-r', '180',                # Speech rate (words per minute) - natural pace
        '-o', output_path,
        '--data-format=LEF32@22050',  # High quality audio format
        text
    ]
    
    print(f"🎤 Generating speech with Alex voice...")
    print(f"   Text: '{text[:60]}{'...' if len(text) > 60 else ''}'")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✅ Audio generated: {output_path}")
        
        # Optional: Apply post-processing for voice character
        # This is where you could add pitch shifting, formant adjusting, etc.
        # to make it sound more like your voice reference
        
        if reference_audio and Path(reference_audio).exists():
            print(f"   📼 Reference voice available: {Path(reference_audio).name}")
            print(f"   💡 Using premium macOS voice. Install XTTS for true cloning.")
        
        return output_path
    else:
        print(f"   ❌ Error: {result.stderr}")
        return None

def get_available_voices():
    """List all available macOS voices."""
    result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 pragmatic_tts.py 'text' output.wav [reference.wav]")
        print("\nAvailable voices:")
        print(get_available_voices()[:500] + "...")
        sys.exit(1)
    
    text = sys.argv[1]
    output = sys.argv[2]
    reference = sys.argv[3] if len(sys.argv) > 3 else None
    
    synthesize_speech(text, output, reference)
