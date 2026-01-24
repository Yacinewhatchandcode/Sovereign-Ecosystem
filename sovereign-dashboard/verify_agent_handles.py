import sys
import os
import asyncio
from pathlib import Path

# Add the directory to sys.path
sys.path.append("/Users/yacinebenhamou/aSiReM/sovereign-dashboard")

async def verify():
    try:
        from real_agent_system import RealMultiAgentOrchestrator
        orchestrator = RealMultiAgentOrchestrator()
        
        agents_to_check = [
            ("scanner", orchestrator.scanner),
            ("classifier", orchestrator.classifier),
            ("extractor", orchestrator.extractor),
            ("memory", orchestrator.memory),
            ("security", orchestrator.security),
            ("qa", orchestrator.qa),
            ("devops", orchestrator.devops),
            ("spectra", orchestrator.spectra),
            ("evolution", orchestrator.evolution),
            ("searcher", orchestrator.searcher),
            ("embedding", orchestrator.embedding),
        ]
        
        print(f"Checking {len(agents_to_check)} agents...")
        
        for name, agent in agents_to_check:
            if agent is None:
                print(f"❌ {name}: NOT INITIALIZED")
                continue
                
            has_bridge = hasattr(agent, "bytebot_bridge") and agent.bytebot_bridge is not None
            has_dispatcher = hasattr(agent, "dispatcher") and agent.dispatcher is not None
            
            status = "✅" if has_bridge and has_dispatcher else "❌"
            br_status = "Bridge: OK" if has_bridge else "Bridge: MISSING"
            ds_status = "Dispatcher: OK" if has_dispatcher else "Dispatcher: MISSING"
            
            print(f"{status} {name:15} | {br_status:15} | {ds_status:15}")

        # Check Mesh
        from agent_mesh_orchestrator import SovereignAgentMesh
        mesh = SovereignAgentMesh(
            bytebot_bridge=orchestrator.bytebot_bridge,
            dispatcher=orchestrator.dispatcher
        )
        
        has_bridge = hasattr(mesh, "bytebot_bridge") and mesh.bytebot_bridge is not None
        has_dispatcher = hasattr(mesh, "dispatcher") and mesh.dispatcher is not None
        has_exec_bridge = hasattr(mesh.executor, "bytebot_bridge") and mesh.executor.bytebot_bridge is not None
        has_exec_dispatcher = hasattr(mesh.executor, "dispatcher") and mesh.executor.dispatcher is not None
        
        print(f"\n🌐 Sovereign Agent Mesh:")
        print(f"{'✅' if has_bridge else '❌'} Mesh Bridge: {'OK' if has_bridge else 'MISSING'}")
        print(f"{'✅' if has_dispatcher else '❌'} Mesh Dispatcher: {'OK' if has_dispatcher else 'MISSING'}")
        print(f"{'✅' if has_exec_bridge else '❌'} Executor Bridge: {'OK' if has_exec_bridge else 'MISSING'}")
        print(f"{'✅' if has_exec_dispatcher else '❌'} Executor Dispatcher: {'OK' if has_exec_dispatcher else 'MISSING'}")

    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
