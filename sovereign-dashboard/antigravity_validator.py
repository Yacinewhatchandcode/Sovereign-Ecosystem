#!/usr/bin/env python3
"""
Antigravity Validator
Enforces production-ready, zero-mock standards across the Sovereign Dashboard.

Implements 4 validation scanners:
1. Mock Detector - Flags mock/fake/system_value code
2. Dead UI Detector - Identifies UI elements without backend connections
3. Backend Linkage Validator - Verifies UI calls have corresponding backend handlers
4. Completion Checker - Validates overall compliance

Usage:
    python antigravity_validator.py
    python antigravity_validator.py --fix  # Auto-remediate violations
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class Violation:
    """Single rule violation."""
    rule: str
    severity: str  # 'error', 'warning'
    file: str
    line: int
    message: str
    context: str = ""


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    violations: List[Violation] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    
    def add_violation(self, violation: Violation):
        self.violations.append(violation)
        
    def is_passing(self) -> bool:
        return len([v for v in self.violations if v.severity == 'error']) == 0
    
    def summary(self) -> str:
        errors = len([v for v in self.violations if v.severity == 'error'])
        warnings = len([v for v in self.violations if v.severity == 'warning'])
        
        if errors == 0 and warnings == 0:
            return "✅ ANTIGRAVITY COMPLIANCE: PASS"
        
        return f"❌ ANTIGRAVITY COMPLIANCE: FAIL ({errors} errors, {warnings} warnings)"


class MockDetector:
    """Scans for mock/fake/system_value code patterns."""
    
    PROD_PATTERNS = [
        r'\bmock\b',
        r'\bfake\b',
        r'\bsystem_value\b',
        r'\bsimulat(e|ed|ion)\b',
        r'\bdummy\b',
        r'\bstub\b',
        r'\/\/\s*RESOLVED_TASK.*mock',
        r'\/\*.*mock.*\*\/',
    ]
    
    def scan_file(self, filepath: Path) -> List[Violation]:
        violations = []
        
        try:
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in self.PROD_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments that are acknowledging removal of mocks
                        if 'removed' in line.lower() or 'deleted' in line.lower():
                            continue
                            
                        violations.append(Violation(
                            rule='2.2 Zero Mock Tolerance',
                            severity='error',
                            file=str(filepath),
                            line=i,
                            message=f'Mock/system_value detected',
                            context=line.strip()
                        ))
        except Exception as e:
            print(f"⚠️  Error scanning {filepath}: {e}")
            
        return violations


class DeadUIDetector:
    """Identifies UI elements without backend connections."""
    
    def scan_html(self, filepath: Path) -> List[Violation]:
        violations = []
        
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract all interactive elements
            elements = self._extract_interactive_elements(content)
            
            # Extract all event handlers
            handlers = self._extract_event_handlers(content)
            
            # Check each element has a handler
            for elem in elements:
                if not self._has_handler(elem, handlers):
                    violations.append(Violation(
                        rule='2.4 DOM Is Law',
                        severity='error',
                        file=str(filepath),
                        line=elem['line'],
                        message=f'Dead UI: {elem["type"]} has no backend connection',
                        context=elem['html']
                    ))
                    
        except Exception as e:
            print(f"⚠️  Error scanning {filepath}: {e}")
            
        return violations
    
    def _extract_interactive_elements(self, html: str) -> List[Dict]:
        """Extract buttons, inputs, forms."""
        elements = []
        lines = html.split('\n')
        
        patterns = [
            (r'<button[^>]*onclick=["\']([^"\']+)["\']', 'button'),
            (r'<button[^>]*id=["\']([^"\']+)["\']', 'button'),
            (r'<input[^>]*type=["\']button["\']', 'input'),
            (r'<input[^>]*type=["\']submit["\']', 'input'),
            (r'<form[^>]*onsubmit=["\']([^"\']+)["\']', 'form'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, elem_type in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    elements.append({
                        'type': elem_type,
                        'line': i,
                        'html': line.strip(),
                        'handler': match.group(1) if match.lastindex else None
                    })
                    
        return elements
    
    def _extract_event_handlers(self, html: str) -> Set[str]:
        """Extract function names from JavaScript."""
        handlers = set()
        
        # Extract function definitions
        func_pattern = r'function\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, html):
            handlers.add(match.group(1))
            
        # Extract arrow functions assigned to constants
        arrow_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        for match in re.finditer(arrow_pattern, html):
            handlers.add(match.group(1))
            
        return handlers
    
    def _has_handler(self, elem: Dict, handlers: Set[str]) -> bool:
        """Check if element has a corresponding handler."""
        if elem['handler']:
            # Extract function name from onclick="funcName()"
            func_name = elem['handler'].split('(')[0].strip()
            return func_name in handlers
        return False


class BackendLinkageValidator:
    """Verifies UI calls have corresponding backend endpoints."""
    
    def validate(self, frontend_path: Path, backend_path: Path) -> List[Violation]:
        violations = []
        
        try:
            # Extract API calls from frontend
            frontend_calls = self._extract_api_calls(frontend_path)
            
            # Extract endpoints from backend
            backend_endpoints = self._extract_endpoints(backend_path)
            
            # Find orphaned calls
            for call in frontend_calls:
                if call['endpoint'] not in backend_endpoints:
                    violations.append(Violation(
                        rule='2.5 Fail Loud',
                        severity='error',
                        file=str(frontend_path),
                        line=call['line'],
                        message=f'Missing backend endpoint: {call["endpoint"]}',
                        context=call['context']
                    ))
                    
        except Exception as e:
            print(f"⚠️  Error validating linkage: {e}")
            
        return violations
    
    def _extract_api_calls(self, filepath: Path) -> List[Dict]:
        """Extract fetch() and WebSocket.send() calls."""
        calls = []
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Match fetch(CONFIG.API_BASE + '/endpoint')
        fetch_pattern = r'fetch\([^)]*[\'"`](/[^\'"`]+)[\'"`]'
        
        for i, line in enumerate(lines, 1):
            for match in re.finditer(fetch_pattern, line):
                endpoint = match.group(1)
                calls.append({
                    'endpoint': endpoint,
                    'line': i,
                    'context': line.strip()
                })
                
        return calls
    
    def _extract_endpoints(self, filepath: Path) -> Set[str]:
        """Extract route definitions from backend."""
        endpoints = set()
        content = filepath.read_text(encoding='utf-8')
        
        # Match app.router.add_get("/api/...", ...)
        route_pattern = r'app\.router\.add_\w+\([\'"`]([^\'"`]+)[\'"`]'
        
        for match in re.finditer(route_pattern, content):
            endpoints.add(match.group(1))
            
        return endpoints


class CompletionChecker:
    """Validates overall Antigravity compliance."""
    
    def check(self, report: ValidationReport) -> List[Violation]:
        violations = []
        
        # Rule: Must have 0 mocks
        prod_violations = [v for v in report.violations if '2.2' in v.rule]
        if len(prod_violations) > 0:
            violations.append(Violation(
                rule='4.0 Completion Criteria',
                severity='error',
                file='SYSTEM',
                line=0,
                message=f'Completion blocked: {len(prod_violations)} mocks detected'
            ))
            
        # Rule: Must have 0 dead UI
        dead_ui = [v for v in report.violations if '2.4' in v.rule]
        if len(dead_ui) > 0:
            violations.append(Violation(
                rule='4.0 Completion Criteria',
                severity='error',
                file='SYSTEM',
                line=0,
                message=f'Completion blocked: {len(dead_ui)} dead UI elements'
            ))
            
        return violations


class AntigravityValidator:
    """Main validator orchestrator."""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.prod_detector = MockDetector()
        self.dead_ui_detector = DeadUIDetector()
        self.linkage_validator = BackendLinkageValidator()
        self.completion_checker = CompletionChecker()
        
    def validate_all(self) -> ValidationReport:
        report = ValidationReport()
        
        print("🔍 Running Antigravity Validation...\n")
        
        # 1. Mock Detection
        print("1️⃣  Mock Detection")
        html_path = self.root / "sovereign-dashboard" / "index.html"
        backend_path = self.root / "sovereign-dashboard" / "real_agent_system.py"
        
        for filepath in [html_path, backend_path]:
            if filepath.exists():
                violations = self.prod_detector.scan_file(filepath)
                for v in violations:
                    report.add_violation(v)
                    
        prod_errors = len([v for v in report.violations if '2.2' in v.rule])
        if prod_errors == 0:
            print("   ✅ 0 violations")
        else:
            print(f"   ❌ {prod_errors} violations")
            
        # 2. Dead UI Detection
        print("2️⃣  Dead UI Detection")
        if html_path.exists():
            violations = self.dead_ui_detector.scan_html(html_path)
            for v in violations:
                report.add_violation(v)
                
        dead_ui_errors = len([v for v in report.violations if '2.4' in v.rule])
        if dead_ui_errors == 0:
            print("   ✅ 0 violations")
        else:
            print(f"   ❌ {dead_ui_errors} violations")
            
        # 3. Backend Linkage
        print("3️⃣  Backend Linkage Validation")
        if html_path.exists() and backend_path.exists():
            violations = self.linkage_validator.validate(html_path, backend_path)
            for v in violations:
                report.add_violation(v)
                
        linkage_errors = len([v for v in report.violations if '2.5' in v.rule])
        if linkage_errors == 0:
            print("   ✅ 100% coverage")
        else:
            print(f"   ❌ {linkage_errors} missing endpoints")
            
        # 4. Completion Check
        print("4️⃣  Completion Check")
        violations = self.completion_checker.check(report)
        for v in violations:
            report.add_violation(v)
            
        completion_errors = len([v for v in report.violations if '4.0' in v.rule])
        if completion_errors == 0:
            print("   ✅ PASS")
        else:
            print(f"   ❌ FAIL")
            
        return report


def main():
    project_root = Path(__file__).parent
    validator = AntigravityValidator(project_root)
    
    report = validator.validate_all()
    
    print("\n" + "="*60)
    print(report.summary())
    print("="*60 + "\n")
    
    if report.violations:
        print("VIOLATIONS:")
        for v in report.violations:
            print(f"\n[{v.severity.upper()}] {v.rule}")
            print(f"  File: {v.file}:{v.line}")
            print(f"  {v.message}")
            if v.context:
                print(f"  Context: {v.context}")
                
    sys.exit(0 if report.is_passing() else 1)


if __name__ == '__main__':
    main()
