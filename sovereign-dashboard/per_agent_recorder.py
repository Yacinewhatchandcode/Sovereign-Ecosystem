#!/usr/bin/env python3
"""
🎬 PER-AGENT VIDEO RECORDER
============================
Records each agent's desktop actions as separate MP4 streams.

Features:
- Simultaneous recording of multiple agent windows
- Region-based capture (specific app windows)
- Picture-in-picture composite view
- Real-time streaming via WebSocket
- Automatic start/stop based on agent activity
"""

import asyncio
import subprocess
import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import platform


class RecordingState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AgentRecording:
    """Represents a single agent's recording session"""
    agent_id: str
    agent_name: str
    output_path: str
    state: RecordingState = RecordingState.IDLE
    process: Optional[subprocess.Popen] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    frame_count: int = 0
    file_size_bytes: int = 0
    error: str = ""
    
    def duration_seconds(self) -> float:
        if self.start_time is None:
            return 0
        end = self.end_time or time.time()
        return end - self.start_time
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "output_path": self.output_path,
            "state": self.state.value,
            "duration_seconds": self.duration_seconds(),
            "file_size_bytes": self.file_size_bytes,
            "error": self.error
        }


class PerAgentRecorder:
    """
    Manages per-agent screen recordings.
    
    Each agent gets its own MP4 stream showing their desktop actions.
    Uses macOS screencapture or ffmpeg for cross-platform support.
    """
    
    # Agent color scheme for overlay
    AGENT_COLORS = {
        "azirem": "#FFD700",      # Gold
        "bumblebee": "#FFA500",   # Orange
        "scanner": "#00D4FF",     # Cyan
        "spectra": "#9F4FFF",     # Purple
        "classifier": "#00FF41",  # Green
        "evolution": "#FF0066",   # Pink
    }
    
    def __init__(self, 
                 output_dir: str = "outputs/agent_streams",
                 fps: int = 15,
                 quality: str = "medium"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.fps = fps
        self.quality = quality
        self.is_mac = platform.system() == "Darwin"
        
        self.recordings: Dict[str, AgentRecording] = {}
        self.callback: Optional[Callable] = None
        self._composite_process: Optional[subprocess.Popen] = None
        
        # Check for ffmpeg
        self.has_ffmpeg = self._check_ffmpeg()
        
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ ffmpeg not found - using screencapture (macOS only)")
            return False
    
    def set_callback(self, callback: Callable):
        """Set callback for recording events"""
        self.callback = callback
    
    async def emit(self, event_type: str, data: dict):
        """Emit event to dashboard"""
        if self.callback:
            await self.callback(event_type, data)
    
    async def start_recording(self, 
                              agent_id: str, 
                              agent_name: str = None,
                              region: tuple = None) -> AgentRecording:
        """
        Start recording for a specific agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Display name for the agent
            region: Optional (x, y, width, height) to capture specific region
        
        Returns:
            AgentRecording object
        """
        if agent_id in self.recordings and self.recordings[agent_id].state == RecordingState.RECORDING:
            return self.recordings[agent_id]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(self.output_dir / f"{agent_id}_{timestamp}.mp4")
        
        recording = AgentRecording(
            agent_id=agent_id,
            agent_name=agent_name or agent_id.upper(),
            output_path=output_path
        )
        
        try:
            if self.is_mac:
                process = await self._start_mac_recording(output_path, region)
            elif self.has_ffmpeg:
                process = await self._start_ffmpeg_recording(output_path, region)
            else:
                raise RuntimeError("No recording method available")
            
            recording.process = process
            recording.state = RecordingState.RECORDING
            recording.start_time = time.time()
            
            self.recordings[agent_id] = recording
            
            await self.emit("recording_started", {
                "agent_id": agent_id,
                "output_path": output_path
            })
            
            print(f"🎬 Started recording for {agent_id}: {output_path}")
            
        except Exception as e:
            recording.state = RecordingState.ERROR
            recording.error = str(e)
            print(f"❌ Failed to start recording for {agent_id}: {e}")
        
        return recording
    
    async def _start_mac_recording(self, output_path: str, region: tuple = None) -> subprocess.Popen:
        """Start screen recording on macOS using screencapture"""
        cmd = ["screencapture", "-v", "-C"]
        
        if region:
            x, y, w, h = region
            cmd.extend(["-R", f"{x},{y},{w},{h}"])
        
        cmd.extend(["-r", output_path])
        
        # screencapture -v records video
        # We'll use a different approach with ffmpeg for continuous recording
        
        # Actually, let's use ffmpeg on macOS too for better control
        return await self._start_ffmpeg_recording(output_path, region)
    
    async def _start_ffmpeg_recording(self, output_path: str, region: tuple = None) -> subprocess.Popen:
        """Start screen recording using ffmpeg"""
        if self.is_mac:
            # macOS uses avfoundation
            input_device = "avfoundation"
            input_source = "1:none"  # Screen only, no audio
            
            cmd = [
                "ffmpeg", "-y",
                "-f", input_device,
                "-framerate", str(self.fps),
                "-i", input_source,
            ]
            
            if region:
                x, y, w, h = region
                cmd.extend(["-vf", f"crop={w}:{h}:{x}:{y}"])
            
            # Quality settings
            if self.quality == "high":
                cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "18"])
            elif self.quality == "medium":
                cmd.extend(["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"])
            else:  # low
                cmd.extend(["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"])
            
            cmd.append(output_path)
            
        else:
            # Linux uses x11grab
            cmd = [
                "ffmpeg", "-y",
                "-f", "x11grab",
                "-framerate", str(self.fps),
                "-i", ":0.0",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                output_path
            ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return process
    
    async def stop_recording(self, agent_id: str) -> Optional[AgentRecording]:
        """Stop recording for a specific agent"""
        if agent_id not in self.recordings:
            return None
        
        recording = self.recordings[agent_id]
        
        if recording.state != RecordingState.RECORDING:
            return recording
        
        try:
            if recording.process:
                # Send 'q' to ffmpeg to gracefully stop
                recording.process.stdin.write(b'q')
                recording.process.stdin.flush()
                
                # Wait for process to finish
                try:
                    recording.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    recording.process.terminate()
                    recording.process.wait(timeout=2)
            
            recording.state = RecordingState.STOPPED
            recording.end_time = time.time()
            
            # Get file size
            if os.path.exists(recording.output_path):
                recording.file_size_bytes = os.path.getsize(recording.output_path)
            
            await self.emit("recording_stopped", recording.to_dict())
            
            print(f"⏹️ Stopped recording for {agent_id}: {recording.duration_seconds():.1f}s, {recording.file_size_bytes / 1024:.1f}KB")
            
        except Exception as e:
            recording.state = RecordingState.ERROR
            recording.error = str(e)
            print(f"❌ Error stopping recording for {agent_id}: {e}")
        
        return recording
    
    async def stop_all_recordings(self):
        """Stop all active recordings"""
        tasks = []
        for agent_id in list(self.recordings.keys()):
            if self.recordings[agent_id].state == RecordingState.RECORDING:
                tasks.append(self.stop_recording(agent_id))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    def get_recording_status(self, agent_id: str) -> Optional[dict]:
        """Get status of a specific recording"""
        if agent_id not in self.recordings:
            return None
        return self.recordings[agent_id].to_dict()
    
    def get_all_recordings(self) -> List[dict]:
        """Get status of all recordings"""
        return [r.to_dict() for r in self.recordings.values()]
    
    def get_latest_recordings(self, limit: int = 10) -> List[str]:
        """Get paths to the most recent recording files"""
        recordings = []
        for f in sorted(self.output_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)[:limit]:
            recordings.append(str(f))
        return recordings
    
    async def create_composite_video(self, 
                                     agent_ids: List[str] = None,
                                     output_path: str = None,
                                     layout: str = "grid") -> str:
        """
        Create a picture-in-picture composite of multiple agent recordings.
        
        Args:
            agent_ids: List of agent IDs to include (None = all)
            output_path: Output file path
            layout: "grid" (2x2), "pip" (main + corner), or "horizontal"
        
        Returns:
            Path to composite video
        """
        if not self.has_ffmpeg:
            raise RuntimeError("ffmpeg required for composite videos")
        
        # Get the recordings to composite
        if agent_ids is None:
            recordings = list(self.recordings.values())
        else:
            recordings = [self.recordings[aid] for aid in agent_ids if aid in self.recordings]
        
        if len(recordings) < 2:
            raise ValueError("Need at least 2 recordings for composite")
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"composite_{timestamp}.mp4")
        
        # Build ffmpeg filter for grid layout
        input_files = [r.output_path for r in recordings[:4]]  # Max 4 for grid
        
        cmd = ["ffmpeg", "-y"]
        
        # Add input files
        for f in input_files:
            cmd.extend(["-i", f])
        
        # Build filter complex for 2x2 grid
        n = len(input_files)
        if layout == "grid" and n >= 4:
            filter_complex = (
                "[0:v]scale=640:360[v0];"
                "[1:v]scale=640:360[v1];"
                "[2:v]scale=640:360[v2];"
                "[3:v]scale=640:360[v3];"
                "[v0][v1]hstack[top];"
                "[v2][v3]hstack[bottom];"
                "[top][bottom]vstack[out]"
            )
        elif layout == "pip" and n >= 2:
            filter_complex = (
                "[0:v]scale=1280:720[main];"
                "[1:v]scale=320:180[pip];"
                "[main][pip]overlay=W-w-10:H-h-10[out]"
            )
        else:  # horizontal
            if n == 2:
                filter_complex = "[0:v][1:v]hstack[out]"
            elif n == 3:
                filter_complex = "[0:v][1:v][2:v]hstack=3[out]"
            else:
                filter_complex = "[0:v][1:v]hstack[out]"
        
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:v", "libx264",
            "-preset", "fast",
            output_path
        ])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Composite creation failed: {stderr.decode()}")
        
        print(f"🎬 Created composite video: {output_path}")
        return output_path


