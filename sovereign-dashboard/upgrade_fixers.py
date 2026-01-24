#!/usr/bin/env python3
"""
⚔️ UPGRADE TO LEVEL 4 (IMPERATOR CLASS)
=======================================
Upgrades specific agents to 'Fixers' capable of writing to disk.
"""

from pathlib import Path
from swarm_fixer_skills import FIXER_MAP
from swarm_evolution_matrix import EVOLVED_AGENT_TEMPLATE

AGENTS_DIR = Path("sovereign-dashboard/autonomy_agents")

def upgrade_fixers():
    print("⚔️ UPGRADING AGENTS TO LEVEL 4 (FIXERS)")
    print("=====================================")
    
    count = 0
    for agent_file in AGENTS_DIR.glob("*_agent.py"):
        agent_name = agent_file.stem
        
        if agent_name in FIXER_MAP:
            skill = FIXER_MAP[agent_name]
            class_name = "".join(x.title() for x in agent_name.replace("_agent", "").split("_")) + "Agent"
            
            # The template handles the injection
            code = EVOLVED_AGENT_TEMPLATE.format(
                name=agent_name.replace("_", " ").title(),
                class_name=class_name,
                agent_id=agent_name,
                skill_code=skill
            )
            
            agent_file.write_text(code)
            print(f"⚔️ {agent_name} -> Level 4 (Resolver)")
            count += 1
            
    print(f"\n✅ Upgraded {count} Agents to Imperator Class.")

if __name__ == "__main__":
    upgrade_fixers()
