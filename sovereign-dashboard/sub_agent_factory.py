#!/usr/bin/env python3
"""
👶 SUB-AGENT FACTORY
====================
Creates lightweight sub-agents for task decomposition under master agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import asyncio

class SubAgentState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class SubAgentTask:
    """Task for a sub-agent"""
    id: str
    name: str
    params: Dict[str, Any]
    parent_agent: str
    priority: int = 5
    timeout: float = 30.0

@dataclass
class SubAgentResult:
    """Result from sub-agent execution"""
    task_id: str
    success: bool
    data: Any
    execution_time: float
    error: Optional[str] = None

class SubAgent:
    """
    Lightweight sub-agent for specific tasks.
    Runs under a parent master agent.
    """
    
    def __init__(
        self,
        name: str,
        parent: str,
        task_handler: Callable,
        capabilities: List[str] = None
    ):
        self.name = name
        self.parent = parent
        self.task_handler = task_handler
        self.capabilities = capabilities or []
        self.state = SubAgentState.IDLE
        self.tasks_completed = 0
        self.created_at = datetime.now()
        
    async def execute(self, task: SubAgentTask) -> SubAgentResult:
        """Execute a task"""
        self.state = SubAgentState.RUNNING
        start_time = datetime.now()
        
        try:
            result = await asyncio.wait_for(
                self.task_handler(task.params),
                timeout=task.timeout
            )
            
            self.state = SubAgentState.COMPLETED
            self.tasks_completed += 1
            
            return SubAgentResult(
                task_id=task.id,
                success=True,
                data=result,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            
        except asyncio.TimeoutError:
            self.state = SubAgentState.FAILED
            return SubAgentResult(
                task_id=task.id,
                success=False,
                data=None,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error="Task timed out"
            )
        except Exception as e:
            self.state = SubAgentState.FAILED
            return SubAgentResult(
                task_id=task.id,
                success=False,
                data=None,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )

class SubAgentFactory:
    """
    👶 Factory for creating sub-agents
    
    Creates focused sub-agents that handle specific subtasks
    for master agents, enabling task decomposition.
    """
    
    # Sub-agent templates by purpose
    SUB_AGENT_TYPES = {
        "analyzer": {
            "description": "Analyzes data and returns insights",
            "capabilities": ["analyze", "report", "summarize"]
        },
        "validator": {
            "description": "Validates data against rules",
            "capabilities": ["validate", "check", "verify"]
        },
        "transformer": {
            "description": "Transforms data from one format to another",
            "capabilities": ["transform", "convert", "format"]
        },
        "fetcher": {
            "description": "Fetches data from sources",
            "capabilities": ["fetch", "retrieve", "load"]
        },
        "executor": {
            "description": "Executes actions/commands",
            "capabilities": ["execute", "run", "apply"]
        },
        "reporter": {
            "description": "Generates reports and summaries",
            "capabilities": ["report", "summarize", "format"]
        },
        "detector": {
            "description": "Detects patterns or issues",
            "capabilities": ["detect", "find", "identify"]
        },
        "fixer": {
            "description": "Fixes issues automatically",
            "capabilities": ["fix", "repair", "patch"]
        }
    }
    
    def __init__(self):
        self.sub_agents: Dict[str, SubAgent] = {}
        self.parent_mappings: Dict[str, List[str]] = {}
        
    def create_sub_agent(
        self,
        name: str,
        parent: str,
        sub_type: str,
        custom_handler: Callable = None
    ) -> SubAgent:
        """Create a new sub-agent"""
        
        if sub_type not in self.SUB_AGENT_TYPES:
            raise ValueError(f"Unknown sub-agent type: {sub_type}")
            
        type_info = self.SUB_AGENT_TYPES[sub_type]
        
        # Use custom handler or create default
        handler = custom_handler or self._create_default_handler(sub_type)
        
        # Create sub-agent
        sub_agent = SubAgent(
            name=name,
            parent=parent,
            task_handler=handler,
            capabilities=type_info["capabilities"]
        )
        
        # Register
        self.sub_agents[name] = sub_agent
        
        if parent not in self.parent_mappings:
            self.parent_mappings[parent] = []
        self.parent_mappings[parent].append(name)
        
        return sub_agent
    
    def _create_default_handler(self, sub_type: str) -> Callable:
        """Create default handler for sub-agent type"""
        
        async def analyzer_handler(params: Dict) -> Dict:
            return {"analysis": "completed", "params": params}
            
        async def validator_handler(params: Dict) -> Dict:
            return {"valid": True, "params": params}
            
        async def transformer_handler(params: Dict) -> Dict:
            return {"transformed": params}
            
        async def fetcher_handler(params: Dict) -> Dict:
            return {"data": None, "source": params.get("source")}
            
        async def executor_handler(params: Dict) -> Dict:
            return {"executed": True, "command": params.get("command")}
            
        async def reporter_handler(params: Dict) -> Dict:
            return {"report": "Generated report", "params": params}
            
        async def detector_handler(params: Dict) -> Dict:
            return {"detected": [], "params": params}
            
        async def fixer_handler(params: Dict) -> Dict:
            return {"fixed": True, "params": params}
        
        handlers = {
            "analyzer": analyzer_handler,
            "validator": validator_handler,
            "transformer": transformer_handler,
            "fetcher": fetcher_handler,
            "executor": executor_handler,
            "reporter": reporter_handler,
            "detector": detector_handler,
            "fixer": fixer_handler,
        }
        
        return handlers.get(sub_type, analyzer_handler)
    
    def get_sub_agents_for_parent(self, parent: str) -> List[SubAgent]:
        """Get all sub-agents for a parent"""
        names = self.parent_mappings.get(parent, [])
        return [self.sub_agents[name] for name in names if name in self.sub_agents]
    
    def create_standard_sub_agents(self, parent: str) -> List[SubAgent]:
        """Create standard set of sub-agents for a parent"""
        created = []
        
        for sub_type in ["analyzer", "validator", "executor", "reporter"]:
            name = f"{parent}_{sub_type}"
            sub_agent = self.create_sub_agent(name, parent, sub_type)
            created.append(sub_agent)
            
        return created
    
    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        return {
            "total_sub_agents": len(self.sub_agents),
            "total_parents": len(self.parent_mappings),
            "by_state": {
                state.value: sum(
                    1 for sa in self.sub_agents.values() 
                    if sa.state == state
                )
                for state in SubAgentState
            },
            "tasks_completed": sum(
                sa.tasks_completed for sa in self.sub_agents.values()
            )
        }

# Pre-defined sub-agent configurations for critical master agents
STANDARD_SUB_AGENTS = {
    "ErrorAutoFixAgent": [
        ("syntax_error_detector", "detector"),
        ("runtime_error_detector", "detector"),
        ("logic_error_detector", "detector"),
        ("fix_generator", "fixer"),
        ("fix_validator", "validator"),
    ],
    "CodeQualityLoopAgent": [
        ("complexity_analyzer", "analyzer"),
        ("duplication_detector", "detector"),
        ("naming_validator", "validator"),
        ("refactoring_executor", "executor"),
    ],
    "UIAutoGeneratorAgent": [
        ("form_generator", "transformer"),
        ("list_generator", "transformer"),
        ("detail_generator", "transformer"),
        ("component_validator", "validator"),
    ],
    "PatternLearnerAgent": [
        ("pattern_detector", "detector"),
        ("pattern_analyzer", "analyzer"),
        ("knowledge_reporter", "reporter"),
    ],
}

# Export
__all__ = [
    "SubAgentFactory",
    "SubAgent",
    "SubAgentTask",
    "SubAgentResult",
    "SubAgentState",
    "STANDARD_SUB_AGENTS"
]

if __name__ == "__main__":
    # Demo
    factory = SubAgentFactory()
    
    print("👶 SUB-AGENT FACTORY")
    print("=" * 60)
    
    for parent, sub_configs in STANDARD_SUB_AGENTS.items():
        print(f"\n📦 Parent: {parent}")
        for name, sub_type in sub_configs:
            sub_agent = factory.create_sub_agent(
                name=f"{parent}_{name}",
                parent=parent,
                sub_type=sub_type
            )
            print(f"   ✅ Created: {sub_agent.name} ({sub_type})")
    
    print("\n📊 Stats:", factory.get_stats())
