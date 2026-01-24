#!/usr/bin/env python3
"""
🎙️ AZIREM VOICE PODCAST - Real-time Speech-to-Speech
=====================================================
True conversational AI with:
- Continuous microphone listening (Whisper STT)
- DeepSeek LLM reasoning
- Voice cloning response (XTTS)

Requirements:
  pip install sounddevice numpy scipy faster-whisper
"""

import asyncio
import sys
import os
import tempfile
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

# Audio processing
try:
    import sounddevice as sd
    import numpy as np
    from scipy.io import wavfile
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio libraries not installed. Run: pip install sounddevice numpy scipy")

# Whisper STT
WHISPER_AVAILABLE = False
USING_OPENAI_WHISPER = False
WhisperModel = None

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
    USING_OPENAI_WHISPER = False
except ImportError:
    try:
        import whisper
        WHISPER_AVAILABLE = True
        USING_OPENAI_WHISPER = True
    except ImportError:
        print("⚠️ Whisper not installed. Run: pip install openai-whisper")


# Add parent paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))


class VoicePodcast:
    """
    Real-time speech-to-speech conversation with AZIREM.
    """
    
    def __init__(
        self,
        whisper_model: str = "base",  # tiny, base, small, medium, large
        live_rate: int = 16000,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,  # seconds of silence to trigger processing
        min_audio_length: float = 0.5,  # minimum audio length to process
    ):
        self.live_rate = live_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_audio_length = min_audio_length
        
        # State
        self.is_running = False
        self.is_listening = True
        self.is_speaking = False
        self.audio_buffer = []
        self.last_sound_time = time.time()
        
        # Queues for async processing
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Initialize Whisper
        self.whisper_model = None
        self.whisper_model_name = whisper_model
        
        # Initialize Brain
        self.brain = None
        
        # Initialize TTS
        self.speaking_engine = None
        
        # Callbacks
        self.on_transcription: Optional[Callable] = None
        self.on_response: Optional[Callable] = None
        self.on_status: Optional[Callable] = None
        
    async def initialize(self):
        """Initialize all components."""
        print("🎙️ Initializing Voice Podcast...")
        print()
        
        # Check audio
        if not AUDIO_AVAILABLE:
            print("❌ Audio libraries not available")
            print("   Run: pip install sounddevice numpy scipy")
            return False
            
        # Check Whisper
        if not WHISPER_AVAILABLE:
            print("❌ Whisper not available")
            print("   Run: pip install faster-whisper")
            return False
            
        # Initialize Whisper
        print(f"🔊 Loading Whisper model: {self.whisper_model_name}")
        try:
            if USING_OPENAI_WHISPER:
                import whisper
                self.whisper_model = whisper.load_model(self.whisper_model_name)
                self.whisper_type = "openai"
            else:
                self.whisper_model = WhisperModel(
                    self.whisper_model_name,
                    device="cpu",  # Use "cuda" if available
                    compute_type="int8"
                )
                self.whisper_type = "faster"
            print(f"   ✅ Whisper loaded ({self.whisper_type})")
        except Exception as e:
            print(f"   ❌ Failed to load Whisper: {e}")
            return False

            
        # Initialize Brain
        print("🧠 Loading AZIREM Brain...")
        try:
            from azirem_brain import AziremBrain
            self.brain = AziremBrain()
            
            if await self.brain.check_ollama_available():
                print(f"   ✅ Brain connected to Ollama ({self.brain.model})")
            else:
                print("   ⚠️ Ollama not available, using fallback mode")
        except Exception as e:
            print(f"   ❌ Failed to load Brain: {e}")
            return False
            
        # Initialize TTS
        print("🔈 Loading TTS Engine...")
        try:
            from asirem_speaking_engine import ASiREMSpeakingEngine
            self.speaking_engine = ASiREMSpeakingEngine()
            print(f"   ✅ TTS ready ({self.speaking_engine.tts_backend})")
        except Exception as e:
            print(f"   ⚠️ TTS not available: {e}")
            print("   Will use system speech")
            
        print()
        return True
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Called for each audio block from the microphone."""
        if status:
            print(f"⚠️ Audio status: {status}")
            
        if not self.is_listening or self.is_speaking:
            return
            
        # Calculate volume
        volume = np.abs(indata).mean()
        
        # Add to buffer
        self.audio_buffer.append(indata.copy())
        
        # Check for sound
        if volume > self.silence_threshold:
            self.last_sound_time = time.time()
        else:
            # Check if silence duration exceeded
            silence_time = time.time() - self.last_sound_time
            buffer_duration = len(self.audio_buffer) * frames / self.live_rate
            
            if silence_time > self.silence_duration and buffer_duration > self.min_audio_length:
                # We have audio to process
                audio_data = np.concatenate(self.audio_buffer, axis=0)
                self.audio_queue.put(audio_data)
                self.audio_buffer = []
                self.last_sound_time = time.time()
                
    def _transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Whisper."""
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            persistent_path = f.name
            # Ensure audio is in correct format
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(persistent_path, self.live_rate, audio_int16)
            
        try:
            if self.whisper_type == "faster":
                segments, info = self.whisper_model.transcribe(
                    persistent_path,
                    language="en",
                    beam_size=5
                )
                text = " ".join([s.text for s in segments]).strip()
            else:
                result = self.whisper_model.transcribe(persistent_path, language="en")
                text = result["text"].strip()
                
            return text
        finally:
            os.unlink(persistent_path)
            
    async def _process_audio(self, audio_data: np.ndarray):
        """Process recorded audio: transcribe -> think -> speak."""
        self.is_listening = False
        
        # Transcribe
        if self.on_status:
            self.on_status("transcribing")
        print("\n🎧 Transcribing...")
        
        text = self._transcribe(audio_data)
        
        if not text or len(text) < 2:
            print("   (no speech detected)")
            self.is_listening = True
            return
            
        print(f"\n🧑 You: {text}")
        if self.on_transcription:
            self.on_transcription(text)
            
        # Check for exit commands
        if text.lower() in ["quit", "exit", "stop", "goodbye", "bye"]:
            print("\n👋 AZIREM: Goodbye! It was great talking with you.")
            if self.speaking_engine:
                await self._speak("Goodbye! It was great talking with you.")
            self.is_running = False
            return
            
        # Think
        if self.on_status:
            self.on_status("thinking")
        print("\n🤔 AZIREM is thinking...")
        
        response = await self.brain.think(text)
        
        print(f"\n🤖 AZIREM: {response}")
        if self.on_response:
            self.on_response(response)
            
        # Speak
        if self.on_status:
            self.on_status("speaking")
        await self._speak(response)
        
        # Resume listening
        self.is_listening = True
        if self.on_status:
            self.on_status("listening")
        print("\n🎤 Listening... (say 'quit' to exit)")
        
    async def _speak(self, text: str):
        """Speak text using TTS."""
        self.is_speaking = True
        
        try:
            if self.speaking_engine:
                result = await self.speaking_engine.speak(text)
                if result.get("audio_path"):
                    # Audio was generated and played
                    pass
            else:
                # Fallback to system TTS
                import subprocess
                subprocess.run(["say", "-v", "Samantha", text], check=False)
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
            # Fallback
            try:
                import subprocess
                subprocess.run(["say", text[:500]], check=False)
            except:
                pass
                
        self.is_speaking = False
        
    async def run(self):
        """Run the voice podcast session."""
        if not await self.initialize():
            print("\n❌ Failed to initialize. Please install required packages.")
            return
            
        print("=" * 60)
        print("🎙️ AZIREM VOICE PODCAST - Live Session")
        print("=" * 60)
        print()
        print("🎤 Speak naturally. AZIREM will listen and respond.")
        print("   Say 'quit' or 'goodbye' to end the session.")
        print()
        print("-" * 60)
        print("🎤 Listening...")
        print()
        
        self.is_running = True
        self.is_listening = True
        
        # Start audio stream
        try:
            with sd.InputStream(
                samplerate=self.live_rate,
                channels=1,
                dtype=np.float32,
                callback=self._audio_callback,
                blocksize=int(self.live_rate * 0.1)  # 100ms blocks
            ):
                while self.is_running:
                    # Check for audio to process
                    try:
                        audio_data = self.audio_queue.get_nowait()
                        await self._process_audio(audio_data)
                    except queue.Empty:
                        await asyncio.sleep(0.1)
                        
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.is_running = False
            
    def stop(self):
        """Stop the podcast session."""
        self.is_running = False


