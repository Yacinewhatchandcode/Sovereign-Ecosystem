#!/usr/bin/env python3
"""
AZIREM Disk Discovery Scanner
============================
READ-ONLY inventory of the entire aSiReM workspace.
Rule: inventory → map → freeze → orchestrate → intelligence

Follows Antigravity Engineering Standards:
- No writes to source files
- Deterministic, reproducible outputs
- Classification before intelligence
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set
from collections import defaultdict
import fnmatch

# ============================================================================
# CLASSIFICATION SYSTEM
# ============================================================================

class Classification:
    """File type classifications for the AZIREM ecosystem."""
    AGENT = "agent"           # Agent implementations
    SCRIPT = "script"         # Executable scripts, demos
    LIB = "lib"               # Libraries, utilities
    CONFIG = "config"         # Configuration files
    DATA = "data"             # Data files (JSON, CSV, etc.)
    DOC = "doc"               # Documentation (MD, TXT, RST)
    UI = "ui"                 # Frontend/UI files
    TEST = "test"             # Test files
    CACHE = "cache"           # Cache/build artifacts
    UNKNOWN = "unknown"       # Unclassified

    @staticmethod
    def get_all() -> List[str]:
        return [Classification.AGENT, Classification.SCRIPT, 
                Classification.LIB, Classification.CONFIG, 
                Classification.DATA, Classification.DOC,
                Classification.UI, Classification.TEST,
                Classification.CACHE, Classification.UNKNOWN]


# Classification patterns
CLASSIFICATION_RULES = {
    # Agent patterns (files containing agent implementations)
    Classification.AGENT: {
        "filename_patterns": ["*_agent.py", "*agent*.py", "base_agent.py"],
        "content_patterns": ["class.*Agent", "BaseAgent", "def think(", "def execute("],
        "dir_patterns": ["agents", "*agent*"],
    },
    # Script patterns
    Classification.SCRIPT: {
        "filename_patterns": ["demo*.py", "run*.py", "test_*.py", "quick_*.py", "*.sh", "main.py"],
        "content_patterns": ["if __name__", "argparse", "click.command"],
        "dir_patterns": ["scripts", "bin"],
    },
    # Library/utility patterns
    Classification.LIB: {
        "filename_patterns": ["*_utils.py", "*_helper*.py", "util*.py", "helper*.py"],
        "content_patterns": ["def ", "class "],  # Generic, lowest priority
        "dir_patterns": ["lib", "utils", "helpers", "common"],
    },
    # Config patterns
    Classification.CONFIG: {
        "filename_patterns": ["*.yaml", "*.yml", "*.toml", "*.ini", "*.env*", 
                              "*config*.py", "settings.py", "pyproject.toml",
                              "requirements*.txt", "package*.json", "*.lock"],
        "content_patterns": [],
        "dir_patterns": ["config", "settings", ".config"],
    },
    # Data patterns
    Classification.DATA: {
        "filename_patterns": ["*.json", "*.csv", "*.xml", "*.sqlite", "*.db",
                              "*.parquet", "*.pkl", "*.npy"],
        "content_patterns": [],
        "dir_patterns": ["data", "datasets", "output", "results"],
    },
    # Documentation patterns
    Classification.DOC: {
        "filename_patterns": ["*.md", "*.rst", "*.txt", "README*", "CHANGELOG*",
                              "LICENSE*", "CONTRIBUTING*", "*GUIDE*.md", "*PLAN*.md"],
        "content_patterns": [],
        "dir_patterns": ["docs", "documentation"],
    },
    # UI patterns
    Classification.UI: {
        "filename_patterns": ["*.html", "*.css", "*.js", "*.jsx", "*.tsx", "*.vue",
                              "*.svelte", "*.scss", "*.sass", "*.less"],
        "content_patterns": ["<!DOCTYPE", "<html", "React", "Vue", "angular"],
        "dir_patterns": ["ui", "frontend", "web", "static", "templates", "public"],
    },
    # Test patterns
    Classification.TEST: {
        "filename_patterns": ["test_*.py", "*_test.py", "conftest.py", "pytest.ini"],
        "content_patterns": ["def test_", "unittest", "pytest"],
        "dir_patterns": ["tests", "test", "__tests__", "spec"],
    },
    # Cache/build artifacts
    Classification.CACHE: {
        "filename_patterns": ["*.pyc", "*.pyo", "*.so", "*.o", "*.a"],
        "content_patterns": [],
        "dir_patterns": ["__pycache__", ".cache", "node_modules", "dist", "build",
                         ".git", ".venv", "venv", "env", ".pytest_cache", ".mypy_cache"],
    },
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FileInfo:
    """Information about a single file."""
    path: str
    name: str
    extension: str
    size_bytes: int
    classification: str
    confidence: float  # 0.0 to 1.0
    parent_dir: str
    is_executable: bool
    content_hash: Optional[str] = None  # First 1KB hash for dedup
    agent_names: List[str] = field(default_factory=list)  # Detected agent names
    imports: List[str] = field(default_factory=list)  # Python imports


@dataclass  
class DirInfo:
    """Information about a directory."""
    path: str
    name: str
    total_files: int
    total_size_bytes: int
    classifications: Dict[str, int]  # Count per classification
    depth: int
    is_package: bool  # Has __init__.py


@dataclass
class AgentDefinition:
    """Detected agent definition."""
    name: str
    file_path: str
    class_name: str
    base_class: Optional[str]
    line_number: int
    capabilities: List[str] = field(default_factory=list)


@dataclass
class InventoryReport:
    """Complete disk inventory report."""
    scan_timestamp: str
    root_path: str
    total_files: int
    total_dirs: int
    total_size_bytes: int
    files: List[FileInfo]
    dirs: List[DirInfo]
    agents: List[AgentDefinition]
    classification_summary: Dict[str, Dict]
    extension_summary: Dict[str, int]
    largest_files: List[FileInfo]
    errors: List[str]


# ============================================================================
# SCANNER IMPLEMENTATION
# ============================================================================

class AZIREMScanner:
    """
    Read-only scanner that inventories the entire workspace.
    NO WRITES - only reads and analyzes.
    """
    
    def __init__(self, root_path: str, 
                 exclude_patterns: Optional[List[str]] = None,
                 max_content_read_bytes: int = 2048):
        self.root_path = Path(root_path).resolve()
        self.exclude_patterns = exclude_patterns or [
            "__pycache__", ".git", "node_modules", ".venv", "venv",
            ".pytest_cache", ".mypy_cache", "*.pyc", ".DS_Store",
            "avatar"  # Large external project (865 files)
        ]
        self.max_content_read = max_content_read_bytes
        
        self.files: List[FileInfo] = []
        self.dirs: List[DirInfo] = []
        self.agents: List[AgentDefinition] = []
        self.errors: List[str] = []
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        name = path.name
        rel_path = str(path.relative_to(self.root_path))
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        return False
    
    def classify_file(self, path: Path, content: Optional[str] = None) -> tuple[str, float]:
        """
        Classify a file and return (classification, confidence).
        Uses filename patterns first, then content patterns for Python files.
        """
        name = path.name
        parent = path.parent.name
        ext = path.suffix.lower()
        
        scores = defaultdict(float)
        
        # Check each classification's rules
        for classification, rules in CLASSIFICATION_RULES.items():
            # Filename pattern matching (highest weight)
            for pattern in rules.get("filename_patterns", []):
                if fnmatch.fnmatch(name.lower(), pattern.lower()):
                    scores[classification] += 3.0
            
            # Directory pattern matching (medium weight)
            for pattern in rules.get("dir_patterns", []):
                if fnmatch.fnmatch(parent.lower(), pattern.lower()):
                    scores[classification] += 2.0
            
            # Content pattern matching (for Python files)
            if content and ext == ".py":
                for pattern in rules.get("content_patterns", []):
                    if pattern in content:
                        scores[classification] += 1.5
        
        # Determine best match
        if not scores:
            return Classification.UNKNOWN, 0.0
        
        best = max(scores.items(), key=lambda x: x[1])
        # Normalize confidence to 0-1 range
        max_possible = 6.5  # 3 + 2 + 1.5
        confidence = min(best[1] / max_possible, 1.0)
        
        return best[0], confidence
    
    def extract_agent_definitions(self, path: Path, content: str) -> List[AgentDefinition]:
        """Extract agent class definitions from Python files."""
        agents = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Look for class definitions
            if line.strip().startswith("class ") and "Agent" in line:
                # Parse class name and base class
                try:
                    parts = line.split("class ")[1]
                    if "(" in parts:
                        class_name = parts.split("(")[0].strip()
                        base_part = parts.split("(")[1].split(")")[0]
                        base_class = base_part.split(",")[0].strip() if base_part else None
                    else:
                        class_name = parts.split(":")[0].strip()
                        base_class = None
                    
                    agents.append(AgentDefinition(
                        name=class_name,
                        file_path=str(path),
                        class_name=class_name,
                        base_class=base_class,
                        line_number=i
                    ))
                except:
                    pass  # Skip malformed lines
        
        return agents
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python content."""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        return imports[:20]  # Limit to top 20 imports
    
    def compute_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content[:1024]).hexdigest()[:16]
    
    def scan_file(self, path: Path) -> Optional[FileInfo]:
        """Scan a single file and return FileInfo."""
        try:
            stat = path.stat()
            
            # Read content for classification (Python files only)
            content = None
            content_bytes = None
            if path.suffix == ".py" and stat.st_size < 100_000:  # < 100KB
                try:
                    content_bytes = path.read_bytes()
                    content = content_bytes[:self.max_content_read].decode('utf-8', errors='ignore')
                except:
                    pass
            
            # Classify
            classification, confidence = self.classify_file(path, content)
            
            # Extract agent definitions
            agent_names = []
            if classification == Classification.AGENT and content:
                detected = self.extract_agent_definitions(path, content)
                self.agents.extend(detected)
                agent_names = [a.name for a in detected]
            
            # Extract imports
            imports = []
            if content and path.suffix == ".py":
                imports = self.extract_imports(content)
            
            return FileInfo(
                path=str(path),
                name=path.name,
                extension=path.suffix,
                size_bytes=stat.st_size,
                classification=classification,
                confidence=confidence,
                parent_dir=path.parent.name,
                is_executable=os.access(path, os.X_OK),
                content_hash=self.compute_hash(content_bytes) if content_bytes else None,
                agent_names=agent_names,
                imports=imports
            )
            
        except Exception as e:
            self.errors.append(f"Error scanning {path}: {e}")
            return None
    
    def scan_directory(self, path: Path, depth: int = 0) -> Optional[DirInfo]:
        """Scan a directory and return DirInfo."""
        try:
            classifications = defaultdict(int)
            total_files = 0
            total_size = 0
            is_package = (path / "__init__.py").exists()
            
            for item in path.iterdir():
                if item.is_file():
                    file_info = next(
                        (f for f in self.files if f.path == str(item)), 
                        None
                    )
                    if file_info:
                        classifications[file_info.classification] += 1
                        total_files += 1
                        total_size += file_info.size_bytes
            
            return DirInfo(
                path=str(path),
                name=path.name,
                total_files=total_files,
                total_size_bytes=total_size,
                classifications=dict(classifications),
                depth=depth,
                is_package=is_package
            )
        except Exception as e:
            self.errors.append(f"Error scanning directory {path}: {e}")
            return None
    
    def scan(self) -> InventoryReport:
        """
        Perform full read-only scan of the workspace.
        Returns complete inventory report.
        """
        print(f"🔍 AZIREM Scanner: Inventorying {self.root_path}")
        print(f"   Exclusions: {', '.join(self.exclude_patterns)}")
        print()
        
        # Phase 1: Scan all files
        print("📂 Phase 1: Scanning files...")
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Filter excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if not self.should_exclude(file_path):
                    file_info = self.scan_file(file_path)
                    if file_info:
                        self.files.append(file_info)
        
        print(f"   Found {len(self.files)} files")
        
        # Phase 2: Scan directories
        print("📁 Phase 2: Analyzing directories...")
        for root, dirs, _ in os.walk(self.root_path):
            root_path = Path(root)
            if not self.should_exclude(root_path):
                depth = len(root_path.relative_to(self.root_path).parts)
                dir_info = self.scan_directory(root_path, depth)
                if dir_info:
                    self.dirs.append(dir_info)
        
        print(f"   Analyzed {len(self.dirs)} directories")
        
        # Phase 3: Build summaries
        print("📊 Phase 3: Building summaries...")
        
        # Classification summary
        classification_summary = {}
        for c in Classification.get_all():
            files_in_class = [f for f in self.files if f.classification == c]
            if files_in_class:
                classification_summary[c] = {
                    "count": len(files_in_class),
                    "total_bytes": sum(f.size_bytes for f in files_in_class),
                    "examples": [f.name for f in files_in_class[:5]]
                }
        
        # Extension summary
        extension_summary = defaultdict(int)
        for f in self.files:
            extension_summary[f.extension or "(no ext)"] += 1
        
        # Largest files
        largest_files = sorted(self.files, key=lambda x: x.size_bytes, reverse=True)[:10]
        
        # Build report
        report = InventoryReport(
            scan_timestamp=datetime.now().isoformat(),
            root_path=str(self.root_path),
            total_files=len(self.files),
            total_dirs=len(self.dirs),
            total_size_bytes=sum(f.size_bytes for f in self.files),
            files=self.files,
            dirs=self.dirs,
            agents=self.agents,
            classification_summary=classification_summary,
            extension_summary=dict(sorted(extension_summary.items(), key=lambda x: -x[1])),
            largest_files=largest_files,
            errors=self.errors
        )
        
        print(f"✅ Scan complete!")
        print(f"   Total: {report.total_files} files, {report.total_size_bytes:,} bytes")
        print(f"   Agents detected: {len(self.agents)}")
        if self.errors:
            print(f"   ⚠️  Errors: {len(self.errors)}")
        
        return report
    
    def export_report(self, report: InventoryReport, output_path: str) -> None:
        """Export report to JSON file (the ONLY write operation)."""
        # Convert dataclasses to dicts for JSON serialization
        report_dict = {
            "scan_timestamp": report.scan_timestamp,
            "root_path": report.root_path,
            "total_files": report.total_files,
            "total_dirs": report.total_dirs,
            "total_size_bytes": report.total_size_bytes,
            "classification_summary": report.classification_summary,
            "extension_summary": report.extension_summary,
            "agents": [asdict(a) for a in report.agents],
            "largest_files": [asdict(f) for f in report.largest_files],
            "errors": report.errors,
            # Files and dirs are large - optionally include
            "files_count": len(report.files),
            "dirs_count": len(report.dirs),
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"📄 Report exported to: {output_path}")


