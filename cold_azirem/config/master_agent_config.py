"""
Master Agent Configuration
AZIREM (Coding), BumbleBee (Research), and SPECTRA (Design)
"""

from dataclasses import dataclass
from typing import List

from .agent_config import AgentConfig


# ============================================================================
# AZIREM - Master Coding Orchestrator
# ============================================================================

AZIREM_CONFIG = AgentConfig(
    name="AZIREM",
    role="Master Coding Orchestrator - Manages all 10 coding agents",
    model="deepseek-r1:7b",  # Deep reasoning for strategic coordination
    fallback_model="llama3.1:8b",
    fast_model="qwen3:8b",
    specialty="Strategic coordination, task decomposition, agent orchestration",
    tools=["web_search", "code_analysis", "github_mcp", "supabase_mcp"],
    max_context_messages=20,  # Larger context for coordination
    temperature=0.7,
)

# AZIREM's Sub-Agents (the 10 coding agents)
AZIREM_SUB_AGENTS = [
    "ArchitectureDev",
    "ProductManager",
    "BusinessAnalyst",
    "FrontendDev",
    "BackendDev",
    "DevOpsEngineer",
    "DatabaseEngineer",
    "QASpecialist",
    "SecuritySpecialist",
    "TechnicalWriter",
]


# ============================================================================
# BUMBLEBEE - Master Research & Document Orchestrator
# ============================================================================

BUMBLEBEE_CONFIG = AgentConfig(
    name="BumbleBee",
    role="Master Research & Document Orchestrator - Manages research and document processing agents",
    model="llama3.1:8b",  # Balanced model for coordination
    fallback_model="qwen3:8b",
    fast_model="gemma2:2b",
    specialty="Research coordination, document synthesis, multi-source information gathering",
    tools=[
        "semantic_web_search",
        "multi_source_research",
        "create_pdf",
        "create_word_doc",
        "create_excel_sheet",
        "create_presentation",
        "synthesize_research_report",
    ],
    max_context_messages=20,
    temperature=0.7,
)

# BumbleBee's Sub-Agents (research and document processing)
BUMBLEBEE_SUB_AGENT_CONFIGS = {
    "WebSearchSpecialist": AgentConfig(
        name="WebSearchSpecialist",
        role="Cutting-edge semantic web search specialist",
        model="qwen3:8b",  # Fast for search operations
        fallback_model="gemma2:2b",
        fast_model="llama3.2:3b",
        specialty="Semantic search, multi-source research, query optimization",
        tools=["semantic_web_search", "multi_source_research"],
    ),
    
    "ResearchAnalyst": AgentConfig(
        name="ResearchAnalyst",
        role="Deep research analysis and synthesis",
        model="llama3.1:8b",  # Balanced for analysis
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Information synthesis, fact-checking, trend analysis",
        tools=["multi_source_research", "synthesize_research_report"],
    ),
    
    "PDFProcessor": AgentConfig(
        name="PDFProcessor",
        role="PDF creation, editing, and extraction",
        model="gemma2:2b",  # Lightweight for document ops
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="PDF operations, document conversion",
        tools=["create_pdf", "extract_pdf_content", "merge_pdfs"],
    ),
    
    "WordProcessor": AgentConfig(
        name="WordProcessor",
        role="Word document generation and editing",
        model="gemma2:2b",
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="Word document creation, formatting, templates",
        tools=["create_word_doc", "add_word_table"],
    ),
    
    "ExcelProcessor": AgentConfig(
        name="ExcelProcessor",
        role="Excel spreadsheet creation and analysis",
        model="gemma2:2b",
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="Spreadsheet creation, formulas, charts",
        tools=["create_excel_sheet", "add_excel_chart"],
    ),
    
    "PowerPointProcessor": AgentConfig(
        name="PowerPointProcessor",
        role="PowerPoint presentation creation",
        model="gemma2:2b",
        fallback_model="llama3.2:3b",
        fast_model="qwen3:8b",
        specialty="Presentation creation, slide design",
        tools=["create_presentation", "add_slide"],
    ),
    
    "DocumentSynthesizer": AgentConfig(
        name="DocumentSynthesizer",
        role="Combines research into comprehensive documents",
        model="llama3.1:8b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Document synthesis, report generation",
        tools=["synthesize_research_report", "create_pdf", "create_word_doc"],
    ),
}


