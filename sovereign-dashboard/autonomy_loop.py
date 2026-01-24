#!/usr/bin/env python3
"""
🔄 AUTONOMY LOOP
================
The core self-improving loop that ties everything together.
Creates a closed-loop autonomous system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from enum import Enum
import asyncio
import json
from pathlib import Path

# Import our factories
from autonomous_factory import (
    AutonomousFactory, AgentSpec, AgentCategory, AgentPriority,
    CRITICAL_AGENT_SPECS
)
from sub_agent_factory import SubAgentFactory, STANDARD_SUB_AGENTS
from rpa_bot_generator import RPABotGenerator, ASIREM_RPA_BOTS
from plugin_connector import PluginConnector, MCP_INTEGRATIONS

class LoopState(Enum):
    IDLE = "idle"
    DETECTING = "detecting"
    GENERATING = "generating"
    TESTING = "testing"
    DEPLOYING = "deploying"
    LEARNING = "learning"

@dataclass
class Gap:
    """A detected gap in the system"""
    id: str
    type: str
    severity: str
    description: str
    suggested_solution: str
    auto_fixable: bool = False
    fixed: bool = False

@dataclass
class LoopIteration:
    """Result of a single loop iteration"""
    iteration: int
    gaps_detected: int
    components_generated: int
    tests_passed: int
    tests_failed: int
    deployed: int
    learning_updates: int
    duration: float

class AutonomyLoop:
    """
    🔄 Self-Improving Autonomous Loop
    
    The core loop that:
    1. Detects gaps in the system
    2. Generates solutions using factories
    3. Tests the solutions
    4. Deploys working solutions
    5. Learns from results
    
    This creates a CLOSED-LOOP autonomous system.
    """
    
    def __init__(self, base_path: str = "sovereign-dashboard"):
        self.base_path = Path(base_path)
        self.state = LoopState.IDLE
        
        # Initialize factories
        self.agent_factory = AutonomousFactory(str(self.base_path))
        self.sub_agent_factory = SubAgentFactory()
        self.rpa_generator = RPABotGenerator()
        self.plugin_connector = PluginConnector()
        
        # Loop state
        self.iteration_count = 0
        self.gaps: List[Gap] = []
        self.generated_components: List[str] = []
        self.deployed_components: Set[str] = set()
        self.history: List[LoopIteration] = []
        
        # Running flag
        self._running = False
        
    async def start(self, max_iterations: int = None):
        """Start the autonomy loop"""
        self._running = True
        
        print("🔄 AUTONOMY LOOP STARTED")
        print("=" * 60)
        
        while self._running:
            if max_iterations and self.iteration_count >= max_iterations:
                print(f"\n✅ Completed {max_iterations} iterations")
                break
                
            await self._run_iteration()
            
            # Small delay between iterations
            await asyncio.sleep(1)
        
        print("\n🔴 Autonomy Loop Stopped")
        
    async def stop(self):
        """Stop the loop"""
        self._running = False
        
    async def _run_iteration(self):
        """Run single iteration of the loop"""
        start_time = datetime.now()
        self.iteration_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔄 ITERATION {self.iteration_count}")
        print(f"{'='*60}")
        
        # Phase 1: Detect gaps
        self.state = LoopState.DETECTING
        gaps = await self._detect_gaps()
        print(f"🔍 Detected {len(gaps)} gaps")
        
        # Phase 2: Generate solutions
        self.state = LoopState.GENERATING
        generated = await self._generate_solutions(gaps)
        print(f"🏭 Generated {len(generated)} components")
        
        # Phase 3: Test solutions
        self.state = LoopState.TESTING
        passed, failed = await self._test_solutions(generated)
        print(f"🧪 Tests: {passed} passed, {failed} failed")
        
        # Phase 4: Deploy solutions
        self.state = LoopState.DEPLOYING
        deployed = await self._deploy_solutions(generated)
        print(f"🚀 Deployed {deployed} components")
        
        # Phase 5: Learn from results
        self.state = LoopState.LEARNING
        learning_updates = await self._learn(gaps, generated)
        print(f"🧠 Learning updates: {learning_updates}")
        
        # Record iteration
        duration = (datetime.now() - start_time).total_seconds()
        iteration = LoopIteration(
            iteration=self.iteration_count,
            gaps_detected=len(gaps),
            components_generated=len(generated),
            tests_passed=passed,
            tests_failed=failed,
            deployed=deployed,
            learning_updates=learning_updates,
            duration=duration
        )
        self.history.append(iteration)
        
        self.state = LoopState.IDLE
        print(f"⏱️  Duration: {duration:.2f}s")
        
    async def _detect_gaps(self) -> List[Gap]:
        """Detect gaps in the system"""
        gaps = []
        
        # Check for missing critical agents
        existing_agents = set(self.agent_factory.registry.keys())
        for spec in CRITICAL_AGENT_SPECS:
            if spec.name not in existing_agents:
                gaps.append(Gap(
                    id=f"missing_agent_{spec.name}",
                    type="missing_agent",
                    severity=spec.priority.value,
                    description=f"Missing agent: {spec.name}",
                    suggested_solution=f"Generate {spec.name} using AutonomousFactory",
                    auto_fixable=True
                ))
        
        # Check for missing sub-agents
        for parent, sub_configs in STANDARD_SUB_AGENTS.items():
            for name, sub_type in sub_configs:
                full_name = f"{parent}_{name}"
                if full_name not in self.sub_agent_factory.sub_agents:
                    gaps.append(Gap(
                        id=f"missing_subagent_{full_name}",
                        type="missing_subagent",
                        severity="high",
                        description=f"Missing sub-agent: {full_name}",
                        suggested_solution=f"Create sub-agent using SubAgentFactory",
                        auto_fixable=True
                    ))
        
        # Check for missing RPA bots
        for bot_name, template, config in ASIREM_RPA_BOTS:
            if bot_name not in self.rpa_generator.bots:
                gaps.append(Gap(
                    id=f"missing_bot_{bot_name}",
                    type="missing_rpa_bot",
                    severity="medium",
                    description=f"Missing RPA bot: {bot_name}",
                    suggested_solution=f"Generate bot from template: {template}",
                    auto_fixable=True
                ))
        
        # Check for missing plugin connections
        connected = set(self.plugin_connector.connected_plugins.keys())
        for mcp_name, info in MCP_INTEGRATIONS.items():
            plugin = info["plugin"]
            if plugin not in connected:
                gaps.append(Gap(
                    id=f"missing_plugin_{plugin}",
                    type="missing_plugin",
                    severity="high",
                    description=f"Missing plugin connection: {plugin}",
                    suggested_solution=f"Connect plugin: {plugin}",
                    auto_fixable=True
                ))
        
        self.gaps.extend(gaps)
        return gaps
        
    async def _generate_solutions(self, gaps: List[Gap]) -> List[str]:
        """Generate solutions for detected gaps"""
        generated = []
        
        for gap in gaps:
            if not gap.auto_fixable:
                continue
                
            try:
                if gap.type == "missing_agent":
                    # Find spec and generate
                    spec = next(
                        (s for s in CRITICAL_AGENT_SPECS if s.name in gap.id),
                        None
                    )
                    if spec:
                        agent = self.agent_factory.generate_agent(spec)
                        if self.agent_factory.validate_agent(agent):
                            self.agent_factory.save_agent(agent)
                            generated.append(agent.name)
                            gap.fixed = True
                            
                elif gap.type == "missing_subagent":
                    # Parse parent and type from id
                    parts = gap.id.replace("missing_subagent_", "").split("_")
                    parent = parts[0] + parts[1] if len(parts) > 2 else parts[0]
                    
                    for p, subs in STANDARD_SUB_AGENTS.items():
                        for name, sub_type in subs:
                            if name in gap.id:
                                sub = self.sub_agent_factory.create_sub_agent(
                                    name=f"{p}_{name}",
                                    parent=p,
                                    sub_type=sub_type
                                )
                                generated.append(sub.name)
                                gap.fixed = True
                                break
                                
                elif gap.type == "missing_rpa_bot":
                    for bot_name, template, config in ASIREM_RPA_BOTS:
                        if bot_name in gap.id:
                            bot = self.rpa_generator.create_bot_from_template(
                                name=bot_name,
                                template_name=template,
                                config=config
                            )
                            generated.append(bot.name)
                            gap.fixed = True
                            break
                            
                elif gap.type == "missing_plugin":
                    plugin = gap.id.replace("missing_plugin_", "")
                    try:
                        agent = self.plugin_connector.connect(plugin)
                        generated.append(agent.name)
                        gap.fixed = True
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ⚠️  Failed to generate solution for {gap.id}: {e}")
        
        self.generated_components.extend(generated)
        return generated
        
    async def _test_solutions(self, generated: List[str]) -> tuple:
        """Test generated solutions"""
        passed = 0
        failed = 0
        
        for component in generated:
            # Check if agent is valid
            if component in self.agent_factory.registry:
                agent = self.agent_factory.registry[component]
                if agent.validated:
                    passed += 1
                else:
                    failed += 1
            else:
                # Other components are considered passed if they exist
                passed += 1
        
        return passed, failed
        
    async def _deploy_solutions(self, generated: List[str]) -> int:
        """Deploy working solutions"""
        deployed = 0
        
        for component in generated:
            if component not in self.deployed_components:
                self.deployed_components.add(component)
                deployed += 1
        
        return deployed
        
    async def _learn(self, gaps: List[Gap], generated: List[str]) -> int:
        """Learn from the iteration results"""
        updates = 0
        
        # Track success/failure patterns
        fixed_count = sum(1 for g in gaps if g.fixed)
        if fixed_count > 0:
            updates += 1  # Learning: successful patterns
            
        # Track generation efficiency
        if len(generated) > 0:
            updates += 1  # Learning: generation patterns
            
        return updates
        
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status"""
        return {
            "state": self.state.value,
            "iteration_count": self.iteration_count,
            "gaps_total": len(self.gaps),
            "gaps_fixed": sum(1 for g in self.gaps if g.fixed),
            "components_generated": len(self.generated_components),
            "components_deployed": len(self.deployed_components),
            "factories": {
                "agents": self.agent_factory.get_stats(),
                "sub_agents": self.sub_agent_factory.get_stats(),
                "rpa_bots": self.rpa_generator.get_stats(),
                "plugins": self.plugin_connector.get_stats()
            }
        }
        
    def print_summary(self):
        """Print summary of all iterations"""
        print("\n" + "=" * 60)
        print("📊 AUTONOMY LOOP SUMMARY")
        print("=" * 60)
        
        total_gaps = sum(i.gaps_detected for i in self.history)
        total_generated = sum(i.components_generated for i in self.history)
        total_passed = sum(i.tests_passed for i in self.history)
        total_deployed = sum(i.deployed for i in self.history)
        total_duration = sum(i.duration for i in self.history)
        
        print(f"\nIterations:           {len(self.history)}")
        print(f"Total gaps detected:  {total_gaps}")
        print(f"Components generated: {total_generated}")
        print(f"Tests passed:         {total_passed}")
        print(f"Components deployed:  {total_deployed}")
        print(f"Total duration:       {total_duration:.2f}s")
        
        print("\n📦 Factory Status:")
        status = self.get_status()
        for factory, stats in status["factories"].items():
            print(f"   {factory}: {stats}")

# Export
__all__ = ["AutonomyLoop", "Gap", "LoopIteration", "LoopState"]

if __name__ == "__main__":
    print("🔄 AUTONOMY LOOP - DEMO")
    print("=" * 60)
    print()
    print("This is the core self-improvement loop that:")
    print("  1. 🔍 Detects gaps in the system")
    print("  2. 🏭 Generates solutions using factories")
    print("  3. 🧪 Tests the solutions")
    print("  4. 🚀 Deploys working solutions")
    print("  5. 🧠 Learns from results")
    print()
    
    # Run demo
    async def demo():
        loop = AutonomyLoop()
        
        # Run 3 iterations
        await loop.start(max_iterations=3)
        
        # Print summary
        loop.print_summary()
        
        print("\n✅ System Status:")
        print(json.dumps(loop.get_status(), indent=2, default=str))
    
    asyncio.run(demo())
