#!/usr/bin/env python3
"""
🎬 VISUAL OPERATOR AGENT - OpenAI Operator Style
=================================================
This agent VISUALLY controls the screen like a human would:
- Opens Finder windows to browse directories
- Opens files in a code viewer/editor
- Scrolls through code, highlights patterns
- ALL actions are streamed live via screencapture

The user WATCHES the agent work in real-time.
"""

import asyncio
import subprocess
import os
import json
import time
from datetime import datetime
from typing import Optional, Callable, List, Dict
from pathlib import Path
import random
from pattern_engine import AGENTIC_PATTERNS

class VisualOperatorAgent:
    """
    An agent that visually explores the filesystem like a human would.
    Uses macOS automation to open Finder, Preview, and other apps.
    All screen activity is captured and streamed to the dashboard.
    """
    
    def __init__(self, output_dir: str = "outputs/operator_streams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
        self.callback: Optional[Callable] = None
        self.frame_count = 0
        self.capture_process = None
        self.current_file = None
        self.files_explored = []
        
        # Stream directories
        self.stream_dir = self.output_dir / "live"
        self.stream_dir.mkdir(parents=True, exist_ok=True)
        
    def set_callback(self, callback: Callable):
        """Set callback for WebSocket updates."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: dict):
        """Emit event to dashboard."""
        if self.callback:
            await self.callback(event_type, {
                "agent": "visual_operator",
                "timestamp": datetime.now().isoformat(),
                **data
            })
    
    async def start_screen_recording(self):
        """Start continuous screen recording to MP4."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = self.stream_dir / f"operator_session_{timestamp}.mp4"
        
        # Use ffmpeg to record screen (macOS)
        # avfoundation device 1 is usually the screen
        try:
            self.capture_process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y",
                "-f", "avfoundation",
                "-framerate", "10",
                "-i", "1:none",  # Screen capture, no audio
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-pix_fmt", "yuv420p",
                "-s", "1280x720",
                str(self.video_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print(f"🎬 Started screen recording: {self.video_path}")
            return True
        except Exception as e:
            print(f"⚠️ Screen recording failed: {e}")
            # Fallback to screenshot mode
            return False
            
    async def stop_screen_recording(self):
        """Stop screen recording."""
        if self.capture_process:
            self.capture_process.terminate()
            await self.capture_process.wait()
            self.capture_process = None
            
            await self.emit("operator_update", {
                "status": "recording_saved",
                "video_url": f"/outputs/operator_streams/live/{self.video_path.name}"
            })
    
    async def capture_frame(self, annotation: str = ""):
        """Capture a single screenshot frame."""
        frame_path = self.stream_dir / f"frame_{self.frame_count:06d}.png"
        
        subprocess.run(
            ["screencapture", "-x", "-C", "-T0", str(frame_path)],
            capture_output=True,
            timeout=3
        )
        
        if frame_path.exists():
            await self.emit("operator_frame", {
                "frame_number": self.frame_count,
                "frame_url": f"/outputs/operator_streams/live/frame_{self.frame_count:06d}.png",
                "annotation": annotation,
                "current_file": self.current_file
            })
            self.frame_count += 1
            
            # Keep only last 60 frames
            if self.frame_count > 60:
                old = self.stream_dir / f"frame_{self.frame_count - 61:06d}.png"
                if old.exists():
                    old.unlink()
                    
    async def _run_cmd(self, cmd: List[str], timeout: int = 10):
        """Run a command asynchronously."""
        def run():
            return subprocess.run(cmd, capture_output=True, timeout=timeout)
        return await asyncio.to_thread(run)

    async def open_finder_window(self, path: str):
        """Open a Finder window at the specified path."""
        await self.emit("operator_action", {
            "action": "opening_finder",
            "path": path,
            "message": f"📂 Opening Finder: {path}"
        })
        
        # AppleScript to open Finder at path
        script = f'''
        tell application "Finder"
            activate
            make new Finder window to (POSIX file "{path}" as alias)
            set bounds of front window to {{100, 100, 900, 700}}
        end tell
        '''
        await self._run_cmd(["osascript", "-e", script])
        await asyncio.sleep(0.8)
        await self.capture_frame(f"Opened Finder: {os.path.basename(path)}")
        
    async def close_finder_windows(self):
        """Close all Finder windows."""
        script = '''
        tell application "Finder"
            close every window
        end tell
        '''
        await self._run_cmd(["osascript", "-e", script])
        
    async def navigate_to_folder(self, path: str):
        """Navigate Finder to a specific folder."""
        await self.emit("operator_action", {
            "action": "navigating",
            "path": path,
            "message": f"📁 Navigating to: {os.path.basename(path)}"
        })
        
        script = f'''
        tell application "Finder"
            activate
            set target of front window to (POSIX file "{path}" as alias)
        end tell
        '''
        await self._run_cmd(["osascript", "-e", script])
        await asyncio.sleep(0.5)
        await self.capture_frame(f"Navigated: {os.path.basename(path)}")
        
    async def open_file_in_preview(self, filepath: str):
        """Open a file for viewing (code files in VS Code, images in Preview)."""
        ext = os.path.splitext(filepath)[1].lower()
        self.current_file = filepath
        
        await self.emit("operator_action", {
            "action": "opening_file",
            "file": filepath,
            "message": f"📄 Opening: {os.path.basename(filepath)}"
        })
        
        if ext in ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.yaml', '.yml', '.sh']:
            # Open code files in VS Code or default text editor
            script = f'''
            tell application "Finder"
                open file (POSIX file "{filepath}" as alias)
            end tell
            '''
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            # Open images in Preview
            script = f'''
            tell application "Preview"
                activate
                open (POSIX file "{filepath}" as alias)
            end tell
            '''
        else:
            # Default: Quick Look
            script = f'''
            tell application "Finder"
                activate
                select (POSIX file "{filepath}" as alias)
            end tell
            delay 0.3
            tell application "System Events"
                keystroke " "
            end tell
            '''
            
        await self._run_cmd(["osascript", "-e", script])
        await asyncio.sleep(1)
        await self.capture_frame(f"Opened: {os.path.basename(filepath)}")
        self.files_explored.append(filepath)
        
    async def scroll_document(self, direction: str = "down", times: int = 3):
        """Scroll the current document."""
        await self.emit("operator_action", {
            "action": "scrolling",
            "direction": direction,
            "message": f"📜 Scrolling {direction}..."
        })
        
        key = "down" if direction == "down" else "up"
        for _ in range(times):
            script = f'''
            tell application "System Events"
                key code {125 if direction == "down" else 126}
            end tell
            '''
            await self._run_cmd(["osascript", "-e", script])
            await asyncio.sleep(0.3)
            
        await self.capture_frame(f"Scrolled {direction}")
        
    async def highlight_text(self, search_term: str):
        """Use Cmd+F to search/highlight text in the current document."""
        await self.emit("operator_action", {
            "action": "searching",
            "term": search_term,
            "message": f"🔍 Searching for: {search_term}"
        })
        
        script = f'''
        tell application "System Events"
            keystroke "f" using command down
            delay 0.3
            keystroke "{search_term}"
            delay 0.2
            keystroke return
        end tell
        '''
        await self._run_cmd(["osascript", "-e", script])
        await asyncio.sleep(0.8)
        await self.capture_frame(f"Found: {search_term}")
        
    async def close_current_file(self):
        """Close the current file/window."""
        script = '''
        tell application "System Events"
            keystroke "w" using command down
        end tell
        '''
        await self._run_cmd(["osascript", "-e", script])
        await asyncio.sleep(0.3)
        self.current_file = None
        
    async def explore_directory_visually(self, base_path: str, patterns: List[str] = None):
        """
        Visually explore a directory, opening and examining files.
        This is what the user watches on screen.
        """
        self.is_running = True
        patterns = patterns or list(AGENTIC_PATTERNS.keys())
        
        await self.emit("operator_started", {
            "status": "started",
            "base_path": base_path,
            "message": f"🎬 Starting visual exploration of {base_path}"
        })
        
        # Start by opening Finder at the base path
        await self.open_finder_window(base_path)
        
        # Collect interesting files to explore
        interesting_files = []
        for root, dirs, files in os.walk(base_path):
            # Skip hidden and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', '__pycache__', 'venv', 'dist', 'build']]
            
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ['.py', '.js', '.ts', '.html', '.md']:
                    filepath = os.path.join(root, f)
                    try:
                        with open(filepath, 'r', errors='ignore') as file:
                            content = file.read(5000)
                            # Check for patterns
                            for pattern in patterns:
                                if pattern.lower() in content.lower():
                                    interesting_files.append({
                                        "path": filepath,
                                        "pattern": pattern,
                                        "name": f
                                    })
                                    break
                    except:
                        pass
                        
            if len(interesting_files) >= 20:  # Limit to 20 files
                break
                
        await self.emit("operator_update", {
            "status": "files_identified",
            "count": len(interesting_files),
            "message": f"Found {len(interesting_files)} interesting files to examine"
        })
        
        # Visually explore each file
        explored = 0
        for file_info in interesting_files[:10]:  # Explore up to 10 files
            if not self.is_running:
                break
                
            filepath = file_info["path"]
            pattern = file_info["pattern"]
            
            await self.emit("operator_update", {
                "status": "examining",
                "file": filepath,
                "pattern": pattern,
                "progress": f"{explored + 1}/{min(10, len(interesting_files))}"
            })
            
            # Navigate to folder
            folder = os.path.dirname(filepath)
            await self.navigate_to_folder(folder)
            
            # Open the file
            await self.open_file_in_preview(filepath)
            await asyncio.sleep(0.5)
            
            # Scroll through it
            await self.scroll_document("down", 3)
            await asyncio.sleep(0.3)
            
            # Search for the pattern
            await self.highlight_text(pattern)
            await asyncio.sleep(0.8)
            
            # Scroll more
            await self.scroll_document("down", 2)
            await asyncio.sleep(0.3)
            
            # Close it
            await self.close_current_file()
            await asyncio.sleep(0.3)
            
            explored += 1
            
        # Wrap up
        await self.close_finder_windows()
        
        await self.emit("operator_completed", {
            "status": "completed",
            "files_explored": len(self.files_explored),
            "patterns_found": patterns,
            "message": f"✅ Visual exploration complete! Examined {len(self.files_explored)} files"
        })
        
        self.is_running = False
        return self.files_explored
        
    async def stop(self):
        """Stop the visual operator."""
        self.is_running = False
        await self.stop_screen_recording()
        await self.close_finder_windows()


# Integration with the main system
class VisualOperatorMode:
    """
    Integration layer for Visual Operator Mode with the dashboard.
    """
    
    def __init__(self):
        self.operator = VisualOperatorAgent()
        self.is_active = False
        
    def set_callback(self, callback):
        self.operator.set_callback(callback)
        
    async def start_visual_scan(self, paths: List[str], patterns: List[str] = None):
        """Start a visual scanning session."""
        self.is_active = True
        
        for path in paths:
            if not self.is_active:
                break
            if os.path.exists(path):
                await self.operator.explore_directory_visually(path, patterns)
                
        self.is_active = False
        
    async def stop(self):
        """Stop visual scan."""
        self.is_active = False
        await self.operator.stop()


# CLI for testing
if __name__ == "__main__":
    import sys
    
    async def main():
        agent = VisualOperatorAgent()
        
        # Callback for testing
        async def print_event(event_type, data):
            print(f"[{event_type}] {json.dumps(data, indent=2)}")
        agent.set_callback(print_event)
        
        path = sys.argv[1] if len(sys.argv) > 1 else "/Users/yacinebenhamou/aSiReM"
        
        print(f"🎬 Starting Visual Operator Agent on {path}")
        print("Watch your screen - the agent will take control!")
        print()
        
        await agent.explore_directory_visually(path, ["agent", "async", "mcp"])
        
    asyncio.run(main())
