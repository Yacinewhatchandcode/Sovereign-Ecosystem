#!/usr/bin/env python3
"""
🧬 UNIFIED SYSTEM INTEGRATION
=============================
Bridges ALL aSiReM modules into the Sovereign Dashboard.

Integrates:
- azirem_agents/ - Core agents (MemoryAgent, DocGenAgent, etc.)
- azirem_evolution/ - AutonomousEvolutionEngine
- azirem_memory/ - RAGEngine, KnowledgeGraph
- azirem_orchestration/ - MasterOrchestrator, PipelineOrchestrator
- azirem_discovery/ - Scanner, Discovery CLI
- azirem_registry/ - RegistryManager
- autonomy_agents/ - 74 autonomy agents
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# MODULE IMPORTS (Lazy Loading)
# ============================================================================

_evolution_engine = None
_rag_engine = None
_master_orchestrator = None
_knowledge_graph = None
_registry_manager = None
_scanner = None

def get_evolution_engine():
    """Get the AutonomousEvolutionEngine."""
    global _evolution_engine
    if _evolution_engine is None:
        try:
            from azirem_evolution.evolution_engine import AutonomousEvolutionEngine
            _evolution_engine = AutonomousEvolutionEngine()
            print("🧬 Evolution Engine: CONNECTED")
        except Exception as e:
            print(f"⚠️ Evolution Engine failed: {e}")
    return _evolution_engine

def get_rag_engine():
    """Get the RAG Engine."""
    global _rag_engine
    if _rag_engine is None:
        try:
            from azirem_memory.rag_engine import RAGEngine
            _rag_engine = RAGEngine()
            print("📚 RAG Engine: CONNECTED")
        except Exception as e:
            print(f"⚠️ RAG Engine failed: {e}")
    return _rag_engine

def get_knowledge_graph():
    """Get the Knowledge Graph Builder (the graph itself is built on demand)."""
    global _knowledge_graph
    if _knowledge_graph is None:
        try:
            from azirem_memory.knowledge_graph import KnowledgeGraphBuilder
            _knowledge_graph = KnowledgeGraphBuilder()
            print("🕸️ Knowledge Graph Builder: CONNECTED")
        except Exception as e:
            print(f"⚠️ Knowledge Graph failed: {e}")
    return _knowledge_graph

def get_master_orchestrator():
    """Get the Master Orchestrator."""
    global _master_orchestrator
    if _master_orchestrator is None:
        try:
            from azirem_orchestration.master_orchestrator import create_default_orchestrator
            _master_orchestrator = create_default_orchestrator()
            print("🎭 Master Orchestrator: CONNECTED")
        except Exception as e:
            print(f"⚠️ Master Orchestrator failed: {e}")
    return _master_orchestrator

def get_registry_manager():
    """Get the Registry Manager."""
    global _registry_manager
    if _registry_manager is None:
        try:
            from azirem_registry.registry_manager import RegistryManager
            inventory_path = str(PROJECT_ROOT / "azirem_discovery" / "inventory_frozen.json")
            _registry_manager = RegistryManager(inventory_path)
            _registry_manager.load_inventory()
            _registry_manager.build_registry()
            print("📋 Registry Manager: CONNECTED")
        except Exception as e:
            print(f"⚠️ Registry Manager failed: {e}")
    return _registry_manager

def get_scanner():
    """Get the Discovery Scanner."""
    global _scanner
    if _scanner is None:
        try:
            from azirem_discovery.scanner import AZIREMScanner
            root_path = str(PROJECT_ROOT)
            _scanner = AZIREMScanner(root_path)
            print("🔍 Discovery Scanner: CONNECTED")
        except Exception as e:
            print(f"⚠️ Discovery Scanner failed: {e}")
    return _scanner


# ============================================================================
# UNIFIED INTEGRATION LAYER
# ============================================================================

@dataclass
class UnifiedSystemStatus:
    """Complete system status."""
    evolution_active: bool = False
    rag_documents: int = 0
    knowledge_nodes: int = 0
    orchestrator_ready: bool = False
    agents_registered: int = 0
    autonomy_agents: int = 74
    total_capabilities: int = 0

class UnifiedSystemIntegration:
    """
    🧬 Unified System Integration Layer
    
    Provides a single entry point to all aSiReM subsystems:
    - Evolution Engine for continuous learning
    - RAG Engine for document search
    - Knowledge Graph for entity relationships
    - Master Orchestrator for workflow execution
    - Registry Manager for agent inventory
    - Discovery Scanner for codebase analysis
    """
    
    def __init__(self):
        self.initialized = False
        self._components = {}
        
    async def initialize(self) -> bool:
        """Initialize all subsystems."""
        print("🧬 Initializing Unified System Integration...")
        
        # Load all components
        self._components = {
            "evolution": get_evolution_engine(),
            "rag": get_rag_engine(),
            "knowledge_graph": get_knowledge_graph(),
            "orchestrator": get_master_orchestrator(),
            "registry": get_registry_manager(),
            "scanner": get_scanner()
        }
        
        # Count successful loads
        loaded = sum(1 for v in self._components.values() if v is not None)
        print(f"✅ Unified Integration: {loaded}/6 components loaded")
        
        self.initialized = True
        return loaded > 0
        
    def get_status(self) -> UnifiedSystemStatus:
        """Get complete system status."""
        status = UnifiedSystemStatus()
        
        # Evolution Engine
        evolution = self._components.get("evolution")
        if evolution:
            try:
                status.evolution_active = True
            except:
                pass
                
        # RAG Engine
        rag = self._components.get("rag")
        if rag:
            try:
                stats = rag.get_stats()
                status.rag_documents = stats.get("total_documents", 0)
            except:
                pass
                
        # Knowledge Graph
        kg = self._components.get("knowledge_graph")
        if kg:
            try:
                status.knowledge_nodes = len(kg.nodes) if hasattr(kg, 'nodes') else 0
            except:
                pass
                
        # Orchestrator
        orch = self._components.get("orchestrator")
        if orch:
            status.orchestrator_ready = True
            
        # Registry
        registry = self._components.get("registry")
        if registry:
            try:
                agents = registry.list_agents() if hasattr(registry, 'list_agents') else []
                status.agents_registered = len(agents)
            except:
                pass
                
        return status
        
    # ========================================================================
    # EVOLUTION OPERATIONS
    # ========================================================================
    
    async def trigger_evolution_cycle(self) -> Dict[str, Any]:
        """Trigger one evolution cycle."""
        engine = self._components.get("evolution")
        if not engine:
            return {"success": False, "error": "Evolution Engine not available"}
            
        try:
            await engine.evolve_cycle()
            return {"success": True, "metrics": engine.metrics.__dict__}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def get_evolution_status(self) -> Dict[str, Any]:
        """Get evolution engine status."""
        engine = self._components.get("evolution")
        if not engine:
            return {"available": False}
            
        return engine.get_status()
        
    # ========================================================================
    # RAG OPERATIONS
    # ========================================================================
    
    async def index_directory(self, path: str) -> Dict[str, Any]:
        """Index a directory into RAG."""
        rag = self._components.get("rag")
        if not rag:
            return {"success": False, "error": "RAG Engine not available"}
            
        try:
            count = rag.index_directory(path)
            return {"success": True, "indexed_files": count}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def rag_search(self, query: str) -> Dict[str, Any]:
        """Search the RAG knowledge base."""
        rag = self._components.get("rag")
        if not rag:
            return {"success": False, "error": "RAG Engine not available"}
            
        try:
            results = rag.search(query)
            return {
                "success": True,
                "results": [
                    {"content": r.document.content[:500], "score": r.score}
                    for r in results
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def rag_query(self, question: str) -> Dict[str, Any]:
        """Query RAG with AI-generated answer."""
        rag = self._components.get("rag")
        if not rag:
            return {"success": False, "error": "RAG Engine not available"}
            
        try:
            response = rag.query(question)
            return {
                "success": True,
                "answer": response.answer,
                "sources": response.sources,
                "confidence": response.confidence
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    # ========================================================================
    # ORCHESTRATION OPERATIONS
    # ========================================================================
    
    async def create_workflow(self, name: str, steps: List[Dict]) -> Dict[str, Any]:
        """Create an execution workflow."""
        orch = self._components.get("orchestrator")
        if not orch:
            return {"success": False, "error": "Orchestrator not available"}
            
        try:
            plan = orch.create_execution_plan(name, steps)
            return {"success": True, "plan_id": plan.plan_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def execute_workflow(self, plan_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a workflow plan."""
        orch = self._components.get("orchestrator")
        if not orch:
            return {"success": False, "error": "Orchestrator not available"}
            
        try:
            results = orch.execute_plan(plan_id, dry_run=dry_run)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def list_available_agents(self) -> Dict[str, Any]:
        """List all available agents from registry."""
        orch = self._components.get("orchestrator")
        if not orch:
            return {"success": False, "error": "Orchestrator not available"}
            
        try:
            agents = orch.list_agents()
            return {"success": True, "agents": agents}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    # ========================================================================
    # DISCOVERY OPERATIONS
    # ========================================================================
    
    async def scan_codebase(self, path: str) -> Dict[str, Any]:
        """Scan codebase for agents and patterns."""
        scanner = self._components.get("scanner")
        if not scanner:
            return {"success": False, "error": "Scanner not available"}
            
        try:
            results = scanner.scan(path)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
            

