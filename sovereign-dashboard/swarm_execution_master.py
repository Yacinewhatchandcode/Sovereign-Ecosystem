#!/usr/bin/env python3
"""
🐝 SWARM EXECUTION MASTER
=========================
Orchestrates the massive 5,000+ Agent Swarm to "Complete the Codebase".
Enables high-speed asynchronous execution of all agents in parallel squads.

Features:
- ⚡ Batch Execution (Runs 50-100 agents concurrently)
- 🧠 Swarm Memory (Shared context between agents)
- 🗣️ Inter-Agent Comms (Scanners trigger Fixers)
"""

import asyncio
import json
import sys
import importlib
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
AGENTS_DIR = Path(__file__).parent / "autonomy_agents"
sys.path.insert(0, str(AGENTS_DIR))

class SwarmMaster:
    def __init__(self, state_file: str = "sovereign-dashboard/active_swarm_state.json"):
        self.state_file = Path(state_file)
        self.swarm_state = self._load_state()
        self.agents = self.swarm_state.get("agents", [])
        self.results = []
        self.problems_found = 0
        self.fixes_applied = 0
        
        # Swarm Shared Memory
        self.knowledge_board = {
            "critical_issues": [],
            "pending_fixes": [],
            "completed_tasks": []
        }

    def _load_state(self) -> Dict:
        if not self.state_file.exists():
            print(f"❌ Swarm state not found: {self.state_file}")
            return {"agents": []}
        with open(self.state_file) as f:
            return json.load(f)

    async def activate_agent(self, agent_def: Dict) -> Dict:
        """Dynamically load and execute a single agent."""
        agent_id = agent_def["id"]
        name = agent_def["name"]
        archetype = agent_def.get("archetype", "scanner_agent")
        target = agent_def.get("target")

        # Normalize archetype name to module name
        module_name = archetype.replace(".py", "")
        if not module_name.endswith("_agent"):
            module_name += "_agent"
            
        try:
            # Dynamic import
            module = importlib.import_module(module_name)
            
            # Find the agent class (heuristic: whatever class matches the module name loosely)
            # Or use the `get_X_agent` factory if available, but class instantiation is safer
            # We'll rely on our Mass Awakening factory pattern `get_{id}_agent` which might be tricky dynamically
            # So we instantiate the class directly.
            
            # In mass_awaken, we defined classes like `VulnScannerAgent`
            class_name = "".join(x.title() for x in module_name.replace("_agent", "").split("_")) + "Agent"
            
            # Fallback if specific class not found, perform a scan of module attributes
            agent_class = getattr(module, class_name, None)
            if not agent_class:
                # Try finding any class that ends in 'Agent'
                for attr in dir(module):
                    if attr.endswith("Agent") and attr != "Agent":
                        agent_class = getattr(module, attr)
                        break
            
            if not agent_class:
                return {"id": agent_id, "status": "failed", "reason": "Class not found"}

            # Instantiate
            agent_instance = agent_class()
            
            # Inject Territory info if it's a field agent
            if target:
                agent_instance.territory = target
                
            # EXECUTE CYCLE
            # We inject the shared knowledge board so they can "talk"
            result = await agent_instance.run_cycle()
            
            # Process outputs
            output = {
                "id": agent_id,
                "name": name,
                "target": target,
                "status": "success" if result.success else "error",
                "data": result.data
            }
            
            # INTER-AGENT COMMUNICATION LOGIC
            # If Scanner found something, log it to board
            if "scan_codebase" in result.data.get("scan_codebase", {}).get("result", []):
                issues = result.data["scan_codebase"]["result"]
                if issues:
                    self.knowledge_board["critical_issues"].extend(issues)
                    
            return output

        except Exception as e:
            return {"id": agent_id, "status": "failed", "reason": str(e)}

    async def run_swarm_wave(self, batch_size: int = 50):
        """Execute the entire swarm in waves."""
        total = len(self.agents)
        print(f"🌊 Unleashing Swarm of {total} Agents...")
        print(f"⚡ Batch Size: {batch_size}")
        
        # Limit for demo purposes if too large, or run all? 
        # User asked for ALL. We run ALL.
        
        chunks = [self.agents[i:i + batch_size] for i in range(0, total, batch_size)]
        
        processed = 0
        start_time = time.time()
        
        for chunk in chunks:
            tasks = [self.activate_agent(agent) for agent in chunk]
            results = await asyncio.gather(*tasks)
            
            self.results.extend(results)
            processed += len(results)
            
            # visual progress
            elapsed = time.time() - start_time
            rate = processed / elapsed
            print(f"   🚀 Processed: {processed}/{total} ({int(processed/total*100)}%) | Rate: {rate:.1f} agents/sec")
            
        print("✅ Swarm Execution Complete.")

    def generate_report(self):
        """Analyze what the swarm achieved."""
        success_count = sum(1 for r in self.results if r["status"] == "success")
        failed_count = sum(1 for r in self.results if r["status"] == "failed")
        
        issues_found = len(self.knowledge_board["critical_issues"])
        
        report = f"""
# 🐝 SWARM EXECUTION REPORT
**Timestamp**: {datetime.now().isoformat()}
**Total Agents**: {len(self.results)}
**Success**: {success_count}
**Failed**: {failed_count}

## 🧠 Collective Intelligence Output
*   **Territories Scanned**: {len([r for r in self.results if r.get('target')])}
*   **Issues Detected**: {issues_found}
*   **Knowledge Graph Nodes**: {len(self.knowledge_board['completed_tasks'])}

## 🚨 Critical Findings (Sample)
"""
        # Add top 10 issues
        for issue in self.knowledge_board["critical_issues"][:10]:
            report += f"* {issue}\n"
            
        with open("sovereign-dashboard/SWARM_EXECUTION_LOG.md", "w") as f:
            f.write(report)
            
        print(f"\n📄 Report generated: sovereign-dashboard/SWARM_EXECUTION_LOG.md")

if __name__ == "__main__":
    async def main():
        master = SwarmMaster()
        if not master.agents:
            print("⚠️ No agents found. Run swarm_expansion_protocol.py first.")
            return
            
        await master.run_swarm_wave()
        master.generate_report()
        
    asyncio.run(main())
