#!/usr/bin/env python3
"""
🎬 PER-AGENT VISUAL STREAM GENERATOR
====================================
Creates unique visual output streams for each agent showing:
- Repository detection
- File scanning progress
- Code structure analysis
- Pattern highlighting
- Real-time discoveries

Each agent gets its own visual feed that can be displayed in the dashboard.
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import subprocess

@dataclass
class VisualFrame:
    """A single frame of visual output for an agent."""
    agent_id: str
    agent_name: str
    timestamp: str
    frame_type: str  # 'scan', 'discovery', 'analysis', 'highlight'
    content: Dict
    
class PerAgentStreamGenerator:
    """
    Generates unique visual streams for each agent.
    Each stream shows what the agent is currently doing.
    """
    
    def __init__(self, output_dir: str = "outputs/agent_streams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.active_streams: Dict[str, List[VisualFrame]] = {}
        self.callbacks: Dict[str, Callable] = {}
        
    def register_agent(self, agent_id: str, agent_name: str):
        """Register an agent for visual streaming."""
        if agent_id not in self.active_streams:
            self.active_streams[agent_id] = []
            agent_dir = self.output_dir / agent_id
            agent_dir.mkdir(exist_ok=True)
            print(f"📹 Registered visual stream for {agent_name} ({agent_id})")
            
    def set_callback(self, agent_id: str, callback: Callable):
        """Set callback for real-time stream updates."""
        self.callbacks[agent_id] = callback
        
    async def emit_frame(self, agent_id: str, frame: VisualFrame):
        """Emit a visual frame for an agent."""
        if agent_id not in self.active_streams:
            self.register_agent(agent_id, frame.agent_name)
            
        self.active_streams[agent_id].append(frame)
        
        # Save frame to disk
        agent_dir = self.output_dir / agent_id
        frame_file = agent_dir / f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(frame_file, 'w') as f:
            json.dump(asdict(frame), f, indent=2)
            
        # Call callback for real-time updates
        if agent_id in self.callbacks:
            await self.callbacks[agent_id]("visual_frame", asdict(frame))
            
    async def create_repository_detection_frame(
        self, 
        agent_id: str, 
        agent_name: str,
        repo_path: str,
        repo_name: str,
        file_count: int,
        languages: List[str]
    ):
        """Create a frame showing repository detection."""
        frame = VisualFrame(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            frame_type="repository_detection",
            content={
                "action": "detected_repository",
                "repo_path": repo_path,
                "repo_name": repo_name,
                "file_count": file_count,
                "languages": languages,
                "visual": {
                    "icon": "📁",
                    "color": "#00ff88",
                    "message": f"Detected repository: {repo_name} ({file_count} files)"
                }
            }
        )
        await self.emit_frame(agent_id, frame)
        
    async def create_file_scan_frame(
        self,
        agent_id: str,
        agent_name: str,
        filepath: str,
        language: str,
        size_bytes: int,
        patterns_found: List[str]
    ):
        """Create a frame showing file scanning."""
        frame = VisualFrame(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            frame_type="file_scan",
            content={
                "action": "scanning_file",
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "language": language,
                "size_bytes": size_bytes,
                "patterns_found": patterns_found,
                "visual": {
                    "icon": "🔍",
                    "color": "#00ddff",
                    "message": f"Scanning {os.path.basename(filepath)} - Found {len(patterns_found)} patterns",
                    "highlight": len(patterns_found) > 3
                }
            }
        )
        await self.emit_frame(agent_id, frame)
        
    async def create_code_analysis_frame(
        self,
        agent_id: str,
        agent_name: str,
        filepath: str,
        analysis: Dict
    ):
        """Create a frame showing code structure analysis."""
        frame = VisualFrame(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            frame_type="code_analysis",
            content={
                "action": "analyzing_structure",
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "functions": analysis.get("functions", []),
                "classes": analysis.get("classes", []),
                "imports": analysis.get("imports", []),
                "complexity": analysis.get("score", 0),
                "visual": {
                    "icon": "🧬",
                    "color": "#ff00ff",
                    "message": f"Analyzed {os.path.basename(filepath)}: {len(analysis.get('functions', []))} functions, {len(analysis.get('classes', []))} classes",
                    "tree": self._generate_code_tree(analysis)
                }
            }
        )
        await self.emit_frame(agent_id, frame)
        
    async def create_pattern_highlight_frame(
        self,
        agent_id: str,
        agent_name: str,
        filepath: str,
        pattern: str,
        line_numbers: List[int],
        code_snippet: str
    ):
        """Create a frame highlighting discovered patterns."""
        frame = VisualFrame(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            frame_type="pattern_highlight",
            content={
                "action": "highlighting_pattern",
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "pattern": pattern,
                "line_numbers": line_numbers,
                "code_snippet": code_snippet,
                "visual": {
                    "icon": "⚡",
                    "color": "#ffff00",
                    "message": f"Found '{pattern}' pattern in {os.path.basename(filepath)}",
                    "highlight": True,
                    "snippet_preview": code_snippet[:200]
                }
            }
        )
        await self.emit_frame(agent_id, frame)
        
    async def create_discovery_summary_frame(
        self,
        agent_id: str,
        agent_name: str,
        total_files: int,
        total_patterns: int,
        top_patterns: List[tuple],
        top_files: List[str]
    ):
        """Create a summary frame of all discoveries."""
        frame = VisualFrame(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            frame_type="discovery_summary",
            content={
                "action": "summary",
                "total_files": total_files,
                "total_patterns": total_patterns,
                "top_patterns": [{"pattern": p, "count": c} for p, c in top_patterns],
                "top_files": top_files,
                "visual": {
                    "icon": "📊",
                    "color": "#00ff00",
                    "message": f"Discovery complete: {total_files} files, {total_patterns} patterns",
                    "chart_data": {
                        "patterns": dict(top_patterns)
                    }
                }
            }
        )
        await self.emit_frame(agent_id, frame)
        
    def _generate_code_tree(self, analysis: Dict) -> Dict:
        """Generate a visual tree structure of code."""
        tree = {
            "type": "file",
            "children": []
        }
        
        # Add classes
        for cls in analysis.get("classes", []):
            tree["children"].append({
                "type": "class",
                "name": cls,
                "icon": "🏛️"
            })
            
        # Add functions
        for func in analysis.get("functions", []):
            tree["children"].append({
                "type": "function",
                "name": func,
                "icon": "⚙️"
            })
            
        return tree
        
    async def generate_idle_stream(self, agent_id: str, agent_name: str):
        """Generate an idle/waiting visual stream for an agent."""
        agent_dir = self.output_dir / agent_id
        agent_dir.mkdir(exist_ok=True)
        
        # Create a simple idle animation video using ffmpeg if available
        idle_video = agent_dir / "idle_stream.mp4"
        
        # For now, create a JSON manifest
        manifest = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "status": "idle",
            "message": f"{agent_name} is ready and waiting for tasks",
            "visual": {
                "icon": "💤",
                "color": "#888888"
            }
        }
        
        with open(agent_dir / "idle_manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"📹 Generated idle stream for {agent_name}")
        
    async def get_agent_stream_url(self, agent_id: str) -> str:
        """Get the stream URL for an agent."""
        return f"/outputs/agent_streams/{agent_id}/idle_stream.mp4"
        
    async def get_latest_frames(self, agent_id: str, count: int = 10) -> List[Dict]:
        """Get the latest visual frames for an agent."""
        if agent_id not in self.active_streams:
            return []
            
        frames = self.active_streams[agent_id][-count:]
        return [asdict(f) for f in frames]
        
    async def clear_agent_stream(self, agent_id: str):
        """Clear the visual stream for an agent."""
        if agent_id in self.active_streams:
            self.active_streams[agent_id] = []
            
        agent_dir = self.output_dir / agent_id
        if agent_dir.exists():
            for frame_file in agent_dir.glob("frame_*.json"):
                frame_file.unlink()
                
    async def initialize_all_agents(self, agents: List[Dict]):
        """Initialize visual streams for all agents."""
        for agent in agents:
            agent_id = agent["id"]
            agent_name = agent["name"]
            self.register_agent(agent_id, agent_name)
            await self.generate_idle_stream(agent_id, agent_name)


# Example usage
if __name__ == "__main__":
    async def main():
        generator = PerAgentStreamGenerator()
        
        # Register agents
        agents = [
            {"id": "scanner", "name": "Scanner"},
            {"id": "classifier", "name": "Classifier"},
            {"id": "extractor", "name": "Extractor"}
        ]
        
        await generator.initialize_all_agents(agents)
        
        # Simulate scanning activity
        await generator.create_repository_detection_frame(
            "scanner", "Scanner",
            "/Users/yacinebenhamou/aSiReM",
            "aSiReM",
            1523,
            ["Python", "JavaScript", "TypeScript"]
        )
        
        await generator.create_file_scan_frame(
            "scanner", "Scanner",
            "/Users/yacinebenhamou/aSiReM/real_agent_system.py",
            "Python",
            109770,
            ["agent", "async", "websocket", "mcp"]
        )
        
        await generator.create_code_analysis_frame(
            "classifier", "Classifier",
            "/Users/yacinebenhamou/aSiReM/real_agent_system.py",
            {
                "functions": ["handle_status", "handle_run_pipeline", "broadcast_event"],
                "classes": ["RealAgentStreamingServer", "RealMultiAgentOrchestrator"],
                "imports": ["asyncio", "aiohttp", "json"],
                "score": 8.5
            }
        )
        
        await generator.create_pattern_highlight_frame(
            "extractor", "Extractor",
            "/Users/yacinebenhamou/aSiReM/real_agent_system.py",
            "websocket",
            [1629, 1687, 2561],
            "async def websocket_handler(self, request):\n    ws = web.WebSocketResponse()\n    await ws.prepare(request)"
        )
        
        print("\n✅ Generated visual streams for all agents")
        print(f"📁 Output directory: {generator.output_dir}")
        
    asyncio.run(main())
