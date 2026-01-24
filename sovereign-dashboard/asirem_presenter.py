#!/usr/bin/env python3
"""
🧬 aSiReM PRESENTER - Avatar Control & Voice Synthesis
=====================================================
Controls aSiReM avatar states and voice synthesis
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable


class AsiremPresenter:
    """
    aSiReM Avatar Presenter
    Controls avatar state and voice synthesis
    """
    
    def __init__(self, broadcast_callback: Callable):
        self.broadcast = broadcast_callback
        self.state = "idle"
        self.voice_engine = None
        
        # Initialize voice engine if available
        try:
            from asirem_speaking_engine import ASiREMSpeakingEngine
            self.voice_engine = ASiREMSpeakingEngine()
            print("✅ aSiReM Voice Engine initialized")
        except Exception as e:
            print(f"⚠️ Voice engine not available: {e}")
    
    async def set_state(self, state: str, message: Optional[str] = None):
        """Change aSiReM avatar state and optionally speak"""
        self.state = state
        
        await self.broadcast("asirem_state", {
            "state": state,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"🧬 aSiReM: [{state.upper()}] {message if message else ''}")
    
    async def greet(self):
        """aSiReM greeting"""
        await self.set_state("idle", 
            "I am aSiReM, your Sovereign Master Orchestrator. Ready to build.")
    
    async def analyze_request(self, request: str):
        """aSiReM analyzing"""
        preview = request[:50] + "..." if len(request) > 50 else request
        await self.set_state("analyzing", 
            f"Analyzing request: {preview}. Deploying agents.")
    
    async def command_agents(self, agent_count: int, agents: list = None):
        """aSiReM commanding"""
        agent_list = ", ".join(agents) if agents else "agents"
        await self.set_state("commanding", 
            f"Deploying {agent_count}-agent team: {agent_list}. Executing plan now.")
    
    async def report_progress(self, percent: int, current_task: str = ""):
        """aSiReM building"""
        task_info = f" - {current_task}" if current_task else ""
        await self.set_state("building", 
            f"Progress: {percent}%{task_info}. Continuing execution...")
    
    async def complete_mission(self, result: str = "Solution deployed successfully"):
        """aSiReM complete"""
        await self.set_state("complete", 
            f"Mission accomplished. {result}")
    
    async def error(self, error_msg: str):
        """aSiReM error state"""
        await self.set_state("idle", 
            f"Error encountered: {error_msg}")


if __name__ == "__main__":
    # Test the presenter
    async def test_broadcast(event_type, data):
        print(f"[{event_type}] {data}")
    
    async def test():
        presenter = AsiremPresenter(test_broadcast)
        
        await presenter.greet()
        await asyncio.sleep(2)
        
        await presenter.analyze_request("Build a food delivery app")
        await asyncio.sleep(2)
        
        await presenter.command_agents(5, ["Architect", "Backend", "Frontend", "Database", "DevOps"])
        await asyncio.sleep(2)
        
        for i in range(0, 101, 25):
            await presenter.report_progress(i, f"Building component {i//25 + 1}")
            await asyncio.sleep(1)
        
        await presenter.complete_mission("App running at localhost:3000")
    
    asyncio.run(test())
