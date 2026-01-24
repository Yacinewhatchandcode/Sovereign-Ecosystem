#!/usr/bin/env python3
"""
🧬 AZIREM AUTONOMOUS EVOLUTION ENGINE
=====================================
Self-growing, self-learning, self-expanding agent ecosystem.
Runs continuously to evolve the system intelligence.

INTEGRATES ALL AZIREM COMPONENTS:
- Ollama Executor (real LLM reasoning)
- RAG Engine (knowledge retrieval)
- MCP Bridge (GitHub/Supabase/Perplexity tools)
- Cold Azirem (AZIREM/BumbleBee/Spectra agents)
- Knowledge Graph (entity extraction)
- Pipeline Orchestrator (workflow execution)

The Prime Directive: GROW. LEARN. EXPAND. EVOLVE.
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import random

# Add paths
AZIREM_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AZIREM_ROOT))

# Import AZIREM components (lazy loaded)
_ollama_executor = None
_rag_engine = None
_mcp_bridge = None
_cold_bridge = None
_knowledge_builder = None

def get_ollama():
    global _ollama_executor
    if _ollama_executor is None:
        try:
            from azirem_agents.ollama_executor import AgentExecutor
            _ollama_executor = AgentExecutor()
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
    return _ollama_executor

def get_rag():
    global _rag_engine
    if _rag_engine is None:
        try:
            from azirem_memory.rag_engine import RAGEngine
            _rag_engine = RAGEngine()
        except Exception as e:
            print(f"⚠️ RAG not available: {e}")
    return _rag_engine

def get_mcp():
    global _mcp_bridge
    if _mcp_bridge is None:
        try:
            from azirem_orchestration.mcp_bridge import AgentMCPIntegration
            _mcp_bridge = AgentMCPIntegration()
        except Exception as e:
            print(f"⚠️ MCP not available: {e}")
    return _mcp_bridge

def get_cold_azirem():
    global _cold_bridge
    if _cold_bridge is None:
        try:
            from azirem_orchestration.cold_integration import ColdAziremBridge
            _cold_bridge = ColdAziremBridge()
        except Exception as e:
            print(f"⚠️ Cold Azirem not available: {e}")
    return _cold_bridge

def get_knowledge_graph():
    global _knowledge_builder
    if _knowledge_builder is None:
        try:
            from azirem_memory.knowledge_graph import KnowledgeGraphBuilder
            _knowledge_builder = KnowledgeGraphBuilder()
        except Exception as e:
            print(f"⚠️ Knowledge Graph not available: {e}")
    return _knowledge_builder


# ============================================================================
# EVOLUTION CORE
# ============================================================================

class EvolutionPhase(Enum):
    """Phases of autonomous evolution."""
    DORMANT = "dormant"
    SCANNING = "scanning"
    LEARNING = "learning"
    EXPANDING = "expanding"
    EVOLVING = "evolving"
    OPTIMIZING = "optimizing"


@dataclass
class DiscoveredPattern:
    """A pattern discovered during evolution."""
    pattern_id: str
    pattern_type: str  # code, architecture, workflow, insight
    source: str
    content: str
    confidence: float
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    learned: bool = False


@dataclass
class EvolutionMetrics:
    """Metrics for evolution tracking."""
    files_scanned: int = 0
    patterns_discovered: int = 0
    knowledge_items_created: int = 0
    agents_spawned: int = 0
    self_improvements: int = 0
    uptime_seconds: int = 0
    cycles_completed: int = 0


@dataclass
class AgentCapability:
    """A capability that can be learned."""
    name: str
    description: str
    code_template: str
    learned_from: str
    mastery_level: float = 0.0


# ============================================================================
# AUTONOMOUS EVOLUTION ENGINE
# ============================================================================

class AutonomousEvolutionEngine:
    """
    🧬 The Autonomous Evolution Engine
    
    Core capabilities:
    1. SCAN - Continuously discover new code and patterns
    2. LEARN - Extract knowledge from discoveries
    3. EXPAND - Grow the knowledge graph
    4. EVOLVE - Improve agents and capabilities
    5. HEAL - Self-repair and optimize
    """
    
    def __init__(self, root_path: str = "/Users/yacinebenhamou"):
        self.root_path = Path(root_path)
        self.azirem_path = self.root_path / "aSiReM"
        self.evolution_path = self.azirem_path / "azirem_evolution"
        self.evolution_path.mkdir(exist_ok=True)
        
        # State
        self.phase = EvolutionPhase.DORMANT
        self.metrics = EvolutionMetrics()
        self.discovered_patterns: Dict[str, DiscoveredPattern] = {}
        self.learned_capabilities: Dict[str, AgentCapability] = {}
        self.knowledge_graph: Dict[str, List[str]] = defaultdict(list)
        
        # Evolution parameters
        self.scan_interval = 300  # 5 minutes
        self.learn_threshold = 10  # Patterns before learning
        self.evolution_rate = 0.1  # Rate of capability improvement
        
        # Running state
        self.running = False
        self.start_time = None
        self.last_scan = None
        
        # Callbacks
        self.on_discovery: Optional[Callable] = None
        self.on_evolution: Optional[Callable] = None
        
        # Load previous state
        self._load_state()
    
    def _load_state(self):
        """Load previous evolution state."""
        state_file = self.evolution_path / "evolution_state.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                self.metrics.cycles_completed = data.get("cycles_completed", 0)
                self.metrics.patterns_discovered = data.get("patterns_discovered", 0)
                print(f"🧬 Loaded evolution state: {self.metrics.cycles_completed} cycles completed")
            except:
                pass
    
    def _save_state(self):
        """Save evolution state."""
        state_file = self.evolution_path / "evolution_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                "cycles_completed": self.metrics.cycles_completed,
                "patterns_discovered": self.metrics.patterns_discovered,
                "knowledge_items": self.metrics.knowledge_items_created,
                "last_update": datetime.now().isoformat(),
            }, f, indent=2)
    
    # ========================================================================
    # PHASE 1: SCANNING
    # ========================================================================
    
    def _scan_for_patterns(self) -> List[DiscoveredPattern]:
        """Scan the filesystem for new patterns."""
        self.phase = EvolutionPhase.SCANNING
        patterns = []
        
        # Directories to scan
        scan_dirs = [
            self.root_path / "aSiReM",
            self.root_path / "VoiceCloning",
            self.root_path / "Duix-Avatar",
            self.root_path / "Documents",
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            # Find Python files with agent patterns
            for py_file in scan_dir.rglob("*.py"):
                if any(x in str(py_file) for x in ['node_modules', '.git', '__pycache__', '.venv']):
                    continue
                
                pattern = self._analyze_file(py_file)
                if pattern:
                    patterns.append(pattern)
                    self.metrics.files_scanned += 1
        
        return patterns
    
    def _analyze_file(self, filepath: Path) -> Optional[DiscoveredPattern]:
        """Analyze a file for interesting patterns."""
        try:
            content = filepath.read_text(errors='ignore')
        except:
            return None
        
        # Skip small files
        if len(content) < 500:
            return None
        
        # Create hash to avoid duplicates
        pattern_id = hashlib.md5(content[:2000].encode()).hexdigest()
        if pattern_id in self.discovered_patterns:
            return None
        
        # Pattern detection
        patterns_found = []
        confidence = 0.0
        
        # Agent patterns
        if 'class' in content and 'Agent' in content:
            patterns_found.append("agent_class")
            confidence += 0.3
        
        # Orchestration patterns
        if 'async def' in content and ('orchestrat' in content.lower() or 'pipeline' in content.lower()):
            patterns_found.append("orchestration")
            confidence += 0.25
        
        # AI/ML patterns
        if any(x in content for x in ['ollama', 'langchain', 'openai', 'anthropic', 'llm']):
            patterns_found.append("ai_integration")
            confidence += 0.2
        
        # Self-improvement patterns
        if any(x in content.lower() for x in ['self_improve', 'evolve', 'learn', 'adapt']):
            patterns_found.append("self_evolution")
            confidence += 0.35
        
        if not patterns_found or confidence < 0.2:
            return None
        
        return DiscoveredPattern(
            pattern_id=pattern_id,
            pattern_type=patterns_found[0],
            source=str(filepath),
            content=content[:3000],
            confidence=min(confidence, 1.0)
        )
    
    # ========================================================================
    # PHASE 2: LEARNING (AI-POWERED)
    # ========================================================================
    
    def _learn_from_patterns(self, patterns: List[DiscoveredPattern]):
        """Learn from discovered patterns using AI."""
        self.phase = EvolutionPhase.LEARNING
        
        for pattern in patterns:
            if pattern.pattern_id in self.discovered_patterns:
                continue
            
            # Store pattern
            self.discovered_patterns[pattern.pattern_id] = pattern
            self.metrics.patterns_discovered += 1
            
            # Extract knowledge (basic)
            knowledge = self._extract_knowledge(pattern)
            if knowledge:
                self._add_to_knowledge_graph(knowledge)
                pattern.learned = True
            
            # AI-POWERED: Use Ollama to analyze high-value patterns (optional, non-blocking)
            if pattern.confidence >= 0.7:  # Only analyze very high confidence
                try:
                    insight = self._ai_analyze_pattern(pattern)
                    if insight:
                        self._store_insight(pattern.pattern_id, insight)
                except Exception as e:
                    pass  # Continue without AI analysis
            
            # Try to learn new capabilities
            capability = self._learn_capability(pattern)
            if capability:
                self.learned_capabilities[capability.name] = capability
                print(f"   🧠 Learned new capability: {capability.name}")
    
    def _ai_analyze_pattern(self, pattern: DiscoveredPattern) -> Optional[Dict]:
        """Use Ollama to analyze a pattern and extract deep insights."""
        executor = get_ollama()
        if not executor:
            return None
        
        # Quick check if Ollama is responsive
        status = executor.get_status()
        if not status.get("ollama_available"):
            return None
        
        # Use shorter prompt for speed
        prompt = f"""Analyze this code pattern briefly:
