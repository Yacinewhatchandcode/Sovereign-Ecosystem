#!/usr/bin/env python3
"""
AZIREM Core Agents
==================
The 6 core agent types for the AZIREM ecosystem.

1. Scanner Agent - Creates manifest (read-only)
2. Classifier Agent - Tags and prioritizes files
3. Extractor Agent - Extracts code snippets, signatures
4. Dependency Resolver Agent - Resolves package dependencies
5. Secrets Agent - Finds secrets, flags them (NEVER stores actual secrets)
6. Summarizer Agent - Creates embeddings and descriptions
"""

import json
import re
import os
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
from collections import defaultdict


# ============================================================================
# BASE AGENT
# ============================================================================

@dataclass
class TaskResult:
    """Result from an agent task."""
    agent_id: str
    agent_type: str
    task_id: str
    status: str  # success, error, partial
    output: Any
    errors: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent(ABC):
    """Abstract base class for all AZIREM agents."""
    
    AGENT_TYPE = "base"
    VERSION = "1.0.0"
    
    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.results: List[TaskResult] = []
    
    @abstractmethod
    def process(self, task: Dict) -> TaskResult:
        """Process a single task."""
        pass
    
    def process_batch(self, tasks: List[Dict]) -> List[TaskResult]:
        """Process a batch of tasks."""
        results = []
        for task in tasks:
            result = self.process(task)
            results.append(result)
            self.results.append(result)
        return results
    
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.AGENT_TYPE,
            "version": self.VERSION,
            "results_count": len(self.results),
            "last_run": self.results[-1].timestamp if self.results else None,
        }


# ============================================================================
# 1. SCANNER AGENT
# ============================================================================

class ScannerAgent(BaseAgent):
    """
    Agent 1: Scanner (Discovery)
    Creates the manifest; read-only operations only.
    Supports bash-native mode for precise, high-performance scanning.
    """
    
    AGENT_TYPE = "scanner"
    VERSION = "2.0.0"  # Upgraded with bash-native support
    
    SKIP_PATTERNS = {
        "__pycache__", ".git", "node_modules", ".venv", "venv",
        ".pytest_cache", ".mypy_cache", "dist", "build",
    }
    
    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.max_files = config.get("max_files", 100000) if config else 100000
        self.use_bash_native = config.get("use_bash_native", False) if config else False
    
    def should_skip(self, path: Path) -> bool:
        for part in path.parts:
            if part in self.SKIP_PATTERNS or part.startswith('.'):
                return True
        return False
    
    def _bash_scan(self, scan_path: Path, max_files: int, extensions: Optional[List[str]] = None) -> List[Dict]:
        """
        Bash-native scanning using find command.
        More precise and performant than Python os.walk.
        """
        import subprocess
        
        # Build find command with exclusions
        exclude_args = []
        for pattern in self.SKIP_PATTERNS:
            exclude_args.extend(["-path", f"*/{pattern}/*", "-prune", "-o"])
        
        # Build extension filter
        if extensions:
            ext_args = []
            for i, ext in enumerate(extensions):
                if i > 0:
                    ext_args.append("-o")
                ext_args.extend(["-name", f"*{ext}"])
            find_cmd = ["find", str(scan_path)] + exclude_args + ["-type", "f", "("] + ext_args + [")", "-print"]
        else:
            find_cmd = ["find", str(scan_path)] + exclude_args + ["-type", "f", "-print"]
        
        try:
            result = subprocess.run(
                find_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            files = []
            for line in result.stdout.strip().split('\n')[:max_files]:
                if not line:
                    continue
                file_path = Path(line)
                try:
                    stat = file_path.stat()
                    files.append({
                        "path": str(file_path),
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": file_path.suffix.lower(),
                        "scan_mode": "bash_native"
                    })
                except:
                    pass
            
            return files
        except Exception as e:
            print(f"⚠️ Bash scan failed, falling back to Python: {e}")
            return []
    
    def process(self, task: Dict) -> TaskResult:
        """
        Scan a directory and produce file list.
        Task: {"path": "/path/to/scan", "max_files": 10000, "use_bash": true}
        """
        start = datetime.now()
        scan_path = Path(task.get("path", "."))
        max_files = task.get("max_files", self.max_files)
        use_bash = task.get("use_bash", self.use_bash_native)
        extensions = task.get("extensions", None)
        
        files = []
        errors = []
        scan_mode = "python"
        
        # Try bash-native first if enabled
        if use_bash:
            files = self._bash_scan(scan_path, max_files, extensions)
            if files:
                scan_mode = "bash_native"
        
        # Fallback to Python if bash failed or not enabled
        if not files:
            try:
                for root, dirs, filenames in os.walk(scan_path):
                    dirs[:] = [d for d in dirs if d not in self.SKIP_PATTERNS]
                    
                    for filename in filenames:
                        if len(files) >= max_files:
                            break
                        
                        file_path = Path(root) / filename
                        if self.should_skip(file_path):
                            continue
                        
                        # Filter by extension if specified
                        if extensions and file_path.suffix.lower() not in extensions:
                            continue
                        
                        try:
                            stat = file_path.stat()
                            files.append({
                                "path": str(file_path),
                                "size": stat.st_size,
                                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "extension": file_path.suffix.lower(),
                                "scan_mode": "python"
                            })
                        except Exception as e:
                            errors.append(str(e))
                    
                    if len(files) >= max_files:
                        break
            
            except Exception as e:
                errors.append(f"Scan failed: {e}")
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "scan"),
            status="success" if not errors or len(files) > 0 else "error",
            output={"files": files, "count": len(files), "scan_mode": scan_mode},
            errors=errors[:10],
            execution_time_ms=execution_time,
        )


