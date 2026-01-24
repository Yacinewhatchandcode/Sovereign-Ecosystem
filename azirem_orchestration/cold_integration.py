#!/usr/bin/env python3
"""
AZIREM Cold Integration
=======================
Connects the Cold Azirem multi-agent ecosystem to the AZIREM orchestration layer.
Provides a unified interface for all Cold Azirem agents.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Add cold_azirem to path
COLD_AZIREM_PATH = Path(__file__).parent.parent / "cold_azirem"
sys.path.insert(0, str(COLD_AZIREM_PATH))


# ============================================================================
# AGENT REGISTRY
# ============================================================================

class AgentTier(Enum):
    """Agent tiers in the Cold Azirem hierarchy."""
    MASTER = 1  # AZIREM, BumbleBee, Spectra
    SUB = 2     # Sub-agents under masters
    TOOL = 3    # Tool-specific agents


@dataclass
class ColdAgent:
    """A Cold Azirem agent registration."""
    name: str
    tier: AgentTier
    master: Optional[str]  # Master agent name, if any
    role: str
    model: str
    capabilities: List[str]
    status: str = "available"
    module_path: Optional[str] = None


# Cold Azirem Agent Registry
COLD_AGENTS = {
    # Master Agents
    "AZIREM": ColdAgent(
        name="AZIREM",
        tier=AgentTier.MASTER,
        master=None,
        role="Master Coding Orchestrator",
        model="qwen2.5:14b",
        capabilities=[
            "code_analysis", "architecture_design", "task_delegation",
            "project_coordination", "code_generation", "code_review"
        ],
        module_path="cold_azirem.agents.azirem_agent.AziremAgent"
    ),
    "BumbleBee": ColdAgent(
        name="BumbleBee",
        tier=AgentTier.MASTER,
        master=None,
        role="Master Research & Document Orchestrator",
        model="qwen2.5:14b",
        capabilities=[
            "web_research", "document_processing", "pdf_generation",
            "report_creation", "data_synthesis"
        ],
        module_path="cold_azirem.agents.bumblebee_agent.BumbleBeeAgent"
    ),
    "Spectra": ColdAgent(
        name="Spectra",
        tier=AgentTier.MASTER,
        master=None,
        role="Master Design Orchestrator",
        model="qwen2.5:14b",
        capabilities=[
            "ui_design", "visual_identity", "motion_design",
            "css_generation", "design_systems"
        ],
        module_path="cold_azirem.agents.spectra_agent.SpectraAgent"
    ),
    
    # AZIREM Sub-Agents
    "ArchitectureDev": ColdAgent(
        name="ArchitectureDev",
        tier=AgentTier.SUB,
        master="AZIREM",
        role="System Architecture Specialist",
        model="qwen2.5-coder:7b",
        capabilities=["system_design", "design_patterns", "scalability"]
    ),
    "FrontendDev": ColdAgent(
        name="FrontendDev",
        tier=AgentTier.SUB,
        master="AZIREM",
        role="Frontend Development Specialist",
        model="qwen2.5-coder:7b",
        capabilities=["react", "nextjs", "css", "accessibility"]
    ),
    "BackendDev": ColdAgent(
        name="BackendDev",
        tier=AgentTier.SUB,
        master="AZIREM",
        role="Backend Development Specialist",
        model="qwen2.5-coder:7b",
        capabilities=["apis", "databases", "microservices", "python"]
    ),
    "DevOpsEngineer": ColdAgent(
        name="DevOpsEngineer",
        tier=AgentTier.SUB,
        master="AZIREM",
        role="DevOps & Infrastructure Specialist",
        model="llama3.1:8b",
        capabilities=["ci_cd", "docker", "kubernetes", "aws"]
    ),
    "QASpecialist": ColdAgent(
        name="QASpecialist",
        tier=AgentTier.SUB,
        master="AZIREM",
        role="Quality Assurance Specialist",
        model="llama3.1:8b",
        capabilities=["testing", "automation", "quality_gates"]
    ),
    
    # BumbleBee Sub-Agents
    "WebSearchSpecialist": ColdAgent(
        name="WebSearchSpecialist",
        tier=AgentTier.SUB,
        master="BumbleBee",
        role="Web Search & Research Specialist",
        model="llama3.1:8b",
        capabilities=["web_search", "source_validation", "fact_checking"]
    ),
    "DocumentProcessor": ColdAgent(
        name="DocumentProcessor",
        tier=AgentTier.SUB,
        master="BumbleBee",
        role="Document Processing Specialist",
        model="llama3.1:8b",
        capabilities=["pdf_processing", "text_extraction", "formatting"]
    ),
    
    # Spectra Sub-Agents
    "CreativeDirector": ColdAgent(
        name="CreativeDirector",
        tier=AgentTier.SUB,
        master="Spectra",
        role="Creative Direction Specialist",
        model="llama3.1:8b",
        capabilities=["visual_identity", "color_theory", "brand_design"]
    ),
    "InterfaceArchitect": ColdAgent(
        name="InterfaceArchitect",
        tier=AgentTier.SUB,
        master="Spectra",
        role="Interface Architecture Specialist",
        model="qwen2.5-coder:7b",
        capabilities=["ui_architecture", "component_design", "html_css"]
    ),
    "MotionChoreographer": ColdAgent(
        name="MotionChoreographer",
        tier=AgentTier.SUB,
        master="Spectra",
        role="Motion Design Specialist",
        model="llama3.1:8b",
        capabilities=["animation", "gsap", "transitions", "micro_interactions"]
    ),
}


# ============================================================================
# COLD AZIREM BRIDGE
# ============================================================================

class ColdAziremBridge:
    """
    Bridge between AZIREM orchestration and Cold Azirem agents.
    Provides a unified interface for agent operations.
    """
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.agents = COLD_AGENTS.copy()
        self.active_agents: Dict[str, Any] = {}
        self.execution_log: List[Dict] = []
    
    def get_agent_registry(self) -> Dict[str, Dict]:
        """Get the full agent registry."""
        return {
            name: {
                "name": agent.name,
                "tier": agent.tier.name,
                "master": agent.master,
                "role": agent.role,
                "model": agent.model,
                "capabilities": agent.capabilities,
                "status": agent.status,
            }
            for name, agent in self.agents.items()
        }
    
    def get_masters(self) -> List[str]:
        """Get list of master agents."""
        return [
            name for name, agent in self.agents.items() 
            if agent.tier == AgentTier.MASTER
        ]
    
    def get_sub_agents(self, master: str) -> List[str]:
        """Get sub-agents for a master."""
        return [
            name for name, agent in self.agents.items() 
            if agent.master == master
        ]
    
    def get_agent_by_capability(self, capability: str) -> List[str]:
        """Find agents with a specific capability."""
        return [
            name for name, agent in self.agents.items() 
            if capability in agent.capabilities
        ]
    
    def route_task(self, task: str, context: Dict = None) -> Dict:
        """
        Route a task to the appropriate agent(s).
        Uses simple keyword matching for routing.
        """
        task_lower = task.lower()
        
        # Routing rules
        if any(w in task_lower for w in ["code", "build", "develop", "api", "backend", "frontend"]):
            return {"master": "AZIREM", "reason": "Coding task detected"}
        
        if any(w in task_lower for w in ["research", "search", "document", "pdf", "report"]):
            return {"master": "BumbleBee", "reason": "Research/document task detected"}
        
        if any(w in task_lower for w in ["design", "ui", "style", "visual", "css", "animation"]):
            return {"master": "Spectra", "reason": "Design task detected"}
        
        # Default to AZIREM for complex tasks
        return {"master": "AZIREM", "reason": "Default routing to master coordinator"}
    
    def create_execution_plan(self, task: str, context: Dict = None) -> Dict:
        """
        Create an execution plan for a task.
        Determines which agents to involve and in what order.
        """
        routing = self.route_task(task, context)
        master = routing["master"]
        sub_agents = self.get_sub_agents(master)
        
        # Simple sequential plan
        phases = [
            {
                "phase": 1,
                "agent": master,
                "action": "analyze",
                "description": "Analyze task and create detailed plan"
            },
        ]
        
        # Add relevant sub-agents
        for i, sub in enumerate(sub_agents[:3], start=2):
            phases.append({
                "phase": i,
                "agent": sub,
                "action": "execute",
                "description": f"Execute assigned subtask"
            })
        
        # Final synthesis
        phases.append({
            "phase": len(phases) + 1,
            "agent": master,
            "action": "synthesize",
            "description": "Synthesize results and finalize"
        })
        
        return {
            "task": task,
            "routing": routing,
            "phases": phases,
            "estimated_agents": 1 + len(sub_agents),
            "created_at": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bridge status."""
        return {
            "total_agents": len(self.agents),
            "masters": self.get_masters(),
            "sub_agents_count": len([a for a in self.agents.values() if a.tier == AgentTier.SUB]),
            "active_agents": list(self.active_agents.keys()),
            "executions": len(self.execution_log),
        }


