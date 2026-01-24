"""
AZIREM Agents Package
======================
Complete agent ecosystem for the AZIREM multi-agent system.

Core Agents (Phase 1-5):
- ScannerAgent: File discovery
- ClassifierAgent: File tagging
- ExtractorAgent: Code extraction
- DependencyResolverAgent: Dependency parsing
- SecretsAgent: Secret detection
- SummarizerAgent: Summary generation (LLM-enhanced)

Extended Agents (Phase 6-8):
- MemoryAgent: ChromaDB vector store, conversation persistence
- MCPToolAgent: GitHub, Supabase, Perplexity integration
- EmbeddingAgent: Semantic search via sentence-transformers
- DocGenAgent: Automatic documentation generation
"""

# Core agents
from .core_agents import (
    BaseAgent,
    TaskResult,
    ScannerAgent,
    ClassifierAgent,
    ExtractorAgent,
    DependencyResolverAgent,
    SecretsAgent,
    SummarizerAgent,
    AgentFactory,
)

# Extended agents (optional imports)
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

try:
    from .zen_agents import ZenArchitectAgent
except ImportError:
    ZenArchitectAgent = None


__all__ = [
    # Core
    "BaseAgent",
    "TaskResult",
    "ScannerAgent",
    "ClassifierAgent",
    "ExtractorAgent",
    "DependencyResolverAgent",
    "SecretsAgent",
    "SummarizerAgent",
    "AgentFactory",
    # Extended
    "MemoryAgent",
    "MCPToolAgent",
    "EmbeddingAgent",
    "DocGenAgent",
    "ZenArchitectAgent",
]

__version__ = "2.1.0"
