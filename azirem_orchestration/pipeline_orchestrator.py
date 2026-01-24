#!/usr/bin/env python3
"""
AZIREM Pipeline Orchestrator
============================
Master orchestrator that schedules the agent pipeline:
scan → classify → extract → deps → secrets → summarize → merge

Supports both synchronous and queue-based (Redis) execution.
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import time
from collections import deque
import threading

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azirem_agents.core_agents import (
    AgentFactory, BaseAgent, TaskResult,
    ScannerAgent, ClassifierAgent, ExtractorAgent,
    DependencyResolverAgent, SecretsAgent, SummarizerAgent
)


# ============================================================================
# PIPELINE STAGES
# ============================================================================

class PipelineStage(Enum):
    """Pipeline execution stages."""
    INIT = "init"
    SCAN = "scan"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    DEPS = "deps"
    SECRETS = "secrets"
    SUMMARIZE = "summarize"
    MERGE = "merge"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class PipelineTask:
    """A task in the pipeline queue."""
    task_id: str
    stage: PipelineStage
    payload: Dict
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "pending"
    result: Optional[TaskResult] = None


@dataclass
class PipelineRun:
    """A complete pipeline run."""
    run_id: str
    root_path: str
    created_at: str
    stages_completed: List[str] = field(default_factory=list)
    current_stage: PipelineStage = PipelineStage.INIT
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    total_files: int = 0
    execution_time_ms: int = 0


# ============================================================================
# IN-MEMORY QUEUE (Simple, no Redis dependency)
# ============================================================================

class SimpleQueue:
    """Simple thread-safe in-memory queue."""
    
    def __init__(self):
        self._queue = deque()
        self._lock = threading.Lock()
    
    def push(self, item: Any, priority: int = 0):
        """Push item to queue."""
        with self._lock:
            self._queue.append((priority, item))
            # Sort by priority (higher first)
            self._queue = deque(sorted(self._queue, key=lambda x: -x[0]))
    
    def pop(self) -> Optional[Any]:
        """Pop item from queue."""
        with self._lock:
            if self._queue:
                return self._queue.popleft()[1]
            return None
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        with self._lock:
            return len(self._queue) == 0
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


# ============================================================================
# PIPELINE ORCHESTRATOR
# ============================================================================

class PipelineOrchestrator:
    """
    Master orchestrator for the AZIREM pipeline.
    
    Pipeline flow:
    1. SCAN - Discover all files
    2. CLASSIFY - Tag files by type
    3. EXTRACT - Extract code metadata
    4. DEPS - Resolve dependencies  
    5. SECRETS - Find potential secrets
    6. SUMMARIZE - Generate descriptions
    7. MERGE - Consolidate into registry
    """
    
    def __init__(self, output_dir: str = "/tmp/azirem_pipeline"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue = SimpleQueue()
        self.agents: Dict[str, BaseAgent] = {}
        self.current_run: Optional[PipelineRun] = None
        
        # Initialize agents
        self._init_agents()
    
    def _init_agents(self):
        """Initialize all pipeline agents."""
        self.agents = {
            "scanner": AgentFactory.create("scanner", "pipeline_scanner"),
            "classifier": AgentFactory.create("classifier", "pipeline_classifier"),
            "extractor": AgentFactory.create("extractor", "pipeline_extractor"),
            "deps": AgentFactory.create("dependency_resolver", "pipeline_deps"),
            "secrets": AgentFactory.create("secrets", "pipeline_secrets"),
            "summarizer": AgentFactory.create("summarizer", "pipeline_summarizer"),
        }
        print(f"✅ Initialized {len(self.agents)} pipeline agents")
    
    def create_run(self, root_path: str) -> PipelineRun:
        """Create a new pipeline run."""
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_run = PipelineRun(
            run_id=run_id,
            root_path=root_path,
            created_at=datetime.now().isoformat(),
        )
        
        print(f"📋 Created pipeline run: {run_id}")
        return self.current_run
    
    def execute_stage(self, stage: PipelineStage, payload: Dict) -> TaskResult:
        """Execute a single pipeline stage."""
        agent_map = {
            PipelineStage.SCAN: "scanner",
            PipelineStage.CLASSIFY: "classifier",
            PipelineStage.EXTRACT: "extractor",
            PipelineStage.DEPS: "deps",
            PipelineStage.SECRETS: "secrets",
            PipelineStage.SUMMARIZE: "summarizer",
        }
        
        agent_name = agent_map.get(stage)
        if not agent_name or agent_name not in self.agents:
            raise ValueError(f"No agent for stage: {stage}")
        
        agent = self.agents[agent_name]
        return agent.process(payload)
    
    def run_full_pipeline(self, root_path: str, 
                          max_files: int = 10000,
                          progress_callback: Optional[Callable] = None) -> PipelineRun:
        """
        Execute the full pipeline synchronously.
        
        Args:
            root_path: Path to scan
            max_files: Maximum files to process
            progress_callback: Optional callback(stage, progress_pct, message)
        
        Returns:
            PipelineRun with all results
        """
        start_time = datetime.now()
        run = self.create_run(root_path)
        
        def report(stage: str, pct: int, msg: str):
            run.current_stage = PipelineStage[stage.upper()]
            if progress_callback:
                progress_callback(stage, pct, msg)
            print(f"   [{stage}] {pct}% - {msg}")
        
        try:
            # Stage 1: SCAN
            report("scan", 0, "Starting file discovery...")
            scan_result = self.execute_stage(
                PipelineStage.SCAN,
                {"path": root_path, "max_files": max_files, "task_id": "scan"}
            )
            
            if scan_result.status != "success":
                raise RuntimeError(f"Scan failed: {scan_result.errors}")
            
            files = scan_result.output.get("files", [])
            run.total_files = len(files)
            run.results["scan"] = {"count": len(files)}
            run.stages_completed.append("scan")
            report("scan", 100, f"Found {len(files)} files")
            
            # Stage 2: CLASSIFY
            report("classify", 0, "Classifying files...")
            classify_result = self.execute_stage(
                PipelineStage.CLASSIFY,
                {"files": files, "task_id": "classify"}
            )
            
            classified_files = classify_result.output.get("files", [])
            tag_counts = classify_result.output.get("tag_counts", {})
            run.results["classify"] = {"tag_counts": tag_counts}
            run.stages_completed.append("classify")
            report("classify", 100, f"Tags: {dict(list(tag_counts.items())[:5])}")
            
            # Stage 3: EXTRACT (Python files only for speed)
            report("extract", 0, "Extracting code metadata...")
            code_files = [f for f in classified_files 
                         if f.get("extension") in {".py", ".js", ".ts"}][:500]
            
            extract_result = self.execute_stage(
                PipelineStage.EXTRACT,
                {"files": code_files, "task_id": "extract"}
            )
            
            extracted = extract_result.output.get("extracted", [])
            run.results["extract"] = {"count": len(extracted)}
            run.stages_completed.append("extract")
            report("extract", 100, f"Extracted metadata from {len(extracted)} files")
            
            # Stage 4: DEPS
            report("deps", 0, "Resolving dependencies...")
            dep_files = [f for f in classified_files
                        if Path(f.get("path", "")).name in {
                            "requirements.txt", "package.json", "go.mod",
                            "Cargo.toml", "pyproject.toml", "Pipfile"
                        }]
            
            deps_result = self.execute_stage(
                PipelineStage.DEPS,
                {"files": dep_files, "task_id": "deps"}
            )
            
            projects = deps_result.output.get("projects", [])
            run.results["deps"] = {"projects": len(projects)}
            run.stages_completed.append("deps")
            report("deps", 100, f"Found {len(projects)} projects with dependencies")
            
            # Stage 5: SECRETS
            report("secrets", 0, "Scanning for secrets...")
            suspect_files = [f for f in classified_files
                            if "secret-suspect" in f.get("tags", [])
                            or f.get("extension") in {".env", ".pem", ".key"}][:100]
            
            secrets_result = self.execute_stage(
                PipelineStage.SECRETS,
                {"files": suspect_files, "task_id": "secrets"}
            )
            
            secrets_output = secrets_result.output
            run.results["secrets"] = {
                "files_flagged": secrets_output.get("files_with_secrets", 0),
                "critical": secrets_output.get("critical_count", 0),
                "high": secrets_output.get("high_count", 0),
            }
            run.stages_completed.append("secrets")
            report("secrets", 100, 
                   f"Flagged: {secrets_output.get('files_with_secrets', 0)} files "
                   f"({secrets_output.get('critical_count', 0)} critical)")
            
            # Stage 6: SUMMARIZE
            report("summarize", 0, "Generating summaries...")
            # Combine extracted data with classified files
            files_for_summary = []
            extracted_map = {e.get("path"): e for e in extracted}
            for f in classified_files[:200]:  # Limit for speed
                files_for_summary.append({
                    **f,
                    "extracted": extracted_map.get(f.get("path"), {})
                })
            
            summary_result = self.execute_stage(
                PipelineStage.SUMMARIZE,
                {"files": files_for_summary, "task_id": "summarize"}
            )
            
            summaries = summary_result.output.get("summaries", [])
            run.results["summarize"] = {"count": len(summaries)}
            run.stages_completed.append("summarize")
            report("summarize", 100, f"Generated {len(summaries)} summaries")
            
            # Stage 7: MERGE (save final registry)
            report("merge", 0, "Merging into registry...")
            registry = self._merge_results(run, classified_files, extracted, projects, summaries)
            run.results["registry"] = {"total_items": len(registry.get("files", []))}
            run.stages_completed.append("merge")
            report("merge", 100, "Registry saved!")
            
            run.current_stage = PipelineStage.COMPLETE
            
        except Exception as e:
            run.current_stage = PipelineStage.ERROR
            run.errors.append(str(e))
            print(f"❌ Pipeline error: {e}")
        
        run.execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save run metadata
        self._save_run(run)
        
        return run
    
    def _merge_results(self, run: PipelineRun, 
                       files: List[Dict],
                       extracted: List[Dict],
                       projects: List[Dict],
                       summaries: List[Dict]) -> Dict:
        """Merge all results into final registry."""
        
        # Build lookup maps
        extracted_map = {e.get("path"): e for e in extracted}
        summary_map = {s.get("path"): s for s in summaries}
        
        # Merge into registry entries
        registry_files = []
        for f in files:
            path = f.get("path")
            entry = {
                **f,
                "extracted": extracted_map.get(path, {}),
                "summary": summary_map.get(path, {}).get("summary", ""),
            }
            registry_files.append(entry)
        
        registry = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "run_id": run.run_id,
            "root_path": run.root_path,
            "summary": {
                "total_files": len(files),
                "total_projects": len(projects),
                "execution_time_ms": run.execution_time_ms,
            },
            "by_tag": run.results.get("classify", {}).get("tag_counts", {}),
            "secrets_summary": run.results.get("secrets", {}),
            "projects": projects,
            "files": registry_files[:1000],  # Limit for file size
        }
        
        # Save registry
        registry_path = self.output_dir / "registry.json"
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"📄 Registry saved: {registry_path}")
        
        return registry
    
    def _save_run(self, run: PipelineRun):
        """Save run metadata."""
        run_path = self.output_dir / f"{run.run_id}.json"
        
        run_data = {
            "run_id": run.run_id,
            "root_path": run.root_path,
            "created_at": run.created_at,
            "current_stage": run.current_stage.value,
            "stages_completed": run.stages_completed,
            "results": run.results,
            "errors": run.errors,
            "total_files": run.total_files,
            "execution_time_ms": run.execution_time_ms,
        }
        
        with open(run_path, 'w') as f:
            json.dump(run_data, f, indent=2)
        
        print(f"📄 Run saved: {run_path}")
    
    def get_status(self) -> Dict:
        """Get orchestrator status."""
        return {
            "agents": list(self.agents.keys()),
            "queue_size": self.queue.size(),
            "current_run": self.current_run.run_id if self.current_run else None,
            "output_dir": str(self.output_dir),
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AZIREM Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("path", help="Root path to scan")
    parser.add_argument("--output", "-o", default="/tmp/azirem_pipeline",
                       help="Output directory")
    parser.add_argument("--max-files", "-m", type=int, default=10000,
                       help="Maximum files to process")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌌 AZIREM PIPELINE ORCHESTRATOR")
    print("=" * 60)
    print(f"Root: {args.path}")
    print(f"Output: {args.output}")
    print(f"Max files: {args.max_files}")
    print()
    
    orchestrator = PipelineOrchestrator(args.output)
    
    run = orchestrator.run_full_pipeline(
        args.path,
        max_files=args.max_files
    )
    
    print()
    print("=" * 60)
    print("📊 PIPELINE RESULTS")
    print("=" * 60)
    print(f"Run ID: {run.run_id}")
    print(f"Status: {run.current_stage.value}")
    print(f"Files: {run.total_files}")
    print(f"Time: {run.execution_time_ms}ms")
    print(f"Stages: {' → '.join(run.stages_completed)}")
    
    if run.results.get("secrets"):
        secrets = run.results["secrets"]
        if secrets.get("critical", 0) > 0:
            print(f"⚠️  SECRETS: {secrets['files_flagged']} files flagged "
                  f"({secrets['critical']} CRITICAL)")
    
    if run.errors:
        print(f"❌ Errors: {len(run.errors)}")
        for err in run.errors[:3]:
            print(f"   - {err}")


if __name__ == "__main__":
    main()
