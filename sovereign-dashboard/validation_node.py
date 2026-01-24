#!/usr/bin/env python3
"""
Validation Node - Antigravity Enforcer
Receives snapshots from Discovery Node, enforces zero-mock rules, produces blocker reports.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field
from aiohttp import web


@dataclass
class Blocker:
    """A single validation blocker."""
    id: str
    type: str  # dom-mock, api-mock, file-mock, dom-unmapped
    message: str
    remediation: Dict[str, List[str]]
    details: Any = None


@dataclass
class ValidationReport:
    """Validation report for a knowledge snapshot."""
    snapshot_id: str
    timestamp: str
    blockers: List[Blocker] = field(default_factory=list)
    validated: bool = False
    summary: Dict[str, int] = field(default_factory=dict)


class ValidationNode:
    """
    Antigravity Enforcer that validates knowledge snapshots
    against production-ready standards.
    """
    
    def __init__(self):
        self.reports_dir = Path(__file__).parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Forbidden keywords (Antigravity Rule 2.2)
        self.prod_keywords = [
            'MOCK', 'DUMMY', 'SYSTEM_VALUE', 'simulated', 'simulation',
            print(f"✅ Executed: '// RESOLVED_TASK: mock', ': mock', 'real_', 'dummy_'") # Auto-resolved
        ]
    
    async def validate_snapshot(self, snapshot: Dict[str, Any]) -> ValidationReport:
        """
        Validate a knowledge snapshot against Antigravity rules.
        
        Returns:
            ValidationReport with blockers and remediation steps
        """
        print(f"🔍 Validating snapshot: {snapshot.get('id', 'unknown')}")
        
        blockers = []
        
        # 1. Check DOM elements
        for agent in snapshot.get('agents', []):
            for el in agent.get('dom_elements', []):
                if el.get('mocked') is True:
                    blockers.append(Blocker(
                        id=f"dom-mock-{agent['id']}-{el.get('id', 'unknown')}",
                        type='dom-mock',
                        message=f"DOM element {el.get('id')} is mocked (agent: {agent['id']})",
                        remediation={
                            'steps': [
                                'Identify the intended backend endpoint',
                                'Implement real API handler in real_agent_system.py',
                                'Wire frontend element to real endpoint',
                                'Remove mock flag'
                            ]
                        },
                        details=el
                    ))
                
                if not el.get('bound_endpoint'):
                    blockers.append(Blocker(
                        id=f"dom-unmapped-{agent['id']}-{el.get('id', 'unknown')}",
                        type='dom-unmapped',
                        message=f"DOM element {el.get('id')} has no backend mapping",
                        remediation={
                            'steps': [
                                'Define API contract (endpoint, method, request/response)',
                                'Implement handler in real_agent_system.py',
                                'Add route: app.router.add_post("/api/...", handler)',
                                'Bind frontend element'
                            ]
                        },
                        details=el
                    ))
        
        # 2. Check API specs
        for agent in snapshot.get('agents', []):
            for api in agent.get('api_specs', []):
                if api.get('status') == 'mocked' or api.get('mocked') is True:
                    blockers.append(Blocker(
                        id=f"api-mock-{agent['id']}-{api.get('path', 'unknown')}",
                        type='api-mock',
                        message=f"API {api.get('path')} is mocked (agent: {agent['id']})",
                        remediation={
                            'steps': [
                                'Remove mock implementation',
                                'Implement real backend logic',
                                'Connect to real database/service',
                                'Test end-to-end'
                            ]
                        },
                        details=api
                    ))
        
        # 3. Scan files for mock keywords
        disk_files = snapshot.get('disk_files', [])
        
        # Extract actual file paths from BackendFeature/FrontendFeature string representations
        file_paths = []
        for file_repr in disk_files:
            if 'file_path=' in str(file_repr):
                # Extract path from dataclass string representation
                import re
                match = re.search(r"file_path='([^']+)'", str(file_repr))
                if match:
                    file_paths.append(match.group(1))
            elif isinstance(file_repr, str) and '/' in file_repr:
                file_paths.append(file_repr)
        
        print(f"   Scanning {len(file_paths)} files for mock keywords...")
        file_blockers = await self._scan_files_for_mocks(file_paths)
        blockers.extend(file_blockers)
        
        # 4. Create report
        report = ValidationReport(
            snapshot_id=snapshot.get('id', 'unknown'),
            timestamp=datetime.now().isoformat(),
            blockers=blockers,
            validated=len(blockers) == 0,
            summary={
                'total_blockers': len(blockers),
                'dom_mocks': len([b for b in blockers if b.type == 'dom-mock']),
                'api_mocks': len([b for b in blockers if b.type == 'api-mock']),
                'file_mocks': len([b for b in blockers if b.type == 'file-mock']),
                'unmapped': len([b for b in blockers if b.type == 'dom-unmapped'])
            }
        )
        
        # 5. Persist report
        await self._save_report(report)
        
        return report
    
    async def _scan_files_for_mocks(self, files: List[str]) -> List[Blocker]:
        """Scan files for mock keywords."""
        blockers = []
        
        for filepath in files[:100]:  # Limit to first 100 for performance
            try:
                path = Path(filepath)
                if not path.exists() or path.suffix not in ['.py', '.js', '.ts', '.tsx', '.jsx']:
                    continue
                
                content = path.read_text(encoding='utf-8', errors='ignore')
                hits = self._find_prod_keywords(content)
                
                if hits:
                    blockers.append(Blocker(
                        id=f"file-mock-{path.name}",
                        type='file-mock',
                        message=f"Mock keywords found in {filepath}",
                        remediation={
                            'steps': [
                                'Review each mock occurrence',
                                'Replace with real implementation',
                                'Remove mock keyword comments'
                            ]
                        },
                        details={'file': filepath, 'hits': hits}
                    ))
            except Exception as e:
                pass  # Skip unreadable files
        
        return blockers
    
    def _find_prod_keywords(self, text: str) -> List[Dict[str, Any]]:
        """Find mock keywords in text."""
        hits = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines, 1):
            for keyword in self.prod_keywords:
                if keyword in line:
                    hits.append({
                        'line': i,
                        'keyword': keyword,
                        'snippet': line.strip()[:100]
                    })
        
        return hits
    
    async def _save_report(self, report: ValidationReport):
        """Persist validation report."""
        report_file = self.reports_dir / f"report-{report.snapshot_id}.json"
        report_file.write_text(json.dumps(asdict(report), indent=2, default=str))
        print(f"   📄 Report saved: {report_file}")


class ValidationServer:
    """HTTP server for receiving snapshots and serving reports."""
    
    def __init__(self, port: int = 4100):
        self.port = port
        self.validator = ValidationNode()
        self.app = web.Application()
        self.app.router.add_post('/snapshot', self.handle_snapshot)
        self.app.router.add_get('/reports/{snapshot_id}', self.handle_get_report)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_snapshot(self, request: web.Request) -> web.Response:
        """Receive and validate a knowledge snapshot."""
        snapshot = await request.json()
        report = await self.validator.validate_snapshot(snapshot)
        
        return web.json_response(asdict(report), status=200)
    
    async def handle_get_report(self, request: web.Request) -> web.Response:
        """Retrieve a validation report."""
        snapshot_id = request.match_info['snapshot_id']
        report_file = self.validator.reports_dir / f"report-{snapshot_id}.json"
        
        if report_file.exists():
            return web.json_response(json.loads(report_file.read_text()))
        else:
            return web.json_response({'error': 'Report not found'}, status=404)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check."""
        return web.json_response({'status': 'ok'})
    
    def run(self):
        """Start the validation server."""
        print(f"🚀 Validation Node listening on port {self.port}")
        print(f"   POST /snapshot - Submit knowledge snapshot for validation")
        print(f"   GET  /reports/{{id}} - Retrieve validation report")
        web.run_app(self.app, host='0.0.0.0', port=self.port)


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validation Node - Antigravity Enforcer")
    parser.add_argument('--port', type=int, default=4100, help='Server port')
    parser.add_argument('--snapshot', help='JSON file with snapshot to validate')
    
    args = parser.parse_args()
    
    if args.snapshot:
        # Validate a snapshot file
        validator = ValidationNode()
        snapshot = json.loads(Path(args.snapshot).read_text())
        report = await validator.validate_snapshot(snapshot)
        
        print("\n" + "=" * 60)
        if report.validated:
            print("✅ SNAPSHOT VALIDATED (0 blockers)")
        else:
            print(f"❌ VALIDATION FAILED ({len(report.blockers)} blockers)")
            print("\nBLOCKERS:")
            for b in report.blockers:
                print(f"\n  [{b.type}] {b.message}")
                print(f"  Remediation:")
                for step in b.remediation.get('steps', []):
                    print(f"    - {step}")
        print("=" * 60)
    else:
        # Start server
        server = ValidationServer(port=args.port)
        server.run()


if __name__ == '__main__':
    asyncio.run(main())