def format_bytes(size: int) -> str:
    """Format byte size to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def print_summary(report: InventoryReport) -> None:
    """Print human-readable summary of the inventory."""
    print("\n" + "=" * 70)
    print("🌌 AZIREM DISK INVENTORY REPORT")
    print("=" * 70)
    print(f"📅 Scan Time: {report.scan_timestamp}")
    print(f"📂 Root Path: {report.root_path}")
    print(f"📊 Total: {report.total_files} files, {report.total_dirs} dirs, {format_bytes(report.total_size_bytes)}")
    
    print("\n" + "-" * 70)
    print("📋 CLASSIFICATION SUMMARY")
    print("-" * 70)
    for classification, data in sorted(report.classification_summary.items()):
        print(f"  {classification:12} → {data['count']:4} files ({format_bytes(data['total_bytes']):>10})")
        if data.get('examples'):
            print(f"               Examples: {', '.join(data['examples'][:3])}")
    
    print("\n" + "-" * 70)
    print("🤖 DETECTED AGENTS")
    print("-" * 70)
    if report.agents:
        for agent in report.agents:
            base = f" → {agent.base_class}" if agent.base_class else ""
            print(f"  • {agent.class_name}{base}")
            print(f"    File: {Path(agent.file_path).name}:{agent.line_number}")
    else:
        print("  (No agents detected)")
    
    print("\n" + "-" * 70)
    print("📦 FILE EXTENSIONS")
    print("-" * 70)
    for ext, count in list(report.extension_summary.items())[:15]:
        print(f"  {ext:12} → {count:4} files")
    
    print("\n" + "-" * 70)
    print("📏 LARGEST FILES")
    print("-" * 70)
    for f in report.largest_files[:5]:
        print(f"  {format_bytes(f.size_bytes):>10} │ {f.classification:10} │ {Path(f.path).name}")
    
    if report.errors:
        print("\n" + "-" * 70)
        print("⚠️  ERRORS")
        print("-" * 70)
        for err in report.errors[:10]:
            print(f"  • {err}")
    
    print("\n" + "=" * 70)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Default to aSiReM workspace
    root = sys.argv[1] if len(sys.argv) > 1 else "/Users/yacinebenhamou/aSiReM"
    
    scanner = AZIREMScanner(root)
    report = scanner.scan()
    
    # Print summary
    print_summary(report)
    
    # Export to JSON (only write)
    output_dir = Path(root) / "azirem_discovery"
    output_dir.mkdir(exist_ok=True)
    scanner.export_report(report, str(output_dir / "inventory_frozen.json"))
