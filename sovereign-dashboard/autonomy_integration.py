#!/usr/bin/env python3
"""
🧬 AUTONOMY AGENTS INTEGRATION
===============================
Integrates the 74 autonomous agents into the main Sovereign system.

This module provides:
- Dynamic agent loading from autonomy_agents/
- Integration with RealMultiAgentOrchestrator
- Agent lifecycle management
- Unified API for all 142 agents (68 original + 74 autonomy)
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add autonomy_agents to path
AUTONOMY_DIR = Path(__file__).parent / "autonomy_agents"
if str(AUTONOMY_DIR) not in sys.path:
    sys.path.insert(0, str(AUTONOMY_DIR))

# Import autonomy registry
try:
    from autonomy_mesh_registry import (
        AGENT_REGISTRY,
        AGENTS_BY_CATEGORY,
        AGENTS_BY_PRIORITY,
        get_all_agents,
        get_agent_by_id,
        get_agents_by_category,
        get_agents_by_priority,
        get_critical_agents,
        initialize_all_agents,
        get_registry_stats,
    )
    AUTONOMY_AVAILABLE = True
    print(f"🧬 Autonomy Agents: {len(AGENT_REGISTRY)} agents loaded")
except ImportError as e:
    AUTONOMY_AVAILABLE = False
    AGENT_REGISTRY = {}
    print(f"⚠️ Autonomy Agents not available: {e}")


@dataclass
class AgentExecutionResult:
    """Result from agent execution."""
    agent_id: str
    success: bool
    data: Dict[str, Any]
    duration_ms: float
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class AutonomyIntegration:
    """
    Integration layer between autonomous agents and the main orchestrator.
    
    Provides:
    - Agent discovery and initialization
    - Parallel agent execution
    - Result aggregation
    - Health monitoring
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.initialized_agents: Dict[str, bool] = {}
        self._execution_log: List[AgentExecutionResult] = []
        
    async def initialize(self) -> bool:
        """Initialize the autonomy integration layer."""
        if not AUTONOMY_AVAILABLE:
            print("❌ Autonomy agents not available")
            return False
        
        print("🧬 Initializing Autonomy Integration Layer...")
        
        # Load all agents
        for agent_id, spec in AGENT_REGISTRY.items():
            try:
                agent = spec["factory"]()
                self.agents[agent_id] = agent
                self.initialized_agents[agent_id] = False
            except Exception as e:
                print(f"  ⚠️ Failed to load {agent_id}: {e}")
        
        print(f"✅ Loaded {len(self.agents)} autonomy agents")
        return True
    
    async def initialize_critical_agents(self) -> Dict[str, bool]:
        """Initialize only CRITICAL priority agents."""
        results = {}
        critical = get_critical_agents()
        
        print(f"🔴 Initializing {len(critical)} CRITICAL agents...")
        
        for spec in critical:
            agent_id = spec["id"]
            try:
                agent = self.agents.get(agent_id)
                if agent:
                    await agent.initialize()
                    self.initialized_agents[agent_id] = True
                    results[agent_id] = True
                    print(f"  ✅ {spec['name']}")
            except Exception as e:
                results[agent_id] = False
                print(f"  ❌ {spec['name']}: {e}")
        
        return results
    
    async def initialize_by_category(self, category: str) -> Dict[str, bool]:
        """Initialize all agents in a specific category."""
        results = {}
        agents = get_agents_by_category(category)
        
        print(f"📦 Initializing {len(agents)} agents in category: {category}")
        
        for spec in agents:
            agent_id = spec["id"]
            try:
                agent = self.agents.get(agent_id)
                if agent and not self.initialized_agents.get(agent_id):
                    await agent.initialize()
                    self.initialized_agents[agent_id] = True
                    results[agent_id] = True
            except Exception as e:
                results[agent_id] = False
        
        return results
    
    async def run_agent(self, agent_id: str, **kwargs) -> AgentExecutionResult:
        """Run a single agent's cycle."""
        start_time = datetime.now()
        
        agent = self.agents.get(agent_id)
        if not agent:
            return AgentExecutionResult(
                agent_id=agent_id,
                success=False,
                data={"error": "Agent not found"},
                duration_ms=0
            )
        
        # Initialize if needed
        if not self.initialized_agents.get(agent_id):
            await agent.initialize()
            self.initialized_agents[agent_id] = True
        
        try:
            result = await agent.run_cycle()
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            exec_result = AgentExecutionResult(
                agent_id=agent_id,
                success=result.success,
                data=result.data,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = AgentExecutionResult(
                agent_id=agent_id,
                success=False,
                data={"error": str(e)},
                duration_ms=duration_ms
            )
        
        self._execution_log.append(exec_result)
        return exec_result
    
    async def run_category(self, category: str) -> List[AgentExecutionResult]:
        """Run all agents in a category in parallel."""
        agents = get_agents_by_category(category)
        
        async def run_one(spec):
            return await self.run_agent(spec["id"])
        
        tasks = [run_one(spec) for spec in agents]
        return await asyncio.gather(*tasks)
    
    async def run_critical_cycle(self) -> List[AgentExecutionResult]:
        """Run all CRITICAL agents (essential for autonomy)."""
        critical = get_critical_agents()
        
        print(f"🔴 Running CRITICAL agent cycle ({len(critical)} agents)...")
        
        async def run_one(spec):
            return await self.run_agent(spec["id"])
        
        tasks = [run_one(spec) for spec in critical]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r.success)
        print(f"✅ CRITICAL cycle complete: {success_count}/{len(results)} succeeded")
        
        return results
    
    async def run_self_correction_cycle(self) -> List[AgentExecutionResult]:
        """Run the self-correction category (auto-fix, quality, dependencies)."""
        return await self.run_category("self_correction")
    
    async def run_security_scan(self) -> List[AgentExecutionResult]:
        """Run all security agents."""
        return await self.run_category("security")
    
    async def run_monitoring_cycle(self) -> List[AgentExecutionResult]:
        """Run all monitoring agents."""
        return await self.run_category("monitoring")
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent."""
        agent = self.agents.get(agent_id)
        if agent:
            return agent.get_status()
        return {"error": "Agent not found"}
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "total_agents": len(self.agents),
            "initialized": sum(1 for v in self.initialized_agents.values() if v),
            "by_category": {cat: len(agents) for cat, agents in AGENTS_BY_CATEGORY.items()},
            "by_priority": {pri: len(agents) for pri, agents in AGENTS_BY_PRIORITY.items()},
            "recent_executions": len(self._execution_log),
        }
    
    def get_execution_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution log."""
        return [
            {
                "agent_id": r.agent_id,
                "success": r.success,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp
            }
            for r in self._execution_log[-limit:]
        ]


# Singleton instance
_integration_instance: Optional[AutonomyIntegration] = None

def get_autonomy_integration() -> AutonomyIntegration:
    """Get or create the singleton integration instance."""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = AutonomyIntegration()
    return _integration_instance


async def demo():
    """Demo the autonomy integration."""
    print("=" * 60)
    print("🧬 AUTONOMY INTEGRATION DEMO")
    print("=" * 60)
    
    integration = get_autonomy_integration()
    await integration.initialize()
    
    print("\n📊 Status:")
    status = integration.get_all_status()
    print(f"  Total Agents: {status['total_agents']}")
    print(f"  Initialized: {status['initialized']}")
    
    print("\n🔴 Running CRITICAL agent cycle...")
    results = await integration.run_critical_cycle()
    
    for result in results:
        icon = "✅" if result.success else "❌"
        print(f"  {icon} {result.agent_id}: {result.duration_ms:.1f}ms")
    
    print("\n📋 Execution Log:")
    log = integration.get_execution_log(10)
    for entry in log:
        print(f"  - {entry['agent_id']}: {'✅' if entry['success'] else '❌'}")


if __name__ == "__main__":
    asyncio.run(demo())