# ============================================================================
# 2. CLASSIFIER AGENT
# ============================================================================

class ClassifierAgent(BaseAgent):
    """
    Agent 2: Classifier
    Tags and prioritizes files based on patterns.
    """
    
    AGENT_TYPE = "classifier"
    
    # Classification rules
    RULES = {
        "agent": {"extensions": [".py"], "patterns": ["*agent*"]},
        "script": {"extensions": [".py", ".sh", ".bash"], "patterns": ["run*", "demo*", "main*"]},
        "config": {"extensions": [".yaml", ".yml", ".json", ".toml", ".env", ".ini"]},
        "api": {"extensions": [".py", ".js", ".ts"], "patterns": ["*api*", "*route*"]},
        "frontend": {"extensions": [".html", ".css", ".jsx", ".tsx", ".vue"]},
        "backend": {"extensions": [".py", ".go", ".java", ".rs"], "patterns": ["server*", "app*"]},
        "docs": {"extensions": [".md", ".rst", ".txt"]},
        "test": {"extensions": [".py", ".js", ".ts"], "patterns": ["test_*", "*_test*"]},
        "secret-suspect": {"extensions": [".pem", ".key", ".env"], "patterns": ["*secret*", "*cred*"]},
    }
    
    def classify_file(self, file_info: Dict) -> List[str]:
        """Classify a single file."""
        tags = []
        ext = file_info.get("extension", "").lower()
        name = Path(file_info.get("path", "")).name.lower()
        
        for tag, rules in self.RULES.items():
            if ext in rules.get("extensions", []):
                tags.append(tag)
            for pattern in rules.get("patterns", []):
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    if tag not in tags:
                        tags.append(tag)
        
        return tags if tags else ["unknown"]
    
    def process(self, task: Dict) -> TaskResult:
        """
        Classify a batch of files.
        Task: {"files": [{"path": ..., "extension": ...}, ...]}
        """
        start = datetime.now()
        files = task.get("files", [])
        
        classified = []
        tag_counts = defaultdict(int)
        
        for file_info in files:
            tags = self.classify_file(file_info)
            classified.append({
                **file_info,
                "tags": tags,
            })
            for tag in tags:
                tag_counts[tag] += 1
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "classify"),
            status="success",
            output={
                "files": classified,
                "tag_counts": dict(tag_counts),
            },
            execution_time_ms=execution_time,
        )