class ScreenRecorderPool:
    """
    Pool manager for multiple simultaneous recordings.
    Handles resource allocation and limits.
    """
    
    MAX_CONCURRENT = 4  # Maximum simultaneous recordings
    
    def __init__(self, output_dir: str = "outputs/agent_streams"):
        self.recorder = PerAgentRecorder(output_dir)
        self.active_count = 0
        self._lock = asyncio.Lock()
    
    async def request_recording(self, agent_id: str, agent_name: str = None) -> Optional[AgentRecording]:
        """Request a new recording slot"""
        async with self._lock:
            if self.active_count >= self.MAX_CONCURRENT:
                print(f"⚠️ Max concurrent recordings ({self.MAX_CONCURRENT}) reached")
                return None
            
            recording = await self.recorder.start_recording(agent_id, agent_name)
            if recording.state == RecordingState.RECORDING:
                self.active_count += 1
            
            return recording
    
    async def release_recording(self, agent_id: str) -> Optional[AgentRecording]:
        """Stop and release a recording"""
        async with self._lock:
            recording = await self.recorder.stop_recording(agent_id)
            if recording and recording.state == RecordingState.STOPPED:
                self.active_count = max(0, self.active_count - 1)
            return recording
    
    def get_pool_status(self) -> dict:
        """Get current pool status"""
        return {
            "active_recordings": self.active_count,
            "max_concurrent": self.MAX_CONCURRENT,
            "available_slots": self.MAX_CONCURRENT - self.active_count,
            "recordings": self.recorder.get_all_recordings()
        }


