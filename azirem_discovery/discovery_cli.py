#!/usr/bin/env python3
"""
AZIREM Enhanced Discovery CLI
=============================
Full-featured read-only discovery that produces comprehensive manifest.
Generates JSONL shards for parallel processing.

Usage:
    python discovery_cli.py scan /path/to/scan
    python discovery_cli.py scan /path/to/scan --output /tmp/azirem_manifest
    python discovery_cli.py quick /path/to/scan  # Fast mode, top 10k files
"""

import os
import sys
import json
import re
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Generator
from collections import defaultdict
import fnmatch
import subprocess


# ============================================================================
# CONFIGURATION
# ============================================================================

# File patterns for classification
CLASSIFICATION_PATTERNS = {
    "agent": {
        "extensions": [".py"],
        "filename_patterns": ["*agent*.py", "*_agent.py"],
        "content_patterns": [r"class\s+\w*Agent", r"def\s+think\(", r"def\s+execute\("],
    },
    "script": {
        "extensions": [".py", ".sh", ".bash", ".zsh", ".ps1", ".rb", ".pl"],
        "filename_patterns": ["run*.py", "demo*.py", "test_*.py", "main.py", "*.sh"],
        "content_patterns": [r'if\s+__name__\s*==\s*["\']__main__["\']', r"argparse", r"#!/"],
    },
    "lib": {
        "extensions": [".py", ".rb", ".go", ".rs"],
        "filename_patterns": ["*_utils.py", "*_helper*.py", "util*.py", "common*.py"],
        "content_patterns": [r"^class\s+\w+", r"^def\s+\w+"],
    },
    "config": {
        "extensions": [".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".json"],
        "filename_patterns": ["*config*", "settings*", ".env*", "*.lock", "requirements*.txt",
                              "package*.json", "Pipfile*", "pyproject.toml", "Dockerfile*",
                              "docker-compose*", "Makefile", "*.mk"],
        "content_patterns": [],
    },
    "api": {
        "extensions": [".py", ".js", ".ts", ".go", ".java"],
        "filename_patterns": ["*api*.py", "*route*.py", "*endpoint*.py", "openapi*", "swagger*"],
        "content_patterns": [r"@app\.(get|post|put|delete|patch)", r"express\(\)", 
                             r"flask", r"fastapi", r"swagger", r"openapi"],
    },
    "frontend": {
        "extensions": [".html", ".css", ".js", ".jsx", ".tsx", ".vue", ".svelte", ".scss", ".sass"],
        "filename_patterns": ["*.html", "*.css", "*.jsx", "*.tsx", "*.vue"],
        "content_patterns": [r"<!DOCTYPE", r"<html", r"React", r"Vue", r"angular"],
    },
    "backend": {
        "extensions": [".py", ".js", ".ts", ".go", ".java", ".rs", ".rb"],
        "filename_patterns": ["server*.py", "app.py", "main.py", "index.js", "server.js"],
        "content_patterns": [r"express", r"flask", r"django", r"fastapi", r"gin\.", r"http\.Server"],
    },
    "secret-suspect": {
        "extensions": [".pem", ".key", ".crt", ".p12", ".pfx", ".env"],
        "filename_patterns": ["*.pem", "*.key", "*secret*", "*credential*", "*.env", ".env*"],
        "content_patterns": [r"AWS_ACCESS_KEY", r"API_KEY", r"SECRET_KEY", r"PRIVATE_KEY",
                             r"password\s*=", r"token\s*=", r"-----BEGIN.*PRIVATE KEY-----"],
    },
    "docs": {
        "extensions": [".md", ".rst", ".txt", ".adoc", ".org"],
        "filename_patterns": ["README*", "CHANGELOG*", "LICENSE*", "CONTRIBUTING*", "*.md", "docs/*"],
        "content_patterns": [],
    },
    "db": {
        "extensions": [".sql", ".sqlite", ".db", ".sqlite3"],
        "filename_patterns": ["*.sql", "migrations/*", "schema*", "*model*.py"],
        "content_patterns": [r"CREATE TABLE", r"SELECT\s+", r"sqlalchemy", r"prisma"],
    },
    "archived": {
        "extensions": [".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz"],
        "filename_patterns": ["*.zip", "*.tar.*", "*.gz", "backup*"],
        "content_patterns": [],
    },
    "media": {
        "extensions": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".webm", ".mp3", ".wav"],
        "filename_patterns": [],
        "content_patterns": [],
    },
    "test": {
        "extensions": [".py", ".js", ".ts"],
        "filename_patterns": ["test_*.py", "*_test.py", "*.test.js", "*.spec.ts", "conftest.py"],
        "content_patterns": [r"def test_", r"describe\(", r"it\(", r"unittest", r"pytest"],
    },
}

