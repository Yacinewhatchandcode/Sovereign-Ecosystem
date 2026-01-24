#!/usr/bin/env python3
"""
🎬 PER-AGENT REAL-TIME STREAM GENERATOR
========================================
Generates unique visual streams for each agent based on their current work.
Uses ffmpeg to create dynamic MP4s with agent-specific overlays.
"""

import asyncio
import subprocess
import os
import random
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, Dict

# Agent configurations with unique visual styles
AGENT_CONFIGS = {
    "azirem": {
        "name": "AZIREM", 
        "color": "cyan",
        "bg_overlay": "Strategic Analysis",
        "work_types": ["reasoning", "planning", "coordinating"]
    },
    "bumblebee": {
        "name": "BumbleBee",
        "color": "yellow", 
        "bg_overlay": "Execution Pipeline",
        "work_types": ["executing", "dispatching", "monitoring"]
    },
    "spectra": {
        "name": "Spectra",
        "color": "magenta",
        "bg_overlay": "Knowledge Synthesis",
        "work_types": ["synthesizing", "learning", "connecting"]
    },
    "scanner": {
        "name": "Scanner",
        "color": "green",
        "bg_overlay": "Deep Scan Active",
        "work_types": ["scanning", "discovering", "indexing"]
    },
    "classifier": {
        "name": "Classifier",
        "color": "orange",
        "bg_overlay": "Pattern Classification",
        "work_types": ["classifying", "tagging", "categorizing"]
    },
    "extractor": {
        "name": "Extractor",
        "color": "blue",
        "bg_overlay": "Code Analysis",
        "work_types": ["extracting", "analyzing", "parsing"]
    },
    "summarizer": {
        "name": "Summarizer",
        "color": "white",
        "bg_overlay": "Natural Language Gen",
        "work_types": ["summarizing", "generating", "writing"]
    },
    "evolution": {
        "name": "Evolution",
        "color": "purple",
        "bg_overlay": "Self-Evolution",
        "work_types": ["evolving", "learning", "adapting"]
    },
    "researcher": {
        "name": "Researcher",
        "color": "cyan",
        "bg_overlay": "Web Research",
        "work_types": ["searching", "researching", "gathering"]
    },
    "architect": {
        "name": "Architect",
        "color": "gold",
        "bg_overlay": "System Design",
        "work_types": ["designing", "architecting", "planning"]
    },
    "devops": {
        "name": "DevOps",
        "color": "lime",
        "bg_overlay": "Deployment Pipeline",
        "work_types": ["deploying", "building", "testing"]
    },
    "qa": {
        "name": "QA",
        "color": "teal",
        "bg_overlay": "Quality Assurance",
        "work_types": ["testing", "validating", "verifying"]
    },
    "security": {
        "name": "Security",
        "color": "red",
        "bg_overlay": "Security Scan",
        "work_types": ["scanning", "auditing", "protecting"]
    },
    "archdev": {
        "name": "Chief Architect",
        "color": "gold",
        "bg_overlay": "Sovereign Scheme Design",
        "work_types": ["schematizing", "architecting", "prototyping"]
    },
    "prodman": {
        "name": "Product Manager",
        "color": "#ff69b4",
        "bg_overlay": "Roadmap & Strategy",
        "work_types": ["strategizing", "prioritizing", "writing"]
    },
    "uiarch": {
        "name": "Interface Architect",
        "color": "#00ced1",
        "bg_overlay": "UI/UX Synthesis",
        "work_types": ["designing", "framing", "beautifying"]
    }
}


