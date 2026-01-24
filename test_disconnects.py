import asyncio
from agent_mesh_orchestrator import SovereignAgentMesh

async def find_disconnects():
    mesh = SovereignAgentMesh()
    
    query = """
    Identify every UI button in sovereign-dashboard/index.html (look for 'onclick' attributes).
    For each button function (e.g., triggerEvolutionCycle, toggleAutoEvolve, searchWeb, executeApiCall), 
    verify if there is a corresponding API route or WebSocket handler in sovereign-dashboard/real_agent_system.py.
    
    List the 'BROKEN' ones (those without a backend handler).
    """
    
    print(f"\n❓ Querying mesh for disconnects...")
    answer = await mesh.query(query)
    
    print("\n✅ DISCONNECT ANALYSIS:")
    print("-" * 60)
    print(answer)
    print("-" * 60)

if __name__ == "__main__":
    asyncio.run(find_disconnects())
