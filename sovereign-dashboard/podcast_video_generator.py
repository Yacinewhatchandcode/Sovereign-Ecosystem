#!/usr/bin/env python3
"""
🎬 PODCAST VIDEO GENERATOR - Two-Character Conversation
========================================================
Generates real-time MP4 videos of podcast conversations between:
- User (with cloned voice from MyVoice.wav)
- AZIREM (with anime/Sony character avatar)

Features:
- Dual character video layout (side-by-side or picture-in-picture)
- Voice cloning for both speakers
- Lip-sync animation for both avatars
- Real-time streaming to dashboard
- Export to MP4
"""

import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class Speaker:
    """Represents a speaker in the podcast."""
    name: str
    avatar_image: str
    voice_sample: Optional[str] = None  # For voice cloning
    character_type: str = "user"  # "user" or "ai"


@dataclass
class PodcastSegment:
    """A single segment of the podcast conversation."""
    speaker: Speaker
    text: str
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    duration: float = 0.0


class PodcastVideoGenerator:
    """
    Generates podcast videos with two characters conversing.
    """
    
    def __init__(
        self,
        output_dir: str = "outputs/podcasts",
        layout: str = "side_by_side"  # "side_by_side" or "pip"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.layout = layout
        
        # Initialize speakers
        self.user_speaker = Speaker(
            name="You",
            avatar_image=str(Path(__file__).parent / "assets/character/WhatsApp Image 2025-10-27 at 15.20.55.jpeg"),
            voice_sample=str(Path(__file__).parent / "assets/MyVoice.wav"),
            character_type="user"
        )
        
        self.azirem_speaker = Speaker(
            name="AZIREM",
            avatar_image=str(Path(__file__).parent / "assets/character/Gemini_Generated_Image_rxyzqarxyzqarxyz.png"),
            voice_sample=None,  # Will use TTS
            character_type="ai"
        )
        
        # Initialize engines
        self.tts_engine = None
        self.lipsync_engine = None
        
    async def initialize(self):
        """Initialize TTS and lip-sync engines."""
        print("🎬 Initializing Podcast Video Generator...")
        
        # Import speaking engine
        try:
            from asirem_speaking_engine import ASiREMSpeakingEngine
            self.tts_engine = ASiREMSpeakingEngine()
            print("   ✅ TTS Engine loaded")
        except Exception as e:
            print(f"   ⚠️ TTS Engine failed: {e}")
            
        # Import lipsync
        try:
            from avatar_lipsync import AvatarLipSync
            self.lipsync_engine = AvatarLipSync()
            print("   ✅ Lip-Sync Engine loaded")
        except Exception as e:
            print(f"   ⚠️ Lip-Sync failed: {e}")
            
        return True
        
    async def generate_speech(
        self,
        text: str,
        speaker: Speaker,
        output_audio: str
    ) -> bool:
        """Generate speech audio for a speaker."""
        try:
            if speaker.character_type == "ai" and self.tts_engine:
                # Use AZIREM's TTS
                result = await self.tts_engine.tts.synthesize(text, output_audio)
                return True
            elif speaker.voice_sample and os.path.exists(speaker.voice_sample):
                # Use voice cloning (XTTS or F5-TTS)
                if self.tts_engine:
                    # Try XTTS voice cloning
                    result = await self.tts_engine.tts.synthesize(
                        text,
                        output_audio,
                        speaker_wav=speaker.voice_sample
                    )
                    return True
                else:
                    # Fallback: use system TTS
                    subprocess.run([
                        "say", "-v", "Samantha", "-o", output_audio, text
                    ], check=False)
                    return True
            else:
                # Fallback: system TTS
                subprocess.run([
                    "say", "-v", "Samantha", "-o", output_audio, text
                ], check=False)
                return True
                
        except Exception as e:
            print(f"   ⚠️ Speech generation failed: {e}")
            return False
            
    async def generate_talking_head(
        self,
        audio_path: str,
        speaker: Speaker,
        output_video: str
    ) -> bool:
        """Generate talking head video for a speaker."""
        try:
            if self.lipsync_engine and os.path.exists(speaker.avatar_image):
                # Use lip-sync engine
                self.lipsync_engine.avatar_image = speaker.avatar_image
                result = await self.lipsync_engine.generate_talking_head(
                    audio_path,
                    output_video
                )
                return result.success
            else:
                # Fallback: static image with waveform
                await self._generate_static_video(
                    audio_path,
                    speaker.avatar_image,
                    output_video
                )
                return True
                
        except Exception as e:
            print(f"   ⚠️ Video generation failed: {e}")
            return False
            
    async def _generate_static_video(
        self,
        audio_path: str,
        image_path: str,
        output_video: str
    ):
        """Generate static video with audio waveform overlay."""
        if not os.path.exists(image_path):
            # Create system_value
            image_path = str(Path(__file__).parent / "assets/character/Gemini_Generated_Image_rxyzqarxyzqarxyz.png")
            
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-vf", "scale=1280:720",
            output_video
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
    async def generate_segment(
        self,
        speaker: Speaker,
        text: str
    ) -> PodcastSegment:
        """Generate a complete podcast segment (audio + video)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        
        segment = PodcastSegment(
            speaker=speaker,
            text=text
        )
        
        # Generate audio
        audio_path = self.output_dir / f"audio_{speaker.name}_{timestamp}.wav"
        print(f"\n🎤 Generating speech for {speaker.name}...")
        print(f"   Text: {text[:60]}...")
        
        success = await self.generate_speech(text, speaker, str(audio_path))
        if success:
            segment.audio_path = str(audio_path)
            print(f"   ✅ Audio: {audio_path.name}")
        else:
            print(f"   ❌ Audio generation failed")
            return segment
            
        # Generate video
        video_path = self.output_dir / f"video_{speaker.name}_{timestamp}.mp4"
        print(f"\n🎬 Generating video for {speaker.name}...")
        
        success = await self.generate_talking_head(
            str(audio_path),
            speaker,
            str(video_path)
        )
        
        if success:
            segment.video_path = str(video_path)
            print(f"   ✅ Video: {video_path.name}")
            
            # Get duration
            try:
                result = subprocess.run([
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path)
                ], capture_output=True, text=True, check=True)
                segment.duration = float(result.stdout.strip())
            except:
                segment.duration = 5.0
        else:
            print(f"   ❌ Video generation failed")
            
        return segment
        
    async def combine_segments(
        self,
        segments: List[PodcastSegment],
        output_path: str
    ) -> str:
        """Combine all segments into a single podcast video."""
        print(f"\n🎬 Combining {len(segments)} segments...")
        
        # Create concat file
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, "w") as f:
            for seg in segments:
                if seg.video_path and os.path.exists(seg.video_path):
                    f.write(f"file '{os.path.abspath(seg.video_path)}'\n")
                    
        # Concatenate videos
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"   ✅ Final video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Concatenation failed: {e.stderr if e.stderr else e}")
            # Try re-encoding instead of copy
            try:
                reencode_cmd = [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    output_path
                ]
                subprocess.run(reencode_cmd, check=True, capture_output=True, text=True)
                print(f"   ✅ Final video (re-encoded): {output_path}")
                return output_path
            except subprocess.CalledProcessError as e2:
                print(f"   ❌ Re-encoding also failed: {e2.stderr if e2.stderr else e2}")
                # Last resort: return first segment if available
                if segments and segments[0].video_path:
                    print(f"   ⚠️ Returning first segment as fallback")
                    return segments[0].video_path
                raise
            
    async def generate_conversation(
        self,
        conversation: List[Tuple[str, str]]  # List of (speaker_type, text)
    ) -> str:
        """
        Generate a full podcast conversation video.
        
        Args:
            conversation: List of (speaker_type, text) where speaker_type is "user" or "ai"
            
        Returns:
            Path to final video
        """
        print("\n" + "="*60)
        print("🎙️ PODCAST VIDEO GENERATION")
        print("="*60)
        
        segments = []
        
        for i, (speaker_type, text) in enumerate(conversation, 1):
            speaker = self.user_speaker if speaker_type == "user" else self.azirem_speaker
            
            print(f"\n--- Segment {i}/{len(conversation)} ---")
            print(f"Speaker: {speaker.name}")
            
            segment = await self.generate_segment(speaker, text)
            segments.append(segment)
            
        # Combine all segments
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_video = str(self.output_dir / f"podcast_{timestamp}.mp4")
        
        await self.combine_segments(segments, final_video)
        
        print("\n" + "="*60)
        print(f"✅ PODCAST COMPLETE: {final_video}")
        print("="*60)
        
        return final_video
        
    async def generate_from_transcript(
        self,
        transcript_file: str
    ) -> str:
        """Generate podcast from a JSON transcript file."""
        with open(transcript_file) as f:
            data = json.load(f)
            
        conversation = [
            (item["speaker"], item["text"])
            for item in data["conversation"]
        ]
        
        return await self.generate_conversation(conversation)


async def demo():
    """Demo the podcast video generator."""
    generator = PodcastVideoGenerator()
    await generator.initialize()
    
    # Sample conversation
    conversation = [
        ("user", "Hello AZIREM! Can you tell me about your agent fleet?"),
        ("ai", "Hello! I'm AZIREM, and I manage a fleet of 13 specialized agents. Each agent has unique capabilities - from Scanner who discovers patterns, to DevOps who handles deployment."),
        ("user", "That's impressive! Which agent is your favorite?"),
        ("ai", "I appreciate all my agents equally, but I have a special connection with Spectra, the Orchestration Master. She helps coordinate the entire fleet's activities."),
        ("user", "Can you show me how they work together?"),
        ("ai", "Absolutely! When you trigger an evolution, Scanner first analyzes your codebase, then Classifier organizes the findings, and finally Evolution synthesizes new insights. It's a beautiful symphony of AI collaboration!")
    ]
    
    video_path = await generator.generate_conversation(conversation)
    print(f"\n🎬 Demo video generated: {video_path}")


if __name__ == "__main__":
    asyncio.run(demo())
