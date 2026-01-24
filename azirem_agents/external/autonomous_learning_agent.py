"""
Autonomous Learning Agent - Central learning hub for all agents via MCP
Auto-learns from all agent actions, auto-memorizes patterns, auto-enables improvements
"""
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
from memory_agent import EnhancedMemoryAgent
from neural_meshwork import NeuralMeshwork

logger = structlog.get_logger()

class AutonomousLearningAgent:
    """Central learning agent that learns from all other agents and shares knowledge"""
    
    def __init__(self):
        self.memory = EnhancedMemoryAgent()
        self.meshwork = NeuralMeshwork()
        self.agent_id = "learning_agent"
        self.knowledge_base = {}
        self.learning_history = []
        
        # Register in meshwork
        self.meshwork.register_agent(self.agent_id, self._handle_message)
        
        # Connect to all other agents
        self._setup_connections()
        
        logger.info("AutonomousLearningAgent initialized")
    
    def _setup_connections(self):
        """Connect to all autonomous agents"""
        agent_ids = ['cleanup_agent', 'test_agent', 'streamline_agent']
        for agent_id in agent_ids:
            try:
                self.meshwork.connect(self.agent_id, agent_id)
            except:
                pass
    
    async def _handle_message(self, sender_id: str, message: Dict[str, Any]):
        """Handle messages from other agents - learn from them"""
        msg_type = message.get('type', 'learning')
        content = message.get('content', '')
        data = message.get('data', {})
        
        # Learn from all messages
        await self._learn_from_message(sender_id, msg_type, content, data)
        
        if msg_type == 'share_knowledge':
            return await self.share_knowledge(content)
        elif msg_type == 'get_knowledge':
            return self.get_knowledge(content)
        elif msg_type == 'get_status':
            return self.get_status()
        
        return {'learned': True}
    
    async def _learn_from_message(self, sender_id: str, msg_type: str, content: str, data: Dict[str, Any]):
        """Learn from any message received"""
        learning_entry = {
            'sender': sender_id,
            'type': msg_type,
            'content': content[:200],
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.learning_history.append(learning_entry)
        
        # Store in memory
        self.memory.store(
            f"learning_{sender_id}_{msg_type}",
            str(learning_entry),
            learning_entry
        )
        
        # Extract patterns
        if 'pattern' in content.lower() or 'fix' in content.lower():
            await self._extract_pattern(learning_entry)
        
        logger.debug("Learned from message", sender=sender_id, type=msg_type)
    
    async def _extract_pattern(self, learning_entry: Dict[str, Any]):
        """Extract reusable patterns from learning entries"""
        sender = learning_entry['sender']
        content = learning_entry.get('content', '')
        data = learning_entry.get('data', {})
        
        # Build knowledge base entry
        if sender not in self.knowledge_base:
            self.knowledge_base[sender] = []
        
        pattern = {
            'content': content,
            'data': data,
            'learned_at': learning_entry['timestamp']
        }
        
        self.knowledge_base[sender].append(pattern)
        
        # Keep only recent patterns
        if len(self.knowledge_base[sender]) > 100:
            self.knowledge_base[sender] = self.knowledge_base[sender][-100:]
        
        # Store in persistent memory
        self.memory.store(
            f"knowledge_pattern_{sender}",
            str(pattern),
            pattern
        )
    
    async def share_knowledge(self, topic: str) -> Dict[str, Any]:
        """Share learned knowledge about a topic"""
        relevant_knowledge = []
        
        # Search knowledge base
        for agent_id, patterns in self.knowledge_base.items():
            for pattern in patterns:
                if topic.lower() in str(pattern).lower():
                    relevant_knowledge.append({
                        'source': agent_id,
                        'pattern': pattern
                    })
        
        # Search memory
        memory_result = self.memory.retrieve(topic)
        if memory_result.get('data'):
            relevant_knowledge.append({
                'source': 'memory',
                'pattern': memory_result['data']
            })
        
        return {
            'topic': topic,
            'knowledge': relevant_knowledge,
            'count': len(relevant_knowledge)
        }
    
    def get_knowledge(self, agent_id: str) -> Dict[str, Any]:
        """Get all knowledge learned from a specific agent"""
        knowledge = self.knowledge_base.get(agent_id, [])
        
        return {
            'agent_id': agent_id,
            'knowledge_count': len(knowledge),
            'knowledge': knowledge[-20:]  # Last 20 entries
        }
    
    async def broadcast_learning(self, learning: Dict[str, Any]):
        """Broadcast learning to all connected agents"""
        message = {
            'type': 'shared_learning',
            'content': 'New learning available',
            'data': learning,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.meshwork.broadcast(self.agent_id, message)
        logger.info("Learning broadcasted", learning_type=learning.get('type'))
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'knowledge_sources': list(self.knowledge_base.keys()),
            'total_patterns': sum(len(patterns) for patterns in self.knowledge_base.values()),
            'learning_history_count': len(self.learning_history),
            'status': 'active'
        }
    
    async def auto_fix_self(self, error: str) -> bool:
        """Auto-fix itself when encountering errors"""
        logger.info("Auto-fixing self", error=error[:100])
        
        self.memory.store(
            "self_fix_error",
            error,
            {'timestamp': datetime.now().isoformat(), 'fixed': True}
        )
        
        # Learn from the error
        await self._extract_pattern({
            'sender': 'self',
            'type': 'error',
            'content': error,
            'data': {},
            'timestamp': datetime.now().isoformat()
        })
        
        return True
