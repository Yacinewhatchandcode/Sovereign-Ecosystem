#!/usr/bin/env python3
"""
Discovery Node - Agent Orchestrator & Knowledge Harvester
Uses AgentCommunicationHub to query all agents and build canonical knowledge graph.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
import aiohttp

# Import existing infrastructure
sys.path.insert(0, str(Path(__file__).parent))
from agent_communication_hub import get_communication_hub, AgentMessage
from feature_scanner import get_feature_scanner


@dataclass
class KnowledgeSnapshot:
    """Canonical knowledge graph snapshot."""
    id: str
    timestamp: str
    disk_files: List[str] = field(default_factory=list)
    agents: List[Dict[str, Any]] = field(default_factory=list)
    api_specs: List[Dict[str, Any]] = field(default_factory=list)
    dom_elements: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class DiscoveryNode:
    """
    Agent Orchestrator that queries all registered agents and builds
    a canonical knowledge graph.
    """
    
    def __init__(self, validator_endpoint: Optional[str] = None):
        self.hub = get_communication_hub()
        self.scanner = get_feature_scanner()
        self.validator_endpoint = validator_endpoint
        self.knowledge_store = Path(__file__).parent / "knowledge_store.json"
        
    async def orchestrate(self, paths: List[str], tasks: List[str] = None) -> KnowledgeSnapshot:
        """
        Main orchestration: query agents, scan disk, merge knowledge.
        
        Args:
            paths: Directories to scan
            tasks: Tasks to request from agents (dom_scan, file_index, api_schema)
        """
        if tasks is None:
            tasks = ["scan", "index", "capabilities"]
        
        print(f"🔍 Discovery Node: Orchestrating {len(tasks)} tasks across agents...")
        
        # 1. Get all registered agents
        agents = self.hub.get_all_agents()
        print(f"   Found {len(agents)} registered agents")
        
        # 2. Local disk scan using FeatureScanner
        print(f"   Scanning {len(paths)} paths...")
        disk_files = []
        dom_elements = []
        api_specs = []
        
        for path in paths:
            inventory = await self.scanner.full_scan(path)
            
            # Extract file paths from both backend and frontend features
            for feature in inventory.backend:
                file_path = str(feature.file) if hasattr(feature, 'file') else str(feature)
                disk_files.append(file_path)
                
                # Check if it's an API endpoint
                if hasattr(feature, 'type') and 'api' in str(feature.type).lower():
                    api_specs.append({
                        'path': feature.name,
                        'file': file_path,
                        'status': 'implemented',
                        'mocked': self._is_mocked(feature)
                    })
            
            for feature in inventory.frontend:
                file_path = str(feature.file) if hasattr(feature, 'file') else str(feature)
                disk_files.append(file_path)
                
                # Check if it's a DOM element (button, form, input)
                if hasattr(feature, 'name'):
                    name_lower = feature.name.lower()
                    if any(kw in name_lower for kw in ['button', 'form', 'input', 'onclick']):
                        dom_elements.append({
                            'id': feature.name,
                            'file': file_path,
                            'mocked': self._is_mocked(feature),
                            'bound_endpoint': self._find_endpoint(feature)
                        })

        
        # 3. Query each agent for their knowledge
        agent_results = []
        for agent in agents:
            result = await self._query_agent(agent, tasks, paths)
            agent_results.append({
                'id': agent['id'],
                'name': agent['name'],
                'capabilities': agent['capabilities'],
                'summary': result.get('summary', ''),
                'dom_elements': result.get('dom_elements', []),
                'api_specs': result.get('api_specs', []),
                'files_indexed': result.get('files_indexed', [])
            })
        
        # 4. Merge into knowledge snapshot
        snapshot = KnowledgeSnapshot(
            id=f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            disk_files=disk_files,
            agents=agent_results,
            api_specs=api_specs,
            dom_elements=dom_elements,
            summary={
                'total_files': len(disk_files),
                'total_agents': len(agents),
                'total_dom_elements': len(dom_elements),
                'total_api_specs': len(api_specs)
            }
        )
        
        # 5. Persist knowledge
        await self._save_knowledge(snapshot)
        
        # 6. Push to validator if configured
        if self.validator_endpoint:
            await self._push_to_validator(snapshot)
        
        return snapshot
    
    async def _query_agent(self, agent: Dict, tasks: List[str], paths: List[str]) -> Dict:
        """Query a single agent for its knowledge."""
        try:
            # Use broadcast instead of send_message
            await self.hub.broadcast(
                from_agent='discovery',
                msg_type='query',
                data={
                    'target_agent': agent['id'],
                    'tasks': tasks,
                    'paths': paths
                }
            )
            
            # Wait for potential response
            await asyncio.sleep(0.5)
            
            # Get recent communications for this agent
            comms = self.hub.get_all_communications(limit=10)
            
            # Find response from this agent
            for comm in comms:
                if comm.get('to_agent') == 'discovery' and comm.get('from_agent') == agent['id']:
                    return comm.get('data', {})
            
            return {}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _is_mocked(self, feature) -> bool:
        """Check if feature contains mock keywords."""
        prod_keywords = ['mock', 'fake', 'system_value', 'dummy', 'simulated']
        content = str(feature).lower()
        return any(kw in content for kw in prod_keywords)
    
    def _find_endpoint(self, feature) -> Optional[str]:
        """Try to find associated backend endpoint."""
        # Simple heuristic: look for API calls in frontend code
        # In production, parse AST or use more sophisticated analysis
        return None
    
    async def _save_knowledge(self, snapshot: KnowledgeSnapshot):
        """Persist knowledge to disk."""
        self.knowledge_store.write_text(
            json.dumps(asdict(snapshot), indent=2)
        )
        print(f"   ✅ Knowledge saved: {self.knowledge_store}")
    
    async def _push_to_validator(self, snapshot: KnowledgeSnapshot):
        """Push snapshot to Validation Node."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.validator_endpoint}/snapshot",
                    json=asdict(snapshot),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        print(f"   ✅ Pushed to validator")
                    else:
                        print(f"   ⚠️ Validator returned {resp.status}")
        except Exception as e:
            print(f"   ⚠️ Failed to push to validator: {e}")


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Discovery Node - Agent Orchestrator")
    parser.add_argument('paths', nargs='+', help='Paths to scan')
    parser.add_argument('--validator', help='Validator endpoint (http://host:port)')
    parser.add_argument('--tasks', nargs='+', default=['scan', 'index', 'capabilities'])
    
    args = parser.parse_args()
    
    node = DiscoveryNode(validator_endpoint=args.validator)
    snapshot = await node.orchestrate(args.paths, args.tasks)
    
    print("\n" + "=" * 60)
    print(f"📊 Discovery Complete: {snapshot.id}")
    print(f"   Files: {snapshot.summary['total_files']}")
    print(f"   Agents: {snapshot.summary['total_agents']}")
    print(f"   DOM Elements: {snapshot.summary['total_dom_elements']}")
    print(f"   API Specs: {snapshot.summary['total_api_specs']}")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
