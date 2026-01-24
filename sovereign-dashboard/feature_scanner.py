#!/usr/bin/env python3
"""
🔍 AZIREM DEEP FEATURE SCANNER
==============================
REAL disk scanner that discovers all backend and frontend features.
Zero mocks - scans actual files and analyzes real code.
"""

import os
import re
import json
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Callable, Set
from pathlib import Path
import ast


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class BackendFeature:
    """A discovered backend feature."""
    id: str
    name: str
    feature_type: str  # "api", "agent", "model", "service", "util", "mcp", "database"
    file_path: str
    line_number: int
    description: str
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class FrontendFeature:
    """A discovered frontend feature."""
    id: str
    name: str
    feature_type: str  # "component", "page", "route", "style", "script", "template"
    file_path: str
    line_number: int
    description: str
    props: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class FeatureInventory:
    """Complete inventory of all discovered features."""
    backend: List[BackendFeature] = field(default_factory=list)
    frontend: List[FrontendFeature] = field(default_factory=list)
    scan_path: str = ""
    scan_time: str = ""
    total_files_scanned: int = 0
    total_features: int = 0
    
    def to_dict(self):
        return {
            "backend": [f.to_dict() for f in self.backend],
            "frontend": [f.to_dict() for f in self.frontend],
            "scan_path": self.scan_path,
            "scan_time": self.scan_time,
            "total_files_scanned": self.total_files_scanned,
            "total_features": len(self.backend) + len(self.frontend),
            "summary": {
                "backend_count": len(self.backend),
                "frontend_count": len(self.frontend),
                "by_type": self._count_by_type()
            }
        }
    
    def _count_by_type(self) -> dict:
        counts = {}
        for f in self.backend:
            counts[f.feature_type] = counts.get(f.feature_type, 0) + 1
        for f in self.frontend:
            counts[f.feature_type] = counts.get(f.feature_type, 0) + 1
        return counts


# =============================================================================
# PATTERN MATCHERS
# =============================================================================

# Backend patterns
BACKEND_PATTERNS = {
    "agent": [
        r"class\s+(\w*Agent\w*)\s*[:\(]",
        r"class\s+(\w*Orchestrator\w*)\s*[:\(]",
        r"class\s+(\w*Executor\w*)\s*[:\(]",
    ],
    "api": [
        r"@app\.(get|post|put|delete|patch)\s*\(['\"]([^'\"]+)['\"]",
        r"@router\.(get|post|put|delete|patch)\s*\(['\"]([^'\"]+)['\"]",
        r"async\s+def\s+handle_(\w+)\s*\(",
    ],
    "model": [
        r"class\s+(\w+)\s*\(\s*(?:Base|Model|db\.Model)\s*\)",
        r"@dataclass\s*\nclass\s+(\w+)",
    ],
    "service": [
        r"class\s+(\w*Service\w*)\s*[:\(]",
        r"class\s+(\w*Manager\w*)\s*[:\(]",
        r"class\s+(\w*Handler\w*)\s*[:\(]",
    ],
    "mcp": [
        r"mcp\.(tool|resource|prompt)\s*\(",
        r"from\s+mcp\s+import",
        r"MCPServer|MCPClient|MCPTool",
    ],
    "database": [
        r"CREATE\s+TABLE\s+(\w+)",
        r"conn\s*=\s*sqlite3\.connect",
        r"engine\s*=\s*create_engine",
    ],
}

# Frontend patterns
FRONTEND_PATTERNS = {
    "component": [
        r"class\s+(\w+)\s+extends\s+(?:React\.)?Component",
        r"function\s+(\w+)\s*\([^)]*\)\s*{\s*return\s*\(",
        r"const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\(",
        r"<template>\s*<(\w+)",
    ],
    "page": [
        r'<title[^>]*>([^<]+)</title>',
        r"export\s+default\s+function\s+(\w*Page\w*)",
    ],
    "route": [
        r"path:\s*['\"]([^'\"]+)['\"]",
        r"Route\s+path=['\"]([^'\"]+)['\"]",
        r"router\.(push|replace)\s*\(['\"]([^'\"]+)['\"]",
    ],
    "style": [
        r"\.(\w+)\s*{",
        r"--(\w[\w-]*)\s*:",
    ],
    "event": [
        r"on(\w+)\s*=\s*{",
        r"addEventListener\s*\(['\"](\w+)['\"]",
        r"@(\w+)\s*=",
    ],
}


# =============================================================================
# FEATURE SCANNER
# =============================================================================

