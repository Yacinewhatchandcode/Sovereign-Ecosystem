"""
AZIREM & BumbleBee Demo
Demonstrates the master orchestrator agents and their sub-agent teams
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cold_azirem.agents.azirem_agent import AziremAgent
from cold_azirem.agents.bumblebee_agent import BumbleBeeAgent
from cold_azirem.agents.bumblebee_subagents import (
    WebSearchSpecialistAgent,
    ResearchAnalystAgent,
    PDFProcessorAgent,
    WordProcessorAgent,
    ExcelProcessorAgent,
    PowerPointProcessorAgent,
    DocumentSynthesizerAgent,
)
from cold_azirem.config.master_agent_config import (
    AZIREM_CONFIG,
    BUMBLEBEE_CONFIG,
    BUMBLEBEE_SUB_AGENT_CONFIGS,
)
from cold_azirem.tools.agent_tools import get_tools_for_agent
from cold_azirem.tools.bumblebee_tools import get_bumblebee_tools
from cold_azirem.orchestration.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


async def demo_1_initialize_master_agents():
    """Demo 1: Initialize AZIREM and BumbleBee"""
    print_section("DEMO 1: Initialize Master Orchestrator Agents")
    
    orchestrator = AgentOrchestrator()
    
    # Initialize all 10 coding agents first
    print("🚀 Initializing AZIREM's coding team (10 agents)...")
    await orchestrator.initialize_all_agents()
    
    # Initialize AZIREM
    print("\n🎯 Initializing AZIREM (Master Coding Orchestrator)...")
    azirem_tools = get_tools_for_agent("AZIREM", AZIREM_CONFIG.tools)
    azirem = AziremAgent(
        name=AZIREM_CONFIG.name,
        role=AZIREM_CONFIG.role,
        model=AZIREM_CONFIG.model,
        fallback_model=AZIREM_CONFIG.fallback_model,
        tools=azirem_tools,
    )
    
    # Register all coding agents as AZIREM's sub-agents
    for agent_name, agent in orchestrator.agents.items():
        azirem.register_sub_agent(agent_name, agent)
    
    print(f"✅ AZIREM initialized with {len(azirem.sub_agents)} sub-agents")
    print(f"   Sub-agents: {', '.join(azirem.sub_agents.keys())}")
    
    # Initialize BumbleBee
    print("\n🐝 Initializing BumbleBee (Master Research & Document Orchestrator)...")
    bumblebee_tools = get_bumblebee_tools("BumbleBee", BUMBLEBEE_CONFIG.tools)
    bumblebee = BumbleBeeAgent(
        name=BUMBLEBEE_CONFIG.name,
        role=BUMBLEBEE_CONFIG.role,
        model=BUMBLEBEE_CONFIG.model,
        fallback_model=BUMBLEBEE_CONFIG.fallback_model,
        tools=bumblebee_tools,
    )
    
    # Initialize BumbleBee's sub-agents
    print("\n🔧 Initializing BumbleBee's sub-agents...")
    bumblebee_subagents = {}
    
    for agent_name, config in BUMBLEBEE_SUB_AGENT_CONFIGS.items():
        tools = get_bumblebee_tools(agent_name, config.tools)
        
        # Create appropriate agent instance
        if agent_name == "WebSearchSpecialist":
            agent = WebSearchSpecialistAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "ResearchAnalyst":
            agent = ResearchAnalystAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "PDFProcessor":
            agent = PDFProcessorAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "WordProcessor":
            agent = WordProcessorAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "ExcelProcessor":
            agent = ExcelProcessorAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "PowerPointProcessor":
            agent = PowerPointProcessorAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        elif agent_name == "DocumentSynthesizer":
            agent = DocumentSynthesizerAgent(
                name=config.name,
                role=config.role,
                model=config.model,
                fallback_model=config.fallback_model,
                tools=tools,
            )
        
        bumblebee_subagents[agent_name] = agent
        bumblebee.register_sub_agent(agent_name, agent)
        print(f"   ✅ {agent_name} ({config.model})")
    
    print(f"\n✅ BumbleBee initialized with {len(bumblebee.sub_agents)} sub-agents")
    
    return orchestrator, azirem, bumblebee, bumblebee_subagents


async def demo_2_azirem_coding_task():
    """Demo 2: AZIREM coordinates a coding task"""
    print_section("DEMO 2: AZIREM Coordinates Coding Task")
    
    orchestrator, azirem, bumblebee, _ = await demo_1_initialize_master_agents()
    
    task = "Build a real-time chat application with user authentication"
    
    print(f"📋 Task: {task}\n")
    print("🎯 AZIREM analyzing and creating execution plan...")
    
    plan = await azirem.analyze_and_plan(task)
    
    print("\n📊 AZIREM's Analysis:")
    print(f"   Response: {plan['raw_response'][:300]}...")
    
    print("\n✅ AZIREM would now coordinate:")
    print("   1. ProductManager - Define requirements")
    print("   2. ArchitectureDev - Design architecture")
    print("   3. FrontendDev + BackendDev - Parallel development")
    print("   4. QASpecialist + SecuritySpecialist - Testing & security")
    print("   5. TechnicalWriter - Documentation")


async def demo_3_bumblebee_research_task():
    """Demo 3: BumbleBee coordinates research and document generation"""
    print_section("DEMO 3: BumbleBee Coordinates Research & Documentation")
    
    _, _, bumblebee, bumblebee_subagents = await demo_1_initialize_master_agents()
    
    topic = "AI trends in 2026"
    
    print(f"📋 Research Topic: {topic}\n")
    print("🐝 BumbleBee creating research and documentation plan...")
    
    plan = await bumblebee.research_and_document(
        topic=topic,
        output_format="pdf",
        depth="deep"
    )
    
    print("\n📊 BumbleBee's Plan:")
    print(f"   Response: {plan['raw_response'][:300]}...")
    
    print("\n✅ BumbleBee would now coordinate:")
    print("   1. WebSearchSpecialist - Multi-source web search")
    print("   2. ResearchAnalyst - Analyze and synthesize findings")
    print("   3. DocumentSynthesizer - Structure the report")
    print("   4. PDFProcessor - Generate professional PDF")
    
    # Test document tools
    print("\n🧪 Testing BumbleBee's document tools...")
    
    # Test web search
    search_agent = bumblebee_subagents["WebSearchSpecialist"]
    search_result = await search_agent.execute_tool(
        "semantic_web_search",
        {"query": topic, "depth": "deep"}
    )
    print(f"\n   ✅ Web Search: Found {len(search_result['results'])} results")
    
    # Test PDF creation
    pdf_agent = bumblebee_subagents["PDFProcessor"]
    pdf_result = await pdf_agent.execute_tool(
        "create_pdf",
        {
            "content": "Research findings on AI trends...",
            "title": "AI Trends 2026",
            "filename": "ai_trends_2026.pdf"
        }
    )
    print(f"   ✅ PDF Created: {pdf_result['filename']} ({pdf_result['pages']} pages)")


async def demo_4_azirem_bumblebee_collaboration():
    """Demo 4: AZIREM and BumbleBee collaborate"""
    print_section("DEMO 4: AZIREM & BumbleBee Collaboration")
    
    orchestrator, azirem, bumblebee, _ = await demo_1_initialize_master_agents()
    
    task = "Research best practices for microservices architecture and build a demo application with full documentation"
    
    print(f"📋 Complex Task: {task}\n")
    
    print("🔄 Collaboration Workflow:")
    print("\n   Phase 1: BumbleBee Research")
    print("   🐝 BumbleBee:")
    print("      - WebSearchSpecialist: Search for microservices best practices")
    print("      - ResearchAnalyst: Analyze and synthesize findings")
    print("      - DocumentSynthesizer: Create research summary")
    
    print("\n   Phase 2: AZIREM Development")
    print("   🎯 AZIREM (using BumbleBee's research):")
    print("      - ArchitectureDev: Design microservices architecture")
    print("      - BackendDev: Implement demo services")
    print("      - FrontendDev: Create demo UI")
    print("      - QASpecialist: Test the demo")
    
    print("\n   Phase 3: BumbleBee Documentation")
    print("   🐝 BumbleBee:")
    print("      - DocumentSynthesizer: Combine code + research")
    print("      - WordProcessor: Create comprehensive guide")
    print("      - PowerPointProcessor: Create presentation")
    print("      - PDFProcessor: Generate final PDF documentation")
    
    print("\n✅ Final Deliverables:")
    print("   - Research report (PDF)")
    print("   - Demo application (code)")
    print("   - User guide (Word)")
    print("   - Architecture presentation (PowerPoint)")


async def demo_5_master_agent_status():
    """Demo 5: Show master agent status"""
    print_section("DEMO 5: Master Agent Status")
    
    orchestrator, azirem, bumblebee, _ = await demo_1_initialize_master_agents()
    
    print("📊 AZIREM Status:")
    azirem_status = azirem.get_team_status()
    print(f"   Master: {azirem_status['master']}")
    print(f"   Sub-agents: {len(azirem_status['sub_agents'])}")
    print(f"   Team: {', '.join(azirem_status['sub_agents'][:5])}...")
    
    print("\n📊 BumbleBee Status:")
    bumblebee_status = bumblebee.get_team_status()
    print(f"   Master: {bumblebee_status['master']}")
    print(f"   Sub-agents: {len(bumblebee_status['sub_agents'])}")
    print(f"   Team: {', '.join(bumblebee_status['sub_agents'])}")


async def main():
    """Run all demos"""
    print("\n" + "🌌 " * 20)
    print("  AZIREM & BUMBLEBEE - MASTER ORCHESTRATOR AGENTS DEMO")
    print("🌌 " * 20 + "\n")
    
    try:
        await demo_2_azirem_coding_task()
        await demo_3_bumblebee_research_task()
        await demo_4_azirem_bumblebee_collaboration()
        await demo_5_master_agent_status()
        
        print_section("✅ All Demos Complete!")
        print("AZIREM and BumbleBee are ready to orchestrate complex tasks!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