# ============================================================================
# UNIFIED ORCHESTRATOR
# ============================================================================

class UnifiedOrchestrator:
    """
    Unified orchestrator that combines AZIREM pipeline with Cold Azirem agents.
    """
    
    def __init__(self):
        self.cold_bridge = ColdAziremBridge()
        self.ollama_executor = None  # Will be set up lazily
        self.rag_engine = None  # Will be set up lazily
        self.mcp_bridge = None  # Will be set up lazily
    
    def _init_ollama(self):
        """Lazy init for Ollama executor."""
        if self.ollama_executor is None:
            try:
                from azirem_agents.ollama_executor import AgentExecutor
                self.ollama_executor = AgentExecutor()
            except ImportError:
                pass
    
    def _init_rag(self):
        """Lazy init for RAG engine."""
        if self.rag_engine is None:
            try:
                from azirem_memory.rag_engine import RAGEngine
                self.rag_engine = RAGEngine()
            except ImportError:
                pass
    
    def _init_mcp(self):
        """Lazy init for MCP bridge."""
        if self.mcp_bridge is None:
            try:
                from azirem_orchestration.mcp_bridge import AgentMCPIntegration
                self.mcp_bridge = AgentMCPIntegration()
            except ImportError:
                pass
    
    def execute_task(self, task: str, use_rag: bool = True) -> Dict:
        """
        Execute a task using the unified orchestrator.
        Combines Cold Azirem routing with Ollama execution.
        """
        self._init_ollama()
        
        # Route task
        plan = self.cold_bridge.create_execution_plan(task)
        
        # Get context from RAG if enabled
        context = {}
        if use_rag:
            self._init_rag()
            if self.rag_engine:
                results = self.rag_engine.search(task, top_k=3)
                if results:
                    context["rag_context"] = [r.document.content for r in results]
        
        # Execute with Ollama if available
        if self.ollama_executor:
            agent_type = "researcher" if "research" in task.lower() else "code_generator"
            result = self.ollama_executor.execute(agent_type, task, context)
            
            return {
                "success": result["success"],
                "plan": plan,
                "output": result["output"],
                "model": result["model"],
                "tokens": result["tokens"],
                "duration_ms": result["duration_ms"],
            }
        
        # Fallback: return plan only
        return {
            "success": True,
            "plan": plan,
            "output": "Execution plan created (Ollama not available)",
            "model": None,
            "tokens": 0,
            "duration_ms": 0,
        }
    
    def get_status(self) -> Dict:
        """Get unified orchestrator status."""
        self._init_ollama()
        self._init_rag()
        self._init_mcp()
        
        return {
            "cold_azirem": self.cold_bridge.get_status(),
            "ollama": self.ollama_executor.get_status() if self.ollama_executor else None,
            "rag": self.rag_engine.get_stats() if self.rag_engine else None,
            "mcp": {
                "available_actions": list(self.mcp_bridge.get_available_actions().keys())
            } if self.mcp_bridge else None,
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    print("=" * 60)
    print("🧊 COLD AZIREM INTEGRATION")
    print("=" * 60)
    
    bridge = ColdAziremBridge()
    
    print("\n📋 AGENT HIERARCHY")
    print("-" * 60)
    
    for master in bridge.get_masters():
        agent = bridge.agents[master]
        print(f"\n👑 {master} ({agent.role})")
        print(f"   Model: {agent.model}")
        print(f"   Capabilities: {', '.join(agent.capabilities[:4])}")
        
        for sub in bridge.get_sub_agents(master):
            sub_agent = bridge.agents[sub]
            print(f"   └─ 🔹 {sub}")
            print(f"         {sub_agent.role}")
    
    print("\n" + "-" * 60)
    print("🧪 TASK ROUTING DEMO")
    print("-" * 60)
    
    tasks = [
        "Build a REST API for user authentication",
        "Research the latest AI agent frameworks",
        "Design a modern landing page with animations",
        "Create a full-stack e-commerce application",
    ]
    
    for task in tasks:
        routing = bridge.route_task(task)
        print(f"\n📝 \"{task[:50]}...\"")
        print(f"   → Master: {routing['master']}")
        print(f"   → Reason: {routing['reason']}")
    
    # Create execution plan demo
    print("\n" + "-" * 60)
    print("📊 EXECUTION PLAN DEMO")
    print("-" * 60)
    
    plan = bridge.create_execution_plan("Build a dashboard with real-time data visualization")
    print(f"\nTask: {plan['task'][:50]}...")
    print(f"Routed to: {plan['routing']['master']}")
    print(f"Phases:")
    for phase in plan['phases']:
        print(f"   {phase['phase']}. {phase['agent']} → {phase['action']}")
    
    print("\n" + "=" * 60)
    print("✅ Cold Azirem integration ready!")
    print(f"   Total agents: {len(bridge.agents)}")
    print(f"   Masters: {', '.join(bridge.get_masters())}")


if __name__ == "__main__":
    main()