class PerAgentStreamGenerator:
    """
    Generates unique real-time video streams for each agent.
    """
    
    def __init__(self, output_base: str = "outputs/agent_streams"):
        self.output_base = Path(output_base)
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.active_agents: Dict[str, asyncio.Task] = {}
        self.callback: Optional[Callable] = None
        self.contexts: Dict[str, Dict] = {}
        
    def set_callback(self, callback: Callable):
        self.callback = callback
        
    async def emit(self, event_type: str, data: dict):
        if self.callback:
            await self.callback(event_type, data)

    def update_agent_context(self, agent_id: str, data: dict):
        """Update the live context for an agent's stream."""
        if agent_id in self.active_agents:
             # We need a way to pass this to the running task.
             # Since _generate_work_stream takes 'context' dict, we can't easily update it unless it was a shared object.
             # But we can store contexts in a class dictionary.
             pass
        # Better approach: store contexts in self.contexts
        if not hasattr(self, 'contexts'):
            self.contexts = {}
        
        if agent_id not in self.contexts:
            self.contexts[agent_id] = {}
            
        self.contexts[agent_id].update(data)

    async def start_agent_stream(self, agent_id: str, work_type: str, context: dict = None):

        """
        Start generating a unique work stream for an agent.
        """
        if agent_id not in AGENT_CONFIGS:
            return
            
        config = AGENT_CONFIGS[agent_id]
        if not hasattr(self, 'contexts'):
            self.contexts = {}
            
        # Stop any existing stream for this agent
        if agent_id in self.active_agents:
            await self.stop_agent_stream(agent_id)
            
        # Create agent stream directory
        agent_dir = self.output_base / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        self.contexts[agent_id] = context.copy() if context else {}
        
        # Start stream generation task
        task = asyncio.create_task(
            self._generate_work_stream(agent_id, config, work_type, agent_dir)
        )
        self.active_agents[agent_id] = task
        
        await self.emit("agent_stream_update", {
            "agent_id": agent_id,
            "agent_name": config["name"],
            "status": "streaming",
            "work_type": work_type,
            "stream_url": f"/outputs/agent_streams/{agent_id}/work_stream.mp4",
            "message": f"{config['name']} started {work_type}"
        })
        
    async def _generate_work_stream(
        self, 
        agent_id: str, 
        config: dict, 
        work_type: str, 
        output_dir: Path
    ):
        """
        Generate continuous work stream video.
        Updates the video file periodically to show progress.
        """
        # Use absolute path for assets relative to this script
        script_dir = Path(__file__).parent
        base_video = script_dir / "assets" / "bg-loop.mp4"
        
        if not base_video.exists():
            print(f"⚠️ Base video not found at {base_video}")
            return
            
        frame_count = 0
        work_stream = output_dir / "work_stream.mp4"
        
        try:
            while True:
                # Generate frame with dynamic overlay
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Get LATEST REAL CONTEXT
                current_context = self.contexts.get(agent_id, {})
                progress = current_context.get("progress", 0)  # Default to 0, NO FAKE SIMULATION
                current_item = current_context.get("current_item", "Waiting for task data...")
                details = current_context.get("details", "")
                
                # Create overlay text
                overlay_text = f"{config['name']} | {work_type.upper()}\\n{config['bg_overlay']}\\n{timestamp} | {progress}%\\n{current_item[:40]}\\n{details[:40]}"
                
                # Generate video segment with ffmpeg
                try:
                    def run_ffmpeg():
                        return subprocess.run([
                            "ffmpeg", "-y",
                            "-i", str(base_video),
                            "-vf", (
                                f"drawtext=text='{overlay_text}':"
                                f"fontcolor={config['color']}:"
                                f"fontsize=18:"
                                f"x=10:y=10:"
                                f"box=1:boxcolor=black@0.5:boxborderw=5,"
                                f"drawtext=text='LIVE':"
                                f"fontcolor=red:"
                                f"fontsize=14:"
                                f"x=w-60:y=10"
                            ),
                            "-t", "5",  # 5 second segments
                            "-c:v", "libx264",
                            "-preset", "ultrafast",
                            "-crf", "28",
                            str(work_stream)
                        ], capture_output=True, timeout=10)
                    
                    result = await asyncio.to_thread(run_ffmpeg)
                    
                    if work_stream.exists():
                        # Emit update
                        await self.emit("agent_stream_update", {
                            "agent_id": agent_id,
                            "agent_name": config["name"],
                            "status": "streaming",
                            "frame": frame_count,
                            "work_type": work_type,
                            "stream_url": f"/outputs/agent_streams/{agent_id}/work_stream.mp4?t={frame_count}",
                            "message": f"{config['name']} {work_type}: {progress}%"
                        })
                        
                except subprocess.TimeoutExpired:
                    print(f"⚠️ ffmpeg timeout for {agent_id}")
                    
                frame_count += 1
                await asyncio.sleep(3)  # Update every 3 seconds
                
        except asyncio.CancelledError:
            # Generate final idle stream
            await self._generate_idle_stream(agent_id, config, output_dir)
            
    async def _generate_idle_stream(self, agent_id: str, config: dict, output_dir: Path):
        """Generate idle state video."""
        base_video = Path("assets/bg-loop.mp4")
        idle_stream = output_dir / "idle_stream.mp4"
        
        overlay_text = f"{config['name']}\\nIDLE\\nReady for tasks"
        
        try:
            def run_ffmpeg():
                return subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(base_video),
                    "-vf", (
                        f"drawtext=text='{overlay_text}':"
                        f"fontcolor={config['color']}:"
                        f"fontsize=20:"
                        f"x=10:y=10:"
                        f"box=1:boxcolor=black@0.5:boxborderw=5"
                    ),
                    "-t", "5",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "28",
                    str(idle_stream)
                ], capture_output=True, timeout=10)
            
            await asyncio.to_thread(run_ffmpeg)
        except:
            pass
            
        await self.emit("agent_stream_update", {
            "agent_id": agent_id,
            "agent_name": config["name"],
            "status": "idle",
            "stream_url": f"/outputs/agent_streams/{agent_id}/idle_stream.mp4",
            "message": f"{config['name']} idle"
        })
        
    async def stop_agent_stream(self, agent_id: str):
        """Stop generating stream for an agent."""
        if agent_id in self.active_agents:
            task = self.active_agents[agent_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self.active_agents.pop(agent_id, None)
            
    async def generate_all_idle_streams(self):
        """Generate idle streams for all agents."""
        for agent_id, config in AGENT_CONFIGS.items():
            agent_dir = self.output_base / agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            await self._generate_idle_stream(agent_id, config, agent_dir)
            print(f"📹 Generated idle stream for {config['name']}")


async def regenerate_all_agent_streams():
    """Utility to regenerate all agent idle streams."""
    generator = PerAgentStreamGenerator()
    
    async def log_event(event_type, data):
        print(f"[{event_type}] {data.get('agent_name', 'Unknown')}: {data.get('message', '')}")
        
    generator.set_callback(log_event)
    
    print("🎬 Regenerating all agent idle streams...")
    await generator.generate_all_idle_streams()
    print("✅ All streams regenerated!")


if __name__ == "__main__":
    asyncio.run(regenerate_all_agent_streams())
