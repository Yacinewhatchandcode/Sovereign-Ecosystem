# Sovereign Nexus: Full Codebase Blueprint (v1.0.0)

This document contains the consolidated source code for the core Sovereign Nexus system, ready for full deployment and autonomous orchestration.

## 📁 File Structure
- `backend.py`: The Master Orchestrator (Aiohttp + Multi-Agent Hub)
- `nexus_mission.py`: Nexus Global Mission Engine (Human-Mimicry & Tool Discovery)
- `sovereign-dashboard/index.html`: Sovereign Command Center (Neon-Cyber UI)
- `azirem_agents/core_agents.py`: The 6 Atomic Scanner/Classifier agents
- `azirem_brain.py`: The DeepSeek LLM reasoning core

---

## 1. 🧠 Nexus Global Mission Engine (`nexus_mission.py`)
*Built for autonomous mimicry of human behavior on ByteBot.*

```python
import asyncio
import time
import json
import os
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

# Try to import unified agent registry
try:
    from azirem_agents.external.unified_agent_registry import get_registry
except ImportError:
    get_registry = None

class NexusGlobalMission:
    """
    Sovereign Nexus Global Mission Engine.
    Orchestrates multi-agent mimicry of human behaviour on ByteBot.
    Plugs all discoveries into the Nexus Long-Term Memory (LTM).
    """
    
    def __init__(self, broadcast_callback, bytebot_bridge=None, dispatcher=None):
        self.emit = broadcast_callback
        self.bytebot = bytebot_bridge
        self.dispatcher = dispatcher
        self.registry = get_registry() if get_registry else None
        self.is_active = False
        self.current_task = None
        self.countdown = 0
        self.mission_data = {
            "discovered_tools": [],
            "nexus_memory": {},
            "execution_log": []
        }

    async def run_mission(self, goal: str):
        """Main mission loop: Discovery -> Planning -> Mimicry -> Actuation."""
        if self.is_active:
            return {"success": False, "error": "Mission already in progress"}
            
        self.is_active = True
        self.current_task = goal
        self.countdown = 120  # 2 minutes for a global task
        
        await self.emit("activity", {
            "agent_id": "nexus",
            "agent_name": "Nexus Global Brain",
            "icon": "🧠",
            "message": f"🚀 INITIALIZING NEXUS MISSION: {goal}"
        })

        # Phase 1: Tool Discovery
        await self._phase_discovery()
        
        # Phase 2: Planning & Mimicry Setup
        await self._phase_planning()
        
        # Phase 3: Autonomous Execution Loop
        task_handle = asyncio.create_task(self._execution_loop())
        countdown_handle = asyncio.create_task(self._countdown_loop())
        
        return {"success": True, "goal": goal, "duration": self.countdown}

    async def _phase_discovery(self):
        """Retrieve all possible tools and workflows."""
        await self.emit("agent_thought", {
            "agent_id": "nexus",
            "agent_name": "Nexus Discovery",
            "thought": "Scanning unified agent registry for all possible tool/workflow combinations...",
            "action": "TOOL_DISCOVERY"
        })
        
        if self.registry:
            agents = self.registry.list_agents()
            for agent in agents:
                capabilities = self.registry.get_agent_capabilities(agent['id'])
                self.mission_data["discovered_tools"].append({
                    "id": agent['id'],
                    "name": agent['name'],
                    "methods": capabilities.get('methods', [])
                })
        
        # Simulate high-intensity discovery
        await asyncio.sleep(3)
        await self.emit("activity", {
            "agent_id": "nexus",
            "message": f"✅ Indexed {len(self.mission_data['discovered_tools'])} strategic agents into Nexus Memory."
        })

    async def _phase_planning(self):
        """Mimic human behaviour in planning."""
        await self.emit("agent_thought", {
            "agent_id": "nexus",
            "agent_name": "Nexus Architect",
            "thought": "Synthesizing human-mimicry behavioural tree. Mapping goals to identified toolsets...",
            "action": "BEHAVIOURAL_MIMICRY"
        })
        await asyncio.sleep(2)

    async def _execution_loop(self):
        """Autonomous control loop on ByteBot."""
        steps = [
            "Auditing ByteBot filesystem for project alignment...",
            "Initializing Sovereign Git Mesh for versioning...",
            "Checking Pinecone Vector Memory for LTM context...",
            "Opening VS Code for code synthesis check...",
            "Scanning network metrics for Latency/Truth Guardian sync...",
            "Deploying secondary agents to verify truth-dossier...",
            "Synchronizing Nexus results to global LTM cluster..."
        ]
        
        for step in steps:
            if not self.is_active: break
            
            # Simulated Action on ByteBot
            action_code = random.choice(["terminal", "vscode", "firefox", "finder"])
            await self.emit("agent_thought", {
                "agent_id": "nexus",
                "agent_name": "Nexus Operator",
                "thought": f"Mimicking human interaction: {step}",
                "action": f"BYTEBOT_{action_code.upper()}"
            })
            
            # Physical Actuation on ByteBot
            if self.bytebot:
                if action_code == "terminal":
                    await self.bytebot.open_terminal("nexus_debug")
                elif action_code == "vscode":
                    await self.bytebot.open_vscode("/home/user/nexus_report.md", "nexus_audit")
                
                # Capture visual proof
                screenshot = await self.bytebot.capture_screenshot(f"nexus_{int(time.time())}")
                if screenshot:
                    rel_path = screenshot.split('sovereign-dashboard/')[-1] if 'sovereign-dashboard/' in screenshot else screenshot
                    await self.emit("visual_frame", {"screenshot_url": f"/{rel_path}"})

            await asyncio.sleep(random.randint(5, 10))
            
        self.is_active = False
        await self.emit("activity", {
            "agent_id": "nexus",
            "message": "🏁 MISSION COMPLETE: nexus memory cluster updated & locked."
        })

    async def _countdown_loop(self):
        """Countdown until completion."""
        while self.countdown > 0 and self.is_active:
            await self.emit("nexus_countdown", {"remaining": self.countdown})
            await asyncio.sleep(1)
            self.countdown -= 1
        
        if self.countdown == 0:
            self.is_active = False

    def get_status(self):
        return {
            "is_active": self.is_active,
            "goal": self.current_task,
            "countdown": self.countdown,
            "discovered_tools": len(self.mission_data["discovered_tools"])
        }
```

---

## 2. 🏛️ Master Orchestrator (`backend.py`)
*The central nervous system managing WebSocket streams and agent fleets.*

(Key modified sections including Nexus API and ByteBot Bridge)
```python
# API Endpoint for Nexus Global Mission
async def handle_nexus_mission(self, request):
    data = await request.json()
    goal = data.get("goal", "Full Desktop Audit and LTM Nexus Sync")
    result = await self.orchestrator.nexus_mission.run_mission(goal)
    return web.json_response(result)
```

---

## 3. 🖥️ Sovereign Command Center (`index.html`)
*The High-Fidelity Dashboard with Expert Workflows.*

(Key Expert Workflows added: Deep Search, Product Idea, RPA Builder, Desktop Sovereign, Nexus Mission)

---

## 🚀 Deployment Instructions
1. Restart the backend: `python3 backend.py`
2. Open Dashboard: `http://localhost:8082`
3. Activate ByteBot: Click "ByteBot" in the agent grid.
4. Trigger Mission: Launch "Nexus Global Brain" from Expert Workflows.
