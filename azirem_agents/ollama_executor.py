#!/usr/bin/env python3
"""
AZIREM Ollama Executor
======================
Real LLM execution using Ollama for all agents.
Supports streaming, tool calls, and multi-model routing.
"""

import json
import requests
import subprocess
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import os

# Configure Opik for local Sovereign Observability
if "OPIK_URL_OVERRIDE" not in os.environ:
    os.environ["OPIK_URL_OVERRIDE"] = "http://localhost:5173/api"
if "OPIK_PROJECT_NAME" not in os.environ:
    os.environ["OPIK_PROJECT_NAME"] = "asirem-sovereign"

import opik
from opik import track


# ============================================================================
# CONFIGURATION
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"

# Model routing based on task type
MODEL_ROUTING = {
    "fast": "llama3.2:3b",
    "balanced": "llama3.1:8b",
    "powerful": "qwen2.5:14b",
    "code": "qwen2.5-coder:7b",
    "reasoning": "deepseek-r1:8b",
    "vision": "llava:13b",
}

# Agent-to-model mapping
AGENT_MODELS = {
    "scanner": "fast",
    "classifier": "fast",
    "extractor": "balanced",
    "summarizer": "balanced",
    "code_generator": "code",
    "researcher": "powerful",
    "reasoner": "reasoning",
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class OllamaResponse:
    """Response from Ollama."""
    content: str
    model: str
    tokens_generated: int
    tokens_prompt: int
    total_duration_ms: int
    success: bool
    error: Optional[str] = None


@dataclass
class AgentExecution:
    """Record of an agent execution."""
    agent_id: str
    model: str
    prompt: str
    response: str
    tokens: int
    duration_ms: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# OLLAMA CLIENT
# ============================================================================

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.available_models: List[str] = []
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m["name"] for m in data.get("models", [])]
                return self.available_models
        except:
            pass
        return []
    
    def get_best_model(self, preferred: str) -> str:
        """Get best available model from routing table."""
        if not self.available_models:
            self.list_models()
        
        # Get model from routing
        target = MODEL_ROUTING.get(preferred, preferred)
        
        # Check if exact match available
        if target in self.available_models:
            return target
        
        # Try to find partial match
        base_name = target.split(":")[0]
        for model in self.available_models:
            if base_name in model:
                return model
        
        # Fallback to first available
        return self.available_models[0] if self.available_models else "llama3.1:8b"
    
    def generate(self, prompt: str, model: str = "llama3.1:8b",
                 system: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 2048) -> OllamaResponse:
        """Generate a response from Ollama."""
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return OllamaResponse(
                    content=data.get("message", {}).get("content", ""),
                    model=model,
                    tokens_generated=data.get("eval_count", 0),
                    tokens_prompt=data.get("prompt_eval_count", 0),
                    total_duration_ms=data.get("total_duration", 0) // 1_000_000,
                    success=True
                )
            else:
                return OllamaResponse(
                    content="",
                    model=model,
                    tokens_generated=0,
                    tokens_prompt=0,
                    total_duration_ms=0,
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
        
        except Exception as e:
            return OllamaResponse(
                content="",
                model=model,
                tokens_generated=0,
                tokens_prompt=0,
                total_duration_ms=0,
                success=False,
                error=str(e)
            )
    
    def stream(self, prompt: str, model: str = "llama3.1:8b",
               system: Optional[str] = None) -> Generator[str, None, None]:
        """Stream a response from Ollama."""
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                },
                stream=True,
                timeout=120
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
        
        except Exception as e:
            yield f"[Error: {e}]"


# ============================================================================
# AGENT EXECUTOR
# ============================================================================

