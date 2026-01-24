"""
Multi-Agent Orchestration System
Manages agent lifecycle, communication, and coordination
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..agents.base_agent import BaseAgent
from ..agents.azirem_agent import AziremAgent
from ..agents.bumblebee_agent import BumbleBeeAgent
from ..agents.spectra_agent import SpectraAgent  # Added Spectra
from ..agents.specialized_agents import (
    ArchitectureDevAgent,
    ProductManagerAgent,
    QASpecialistAgent,
)
from ..agents.bumblebee_subagents import * # Import all BumbleBee subagents
from ..agents.spectra_subagents import *   # Import all Spectra subagents
from ..config.agent_config import AGENT_CONFIGS, get_agent_config
from ..config.master_agent_config import (
    MASTER_AGENT_HIERARCHY, 
    get_master_agent_config,
    get_bumblebee_subagent_config,
    get_spectra_subagent_config
)
from ..tools.agent_tools import get_tools_for_agent
from ..tools.bumblebee_tools import get_bumblebee_tools
from ..tools.design_tools import get_spectra_tools

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates multiple agents, manages communication, and coordinates tasks
    """
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize the orchestrator
        
        Args:
            ollama_base_url: Ollama API base URL
        """
        self.ollama_base_url = ollama_base_url
        self.agents: Dict[str, BaseAgent] = {}
        self.message_bus: List[Dict[str, Any]] = []  # Event log
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("🎯 Initializing Cold Azirem Agent Orchestrator")
    
    async def initialize_master_agent(self, master_name: str) -> BaseAgent:
        """Initialize a master agent (AZIREM, BumbleBee, SKYNET)"""
        if master_name in self.agents:
            return self.agents[master_name]

        config = get_master_agent_config(master_name)
        
        if master_name == "AZIREM":
            # AZIREM uses standard tools
            tools = get_tools_for_agent(master_name, config.tools)
            agent = AziremAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                ollama_base_url=self.ollama_base_url
            )
            agent.orchestrator = self
        
        elif master_name == "BumbleBee":
            # BumbleBee uses specific research tools
            tools = get_bumblebee_tools()
            agent = BumbleBeeAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                ollama_base_url=self.ollama_base_url
            )
            agent.orchestrator = self
            
        elif master_name == "SPECTRA":
             # SPECTRA uses design tools
             tools = get_spectra_tools()
             # SpectraAgent is defined to take (name, config, orchestrator) in my previous step,
             # but to be consistent and avoid errors if I change it to standard, let's fix SpectraAgent class 
             # to take standard args too, OR leave this specific call if I trust my previous file write.
             # However, BaseAgent.__init__ failed because fallback_model was missing.
             # So I WILL change SpectraAgent to take standard args in the next step.
             # Here I call it with standard args + config as extra?
             # Let's pass 'config' as a keyword argument if the class supports it, or handle sub-agents differently.
             # Actually, simpler: Pass standard args, and pass config manually after?
             # No, SpectraAgent needs config in init to setup subagents.
             # So I will call it with standard args, BUT I will also fix SpectraAgent to accept them.
             agent = SpectraAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                ollama_base_url=self.ollama_base_url,
                config=config, # Special arg for Spectra
                orchestrator=self
             )
             
        else:
            raise ValueError(f"Unknown master agent type: {master_name}")

        self.agents[master_name] = agent
        logger.info(f"✅ Initialized Master Agent: {master_name}")
        return agent

    async def initialize_all_agents(self):
        """Initialize all 10 agents"""
        logger.info("🚀 Initializing all agents...")
        
        for agent_name, config in AGENT_CONFIGS.items():
            await self.initialize_agent(agent_name)
        
        logger.info(f"✅ Initialized {len(self.agents)} agents")
    
    async def initialize_agent(self, agent_name: str) -> BaseAgent:
        """
        Initialize a single agent
        
        Args:
            agent_name: Name of the agent to initialize
            
        Returns:
            Initialized agent instance
        """
        if agent_name in self.agents:
            logger.warning(f"Agent {agent_name} already initialized")
            return self.agents[agent_name]
        
        # Check if it is a Spectra Sub-agent
        if agent_name in ["CreativeDirector", "InterfaceArchitect", "MotionChoreographer"]:
             config = get_spectra_subagent_config(agent_name)
             tools = get_spectra_tools() # Give them design tools
             
             if agent_name == "CreativeDirector":
                 agent = CreativeDirectorAgent(config.name, config)
             elif agent_name == "InterfaceArchitect":
                 agent = InterfaceArchitectAgent(config.name, config)
             elif agent_name == "MotionChoreographer":
                 agent = MotionChoreographerAgent(config.name, config)
             
             self.agents[agent_name] = agent
             return agent
        
        config = get_agent_config(agent_name)
        tools = get_tools_for_agent(agent_name, config.tools)
        
        # Create specialized agent instance
        if agent_name == "ArchitectureDev":
            agent = ArchitectureDevAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                top_p=config.top_p,
                ollama_base_url=self.ollama_base_url,
            )
        elif agent_name == "ProductManager":
            agent = ProductManagerAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                top_p=config.top_p,
                ollama_base_url=self.ollama_base_url,
            )
        elif agent_name == "QASpecialist":
            agent = QASpecialistAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                top_p=config.top_p,
                ollama_base_url=self.ollama_base_url,
            )
        else:
            # Use base agent for others
            agent = BaseAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
                max_context_messages=config.max_context_messages,
                temperature=config.temperature,
                top_p=config.top_p,
                ollama_base_url=self.ollama_base_url,
            )
        
        # Register event callback for inter-agent communication
        agent.register_callback(self._handle_agent_event)
        
        self.agents[agent_name] = agent
        logger.info(f"✅ Initialized {agent_name} with model {config.model}")
        
        return agent
    
    async def _handle_agent_event(self, event: Dict[str, Any]):
        """
        Handle events from agents (for inter-agent communication)
        
        Args:
            event: Event data from agent
        """
        # Log event to message bus
        self.message_bus.append(event)
        
        # Log important events
        if event["type"] in ["process_complete", "tool_end", "error"]:
            logger.info(f"📨 Event from {event['source']}: {event['type']}")
    
    async def execute_task(
        self,
        agent_name: str,
        task: str,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a task with a specific agent
        
        Args:
            agent_name: Name of the agent to use
            task: Task description
            max_iterations: Maximum iterations for tool usage
            
        Returns:
            Task result
        """
        if agent_name not in self.agents:
            # Try to initialize as a master agent first
            if agent_name in ["AZIREM", "BumbleBee", "SPECTRA"]:
                await self.initialize_master_agent(agent_name)
            else:
                await self.initialize_agent(agent_name)
        
        agent = self.agents[agent_name]
        
        logger.info(f"🎯 Executing task with {agent_name}: {task[:100]}...")
        
        result = await agent.process(task, max_iterations=max_iterations)
        
        return result
    
    async def execute_parallel_tasks(
        self,
        tasks: Dict[str, str],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in parallel with different agents
        
        Args:
            tasks: Dictionary of agent_name -> task
            max_iterations: Maximum iterations per agent
            
        Returns:
            Dictionary of agent_name -> result
        """
        logger.info(f"⚡ Executing {len(tasks)} tasks in parallel")
        
        # Create tasks for each agent
        async_tasks = {
            agent_name: self.execute_task(agent_name, task, max_iterations)
            for agent_name, task in tasks.items()
        }
        
        # Execute all in parallel
        results = await asyncio.gather(*async_tasks.values(), return_exceptions=True)
        
        # Map results back to agent names
        result_dict = {}
        for agent_name, result in zip(async_tasks.keys(), results):
            if isinstance(result, Exception):
                result_dict[agent_name] = {
                    "agent": agent_name,
                    "success": False,
                    "error": str(result)
                }
            else:
                result_dict[agent_name] = result
        
        return result_dict
    
    async def agent_collaboration(
        self,
        task: str,
        agent_sequence: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Execute a task through a sequence of agents (pipeline)
        
        Args:
            task: Initial task description
            agent_sequence: List of agent names in execution order
            
        Returns:
            List of results from each agent
        """
        logger.info(f"🔄 Agent collaboration: {' -> '.join(agent_sequence)}")
        
        results = []
        current_task = task
        
        for agent_name in agent_sequence:
            logger.info(f"📍 Step: {agent_name}")
            
            result = await self.execute_task(agent_name, current_task)
            results.append(result)
            
            # Use the agent's response as input for the next agent
            current_task = f"""Previous agent ({agent_name}) completed:
{result['response']}

Continue with the next step based on this information."""
        
        return results
    
    def get_agent_status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of agents
        
        Args:
            agent_name: Specific agent name, or None for all agents
            
        Returns:
            Agent status information
        """
        if agent_name:
            if agent_name not in self.agents:
                return {"error": f"Agent {agent_name} not initialized"}
            
            agent = self.agents[agent_name]
            return {
                "name": agent.name,
                "model": agent.model,
                "tools": list(agent.tools.keys()) if hasattr(agent, 'tools') else [],
                "metrics": agent.get_metrics(),
                "context_size": len(agent.context),
            }
        else:
            # Return status for all agents
            return {
                agent_name: {
                    "name": agent.name,
                    "model": agent.model,
                    "tools": list(agent.tools.keys()) if hasattr(agent, 'tools') else [],
                    "metrics": agent.get_metrics(),
                    "context_size": len(agent.context),
                }
                for agent_name, agent in self.agents.items()
            }
    
    def get_message_bus_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent events from the message bus
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self.message_bus[-limit:]
    
    async def test_agent_tools(self, agent_name: str) -> Dict[str, Any]:
        """
        Test all tools for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Tool test results
        """
        if agent_name not in self.agents:
            await self.initialize_agent(agent_name)
        
        agent = self.agents[agent_name]
        
        logger.info(f"🧪 Testing tools for {agent_name}")
        
        results = {}
        for tool_name, tool_func in agent.tools.items():
            try:
                # Test with minimal args
                if tool_name == "web_search":
                    result = await tool_func(query="test query")
                elif tool_name == "code_gen":
                    result = await tool_func(description="test function")
                elif tool_name == "github_mcp":
                    result = await tool_func(action="test")
                elif tool_name == "supabase_mcp":
                    result = await tool_func(action="test")
                else:
                    # Try calling with no args
                    result = await tool_func()
                
                results[tool_name] = {
                    "status": "✅ success",
                    "result": str(result)[:200]  # Truncate for display
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "❌ failed",
                    "error": str(e)
                }
        
        return {
            "agent": agent_name,
            "tools_tested": len(results),
            "results": results
        }
    
    async def cleanup(self):
        """Cleanup all agents"""
        logger.info("🧹 Cleaning up agents...")
        
        for agent in self.agents.values():
            await agent.close()
        
        self.agents.clear()
        logger.info("✅ Cleanup complete")
