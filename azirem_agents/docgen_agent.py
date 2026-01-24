#!/usr/bin/env python3
"""
📚 DOCGEN AGENT - Automatic Documentation Generation
====================================================
Generates documentation from code using LLM analysis.
Creates README files, API docs, and inline comments.

Priority 4 Agent for completing Phase 8 tasks.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
from dataclasses import dataclass
import ast
import sys

# Add parent path for brain import
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class DocResult:
    """Documentation generation result."""
    file_path: str
    doc_type: str  # readme, api, inline, module
    content: str
    metadata: Dict[str, Any]
    timestamp: str


class CodeAnalyzer:
    """Analyzes Python code structure."""
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file's structure."""
        path = Path(file_path)
        
        if not path.exists() or path.suffix != '.py':
            return {"error": "Invalid Python file"}
            
        try:
            content = path.read_text()
            tree = ast.parse(content)
        except Exception as e:
            return {"error": str(e)}
            
        result = {
            "file": str(path),
            "name": path.stem,
            "docstring": ast.get_docstring(tree),
            "classes": [],
            "functions": [],
            "imports": [],
            "constants": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [],
                    "bases": [self._get_name(b) for b in node.bases]
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info["methods"].append({
                            "name": item.name,
                            "docstring": ast.get_docstring(item),
                            "args": [a.arg for a in item.args.args if a.arg != 'self']
                        })
                result["classes"].append(class_info)
                
            elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                # Top-level function (not in class)
                if hasattr(node, 'col_offset') and node.col_offset == 0:
                    result["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [a.arg for a in node.args.args]
                    })
                    
            elif isinstance(node, ast.AsyncFunctionDef):
                if hasattr(node, 'col_offset') and node.col_offset == 0:
                    result["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [a.arg for a in node.args.args],
                        "async": True
                    })
                    
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{module}.{alias.name}")
                    
        return result
        
    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)


class DocGenAgent:
    """
    DocGen Agent - automatic documentation generation.
    
    Provides:
    - README generation from code analysis
    - API documentation generation
    - Module docstrings
    - Code comment suggestions
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.analyzer = CodeAnalyzer()
        self.brain = None
        self.callback: Optional[Callable] = None
        
        if use_llm:
            self._init_brain()
            
    def _init_brain(self):
        """Initialize AZIREM Brain for LLM generation."""
        try:
            from azirem_brain import AziremBrain
            self.brain = AziremBrain()
        except Exception as e:
            print(f"⚠️ Brain not available: {e}")
            self.use_llm = False
            
    def set_callback(self, callback: Callable):
        """Set event callback."""
        self.callback = callback
        
    async def emit(self, event_type: str, data: Dict):
        """Emit event to listeners."""
        if self.callback:
            await self.callback(event_type, {
                "agent": "docgen",
                "timestamp": datetime.now().isoformat(),
                **data
            })
            
    async def generate_readme(self, directory: str) -> DocResult:
        """Generate README.md for a directory."""
        path = Path(directory)
        
        if not path.is_dir():
            return DocResult(
                file_path=str(path),
                doc_type="readme",
                content="",
                metadata={"error": "Not a directory"},
                timestamp=datetime.now().isoformat()
            )
            
        await self.emit("generating", {"type": "readme", "path": directory})
        
        # Analyze all Python files
        py_files = list(path.glob("*.py"))
        analyses = []
        
        for py_file in py_files[:10]:  # Limit to 10 files
            analysis = self.analyzer.analyze_file(str(py_file))
            if "error" not in analysis:
                analyses.append(analysis)
                
        # Generate README content
        if self.use_llm and self.brain:
            content = await self._llm_readme(path.name, analyses)
        else:
            content = self._template_readme(path.name, analyses)
            
        result = DocResult(
            file_path=str(path / "README.md"),
            doc_type="readme",
            content=content,
            metadata={"files_analyzed": len(analyses)},
            timestamp=datetime.now().isoformat()
        )
        
        await self.emit("generated", {"type": "readme", "path": result.file_path})
        
        return result
        
    async def generate_api_doc(self, file_path: str) -> DocResult:
        """Generate API documentation for a Python file."""
        await self.emit("generating", {"type": "api", "path": file_path})
        
        analysis = self.analyzer.analyze_file(file_path)
        
        if "error" in analysis:
            return DocResult(
                file_path=file_path,
                doc_type="api",
                content="",
                metadata={"error": analysis["error"]},
                timestamp=datetime.now().isoformat()
            )
            
        # Generate API content
        if self.use_llm and self.brain:
            content = await self._llm_api_doc(analysis)
        else:
            content = self._template_api_doc(analysis)
            
        result = DocResult(
            file_path=file_path.replace(".py", "_API.md"),
            doc_type="api",
            content=content,
            metadata={"classes": len(analysis["classes"]), "functions": len(analysis["functions"])},
            timestamp=datetime.now().isoformat()
        )
        
        await self.emit("generated", {"type": "api", "path": result.file_path})
        
        return result
        
    async def _llm_readme(self, name: str, analyses: List[Dict]) -> str:
        """Generate README using LLM."""
        # Build prompt
        files_info = []
        for a in analyses:
            classes = ", ".join(c["name"] for c in a.get("classes", []))
            funcs = ", ".join(f["name"] for f in a.get("functions", []))
            files_info.append(f"- {a['name']}.py: Classes: {classes or 'none'}, Functions: {funcs or 'none'}")
            
        prompt = f"""Generate a README.md for the module '{name}'.

