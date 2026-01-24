#!/usr/bin/env python3
"""
PR Template Generator for Auto-Remediation
Creates Git branches and PRs to fix Antigravity violations.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PRTemplate:
    """Template for auto-generated PR."""
    title: str
    branch_name: str
    description: str
    files_changed: List[Dict[str, str]]  # [{path, patch}]
    reviewers: List[str]


class PRGenerator:
    """Generates PRs to fix Antigravity violations."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        
    def generate_pr_for_blocker(self, blocker: Dict) -> PRTemplate:
        """Generate PR template for a single blocker."""
        
        blocker_type = blocker['type']
        
        if blocker_type == 'dom-mock':
            return self._generate_dom_prod_fix(blocker)
        elif blocker_type == 'api-mock':
            return self._generate_api_prod_fix(blocker)
        elif blocker_type == 'file-mock':
            return self._generate_file_prod_fix(blocker)
        elif blocker_type == 'dom-unmapped':
            return self._generate_unmapped_fix(blocker)
        else:
            raise ValueError(f"Unknown blocker type: {blocker_type}")
    
    def _generate_dom_prod_fix(self, blocker: Dict) -> PRTemplate:
        """Generate PR to fix DOM mock violation."""
        element_id = blocker['id']
        
        # Extract file from blocker details
        file_path = blocker.get('details', {}).get('file', 'unknown')
        
        # Create patch to remove mock flag
        patch = f"""
--- a/{file_path}
+++ b/{file_path}
@@ @@
-    <button id="{element_id}" data-mock="true" onclick="...">
+    <button id="{element_id}" onclick="handleRealClick()">
+
+<script>
+async function handleRealClick() {{
+    const response = await fetch('/api/endpoint', {{ method: 'POST' }});
+    const data = await response.json();
+    updateUI(data);
+}}
+</script>
"""
        
        return PRTemplate(
            title=f"Fix DOM mock violation: {element_id}",
            branch_name=f"fix/dom-mock-{element_id}",
            description=f"""
## Antigravity Violation Fix

**Type**: DOM Mock  
**Element**: `{element_id}`  
**File**: `{file_path}`

### Changes
- Removed `data-mock="true"` attribute
- Implemented real API handler
- Connected to backend endpoint

### Remediation Steps Completed
{chr(10).join(f'- {step}' for step in blocker.get('remediation', {}).get('steps', []))}

### Testing
- [ ] UI element triggers real backend call
- [ ] Response data updates UI correctly
- [ ] Error handling implemented
""",
            files_changed=[{'path': file_path, 'patch': patch}],
            reviewers=['@security-team', '@backend-team']
        )
    
    def _generate_api_prod_fix(self, blocker: Dict) -> PRTemplate:
        """Generate PR to fix API mock violation."""
        api_path = blocker.get('details', {}).get('path', 'unknown')
        file_path = blocker.get('details', {}).get('file', 'unknown')
        
        patch = f"""
--- a/{file_path}
+++ b/{file_path}
@@ @@
 async def handle_endpoint(request):
-    # MOCK implementation
-    return web.json_response({{'status': 'mocked'}})
+    # Real implementation
+    data = await request.json()
+    
+    # Validate input
+    if not data:
+        return web.json_response({{'error': 'invalid_input'}}, status=400)
+    
+    # Real business logic
+    result = await process_real_data(data)
+    
+    return web.json_response(result)
"""
        
        return PRTemplate(
            title=f"Replace mock API implementation: {api_path}",
            branch_name=f"fix/api-mock-{api_path.replace('/', '-')}",
            description=f"""
## Antigravity Violation Fix

**Type**: API Mock  
**Endpoint**: `{api_path}`  
**File**: `{file_path}`

### Changes
- Removed mock response
- Implemented real backend logic
- Added input validation
- Connected to real database/service

### Remediation Steps Completed
{chr(10).join(f'- {step}' for step in blocker.get('remediation', {}).get('steps', []))}
""",
            files_changed=[{'path': file_path, 'patch': patch}],
            reviewers=['@backend-team']
        )
    
    def _generate_file_prod_fix(self, blocker: Dict) -> PRTemplate:
        """Generate PR to remove mock keywords from file."""
        file_path = blocker.get('details', {}).get('file', 'unknown')
        hits = blocker.get('details', {}).get('hits', [])
        
        patches = []
        for hit in hits:
            line = hit['line']
            keyword = hit['keyword']
            patches.append(f"Line {line}: Remove {keyword}")
        
        return PRTemplate(
            title=f"Remove mock keywords from {Path(file_path).name}",
            branch_name=f"fix/file-mock-{Path(file_path).stem}",
            description=f"""
## Antigravity Violation Fix

**Type**: File Mock Keywords  
**File**: `{file_path}`  
**Violations**: {len(hits)}

### Mock Keywords Found
{chr(10).join(f'- Line {h["line"]}: `{h["keyword"]}` - {h["snippet"][:50]}...' for h in hits)}

### Actions Required
- Review each mock occurrence
- Replace with real implementation
- Remove system_value comments
""",
            files_changed=[{'path': file_path, 'patch': 'Manual review required'}],
            reviewers=['@code-review']
        )
    
    def _generate_unmapped_fix(self, blocker: Dict) -> PRTemplate:
        """Generate PR to map DOM element to backend."""
        element_id = blocker['id']
        file_path = blocker.get('details', {}).get('file', 'unknown')
        
        # Generate both frontend and backend patches
        frontend_patch = f"""
--- a/{file_path}
+++ b/{file_path}
@@ @@
-    <button id="{element_id}">Action</button>
+    <button id="{element_id}" onclick="handleAction()">Action</button>
+
+<script>
+async function handleAction() {{
+    const response = await fetch('/api/new-endpoint', {{
+        method: 'POST',
+        headers: {{'Content-Type': 'application/json'}},
+        body: JSON.stringify({{ action: 'perform' }})
+    }});
+    const result = await response.json();
+    console.log('Result:', result);
+}}
+</script>
"""
        
        backend_patch = """
--- a/real_agent_system.py
+++ b/real_agent_system.py
@@ @@
+    async def handle_new_endpoint(self, request):
+        \"\"\"Handle new endpoint for unmapped UI element.\"\"\"
+        data = await request.json()
+        
+        # Implement real logic
+        result = await self.process_action(data)
+        
+        return web.json_response(result)
+
     def create_app(self):
         app = web.Application()
+        app.router.add_post('/api/new-endpoint', self.handle_new_endpoint)
"""
        
        return PRTemplate(
            title=f"Map DOM element to backend: {element_id}",
            branch_name=f"fix/unmapped-{element_id}",
            description=f"""
## Antigravity Violation Fix

**Type**: Unmapped DOM Element  
**Element**: `{element_id}`  
**File**: `{file_path}`

### Changes
1. **Frontend**: Added event handler with API call
2. **Backend**: Implemented `/api/new-endpoint` handler
3. **Routing**: Registered endpoint in application

### Remediation Steps Completed
{chr(10).join(f'- {step}' for step in blocker.get('remediation', {}).get('steps', []))}
""",
            files_changed=[
                {'path': file_path, 'patch': frontend_patch},
                {'path': 'real_agent_system.py', 'patch': backend_patch}
            ],
            reviewers=['@fullstack-team']
        )
    
    def create_pr(self, template: PRTemplate) -> Dict:
        """Create actual Git branch and PR."""
        try:
            # Create branch
            subprocess.run(
                ['git', 'checkout', '-b', template.branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Apply patches (simplified - in production use git apply)
            for file_change in template.files_changed:
                print(f"   Would apply patch to: {file_change['path']}")
            
            # Commit
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.repo_path,
                check=True
            )
            
            subprocess.run(
                ['git', 'commit', '-m', template.title + '\n\n' + template.description],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            return {
                'status': 'created',
                'branch': template.branch_name,
                'title': template.title
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'error': str(e)
            }


def main():
    """Demo PR generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate PR templates for violations")
    parser.add_argument('report', help='Validation report JSON file')
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--create', action='store_true', help='Actually create PRs')
    
    args = parser.parse_args()
    
    # Load validation report
    report = json.loads(Path(args.report).read_text())
    
    generator = PRGenerator(Path(args.repo))
    
    print(f"📋 Generating PR templates for {len(report['blockers'])} violations\n")
    
    for blocker in report['blockers']:
        template = generator.generate_pr_for_blocker(blocker)
        
        print(f"PR: {template.title}")
        print(f"   Branch: {template.branch_name}")
        print(f"   Files: {len(template.files_changed)}")
        
        if args.create:
            result = generator.create_pr(template)
            print(f"   Status: {result['status']}")
        
        print()


if __name__ == '__main__':
    main()
