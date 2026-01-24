#!/usr/bin/env python3
"""
AZIREM Registry Manager
=======================
Builds and freezes the agent registry from discovery inventory.
Rule: inventory → map → freeze → orchestrate → intelligence

NO MODIFICATIONS to source files - only reads frozen inventory.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AgentCapability:
    """Describes what an agent can do."""
    name: str
    description: str
    required_tools: List[str] = field(default_factory=list)
    model_preference: str = "llama3.1:8b"


@dataclass
class RegisteredAgent:
    """An agent in the registry."""
    id: str                      # Unique identifier
    name: str                    # Human-readable name
    class_name: str              # Python class name
    file_path: str               # Absolute path to agent file
    base_class: Optional[str]    # Parent class
    line_number: int             # Line number in file
    tier: int                    # 1=Strategic, 2=Execution, 3=Specialist
    status: str                  # active, inactive, deprecated
    capabilities: List[AgentCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other agent IDs
    model: str = "llama3.1:8b"   # Preferred Ollama model
    tools: List[str] = field(default_factory=list)


@dataclass
class AgentRegistry:
    """Frozen agent registry."""
    frozen_at: str
    source_inventory: str
    total_agents: int
    agents: List[RegisteredAgent]
    tiers: Dict[int, List[str]]  # tier -> agent_ids


# ============================================================================
# TIER AND CAPABILITY DEFINITIONS
# ============================================================================

# Agent classifications by tier (based on discovered agents)
AGENT_TIER_MAP = {
    "AziremAgent": 1,                    # Strategic: Main coding orchestrator
    "BumbleBeeAgent": 1,                 # Strategic: Research orchestrator
    "SpectraAgent": 1,                   # Strategic: Experience orchestrator
    "ArchitectureDevAgent": 2,           # Execution: System design
    "ProductManagerAgent": 2,            # Execution: Product planning
    "WebSearchSpecialistAgent": 3,       # Specialist: Web research
    "ResearchAnalystAgent": 3,           # Specialist: Research analysis
    "PDFProcessorAgent": 3,              # Specialist: PDF processing
    "CreativeDirectorAgent": 3,          # Specialist: Creative design
    "InterfaceArchitectAgent": 3,        # Specialist: UI/UX
    "MotionChoreographerAgent": 3,       # Specialist: Animation/motion
    "BaseAgent": 0,                      # Base class (not directly usable)
}

# Model preferences by agent type
AGENT_MODEL_MAP = {
    "AziremAgent": "deepseek-r1:7b",     # Deep reasoning for architecture
    "BumbleBeeAgent": "phi3:14b",        # Strong reasoning for research
    "SpectraAgent": "llama3.1:8b",       # Balanced for experience
    "ArchitectureDevAgent": "deepseek-r1:7b",
    "ProductManagerAgent": "llama3.1:8b",
    "WebSearchSpecialistAgent": "qwen3:8b",
    "ResearchAnalystAgent": "phi3:14b",
    "PDFProcessorAgent": "llama3.2:3b",  # Lightweight for document processing
    "CreativeDirectorAgent": "llama3.1:8b",
    "InterfaceArchitectAgent": "phi3:14b",
    "MotionChoreographerAgent": "qwen3:8b",
}

# Capability definitions
AGENT_CAPABILITIES = {
    "AziremAgent": [
        AgentCapability("code_generation", "Generate production code", ["github_mcp"]),
        AgentCapability("code_review", "Review and improve code", ["github_mcp"]),
        AgentCapability("architecture", "Design system architecture", []),
    ],
    "BumbleBeeAgent": [
        AgentCapability("web_research", "Search and synthesize web content", ["web_search"]),
        AgentCapability("document_analysis", "Analyze documents and PDFs", []),
        AgentCapability("knowledge_extraction", "Extract and structure knowledge", []),
    ],
    "SpectraAgent": [
        AgentCapability("ui_design", "Design user interfaces", ["design_tools"]),
        AgentCapability("animation", "Create motion and animations", []),
        AgentCapability("user_experience", "Optimize user experience", []),
    ],
}


# ============================================================================
# REGISTRY MANAGER
# ============================================================================

class RegistryManager:
    """
    Manages the agent registry.
    Reads from frozen inventory, never modifies source files.
    """
    
    def __init__(self, inventory_path: str):
        self.inventory_path = Path(inventory_path)
        self.inventory: Dict[str, Any] = {}
        self.registry: Optional[AgentRegistry] = None
    
    def load_inventory(self) -> bool:
        """Load the frozen inventory from JSON."""
        try:
            with open(self.inventory_path) as f:
                self.inventory = json.load(f)
            print(f"✅ Loaded inventory from: {self.inventory_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load inventory: {e}")
            return False
    
    def build_registry(self) -> AgentRegistry:
        """Build agent registry from inventory."""
        if not self.inventory:
            raise ValueError("Inventory not loaded. Call load_inventory() first.")
        
        agents_data = self.inventory.get("agents", [])
        registered_agents = []
        tiers: Dict[int, List[str]] = {0: [], 1: [], 2: [], 3: []}
        
        for agent_data in agents_data:
            class_name = agent_data.get("class_name", "")
            
            # Skip BaseAgent (it's abstract)
            if class_name == "BaseAgent":
                continue
            
            # Determine tier
            tier = AGENT_TIER_MAP.get(class_name, 3)
            
            # Get model preference
            model = AGENT_MODEL_MAP.get(class_name, "llama3.1:8b")
            
            # Get capabilities
            capabilities = AGENT_CAPABILITIES.get(class_name, [])
            
            # Create agent ID
            agent_id = f"agent_{class_name.lower().replace('agent', '')}"
            
            registered = RegisteredAgent(
                id=agent_id,
                name=class_name.replace("Agent", " Agent"),
                class_name=class_name,
                file_path=agent_data.get("file_path", ""),
                base_class=agent_data.get("base_class"),
                line_number=agent_data.get("line_number", 0),
                tier=tier,
                status="active",
                capabilities=capabilities,
                model=model,
                dependencies=[],
                tools=[cap.required_tools[0] for cap in capabilities 
                       if cap.required_tools]
            )
            
            registered_agents.append(registered)
            tiers[tier].append(agent_id)
        
        self.registry = AgentRegistry(
            frozen_at=datetime.now().isoformat(),
            source_inventory=str(self.inventory_path),
            total_agents=len(registered_agents),
            agents=registered_agents,
            tiers={k: v for k, v in tiers.items() if v}  # Only non-empty tiers
        )
        
        return self.registry
    
    def freeze_registry(self, output_path: str) -> None:
        """Export registry to JSON file (freeze it)."""
        if not self.registry:
            raise ValueError("Registry not built. Call build_registry() first.")
        
        # Convert to JSON-serializable format
        registry_dict = {
            "frozen_at": self.registry.frozen_at,
            "source_inventory": self.registry.source_inventory,
            "total_agents": self.registry.total_agents,
            "agents": [
                {
                    **asdict(agent),
                    "capabilities": [asdict(cap) for cap in agent.capabilities]
                }
                for agent in self.registry.agents
            ],
            "tiers": self.registry.tiers
        }
        
        with open(output_path, 'w') as f:
            json.dump(registry_dict, f, indent=2)
        
        print(f"📄 Registry frozen to: {output_path}")
    
    def get_agent_by_id(self, agent_id: str) -> Optional[RegisteredAgent]:
        """Get agent by ID."""
        if not self.registry:
            return None
        return next((a for a in self.registry.agents if a.id == agent_id), None)
    
    def get_agents_by_tier(self, tier: int) -> List[RegisteredAgent]:
        """Get all agents in a tier."""
        if not self.registry:
            return []
        return [a for a in self.registry.agents if a.tier == tier]
    
    def get_agents_with_capability(self, capability_name: str) -> List[RegisteredAgent]:
        """Get agents that have a specific capability."""
        if not self.registry:
            return []
        return [
            a for a in self.registry.agents 
            if any(cap.name == capability_name for cap in a.capabilities)
        ]


def print_registry_summary(registry: AgentRegistry) -> None:
    """Print human-readable registry summary."""
    print("\n" + "=" * 70)
    print("🤖 AZIREM AGENT REGISTRY")
    print("=" * 70)
    print(f"📅 Frozen At: {registry.frozen_at}")
    print(f"📊 Total Agents: {registry.total_agents}")
    
    tier_names = {1: "Strategic", 2: "Execution", 3: "Specialist"}
    
    for tier, agents in sorted(registry.tiers.items()):
        if tier == 0:
            continue  # Skip base class
        print(f"\n{'─' * 70}")
        print(f"🎯 TIER {tier}: {tier_names.get(tier, 'Unknown')}")
        print(f"{'─' * 70}")
        
        for agent in registry.agents:
            if agent.tier == tier:
                print(f"  • {agent.name}")
                print(f"    Model: {agent.model}")
                if agent.capabilities:
                    caps = ", ".join(cap.name for cap in agent.capabilities)
                    print(f"    Capabilities: {caps}")
                print(f"    File: {Path(agent.file_path).name}:{agent.line_number}")
    
    print("\n" + "=" * 70)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Default paths
    inventory_path = sys.argv[1] if len(sys.argv) > 1 else \
        "/Users/yacinebenhamou/aSiReM/azirem_discovery/inventory_frozen.json"
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else \
        "/Users/yacinebenhamou/aSiReM/azirem_registry/agents_frozen.json"
    
    # Build and freeze registry
    manager = RegistryManager(inventory_path)
    
    if manager.load_inventory():
        registry = manager.build_registry()
        print_registry_summary(registry)
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        manager.freeze_registry(output_path)