class AziremVoiceService:
    """
    Unified Voice Service for Backend Integration.
    Handles Audio -> Text -> Thinking -> Text -> Audio
    """

    def __init__(self, whisper_model="base"):
        self.whisper_model_name = whisper_model
        self.whisper_model = None
        self.brain = None
        self.speaking_engine = None
        self.live_rate = 16000
        self.speaking_engine = None
        self.live_rate = 16000
        self.initialized = False
        self.command_handler = None  # Optional async function(text) -> str or None

    def set_command_handler(self, handler):
        """Set a handler for parsing voice commands."""
        self.command_handler = handler

    async def initialize(self):
        """Initialize all AI components."""
        if self.initialized:
            return True

        print("🎙️ Initializing Azirem Voice Service for Backend...")
        
        # 1. Initialize Whisper
        if WHISPER_AVAILABLE:
            try:
                if USING_OPENAI_WHISPER:
                    import whisper
                    self.whisper_model = whisper.load_model(self.whisper_model_name)
                    self.whisper_type = "openai"
                else:
                    self.whisper_model = WhisperModel(
                        self.whisper_model_name,
                        device="cpu", 
                        compute_type="int8"
                    )
                    self.whisper_type = "faster"
                print(f"   ✅ Whisper loaded ({self.whisper_type})")
            except Exception as e:
                print(f"   ❌ Failed to load Whisper: {e}")
        else:
            print("   ⚠️ Whisper not available")

        # 2. Initialize Brain
        try:
            from azirem_brain import AziremBrain
            self.brain = AziremBrain()
            await self.brain.initialize()  # Ensure async init if needed
            print(f"   ✅ Brain ready")
        except Exception as e:
            print(f"   ❌ Failed to load Brain: {e}")

        # 3. Initialize TTS
        try:
            from asirem_speaking_engine import ASiREMSpeakingEngine
            self.speaking_engine = ASiREMSpeakingEngine()
            print(f"   ✅ TTS ready")
        except Exception as e:
            print(f"   ⚠️ TTS not available: {e}")

        self.initialized = True
        return True

    async def process_audio_blob(self, audio_bytes: bytes) -> dict:
        """
        Process a raw audio blob (WAV/WEBM) and return response audio + text.
        """
        if not self.initialized:
            await self.initialize()

        # 1. Transcribe
        transcription = await self.transcribe_audio_bytes(audio_bytes)
        if not transcription:
            return {"status": "no_speech", "text": ""}

        print(f"🎤 Heard: {transcription}")

        # 2. Command Check OR Think
        response_text = None
        
        # Try command handler first
        if self.command_handler:
            try:
                cmd_response = await self.command_handler(transcription)
                if cmd_response:
                    print(f"⚡ Executed Command: {cmd_response}")
                    response_text = cmd_response
            except Exception as e:
                print(f"⚠️ Command handler error: {e}")

        # If no command executed, use Brain
        if not response_text:
            if self.brain:
                response_text = await self.brain.think(transcription)
            else:
                response_text = f"I heard you say: {transcription}, but my brain is offline."

        print(f"🤖 Response: {response_text}")

        # 3. Speak (TTS)
        audio_path = None
        audio_base64 = None
        
        if self.speaking_engine:
            result = await self.speaking_engine.speak(response_text)
            audio_path = result.get("audio_path")
            
            # Read audio to base64 for immediate playback if needed
            if audio_path and os.path.exists(audio_path):
                 import base64
                 with open(audio_path, "rb") as f:
                     audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return {
            "status": "success",
            "user_text": transcription,
            "ai_text": response_text,
            "audio_path": audio_path,
            "audio_base64": audio_base64
        }

    async def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe bytes using Whisper."""
        if not self.whisper_model:
            return "Whisper not available."

        # Write bytes to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            persistent_path = f.name
        
        try:
            # We assume the blob is a valid audio format Whisper can handle (wav, webm, mp3)
            # If it's raw PCM, we might need conversion.
            # Assuming client sends WAV/WebM.
            
            if self.whisper_type == "faster":
                segments, info = self.whisper_model.transcribe(
                    persistent_path,
                    language="en",
                    beam_size=5
                )
                text = " ".join([s.text for s in segments]).strip()
            else:
                result = self.whisper_model.transcribe(persistent_path, language="en")
                text = result["text"].strip()
            
            return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        finally:
            if os.path.exists(persistent_path):
                os.unlink(persistent_path)


async def main():
    """Run the voice podcast."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AZIREM Voice Podcast")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    parser.add_argument("--silence", "-s", type=float, default=1.5,
                       help="Silence duration to trigger processing (seconds)")
    parser.add_argument("--threshold", "-t", type=float, default=0.01,
                       help="Audio threshold for silence detection")
    
    args = parser.parse_args()
    
    podcast = VoicePodcast(
        whisper_model=args.model,
        silence_duration=args.silence,
        silence_threshold=args.threshold
    )
    
    await podcast.run()


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🌌 AZIREM VOICE PODCAST")
    print("=" * 60)
    print()
    
    asyncio.run(main())
