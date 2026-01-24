"""
Cold Azirem Multi-Agent System Demo
Demonstrates all agents, tools, and inter-agent communication
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cold_azirem.orchestration.orchestrator import AgentOrchestrator
from cold_azirem.config.agent_config import list_all_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_result(result: dict):
    """Pretty print a result"""
    print(f"Agent: {result.get('agent', 'Unknown')}")
    print(f"Success: {result.get('success', False)}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Response: {result.get('response', 'No response')[:300]}...")
    
    if result.get('tool_calls'):
        print(f"\nTool Calls: {len(result['tool_calls'])}")
        for i, tool_call in enumerate(result['tool_calls'], 1):
            print(f"  {i}. {tool_call['tool']} - {'✅' if tool_call['success'] else '❌'}")
    
    if result.get('metrics'):
        metrics = result['metrics']
        print(f"\nMetrics:")
        print(f"  Total Requests: {metrics.get('total_requests', 0)}")
        print(f"  Successful: {metrics.get('successful_requests', 0)}")
        print(f"  Failed: {metrics.get('failed_requests', 0)}")
        print(f"  Tool Calls: {metrics.get('tool_calls', 0)}")
        print(f"  Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")


async def demo_1_initialize_agents():
    """Demo 1: Initialize all agents"""
    print_section("DEMO 1: Initialize All Agents")
    
    orchestrator = AgentOrchestrator()
    
    print("📋 Available agents:")
    for agent_name in list_all_agents():
        print(f"  - {agent_name}")
    
    print("\n🚀 Initializing all agents...")
    await orchestrator.initialize_all_agents()
    
    print("\n✅ Agent Status:")
    status = orchestrator.get_agent_status()
    for agent_name, agent_status in status.items():
        print(f"\n{agent_name}:")
        print(f"  Model: {agent_status['model']}")
        print(f"  Tools: {', '.join(agent_status['tools'])}")
    
    return orchestrator


async def demo_2_test_agent_tools(orchestrator: AgentOrchestrator):
    """Demo 2: Test tools for each agent"""
    print_section("DEMO 2: Test Agent Tools")
    
    # Test a few key agents
    test_agents = ["ArchitectureDev", "FrontendDev", "QASpecialist"]
    
    for agent_name in test_agents:
        print(f"\n🧪 Testing tools for {agent_name}...")
        results = await orchestrator.test_agent_tools(agent_name)
        
        print(f"\nResults for {agent_name}:")
        for tool_name, result in results['results'].items():
            status = result['status']
            print(f"  {tool_name}: {status}")


async def demo_3_single_agent_task(orchestrator: AgentOrchestrator):
    """Demo 3: Execute task with single agent"""
    print_section("DEMO 3: Single Agent Task Execution")
    
    task = """Design a scalable architecture for a real-time chat application 
    that needs to support 1 million concurrent users."""
    
    print(f"Task: {task}\n")
    print("🎯 Executing with ArchitectureDev agent...")
    
    result = await orchestrator.execute_task(
        agent_name="ArchitectureDev",
        task=task,
        max_iterations=3
    )
    
    print("\n📊 Result:")
    print_result(result)


async def demo_4_parallel_execution(orchestrator: AgentOrchestrator):
    """Demo 4: Parallel task execution"""
    print_section("DEMO 4: Parallel Task Execution")
    
    tasks = {
        "ArchitectureDev": "Design the system architecture for a microservices platform",
        "FrontendDev": "Create a modern dashboard UI with React and Tailwind CSS",
        "BackendDev": "Design a RESTful API for user management",
        "QASpecialist": "Create a comprehensive test strategy for the platform"
    }
    
    print("⚡ Executing 4 tasks in parallel:")
    for agent, task in tasks.items():
        print(f"  {agent}: {task[:60]}...")
    
    print("\n🚀 Starting parallel execution...")
    results = await orchestrator.execute_parallel_tasks(tasks, max_iterations=2)
    
    print("\n📊 Results:")
    for agent_name, result in results.items():
        print(f"\n{agent_name}:")
        if result.get('success'):
            print(f"  ✅ Success")
            print(f"  Response: {result['response'][:150]}...")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")


async def demo_5_agent_collaboration(orchestrator: AgentOrchestrator):
    """Demo 5: Agent collaboration (sequential pipeline)"""
    print_section("DEMO 5: Agent Collaboration Pipeline")
    
    task = "Build a user authentication system with OAuth2"
    
    # Define agent sequence
    sequence = [
        "ProductManager",      # Define requirements
        "ArchitectureDev",     # Design architecture
        "BackendDev",          # Implement backend
        "QASpecialist",        # Create tests
    ]
    
    print(f"Initial Task: {task}")
    print(f"\nAgent Pipeline: {' → '.join(sequence)}\n")
    
    print("🔄 Starting collaboration...")
    results = await orchestrator.agent_collaboration(task, sequence)
    
    print("\n📊 Pipeline Results:")
    for i, result in enumerate(results, 1):
        print(f"\nStep {i} - {result['agent']}:")
        print(f"  Response: {result['response'][:200]}...")


async def demo_6_inter_agent_communication(orchestrator: AgentOrchestrator):
    """Demo 6: Inter-agent communication via message bus"""
    print_section("DEMO 6: Inter-Agent Communication")
    
    # Execute a task that will generate events
    print("🎯 Executing task to generate inter-agent events...")
    
    await orchestrator.execute_task(
        "ArchitectureDev",
        "Quick architecture review",
        max_iterations=1
    )
    
    # Get message bus log
    events = orchestrator.get_message_bus_log(limit=10)
    
    print(f"\n📨 Recent Events ({len(events)} total):")
    for event in events[-5:]:  # Show last 5
        print(f"\n  Source: {event['source']}")
        print(f"  Type: {event['type']}")
        print(f"  Time: {event['timestamp']}")
        if 'message' in event:
            print(f"  Message: {event['message'][:100]}...")


async def demo_7_agent_metrics(orchestrator: AgentOrchestrator):
    """Demo 7: Agent performance metrics"""
    print_section("DEMO 7: Agent Performance Metrics")
    
    status = orchestrator.get_agent_status()
    
    print("📊 Agent Metrics Summary:\n")
    for agent_name, agent_status in status.items():
        metrics = agent_status.get('metrics', {})
        if metrics.get('total_requests', 0) > 0:
            print(f"{agent_name}:")
            print(f"  Total Requests: {metrics.get('total_requests', 0)}")
            print(f"  Success Rate: {metrics.get('successful_requests', 0) / metrics.get('total_requests', 1) * 100:.1f}%")
            print(f"  Tool Calls: {metrics.get('tool_calls', 0)}")
            print(f"  Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
            print()


async def main():
    """Run all demos"""
    print("\n" + "🌌 " * 20)
    print("  COLD AZIREM MULTI-AGENT ECOSYSTEM - FULL DEMO")
    print("🌌 " * 20 + "\n")
    
    try:
        # Demo 1: Initialize
        orchestrator = await demo_1_initialize_agents()
        
        # Demo 2: Test tools
        await demo_2_test_agent_tools(orchestrator)
        
        # Demo 3: Single agent
        await demo_3_single_agent_task(orchestrator)
        
        # Demo 4: Parallel execution
        await demo_4_parallel_execution(orchestrator)
        
        # Demo 5: Collaboration
        await demo_5_agent_collaboration(orchestrator)
        
        # Demo 6: Inter-agent communication
        await demo_6_inter_agent_communication(orchestrator)
        
        # Demo 7: Metrics
        await demo_7_agent_metrics(orchestrator)
        
        # Cleanup
        print_section("Cleanup")
        await orchestrator.cleanup()
        print("✅ All demos completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