# ============================================================================
# SINGLETON
# ============================================================================

_unified_integration: Optional[UnifiedSystemIntegration] = None

def get_unified_integration() -> UnifiedSystemIntegration:
    """Get or create the unified integration instance."""
    global _unified_integration
    if _unified_integration is None:
        _unified_integration = UnifiedSystemIntegration()
    return _unified_integration


# ============================================================================
# INTEGRATION STATUS CHECK
# ============================================================================

def check_all_modules() -> Dict[str, bool]:
    """Check which modules are available."""
    modules = {}
    
    # Check azirem_evolution
    try:
        from azirem_evolution.evolution_engine import AutonomousEvolutionEngine
        modules["evolution_engine"] = True
    except ImportError:
        modules["evolution_engine"] = False
        
    # Check azirem_memory
    try:
        from azirem_memory.rag_engine import RAGEngine
        modules["rag_engine"] = True
    except ImportError:
        modules["rag_engine"] = False
        
    try:
        from azirem_memory.knowledge_graph import KnowledgeGraph
        modules["knowledge_graph"] = True
    except ImportError:
        modules["knowledge_graph"] = False
        
    # Check azirem_orchestration
    try:
        from azirem_orchestration.master_orchestrator import MasterOrchestrator
        modules["master_orchestrator"] = True
    except ImportError:
        modules["master_orchestrator"] = False
        
    try:
        from azirem_orchestration.pipeline_orchestrator import PipelineOrchestrator
        modules["pipeline_orchestrator"] = True
    except ImportError:
        modules["pipeline_orchestrator"] = False
        
    # Check azirem_discovery
    try:
        from azirem_discovery.scanner import AgentScanner
        modules["scanner"] = True
    except ImportError:
        modules["scanner"] = False
        
    # Check azirem_registry
    try:
        from azirem_registry.registry_manager import RegistryManager
        modules["registry_manager"] = True
    except ImportError:
        modules["registry_manager"] = False
        
    # Check autonomy_agents
    try:
        from autonomy_agents.autonomy_mesh_registry import AGENT_REGISTRY
        modules["autonomy_agents"] = True
        modules["autonomy_agent_count"] = len(AGENT_REGISTRY)
    except ImportError:
        modules["autonomy_agents"] = False
        modules["autonomy_agent_count"] = 0
        
    return modules


if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("🧬 UNIFIED SYSTEM INTEGRATION CHECK")
    print("=" * 60)
    
    modules = check_all_modules()
    
    for module, status in modules.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {module}: {status}")
        
    print("\n" + "=" * 60)
    
    # Initialize and show status
    async def test():
        integration = get_unified_integration()
        await integration.initialize()
        status = integration.get_status()
        print(f"\n📊 System Status:")
        print(f"  Evolution Active: {status.evolution_active}")
        print(f"  RAG Documents: {status.rag_documents}")
        print(f"  Knowledge Nodes: {status.knowledge_nodes}")
        print(f"  Orchestrator Ready: {status.orchestrator_ready}")
        print(f"  Agents Registered: {status.agents_registered}")
        print(f"  Autonomy Agents: {status.autonomy_agents}")
        
    asyncio.run(test())
