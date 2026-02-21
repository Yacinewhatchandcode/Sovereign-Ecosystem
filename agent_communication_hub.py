"""Agent Communication Hub stub."""
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class RegisteredAgent:
    agent_id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"

class AgentCommunicationHub:
    def __init__(self):
        self.agents: Dict[str, RegisteredAgent] = {}
        self.message_queue = asyncio.Queue()
    
    async def register(self, agent: RegisteredAgent):
        self.agents[agent.agent_id] = agent
    
    async def send(self, from_id: str, to_id: str, message: Any):
        await self.message_queue.put({"from": from_id, "to": to_id, "msg": message})
    
    async def broadcast(self, message: Any):
        for aid in self.agents:
            await self.message_queue.put({"from": "hub", "to": aid, "msg": message})
    
    def get_agents(self):
        return list(self.agents.values())