class FeatureScanner:
    """
    Deep scanner for discovering all backend and frontend features.
    
    Scans:
    - Python files for APIs, agents, models, services
    - JavaScript/TypeScript for components, routes
    - HTML for pages, templates
    - CSS for styles, design tokens
    - SQL for database schemas
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "/Users/yacinebenhamou/aSiReM"
        self.inventory = FeatureInventory()
        self.callback: Optional[Callable] = None
        self.files_scanned = 0
        self.feature_id = 0
        
        # Skip patterns
        self.skip_dirs = {
            '__pycache__', 'node_modules', '.git', 'venv', 'venv-speaking',
            '.venv', 'dist', 'build', '.next', '.cache', 'coverage'
        }
        
    def set_callback(self, callback: Callable):
        """Set callback for real-time updates."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: dict):
        """Emit event to callback."""
        if self.callback:
            await self.callback(event_type, data)
            
    def _get_feature_id(self) -> str:
        """Generate unique feature ID."""
        self.feature_id += 1
        return f"feat_{self.feature_id:05d}"
        
    async def scan_backend(self, path: str = None) -> List[BackendFeature]:
        """Scan for backend features (Python, SQL, etc.)."""
        path = path or self.base_path
        features = []
        
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                filepath = os.path.join(root, file)
                
                if file.endswith('.py'):
                    features.extend(await self._scan_python_file(filepath))
                elif file.endswith('.sql'):
                    features.extend(await self._scan_sql_file(filepath))
                    
                self.files_scanned += 1
                
                # Emit progress every 100 files
                if self.files_scanned % 100 == 0:
                    await self.emit("scan_progress", {
                        "files_scanned": self.files_scanned,
                        "features_found": len(features),
                        "current_file": filepath
                    })
                    
        self.inventory.backend = features
        return features
        
    async def _scan_python_file(self, filepath: str) -> List[BackendFeature]:
        """Scan a Python file for backend features."""
        features = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return features
            
        # Check each pattern type
        for feature_type, patterns in BACKEND_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get matched name
                    groups = match.groups()
                    name = groups[0] if groups else match.group(0)
                    if isinstance(name, tuple):
                        name = name[-1] if name else "unknown"
                        
                    # Get context (surrounding lines)
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 3)
                    context = '\n'.join(lines[start_line:end_line])
                    
                    # Create feature
                    feature = BackendFeature(
                        id=self._get_feature_id(),
                        name=str(name),
                        feature_type=feature_type,
                        file_path=filepath,
                        line_number=line_num,
                        description=self._extract_docstring(content, line_num) or f"{feature_type}: {name}",
                        dependencies=self._extract_imports(content),
                        capabilities=self._extract_methods(content, str(name))
                    )
                    features.append(feature)
                    
        return features
        
    async def _scan_sql_file(self, filepath: str) -> List[BackendFeature]:
        """Scan SQL file for database features."""
        features = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return features
            
        # Find CREATE TABLE statements
        for match in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            table_name = match.group(1)
            
            feature = BackendFeature(
                id=self._get_feature_id(),
                name=table_name,
                feature_type="database",
                file_path=filepath,
                line_number=line_num,
                description=f"Database table: {table_name}",
                capabilities=self._extract_table_columns(content, table_name)
            )
            features.append(feature)
            
        return features
        
    async def scan_frontend(self, path: str = None) -> List[FrontendFeature]:
        """Scan for frontend features (HTML, JS, CSS, etc.)."""
        path = path or self.base_path
        features = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                filepath = os.path.join(root, file)
                
                if file.endswith('.html'):
                    features.extend(await self._scan_html_file(filepath))
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    features.extend(await self._scan_js_file(filepath))
                elif file.endswith('.css'):
                    features.extend(await self._scan_css_file(filepath))
                    
                self.files_scanned += 1
                
        self.inventory.frontend = features
        return features
        
    async def _scan_html_file(self, filepath: str) -> List[FrontendFeature]:
        """Scan HTML file for frontend features."""
        features = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return features
            
        # Extract page title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else os.path.basename(filepath)
        
        # Create page feature
        feature = FrontendFeature(
            id=self._get_feature_id(),
            name=title,
            feature_type="page",
            file_path=filepath,
            line_number=1,
            description=f"HTML Page: {title}",
            props=self._extract_html_elements(content),
            events=self._extract_js_events(content)
        )
        features.append(feature)
        
        return features
        
    async def _scan_js_file(self, filepath: str) -> List[FrontendFeature]:
        """Scan JavaScript/TypeScript file for components."""
        features = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return features
            
        # Find React components
        for pattern in FRONTEND_PATTERNS["component"]:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                groups = match.groups()
                name = groups[0] if groups else "Component"
                
                feature = FrontendFeature(
                    id=self._get_feature_id(),
                    name=str(name),
                    feature_type="component",
                    file_path=filepath,
                    line_number=line_num,
                    description=f"React Component: {name}",
                    props=self._extract_react_props(content, str(name)),
                    events=[]
                )
                features.append(feature)
                
        return features
        
    async def _scan_css_file(self, filepath: str) -> List[FrontendFeature]:
        """Scan CSS file for styles and design tokens."""
        features = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return features
            
        # Find CSS custom properties (design tokens)
        tokens = re.findall(r'--([\w-]+)\s*:', content)
        if tokens:
            feature = FrontendFeature(
                id=self._get_feature_id(),
                name=os.path.basename(filepath),
                feature_type="style",
                file_path=filepath,
                line_number=1,
                description=f"Stylesheet with {len(tokens)} design tokens",
                props=list(set(tokens))[:20],  # Limit to 20
                events=[]
            )
            features.append(feature)
            
        return features
        
    async def full_scan(self, path: str = None) -> FeatureInventory:
        """Perform a full scan of all features."""
        path = path or self.base_path
        
        await self.emit("scan_started", {"path": path})
        
        # Reset counters
        self.files_scanned = 0
        self.feature_id = 0
        self.inventory = FeatureInventory()
        self.inventory.scan_path = path
        self.inventory.scan_time = datetime.now().isoformat()
        
        # Scan backend
        await self.emit("scanning_backend", {"path": path})
        backend = await self.scan_backend(path)
        
        # Scan frontend
        await self.emit("scanning_frontend", {"path": path})
        frontend = await self.scan_frontend(path)
        
        # Update inventory
        self.inventory.backend = backend
        self.inventory.frontend = frontend
        self.inventory.total_files_scanned = self.files_scanned
        self.inventory.total_features = len(backend) + len(frontend)
        
        await self.emit("scan_completed", {
            "total_files": self.files_scanned,
            "backend_features": len(backend),
            "frontend_features": len(frontend),
            "total_features": self.inventory.total_features
        })
        
        return self.inventory
        
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _extract_docstring(self, content: str, line_num: int) -> Optional[str]:
        """Extract docstring near a line."""
        lines = content.split('\n')
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + 10)
        
        for i in range(start, end):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Find end of docstring
                quote = '"""' if '"""' in line else "'''"
                if line.count(quote) >= 2:
                    return line.strip(quote).strip()
                for j in range(i+1, min(len(lines), i+10)):
                    if quote in lines[j]:
                        return ' '.join(lines[i:j+1]).replace(quote, '').strip()[:200]
        return None
        
    def _extract_imports(self, content: str) -> List[str]:
        """Extract imports from Python content."""
        imports = []
        for match in re.finditer(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE):
            imports.append(match.group(1))
        return list(set(imports))[:10]  # Limit to 10
        
    def _extract_methods(self, content: str, class_name: str) -> List[str]:
        """Extract method names from a class."""
        methods = []
        # Simple pattern - find def inside class
        pattern = rf"class\s+{class_name}.*?(?=\nclass\s|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            class_content = match.group(0)
            for m in re.finditer(r"def\s+(\w+)\s*\(", class_content):
                method = m.group(1)
                if not method.startswith('_'):
                    methods.append(method)
        return methods[:10]  # Limit to 10
        
    def _extract_table_columns(self, content: str, table_name: str) -> List[str]:
        """Extract column names from CREATE TABLE."""
        # Find the CREATE TABLE block
        pattern = rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{table_name}\s*\((.*?)\)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            columns_str = match.group(1)
            columns = []
            for line in columns_str.split(','):
                line = line.strip()
                if line and not line.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    parts = line.split()
                    if parts:
                        columns.append(parts[0])
            return columns
        return []
        
    def _extract_html_elements(self, content: str) -> List[str]:
        """Extract significant HTML elements."""
        elements = []
        for match in re.finditer(r'<(\w+)[^>]*(?:id|class)=["\']([^"\']+)["\']', content):
            elements.append(f"{match.group(1)}#{match.group(2)}")
        return list(set(elements))[:20]
        
    def _extract_js_events(self, content: str) -> List[str]:
        """Extract JavaScript event handlers."""
        events = []
        for m in re.finditer(r'on(\w+)\s*=|addEventListener\s*\([\'"](\w+)[\'"]', content):
            event = m.group(1) or m.group(2)
            if event:
                events.append(event)
        return list(set(events))
        
    def _extract_react_props(self, content: str, component_name: str) -> List[str]:
        """Extract React component props."""
        props = []
        # Look for props destructuring
        pattern = rf"(?:function\s+{component_name}|const\s+{component_name}\s*=)\s*\(\s*\{{\s*([^}}]+)\s*\}}"
        match = re.search(pattern, content)
        if match:
            props_str = match.group(1)
            for prop in props_str.split(','):
                prop = prop.strip().split('=')[0].strip()
                if prop and not prop.startswith('...'):
                    props.append(prop)
        return props


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_scanner_instance: Optional[FeatureScanner] = None

def get_feature_scanner() -> FeatureScanner:
    """Get the global feature scanner instance."""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = FeatureScanner()
    return _scanner_instance


if __name__ == "__main__":
    # Test the scanner
    import asyncio
    
    async def test():
        scanner = get_feature_scanner()
        
        # Quick scan just the sovereign-dashboard
        inventory = await scanner.full_scan("/Users/yacinebenhamou/aSiReM/sovereign-dashboard")
        
        print(f"\n📊 SCAN RESULTS")
        print(f"   Files scanned: {inventory.total_files_scanned}")
        print(f"   Backend features: {len(inventory.backend)}")
        print(f"   Frontend features: {len(inventory.frontend)}")
        
        print(f"\n🔧 BACKEND FEATURES:")
        for f in inventory.backend[:10]:
            print(f"   [{f.feature_type}] {f.name} @ {os.path.basename(f.file_path)}:{f.line_number}")
            
        print(f"\n🎨 FRONTEND FEATURES:")
        for f in inventory.frontend[:5]:
            print(f"   [{f.feature_type}] {f.name} @ {os.path.basename(f.file_path)}")
            
    asyncio.run(test())
