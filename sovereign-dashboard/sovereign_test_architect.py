#!/usr/bin/env python3
"""
🧬 SOVEREIGN TEST ARCHITECT - AUTONOMOUS TEST CONCEPTION
========================================================
Leverages the full agent fleet (Scanner, Classifier, RPA) to 
generate exhaustive and precise E2E test cases by analyzing 
the DOM and Backend logic.

1. Scans UI for all interactive nodes (Scanner)
2. Maps actions to WebSocket message types (Extractor)
3. Generates combinatorial state matrix (Classifier)
4. Produces executable Playwright/RPA scripts (RPA Generator)
"""

import os
import re
import json
import asyncio
from typing import List, Dict, Any, Set
from pathlib import Path
from autonomous_factory import AutonomousFactory, AgentSpec, AgentCategory, AgentPriority
from rpa_bot_generator import RPABotGenerator, RPAWorkflow, RPAAction, ActionType, TriggerType

class SovereignTestArchitect:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root)
        self.ui_file = self.root / "index.html"
        self.backend_file = self.root / "real_agent_system.py"
        self.output_dir = self.root / "tests/autonomous"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.factory = AutonomousFactory()
        self.rpa_gen = RPABotGenerator()
        
        self.interaction_map = {}
        self.state_matrix = []

    async def run_discovery(self):
        """Phase 1: Deep Discovery of UI/Logic"""
        print("🔍 [PHASE 1] Deep Discovery Starting...")
        
        if not self.ui_file.exists():
            return {"error": "UI file not found"}
            
        content = self.ui_file.read_text()
        
        # 1. Extract IDs and Onclicks
        ids = re.findall(r'id="([^"]+)"', content)
        onclicks = re.findall(r'onclick="([^"]+)"', content)
        
        # 2. Map Functions to WebSocket Types in scripts
        # Simple heuristic: find 'type: "some_msg"' or 'type: \'some_msg\'' near function names
        ws_types = re.findall(r'type:\s*[\'"]([^\'"]+)[\'"]', content)
        
        self.interaction_map = {
            "dom_ids": list(set(ids)),
            "actions": list(set(onclicks)),
            "ws_messages": list(set(ws_types))
        }
        
        print(f"   ✅ Found {len(ids)} IDs, {len(onclicks)} Actions, {len(ws_types)} WS Types")
        return self.interaction_map

    async def conceive_test_scenarios(self):
        """Phase 2: Exhaustive Precising with DeepSeek-style logic"""
        print("🧠 [PHASE 2] Exhaustive Test Conception...")
        
        # Variables from Discovery
        tabs = [a for a in self.interaction_map["actions"] if "setVideoMode" in a or "tab" in a]
        agents = [a for a in self.interaction_map["actions"] if "selectAgent" in a]
        quick_actions = [a for a in self.interaction_map["actions"] if "trigger" in a or "generate" in a or "audit" in a]
        
        scenarios = []
        
        # 1. Tab x Agent Combinations
        for tab in tabs:
            for agent in agents:
                scenarios.append({
                    "id": f"TC-{len(scenarios)+1}",
                    "name": f"Context: {tab} + {agent}",
                    "steps": [tab, agent],
                    "verification": "Check main display and sidebar highlight"
                })
                
        # 2. Action x State Combinations
        for action in quick_actions:
            scenarios.append({
                "id": f"TC-{len(scenarios)+1}",
                "name": f"Action: {action}",
                "steps": [action],
                "verification": "Check terminal/activity log for confirmation"
            })
            
        self.state_matrix = scenarios
        print(f"   ✅ Conceived {len(scenarios)} core functional scenarios")
        return scenarios

    async def generate_rpa_bots(self):
        """Phase 3: Automated RPA/Playwright Generation"""
        print("🤖 [PHASE 3] Generating Sovereign RPA Bots...")
        
        # Convert scenarios to RPA Workflows
        for i, scenario in enumerate(self.state_matrix[:10]): # Limit for demo
            actions = []
            for step in scenario["steps"]:
                actions.append(RPAAction(
                    type=ActionType.CLICK,
                    name=f"click_{step}",
                    params={"selector": f"[onclick*='{step}']"}
                ))
            
            workflow = RPAWorkflow(
                name=f"bot_{scenario['id']}",
                description=scenario["name"],
                trigger=TriggerType.MANUAL,
                trigger_config={},
                actions=actions
            )
            
            self.rpa_gen.create_custom_bot(workflow)
            
        print(f"   ✅ Created {len(self.rpa_gen.bots)} RPA Bots in factory")
        return list(self.rpa_gen.bots.keys())

    async def execute_perfection_audit(self):
        """Final Audit and Documentation"""
        report_path = self.output_dir / "sovereign_intelligence_report.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "discovery": self.interaction_map,
            "scenarios": self.state_matrix,
            "metrics": {
                "total_nodes": len(self.interaction_map["dom_ids"]),
                "exhaustive_combinations": len(self.state_matrix)
            }
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)
            
        print(f"🏁 [COMPLETE] Sovereign Test Intelligence saved to {report_path}")
        return report_path

if __name__ == "__main__":
    from datetime import datetime
    architect = SovereignTestArchitect()
    
    async def run():
        await architect.run_discovery()
        await architect.conceive_test_scenarios()
        await architect.generate_rpa_bots()
        await architect.execute_perfection_audit()
        
    asyncio.run(run())
