"""
Neural Meshwork - Interconnected agent communication architecture
Allows agents to broadcast messages and respond to each other in a mesh pattern
"""
import asyncio
import structlog

logger = structlog.get_logger()

class NeuralMeshwork:
    """Interconnected communication layer for all agents"""

    def __init__(self):
        self.agents = {}
        self.connections = {}
        logger.info("Neural Meshwork initialized")

    def register_agent(self, agent_id: str, receive_callback: Callable):
        """Register an agent and its message handler in the meshwork"""
        self.agents[agent_id] = receive_callback
        self.connections[agent_id] = []
        logger.debug("Agent registered in mesh", agent_id=agent_id)

    def connect(self, agent1_id: str, agent2_id: str):
        """Create a bidirectional connection between two agents"""
        if agent1_id in self.agents and agent2_id in self.agents:
            if agent2_id not in self.connections[agent1_id]:
                self.connections[agent1_id].append(agent2_id)
            if agent1_id not in self.connections[agent2_id]:
                self.connections[agent2_id].append(agent1_id)
            logger.debug("Agents connected in mesh", a1=agent1_id, a2=agent2_id)

    async def broadcast(self, sender_id: str, message: Dict[str, Any]):
        """Broadcast a message from one agent to all its connected peers"""
        if sender_id not in self.connections:
            return

        targets = self.connections[sender_id]
        logger.info("Broadcasting message", sender=sender_id, target_count=len(targets))

        tasks = []
        for target_id in targets:
            if target_id in self.agents:
                tasks.append(self.agents[target_id](sender_id, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_direct(self, sender_id: str, receiver_id: str, message: Dict[str, Any]):
        """Send a direct message between two agents in the mesh"""
        if receiver_id in self.agents:
            logger.debug("Sending direct message", sender=sender_id, receiver=receiver_id)
            await self.agents[receiver_id](sender_id, message)