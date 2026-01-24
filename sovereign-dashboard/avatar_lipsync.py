#!/usr/bin/env python3
"""
👄 AVATAR LIP-SYNC SYSTEM - MuseTalk/LivePortrait Integration
==============================================================
Generates talking head videos with lip-sync from audio.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
import tempfile
import json


@dataclass
class LipSyncResult:
    """Result from lip-sync generation."""
    video_path: str
    audio_path: str
    duration_seconds: float
    success: bool
    error: Optional[str] = None


class AvatarLipSync:
    """
    Avatar lip-sync using MuseTalk or LivePortrait.
    
    Generates talking head videos synchronized with audio.
    """
    
    def __init__(
        self,
        avatar_image: str = None,
        backend: str = "musetalk"  # or "liveportrait"
    ):
        self.avatar_image = avatar_image or self._get_default_avatar()
        self.backend = backend
        self.musetalk_available = self._check_musetalk()
        self.liveportrait_available = self._check_liveportrait()
        
    def _get_default_avatar(self) -> str:
        """Get default avatar image."""
        # Could use MyVoice.wav's speaker or a default image
        return "/tmp/azirem_avatar.jpg"
        
    def _check_musetalk(self) -> bool:
        """Check if MuseTalk is available."""
        try:
            result = subprocess.run(
                ['which', 'musetalk'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
            
    def _check_liveportrait(self) -> bool:
        """Check if LivePortrait is available."""
        try:
            result = subprocess.run(
                ['which', 'liveportrait'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
            
    async def generate_talking_head(
        self,
        audio_path: str,
        output_path: str = None
    ) -> LipSyncResult:
        """
        Generate talking head video from audio.
        
        Args:
            audio_path: Path to audio file
            output_path: Optional output video path
            
        Returns:
            LipSyncResult with video path
        """
        if not Path(audio_path).exists():
            return LipSyncResult(
                video_path="",
                audio_path=audio_path,
                duration_seconds=0,
                success=False,
                error=f"Audio file not found: {audio_path}"
            )
            
        if not output_path:
            output_path = str(Path(tempfile.gettempdir()) / f"avatar_{Path(audio_path).stem}.mp4")
            
        # Try MuseTalk first
        if self.backend == "musetalk" and self.musetalk_available:
            return await self._generate_musetalk(audio_path, output_path)
        # Fallback to LivePortrait
        elif self.backend == "liveportrait" and self.liveportrait_available:
            return await self._generate_liveportrait(audio_path, output_path)
        else:
            # Fallback: create simple video with waveform
            return await self._generate_waveform_video(audio_path, output_path)
            
    async def _generate_musetalk(self, audio_path: str, output_path: str) -> LipSyncResult:
        """Generate using MuseTalk."""
        try:
            cmd = [
                'musetalk',
                '--avatar', self.avatar_image,
                '--audio', audio_path,
                '--output', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and Path(output_path).exists():
                # Get video duration
                duration = await self._get_video_duration(output_path)
                
                return LipSyncResult(
                    video_path=output_path,
                    audio_path=audio_path,
                    duration_seconds=duration,
                    success=True
                )
            else:
                return LipSyncResult(
                    video_path="",
                    audio_path=audio_path,
                    duration_seconds=0,
                    success=False,
                    error=stderr.decode()
                )
                
        except Exception as e:
            return LipSyncResult(
                video_path="",
                audio_path=audio_path,
                duration_seconds=0,
                success=False,
                error=str(e)
            )
            
    async def _generate_liveportrait(self, audio_path: str, output_path: str) -> LipSyncResult:
        """Generate using LivePortrait."""
        # Similar to MuseTalk but with LivePortrait CLI
        try:
            cmd = [
                'liveportrait',
                '--source', self.avatar_image,
                '--audio', audio_path,
                '--output', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and Path(output_path).exists():
                duration = await self._get_video_duration(output_path)
                
                return LipSyncResult(
                    video_path=output_path,
                    audio_path=audio_path,
                    duration_seconds=duration,
                    success=True
                )
            else:
                return LipSyncResult(
                    video_path="",
                    audio_path=audio_path,
                    duration_seconds=0,
                    success=False,
                    error=stderr.decode()
                )
                
        except Exception as e:
            return LipSyncResult(
                video_path="",
                audio_path=audio_path,
                duration_seconds=0,
                success=False,
                error=str(e)
            )
            
    async def _generate_waveform_video(self, audio_path: str, output_path: str) -> LipSyncResult:
        """Fallback: generate video with audio waveform."""
        try:
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-filter_complex',
                '[0:a]showwaves=s=1280x720:mode=line:rate=25:colors=#00ff88,format=yuv420p[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                output_path,
                '-y'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = await self._get_video_duration(output_path)
                
                return LipSyncResult(
                    video_path=output_path,
                    audio_path=audio_path,
                    duration_seconds=duration,
                    success=True
                )
            else:
                return LipSyncResult(
                    video_path="",
                    audio_path=audio_path,
                    duration_seconds=0,
                    success=False,
                    error="FFmpeg waveform generation failed"
                )
                
        except Exception as e:
            return LipSyncResult(
                video_path="",
                audio_path=audio_path,
                duration_seconds=0,
                success=False,
                error=str(e)
            )
            
    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            data = json.loads(stdout)
            
            return float(data.get('format', {}).get('duration', 0))
            
        except:
            return 0.0
            
    def get_status(self) -> Dict:
        """Get avatar system status."""
        return {
            "avatar_image": self.avatar_image,
            "backend": self.backend,
            "musetalk_available": self.musetalk_available,
            "liveportrait_available": self.liveportrait_available,
            "fallback_mode": not (self.musetalk_available or self.liveportrait_available)
        }


# Demo
async def demo():
    """Demo the avatar lip-sync."""
    print("👄 Avatar Lip-Sync Demo")
    print("=" * 50)
    
    avatar = AvatarLipSync()
    status = avatar.get_status()
    
    print(f"\nStatus:")
    print(f"  Backend: {status['backend']}")
    print(f"  MuseTalk: {'✅' if status['musetalk_available'] else '❌'}")
    print(f"  LivePortrait: {'✅' if status['liveportrait_available'] else '❌'}")
    print(f"  Fallback: {'Yes (waveform)' if status['fallback_mode'] else 'No'}")
    
    # Would generate video from audio
    # result = await avatar.generate_talking_head("/path/to/audio.wav")
    

if __name__ == "__main__":
    asyncio.run(demo())
