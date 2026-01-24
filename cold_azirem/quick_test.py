"""
Quick Test: Verify all agents and tools are working
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cold_azirem.orchestration.orchestrator import AgentOrchestrator
from cold_azirem.config.agent_config import list_all_agents


async def main():
    print("\n" + "="*80)
    print("  🌌 COLD AZIREM MULTI-AGENT SYSTEM - QUICK TEST")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Test 1: Initialize all agents
    print("📋 Test 1: Initializing all 10 agents...")
    await orchestrator.initialize_all_agents()
    print(f"✅ Successfully initialized {len(orchestrator.agents)} agents\n")
    
    # Test 2: List agents and their tools
    print("📋 Test 2: Agent Roster")
    print("-" * 80)
    status = orchestrator.get_agent_status()
    for agent_name, agent_status in status.items():
        print(f"\n{agent_name}:")
        print(f"  Model: {agent_status['model']}")
        print(f"  Tools ({len(agent_status['tools'])}): {', '.join(agent_status['tools'])}")
    
    # Test 3: Test tools for a few agents
    print("\n" + "="*80)
    print("📋 Test 3: Testing Agent Tools")
    print("-" * 80)
    
    test_agents = ["ArchitectureDev", "FrontendDev", "QASpecialist"]
    for agent_name in test_agents:
        print(f"\n🧪 Testing {agent_name}...")
        results = await orchestrator.test_agent_tools(agent_name)
        
        success_count = sum(1 for r in results['results'].values() if '✅' in r['status'])
        total_count = len(results['results'])
        
        print(f"   {success_count}/{total_count} tools working")
        
        for tool_name, result in results['results'].items():
            print(f"   {tool_name}: {result['status']}")
    
    # Test 4: Simple agent task (quick)
    print("\n" + "="*80)
    print("📋 Test 4: Single Agent Task Execution")
    print("-" * 80)
    
    print("\n🎯 Task: 'What are the key principles of microservices architecture?'")
    print("   Agent: ArchitectureDev")
    print("   Model: deepseek-r1:7b\n")
    
    result = await orchestrator.execute_task(
        agent_name="ArchitectureDev",
        task="What are the key principles of microservices architecture? Give me 3 main points.",
        max_iterations=1
    )
    
    print(f"✅ Response received ({len(result['response'])} chars)")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Tool calls: {len(result['tool_calls'])}")
    print(f"\n   Response preview:")
    print(f"   {result['response'][:300]}...\n")
    
    # Test 5: Inter-agent communication
    print("="*80)
    print("📋 Test 5: Inter-Agent Communication")
    print("-" * 80)
    
    events = orchestrator.get_message_bus_log(limit=5)
    print(f"\n📨 Recent events ({len(events)} total):")
    for event in events:
        print(f"   {event['source']} → {event['type']} @ {event['timestamp']}")
    
    # Cleanup
    print("\n" + "="*80)
    print("🧹 Cleanup")
    print("-" * 80)
    await orchestrator.cleanup()
    print("✅ All tests completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())
