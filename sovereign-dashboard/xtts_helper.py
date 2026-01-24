#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="XTTS Voice Cloning Helper")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--ref", required=True, help="Reference wav file")
    parser.add_argument("--out", required=True, help="Output wav file")
    args = parser.parse_args()

    try:
        from TTS.api import TTS
        print(f"🎤 Loading XTTS v2 model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        
        print(f"🔊 Synthesizing: {args.text[:50]}...")
        tts.tts_to_file(
            text=args.text,
            speaker_wav=args.ref,
            language="en",
            file_path=args.out
        )
        print(f"✅ Synthesis complete: {args.out}")
        return 0
    except Exception as e:
        print(f"❌ XTTS Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
