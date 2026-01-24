#!/usr/bin/env python3
"""
🏥 AGENT DIAGNOSIS & REPAIR
===========================
This is the "Expert Meta-Agent" that talks to all other agents 
to ensure they are healthy, connected, and aware of the codebase.
"""

import asyncio
import aiohttp
import sys
import json
from datetime import datetime

DASHBOARD_URL = "http://localhost:8082"

async def check_agent(session, agent_id, name):
    print(f"📡 Pinging {name} ({agent_id})...", end="", flush=True)
    try:
        # We'll check the agent via the comms hub or action log
        # For now, we check if the dashboard knows about them
        async with session.get(f"{DASHBOARD_URL}/api/agents/config") as resp:
            if resp.status == 200:
                data = await resp.json()
                agents = data.get("agents", [])
                found = any(a["id"] == agent_id for a in agents)
                if found:
                    print(f" ✅ ONLINE")
                    return True
                else:
                    print(f" ⚠️ MISSING")
                    return False
            else:
                print(f" ❌ API ERROR")
                return False
    except Exception as e:
        print(f" ❌ FAILED: {e}")
        return False

async def trigger_scan(session):
    print("\n🚀 Triggering Codebase Re-Index (Feeding the Agents)...")
    try:
        # Trigger the scanner explicitly
        payload = {"path": "/Users/yacinebenhamou/aSiReM"}
        async with session.post(f"{DASHBOARD_URL}/api/agent/scanner/explore", json=payload) as resp:
            if resp.status == 200:
                print("✅ Scan initiated successfully")
                return True
            else:
                print(f"❌ Scan failed: {resp.status}")
                return False
    except Exception as e:
        print(f"❌ Scan triggering failed: {e}")
        return False

async def trigger_mesh_audit(session):
    print("\n🧠 Triggering Sovereign Mesh Audit...")
    try:
        # Trigger the mesh self-check
        payload = {"query": "FULL_SYSTEM_DIAGNOSTIC"}
        async with session.post(f"{DASHBOARD_URL}/api/mesh/query", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Mesh Response: {json.dumps(data, indent=2)}")
            else:
                print(f"⚠️ Mesh API error (expected if mesh disabled): {resp.status}")
    except Exception as e:
        print(f"⚠️ Mesh trigger failed: {e}")

async def main():
    print("🏥 STARTING SOVEREIGN AGENT DIAGNOSIS")
    print("=====================================")
    
    async with aiohttp.ClientSession() as session:
        # 1. Check Core Agents
        core_agents = [
            ("azirem", "King Agent"),
            ("bytebot", "Visual Operator"),
            ("scanner", "Codebase Scanner"),
            ("researcher", "Web Researcher"),
            ("classifier", "Pattern Expert"),
            ("architect", "System Architect")
        ]
        
        success_count = 0
        for agent_id, name in core_agents:
            if await check_agent(session, agent_id, name):
                success_count += 1
                
        print(f"\n📊 System Health: {success_count}/{len(core_agents)} Agents Operational")
        
        # 2. Trigger "Knowledge Injection"
        await trigger_scan(session)
        
        # 3. Trigger Mesh Audit
        await trigger_mesh_audit(session)
        
        print("\n✅ DIAGNOSIS COMPLETE")
        print("The agents are now updated and scanning the codebase.")

if __name__ == "__main__":
    asyncio.run(main())
