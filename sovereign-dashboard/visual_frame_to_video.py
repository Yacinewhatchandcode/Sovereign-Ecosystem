#!/usr/bin/env python3
"""
🎬 REAL-TIME VISUAL FRAME TO VIDEO CONVERTER
============================================
Converts JSON visual frames into actual MP4 video streams
showing agent activity in real-time.

Uses ffmpeg to create video from text overlays and animations.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import tempfile

class VisualFrameToVideo:
    """Converts visual frames to actual video streams."""
    
    def __init__(self, output_dir: str = "outputs/agent_streams"):
        self.output_dir = Path(output_dir)
        self.ffmpeg_available = self._check_ffmpeg()
        
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ ffmpeg not found. Install with: brew install ffmpeg")
            return False
            
    def create_text_frame_image(self, text: str, icon: str, color: str, output_path: str):
        """Create a single frame image with text overlay using ffmpeg."""
        if not self.ffmpeg_available:
            return False
            
        # Create a colored background with text
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={color}:s=1920x1080:d=1",
            "-vf", f"drawtext=text='{icon} {text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            "-frames:v", "1",
            output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=10)
            return True
        except Exception as e:
            print(f"⚠️ Failed to create frame image: {e}")
            return False
            
    def frames_to_video(self, agent_id: str, frames: List[Dict], output_filename: str = "activity_stream.mp4"):
        """Convert a list of visual frames to a video."""
        if not self.ffmpeg_available:
            print("⚠️ Cannot create video without ffmpeg")
            return None
            
        agent_dir = self.output_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary directory for frame images
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_files = []
            
            # Generate an image for each frame
            for i, frame in enumerate(frames):
                content = frame.get("content", {})
                visual = content.get("visual", {})
                
                icon = visual.get("icon", "📊")
                message = visual.get("message", "Processing...")
                color = visual.get("color", "#1a1a2e").replace("#", "0x")
                
                frame_path = os.path.join(tmpdir, f"frame_{i:04d}.png")
                
                if self.create_text_frame_image(message, icon, color, frame_path):
                    frame_files.append(frame_path)
                    
            if not frame_files:
                print("⚠️ No frames generated")
                return None
                
            # Create video from frames
            output_path = agent_dir / output_filename
            concat_file = os.path.join(tmpdir, "concat.txt")
            
            # Create concat file for ffmpeg
            with open(concat_file, 'w') as f:
                for frame_file in frame_files:
                    f.write(f"file '{frame_file}'\n")
                    f.write("duration 2\n")  # 2 seconds per frame
                    
            # Generate video
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(output_path)
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True, timeout=60)
                print(f"✅ Generated video: {output_path}")
                return str(output_path)
            except Exception as e:
                print(f"⚠️ Failed to create video: {e}")
                return None
                
    def create_live_activity_video(self, agent_id: str, agent_name: str):
        """Create a live activity video showing real-time agent work."""
        # Read recent frames
        agent_dir = self.output_dir / agent_id
        if not agent_dir.exists():
            print(f"⚠️ No frames found for {agent_id}")
            return None
            
        frame_files = sorted(agent_dir.glob("frame_*.json"))
        
        if not frame_files:
            print(f"⚠️ No frame files found for {agent_id}")
            return None
            
        # Load frames
        frames = []
        for frame_file in frame_files[-20:]:  # Last 20 frames
            try:
                with open(frame_file, 'r') as f:
                    frames.append(json.load(f))
            except Exception as e:
                print(f"⚠️ Failed to load frame {frame_file}: {e}")
                
        if frames:
            return self.frames_to_video(agent_id, frames, "live_activity.mp4")
        else:
            return None
            
    def create_simple_idle_video(self, agent_id: str, agent_name: str, icon: str):
        """Create a simple idle/waiting video for an agent."""
        if not self.ffmpeg_available:
            return None
            
        agent_dir = self.output_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        output_path = agent_dir / "idle_stream.mp4"
        
        # Create a simple animated idle video
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=0x1a1a2e:s=1920x1080:d=10",
            "-vf", f"drawtext=text='{icon} {agent_name}\\nReady and Waiting':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            print(f"✅ Created idle video for {agent_name}: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"⚠️ Failed to create idle video: {e}")
            return None


# CLI usage
if __name__ == "__main__":
    import sys
    
    converter = VisualFrameToVideo()
    
    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
        agent_name = sys.argv[2] if len(sys.argv) > 2 else agent_id.capitalize()
        icon = sys.argv[3] if len(sys.argv) > 3 else "🤖"
        
        print(f"🎬 Creating videos for {agent_name}...")
        
        # Create idle video
        converter.create_simple_idle_video(agent_id, agent_name, icon)
        
        # Create live activity video if frames exist
        converter.create_live_activity_video(agent_id, agent_name)
    else:
        # Create videos for all agents
        agents = [
            ("scanner", "Scanner", "📡"),
            ("classifier", "Classifier", "🏷️"),
            ("extractor", "Extractor", "🔬"),
            ("researcher", "Researcher", "🌐"),
            ("security", "Security", "🛡️"),
            ("qa", "QA", "✅"),
            ("devops", "DevOps", "🏗️"),
            ("evolution", "Evolution", "🧬"),
            ("architect", "Architect", "📐"),
            ("bytebot", "ByteBot", "👀"),
            ("bumblebee", "BumbleBee", "🐝"),
            ("spectra", "Spectra", "🌈"),
            ("azirem", "AZIREM", "👑")
        ]
        
        print("🎬 Creating idle videos for all agents...")
        for agent_id, agent_name, icon in agents:
            converter.create_simple_idle_video(agent_id, agent_name, icon)
            
        print("\n✅ All agent videos created!")
