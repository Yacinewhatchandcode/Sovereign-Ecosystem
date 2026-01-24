#!/usr/bin/env python3
"""
🎵 STREAMING TTS - Sentence-by-Sentence Synthesis
==================================================
Streams TTS output sentence-by-sentence for smoother podcast responses.
"""

import asyncio
import re
from pathlib import Path
from typing import List, Callable, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))


class StreamingTTS:
    """Sentence-by-sentence TTS streaming."""
    
    def __init__(self):
        self.speaking_engine = None
        self._init_engine()
        
    def _init_engine(self):
        """Initialize XTTS speaking engine."""
        try:
            from asirem_speaking_engine import ASiREMSpeakingEngine
            self.speaking_engine = ASiREMSpeakingEngine()
        except Exception as e:
            print(f"⚠️ TTS engine unavailable: {e}")
            
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    async def stream_speak(
        self,
        text: str,
        on_sentence_start: Optional[Callable] = None,
        on_sentence_complete: Optional[Callable] = None
    ) -> List[str]:
        """
        Speak text sentence-by-sentence with callbacks.
        
        Args:
            text: Full text to speak
            on_sentence_start: Called when starting each sentence
            on_sentence_complete: Called when sentence audio is ready
            
        Returns:
            List of audio file paths
        """
        if not self.speaking_engine:
            print("⚠️ No TTS engine available")
            return []
            
        sentences = self.split_sentences(text)
        audio_files = []
        
        for i, sentence in enumerate(sentences):
            if on_sentence_start:
                await on_sentence_start(i, sentence)
                
            # Synthesize sentence
            result = await self.speaking_engine.speak(sentence)
            
            if result.get("audio_path"):
                audio_files.append(result["audio_path"])
                
                if on_sentence_complete:
                    await on_sentence_complete(i, sentence, result["audio_path"])
            else:
                print(f"⚠️ Sentence {i} synthesis failed")
                
        return audio_files
        
    async def stream_speak_with_playback(self, text: str):
        """Stream speak with immediate playback of each sentence."""
        async def on_complete(idx, sentence, audio_path):
            print(f"🔊 Playing sentence {idx + 1}: {sentence[:50]}...")
            # Could trigger audio playback here
            
        return await self.stream_speak(
            text,
            on_sentence_complete=on_complete
        )


# Demo
async def demo():
    """Demo streaming TTS."""
    tts = StreamingTTS()
    
    text = """
    AZIREM is a sovereign AI orchestration system. It manages a fleet of 13 specialized agents.
    Each agent has unique capabilities. Together they form a powerful multi-agent ecosystem.
    The system can scan codebases, generate narratives, and synthesize speech.
    """
    
    print("🎵 Streaming TTS Demo")
    print("=" * 50)
    
    async def on_start(idx, sentence):
        print(f"\n[{idx + 1}] Synthesizing: {sentence[:60]}...")
        
    async def on_complete(idx, sentence, audio_path):
        print(f"    ✅ Audio ready: {audio_path}")
        
    audio_files = await tts.stream_speak(
        text,
        on_sentence_start=on_start,
        on_sentence_complete=on_complete
    )
    
    print(f"\n✅ Generated {len(audio_files)} audio files")


if __name__ == "__main__":
    asyncio.run(demo())
