"""
Unified Agent Registry - Discovers and registers ALL agents in the codebase
Enables autonomous multi-agent communication via MCP
"""
import sys
import os
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type
import structlog

logger = structlog.get_logger()

class UnifiedAgentRegistry:
    """Central registry for all agents in the codebase"""
    
    def __init__(self):
        self.agents = {}
        self.agent_instances = {}
        self.agent_metadata = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Discover all agents in the codebase"""
        logger.info("Starting agent discovery...")
        
        # Core agents in agents/ (use direct imports since we're in agents dir)
        core_agents = [
            ('client_agent', 'ClientAgent'),
            ('cache_agent', 'CacheAgent'),
            ('search_agent', 'SearchAgent'),
            ('llm_agent', 'LLMAgent'),
            ('tts_agent', 'TTSAgent'),
            ('orchestrator_agent', 'OrchestratorAgent'),
            ('mcp_agent', 'MCPAgent'),
            ('memory_agent', 'EnhancedMemoryAgent'),
            ('consensus_agent', 'ConsensusAgent'),
        ]
        
        # Ultra-fast video agents
        ultra_fast_agents = [
            ('ultra_fast_video.orchestrator_ultra_fast', 'UltraFastOrchestrator'),
            ('ultra_fast_video.prediction_agent', 'PredictionAgent'),
            ('ultra_fast_video.pregeneration_agent', 'PreGenerationAgent'),
            ('ultra_fast_video.segmentation_agent', 'SegmentationAgent'),
            ('ultra_fast_video.smart_cache_agent', 'SmartCacheAgent'),
            ('ultra_fast_video.streaming_agent', 'StreamingAgent'),
            ('ultra_fast_video.cognitive_search_agent', 'CognitiveSearchAgent'),
            ('ultra_fast_video.progressive_streaming_agent', 'ProgressiveStreamingAgent'),
        ]
        
        # UI-client agents (will be loaded dynamically if needed)
        ui_client_agents = [
            # These will be loaded on-demand due to path issues
        ]
        
        all_agent_specs = core_agents + ultra_fast_agents + ui_client_agents
        
        for module_path, class_name in all_agent_specs:
            try:
                # Try to import (we're already in agents directory)
                module = importlib.import_module(module_path)
                
                agent_class = getattr(module, class_name, None)
                if agent_class and inspect.isclass(agent_class):
                    # Register agent
                    agent_id = class_name.lower().replace('agent', '').replace('orchestrator', 'orch')
                    self.agents[agent_id] = {
                        'class': agent_class,
                        'module': module_path,
                        'name': class_name,
                        'type': self._classify_agent(class_name)
                    }
                    logger.info("Agent discovered", agent=class_name, id=agent_id)
            except Exception as e:
                logger.warning("Failed to discover agent", agent=class_name, error=str(e))
        
        logger.info("Agent discovery complete", total=len(self.agents))
    
    def _classify_agent(self, class_name: str) -> str:
        """Classify agent type"""
        name_lower = class_name.lower()
        if 'orchestrator' in name_lower or 'crawler' in name_lower:
            return 'orchestrator'
        elif 'cache' in name_lower:
            return 'cache'
        elif 'search' in name_lower:
            return 'search'
        elif 'llm' in name_lower or 'bedrock' in name_lower:
            return 'llm'
        elif 'tts' in name_lower or 'audio' in name_lower:
            return 'tts'
        elif 'memory' in name_lower:
            return 'memory'
        elif 'consensus' in name_lower:
            return 'consensus'
        elif 'mcp' in name_lower:
            return 'mcp'
        else:
            return 'specialized'
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get or create agent instance"""
        if agent_id not in self.agents:
            return None
        
        if agent_id not in self.agent_instances:
            try:
                agent_class = self.agents[agent_id]['class']
                # Try to instantiate (some may need params)
                try:
                    instance = agent_class()
                except TypeError:
                    # Try with common params
                    try:
                        instance = agent_class(region_name="us-east-1")
                    except:
                        instance = None
                
                if instance:
                    self.agent_instances[agent_id] = instance
                    logger.info("Agent instantiated", agent_id=agent_id)
            except Exception as e:
                logger.error("Failed to instantiate agent", agent_id=agent_id, error=str(e))
                return None
        
        return self.agent_instances.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            {
                'id': agent_id,
                'name': info['name'],
                'type': info['type'],
                'module': info['module'],
                'instantiated': agent_id in self.agent_instances
            }
            for agent_id, info in self.agents.items()
        ]
    
    def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """Get agent capabilities"""
        agent = self.get_agent(agent_id)
        if not agent:
            return {}
        
        capabilities = {
            'id': agent_id,
            'name': self.agents[agent_id]['name'],
            'type': self.agents[agent_id]['type'],
            'methods': []
        }
        
        # Inspect agent methods
        for name, method in inspect.getmembers(agent, predicate=inspect.ismethod):
            if not name.startswith('_'):
                capabilities['methods'].append(name)
        
        return capabilities

# Global registry instance
_registry = None

def get_registry() -> UnifiedAgentRegistry:
    """Get global agent registry"""
    global _registry
    if _registry is None:
        _registry = UnifiedAgentRegistry()
    return _registry