Files in this module:
{chr(10).join(files_info)}

Create a professional README with:
1. Title and description
2. Features list
3. Installation
4. Usage examples
5. API overview

Keep it concise but informative."""

        try:
            response = await self.brain.think(prompt)
            return response
        except:
            return self._template_readme(name, analyses)
            
    async def _llm_api_doc(self, analysis: Dict) -> str:
        """Generate API doc using LLM."""
        prompt = f"""Generate API documentation for Python module '{analysis['name']}'.

Module docstring: {analysis.get('docstring', 'None')}

Classes:
{json.dumps(analysis.get('classes', []), indent=2)[:2000]}

Functions:
{json.dumps(analysis.get('functions', []), indent=2)[:1000]}

Create professional API documentation with clear descriptions and usage."""

        try:
            response = await self.brain.think(prompt)
            return response
        except:
            return self._template_api_doc(analysis)
            
    def _template_readme(self, name: str, analyses: List[Dict]) -> str:
        """Template-based README generation."""
        lines = [
            f"# {name}",
            "",
            "## Overview",
            "",
            f"This module contains {len(analyses)} Python files.",
            "",
            "## Files",
            ""
        ]
        
        for a in analyses:
            doc = a.get("docstring", "No description")[:100] if a.get("docstring") else "No description"
            lines.append(f"### {a['name']}.py")
            lines.append(f"> {doc}")
            lines.append("")
            
            if a.get("classes"):
                lines.append("**Classes:**")
                for c in a["classes"]:
                    lines.append(f"- `{c['name']}`: {c.get('docstring', 'No doc')[:50] if c.get('docstring') else 'No doc'}")
                lines.append("")
                
            if a.get("functions"):
                lines.append("**Functions:**")
                for f in a["functions"]:
                    args = ", ".join(f.get("args", []))
                    lines.append(f"- `{f['name']}({args})`")
                lines.append("")
                
        return "\n".join(lines)
        
    def _template_api_doc(self, analysis: Dict) -> str:
        """Template-based API documentation."""
        lines = [
            f"# API Reference: {analysis['name']}",
            "",
            analysis.get("docstring", "No description"),
            "",
            "---",
            ""
        ]
        
        if analysis.get("classes"):
            lines.append("## Classes")
            lines.append("")
            
            for c in analysis["classes"]:
                lines.append(f"### `{c['name']}`")
                lines.append("")
                if c.get("bases"):
                    lines.append(f"Inherits from: `{', '.join(c['bases'])}`")
                    lines.append("")
                if c.get("docstring"):
                    lines.append(c["docstring"])
                    lines.append("")
                    
                if c.get("methods"):
                    lines.append("**Methods:**")
                    lines.append("")
                    for m in c["methods"]:
                        args = ", ".join(m.get("args", []))
                        lines.append(f"#### `{m['name']}({args})`")
                        if m.get("docstring"):
                            lines.append(f"> {m['docstring'][:100]}")
                        lines.append("")
                        
        if analysis.get("functions"):
            lines.append("## Functions")
            lines.append("")
            
            for f in analysis["functions"]:
                args = ", ".join(f.get("args", []))
                async_prefix = "async " if f.get("async") else ""
                lines.append(f"### `{async_prefix}{f['name']}({args})`")
                if f.get("docstring"):
                    lines.append(f"> {f['docstring']}")
                lines.append("")
                
        return "\n".join(lines)
        
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "agent": "docgen",
            "version": "1.0.0",
            "llm_enabled": self.use_llm,
            "brain_available": self.brain is not None
        }


# CLI for testing
async def demo():
    """Demo the DocGen Agent."""
    print("📚 DocGen Agent Demo")
    print("=" * 50)
    
    agent = DocGenAgent(use_llm=False)  # Template mode for demo
    status = agent.get_status()
    
    print(f"\n📊 Status:")
    print(f"   LLM Enabled: {status['llm_enabled']}")
    print(f"   Brain Available: {status['brain_available']}")
    
    # Analyze current directory
    print("\n📝 Analyzing current module...")
    result = await agent.generate_readme(str(Path(__file__).parent))
    
    print(f"\n📄 Generated README ({len(result.content)} chars):")
    print("-" * 40)
    print(result.content[:500])
    print("...")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