# ============================================================================
# SPECTRA - Master Design Orchestrator
# ============================================================================

SPECTRA_CONFIG = AgentConfig(
    name="SPECTRA",
    role="Master Design Orchestrator - Manages the creative process",
    model="deepseek-r1:7b", # Deep reasoning for creative direction
    fallback_model="llama3.1:8b",
    fast_model="qwen3:8b",
    specialty="UX/UI Design, Visual Aesthetics, Motion Choreography",
    tools=[
        "analyze_visual_identity",
        "generate_color_palette",
        "scaffold_ui_component",
        "generate_animation_script"
    ],
    max_context_messages=20,
    temperature=0.8, # Higher temperature for creativity
)

SPECTRA_SUB_AGENT_CONFIGS = {
    "CreativeDirector": AgentConfig(
        name="CreativeDirector",
        role="Visionary - Defines aesthetics and style",
        model="llama3.1:8b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="Art direction, brand identity, visual strategy",
        tools=["analyze_visual_identity", "generate_color_palette"],
    ),
    "InterfaceArchitect": AgentConfig(
        name="InterfaceArchitect",
        role="Builder - Implements code structure",
        model="deepseek-r1:7b", # Needs coding logic
        fallback_model="llama3.1:8b",
        fast_model="qwen3:8b",
        specialty="HTML5, CSS3, React, Semantic Markup",
        tools=["scaffold_ui_component"],
    ),
    "MotionChoreographer": AgentConfig(
        name="MotionChoreographer",
        role="Animator - Brings interface to life",
        model="llama3.1:8b",
        fallback_model="qwen3:8b",
        fast_model="gemma2:2b",
        specialty="GSAP, Three.js, CSS Animations",
        tools=["generate_animation_script"],
    ),
}


# ============================================================================
# MASTER AGENT HIERARCHY
# ============================================================================

MASTER_AGENT_HIERARCHY = {
    "AZIREM": {
        "config": AZIREM_CONFIG,
        "sub_agents": AZIREM_SUB_AGENTS,
        "domain": "coding",
    },
    "BumbleBee": {
        "config": BUMBLEBEE_CONFIG,
        "sub_agents": list(BUMBLEBEE_SUB_AGENT_CONFIGS.keys()),
        "domain": "research_and_documents",
    },
    "SPECTRA": {
        "config": SPECTRA_CONFIG,
        "sub_agents": list(SPECTRA_SUB_AGENT_CONFIGS.keys()),
        "domain": "design_and_ux",
    },
}


def get_master_agent_config(master_name: str) -> AgentConfig:
    """Get configuration for a master agent"""
    if master_name == "AZIREM":
        return AZIREM_CONFIG
    elif master_name == "BumbleBee":
        return BUMBLEBEE_CONFIG
    elif master_name == "SPECTRA":
        return SPECTRA_CONFIG
    else:
        raise ValueError(f"Unknown master agent: {master_name}")


def get_bumblebee_subagent_config(agent_name: str) -> AgentConfig:
    """Get configuration for a BumbleBee sub-agent"""
    if agent_name not in BUMBLEBEE_SUB_AGENT_CONFIGS:
        raise ValueError(f"Unknown BumbleBee sub-agent: {agent_name}")
    return BUMBLEBEE_SUB_AGENT_CONFIGS[agent_name]

def get_spectra_subagent_config(agent_name: str) -> AgentConfig:
    """Get configuration for a SPECTRA sub-agent"""
    if agent_name not in SPECTRA_SUB_AGENT_CONFIGS:
        raise ValueError(f"Unknown SPECTRA sub-agent: {agent_name}")
    return SPECTRA_SUB_AGENT_CONFIGS[agent_name]