class AgentExecutor:
    """Execute agents with real LLM capabilities."""
    
    SYSTEM_PROMPTS = {
        "scanner": """You are a file scanner agent. Analyze file listings and provide structured insights.
Output JSON with: {"summary": "...", "key_files": [...], "recommendations": [...]}""",
        
        "classifier": """You are a code classifier agent. Categorize files by their purpose.
Tags: agent, script, config, api, frontend, backend, docs, test, lib, data.
Output JSON with: {"classifications": [{"file": "...", "tags": [...], "confidence": 0.9}]}""",
        
        "extractor": """You are a code extractor agent. Extract key information from source code.
Focus on: function signatures, class definitions, API endpoints, dependencies.
Output JSON with: {"functions": [...], "classes": [...], "apis": [...]}""",
        
        "summarizer": """You are a documentation summarizer. Create concise, informative summaries.
Focus on: purpose, key features, usage examples, dependencies.
Keep summaries under 200 words but information-dense.""",
        
        "code_generator": """You are an expert code generator. Write clean, documented, production-ready code.
Follow best practices: type hints, docstrings, error handling, logging.
Output only the code, no explanations unless asked.""",
        
        "researcher": """You are a research analyst agent. Synthesize information from multiple sources.
Provide: key findings, supporting evidence, recommendations, confidence levels.
Be thorough but concise. Cite sources when available.""",
        
        "reasoner": """You are a reasoning agent specialized in complex problem-solving.
Use step-by-step analysis. Consider multiple perspectives.
Output your reasoning process and final conclusion.""",
    }
    
    def __init__(self):
        self.client = OllamaClient()
        self.execution_log: List[AgentExecution] = []
    
    def get_status(self) -> Dict:
        """Get executor status."""
        available = self.client.is_available()
        models = self.client.list_models() if available else []
        
        return {
            "ollama_available": available,
            "models": models,
            "executions": len(self.execution_log),
            "last_execution": self.execution_log[-1].timestamp if self.execution_log else None,
        }
    
    @track(name="agent_execute")
    def execute(self, agent_type: str, prompt: str, 
                context: Optional[Dict] = None) -> Dict:
        """Execute an agent with the given prompt."""
        
        # Get model routing
        model_type = AGENT_MODELS.get(agent_type, "balanced")
        model = self.client.get_best_model(model_type)
        
        # Get system prompt
        system = self.SYSTEM_PROMPTS.get(agent_type, "You are a helpful AI assistant.")
        
        # Add context to prompt if provided
        full_prompt = prompt
        if context:
            context_str = json.dumps(context, indent=2)
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"
        
        # Execute
        response = self.client.generate(
            prompt=full_prompt,
            model=model,
            system=system
        )
        
        # Log execution
        execution = AgentExecution(
            agent_id=agent_type,
            model=model,
            prompt=prompt[:500],  # Truncate for storage
            response=response.content[:1000],
            tokens=response.tokens_generated,
            duration_ms=response.total_duration_ms
        )
        self.execution_log.append(execution)
        
        # Parse JSON if possible
        output = response.content
        try:
            if output.strip().startswith("{") or output.strip().startswith("["):
                output = json.loads(output)
        except:
            pass
        
        return {
            "success": response.success,
            "agent": agent_type,
            "model": model,
            "output": output,
            "tokens": response.tokens_generated,
            "duration_ms": response.total_duration_ms,
            "error": response.error,
        }
    
    def execute_chain(self, steps: List[Dict]) -> List[Dict]:
        """Execute a chain of agent steps."""
        results = []
        context = {}
        
        for i, step in enumerate(steps):
            agent_type = step.get("agent", "summarizer")
            prompt = step.get("prompt", "")
            
            # Add previous results to context
            if results:
                context["previous_results"] = [r["output"] for r in results[-3:]]
            
            result = self.execute(agent_type, prompt, context)
            result["step"] = i
            results.append(result)
            
            # Update context with this result
            context[f"step_{i}"] = result["output"]
            
            # Stop if error and not configured to continue
            if not result["success"] and not step.get("continue_on_error", False):
                break
        
        return results


# ============================================================================
# CLI
# ============================================================================

def main():
    print("=" * 60)
    print("🤖 AZIREM OLLAMA EXECUTOR")
    print("=" * 60)
    
    executor = AgentExecutor()
    status = executor.get_status()
    
    print(f"\nOllama available: {status['ollama_available']}")
    
    if not status['ollama_available']:
        print("❌ Ollama is not running. Start it with: ollama serve")
        return
    
    print(f"Models: {', '.join(status['models'][:5])}")
    
    # Demo executions
    print("\n" + "-" * 60)
    print("🧪 DEMO EXECUTIONS")
    print("-" * 60)
    
    demos = [
        ("summarizer", "Summarize what AZIREM is based on this: AZIREM is a sovereign discovery ecosystem that inventories, classifies, and orchestrates code across multiple projects."),
        ("classifier", "Classify these files: scanner.py, config.yaml, README.md, test_api.py, app.tsx"),
        ("reasoner", "What are the key benefits of running LLMs locally vs using cloud APIs?"),
    ]
    
    for agent_type, prompt in demos:
        print(f"\n🔹 Agent: {agent_type}")
        print(f"   Prompt: {prompt[:60]}...")
        
        result = executor.execute(agent_type, prompt)
        
        if result["success"]:
            output = result["output"]
            if isinstance(output, str):
                print(f"   Output: {output[:200]}...")
            else:
                print(f"   Output: {json.dumps(output, indent=2)[:200]}...")
            print(f"   Tokens: {result['tokens']} | Time: {result['duration_ms']}ms")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ Executor ready!")


if __name__ == "__main__":
    main()
