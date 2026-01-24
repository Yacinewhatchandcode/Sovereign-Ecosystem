#!/usr/bin/env python3
"""
AZIREM Master Orchestrator
==========================
Minimal orchestrator that coordinates agents ONLY after inventory is frozen.
Rule: inventory → map → freeze → orchestrate → intelligence

This is the SINGLE control point for agent execution.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import importlib.util


# ============================================================================
# ORCHESTRATION STATE
# ============================================================================

class Phase(Enum):
    """AZIREM execution phases."""
    INIT = "init"                # Just created
    INVENTORY_LOADED = "inventory_loaded"
    REGISTRY_LOADED = "registry_loaded"
    FROZEN = "frozen"            # Ready to orchestrate
    EXECUTING = "executing"      # Active task execution
    COMPLETE = "complete"        # Task finished
    ERROR = "error"


@dataclass
class TaskResult:
    """Result from an agent task."""
    agent_id: str
    task_id: str
    status: str  # success, error, timeout
    output: Any
    execution_time_ms: int
    timestamp: str


@dataclass
class ExecutionPlan:
    """Plan for executing a workflow."""
    plan_id: str
    workflow_name: str
    steps: List[Dict[str, Any]]  # Ordered list of agent calls
    created_at: str


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class MasterOrchestrator:
    """
    The SINGLE control point for the AZIREM ecosystem.
    
    Enforces the rule: inventory → map → freeze → orchestrate → intelligence
    
    Key principles:
    1. NEVER call agents before inventory is frozen
    2. NEVER modify source files - read-only access
    3. ALWAYS route through the frozen registry
    """
    
    def __init__(self, discovery_path: str, registry_path: str):
        self.discovery_path = Path(discovery_path)
        self.registry_path = Path(registry_path)
        
        self.inventory: Optional[Dict] = None
        self.registry: Optional[Dict] = None
        self.phase: Phase = Phase.INIT
        
        self.execution_log: List[TaskResult] = []
        self.loaded_agents: Dict[str, Any] = {}  # Cached agent classes
        
        print("🎯 Master Orchestrator initialized")
        print(f"   Discovery: {self.discovery_path}")
        print(f"   Registry:  {self.registry_path}")
    
    # ========================================================================
    # PHASE 1: FREEZE VERIFICATION
    # ========================================================================
    
    def verify_freeze(self) -> bool:
        """
        Verify that inventory and registry are properly frozen.
        MUST be called before any orchestration.
        """
        print("\n🔒 Verifying frozen state...")
        
        # Check inventory exists
        if not self.discovery_path.exists():
            print(f"   ❌ Inventory not found: {self.discovery_path}")
            print("   Run: python azirem_discovery/scanner.py")
            self.phase = Phase.ERROR
            return False
        
        # Load inventory
        try:
            with open(self.discovery_path) as f:
                self.inventory = json.load(f)
            print(f"   ✅ Inventory loaded: {self.inventory.get('total_files', 0)} files")
            self.phase = Phase.INVENTORY_LOADED
        except Exception as e:
            print(f"   ❌ Failed to load inventory: {e}")
            self.phase = Phase.ERROR
            return False
        
        # Check registry exists
        if not self.registry_path.exists():
            print(f"   ❌ Registry not found: {self.registry_path}")
            print("   Run: python azirem_registry/registry_manager.py")
            self.phase = Phase.ERROR
            return False
        
        # Load registry
        try:
            with open(self.registry_path) as f:
                self.registry = json.load(f)
            print(f"   ✅ Registry loaded: {self.registry.get('total_agents', 0)} agents")
            self.phase = Phase.REGISTRY_LOADED
        except Exception as e:
            print(f"   ❌ Failed to load registry: {e}")
            self.phase = Phase.ERROR
            return False
        
        # Validate registry integrity
        agents = self.registry.get("agents", [])
        valid_agents = 0
        for agent in agents:
            file_path = agent.get("file_path")
            if file_path and Path(file_path).exists():
                valid_agents += 1
            else:
                print(f"   ⚠️  Agent file missing: {file_path}")
        
        if valid_agents == 0:
            print("   ❌ No valid agents found!")
            self.phase = Phase.ERROR
            return False
        
        print(f"   ✅ {valid_agents}/{len(agents)} agents validated")
        
        self.phase = Phase.FROZEN
        print("🔒 Freeze verified! Ready to orchestrate.")
        return True
    
    # ========================================================================
    # PHASE 2: AGENT DISCOVERY
    # ========================================================================
    
    def list_agents(self, tier: Optional[int] = None) -> List[Dict]:
        """List available agents from frozen registry."""
        if self.phase != Phase.FROZEN:
            print("⚠️  Cannot list agents: not in frozen state")
            return []
        
        agents = self.registry.get("agents", [])
        
        if tier is not None:
            agents = [a for a in agents if a.get("tier") == tier]
        
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID from frozen registry."""
        if self.phase != Phase.FROZEN:
            return None
        
        for agent in self.registry.get("agents", []):
            if agent.get("id") == agent_id:
                return agent
        return None
    
    def get_agents_for_capability(self, capability: str) -> List[Dict]:
        """Find agents with a specific capability."""
        if self.phase != Phase.FROZEN:
            return []
        
        matching = []
        for agent in self.registry.get("agents", []):
            for cap in agent.get("capabilities", []):
                if cap.get("name") == capability:
                    matching.append(agent)
                    break
        return matching
    
    # ========================================================================
    # PHASE 3: TASK ROUTING
    # ========================================================================
    
    def create_execution_plan(self, 
                              workflow_name: str, 
                              steps: List[Dict]) -> ExecutionPlan:
        """
        Create an execution plan for a workflow.
        
        Args:
            workflow_name: Human-readable name
            steps: List of step definitions, each with:
                   - agent_id: Which agent to call
                   - task: Task description
                   - inputs: Dict of inputs (optional)
                   - depends_on: List of step indices (optional)
        """
        if self.phase != Phase.FROZEN:
            raise RuntimeError("Cannot create plan: not in frozen state")
        
        # Validate all agents exist
        for i, step in enumerate(steps):
            agent_id = step.get("agent_id")
            if not self.get_agent(agent_id):
                raise ValueError(f"Step {i}: Unknown agent '{agent_id}'")
        
        plan = ExecutionPlan(
            plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_name=workflow_name,
            steps=steps,
            created_at=datetime.now().isoformat()
        )
        
        print(f"\n📋 Execution plan created: {plan.plan_id}")
        print(f"   Workflow: {workflow_name}")
        print(f"   Steps: {len(steps)}")
        
        return plan
    
    def execute_plan(self, plan: ExecutionPlan, dry_run: bool = True) -> List[TaskResult]:
        """
        Execute an agent workflow plan.
        
        Args:
            plan: The execution plan
            dry_run: If True, simulate execution without calling agents
        """
        if self.phase not in [Phase.FROZEN, Phase.EXECUTING]:
            raise RuntimeError(f"Cannot execute: invalid phase {self.phase}")
        
        self.phase = Phase.EXECUTING
        results = []
        
        print(f"\n🚀 Executing plan: {plan.plan_id}")
        print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        
        for i, step in enumerate(plan.steps):
            agent_id = step.get("agent_id")
            task = step.get("task", "")
            
            print(f"\n   Step {i+1}: {agent_id}")
            print(f"   Task: {task[:50]}...")
            
            start_time = datetime.now()
            
            if dry_run:
                # Simulate execution
                output = f"[DRY RUN] Agent {agent_id} would execute: {task}"
                status = "success"
            else:
                # Real execution (to be implemented)
                try:
                    output = self._call_agent(agent_id, task, step.get("inputs", {}))
                    status = "success"
                except Exception as e:
                    output = str(e)
                    status = "error"
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            result = TaskResult(
                agent_id=agent_id,
                task_id=f"{plan.plan_id}_step_{i}",
                status=status,
                output=output,
                execution_time_ms=execution_time,
                timestamp=datetime.now().isoformat()
            )
            
            results.append(result)
            self.execution_log.append(result)
            
            print(f"   Status: {status} ({execution_time}ms)")
        
        self.phase = Phase.COMPLETE
        print(f"\n✅ Plan execution complete: {len(results)} steps")
        
        return results
    
    def _call_agent(self, agent_id: str, task: str, inputs: Dict) -> Any:
        """
        Actually call an agent (system_value for real implementation).
        This will integrate with Ollama + existing agent classes.
        """
        # For now, return system_value
        # Real implementation will:
        # 1. Load agent class dynamically
        # 2. Initialize with Ollama model
        # 3. Execute task
        # 4. Return result
        return f"[SYSTEM_VALUE] Agent {agent_id} executed: {task}"
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_execution_log(self) -> List[Dict]:
        """Get the full execution log."""
        return [
            {
                "agent_id": r.agent_id,
                "task_id": r.task_id,
                "status": r.status,
                "execution_time_ms": r.execution_time_ms,
                "timestamp": r.timestamp
            }
            for r in self.execution_log
        ]
    
    def export_execution_log(self, output_path: str) -> None:
        """Export execution log to JSON."""
        log_data = {
            "exported_at": datetime.now().isoformat(),
            "total_tasks": len(self.execution_log),
            "tasks": self.get_execution_log()
        }
        
        with open(output_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"📄 Execution log exported to: {output_path}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_default_orchestrator() -> MasterOrchestrator:
    """Create orchestrator with default AZIREM paths."""
    return MasterOrchestrator(
        discovery_path="/Users/yacinebenhamou/aSiReM/azirem_discovery/inventory_frozen.json",
        registry_path="/Users/yacinebenhamou/aSiReM/azirem_registry/agents_frozen.json"
    )


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🌌 AZIREM MASTER ORCHESTRATOR")
    print("=" * 70)
    
    # Create orchestrator
    orchestrator = create_default_orchestrator()
    
    # Verify freeze (REQUIRED before any orchestration)
    if not orchestrator.verify_freeze():
        print("\n❌ Cannot proceed: freeze verification failed")
        exit(1)
    
    # Show available agents
    print("\n" + "-" * 70)
    print("📋 AVAILABLE AGENTS BY TIER")
    print("-" * 70)
    
    tier_names = {1: "Strategic", 2: "Execution", 3: "Specialist"}
    for tier in [1, 2, 3]:
        agents = orchestrator.list_agents(tier=tier)
        if agents:
            print(f"\n🎯 Tier {tier}: {tier_names[tier]}")
            for agent in agents:
                print(f"   • {agent['id']}: {agent['name']}")
                print(f"     Model: {agent['model']}")
    
    # Demo: Create and execute a simple plan (dry run)
    print("\n" + "-" * 70)
    print("🧪 DEMO: DRY RUN EXECUTION")
    print("-" * 70)
    
    plan = orchestrator.create_execution_plan(
        workflow_name="Simple Research → Code Workflow",
        steps=[
            {
                "agent_id": "agent_bumblebee",
                "task": "Research best practices for Python agent orchestration in 2026",
                "inputs": {}
            },
            {
                "agent_id": "agent_azirem",
                "task": "Generate orchestration code based on research findings",
                "inputs": {},
                "depends_on": [0]
            }
        ]
    )
    
    # Execute (dry run)
    results = orchestrator.execute_plan(plan, dry_run=True)
    
    # Show results
    print("\n" + "-" * 70)
    print("📊 EXECUTION RESULTS")
    print("-" * 70)
    for r in results:
        print(f"   {r.task_id}: {r.status} ({r.execution_time_ms}ms)")
    
    print("\n" + "=" * 70)
    print("✅ Orchestrator demo complete!")
    print("=" * 70)
