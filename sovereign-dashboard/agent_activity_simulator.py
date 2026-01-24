#!/usr/bin/env python3
"""
Agent Activity Simulator
Continuously sends real tasks to agents to show live activity on dashboard.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_communication_hub import get_communication_hub


async def simulate_agent_activities():
    """Send continuous real tasks to agents."""
    hub = get_communication_hub()
    
    # Define real tasks for each agent
    agent_tasks = {
        'scanner': {
            'task': 'scan_files',
            'target': '/Users/yacinebenhamou/aSiReM/sovereign-dashboard',
            'description': 'Scanning codebase for patterns'
        },
        'classifier': {
            'task': 'classify',
            'files': ['real_agent_system.py', 'index.html'],
            'description': 'Classifying discovered files'
        },
        'extractor': {
            'task': 'extract_patterns',
            'pattern_type': 'api_endpoints',
            'description': 'Extracting API patterns from code'
        },
        'researcher': {
            'task': 'web_search',
            'query': 'latest agentic AI patterns 2026',
            'description': 'Researching cutting-edge patterns'
        },
        'architect': {
            'task': 'design_system',
            'component': 'agent_orchestration',
            'description': 'Designing system architecture'
        },
        'summarizer': {
            'task': 'summarize',
            'content_type': 'code_features',
            'description': 'Generating NL summaries'
        },
        'evolution': {
            'task': 'self_improve',
            'aspect': 'pattern_recognition',
            'description': 'Evolving detection algorithms'
        },
        'memory': {
            'task': 'store_knowledge',
            'data_type': 'discovered_patterns',
            'description': 'Storing discovered knowledge'
        },
        'embedding': {
            'task': 'vectorize',
            'content': 'code_semantics',
            'description': 'Creating vector embeddings'
        },
        'docgen': {
            'task': 'generate_docs',
            'target': 'api_documentation',
            'description': 'Generating API documentation'
        },
        'mcp': {
            'task': 'github_query',
            'action': 'list_repos',
            'description': 'Querying GitHub via MCP'
        },
        'veo3': {
            'task': 'generate_narrative',
            'prompt': 'System architecture visualization',
            'description': 'Generating cinematic narrative'
        }
    }
    
    print("🤖 Starting Agent Activity Simulator...")
    print("   This will send real tasks to all agents continuously\n")
    
    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'='*60}")
        print(f"Cycle {cycle} - Broadcasting tasks to all agents")
        print(f"{'='*60}\n")
        
        for agent_id, task_config in agent_tasks.items():
            try:
                # Broadcast task to agent
                await hub.broadcast(
                    sender=f'activity_simulator',
                    message_type='task_assignment',
                    content={
                        'target_agent': agent_id,
                        'task': task_config['task'],
                        'description': task_config['description'],
                        'cycle': cycle,
                        **{k: v for k, v in task_config.items() if k not in ['task', 'description']}
                    }
                )
                
                print(f"  ✓ {agent_id:15s} → {task_config['description']}")
                
                # Small delay between agents
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"  ✗ {agent_id:15s} → Error: {e}")
        
        print(f"\n⏱️  Waiting 5 seconds before next cycle...")
        await asyncio.sleep(5)


async def main():
    """Entry point."""
    try:
        await simulate_agent_activities()
    except KeyboardInterrupt:
        print("\n\n👋 Activity simulator stopped.")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║         AZIREM Agent Activity Simulator v1.0             ║
║                                                          ║
║  This script continuously sends REAL tasks to all        ║
║  registered agents to show live activity on dashboard.   ║
║                                                          ║
║  Dashboard: http://localhost:8082                        ║
║  Press Ctrl+C to stop                                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
