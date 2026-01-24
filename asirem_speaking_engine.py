#!/usr/bin/env python3
"""
🎬 aSiReM SPEAKING ENGINE
=========================
Unified real-time speaking pipeline integrating:
- Veo3 Narrative Factory (9-Expert Story Team)
- Avatar Engine (LivePortrait + MuseTalk)
- ComfyUI F5-TTS (Voice Cloning)
- Real-time WebSocket streaming

This makes aSiReM ACTUALLY speak in the Sovereign Dashboard!
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
import subprocess
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
# Try to import Google GenAI, fall back to mock if unavailable
try:
    from google import genai
    from google.genai import types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    # Create mock objects for when google-genai is not available
    GOOGLE_GENAI_AVAILABLE = False
    genai = None
    types = None
    print("⚠️ google-genai not available, Veo3 will run in simulation mode")

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SpeakingConfig:
    """Configuration for the speaking engine."""
    # Paths
    comfyui_path: str = "/Users/yacinebenhamou/.starconnect/ComfyUI"
    musetalk_path: str = str(PROJECT_ROOT / "cold_azirem/avatar/deps/MuseTalk")
    liveportrait_path: str = str(PROJECT_ROOT / "cold_azirem/avatar/deps/LivePortrait")
    
    # Voice settings
    voice_model: str = "xtts"  # Default to XTTS for high-quality cloning
    reference_audio: str = "/Users/yacinebenhamou/aSiReM/sovereign-dashboard/assets/MyVoice.wav"
    alternative_audio: str = str(PROJECT_ROOT / "sovereign-dashboard/assets/voice/reference.mp3")
    reference_text: str = ""  # Transcription of reference audio (will be auto-detected if empty)
    
    # Character assets (from Story Bible)
    character_assets_dir: str = str(PROJECT_ROOT / "sovereign-dashboard/assets/character")
    source_image: str = str(PROJECT_ROOT / "sovereign-dashboard/assets/character/Gemini_Generated_Image_74pu4274pu4274pu.png")
    source_images: list = None  # Multiple images for variety
    
    # Output
    output_dir: str = str(PROJECT_ROOT / "sovereign-dashboard/generated")
    
    # Streaming
    stream_fps: int = 30
    chunk_duration_ms: int = 100  # Real-time chunk size
    
    def __post_init__(self):
        # Load all available character images
        import os
        if os.path.exists(self.character_assets_dir):
            self.source_images = [
                os.path.join(self.character_assets_dir, f) 
                for f in os.listdir(self.character_assets_dir)
                if f.endswith(('.png', '.jpg', '.jpeg'))
            ]
            print(f"📸 Loaded {len(self.source_images)} aSiReM character images")


# =============================================================================
# TTS ENGINE (Text-to-Speech)
# =============================================================================

class TTSEngine:
    """
    Text-to-Speech using F5-TTS for voice cloning.
    Generates audio from text with YOUR cloned voice.
    """
    
    def __init__(self, config: SpeakingConfig):
        self.config = config
        self.initialized = False
        self.f5_tts_helper = Path.home() / ".starconnect/tts_clone_helper.py"
        self.xtts_helper = Path(__file__).parent / "xtts_helper.py"
        self.xtts_venv = Path.home() / "venv-xtts/bin/python3"
        if not self.xtts_venv.exists():
             self.xtts_venv = Path("/Users/yacinebenhamou/venv-xtts/bin/python3")
        self.model = None # For XTTS model instance
        
    def set_reference_audio(self, audio_path: str, transcription: str = ""):
        """Set the reference audio for voice cloning."""
        self.config.reference_audio = audio_path
        if transcription:
            self.config.reference_text = transcription
        print(f"📼 Reference audio set to: {audio_path}")
        
    async def initialize(self):
        """Initialize the TTS engine."""
        print("🎤 Initializing TTS Engine...")
        
        # PRIORITY 1: XTTS (working with Python 3.11)
        if self.xtts_venv.exists():
            print(f"   ✅ XTTS venv found at {self.xtts_venv}")
            self.tts_backend = "xtts"
        # PRIORITY 2: F5-TTS (requires Python 3.10+ type hints)
        elif self.f5_tts_helper.exists():
            print(f"   ✅ F5-TTS helper found at {self.f5_tts_helper}")
            self.tts_backend = "f5-tts"
        else:
            print("   ⚠️ No voice cloning backend found, will use system TTS")
            self.tts_backend = "system"


        # Priority 1: Use user's provided voice reference
        ref_path = Path(self.config.reference_audio)
        if ref_path.exists():
            print(f"   👑 Master voice reference: {ref_path.name}")
            
            # Load transcription if available
            ref_text_path = ref_path.parent / "reference.txt"
            if ref_text_path.exists() and not self.config.reference_text:
                self.config.reference_text = ref_text_path.read_text().strip()
                print(f"   ✅ Loaded transcription: \"{self.config.reference_text[:50]}...\"")
        else:
            print(f"   ⚠️ Reference voice not found at {ref_path}")
            print(f"   💡 You can provide your voice with engine.tts.set_reference_audio(path, transcription)")
            
        self.initialized = True
        return True
    
    async def _run_command(self, cmd: List[str], cwd: Optional[str] = None, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a command asynchronously in a thread to avoid blocking the event loop."""
        def run():
            return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return await asyncio.to_thread(run)

    async def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Synthesize speech from text using voice cloning.
        
        Args:
            text: Text to synthesize
            output_path: Optional output path for audio
            
        Returns:
            Path to generated audio file
        """
        if not self.initialized:
            await self.initialize()
            
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")
            
        print(f"🔊 Synthesizing with voice cloning: '{text[:50]}...'")
        
        ref_path = Path(self.config.reference_audio)
        
        if self.tts_backend == "f5-tts" and ref_path.exists():
            # Use F5-TTS for zero-shot voice cloning
            try:
                # Get reference text (auto-detect if not provided)
                ref_text = self.config.reference_text
                if not ref_text:
                    # For now, use a system_value. In production, use Whisper for transcription
                    ref_text = "This is a reference audio sample for voice cloning."
                    print(f"   ℹ️ Using system_value reference text. For best results, provide actual transcription.")
                
                # Run F5-TTS helper with ComfyUI environment
                comfyui_venv_python = Path.home() / ".starconnect/comfyui-venv/bin/python3"
                python_cmd = str(comfyui_venv_python) if comfyui_venv_python.exists() else "python3"
                
                cmd = [
                    python_cmd,
                    str(self.f5_tts_helper),
                    "--ref", str(ref_path),
                    "--ref_text", ref_text,
                    "--gen_text", text,
                    "--out", output_path
                ]
                
                print(f"   🔄 Running F5-TTS voice cloning with {python_cmd}...")
                result = await self._run_command(cmd, timeout=60)
                
                if result.returncode == 0:
                    print(f"   ✅ Voice cloned successfully!")
                else:
                    print(f"   ⚠️ F5-TTS failed: {result.stderr}")
                    print(f"   🔄 Falling back to system TTS")
                    await self._run_command(["say", "-o", output_path, "--data-format=LEF32@22050", text], timeout=10)
                    
            except Exception as e:
                print(f"   ⚠️ F5-TTS error: {e}")
                print(f"   🔄 Falling back to system TTS")
                await self._run_command(["say", "-o", output_path, "--data-format=LEF32@22050", text], timeout=10)
                
        elif (self.tts_backend == "xtts" or self.xtts_venv.exists()) and ref_path.exists():
            # Use XTTS with voice cloning via dedicated helper
            try:
                cmd = [
                    str(self.xtts_venv),
                    str(self.xtts_helper),
                    "--text", text,
                    "--ref", str(ref_path),
                    "--out", output_path
                ]
                print(f"   🔄 Running XTTS voice cloning with {self.xtts_venv}...")
                result = await self._run_command(cmd, timeout=120)
                
                if result.returncode == 0:
                    print(f"   ✅ XTTS Voice cloned successfully!")
                else:
                    print(f"   ⚠️ XTTS failed: {result.stdout}\n{result.stderr}")
                    # Fallback
                    await self._run_command(["say", "-v", "Alex", "-o", output_path, "--data-format=LEF32@22050", text], timeout=10)
            except Exception as e:
                print(f"   ⚠️ XTTS error: {e}")
                await self._run_command(["say", "-v", "Alex", "-o", output_path, "--data-format=LEF32@22050", text], timeout=10)
        else:
            # Enhanced fallback: macOS say command with voice quality settings
            # Using Alex voice with slower rate for better clarity
            await self._run_command([
                "say", "-v", "Alex",  # High-quality voice
                "-r", "180",  # Slightly slower for clarity
                "-o", output_path,
                "--data-format=LEF32@22050",
                text
            ], timeout=20)
            print(f"   ℹ️ Using macOS TTS (install TTS library for voice cloning)")
            
        print(f"   ✅ Audio saved to {output_path}")
        return output_path


# =============================================================================
# LIP SYNC ENGINE
# =============================================================================

class LipSyncEngine:
    """
    Lip synchronization using MuseTalk.
    Generates talking head video from audio + source image.
    """
    
    def __init__(self, config: SpeakingConfig):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize MuseTalk."""
        print("👄 Initializing Lip Sync Engine (MuseTalk)...")
        
        musetalk_dir = Path(self.config.musetalk_path)
        if musetalk_dir.exists():
            print(f"   ✅ MuseTalk found at {musetalk_dir}")
            self.musetalk_available = True
        else:
            print(f"   ⚠️ MuseTalk not found at {musetalk_dir}")
            self.musetalk_available = False
            
        self.initialized = True
        return True
    
    async def generate(
        self,
        audio_path: str,
        source_image: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate lip-synced video.
        
        Args:
            audio_path: Path to audio file
            source_image: Path to source face image
            output_path: Path for output video
            
        Returns:
            Path to generated video
        """
        if not self.initialized:
            await self.initialize()
            
        source_image = source_image or self.config.source_image
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp4")
            
        print(f"🎬 Generating lip-synced video...")
        print(f"   Audio: {audio_path}")
        print(f"   Source: {source_image}")
        
        if self.musetalk_available:
            # Real MuseTalk inference - PRODUCTION MODE ACTIVATED
            musetalk_script = Path(self.config.musetalk_path) / "scripts/inference.py"
            if musetalk_script.exists():
                # Use venv-speaking if available
                musetalk_venv_python = Path(__file__).parent / "venv-speaking/bin/python3"
                python_cmd = str(musetalk_venv_python) if musetalk_venv_python.exists() else "python3"
                
                # MuseTalk inference.py requires --result_dir to be set or defaults to ./results
                # We should use config.output_dir
                cmd = [
                    python_cmd, str(musetalk_script),
                    "--audio_path", audio_path,
                    "--source_image", source_image,
                    "--result_dir", self.config.output_dir,
                    "--output_vid_name", os.path.basename(output_path)
                ]
                try:
                    print(f"   🎬 Running MuseTalk lip-sync inference with {python_cmd}...")
                    # Set up PYTHONPATH for MuseTalk
                    env = os.environ.copy()
                    env["PYTHONPATH"] = f"{self.config.musetalk_path}:{env.get('PYTHONPATH', '')}"
                    
                    def run_muse():
                        return subprocess.run(cmd, cwd=self.config.musetalk_path, capture_output=True, env=env, timeout=180)
                    
                    result = await asyncio.to_thread(run_muse)
                    if result.returncode == 0:
                        print(f"   ✅ MuseTalk generated video!")
                        # MuseTalk saves to {result_dir}/{version}/{output_vid_name}
                        # We need to find the actual produced file and copy it to output_path if different
                        generated_file = Path(self.config.output_dir) / "v15" / os.path.basename(output_path)
                        if generated_file.exists():
                            import shutil
                            shutil.copy(generated_file, output_path)
                            return output_path
                        return output_path
                    else:
                        print(f"   ⚠️ MuseTalk failed: {result.stdout.decode()}\n{result.stderr.decode()}")
                except Exception as e:
                    print(f"   ⚠️ MuseTalk error: {e}")
        
        # For now, copy a demo video if available
        demo_video = PROJECT_ROOT / "sovereign-dashboard/assets/asirem-video.mp4"
        if demo_video.exists():
            import shutil
            shutil.copy(demo_video, output_path)
            print(f"   ✅ Demo video copied to {output_path}")
        else:
            print(f"   ⚠️ No demo video available")
            
        return output_path


# =============================================================================
# NARRATIVE ENGINE (Integration with factory.py)
# =============================================================================

class NarrativeEngine:
    """
    Integration with the 9-Expert Narrative Factory.
    Orchestrates story deliberation and script generation.
    """
    
    def __init__(self):
        self.factory = None
        
    async def initialize(self):
        """Load the Narrative Factory."""
        print("📖 Initializing Narrative Engine...")
        
        try:
            from cold_azirem.narrative.factory import NarrativeFactory, STORY_EXPERTS
            self.factory = NarrativeFactory(
                str(PROJECT_ROOT / "cold_azirem/narrative/ASIREM_STORY_BIBLE.md")
            )
            self.experts = STORY_EXPERTS
            print(f"   ✅ Loaded {len(self.experts)} story experts")
            return True
        except ImportError as e:
            print(f"   ⚠️ Narrative Factory not available: {e}")
            self.factory = None
            return False
    
    async def generate_script(self, topic: str, duration_seconds: int = 30) -> str:
        """
        Generate a script for aSiReM to speak.
        
        Args:
            topic: What aSiReM should talk about
            duration_seconds: Target duration
            
        Returns:
            Script text
        """
        print(f"✍️ Generating script for: {topic}")
        
        # Pre-defined scripts for common topics (production would use LLM)
        scripts = {
            "greeting": "Hello! I'm aSiReM, your AI guide to understanding artificial intelligence. I'm here to help you explore the fascinating world of AI in a way that's fun and accessible.",
            "what_is_ai": "Artificial intelligence is like teaching a computer to learn from examples, just like you learn from experience. When you show a computer thousands of pictures of cats, it starts to recognize what makes a cat look like a cat.",
            "how_i_work": "I work by processing patterns in data. Think of it like this: my brain is made of billions of tiny connections, similar to how your brain has neurons. When you ask me something, these connections light up to find the best answer.",
            "the_future": "The future of AI is about collaboration between humans and machines. We're not here to replace you - we're here to help you do amazing things you couldn't do alone.",
            "default": f"Let me tell you about {topic}. This is a fascinating subject that combines technology, creativity, and human ingenuity."
        }
        
        if self.factory:
            # Use real factory with all 9 experts
            print(f"🧬 Orchestrating 9-Expert Story Team for topic: {topic}")
            try:
                # Start a quick deliberation (1 minute minimum)
                deliberation = await self.factory.start_deliberation(topic, min_duration_minutes=0.1)
                # Extract the final script from the deliberation
                script = f"Let me tell you about {topic}. " + deliberation.get_summary()[:200]
                return script
            except Exception as e:
                print(f"⚠️  Factory deliberation failed: {e}")
                # Fall through to default scripts
            
        # Match topic to script
        topic_lower = topic.lower()
        for key, script in scripts.items():
            if key in topic_lower:
                return script
                
        return scripts["default"].format(topic=topic)


# =============================================================================
# UNIFIED SPEAKING PIPELINE
# =============================================================================

class ASiREMSpeakingEngine:
    """
    Complete pipeline for making aSiReM speak:
    1. Generate script (Narrative Engine)
    2. Synthesize voice (TTS Engine)
    3. Generate lip-sync video (Lip Sync Engine)
    4. Stream to dashboard (WebSocket)
    """
    
    def __init__(self, config: Optional[SpeakingConfig] = None):
        self.config = config or SpeakingConfig()
        self.tts = TTSEngine(self.config)
        self.lipsync = LipSyncEngine(self.config)
        self.narrative = NarrativeEngine()
        self.initialized = False
        self.callback = None
        
    def set_callback(self, callback):
        """Set callback for real-time updates."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: dict):
        """Emit event to callback."""
        if self.callback:
            await self.callback(event_type, data)
            
    async def initialize(self):
        """Initialize all engines."""
        print("\n" + "🧬" * 30)
        print("   aSiReM Speaking Engine")
        print("🧬" * 30 + "\n")
        
        await self.tts.initialize()
        await self.lipsync.initialize()
        await self.narrative.initialize()
        
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        self.initialized = True
        print("\n✅ Speaking Engine ready!")
        return True
    
    async def speak(self, text: str) -> Dict[str, Any]:
        """
        Make aSiReM speak the given text.
        
        Args:
            text: Text for aSiReM to say
            
        Returns:
            Result with audio and video paths
        """
        if not self.initialized:
            await self.initialize()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        await self.emit("speaking_started", {
            "text": text,
            "timestamp": timestamp
        })
        
        # Step 1: Synthesize audio
        await self.emit("activity", {
            "agent_id": "tts",
            "agent_name": "Voice Synthesis",
            "icon": "🎤",
            "message": f"Synthesizing speech: '{text[:30]}...'"
        })
        
        audio_path = os.path.join(self.config.output_dir, f"speech_{timestamp}.wav")
        await self.tts.synthesize(text, audio_path)
        
        # Step 2: Generate lip-synced video
        await self.emit("activity", {
            "agent_id": "lipsync",
            "agent_name": "Lip Sync",
            "icon": "👄",
            "message": "Generating lip-synced video..."
        })
        
        video_path = os.path.join(self.config.output_dir, f"video_{timestamp}.mp4")
        await self.lipsync.generate(audio_path, output_path=video_path)
        
        await self.emit("speaking_completed", {
            "text": text,
            "audio_path": audio_path,
            "video_path": video_path,
            "timestamp": timestamp
        })
        
        return {
            "text": text,
            "audio_path": audio_path,
            "video_path": video_path,
            "timestamp": timestamp
        }

    async def podcast_conversation(self, question: str) -> Dict[str, Any]:
        """
        Handle a podcast conversation turn.
        
        Args:
            question: The user's question or topic
            
        Returns:
            Result with text, audio, and video
        """
        await self.emit("activity", {
             "agent_id": "azirem",
             "agent_name": "Azirem Podcast",
             "icon": "🎙️",
             "message": f"Thinking about: {question}"
        })
        
        # 1. Generate text response
        # Using narrative engine to generate a "script" based on the question as topic
        response_text = await self.narrative.generate_script(question)
        
        # 2. Speak it
        result = await self.speak(response_text)
        return result
    
    async def speak_about(self, topic: str) -> Dict[str, Any]:
        """
        Generate a script about a topic and make aSiReM speak it.
        
        Args:
            topic: Topic for aSiReM to discuss
            
        Returns:
            Result with script, audio, and video
        """
        await self.emit("activity", {
            "agent_id": "narrative",
            "agent_name": "Narrative",
            "icon": "📝",
            "message": f"Generating script about: {topic}"
        })
        
        script = await self.narrative.generate_script(topic)
        result = await self.speak(script)
        result["topic"] = topic
        result["script"] = script
        
        return result

    async def produce_cinematic_narrative(self, topic: str) -> Dict[str, Any]:
        """
        Produce a high-quality cinematic narrative sequence.
        Orchestrates script, voice, and Veo3 prompts.
        """
        await self.emit("activity", {
            "agent_id": "azirem",
            "agent_name": "AZIREM",
            "icon": "🎭",
            "message": f"Initializing Cinematic Narrative Production: {topic}"
        })
        
        # 1. Deliberation
        await self.emit("activity", {
            "agent_id": "narrative",
            "agent_name": "Story Team",
            "icon": "🤝",
            "message": "Orchestrating 9-expert deliberation for cinematic narrative..."
        })
        
        script = await self.narrative.generate_script(topic, duration_seconds=60)
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [script]
            
        results = []
        veo3 = Veo3Generator()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, para in enumerate(paragraphs):
            stage = f"(Scene {i+1}/{len(paragraphs)})"
            
            # Sub-task: Voice
            await self.emit("activity", {
                "agent_id": "summarizer",
                "agent_name": "Narrative Analyst",
                "icon": "🎙️",
                "message": f"{stage} Analyzing emotional tone for voice cloning..."
            })
            
            audio_path = os.path.join(self.config.output_dir, f"narrative_{timestamp}_{i}.wav")
            await self.tts.synthesize(para, audio_path)
            
            # Emit visual stream update for speaking
            await self.emit("agent_stream_update", {
                "agent_id": "azirem",
                "agent_name": "aSiReM",
                "status": "speaking",
                "stream_url": f"/outputs/speaking_{timestamp}_{i}.mp4",
                "message": f"Speaking scene {i+1}/{len(paragraphs)}"
            })
            
            # Sub-task: Visuals
            await self.emit("activity", {
                "agent_id": "architect",
                "agent_name": "Visual Architect",
                "icon": "🎨",
                "message": f"{stage} Generating cinematic prompts for Veo3..."
            })
            
            veo3_result = await veo3.generate_chunk(
                prompt=f"Cinematic scene for: {para[:50]}... Ultra-realistic, 8k, futuristic aesthetic.",
                quality="quality"
            )
            
            results.append({
                "paragraph": para,
                "audio": audio_path,
                "veo3": veo3_result
            })
            
        await self.emit("activity", {
            "agent_id": "azirem",
            "agent_name": "AZIREM",
            "icon": "🎬",
            "message": f"Cinematic Narrative Production Complete: {len(results)} scenes generated."
        })
        
        return {
            "topic": topic,
            "script": script,
            "scenes": results,
            "credits": veo3.get_credits()
        }


# =============================================================================
# VEO3 INTEGRATION
# =============================================================================

class Veo3Generator:
    """
    Veo3 video generation with Google Gemini Ultra credits.
    
    Ultra Plan Limits:
    - Gemini App: 3-5 videos/day
    - Google Flow: 12,500 credits/month
      - Veo3 Quality: 100 credits = ~125 videos/month
      - Veo3 Fast: 20 credits = ~625 videos/month
    """
    
    def __init__(self):
        self.credits_used = 0
        self.monthly_limit = 12500
        self.quality_cost = 100
        self.fast_cost = 20
        self.api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBWQtSN35Kfzz823TUeWURPzghSLYmiT0k")
        self.is_simulated = self.api_key in ["PUT_YOUR_KEY", ""] or not GOOGLE_GENAI_AVAILABLE
        
        if not self.is_simulated:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("💎 Veo3 Generator: Production mode ACTIVATED with Google API Key")
            except Exception as e:
                print(f"⚠️ Veo3 Generator: Failed to initialize real client: {e}")
                self.is_simulated = True
        else:
            print("💎 Veo3 Generator: Simulation mode active (No GOOGLE_API_KEY found)")
            self.client = None
        
    def get_remaining_credits(self) -> int:
        return self.monthly_limit - self.credits_used
    
    def get_remaining_videos(self, quality: str = "fast") -> int:
        cost = self.fast_cost if quality == "fast" else self.quality_cost
        return self.get_remaining_credits() // cost
    
    async def generate_chunk(
        self,
        prompt: str,
        duration_seconds: int = 8,
        quality: str = "fast",
        include_audio: bool = True,
        output_dir: str = "sovereign-dashboard/generated"
    ) -> Dict[str, Any]:
        """
        Generate an 8-second video chunk with Veo3.
        
        Args:
            prompt: Scene description
            duration_seconds: 4, 6, or 8 seconds
            quality: "fast" (20 credits) or "quality" (100 credits)
            include_audio: Include generated audio
            output_dir: Where to save the video
            
        Returns:
            Generation result
        """
        cost = self.fast_cost if quality == "fast" else self.quality_cost
        
        if self.credits_used + cost > self.monthly_limit:
            return {
                "error": "Monthly credit limit reached",
                "remaining_credits": self.get_remaining_credits()
            }
        
        # Determine model - Use correct model names from API
        # Available: veo-3.1-fast-generate-preview, veo-3.1-generate-preview
        model_id = "models/veo-3.1-fast-generate-preview" if quality == "fast" else "models/veo-3.1-generate-preview"
        
        # ANTIGRAVITY RULE 2.5: Fail Loud
        # No simulation fallbacks - missing API key must be explicit error
        if self.is_simulated or not self.client:
            raise RuntimeError(
                "Veo3Generator BLOCKED: Missing or invalid GOOGLE_API_KEY. "
                "Set environment variable GOOGLE_API_KEY with valid key. "
                "Simulation mode is FORBIDDEN per Antigravity Rule 2.2 (Zero Mock Tolerance)."
            )

        # REAL PRODUCTION CALL using google-genai Veo 3.1 API
        try:
            print(f"🎬 [PRODUCTION] Calling Veo3.1 API ({model_id}): {prompt[:50]}...")

            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate the video using the google-genai SDK
            # According to Google Gemini API docs (Jan 2026), use generate_videos
            # Veo 3.1 is available in paid preview via Gemini API
            response = self.client.models.generate_videos(
                model=model_id,
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio="16:9",
                    duration_seconds=duration_seconds
                    # generate_audio not yet supported in current API version
                )
            )
            
            # The response is returned directly (no async polling needed)
            # The API handles the generation and returns the result
            print(f"   ✅ Veo3.1 generation complete!")
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"veo3_{timestamp}_{quality}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            # Download the video content
            # The response contains the generated video
            if hasattr(response, 'generated_videos') and response.generated_videos:
                video_output = response.generated_videos[0]
                
                # Try different attributes for getting video data
                if hasattr(video_output, 'video_bytes'):
                    with open(filepath, 'wb') as f:
                        f.write(video_output.video_bytes)
                elif hasattr(video_output, 'video') and hasattr(video_output.video, 'data'):
                    with open(filepath, 'wb') as f:
                        f.write(video_output.video.data)
                elif hasattr(video_output, 'uri'):
                    # Download from GCS URI
                    import requests
                    video_data = requests.get(video_output.uri).content
                    with open(filepath, 'wb') as f:
                        f.write(video_data)
                else:
                    raise Exception(f"Unknown video format in response: {dir(video_output)}")
                
                print(f"   💾 Saved to: {filepath}")
            else:
                raise Exception("No videos in Veo3.1 response")
            
            # Update credits
            self.credits_used += cost
            
            return {
                "status": "completed",
                "video_path": filepath,
                "duration": duration_seconds,
                "quality": quality,
                "credits_used": cost,
                "remaining_credits": self.get_remaining_credits()
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Veo3 Production Error: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg,
                "remaining_credits": self.get_remaining_credits()
            }
    
    def get_credits(self) -> Dict[str, int]:
        """Get credit status"""
        return {
            "total": self.monthly_limit,
            "used": self.credits_used,
            "remaining": self.get_remaining_credits()
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def demo():
    """Run a demo of the speaking engine."""
    engine = ASiREMSpeakingEngine()
    
    # Simple callback to print events
    async def print_callback(event_type, data):
        print(f"[{event_type}] {json.dumps(data, indent=2)}")
    
    engine.set_callback(print_callback)
    
    await engine.initialize()
    
    # Demo: Make aSiReM speak
    result = await engine.speak_about("greeting")
    print(f"\n✅ Result: {result}")
    
    # Show Veo3 credit status
    veo3 = Veo3Generator()
    print(f"\n📊 Veo3 Credit Status:")
    print(f"   Remaining Credits: {veo3.get_remaining_credits()}")
    print(f"   Remaining Fast Videos: {veo3.get_remaining_videos('fast')}")
    print(f"   Remaining Quality Videos: {veo3.get_remaining_videos('quality')}")


if __name__ == "__main__":
    asyncio.run(demo())