# Directories to skip
SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", ".tox", ".eggs", "*.egg-info",
    "dist", "build", ".cache", ".npm", ".yarn", "vendor",
    "Pods", ".gradle", "target", ".idea", ".vscode",
}

# Maximum file size for content analysis (10MB)
MAX_CONTENT_SIZE = 10 * 1024 * 1024


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FileEntry:
    """A single file in the manifest."""
    path: str
    size: int
    mtime: str
    tags: List[str]
    extension: str
    filename: str
    content_hash: Optional[str] = None
    snippets: List[Dict] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    apis: List[Dict] = field(default_factory=list)
    secrets_found: bool = False
    secret_lines: List[int] = field(default_factory=list)  # Line numbers only, not content!


@dataclass
class ManifestShard:
    """A shard of the manifest (for parallel processing)."""
    shard_id: str
    created_at: str
    scanner_version: str = "1.0.0"
    files: List[FileEntry] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


# ============================================================================
# CLASSIFIER
# ============================================================================

class FileClassifier:
    """Classifies files based on extension, name, and content patterns."""
    
    def __init__(self):
        self.compiled_patterns = {}
        for tag, rules in CLASSIFICATION_PATTERNS.items():
            self.compiled_patterns[tag] = {
                "extensions": set(rules.get("extensions", [])),
                "filename_patterns": rules.get("filename_patterns", []),
                "content_patterns": [re.compile(p, re.IGNORECASE) for p in rules.get("content_patterns", [])],
            }
    
    def classify(self, path: Path, content: Optional[str] = None) -> Tuple[List[str], float]:
        """
        Classify a file and return (tags, confidence).
        """
        tags = []
        scores = defaultdict(float)
        
        ext = path.suffix.lower()
        name = path.name.lower()
        
        for tag, rules in self.compiled_patterns.items():
            # Extension match
            if ext in rules["extensions"]:
                scores[tag] += 1.0
            
            # Filename pattern match
            for pattern in rules["filename_patterns"]:
                if fnmatch.fnmatch(name, pattern.lower()):
                    scores[tag] += 2.0
                    break
            
            # Content pattern match
            if content:
                for regex in rules["content_patterns"]:
                    if regex.search(content):
                        scores[tag] += 1.5
                        break
        
        # Sort by score and take top matches
        sorted_tags = sorted(scores.items(), key=lambda x: -x[1])
        tags = [t for t, s in sorted_tags if s >= 1.0][:3]  # Top 3 tags
        
        if not tags:
            tags = ["unknown"]
        
        confidence = min(max(scores.values()) / 4.5, 1.0) if scores else 0.0
        return tags, confidence


# ============================================================================
# EXTRACTORS
# ============================================================================