# ============================================================================
# 3. EXTRACTOR AGENT
# ============================================================================

class ExtractorAgent(BaseAgent):
    """
    Agent 3: Extractor
    Extracts code snippets, function/class signatures, README text.
    Supports bash-native precision extraction with grep and sed.
    """
    
    AGENT_TYPE = "extractor"
    VERSION = "2.0.0"  # Upgraded with bash-native support
    
    # Extraction patterns
    PYTHON_FUNC = re.compile(r'^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)', re.MULTILINE)
    PYTHON_CLASS = re.compile(r'^(\s*)class\s+(\w+)', re.MULTILINE)
    PYTHON_IMPORT = re.compile(r'^(?:from\s+(\S+)\s+)?import\s+(\S+)', re.MULTILINE)
    
    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.use_bash_native = config.get("use_bash_native", False) if config else False
    
    def _bash_find_definitions(self, file_path: str) -> List[Dict]:
        """
        Use grep to find function/class definitions with line numbers.
        Returns: [{"type": "function"|"class", "name": "...", "line": N}, ...]
        """
        import subprocess
        
        definitions = []
        
        try:
            # Find functions: grep for "def " with line numbers
            func_result = subprocess.run(
                ["grep", "-n", r"^\s*\(async \)\?def ", file_path],
                capture_output=True, text=True, timeout=10
            )
            
            for line in func_result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line_num = int(parts[0])
                    # Extract function name
                    match = re.search(r'def\s+(\w+)', parts[1])
                    if match:
                        definitions.append({
                            "type": "function",
                            "name": match.group(1),
                            "line": line_num
                        })
            
            # Find classes: grep for "class " with line numbers
            class_result = subprocess.run(
                ["grep", "-n", r"^class ", file_path],
                capture_output=True, text=True, timeout=10
            )
            
            for line in class_result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line_num = int(parts[0])
                    match = re.search(r'class\s+(\w+)', parts[1])
                    if match:
                        definitions.append({
                            "type": "class",
                            "name": match.group(1),
                            "line": line_num
                        })
                        
        except Exception as e:
            print(f"⚠️ Bash grep failed: {e}")
        
        return sorted(definitions, key=lambda x: x["line"])
    
    def _bash_extract_lines(self, file_path: str, start_line: int, end_line: int) -> str:
        """
        Use sed to extract precise line range from file.
        More efficient than reading entire file into memory.
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["sed", "-n", f"{start_line},{end_line}p", file_path],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout
        except Exception as e:
            print(f"⚠️ Bash sed failed: {e}")
            return ""
    
    def extract_python(self, content: str) -> Dict:
        """Extract Python code metadata."""
        return {
            "functions": [m.group(3) for m in self.PYTHON_FUNC.finditer(content)][:20],
            "classes": [m.group(2) for m in self.PYTHON_CLASS.finditer(content)][:10],
            "imports": list(set(
                (m.group(1) or m.group(2)).split('.')[0]
                for m in self.PYTHON_IMPORT.finditer(content)
            ))[:30],
        }
    
    def extract_snippets(self, content: str, max_snippets: int = 5) -> List[Dict]:
        """Extract function snippets."""
        snippets = []
        lines = content.split('\n')
        
        for match in list(self.PYTHON_FUNC.finditer(content))[:max_snippets]:
            start_line = content[:match.start()].count('\n')
            # Get function header + first few lines
            snippet_lines = lines[start_line:start_line + 6]
            snippets.append({
                "line": start_line + 1,
                "name": match.group(3),
                "code": '\n'.join(snippet_lines),
            })
        
        return snippets
    
    def extract_snippets_bash(self, file_path: str, max_snippets: int = 5) -> List[Dict]:
        """Extract function snippets using bash for precision."""
        definitions = self._bash_find_definitions(file_path)[:max_snippets]
        snippets = []
        
        for defn in definitions:
            if defn["type"] == "function":
                # Extract 6 lines starting from the definition
                code = self._bash_extract_lines(file_path, defn["line"], defn["line"] + 5)
                snippets.append({
                    "line": defn["line"],
                    "name": defn["name"],
                    "code": code.rstrip(),
                    "extraction_mode": "bash_native"
                })
        
        return snippets
    
    def process(self, task: Dict) -> TaskResult:
        """
        Extract metadata from files.
        Task: {"files": [{...}], "use_bash": true}
        """
        start = datetime.now()
        files = task.get("files", [])
        max_snippets = task.get("max_snippets", 3)
        use_bash = task.get("use_bash", self.use_bash_native)
        
        extracted = []
        errors = []
        
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content")
            ext = file_info.get("extension", "").lower()
            extraction = {"path": file_path}
            
            # Try bash-native extraction for Python files
            if use_bash and ext == ".py" and Path(file_path).exists():
                definitions = self._bash_find_definitions(file_path)
                extraction["functions"] = [d["name"] for d in definitions if d["type"] == "function"][:20]
                extraction["classes"] = [d["name"] for d in definitions if d["type"] == "class"][:10]
                extraction["snippets"] = self.extract_snippets_bash(file_path, max_snippets)
                extraction["extraction_mode"] = "bash_native"
            else:
                # Fallback to Python-based extraction
                if not content:
                    try:
                        path = Path(file_path)
                        if path.exists() and path.stat().st_size < 1_000_000:
                            content = path.read_text(errors='ignore')
                    except:
                        pass
                
                if not content:
                    continue
                
                if ext == ".py":
                    extraction.update(self.extract_python(content))
                    extraction["snippets"] = self.extract_snippets(content, max_snippets)
                    extraction["extraction_mode"] = "python"
                elif ext in {".md", ".rst", ".txt"}:
                    paragraphs = content.split('\n\n')
                    extraction["summary"] = paragraphs[0][:500] if paragraphs else ""
                    extraction["extraction_mode"] = "python"
            
            extracted.append(extraction)
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "extract"),
            status="success",
            output={"extracted": extracted, "bash_native_used": use_bash},
            errors=errors,
            execution_time_ms=execution_time,
        )


# ============================================================================
# 4. DEPENDENCY RESOLVER AGENT
# ============================================================================

class DependencyResolverAgent(BaseAgent):
    """
    Agent 4: Dependency Resolver
    Reads requirements.txt, package.json, go.mod, etc.
    """
    
    AGENT_TYPE = "dependency_resolver"
    
    DEP_FILES = {
        "requirements.txt": "python",
        "Pipfile": "python",
        "pyproject.toml": "python",
        "package.json": "node",
        "package-lock.json": "node",
        "yarn.lock": "node",
        "go.mod": "go",
        "Cargo.toml": "rust",
        "pom.xml": "java",
        "build.gradle": "java",
        "Gemfile": "ruby",
        "composer.json": "php",
    }
    
    def parse_requirements_txt(self, content: str) -> List[Dict]:
        """Parse Python requirements.txt."""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse: package==version or package>=version
                match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!]+)?(.+)?$', line)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version": match.group(3) or "*",
                        "constraint": match.group(2) or "==",
                    })
        return deps
    
    def parse_package_json(self, content: str) -> Dict:
        """Parse Node package.json."""
        try:
            pkg = json.loads(content)
            return {
                "name": pkg.get("name"),
                "version": pkg.get("version"),
                "dependencies": list(pkg.get("dependencies", {}).keys()),
                "devDependencies": list(pkg.get("devDependencies", {}).keys()),
            }
        except:
            return {}
    
    def process(self, task: Dict) -> TaskResult:
        """
        Resolve dependencies from discovered files.
        Task: {"files": [{"path": ..., "content": ...}, ...]}
        """
        start = datetime.now()
        files = task.get("files", [])
        
        projects = []
        errors = []
        
        for file_info in files:
            path = Path(file_info.get("path", ""))
            filename = path.name
            
            if filename not in self.DEP_FILES:
                continue
            
            content = file_info.get("content")
            if not content:
                try:
                    if path.exists():
                        content = path.read_text(errors='ignore')
                except:
                    continue
            
            if not content:
                continue
            
            project = {
                "path": str(path.parent),
                "type": self.DEP_FILES[filename],
                "file": filename,
            }
            
            if filename == "requirements.txt":
                project["dependencies"] = self.parse_requirements_txt(content)
            elif filename == "package.json":
                project.update(self.parse_package_json(content))
            else:
                project["raw_deps"] = True  # Mark as needing further parsing
            
            projects.append(project)
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "deps"),
            status="success",
            output={"projects": projects, "count": len(projects)},
            errors=errors,
            execution_time_ms=execution_time,
        )


# ============================================================================
# 5. SECRETS AGENT
# ============================================================================

class SecretsAgent(BaseAgent):
    """
    Agent 5: Secrets & Keys Finder
    Finds probable secrets using regex.
    CRITICAL: NEVER stores or transmits actual secret values!
    Only records: path, line numbers, type, severity.
    """
    
    AGENT_TYPE = "secrets"
    
    # Secret patterns with severity
    PATTERNS = [
        (r'AWS_ACCESS_KEY_ID\s*[=:]\s*[A-Z0-9]{20}', "aws_key", "HIGH"),
        (r'AWS_SECRET_ACCESS_KEY\s*[=:]', "aws_secret", "CRITICAL"),
        (r'(?:api[_-]?key|apikey)\s*[=:]\s*[\'"]?[A-Za-z0-9]{16,}', "api_key", "HIGH"),
        (r'(?:password|passwd|pwd)\s*[=:]\s*[\'"][^\'\"]+[\'"]', "password", "HIGH"),
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', "private_key", "CRITICAL"),
        (r'ghp_[A-Za-z0-9]{36}', "github_pat", "CRITICAL"),
        (r'sk-[A-Za-z0-9]{40,}', "openai_key", "CRITICAL"),
        (r'(?:mysql|postgres|mongodb)://[^:]+:[^@]+@', "db_connection", "CRITICAL"),
        (r'Bearer\s+[A-Za-z0-9_.-]{20,}', "bearer_token", "HIGH"),
        (r'PRIVATE[_-]?KEY\s*[=:]', "generic_private_key", "HIGH"),
    ]
    
    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.compiled = [
            (re.compile(p, re.IGNORECASE), name, severity)
            for p, name, severity in self.PATTERNS
        ]
    
    def scan_content(self, content: str) -> List[Dict]:
        """
        Scan content for secrets.
        Returns ONLY metadata, NEVER actual secret values!
        """
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for regex, secret_type, severity in self.compiled:
                if regex.search(line):
                    findings.append({
                        "line": i,
                        "type": secret_type,
                        "severity": severity,
                        # NEVER include actual content!
                        "context_hash": hash(line[:20]) % 10000,  # Just a reference ID
                    })
                    break  # One finding per line
        
        return findings
    
    def process(self, task: Dict) -> TaskResult:
        """
        Scan files for secrets.
        Task: {"files": [{"path": ..., "content": ...}, ...]}
        
        CRITICAL: Output contains NO actual secret values!
        """
        start = datetime.now()
        files = task.get("files", [])
        
        results = []
        critical_count = 0
        high_count = 0
        
        for file_info in files:
            content = file_info.get("content")
            if not content:
                try:
                    path = Path(file_info.get("path", ""))
                    if path.exists() and path.stat().st_size < 500_000:
                        content = path.read_text(errors='ignore')
                except:
                    continue
            
            if not content:
                continue
            
            findings = self.scan_content(content)
            
            if findings:
                results.append({
                    "path": file_info.get("path"),
                    "findings": findings,
                    "count": len(findings),
                })
                
                for f in findings:
                    if f["severity"] == "CRITICAL":
                        critical_count += 1
                    elif f["severity"] == "HIGH":
                        high_count += 1
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "secrets"),
            status="success",
            output={
                "files_with_secrets": len(results),
                "critical_count": critical_count,
                "high_count": high_count,
                "findings": results,
                "NOTE": "ACTUAL SECRET VALUES ARE NEVER STORED - ONLY METADATA",
            },
            execution_time_ms=execution_time,
        )


# ============================================================================
# 6. SUMMARIZER AGENT
# ============================================================================

class SummarizerAgent(BaseAgent):
    """
    Agent 6: Summarizer / Indexer
    Creates natural-language descriptions and prepares for embedding.
    UPGRADED: Can optionally use DeepSeek LLM for richer summaries.
    """
    
    AGENT_TYPE = "summarizer"
    VERSION = "2.0.0"  # Upgraded with LLM support
    
    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.use_llm = config.get("use_llm", False) if config else False
        self.brain = None
        
        if self.use_llm:
            self._init_brain()
            
    def _init_brain(self):
        """Initialize AZIREM Brain for LLM summaries."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from azirem_brain import AziremBrain
            import asyncio
            
            self.brain = AziremBrain()
            # Check if Ollama is available
            loop = asyncio.new_event_loop()
            available = loop.run_until_complete(self.brain.check_ollama_available())
            loop.close()
            
            if not available:
                self.brain = None
                print("⚠️ LLM not available, using template summaries")
        except Exception as e:
            print(f"⚠️ Brain init failed: {e}")
            self.brain = None
    
    def summarize_file(self, file_info: Dict, extracted: Dict) -> str:
        """Generate a natural-language summary of a file."""
        path = Path(file_info.get("path", ""))
        tags = file_info.get("tags", [])
        
        parts = [f"**{path.name}**"]
        
        if tags:
            parts.append(f"Type: {', '.join(tags)}")
        
        if extracted.get("classes"):
            parts.append(f"Classes: {', '.join(extracted['classes'][:5])}")
        
        if extracted.get("functions"):
            parts.append(f"Functions: {', '.join(extracted['functions'][:5])}")
        
        if extracted.get("imports"):
            parts.append(f"Key imports: {', '.join(extracted['imports'][:5])}")
        
        if extracted.get("summary"):
            parts.append(f"Content: {extracted['summary'][:200]}...")
        
        return " | ".join(parts)
    
    def summarize_with_llm(self, file_info: Dict, extracted: Dict) -> str:
        """Generate LLM-enhanced summary using DeepSeek."""
        if not self.brain:
            return self.summarize_file(file_info, extracted)
            
        path = Path(file_info.get("path", ""))
        tags = file_info.get("tags", [])
        
        prompt = f"""Summarize this code file in 2-3 sentences:
File: {path.name}
Tags: {', '.join(tags) if tags else 'none'}
Classes: {', '.join(extracted.get('classes', [])[:5])}
Functions: {', '.join(extracted.get('functions', [])[:10])}
Imports: {', '.join(extracted.get('imports', [])[:5])}

Be concise and focus on the file's purpose."""

        try:
            import asyncio
            loop = asyncio.new_event_loop()
            response = loop.run_until_complete(self.brain.think(prompt))
            loop.close()
            return response[:500]  # Limit length
        except:
            return self.summarize_file(file_info, extracted)
    
    def process(self, task: Dict) -> TaskResult:
        """
        Generate summaries for files.
        Task: {"files": [{"path": ..., "tags": ..., "extracted": {...}}, ...]}
        """
        start = datetime.now()
        files = task.get("files", [])
        use_llm = task.get("use_llm", self.use_llm)
        
        summaries = []
        
        for file_info in files:
            extracted = file_info.get("extracted", {})
            
            # Use LLM if enabled and available
            if use_llm and self.brain:
                summary = self.summarize_with_llm(file_info, extracted)
            else:
                summary = self.summarize_file(file_info, extracted)
            
            summaries.append({
                "path": file_info.get("path"),
                "summary": summary,
                "llm_enhanced": use_llm and self.brain is not None,
                "embedding_ready": True,
            })
        
        execution_time = int((datetime.now() - start).total_seconds() * 1000)
        
        return TaskResult(
            agent_id=self.agent_id,
            agent_type=self.AGENT_TYPE,
            task_id=task.get("task_id", "summarize"),
            status="success",
            output={"summaries": summaries, "count": len(summaries), "llm_used": use_llm and self.brain is not None},
            execution_time_ms=execution_time,
        )


