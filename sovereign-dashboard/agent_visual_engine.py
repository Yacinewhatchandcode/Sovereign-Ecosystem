"""
Agent Visual Streaming Engine
Real-time MP4 generation and streaming for each agent's work visualization.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Optional, Callable
from datetime import datetime
import subprocess
import tempfile

class AgentVisualStream:
    """
    Manages real-time visual output for a single agent.
    Generates MP4 streams showing the agent's current work.
    """
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.current_stream_path: Optional[str] = None
        self.is_streaming = False
        self.callback: Optional[Callable] = None
        
        # Output directory for agent streams
        self.stream_dir = Path("outputs/agent_streams") / agent_id
        self.stream_dir.mkdir(parents=True, exist_ok=True)
        
    def set_callback(self, callback: Callable):
        """Set callback for stream updates."""
        self.callback = callback
        
    async def emit_stream_update(self, data: dict):
        """Emit stream update event."""
        if self.callback:
            await self.callback("agent_stream_update", {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                **data
            })
    
    async def start_idle_stream(self):
        """Start idle state visualization (ambient loop)."""
        self.is_streaming = True
        script_dir = Path(__file__).parent
        self.current_stream_path = str(script_dir / "assets" / "bg-loop.mp4")
        
        # Silenced for high-signal build logs
        # await self.emit_stream_update({
        #     "status": "idle",
        #     "stream_url": f"/stream/{self.agent_id}/idle",
        #     "message": f"{self.agent_name} in idle state"
        # })
        
    async def start_work_stream(self, work_type: str, context: dict):
        """
        Generate and stream real-time work visualization.
        
        Args:
            work_type: Type of work (scanning, analyzing, speaking, etc.)
            context: Context data for visualization
        """
        self.is_streaming = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        await self.emit_stream_update({
            "status": "working",
            "work_type": work_type,
            "stream_url": f"/stream/{self.agent_id}/work",
            "message": f"{self.agent_name} {work_type}..."
        })
        
        # Generate visualization based on work type
        if work_type == "speaking":
            await self._generate_speaking_visual(context, timestamp)
        elif work_type == "scanning":
            await self._generate_scanning_visual(context, timestamp)
        elif work_type == "analyzing":
            await self._generate_analysis_visual(context, timestamp)
        else:
            await self._generate_generic_visual(work_type, context, timestamp)
            
    async def _generate_speaking_visual(self, context: dict, timestamp: str):
        """Generate lip-synced speaking visual using MuseTalk."""
        audio_path = context.get("audio_path")
        character_image = context.get("character_image", "assets/character/Gemini_Generated_Image_rxyzqarxyzqarxyz.png")
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"⚠️ Audio not found for speaking visual: {audio_path}")
            return
            
        output_path = self.stream_dir / f"speaking_{timestamp}.mp4"
        
        # Use MuseTalk for lip-sync video generation
        print(f"🎬 Generating speaking visual for {self.agent_name}...")
        
        # Simulate MuseTalk call (in production, integrate actual MuseTalk)
        # For now, copy the base video
        try:
            script_dir = Path(__file__).parent
            source_video = script_dir / "assets" / "asirem-video.mp4"
            
            def run_cp():
                return subprocess.run([
                    "cp", 
                    str(source_video),
                    str(output_path)
                ], check=True)
            
            await asyncio.to_thread(run_cp)
            
            self.current_stream_path = str(output_path)
            await self.emit_stream_update({
                "status": "streaming",
                "stream_url": f"/outputs/agent_streams/{self.agent_id}/speaking_{timestamp}.mp4",
                "message": f"{self.agent_name} speaking live"
            })
        except Exception as e:
            print(f"❌ Failed to generate speaking visual: {e}")
            
    async def _generate_scanning_visual(self, context: dict, timestamp: str):
        """Generate file scanning visualization."""
        files_count = context.get("files_count", 0)
        current_file = context.get("current_file", "")
        
        output_path = self.stream_dir / f"scanning_{timestamp}.mp4"
        
        print(f"📡 Generating scanning visual for {self.agent_name}...")
        print(f"   Scanning: {current_file}")
        print(f"   Files processed: {files_count}")
        
        # Use absolute path for assets relative to this script
        script_dir = Path(__file__).parent
        base_video = script_dir / "assets" / "bg-loop.mp4"

        # Generate visualization with ffmpeg (text overlay on base video)
        try:
            text = f"Scanning: {files_count} files\\n{current_file[:50]}"
            
            def run_ffmpeg():
                return subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(base_video),
                    "-vf", f"drawtext=text='{text}':fontcolor=cyan:fontsize=24:x=10:y=10",
                    "-t", "5",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    str(output_path)
                ], capture_output=True, timeout=10)
            
            result = await asyncio.to_thread(run_ffmpeg)
            
            self.current_stream_path = str(output_path)
            await self.emit_stream_update({
                "status": "streaming",
                "stream_url": f"/outputs/agent_streams/{self.agent_id}/scanning_{timestamp}.mp4",
                "message": f"{self.agent_name} scanning files"
            })
        except Exception as e:
            print(f"❌ Failed to generate scanning visual: {e}")
            
    async def _generate_analysis_visual(self, context: dict, timestamp: str):
        """Generate code analysis visualization."""
        patterns_found = context.get("patterns_found", 0)
        current_pattern = context.get("current_pattern", "")
        
        output_path = self.stream_dir / f"analysis_{timestamp}.mp4"
        
        print(f"🔬 Generating analysis visual for {self.agent_name}...")
        
        # Use base loop for now
        script_dir = Path(__file__).parent
        self.current_stream_path = str(script_dir / "assets" / "bg-loop.mp4")
        await self.emit_stream_update({
            "status": "streaming",
            "stream_url": f"/stream/{self.agent_id}/analysis",
            "message": f"{self.agent_name} analyzing: {patterns_found} patterns"
        })
        
    async def _generate_generic_visual(self, work_type: str, context: dict, timestamp: str):
        """Generate generic work visualization."""
        script_dir = Path(__file__).parent
        self.current_stream_path = str(script_dir / "assets" / "bg-loop.mp4")
        await self.emit_stream_update({
            "status": "streaming",
            "stream_url": f"/stream/{self.agent_id}/work",
            "message": f"{self.agent_name} {work_type}"
        })
        
    async def stop_stream(self):
        """Stop current stream."""
        self.is_streaming = False
        await self.emit_stream_update({
            "status": "idle",
            "stream_url": f"/stream/{self.agent_id}/idle",
            "message": f"{self.agent_name} completed work"
        })
        await self.start_idle_stream()


class AgentVisualEngine:
    """
    Orchestrates visual streaming for all agents.
    """
    
    def __init__(self):
        self.streams: Dict[str, AgentVisualStream] = {}
        self.callback: Optional[Callable] = None
        
    def set_callback(self, callback: Callable):
        """Set callback for all stream updates."""
        self.callback = callback
        for stream in self.streams.values():
            stream.set_callback(callback)
            
    def register_agent(self, agent_id: str, agent_name: str):
        """Register an agent for visual streaming."""
        if agent_id not in self.streams:
            stream = AgentVisualStream(agent_id, agent_name)
            if self.callback:
                stream.set_callback(self.callback)
            self.streams[agent_id] = stream
            print(f"📹 Registered visual stream for {agent_name} ({agent_id})")
            
    async def start_agent_work(self, agent_id: str, work_type: str, context: dict = None):
        """Start visual stream for agent work."""
        if agent_id not in self.streams:
            print(f"⚠️ Agent {agent_id} not registered for streaming")
            return
            
        stream = self.streams[agent_id]
        await stream.start_work_stream(work_type, context or {})
        
    async def stop_agent_work(self, agent_id: str):
        """Stop visual stream for agent."""
        if agent_id in self.streams:
            await self.streams[agent_id].stop_stream()
            
    async def initialize_all_agents(self, agents: list):
        """Initialize all agents with idle streams."""
        for agent in agents:
            self.register_agent(agent["id"], agent["name"])
            await self.streams[agent["id"]].start_idle_stream()
            
    def get_stream_url(self, agent_id: str) -> Optional[str]:
        """Get current stream URL for an agent."""
        if agent_id in self.streams:
            return self.streams[agent_id].current_stream_path
        return None
