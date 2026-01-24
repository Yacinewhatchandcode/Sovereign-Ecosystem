"""
🧬 Complete Autonomy Agents Package
====================================
Auto-generated package containing all 74 autonomous agents.
Generated: 2026-01-21T20:58:51.587342

Usage:
    from autonomy_agents import get_agent_by_id, get_critical_agents
    agent = get_agent_by_id("error_auto_fix")
    await agent.initialize()
"""

from .autonomy_mesh_registry import (
    AGENT_REGISTRY,
    AGENTS_BY_CATEGORY,
    AGENTS_BY_PRIORITY,
    get_all_agents,
    get_agent_by_id,
    get_agents_by_category,
    get_agents_by_priority,
    get_critical_agents,
    initialize_all_agents,
    get_registry_stats,
)

__all__ = [
    "AGENT_REGISTRY",
    "AGENTS_BY_CATEGORY", 
    "AGENTS_BY_PRIORITY",
    "get_all_agents",
    "get_agent_by_id",
    "get_agents_by_category",
    "get_agents_by_priority",
    "get_critical_agents",
    "initialize_all_agents",
    "get_registry_stats",
]
