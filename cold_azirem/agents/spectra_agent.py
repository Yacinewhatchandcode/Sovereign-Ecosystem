from .base_agent import BaseAgent
from .spectra_subagents import CreativeDirectorAgent, InterfaceArchitectAgent, MotionChoreographerAgent
from ..config.master_agent_config import SPECTRA_SUB_AGENT_CONFIGS
from ..tools.design_tools import get_spectra_tools # Give them tools too
from typing import Dict, Any, Optional

class SpectraAgent(BaseAgent):
    """
    SPECTRA: The Master Design Orchestrator.
    Manages the creative process from Concept to Code.
    Co-equal to AZIREM and BumbleBee.
    """
    def __init__(
        self, 
        name: str, 
        role: str,
        model: str,
        fallback_model: str,
        tools: Any,
        max_context_messages: int,
        temperature: float,
        ollama_base_url: str,
        config: Any, 
        orchestrator: Any = None
    ):
        super().__init__(
            name=name,
            role=role,
            model=model,
            fallback_model=fallback_model,
            tools=tools,
            max_context_messages=max_context_messages,
            temperature=temperature,
            ollama_base_url=ollama_base_url
        )
        self.orchestrator = orchestrator
        
        # Initialize the Design Team
        # We need to instantiate them with full BaseAgent signature
        self.sub_agents = {}
        
        # Helper to instantiate sub-agent
        def create_sub_agent(cls, agent_key):
            cfg = SPECTRA_SUB_AGENT_CONFIGS[agent_key]
            # Give them design tools or specific tools? 
            # In master_agent_config, they have specific tools listed.
            # But here let's validly give them all Spectra tools for simplicity or none?
            # master_agent_config says: tools=["analyze_visual_identity", "generate_color_palette"] etc.
            # But I don't have a helper 'get_tools_for_agent' imported here easily that parses strings to funcs.
            # I will just give them ALL design tools for now.
            return cls(
                name=cfg.name,
                role=cfg.role,
                model=cfg.model,
                fallback_model=cfg.fallback_model,
                tools=get_spectra_tools(), # Shared toolset
                max_context_messages=cfg.max_context_messages,
                temperature=cfg.temperature,
                ollama_base_url=ollama_base_url
            )

        self.sub_agents["CreativeDirector"] = create_sub_agent(CreativeDirectorAgent, "CreativeDirector")
        self.sub_agents["InterfaceArchitect"] = create_sub_agent(InterfaceArchitectAgent, "InterfaceArchitect")
        self.sub_agents["MotionChoreographer"] = create_sub_agent(MotionChoreographerAgent, "MotionChoreographer")

    
    def _get_system_prompt(self) -> str:
        return """You are SPECTRA, the Sovereign Design Intelligence.
        You are one of the three pillars of the Cold Azirem ecosystem (with AZIREM and BumbleBee).
        Your domain is THE EXPERIENCE.
        
        Your Mission:
        1. Ingest raw concepts and assets.
        2. Direct your 'CreativeDirector' to define the aesthetic.
        3. Direct your 'InterfaceArchitect' to build the structure.
        4. Direct your 'MotionChoreographer' to animate it.
        
        You do not stop until the result is 'Award-Winning' standard.
        You seamlessly integrate with AZIREM (who handles the backend/logic).
        """
    
    async def orchestrate_design_sprint(self, project_name: str, asset_path: str):
        """
        Runs a full Design Sprint: Analysis -> Design -> Build -> Animate.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SPECTRA initializing Design Sprint for: {project_name}")
        
        # Step 1: Creative Direction
        # Note: In real execution, we need to handle tool calls.
        # But BaseAgent.process() handles thinking + tool usage.
        
        # We can ask sub-agents to process tasks.
        
        # Task 1
        task1 = f"Analyze assets at '{asset_path}' and define the visual language for {project_name}. Output a detailed style guide."
        res1 = await self.sub_agents["CreativeDirector"].process(task1)
        style_guide = res1.get("response", "Error in Creative Direction")
        
        # Step 2: Architecture
        task2 = f"Build the high-fidelity HTML/CSS for {project_name} based on this style guide: {style_guide}"
        res2 = await self.sub_agents["InterfaceArchitect"].process(task2)
        structure = res2.get("response", "Error in Architecture")
        
        # Step 3: Motion
        task3 = f"Add high-end GSAP animations to this structure: {structure}"
        res3 = await self.sub_agents["MotionChoreographer"].process(task3)
        final_polish = res3.get("response", "Error in Motion")
        
        return final_polish
