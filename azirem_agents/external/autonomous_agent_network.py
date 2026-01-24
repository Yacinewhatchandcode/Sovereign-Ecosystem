"""
Autonomous Agent Network - Enables agents to communicate autonomously
Agents can talk to each other, coordinate tasks, and work together
"""
import asyncio
from typing import Dict, Any, List, Optional
from neural_meshwork import NeuralMeshwork
from unified_agent_registry import get_registry
import structlog
import json
from datetime import datetime

logger = structlog.get_logger()

class AutonomousAgentNetwork:
    """Network that enables autonomous agent-to-agent communication"""
    
    def __init__(self):
        self.meshwork = NeuralMeshwork()
        self.registry = get_registry()
        self.conversation_log = []
        self.active_conversations = {}
        self._setup_network()
    
    def _setup_network(self):
        """Setup agent network connections"""
        logger.info("Setting up autonomous agent network...")
        
        # Register all agents in meshwork
        agents = self.registry.list_agents()
        for agent_info in agents:
            agent_id = agent_info['id']
            agent = self.registry.get_agent(agent_id)
            if agent:
                # Create message handler for this agent
                handler = self._create_message_handler(agent_id, agent)
                self.meshwork.register_agent(agent_id, handler)
        
        # Create connections based on agent types
        self._create_connections()
        logger.info("Agent network setup complete", agents=len(agents))
    
    def _create_message_handler(self, agent_id: str, agent_instance: Any):
        """Create message handler for an agent"""
        async def handler(sender_id: str, message: Dict[str, Any]):
            """Handle incoming message"""
            try:
                # Log conversation
                self.conversation_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'from': sender_id,
                    'to': agent_id,
                    'message': message.get('content', ''),
                    'type': message.get('type', 'message')
                })
                
                # Try to process message based on agent capabilities
                if hasattr(agent_instance, 'process_message'):
                    result = await agent_instance.process_message(
                        message.get('content', ''),
                        user_id=message.get('user_id'),
                        generate_audio=False
                    )
                    return result
                elif hasattr(agent_instance, 'handle_message'):
                    result = await agent_instance.handle_message(message)
                    return result
                else:
                    logger.debug("Agent has no message handler", agent=agent_id)
                    return None
            except Exception as e:
                logger.error("Message handling failed", agent=agent_id, error=str(e))
                return None
        
        return handler
    
    def _create_connections(self):
        """Create connections between agents"""
        # Orchestrator connects to all
        orchestrators = [a['id'] for a in self.registry.list_agents() if 'orch' in a['id']]
        other_agents = [a['id'] for a in self.registry.list_agents() if 'orch' not in a['id']]
        
        for orch in orchestrators:
            for agent in other_agents:
                self.meshwork.connect(orch, agent)
        
        # LLM agents connect to cache and search
        llm_agents = [a['id'] for a in self.registry.list_agents() if a['type'] == 'llm']
        cache_agents = [a['id'] for a in self.registry.list_agents() if a['type'] == 'cache']
        search_agents = [a['id'] for a in self.registry.list_agents() if a['type'] == 'search']
        
        for llm in llm_agents:
            for cache in cache_agents:
                self.meshwork.connect(llm, cache)
            for search in search_agents:
                self.meshwork.connect(llm, search)
        
        logger.info("Agent connections created")
    
    async def send_message(self, from_agent: str, to_agent: str, content: str, msg_type: str = 'message') -> Optional[Any]:
        """Send message from one agent to another"""
        message = {
            'content': content,
            'type': msg_type,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Sending agent message", from_agent=from_agent, to_agent=to_agent)
        result = await self.meshwork.send_direct(from_agent, to_agent, message)
        return result
    
    async def broadcast_message(self, from_agent: str, content: str, msg_type: str = 'broadcast') -> List[Any]:
        """Broadcast message to all connected agents"""
        message = {
            'content': content,
            'type': msg_type,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Broadcasting message", from_agent=from_agent)
        await self.meshwork.broadcast(from_agent, message)
        return []
    
    def get_conversation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent conversation log"""
        return self.conversation_log[-limit:]
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get network status"""
        agents = self.registry.list_agents()
        return {
            'total_agents': len(agents),
            'active_agents': len([a for a in agents if a['instantiated']]),
            'connections': len(self.meshwork.connections),
            'recent_messages': len(self.conversation_log),
            'agents': agents
        }

# Global network instance
_network = None

def get_network() -> AutonomousAgentNetwork:
    """Get global agent network"""
    global _network
    if _network is None:
        _network = AutonomousAgentNetwork()
    return _network
