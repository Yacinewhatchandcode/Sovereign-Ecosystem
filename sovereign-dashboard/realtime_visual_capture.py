#!/usr/bin/env python3
"""
🎬 Real-Time Agent Visual Capture Engine
=========================================
Screen capture and browser streaming for OpenAI Operator-style visualization.
Integrates with the Sovereign Dashboard for real-time agent activity viewing.

This captures:
1. Desktop/Finder activity (for Scanner/File agents)
2. Browser automation screenshots (for Researcher agent)
3. Terminal/Code activity (for all agents)
"""

import asyncio
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict
import json

class RealTimeVisualCapture:
    """
    Captures real-time screen activity for agent visualization.
    Uses macOS screencapture for desktop and integrates with browser-use for web.
    """
    
    def __init__(self, output_dir: str = "outputs/live_captures", bridge=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_capturing = False
        self.capture_task = None
        self.current_agent: Optional[str] = None
        self.callback: Optional[Callable] = None
        self.frame_count = 0
        self.bridge = bridge
        self.source_mode = "host"  # "host" or "bytebot"
        
        # Agent-specific capture regions (x, y, width, height)
        # None = full screen
        self.capture_regions = {
            "scanner": None,  # Full screen for Finder
            "researcher": None,  # Full screen for browser
            "extractor": None,  # Full screen for code
            "default": None,
        }
        
    def set_callback(self, callback: Callable):
        """Set callback for streaming updates to WebSocket."""
        self.callback = callback
        
    async def emit_update(self, data: dict):
        """Emit update to connected clients."""
        if self.callback:
            await self.callback("live_capture_update", {
                "agent_id": self.current_agent,
                "timestamp": datetime.now().isoformat(),
                **data
            })
    async def start_capture(self, agent_id: str, mode: str = "screen", source: str = "host"):
        """
        Start real-time screen capture for an agent.
        
        Args:
            agent_id: Which agent is being visualized
            mode: "screen" for desktop, "browser" for web automation
            source: "host" (macOS) or "bytebot" (Ubuntu container)
        """
        self.current_agent = agent_id
        self.is_capturing = True
        self.frame_count = 0
        self.source_mode = source
        
        agent_dir = self.output_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        await self.emit_update({
            "status": "started",
            "mode": mode,
            "source": source,
            "message": f"Started live capture for {agent_id} ({source} source)"
        })
        
        if mode == "screen":
            self.capture_task = asyncio.create_task(
                self._screen_capture_loop(agent_id, agent_dir)
            )
        elif mode == "browser":
            # Browser mode uses Playwright screenshots (handled externally)
            await self.emit_update({
                "status": "browser_mode",
                "message": "Browser capture active via Playwright"
            })
            
    async def _screen_capture_loop(self, agent_id: str, output_dir: Path):
        """Continuous screen capture loop."""
        print(f"🎬 Starting screen capture loop for {agent_id} (Source: {self.source_mode})...")
        
        while self.is_capturing:
            try:
                timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
                screenshot_path = output_dir / f"frame_{self.frame_count:06d}.png"
                
                if self.source_mode == "bytebot" and self.bridge:
                    # Capture from ByteBot container
                    print(f"📸 Capturing frame {self.frame_count} from ByteBot...")
                    bytebot_screenshot = await self.bridge.capture_screenshot(agent_id)
                    if bytebot_screenshot:
                        # Move to live_captures dir
                        shutil_path = Path(bytebot_screenshot)
                        if shutil_path.exists():
                            import shutil
                            shutil.copy(str(shutil_path), str(screenshot_path))
                    else:
                        print(f"⚠️ Failed to get screenshot from ByteBot for {agent_id}")
                else:
                    # macOS screencapture command
                    print(f"📸 Capturing frame {self.frame_count} from Host...")
                    result = subprocess.run(
                        ["screencapture", "-x", "-C", "-T0", str(screenshot_path)],
                        capture_output=True,
                        timeout=5
                    )
                
                if screenshot_path.exists():
                    # Emit frame update
                    print(f"📡 Emitting frame {self.frame_count} to dashboard")
                    await self.emit_update({
                        "status": "frame",
                        "frame_number": self.frame_count,
                        "screenshot_url": f"/outputs/live_captures/{agent_id}/frame_{self.frame_count:06d}.png?t={int(time.time())}",
                        "timestamp": timestamp
                    })
                    self.frame_count += 1
                    
                    # Keep only last 30 frames to save disk space
                    if self.frame_count > 30:
                        old_frame = output_dir / f"frame_{self.frame_count - 31:06d}.png"
                        if old_frame.exists():
                            old_frame.unlink()
                else:
                    print(f"⚠️ Screenshot file not found at {screenshot_path}")
                
                # Capture at interval
                interval = 1.0 if self.source_mode == "bytebot" else 0.8
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Screen capture error: {e}")
                await asyncio.sleep(1)
                
        print(f"🛑 Screen capture stopped for {agent_id}")
        
    async def stop_capture(self):
        """Stop the current capture session."""
        self.is_capturing = False
        
        if self.capture_task:
            self.capture_task.cancel()
            try:
                await self.capture_task
            except asyncio.CancelledError:
                pass
            self.capture_task = None
            
        await self.emit_update({
            "status": "stopped",
            "frames_captured": self.frame_count,
            "message": "Live capture stopped"
        })
        
    async def generate_video_from_frames(self, agent_id: str) -> Optional[str]:
        """
        Convert captured frames to MP4 video.
        
        Returns:
            Path to generated video or None if failed
        """
        frames_dir = self.output_dir / agent_id
        output_video = frames_dir / "live_stream.mp4"
        
        if not list(frames_dir.glob("frame_*.png")):
            print(f"⚠️ No frames found for {agent_id}")
            return None
            
        try:
            # Use ffmpeg to create video from frames
            result = subprocess.run([
                "ffmpeg", "-y",
                "-framerate", "2",
                "-pattern_type", "glob",
                "-i", str(frames_dir / "frame_*.png"),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1280:720",
                str(output_video)
            ], capture_output=True, timeout=30)
            
            if output_video.exists():
                return str(output_video)
                
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            
        return None


class AgentActivityMonitor:
    """
    Monitors agent activities and triggers visual capture.
    Integrates with real_agent_system.py events.
    """
    
    def __init__(self, bridge=None):
        self.capture = RealTimeVisualCapture(bridge=bridge)
        self.active_agents: Dict[str, str] = {}  # agent_id -> activity_type
        self.use_bytebot = False
        
    def set_callback(self, callback: Callable):
        """Set WebSocket broadcast callback."""
        self.capture.set_callback(callback)
        
    def set_mode(self, use_bytebot: bool):
        """Set whether to capture from ByteBot or host."""
        self.use_bytebot = use_bytebot
        
    async def on_agent_start_work(self, agent_id: str, work_type: str, context: dict = None):
        """Called when an agent starts work."""
        self.active_agents[agent_id] = work_type
        
        source = "bytebot" if self.use_bytebot else "host"
        
        # Determine capture mode based on agent type
        if agent_id in ["scanner", "extractor", "classifier"]:
            # These work with files - capture desktop/Finder
            await self.capture.start_capture(agent_id, mode="screen", source=source)
        elif agent_id == "researcher":
            # Web research - browser capture handled by browser-use
            await self.capture.start_capture(agent_id, mode="browser", source=source)
        else:
            # Default to screen capture
            await self.capture.start_capture(agent_id, mode="screen", source=source)
            
    async def on_agent_stop_work(self, agent_id: str):
        """Called when an agent finishes work."""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            
        if self.capture.current_agent == agent_id:
            await self.capture.stop_capture()
            
            # Generate video from captured frames
            video_path = await self.capture.generate_video_from_frames(agent_id)
            if video_path:
                await self.capture.emit_update({
                    "status": "video_ready",
                    "video_url": f"/outputs/live_captures/{agent_id}/live_stream.mp4"
                })


# CLI for testing
if __name__ == "__main__":
    import sys
    
    async def test_capture():
        capture = RealTimeVisualCapture()
        
        # Test callback
        async def print_update(event_type, data):
            print(f"[{event_type}] {json.dumps(data, indent=2)}")
        capture.set_callback(print_update)
        
        agent = sys.argv[1] if len(sys.argv) > 1 else "scanner"
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        
        print(f"🎬 Capturing screen for {agent} agent for {duration} seconds...")
        
        await capture.start_capture(agent, mode="screen")
        await asyncio.sleep(duration)
        await capture.stop_capture()
        
        # Generate video
        video = await capture.generate_video_from_frames(agent)
        if video:
            print(f"✅ Video ready: {video}")
        
    asyncio.run(test_capture())
