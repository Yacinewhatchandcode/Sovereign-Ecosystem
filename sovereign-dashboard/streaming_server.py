#!/usr/bin/env python3
"""
🧬 SOVEREIGN COMMAND CENTER - REAL-TIME STREAMING SERVER
=========================================================
WebSocket + REST API for the autonomous self-evolving dashboard.
Powers real-time multi-agent telemetry and video streaming.

Features:
- WebSocket streaming for real-time updates
- REST API for status and control
- Integration with Evolution Engine
- Agent fleet management
- Live metrics broadcasting
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
import random

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try to import aiohttp, fall back to simple HTTP if not available
try:
    from aiohttp import web
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp not installed. Run: pip install aiohttp")

# Try to import evolution engine
try:
    from azirem_evolution.evolution_engine import AutonomousEvolutionEngine
    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False
    print("⚠️ Evolution engine not available, running in simulation mode")


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AgentState:
    """Current state of an agent."""
    id: str
    name: str
    role: str
    icon: str
    status: str  # idle, active, thinking, evolving
    last_activity: str
    tasks_completed: int = 0
    
    
@dataclass
class SystemMetrics:
    """System-wide metrics."""
    patterns_discovered: int = 0
    files_scanned: int = 0
    knowledge_items: int = 0
    agents_spawned: int = 0
    evolution_cycles: int = 0
    uptime_seconds: int = 0
    

@dataclass
class ActivityEvent:
    """An activity event for the stream."""
    timestamp: str
    agent_id: str
    agent_name: str
    icon: str
    message: str
    event_type: str  # info, success, warning, error


# ============================================================================
# SOVEREIGN STREAMING SERVER
# ============================================================================

class SovereignStreamingServer:
    """
    Real-time streaming server for the Sovereign Command Center.
    
    Features:
    - WebSocket broadcasting to all connected clients
    - REST API for control and status
    - Integration with Evolution Engine
    - Automatic agent activity simulation when no real activity
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        
        # Connected WebSocket clients
        self.ws_clients: Set[web.WebSocketResponse] = set()
        
        # State
        self.metrics = SystemMetrics()
        self.agents = self._init_agents()
        self.activities: List[ActivityEvent] = []
        self.current_phase = "idle"
        self.auto_evolve = False
        
        # Knowledge nodes
        self.knowledge_nodes: List[str] = []
        
        # Evolution engine (if available)
        self.evolution_engine = None
        if EVOLUTION_AVAILABLE:
            try:
                self.evolution_engine = AutonomousEvolutionEngine()
            except Exception as e:
                print(f"⚠️ Evolution engine init failed: {e}")
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
    def _init_agents(self) -> Dict[str, AgentState]:
        """Initialize the agent fleet."""
        agent_defs = [
            ("azirem", "AZIREM", "Strategic Master", "🧠", "active"),
            ("bumblebee", "BumbleBee", "Execution Master", "🐝", "active"),
            ("spectra", "Spectra", "Knowledge Master", "🌈", "active"),
            ("scanner", "Scanner", "Discovery Agent", "📡", "idle"),
            ("classifier", "Classifier", "Tagging Agent", "🏷️", "idle"),
            ("extractor", "Extractor", "Code Analyst", "🔬", "idle"),
            ("summarizer", "Summarizer", "NL Generator", "📝", "idle"),
            ("evolution", "Evolution", "Self-Improvement", "🧬", "idle"),
            ("researcher", "Researcher", "Web Search", "🌐", "idle"),
            ("architect", "Architect", "System Design", "🏗️", "idle"),
            ("devops", "DevOps", "Deployment", "⚡", "idle"),
            ("qa", "QA", "Testing", "🧪", "idle"),
            ("security", "Security", "Protection", "🔐", "idle"),
        ]
        
        return {
            agent_id: AgentState(
                id=agent_id,
                name=name,
                role=role,
                icon=icon,
                status=status,
                last_activity=datetime.now().isoformat()
            )
            for agent_id, name, role, icon, status in agent_defs
        }
    
    # ========================================================================
    # WEBSOCKET HANDLING
    # ========================================================================
    
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.ws_clients.add(ws)
        print(f"🔌 WebSocket client connected. Total: {len(self.ws_clients)}")
        
        # Send initial state
        await self._send_full_state(ws)
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_ws_message(ws, data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
        finally:
            self.ws_clients.discard(ws)
            print(f"🔌 WebSocket client disconnected. Total: {len(self.ws_clients)}")
        
        return ws
    
    async def _send_full_state(self, ws: web.WebSocketResponse):
        """Send full system state to a client."""
        state = {
            "type": "full_state",
            "data": {
                "metrics": asdict(self.metrics),
                "agents": [asdict(a) for a in self.agents.values()],
                "activities": [asdict(a) for a in self.activities[-20:]],
                "knowledge_nodes": self.knowledge_nodes[-30:],
                "current_phase": self.current_phase,
                "auto_evolve": self.auto_evolve
            }
        }
        await ws.send_json(state)
    
    async def _handle_ws_message(self, ws: web.WebSocketResponse, data: Dict):
        """Handle incoming WebSocket message."""
        msg_type = data.get("type")
        
        if msg_type == "trigger_evolution":
            await self.trigger_evolution_cycle()
        elif msg_type == "toggle_auto_evolve":
            self.auto_evolve = not self.auto_evolve
            await self.broadcast({
                "type": "auto_evolve_changed",
                "data": {"enabled": self.auto_evolve}
            })
        elif msg_type == "select_agent":
            agent_id = data.get("agent_id")
            await self.activate_agent(agent_id)
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients."""
        if not self.ws_clients:
            return
        
        dead_clients = set()
        for client in self.ws_clients:
            try:
                await client.send_json(message)
            except Exception:
                dead_clients.add(client)
        
        self.ws_clients -= dead_clients
    
    # ========================================================================
    # EVOLUTION INTEGRATION
    # ========================================================================
    
    async def trigger_evolution_cycle(self):
        """Trigger an evolution cycle."""
        self.metrics.evolution_cycles += 1
        
        # Phase 1: Scanning
        self.current_phase = "scanning"
        await self._update_agent_status("scanner", "thinking")
        await self._add_activity("scanner", "Started scanning for new patterns...")
        await self.broadcast({"type": "phase_changed", "data": {"phase": "scanning", "percent": 0}})
        
        for i in range(0, 101, 20):
            await asyncio.sleep(0.3)
            await self.broadcast({"type": "phase_progress", "data": {"phase": "scan", "percent": i}})
        
        # Simulate pattern discovery
        new_patterns = random.randint(5, 25)
        self.metrics.patterns_discovered += new_patterns
        self.metrics.files_scanned += random.randint(20, 100)
        await self._update_agent_status("scanner", "active")
        await self._add_activity("scanner", f"Discovered {new_patterns} new patterns")
        
        # Phase 2: Learning
        self.current_phase = "learning"
        await self._update_agent_status("extractor", "thinking")
        await self._update_agent_status("classifier", "thinking")
        await self._add_activity("extractor", "Analyzing code signatures...")
        await self.broadcast({"type": "phase_changed", "data": {"phase": "learning", "percent": 0}})
        
        for i in range(0, 101, 25):
            await asyncio.sleep(0.3)
            await self.broadcast({"type": "phase_progress", "data": {"phase": "learn", "percent": i}})
        
        # Generate knowledge
        new_knowledge = random.randint(2, 8)
        self.metrics.knowledge_items += new_knowledge
        
        # Add knowledge nodes
        topics = ["LangGraph", "Ollama", "MCP", "RAG", "ChromaDB", "Agent", 
                  "Workflow", "Pipeline", "Reflexion", "DeepSeek", "Vision"]
        for _ in range(min(3, new_knowledge)):
            topic = random.choice(topics)
            if topic not in self.knowledge_nodes:
                self.knowledge_nodes.append(topic)
                await self.broadcast({"type": "knowledge_added", "data": {"topic": topic}})
        
        await self._update_agent_status("extractor", "active")
        await self._update_agent_status("classifier", "idle")
        await self._add_activity("summarizer", f"Generated {new_knowledge} knowledge items")
        
        # Phase 3: Evolving
        self.current_phase = "evolving"
        await self._update_agent_status("evolution", "evolving")
        await self._add_activity("evolution", "Self-improving capabilities...")
        await self.broadcast({"type": "phase_changed", "data": {"phase": "evolving", "percent": 0}})
        
        for i in range(0, 101, 33):
            await asyncio.sleep(0.3)
            await self.broadcast({"type": "phase_progress", "data": {"phase": "evolve", "percent": i}})
        
        # Possibly spawn new agent
        if random.random() > 0.7:
            self.metrics.agents_spawned += 1
            await self._add_activity("evolution", f"Spawned evolved agent #{self.metrics.agents_spawned}")
        
        await self._update_agent_status("evolution", "active")
        
        # Complete
        self.current_phase = "idle"
        await self._add_activity("azirem", f"Evolution cycle {self.metrics.evolution_cycles} complete!")
        
        # Broadcast updated metrics
        await self.broadcast({
            "type": "metrics_updated",
            "data": asdict(self.metrics)
        })
    
    async def _update_agent_status(self, agent_id: str, status: str):
        """Update agent status and broadcast."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_activity = datetime.now().isoformat()
            await self.broadcast({
                "type": "agent_status_changed",
                "data": {"agent_id": agent_id, "status": status}
            })
    
    async def activate_agent(self, agent_id: str):
        """Activate a specific agent."""
        if agent_id in self.agents:
            self.agents[agent_id].status = "active"
            self.agents[agent_id].tasks_completed += 1
            await self._add_activity(agent_id, f"Activated and ready")
    
    async def _add_activity(self, agent_id: str, message: str):
        """Add an activity event and broadcast."""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        event = ActivityEvent(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            agent_name=agent.name,
            icon=agent.icon,
            message=message,
            event_type="info"
        )
        
        self.activities.append(event)
        self.activities = self.activities[-100:]  # Keep last 100
        
        await self.broadcast({
            "type": "activity",
            "data": asdict(event)
        })
    
    # ========================================================================
    # REST API HANDLERS
    # ========================================================================
    
    async def handle_status(self, request: web.Request) -> web.Response:
        """GET /api/status - System status."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        self.metrics.uptime_seconds = int(uptime)
        
        return web.json_response({
            "status": "online",
            "version": "2.0.0",
            "uptime_seconds": int(uptime),
            "connected_clients": len(self.ws_clients),
            "metrics": asdict(self.metrics),
            "current_phase": self.current_phase,
            "auto_evolve": self.auto_evolve,
            "evolution_engine": EVOLUTION_AVAILABLE
        })
    
    async def handle_agents(self, request: web.Request) -> web.Response:
        """GET /api/agents - List all agents."""
        return web.json_response({
            "agents": [asdict(a) for a in self.agents.values()],
            "total": len(self.agents),
            "active": sum(1 for a in self.agents.values() if a.status == "active")
        })
    
    async def handle_trigger_evolution(self, request: web.Request) -> web.Response:
        """POST /api/evolve - Trigger evolution cycle."""
        asyncio.create_task(self.trigger_evolution_cycle())
        return web.json_response({
            "status": "triggered",
            "cycle": self.metrics.evolution_cycles + 1
        })
    
    async def handle_metrics(self, request: web.Request) -> web.Response:
        """GET /api/metrics - Get current metrics."""
        return web.json_response(asdict(self.metrics))
    
    async def handle_activities(self, request: web.Request) -> web.Response:
        """GET /api/activities - Get recent activities."""
        limit = int(request.query.get("limit", 50))
        return web.json_response({
            "activities": [asdict(a) for a in self.activities[-limit:]],
            "total": len(self.activities)
        })
    
    async def handle_knowledge(self, request: web.Request) -> web.Response:
        """GET /api/knowledge - Get knowledge nodes."""
        return web.json_response({
            "nodes": self.knowledge_nodes,
            "total": len(self.knowledge_nodes)
        })
    
    # ========================================================================
    # BACKGROUND TASKS
    # ========================================================================
    
    async def heartbeat_task(self):
        """Send periodic heartbeat to all clients."""
        while True:
            await asyncio.sleep(5)
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.metrics.uptime_seconds = int(uptime)
            
            await self.broadcast({
                "type": "heartbeat",
                "data": {
                    "uptime": int(uptime),
                    "clients": len(self.ws_clients),
                    "cycle": self.metrics.evolution_cycles
                }
            })
    
    async def auto_evolve_task(self):
        """Auto-evolution background task."""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            if self.auto_evolve:
                await self.trigger_evolution_cycle()
    
    async def activity_simulation_task(self):
        """Simulate random agent activity for demo purposes."""
        messages = [
            ("scanner", "Monitoring filesystem for changes..."),
            ("classifier", "Processing new files..."),
            ("extractor", "Extracting code patterns..."),
            ("summarizer", "Generating documentation..."),
            ("researcher", "Searching for cutting-edge patterns..."),
            ("architect", "Analyzing system architecture..."),
            ("azirem", "Strategic planning in progress..."),
            ("bumblebee", "Executing task pipeline..."),
            ("spectra", "Knowledge retrieval complete"),
        ]
        
        while True:
            await asyncio.sleep(random.randint(5, 15))
            agent_id, message = random.choice(messages)
            await self._add_activity(agent_id, message)
    
    # ========================================================================
    # SERVER STARTUP
    # ========================================================================
    
    def create_app(self) -> web.Application:
        """Create the aiohttp application."""
        app = web.Application()
        
        # CORS middleware
        async def cors_middleware(app, handler):
            async def cors_handler(request):
                if request.method == "OPTIONS":
                    return web.Response(headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type",
                    })
                response = await handler(request)
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response
            return cors_handler
        
        app.middlewares.append(cors_middleware)
        
        # Routes
        app.router.add_get("/ws/stream", self.websocket_handler)
        app.router.add_get("/api/status", self.handle_status)
        app.router.add_get("/api/agents", self.handle_agents)
        app.router.add_get("/api/metrics", self.handle_metrics)
        app.router.add_get("/api/activities", self.handle_activities)
        app.router.add_get("/api/knowledge", self.handle_knowledge)
        app.router.add_post("/api/evolve", self.handle_trigger_evolution)
        
        # Static file serving for dashboard
        dashboard_path = Path(__file__).parent
        app.router.add_static("/", dashboard_path, name="static")
        
        # Startup/cleanup
        app.on_startup.append(self._on_startup)
        app.on_cleanup.append(self._on_cleanup)
        
        return app
    
    async def _on_startup(self, app: web.Application):
        """Start background tasks."""
        self.background_tasks = [
            asyncio.create_task(self.heartbeat_task()),
            asyncio.create_task(self.auto_evolve_task()),
            asyncio.create_task(self.activity_simulation_task()),
        ]
        print(f"🚀 Background tasks started")
    
    async def _on_cleanup(self, app: web.Application):
        """Clean up background tasks."""
        for task in self.background_tasks:
            task.cancel()
        print("🛑 Background tasks stopped")
    
    def run(self):
        """Run the server."""
        if not AIOHTTP_AVAILABLE:
            print("❌ Cannot start server: aiohttp not installed")
            return
        
        app = self.create_app()
        
        print("\n" + "🧬" * 30)
        print("   SOVEREIGN COMMAND CENTER")
        print("   Real-Time Streaming Server")
        print("🧬" * 30)
        print(f"\n📡 WebSocket: ws://{self.host}:{self.port}/ws/stream")
        print(f"🌐 Dashboard: http://{self.host}:{self.port}/")
        print(f"📊 API: http://{self.host}:{self.port}/api/status")
        print(f"\n🔧 Evolution Engine: {'✅ Available' if EVOLUTION_AVAILABLE else '⚠️ Simulation'}")
        print("\nPress Ctrl+C to stop\n")
        
        web.run_app(app, host=self.host, port=self.port, print=None)


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sovereign Command Center Streaming Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", "-p", type=int, default=8081, help="Port to listen on")
    
    args = parser.parse_args()
    
    server = SovereignStreamingServer(host=args.host, port=args.port)
    server.run()


if __name__ == "__main__":
    main()
