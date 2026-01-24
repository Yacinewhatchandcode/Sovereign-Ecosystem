#!/usr/bin/env python3
"""
🧪 EVOLVE SWARM SCRIPT
=======================
Upgrades targeted agents from 'mass_awaken_agents.py' (Level 1) 
to 'swarm_evolution_matrix.py' (Level 2).
"""

import os
from pathlib import Path
from swarm_evolution_matrix import EVOLUTION_MAP, EVOLVED_AGENT_TEMPLATE

AGENTS_DIR = Path("sovereign-dashboard/autonomy_agents")

def evolve_agents():
    print("🧪 STARTING SWARM EVOLUTION")
    print("===========================")
    
    count = 0
    for agent_file in AGENTS_DIR.glob("*_agent.py"):
        agent_name = agent_file.stem  # e.g. "vuln_scanner_agent"
        
        if agent_name in EVOLUTION_MAP:
            skill = EVOLUTION_MAP[agent_name]
            class_name = "".join(x.title() for x in agent_name.replace("_agent", "").split("_")) + "Agent"
            
            # Generate Level 2 Code
            code = EVOLVED_AGENT_TEMPLATE.format(
                name=agent_name.replace("_", " ").title(),
                class_name=class_name,
                agent_id=agent_name,
                skill_code=skill
            )
            
            # Overwrite
            agent_file.write_text(code)
            print(f"🌟 UPGRADED {agent_name} to Level 2 (Specialist)")
            count += 1
            
    print(f"\n✅ Evolution Complete. {count} Agents upgraded to Specialist Class.")
    print("=============================================================")

if __name__ == "__main__":
    evolve_agents()
