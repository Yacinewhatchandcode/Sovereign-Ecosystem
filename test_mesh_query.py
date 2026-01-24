import asyncio
import json
import sys
from agent_mesh_orchestrator import SovereignAgentMesh

async def single_test():
    mesh = SovereignAgentMesh()
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "Analyze the connection between index.html and real_agent_system.py. Which buttons are broken?"
        
    print(f"\n❓ Query: {query}")
    print("⏳ Processing...")
    
    answer = await mesh.query(query)
    
    print("\n✅ SOVEREIGN RESPONSE:")
    print("-" * 60)
    print(answer)
    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(single_test())
