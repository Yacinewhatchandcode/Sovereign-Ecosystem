"""
Cold Azirem Agent Configuration
Maps agents to their optimal Ollama models and capabilities
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AgentConfig:
    """Configuration for a single agent"""
    name: str
    role: str
    model: str
    fallback_model: str
    fast_model: str
    specialty: str
    tools: List[str]
    max_context_messages: int = 10
    temperature: float = 0.7
    top_p: float = 0.9


# Agent Registry - All 10 Agents
AGENT_CONFIGS = {
    "ArchitectureDev": AgentConfig(
        name="ArchitectureDev",
        role="Chief Architect - 1000x expertise in system design, patterns, and scalability",
        model="deepseek-r1:7b",
        fallback_model="phi3:14b",
        fast_model="qwen3:8b",
        specialty="Distributed systems, microservices, cloud-native architecture",
        tools=["web_search", "code_analysis", "diagram_gen", "github_mcp", "supabase_mcp"],
    ),
    
    "ProductManager": AgentConfig(
        name="ProductManager",
        role="Product Strategy - Roadmap planning, feature prioritization, stakeholder alignment",
        model="llama3.1:8b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Product vision, user stories, competitive analysis",
        tools=["web_search", "analytics", "documentation"],
    ),
    
    "BusinessAnalyst": AgentConfig(
        name="BusinessAnalyst",
        role="Business Analysis - Requirements gathering, process optimization",
        model="llama3.1:8b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Requirements engineering, stakeholder management, business process modeling",
        tools=["web_search", "documentation", "analytics"],
    ),
    
    "FrontendDev": AgentConfig(
        name="FrontendDev",
        role="Frontend Engineer - React, Next.js, modern UI/UX",
        model="phi3:14b",
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="React, Next.js, TypeScript, Tailwind CSS, responsive design",
        tools=["code_gen", "github_mcp", "web_search", "ui_preview"],
    ),
    
    "BackendDev": AgentConfig(
        name="BackendDev",
        role="Backend Engineer - APIs, databases, microservices",
        model="phi3:14b",
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="Python, FastAPI, PostgreSQL, Redis, async programming",
        tools=["code_gen", "github_mcp", "supabase_mcp", "web_search"],
    ),
    
    "DevOpsEngineer": AgentConfig(
        name="DevOpsEngineer",
        role="DevOps Engineer - CI/CD, infrastructure, deployment automation",
        model="phi3:14b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Docker, Kubernetes, GitHub Actions, monitoring, logging",
        tools=["github_mcp", "deployment", "monitoring", "web_search"],
    ),
    
    "DatabaseEngineer": AgentConfig(
        name="DatabaseEngineer",
        role="Database Engineer - Schema design, migrations, optimization",
        model="qwen3:8b",
        fallback_model="llama3.2:3b",
        fast_model="gemma2:2b",
        specialty="PostgreSQL, schema design, query optimization, migrations",
        tools=["supabase_mcp", "code_gen", "web_search"],
    ),
    
    "QASpecialist": AgentConfig(
        name="QASpecialist",
        role="QA Specialist - Testing strategy, automation, quality gates",
        model="qwen3:8b",
        fallback_model="gemma2:2b",
        fast_model="llama3.2:3b",
        specialty="Pytest, integration testing, E2E testing, test automation",
        tools=["code_gen", "test_runner", "github_mcp", "web_search"],
    ),
    
    "SecuritySpecialist": AgentConfig(
        name="SecuritySpecialist",
        role="Security Specialist - Threat modeling, security audits, compliance",
        model="llama3.1:8b",
        fallback_model="phi3:14b",
        fast_model="qwen3:8b",
        specialty="OWASP, penetration testing, secure coding, compliance",
        tools=["code_analysis", "security_scan", "web_search"],
    ),
    
    "TechnicalWriter": AgentConfig(
        name="TechnicalWriter",
        role="Technical Writer - Documentation, guides, API docs",
        model="gemma2:2b",
        fallback_model="qwen3:8b",
        fast_model="llama3.2:3b",
        specialty="Technical documentation, API docs, user guides, tutorials",
        tools=["documentation", "web_search"],
    ),
}


# Ollama Configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "timeout": 120.0,
    "max_retries": 3,
}


# Memory Configuration
MEMORY_CONFIG = {
    "chromadb": {
        "persist_directory": "/Users/yacinebenhamou/aSiReM/.chroma",
        "collection_name": "cold_azirem_knowledge",
    },
    "faiss": {
        "index_path": "/Users/yacinebenhamou/aSiReM/.faiss/cold_azirem.index",
        "dimension": 768,  # nomic-embed-text dimension
    },
    "embedding_model": "nomic-embed-text",
}


# Inter-Agent Communication
COMMUNICATION_CONFIG = {
    "message_bus": "event_driven",  # Options: event_driven, direct, queue
    "max_parallel_agents": 4,
    "consensus_threshold": 0.7,  # 70% agreement for multi-agent decisions
}


def get_agent_config(agent_name: str) -> AgentConfig:
    """Get configuration for a specific agent"""
    if agent_name not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(AGENT_CONFIGS.keys())}")
    return AGENT_CONFIGS[agent_name]


def list_all_agents() -> List[str]:
    """List all available agents"""
    return list(AGENT_CONFIGS.keys())
