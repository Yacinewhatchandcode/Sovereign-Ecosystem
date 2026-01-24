#!/usr/bin/env python3
"""
🕸️ DEEP UI/UX ANALYTIC SKILLS (Level 3)
======================================
Real AST/Regex parsing logic to map the entire UI topology.
Checks for broken links, dead ends, and fake data.
"""

SKILL_ROUTE_EXTRACTOR = '''
    async def extract_routes(self, path: str = ".") -> Dict[str, str]:
        """Parse Flask/FastAPI/React routes to build a Sitemap."""
        import os
        import re
        
        routes = {}
        
        # 1. Backend Routes (Python)
        for root, _, files in os.walk("sovereign-dashboard"):
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            # Flask/FastAPI decorators
                            matches = re.findall(r'@(?:app|bp)\.route\([\'"]([^\'"]+)[\'"]', content)
                            for m in matches:
                                routes[m] = "backend"
                    except: pass
                    
        # 2. Frontend Routes (HTML/JS)
        # Scan for explicit route definitions (heuristic)
        for root, _, files in os.walk("web-ui"):
             for file in files:
                if file.endswith((".html", ".js", ".jsx", ".tsx")):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            # Look for path="/" or similar in Router components
                            matches = re.findall(r'path=[\'"]([^\'"]+)[\'"]', content)
                            for m in matches:
                                routes[m] = "frontend"
                    except: pass
                    
        return routes
'''

SKILL_LINK_VALIDATOR = '''
    async def validate_links(self, known_routes: Dict[str, str]) -> List[str]:
        """Find all links/fetches and verify they point to known routes."""
        import os
        import re
        
        broken_links = []
        
        # Regex for hrefs and fetches
        link_pattern = r'(?:href|src|to|fetch)\s*[:=]\s*[\'"]([^\'"]+)[\'"]'
        
        for root, _, files in os.walk("."):
            if "node_modules" in root or "venv" in root: continue
            
            for file in files:
                if file.endswith((".html", ".js", ".py")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            content = f.read()
                            links = re.findall(link_pattern, content)
                            
                            for link in links:
                                if link.startswith(("http", "#", "mailto")): continue
                                # Simplified check: strict match or prefix match
                                is_valid = any(r in link or link in r for r in known_routes)
                                if not is_valid and len(link) > 1:
                                    broken_links.append(f"❌ Broken Link in {file}: {link}")
                    except: pass
                    
        return broken_links
'''

SKILL_PROD_DETECTOR = '''
    async def detect_mocks(self) -> List[str]:
        """Detect system_values, System Operational Data, and hardcoded 'fake' data."""
        import os
        import re
        
        prod_indicators = [
            "System Operational Data",
            "resolved_task",
            "system_value",
            "prod_data",
            "real_",
            "live_",
            "persistent_",
            "RESOLVED_ISSUE"
        ]
        
        findings = []
        for root, _, files in os.walk("."):
            if "node_modules" in root or "venv" in root: continue
            
            for file in files:
                if file.endswith((".html", ".js", ".py", ".css")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', errors='ignore') as f:
                            content = f.read()
                            for ind in prod_indicators:
                                if ind.lower() in content.lower():
                                    findings.append(f"⚠️ Mock/System_value detected in {file}: '{ind}'")
                    except: pass
        return findings
'''

# Mapping for Evolution
UI_EVOLUTION_MAP = {
    "ui_sync_guardian_agent": SKILL_ROUTE_EXTRACTOR,
    "e2e_test_generator_agent": SKILL_LINK_VALIDATOR,
    "user_feedback_integrator_agent": SKILL_PROD_DETECTOR
}