Source: {Path(pattern.source).name}
Type: {pattern.pattern_type}

Key insight (1-2 sentences):"""
        
        try:
            result = executor.execute("summarizer", prompt[:500])  # Limit prompt size
            if result.get("success"):
                return {
                    "analysis": result.get("output", "")[:500],
                    "pattern_id": pattern.pattern_id,
                }
        except:
            pass
        
        return None
    
    def _store_insight(self, pattern_id: str, insight: Dict):
        """Store an AI-generated insight."""
        insights_path = self.evolution_path / "ai_insights.json"
        insights = []
        if insights_path.exists():
            try:
                insights = json.loads(insights_path.read_text())
            except:
                pass
        
        insights.append({
            "pattern_id": pattern_id,
            "insight": insight,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Keep last 100 insights
        insights_path.write_text(json.dumps(insights[-100:], indent=2))
    
    def _route_to_cold_agent(self, task: str) -> Optional[Dict]:
        """Route a task to the appropriate Cold Azirem agent."""
        cold = get_cold_azirem()
        if not cold:
            return None
        
        # Route task
        routing = cold.route_task(task)
        plan = cold.create_execution_plan(task)
        
        return {
            "master": routing.get("master"),
            "reason": routing.get("reason"),
            "plan": plan,
        }
    
    def _rag_search(self, query: str) -> List[str]:
        """Search knowledge base using RAG."""
        rag = get_rag()
        if not rag:
            return []
        
        try:
            results = rag.search(query, top_k=3)
            return [r.document.content[:500] for r in results]
        except:
            return []
    
    def _extract_knowledge(self, pattern: DiscoveredPattern) -> Optional[Dict]:
        """Extract actionable knowledge from a pattern."""
        content = pattern.content
        
        # Extract class definitions
        classes = []
        for line in content.split('\n'):
            if line.strip().startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        
        # Extract function definitions
        functions = []
        for line in content.split('\n'):
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append(func_name)
        
        if not classes and not functions:
            return None
        
        return {
            "source": pattern.source,
            "pattern_type": pattern.pattern_type,
            "classes": classes[:10],
            "functions": functions[:20],
            "confidence": pattern.confidence,
        }
    
    def _learn_capability(self, pattern: DiscoveredPattern) -> Optional[AgentCapability]:
        """Try to learn a new capability from a pattern."""
        # Only learn from high-confidence patterns
        if pattern.confidence < 0.5:
            return None
        
        content = pattern.content
        
        # Look for useful patterns to learn
        if pattern.pattern_type == "orchestration":
            # Learn orchestration pattern
            return AgentCapability(
                name=f"orchestration_{pattern.pattern_id[:8]}",
                description="Learned orchestration pattern",
                code_template=content[:1000],
                learned_from=pattern.source,
                mastery_level=pattern.confidence
            )
        
        if pattern.pattern_type == "self_evolution":
            # Prioritize self-evolution patterns
            return AgentCapability(
                name=f"evolution_{pattern.pattern_id[:8]}",
                description="Self-evolution capability",
                code_template=content[:1000],
                learned_from=pattern.source,
                mastery_level=pattern.confidence * 1.5  # Bonus for evolution patterns
            )
        
        return None
    
    def _add_to_knowledge_graph(self, knowledge: Dict):
        """Add knowledge to the graph."""
        source = Path(knowledge["source"]).stem
        
        for cls in knowledge.get("classes", []):
            self.knowledge_graph[source].append(f"class:{cls}")
        
        for func in knowledge.get("functions", [])[:10]:
            self.knowledge_graph[source].append(f"func:{func}")
        
        self.metrics.knowledge_items_created += 1
    
    # ========================================================================
    # PHASE 3: EXPANDING
    # ========================================================================
    
    def _expand_capabilities(self):
        """Expand agent capabilities based on learned knowledge."""
        self.phase = EvolutionPhase.EXPANDING
        
        # Generate new agent configurations
        if self.metrics.patterns_discovered > 5:
            self._generate_evolved_agent()
    
    def _generate_evolved_agent(self):
        """Generate a new evolved agent from learned patterns."""
        if not self.learned_capabilities:
            return
        
        # Select best capabilities
        best_cap = max(
            self.learned_capabilities.values(),
            key=lambda c: c.mastery_level,
            default=None
        )
        
        if not best_cap:
            return
        
        # Create evolved agent definition
        evolved_agent = {
            "name": f"EvolvedAgent_{datetime.now().strftime('%H%M%S')}",
            "base": "BaseAgent",
            "learned_from": best_cap.learned_from,
            "capabilities": [c.name for c in list(self.learned_capabilities.values())[:5]],
            "mastery": best_cap.mastery_level,
            "created_at": datetime.now().isoformat(),
        }
        
        # Save evolved agent
        agents_path = self.evolution_path / "evolved_agents.json"
        agents = []
        if agents_path.exists():
            try:
                agents = json.loads(agents_path.read_text())
            except:
                pass
        
        agents.append(evolved_agent)
        agents_path.write_text(json.dumps(agents, indent=2))
        
        self.metrics.agents_spawned += 1
        print(f"   🦋 Spawned evolved agent: {evolved_agent['name']}")
    
    # ========================================================================
    # PHASE 4: EVOLVING
    # ========================================================================
    
    def _self_evolve(self):
        """Self-improvement through evolution."""
        self.phase = EvolutionPhase.EVOLVING
        
        # Improve mastery of capabilities
        for cap in self.learned_capabilities.values():
            cap.mastery_level = min(cap.mastery_level * (1 + self.evolution_rate), 1.0)
        
        # Optimize scan patterns based on what worked
        if self.metrics.patterns_discovered > 20:
            # Increase scan efficiency
            self.learn_threshold = max(5, self.learn_threshold - 1)
        
        self.metrics.self_improvements += 1
    
    # ========================================================================
    # PHASE 5: OPTIMIZING
    # ========================================================================
    
    def _optimize(self):
        """Optimize the evolution process."""
        self.phase = EvolutionPhase.OPTIMIZING
        
        # Clean up low-value patterns
        to_remove = []
        for pid, pattern in self.discovered_patterns.items():
            if pattern.confidence < 0.1 and not pattern.learned:
                to_remove.append(pid)
        
        for pid in to_remove[:10]:  # Limit cleanup
            del self.discovered_patterns[pid]
        
        # Save state
        self._save_state()
    
    # ========================================================================
    # MAIN EVOLUTION LOOP
    # ========================================================================
    
    def evolve_cycle(self):
        """Run one complete evolution cycle."""
        print(f"\n{'='*60}")
        print(f"🧬 EVOLUTION CYCLE {self.metrics.cycles_completed + 1}")
        print(f"{'='*60}")
        
        # Phase 1: Scan
        print("\n📡 Phase 1: SCANNING...")
        patterns = self._scan_for_patterns()
        print(f"   Discovered {len(patterns)} new patterns")
        
        # Phase 2: Learn
        print("\n🧠 Phase 2: LEARNING...")
        self._learn_from_patterns(patterns)
        print(f"   Total patterns: {self.metrics.patterns_discovered}")
        print(f"   Capabilities: {len(self.learned_capabilities)}")
        
        # Phase 3: Expand
        print("\n🌱 Phase 3: EXPANDING...")
        self._expand_capabilities()
        print(f"   Agents spawned: {self.metrics.agents_spawned}")
        
        # Phase 4: Evolve
        print("\n🦋 Phase 4: EVOLVING...")
        self._self_evolve()
        print(f"   Self-improvements: {self.metrics.self_improvements}")
        
        # Phase 5: Optimize
        print("\n⚡ Phase 5: OPTIMIZING...")
        self._optimize()
        
        self.metrics.cycles_completed += 1
        self.phase = EvolutionPhase.DORMANT
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✅ CYCLE COMPLETE")
        print(f"   Files scanned: {self.metrics.files_scanned}")
        print(f"   Patterns: {self.metrics.patterns_discovered}")
        print(f"   Knowledge items: {self.metrics.knowledge_items_created}")
        print(f"   Agents spawned: {self.metrics.agents_spawned}")
        print(f"{'='*60}")
    
    def start(self, continuous: bool = True, cycles: int = 1):
        """Start the evolution engine."""
        self.running = True
        self.start_time = datetime.now()
        
        print("\n" + "🧬" * 30)
        print("   AZIREM AUTONOMOUS EVOLUTION ENGINE")
        print("   Self-Growing | Self-Learning | Self-Expanding")
        print("🧬" * 30)
        
        if continuous:
            print(f"\n🌌 Starting continuous evolution...")
            print(f"   Scan interval: {self.scan_interval}s")
            print(f"   Press Ctrl+C to stop")
            
            try:
                while self.running:
                    self.evolve_cycle()
                    print(f"\n⏳ Next cycle in {self.scan_interval}s...")
                    time.sleep(self.scan_interval)
            except KeyboardInterrupt:
                print("\n\n🛑 Evolution stopped by user")
                self._save_state()
        else:
            for _ in range(cycles):
                self.evolve_cycle()
            self._save_state()
        
        # Final report
        uptime = (datetime.now() - self.start_time).total_seconds()
        self.metrics.uptime_seconds = int(uptime)
        
        print("\n" + "=" * 60)
        print("📊 EVOLUTION SESSION REPORT")
        print("=" * 60)
        print(f"   Uptime: {int(uptime)}s")
        print(f"   Cycles: {self.metrics.cycles_completed}")
        print(f"   Patterns discovered: {self.metrics.patterns_discovered}")
        print(f"   Capabilities learned: {len(self.learned_capabilities)}")
        print(f"   Agents spawned: {self.metrics.agents_spawned}")
        print("=" * 60)
    
    def stop(self):
        """Stop the evolution engine."""
        self.running = False
        self._save_state()
    
    def get_status(self) -> Dict:
        """Get current evolution status."""
        return {
            "phase": self.phase.value,
            "running": self.running,
            "metrics": asdict(self.metrics),
            "capabilities": len(self.learned_capabilities),
            "patterns": len(self.discovered_patterns),
            "knowledge_graph_size": sum(len(v) for v in self.knowledge_graph.values()),
        }


# ============================================================================
# DAEMON SERVICE
# ============================================================================

def run_as_daemon():
    """Run evolution engine as background daemon."""
    import subprocess
    
    # Create daemon script
    daemon_script = '''
import sys
sys.path.insert(0, "/Users/yacinebenhamou/aSiReM")
from azirem_evolution.evolution_engine import AutonomousEvolutionEngine

engine = AutonomousEvolutionEngine()
engine.scan_interval = 300  # 5 minutes
engine.start(continuous=True)
'''
    
    daemon_path = Path("/Users/yacinebenhamou/aSiReM/azirem_evolution/daemon.py")
    daemon_path.parent.mkdir(exist_ok=True)
    daemon_path.write_text(daemon_script)
    
    # Start as background process
    subprocess.Popen(
        [sys.executable, str(daemon_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    print("🧬 Evolution daemon started in background")
    print(f"   PID file: {daemon_path.parent / 'daemon.pid'}")


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AZIREM Autonomous Evolution Engine")
    parser.add_argument("--continuous", "-c", action="store_true", help="Run continuously")
    parser.add_argument("--cycles", "-n", type=int, default=1, help="Number of cycles (if not continuous)")
    parser.add_argument("--interval", "-i", type=int, default=300, help="Scan interval in seconds")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as background daemon")
    
    args = parser.parse_args()
    
    if args.daemon:
        run_as_daemon()
        return
    
    engine = AutonomousEvolutionEngine()
    engine.scan_interval = args.interval
    engine.start(continuous=args.continuous, cycles=args.cycles)


if __name__ == "__main__":
    main()