# ============================================================================
# AGENT FACTORY (EXTENDED)
# ============================================================================

# Import new agents (optional - graceful fallback if not available)
try:
    from .memory_agent import MemoryAgent
except ImportError:
    MemoryAgent = None
    
try:
    from .mcp_tool_agent import MCPToolAgent
except ImportError:
    MCPToolAgent = None
    
try:
    from .embedding_agent import EmbeddingAgent
except ImportError:
    EmbeddingAgent = None
    
try:
    from .docgen_agent import DocGenAgent
except ImportError:
    DocGenAgent = None


class AgentFactory:
    """Factory for creating agent instances. Extended with Phase 6-8 agents."""
    
    # Core agents (always available)
    AGENT_TYPES = {
        "scanner": ScannerAgent,
        "classifier": ClassifierAgent,
        "extractor": ExtractorAgent,
        "dependency_resolver": DependencyResolverAgent,
        "secrets": SecretsAgent,
        "summarizer": SummarizerAgent,
    }
    
    # Extended agents (Phase 6-8, optional)
    EXTENDED_AGENTS = {
        "memory": MemoryAgent,
        "mcp_tools": MCPToolAgent,
        "embedding": EmbeddingAgent,
        "docgen": DocGenAgent,
    }
    
    @classmethod
    def create(cls, agent_type: str, agent_id: str, config: Optional[Dict] = None) -> BaseAgent:
        """Create an agent instance."""
        # Check core agents first
        if agent_type in cls.AGENT_TYPES:
            return cls.AGENT_TYPES[agent_type](agent_id, config)
            
        # Check extended agents
        if agent_type in cls.EXTENDED_AGENTS:
            agent_cls = cls.EXTENDED_AGENTS[agent_type]
            if agent_cls is None:
                raise ValueError(f"Agent '{agent_type}' module not installed")
            # Extended agents don't need agent_id in constructor
            return agent_cls()
            
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    @classmethod
    def list_types(cls) -> List[str]:
        """List available agent types."""
        types = list(cls.AGENT_TYPES.keys())
        for name, cls_ref in cls.EXTENDED_AGENTS.items():
            if cls_ref is not None:
                types.append(name)
        return types
    
    @classmethod
    def list_extended(cls) -> Dict[str, bool]:
        """List extended agents and their availability."""
        return {name: cls_ref is not None for name, cls_ref in cls.EXTENDED_AGENTS.items()}


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AZIREM CORE AGENTS")
    print("=" * 60)
    print(f"Available agent types: {', '.join(AgentFactory.list_types())}")
    print()
    
    # Demo: Create and test each agent
    demo_files = [
        {"path": "/demo/app.py", "extension": ".py", 
         "content": "from flask import Flask\napp = Flask(__name__)\n@app.get('/api/users')\ndef get_users():\n    pass"},
        {"path": "/demo/config.yaml", "extension": ".yaml"},
        {"path": "/demo/.env", "extension": ".env",
         "content": "API_KEY=sk-test123456789012345678901234567890"},
    ]
    
    for agent_type in AgentFactory.list_types():
        print(f"\n{'─' * 40}")
        print(f"Testing: {agent_type}")
        agent = AgentFactory.create(agent_type, f"test_{agent_type}")
        
        if agent_type == "scanner":
            result = agent.process({"path": ".", "max_files": 10})
        else:
            result = agent.process({"files": demo_files})
        
        print(f"  Status: {result.status}")
        print(f"  Time: {result.execution_time_ms}ms")
        if result.output:
            # Print summary of output
            if isinstance(result.output, dict):
                for k, v in result.output.items():
                    if isinstance(v, list):
                        print(f"  {k}: {len(v)} items")
                    elif isinstance(v, int):
                        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("✅ All agents tested!")