class CodeExtractor:
    """Extracts code signatures, snippets, and metadata."""
    
    # Patterns for extraction
    PYTHON_FUNC = re.compile(r'^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->.*?)?:', re.MULTILINE)
    PYTHON_CLASS = re.compile(r'^(\s*)class\s+(\w+)(?:\([^)]*\))?:', re.MULTILINE)
    PYTHON_IMPORT = re.compile(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', re.MULTILINE)
    
    JS_FUNC = re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)', re.MULTILINE)
    
    API_ROUTE = re.compile(r'@(?:app|router)\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    SWAGGER_PATH = re.compile(r'[\'"]?(paths|openapi|swagger)[\'"]?\s*:', re.IGNORECASE)
    
    def extract_python(self, content: str, max_snippets: int = 5) -> Dict:
        """Extract Python code metadata."""
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "api_routes": [],
            "snippets": [],
        }
        
        # Functions
        for match in self.PYTHON_FUNC.finditer(content):
            result["functions"].append(match.group(3))
        
        # Classes
        for match in self.PYTHON_CLASS.finditer(content):
            result["classes"].append(match.group(2))
        
        # Imports
        for match in self.PYTHON_IMPORT.finditer(content):
            module = match.group(1) or match.group(2).split(',')[0].strip()
            if module:
                result["imports"].append(module.split('.')[0])
        result["imports"] = list(set(result["imports"]))[:20]
        
        # API routes
        for match in self.API_ROUTE.finditer(content):
            result["api_routes"].append({
                "method": match.group(1).upper(),
                "path": match.group(2)
            })
        
        # First N function snippets
        lines = content.split('\n')
        for match in list(self.PYTHON_FUNC.finditer(content))[:max_snippets]:
            start_line = content[:match.start()].count('\n')
            snippet_lines = []
            indent = len(match.group(1))
            for i, line in enumerate(lines[start_line:start_line + 8]):
                if i > 0 and line and not line.startswith(' ' * (indent + 1)) and line.strip():
                    break
                snippet_lines.append(line)
            result["snippets"].append({
                "line": start_line + 1,
                "code": '\n'.join(snippet_lines)
            })
        
        return result
    
    def extract_javascript(self, content: str) -> Dict:
        """Extract JavaScript/TypeScript metadata."""
        result = {
            "functions": [],
            "imports": [],
            "api_routes": [],
        }
        
        # Functions
        for match in self.JS_FUNC.finditer(content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                result["functions"].append(func_name)
        
        # Imports
        import_re = re.compile(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
        for match in import_re.finditer(content):
            result["imports"].append(match.group(1).split('/')[0])
        result["imports"] = list(set(result["imports"]))[:20]
        
        return result
    
    def has_openapi(self, content: str) -> bool:
        """Check if content contains OpenAPI/Swagger spec."""
        return bool(self.SWAGGER_PATH.search(content))


# ============================================================================
# SECRETS DETECTOR
# ============================================================================

class SecretsDetector:
    """Detects potential secrets in files (reports line numbers only, never content!)."""
    
    PATTERNS = [
        (r'AWS_ACCESS_KEY_ID\s*[=:]\s*[\'"]?([A-Z0-9]{20})', "aws_key"),
        (r'AWS_SECRET_ACCESS_KEY\s*[=:]\s*[\'"]?([A-Za-z0-9+/]{40})', "aws_secret"),
        (r'(?:api_key|apikey|api-key)\s*[=:]\s*[\'"]?([A-Za-z0-9_-]{20,})', "api_key"),
        (r'(?:secret|password|passwd|pwd)\s*[=:]\s*[\'"]?([^\'"\\n]{8,})', "password"),
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', "private_key"),
        (r'ghp_[A-Za-z0-9]{36}', "github_pat"),
        (r'sk-[A-Za-z0-9]{48}', "openai_key"),
        (r'Bearer\s+[A-Za-z0-9_-]{20,}', "bearer_token"),
        (r'(?:mysql|postgres|mongodb)://[^:]+:[^@]+@', "db_connection"),
    ]
    
    def __init__(self):
        self.compiled = [(re.compile(p, re.IGNORECASE), name) for p, name in self.PATTERNS]
    
    def detect(self, content: str) -> Tuple[bool, List[int], List[str]]:
        """
        Detect secrets in content.
        Returns: (found, line_numbers, types)
        NOTE: Never returns actual secret values!
        """
        found = False
        line_numbers = []
        types = set()
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for regex, secret_type in self.compiled:
                if regex.search(line):
                    found = True
                    line_numbers.append(i)
                    types.add(secret_type)
                    break
        
        return found, list(set(line_numbers)), list(types)


# ============================================================================
# MAIN SCANNER
# ============================================================================

class EnhancedScanner:
    """
    Full-featured read-only scanner.
    Produces JSONL shards and comprehensive manifest.
    """
    
    def __init__(self, root_path: str, output_dir: str = "/tmp/azirem_manifest"):
        self.root_path = Path(root_path).resolve()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.classifier = FileClassifier()
        self.extractor = CodeExtractor()
        self.secrets_detector = SecretsDetector()
        
        self.stats = {
            "total_files": 0,
            "total_size": 0,
            "by_tag": defaultdict(int),
            "by_extension": defaultdict(int),
            "secrets_found": 0,
            "apis_found": 0,
            "errors": 0,
        }
        
        self.shards: List[ManifestShard] = []
        self.current_shard: List[FileEntry] = []
        self.shard_size = 1000  # Files per shard
        self.shard_count = 0
    
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        for part in path.parts:
            if part in SKIP_DIRS or part.startswith('.'):
                return True
            for pattern in SKIP_DIRS:
                if '*' in pattern and fnmatch.fnmatch(part, pattern):
                    return True
        return False
    
    def compute_hash(self, content: bytes) -> str:
        """Compute SHA256 hash (first 4KB only for speed)."""
        return hashlib.sha256(content[:4096]).hexdigest()[:16]
    
    def scan_file(self, path: Path) -> Optional[FileEntry]:
        """Scan a single file."""
        try:
            stat = path.stat()
            
            entry = FileEntry(
                path=str(path),
                size=stat.st_size,
                mtime=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                tags=[],
                extension=path.suffix.lower(),
                filename=path.name,
            )
            
            # Read content for analysis (if small enough and text-like)
            content = None
            if stat.st_size < MAX_CONTENT_SIZE and path.suffix.lower() in {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.rb',
                '.java', '.yaml', '.yml', '.json', '.md', '.txt', '.sh',
                '.env', '.cfg', '.ini', '.toml', '.sql', '.html', '.css',
                '.vue', '.svelte', '.php', '.c', '.cpp', '.h', '.hpp'
            }:
                try:
                    content_bytes = path.read_bytes()
                    content = content_bytes.decode('utf-8', errors='ignore')
                    entry.content_hash = self.compute_hash(content_bytes)
                except:
                    pass
            
            # Classify
            tags, confidence = self.classifier.classify(path, content)
            entry.tags = tags
            
            # Extract code metadata
            if content and entry.extension == '.py':
                extracted = self.extractor.extract_python(content)
                entry.functions = extracted["functions"][:10]
                entry.classes = extracted["classes"][:10]
                entry.imports = extracted["imports"]
                entry.apis = extracted["api_routes"]
                entry.snippets = extracted["snippets"][:3]
                
                if entry.apis:
                    self.stats["apis_found"] += len(entry.apis)
            
            elif content and entry.extension in {'.js', '.ts', '.jsx', '.tsx'}:
                extracted = self.extractor.extract_javascript(content)
                entry.functions = extracted["functions"][:10]
                entry.imports = extracted["imports"]
            
            # Detect secrets (NEVER store actual secrets!)
            if content and ("secret-suspect" in tags or entry.extension in {'.env', '.pem', '.key'}):
                found, lines, types = self.secrets_detector.detect(content)
                if found:
                    entry.secrets_found = True
                    entry.secret_lines = lines[:10]  # Only line numbers!
                    self.stats["secrets_found"] += 1
            
            # Update stats
            self.stats["total_files"] += 1
            self.stats["total_size"] += stat.st_size
            for tag in tags:
                self.stats["by_tag"][tag] += 1
            self.stats["by_extension"][entry.extension] += 1
            
            return entry
            
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def flush_shard(self):
        """Write current shard to disk."""
        if not self.current_shard:
            return
        
        shard = ManifestShard(
            shard_id=f"shard_{self.shard_count:04d}",
            created_at=datetime.now().isoformat(),
            files=self.current_shard,
            summary={
                "file_count": len(self.current_shard),
                "total_size": sum(f.size for f in self.current_shard),
            }
        )
        
        # Write JSONL
        shard_path = self.output_dir / f"shard_{self.shard_count:04d}.jsonl"
        with open(shard_path, 'w') as f:
            for entry in self.current_shard:
                f.write(json.dumps(asdict(entry)) + '\n')
        
        self.shards.append(shard)
        self.current_shard = []
        self.shard_count += 1
    
    def scan(self, max_files: Optional[int] = None) -> Dict:
        """
        Perform full scan.
        Returns manifest summary.
        """
        print(f"🔍 Enhanced Scanner: {self.root_path}")
        print(f"   Output: {self.output_dir}")
        if max_files:
            print(f"   Limit: {max_files} files")
        print()
        
        file_count = 0
        
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            
            for filename in files:
                if max_files and file_count >= max_files:
                    break
                
                file_path = root_path / filename
                if self.should_skip(file_path):
                    continue
                
                entry = self.scan_file(file_path)
                if entry:
                    self.current_shard.append(entry)
                    file_count += 1
                    
                    if len(self.current_shard) >= self.shard_size:
                        self.flush_shard()
                    
                    if file_count % 1000 == 0:
                        print(f"   Scanned: {file_count} files...")
            
            if max_files and file_count >= max_files:
                break
        
        # Flush remaining
        self.flush_shard()
        
        # Build final manifest
        manifest = self.build_manifest()
        
        print(f"\n✅ Scan complete!")
        print(f"   Total: {self.stats['total_files']} files")
        print(f"   Shards: {self.shard_count}")
        print(f"   Secrets flagged: {self.stats['secrets_found']}")
        print(f"   APIs found: {self.stats['apis_found']}")
        
        return manifest
    
    def build_manifest(self) -> Dict:
        """Build the final manifest summary."""
        manifest = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "scanner": {
                "name": "azirem_enhanced_scanner",
                "version": "1.0.0",
            },
            "summary": {
                "total_files": self.stats["total_files"],
                "total_size_bytes": self.stats["total_size"],
                "shard_count": self.shard_count,
                "secrets_flagged": self.stats["secrets_found"],
                "apis_found": self.stats["apis_found"],
                "errors": self.stats["errors"],
            },
            "by_tag": dict(sorted(self.stats["by_tag"].items(), key=lambda x: -x[1])),
            "by_extension": dict(sorted(self.stats["by_extension"].items(), key=lambda x: -x[1])[:20]),
            "shards": [s.shard_id for s in self.shards],
        }
        
        # Write manifest
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Write YAML version
        yaml_path = self.output_dir / "manifest.yml"
        with open(yaml_path, 'w') as f:
            self._write_yaml(f, manifest)
        
        print(f"\n📄 Manifest: {manifest_path}")
        print(f"📄 YAML: {yaml_path}")
        
        return manifest
    
    def _write_yaml(self, f, data, indent=0):
        """Simple YAML writer (no dependencies)."""
        prefix = "  " * indent
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    f.write(f"{prefix}{k}:\n")
                    self._write_yaml(f, v, indent + 1)
                else:
                    f.write(f"{prefix}{k}: {json.dumps(v)}\n")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    f.write(f"{prefix}-\n")
                    self._write_yaml(f, item, indent + 1)
                else:
                    f.write(f"{prefix}- {json.dumps(item)}\n")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AZIREM Enhanced Discovery CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python discovery_cli.py scan /home/user/projects
  python discovery_cli.py scan /home/user --output /tmp/my_manifest
  python discovery_cli.py quick /home/user  # First 10k files only
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Full scan")
    scan_parser.add_argument("path", help="Path to scan")
    scan_parser.add_argument("--output", "-o", default="/tmp/azirem_manifest",
                            help="Output directory for manifest")
    scan_parser.add_argument("--max-files", "-m", type=int, default=None,
                            help="Maximum files to scan")
    
    # Quick scan command
    quick_parser = subparsers.add_parser("quick", help="Quick scan (10k files)")
    quick_parser.add_argument("path", help="Path to scan")
    quick_parser.add_argument("--output", "-o", default="/tmp/azirem_manifest",
                             help="Output directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("=" * 60)
    print("🌌 AZIREM ENHANCED DISCOVERY")
    print("=" * 60)
    
    max_files = args.max_files if args.command == "scan" else 10000
    
    scanner = EnhancedScanner(args.path, args.output)
    manifest = scanner.scan(max_files)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Files scanned: {manifest['summary']['total_files']}")
    print(f"Total size: {manifest['summary']['total_size_bytes']:,} bytes")
    print(f"Secrets flagged: {manifest['summary']['secrets_flagged']}")
    print(f"APIs found: {manifest['summary']['apis_found']}")
    print(f"\nTop tags:")
    for tag, count in list(manifest['by_tag'].items())[:10]:
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
