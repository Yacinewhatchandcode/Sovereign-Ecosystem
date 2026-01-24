#!/usr/bin/env python3
"""
🔍 REAL SCANNER AGENT - Full Codebase Analysis
===============================================
Scans entire codebase, extracts everything, shows real-time progress.
NO MOCKS - 100% REAL IMPLEMENTATION
"""

import os
import ast
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class ScannedFile:
    """A scanned file with all extracted information."""
    path: str
    filename: str
    extension: str
    language: str
    size_bytes: int
    lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    patterns: List[str]
    score: float
    hash: str
    timestamp: str
    @property
    def name(self) -> str:
        return self.filename

@dataclass
class ScanProgress:
    """Real-time scan progress."""
    total_files: int
    scanned_files: int
    current_file: str
    patterns_found: int
    errors: int
    start_time: str
    elapsed_seconds: float

class RealScannerAgent:
    """
    REAL Scanner Agent - No mocks, actual implementation.
    Scans codebase, extracts everything, provides real-time updates.
    """
    
    def __init__(self, broadcast_callback=None, bytebot_bridge=None):
        self.broadcast_callback = broadcast_callback
        self.bytebot_bridge = bytebot_bridge
        self.scanned_files: List[ScannedFile] = []
        self.progress = ScanProgress(0, 0, "", 0, 0, "", 0.0)
        self.start_time = None
        
        # Agentic patterns to detect
        self.patterns = [
            "agent", "async", "await", "mcp", "tool", "workflow",
            "orchestrator", "task", "execute", "llm", "ai",
            "autonomous", "multi-agent", "communication", "hub"
        ]
        
        # Language support
        self.language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "TypeScript React",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML"
        }
        
    async def broadcast(self, event_type: str, data: dict):
        """Broadcast event to dashboard."""
        if self.broadcast_callback:
            await self.broadcast_callback(event_type, {
                "agent_id": "scanner",
                "agent_name": "Scanner",
                "icon": "🔍",
                "timestamp": datetime.now().isoformat(),
                **data
            })
            
    async def scan_full_codebase(self, root_path: str, include_deep_env: bool = True) -> Dict:
        """
        Scan entire codebase - BYTEBOT ONLY MODE.
        All scanning happens INSIDE the ByteBot container, not locally.
        """
        self.start_time = datetime.now()
        self.scanned_files = []
        
        await self.broadcast("activity", {
            "message": "🐳 Starting BYTEBOT-ONLY SOVEREIGN SCAN (No local scanning)"
        })
        
        all_files = []
        
        # ========== BYTEBOT ONLY MODE ==========
        # ALL scanning happens INSIDE ByteBot container
        
        if self.bytebot_bridge:
            await self.broadcast("activity", {
                "message": "🐳 Connecting to ByteBot Ubuntu Desktop container..."
            })
            
            try:
                # Scan ByteBot workspace folders
                ubuntu_folders = [
                    "/workspace",
                    "/home/user", 
                    "/home/bytebot",
                    "/bytebot",
                    "/root/workspace"
                ]
                
                for folder in ubuntu_folders:
                    await self.broadcast("activity", {
                        "message": f"🔍 Scanning ByteBot folder: {folder}"
                    })
                    container_scan = await self.bytebot_bridge.scan_directory(folder)
                    if container_scan.get("success"):
                        for f in container_scan.get("files", []):
                            all_files.append(f"bytebot://{f}")
                        file_count = len(container_scan.get("files", []))
                        if file_count > 0:
                            await self.broadcast("activity", {
                                "message": f"✅ Found {file_count} files in {folder}"
                            })
                            
                            # VISUAL ACTION: Open Folder in ByteBot to show user we are scanning here
                            try:
                                await self.bytebot_bridge.open_finder(folder, "scanner")
                                # Also pop a terminal briefly showing ls
                                cmd = f"DISPLAY=:0 gnome-terminal -- bash -c 'cd {folder}; ls -la; echo Parsing file structure...; sleep 2'"
                                await self.bytebot_bridge.execute_command(cmd, "scanner")
                            except: pass
                            
                            await asyncio.sleep(2) # Give user time to see it
            except Exception as e:
                await self.broadcast("activity", {
                    "message": f"⚠️ ByteBot scan error: {e}"
                })
                print(f"⚠️ ByteBot scan failed: {e}")
        if self.bytebot_bridge:
            pass # Already scanned above in ByteBot mode
        else:
            await self.broadcast("activity", {
                "message": "⚠️ ByteBot not connected! Cannot scan."
            })
            return {
                "status": "error", 
                "message": "ByteBot not connected",
                "total_files": 0,
                "total_functions": 0,
                "total_classes": 0,
                "total_patterns": 0,
                "total_lines": 0,
                "languages": {},
                "top_files": [],
                "pattern_frequency": {},
                "scan_duration_seconds": 0
            }
        
        # NO LOCAL SCANNING - Everything happens in ByteBot
        # Desktop, local files are NOT scanned

        self.progress.total_files = len(all_files)
        
        await self.broadcast("scan_started", {
            "total_files": len(all_files),
            "root_path": root_path,
            "message": f"📁 Total targets discovered: {len(all_files)}"
        })
        
        # Step 3: Scan each target
        for i, target in enumerate(all_files):
            try:
                if target.startswith("bytebot://"):
                    # Scan inside container
                    scanned = await self._scan_container_file(target.replace("bytebot://", ""))
                else:
                    # Local file
                    scanned = await self._scan_file(target)
                    
                if scanned:
                    self.scanned_files.append(scanned)
                    self.progress.scanned_files = i + 1
                    self.progress.current_file = target
                    
                    # Broadcast progress every 10 files
                    if i % 10 == 0:
                        await self._broadcast_progress()
                        
            except Exception as e:
                self.progress.errors += 1
                print(f"⚠️ Error scanning {target}: {e}")
                
        # Step 4: Generate summary
        summary = await self._generate_summary()
        
        await self.broadcast("scan_completed", {
            "message": f"✅ Deep scan complete: {len(self.scanned_files)} targets analyzed",
            "summary": summary
        })
        
        return summary

    async def _scan_environment(self):
        """Scan and index environment variables."""
        env_vars = dict(os.environ)
        # Sort by key for consistency
        sorted_keys = sorted(env_vars.keys())
        
        # Create a virtual file for environment
        env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()])
        
        scanned = ScannedFile(
            path="system://environment",
            filename="host_env",
            extension=".env",
            language="Environment",
            size_bytes=len(env_content),
            lines=len(env_vars),
            functions=[],
            classes=[],
            imports=[],
            patterns=["env", "secret", "config"],
            score=5.0,
            hash=hashlib.md5(env_content.encode()).hexdigest()[:8],
            timestamp=datetime.now().isoformat()
        )
        self.scanned_files.append(scanned)

    async def _scan_container_file(self, container_path: str) -> Optional[ScannedFile]:
        """Scan a file inside the ByteBot container with deep analysis."""
        if not self.bytebot_bridge:
            return None
            
        try:
            # Read file content from container
            content = await self.bytebot_bridge.read_container_file(container_path)
            if not content:
                # Fallback to preview if full read fails
                analysis = await self.bytebot_bridge.analyze_code_file(container_path)
                content = analysis.get("preview", "")
            
            # Basic info
            filename = os.path.basename(container_path)
            extension = os.path.splitext(container_path)[1]
            language = self.language_map.get(extension, "Ubuntu Code")
            
            # Deep extraction (same logic as local files)
            functions = []
            classes = []
            imports = []
            
            if extension == '.py':
                functions, classes, imports = self._extract_python(content)
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                functions, classes, imports = self._extract_javascript(content)
                
            # Detect patterns
            patterns_found = self._detect_patterns(content)
            
            # Calculate score
            score = self._calculate_score(functions, classes, patterns_found)
            
            # Create ScannedFile entry
            return ScannedFile(
                path=f"bytebot://{container_path}",
                filename=filename,
                extension=extension,
                language=language,
                size_bytes=len(content),
                lines=len(content.split('\n')),
                functions=functions,
                classes=classes,
                imports=imports,
                patterns=patterns_found,
                score=score,
                hash=hashlib.md5(content.encode()).hexdigest()[:8],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"⚠️ Container scan error: {e}")
            return None
        
    async def _discover_files(self, root_path: str) -> List[str]:
        """Discover all relevant files asynchronously."""
        def walk_files():
            files = []
            root = Path(root_path)
            
            # Directories to skip
            skip_dirs = {
                'node_modules', '.git', '__pycache__', '.venv', 'venv',
                'dist', 'build', '.next', '.cache', 'coverage'
            }
            
            for path in root.rglob('*'):
                if path.is_file():
                    # Skip if in excluded directory
                    if any(skip in path.parts for skip in skip_dirs):
                        continue
                        
                    # Only include supported extensions
                    if path.suffix in self.language_map:
                        files.append(str(path))
            return sorted(files)
            
        return await asyncio.to_thread(walk_files)
        
    async def _scan_file(self, filepath: str) -> Optional[ScannedFile]:
        """Scan a single file and extract everything."""
        path = Path(filepath)
        
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Basic info
            extension = path.suffix
            language = self.language_map.get(extension, "Unknown")
            size_bytes = path.stat().st_size
            lines = len(content.split('\n'))
            
            # Extract based on language
            functions = []
            classes = []
            imports = []
            
            if extension == '.py':
                functions, classes, imports = self._extract_python(content)
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                functions, classes, imports = self._extract_javascript(content)
                
            # Detect patterns
            patterns_found = self._detect_patterns(content)
            
            # Calculate score
            score = self._calculate_score(functions, classes, patterns_found)
            
            # Generate hash
            file_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            
            return ScannedFile(
                path=filepath,
                filename=path.name,
                extension=extension,
                language=language,
                size_bytes=size_bytes,
                lines=lines,
                functions=functions,
                classes=classes,
                imports=imports,
                patterns=patterns_found,
                score=score,
                hash=file_hash,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️ Failed to scan {filepath}: {e}")
            return None
            
    def _extract_python(self, content: str) -> tuple:
        """Extract Python code elements."""
        functions = []
        classes = []
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
        except SyntaxError:
            pass  # Skip files with syntax errors
            
        return functions, classes, imports
        
    def _extract_javascript(self, content: str) -> tuple:
        """Extract JavaScript/TypeScript code elements (basic regex)."""
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Find function declarations
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*(?:=\s*)?(?:async\s*)?\('
        functions = re.findall(func_pattern, content)
        
        # Find class declarations
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        
        # Find imports
        import_pattern = r'import\s+.*?from\s+[\'"](.+?)[\'"]'
        imports = re.findall(import_pattern, content)
        
        return functions, classes, imports
        
    def _detect_patterns(self, content: str) -> List[str]:
        """Detect agentic patterns in content."""
        content_lower = content.lower()
        found = []
        
        for pattern in self.patterns:
            if pattern in content_lower:
                found.append(pattern)
                
        return found
        
    def _calculate_score(self, functions: List, classes: List, patterns: List) -> float:
        """Calculate relevance score."""
        score = 0.0
        
        # Points for code elements
        score += len(functions) * 0.5
        score += len(classes) * 1.0
        score += len(patterns) * 2.0
        
        # Cap at 10
        return min(score, 10.0)
        
    async def _broadcast_progress(self):
        """Broadcast current progress."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.progress.elapsed_seconds = elapsed
        
        percent = (self.progress.scanned_files / self.progress.total_files * 100) if self.progress.total_files > 0 else 0
        
        await self.broadcast("scan_progress", {
            "scanned": self.progress.scanned_files,
            "total": self.progress.total_files,
            "percent": round(percent, 1),
            "current_file": Path(self.progress.current_file).name,
            "patterns_found": self.progress.patterns_found,
            "errors": self.progress.errors,
            "elapsed_seconds": round(elapsed, 1),
            "message": f"📊 Scanned {self.progress.scanned_files}/{self.progress.total_files} files ({percent:.1f}%)"
        })
        
    async def _generate_summary(self) -> Dict:
        """Generate scan summary."""
        total_functions = sum(len(f.functions) for f in self.scanned_files)
        total_classes = sum(len(f.classes) for f in self.scanned_files)
        total_patterns = sum(len(f.patterns) for f in self.scanned_files)
        total_lines = sum(f.lines for f in self.scanned_files)
        
        # Language breakdown
        languages = {}
        for f in self.scanned_files:
            languages[f.language] = languages.get(f.language, 0) + 1
            
        # Top files by score
        top_files = sorted(self.scanned_files, key=lambda x: x.score, reverse=True)[:10]
        
        # Pattern frequency
        pattern_freq = {}
        for f in self.scanned_files:
            for p in f.patterns:
                pattern_freq[p] = pattern_freq.get(p, 0) + 1
                
        summary = {
            "total_files": len(self.scanned_files),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_patterns": total_patterns,
            "total_lines": total_lines,
            "languages": languages,
            "top_files": [{"path": f.path, "score": f.score} for f in top_files],
            "pattern_frequency": dict(sorted(pattern_freq.items(), key=lambda x: x[1], reverse=True)),
            "scan_duration_seconds": round((datetime.now() - self.start_time).total_seconds(), 1)
        }
        
        return summary
        
    async def save_results(self, output_path: str):
        """Save scan results to JSON."""
        summary = await self._generate_summary()
        
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_files": len(self.scanned_files),
            "files": [asdict(f) for f in self.scanned_files],
            "summary": summary
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"💾 Results saved to {output_path}")


# CLI usage
if __name__ == "__main__":
    import sys
    
    async def main():
        # Create scanner
        async def print_event(event_type, data):
            print(f"\n[{event_type}] {data.get('message', '')}")
            if 'percent' in data:
                print(f"  Progress: {data['percent']}%")
                
        scanner = RealScannerAgent(broadcast_callback=print_event)
        
        # Get path from args or use default
        path = sys.argv[1] if len(sys.argv) > 1 else "/Users/yacinebenhamou/aSiReM"
        
        print(f"🔍 REAL Scanner Agent - Full Codebase Scan")
        print(f"=" * 60)
        print(f"Target: {path}")
        print(f"=" * 60)
        
        # Run scan
        summary = await scanner.scan_full_codebase(path)
        
        # Print summary
        print(f"\n" + "=" * 60)
        print(f"📊 SCAN COMPLETE")
        print(f"=" * 60)
        print(f"Files scanned: {summary['total_files']}")
        print(f"Functions found: {summary['total_functions']}")
        print(f"Classes found: {summary['total_classes']}")
        print(f"Patterns detected: {summary['total_patterns']}")
        print(f"Total lines: {summary['total_lines']:,}")
        print(f"Duration: {summary['scan_duration_seconds']}s")
        
        print(f"\n📈 Languages:")
        for lang, count in summary['languages'].items():
            print(f"  {lang}: {count} files")
            
        print(f"\n⚡ Top Patterns:")
        for pattern, count in list(summary['pattern_frequency'].items())[:10]:
            print(f"  {pattern}: {count} occurrences")
            
        print(f"\n🏆 Top 5 Files:")
        for f in summary['top_files'][:5]:
            print(f"  {Path(f['path']).name} (score: {f['score']:.1f})")
            
        # Save results
        output_file = "scan_results.json"
        await scanner.save_results(output_file)
        print(f"\n💾 Full results saved to: {output_file}")
        
    asyncio.run(main())