# Singleton instance
_recorder_pool: Optional[ScreenRecorderPool] = None

def get_recorder_pool() -> ScreenRecorderPool:
    """Get or create the singleton recorder pool"""
    global _recorder_pool
    if _recorder_pool is None:
        _recorder_pool = ScreenRecorderPool()
    return _recorder_pool


# CLI Testing
if __name__ == "__main__":
    async def test_recorder():
        pool = get_recorder_pool()
        
        print("🎬 Per-Agent Recorder Test")
        print("=" * 50)
        
        # Test starting recordings
        print("\n1. Starting AZIREM recording (5 seconds)...")
        recording = await pool.request_recording("azirem", "AZIREM Master")
        
        if recording and recording.state == RecordingState.RECORDING:
            print(f"   Recording to: {recording.output_path}")
            
            # Record for 5 seconds
            await asyncio.sleep(5)
            
            # Stop recording
            print("\n2. Stopping recording...")
            result = await pool.release_recording("azirem")
            print(f"   Duration: {result.duration_seconds():.1f}s")
            print(f"   File size: {result.file_size_bytes / 1024:.1f}KB")
        else:
            print(f"   Failed: {recording.error if recording else 'Unknown'}")
        
        # Print pool status
        print("\n📊 Pool Status:")
        print(json.dumps(pool.get_pool_status(), indent=2, default=str))
    
    asyncio.run(test_recorder())
