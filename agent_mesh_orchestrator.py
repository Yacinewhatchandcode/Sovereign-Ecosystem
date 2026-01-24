"""
🌐 SOVEREIGN AGENT MESH ORCHESTRATOR
====================================
LangGraph-based orchestrator for 550+ file-expert agents.
Routes queries to the right agents and coordinates multi-agent collaboration.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# LangChain/LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_ollama import ChatOllama
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangGraph not available: {e}")

# Opik disabled - using pure local LLM
OPIK_ENABLED = False

# Mock decorator
def track(name=None, **kwargs):
    def decorator(func):
        return func
    return decorator

# ============================================================================
# STATE DEFINITION
# ============================================================================

@dataclass
class AgentMeshState:
    """State for the agent mesh graph."""
    user_query: str
    target_files: List[str]  # Files relevant to query
    active_agents: List[str]  # Agents currently working
    agent_responses: Dict[str, str]  # Agent ID -> Response
    final_answer: str
    error: Optional[str] = None

# ============================================================================
# AGENT MESH LOADER
# ============================================================================

class AgentMeshLoader:
    """Loads and manages the file-level agent mesh."""
    
    def __init__(self, mesh_path: str = None):
        if mesh_path is None:
            mesh_path = Path(__file__).parent / "agent_mesh.json"
        self.mesh_path = str(mesh_path)
        self.agents = {}
        self.modules = {}
        self.load_mesh()
    
    def load_mesh(self):
        """Load agent mesh from JSON."""
        with open(self.mesh_path, 'r') as f:
            data = json.load(f)
        
        self.modules = data["modules"]
        
        for agent_data in data["agents"]:
            agent_id = agent_data["file_path"]
            self.agents[agent_id] = agent_data
        
        print(f"✅ Loaded {len(self.agents)} agents from {len(self.modules)} modules")
    
    def find_relevant_agents(self, query: str) -> List[str]:
        """Find agents relevant to a query using keyword matching."""
        relevant = []
        query_lower = query.lower()
        
        # Primary paths to prioritize
        primary_dirs = ["sovereign-dashboard", "azirem_agents", "azirem_orchestration", "root"]
        
        # Keywords to file patterns
        keywords = {
            "dashboard": ["index.html", "real_agent_system.py"],
            "ui": ["index.html", ".js", "css"],
            "backend": ["real_agent_system.py", "azirem_agents"],
            "api": ["real_agent_system.py", "endpoint"],
            "agent": ["azirem_agents", "agent"],
            "evolution": ["azirem_evolution", "evolve"],
            "brain": ["azirem_brain.py"],
        }
        
        # Scoring system for routing
        scores = {}
        for agent_id, agent_data in self.agents.items():
            score = 0
            agent_id_lower = agent_id.lower()
            
            # Boost EXACT file mention in query
            if agent_data["file_name"].lower() in query_lower:
                score += 50
            
            # Keyword matches
            for keyword, patterns in keywords.items():
                if keyword in query_lower:
                    if any(pattern in agent_id_lower for pattern in patterns):
                        score += 10
            
            # Prioritize primary project directories
            if any(agent_id.startswith(p) for p in primary_dirs):
                score += 5
            
            # Penalty for READMEs or non-code files unless relevant
            if "readme" in agent_id_lower and "readme" not in query_lower:
                score -= 20
            
            # Penalize .agent skills unless explicitly asked for internal tools
            if ".agent" in agent_id and "skill" not in query_lower:
                score -= 15
                
            if score > 0:
                scores[agent_id] = score
        
        # Sort by score and take TOP 3 for 15-sec turbo collaboration
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        relevant = [a[0] for a in sorted_agents[:3]]
        
        # Fallback
        if not relevant:
            relevant = ["sovereign-dashboard/real_agent_system.py", "sovereign-dashboard/index.html"]
            
        return relevant
    
    def get_agent_prompt(self, agent_id: str) -> str:
        """Get system prompt for an agent."""
        return self.agents[agent_id]["system_prompt"]

# ============================================================================
# AGENT EXECUTOR
# ============================================================================

class FileAgentExecutor:
    """Executes individual file agents using Ollama."""
    
    # Strategic model routing based on task complexity
    MODEL_ROUTING = {
        "fast": "qwen2.5:3b",           # Quick queries, simple analysis
        "balanced": "llama3.1:8b",      # Most file agents
        "powerful": "phi3:14b",         # Complex reasoning
        "reasoning": "deepseek-r1:7b",  # Deep analysis
        "vision": "llama3.2-vision",    # Image/UI analysis
    }
    
    def __init__(self, model_type: str = "fast", bytebot_bridge=None, dispatcher=None):
        self.model = self.MODEL_ROUTING.get(model_type, "llama3.1:8b")
        self.bytebot_bridge = bytebot_bridge
        self.dispatcher = dispatcher
        
        try:
            from langchain_community.chat_models import ChatOllama
            self.llm = ChatOllama(model=self.model, temperature=0)
        except ImportError:
            self.llm = None
            
        print(f"🚀 [TURBO] Using model: {self.model}")
    
    @track(name="file_agent_execute")
    async def execute(self, agent_id: str, system_prompt: str, query: str) -> str:
        """Execute a file agent with a query and stream the response."""
        if not self.llm:
            return f"[LangGraph not available] Agent {agent_id} would process: {query}"
        
        # Read the actual file content for complete knowledge
        file_content = ""
        file_size = 0
        try:
            # Handle ByteBot paths or assume ByteBot if bridge is present
            if self.bytebot_bridge:
                # If agent_id looks like a relative path, try to read from ByteBot /workspace
                container_path = f"/workspace/{agent_id}" if not agent_id.startswith("/") else agent_id
                file_content = await self.bytebot_bridge.read_container_file(container_path)
                if not file_content:
                    file_content = "[File empty or not readable in ByteBot]"
            else:
                full_path = Path("/Users/yacinebenhamou/aSiReM") / agent_id
                if full_path.exists():
                    # Read only first 400 and last 400 lines for huge files to stay fast
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        file_size = len("".join(lines))
                        if len(lines) > 800:
                            file_content = "".join(lines[:400]) + "\n\n... [TRUNCATED FOR SPEED] ...\n\n" + "".join(lines[-400:])
                        else:
                            file_content = "".join(lines)
                else:
                    file_content = "[File not found on disk]"
        except Exception as e:
            file_content = f"[Error reading file: {e}]"

        # Move content to HumanMessage to ensure attention on small models
        human_msg = f"""I am the user. You are the expert for {agent_id}.
ACTUAL CODE FOR {agent_id}:
---
{file_content}
---
QUERY: {query}
ANSWER IN 3 TECHNICAL SENTENCES:"""
        
        messages = [
            HumanMessage(content=human_msg)
        ]
        
        print(f"\n💬 [STREAMING] Agent {agent_id} is analyzing {len(file_content)} chars...")
        print(f"{'='*20} AGENT: {agent_id} {'='*20}")
        
        full_response = ""
        try:
            # Stream the response chunk by chunk to the console
            async for chunk in self.llm.astream(messages):
                content = chunk.content
                print(content, end="", flush=True)
                full_response += content
            print(f"\n{'='*58}\n")
            
            # Autonomous Actuation check
            if self.dispatcher and "[ACTION:" in full_response:
                await self._parse_and_dispatch(agent_id, full_response)
                
            return full_response
        except Exception as e:
            error_msg = f"[Error] Agent {agent_id} failed: {e}"
            print(f"\n❌ {error_msg}")
            return error_msg

    async def _parse_and_dispatch(self, agent_id: str, response: str):
        """Parse structured action command from LLM response and dispatch."""
        import re
        # Example format: [ACTION: open_vscode path=/workspace]
        match = re.search(r"\[ACTION:\s*(\w+)(.*?)\]", response)
        if match:
            action_name = match.group(1).lower()
            params_str = match.group(2).strip()
            
            params = {}
            # Basic key=value param parser
            param_matches = re.finditer(r"(\w+)=([\w\/\-\.]+)", params_str)
            for m in param_matches:
                params[m.group(1)] = m.group(2)
            
            print(f"⚡ [ACTUATION] Agent {agent_id} triggered: {action_name} with {params}")
            
            try:
                from agent_action_dispatcher import AgentAction, ActionType
                # Map string to ActionType
                action_type = None
                for at in ActionType:
                    if at.value == action_name:
                        action_type = at
                        break
                
                if action_type:
                    action = AgentAction(
                        agent_id=agent_id,
                        agent_type="azirem", # Mesh agents are azirem-team class
                        action_type=action_type,
                        params=params,
                        description=f"Mesh Agent {agent_id} autonomy trigger"
                    )
                    asyncio.create_task(self.dispatcher.dispatch(action))
            except Exception as e:
                print(f"⚠️ Actuation dispatch failed: {e}")

# ============================================================================
# LANGGRAPH ORCHESTRATOR
# ============================================================================

class SovereignAgentMesh:
    """Main orchestrator for the file-level agent mesh."""
    
    def __init__(self, bytebot_bridge=None, dispatcher=None):
        self.loader = AgentMeshLoader()
        self.executor = FileAgentExecutor(bytebot_bridge=bytebot_bridge, dispatcher=dispatcher)
        self.graph = self.build_graph() if LANGGRAPH_AVAILABLE else None
        self.bytebot_bridge = bytebot_bridge
        self.dispatcher = dispatcher
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(AgentMeshState)
        
        # Define nodes
        workflow.add_node("route", self.route_query)
        workflow.add_node("execute_agents", self.execute_agents)
        workflow.add_node("synthesize", self.synthesize_responses)
        
        # Define edges
        workflow.set_entry_point("route")
        workflow.add_edge("route", "execute_agents")
        workflow.add_edge("execute_agents", "synthesize")
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    async def route_query(self, state: AgentMeshState) -> AgentMeshState:
        """Route query to relevant file agents."""
        print(f"\n🔍 Routing query: {state.user_query}")
        
        relevant_agents = self.loader.find_relevant_agents(state.user_query)
        state.target_files = relevant_agents
        state.active_agents = relevant_agents
        
        print(f"✅ Found {len(relevant_agents)} relevant agents:")
        for agent_id in relevant_agents[:5]:
            print(f"  - {agent_id}")
        
        return state
    
    async def execute_agents(self, state: AgentMeshState) -> AgentMeshState:
        """Execute all relevant agents in parallel for maximum speed."""
        print(f"\n🤖 Activating {len(state.active_agents)} Sovereign File Agents...")
        
        results = {}
        
        async def run_and_log(agent_id):
            system_prompt = self.loader.get_agent_prompt(agent_id)
            # This handles its own printing but parallel outputs might weave
            response = await self.executor.execute(agent_id, system_prompt, state.user_query)
            results[agent_id] = response
            return agent_id, response

        # Parallel execution
        tasks = [run_and_log(agent_id) for agent_id in state.active_agents]
        await asyncio.gather(*tasks)
        
        state.agent_responses = results
        print(f"\n✅ All {len(state.agent_responses)} agents have reported back.")
        
        return state
    
    async def synthesize_responses(self, state: AgentMeshState) -> AgentMeshState:
        """Fast synthesis for turbo speed."""
        print(f"\n🧠 Synthesizing {len(state.agent_responses)} responses in turbo mode...")
        
        combined = "\n\n".join([
            f"--- AGENT: {agent_id} ---\n{response}"
            for agent_id, response in state.agent_responses.items()
        ])
        
        # Use the fast model for synthesis too
        synthesis_llm = ChatOllama(model="qwen2.5:3b", temperature=0)
        
        synthesis_prompt = f"""
        You are the Sovereign System Architect. 
        Synthesize these reports into a 15-second technical verdict.
        
        User Query: "{state.user_query}"
        
        Reports:
        {combined}
        """
        
        print(f"🌐 [STREAMING] System Architect is deciding...")
        full_synthesis = ""
        try:
            async for chunk in synthesis_llm.astream([HumanMessage(content=synthesis_prompt)]):
                content = chunk.content
                print(content, end="", flush=True)
                full_synthesis += content
            print("\n")
            state.final_answer = full_synthesis
        except Exception:
            state.final_answer = combined
        
        return state
    
    @track(name="agent_mesh_query")
    async def query(self, user_query: str) -> str:
        """Process a user query through the agent mesh."""
        if not self.graph:
            return "LangGraph not available. Install with: pip install langgraph"
        
        initial_state = AgentMeshState(
            user_query=user_query,
            target_files=[],
            active_agents=[],
            agent_responses={},
            final_answer=""
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["final_answer"]

# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    print("=" * 60)
    print("🌐 SOVEREIGN AGENT MESH - INTERACTIVE MODE")
    print("=" * 60)
    
    mesh = SovereignAgentMesh()
    
    print(f"\n✅ Agent Mesh Ready!")
    print(f"📊 Total Agents: {len(mesh.loader.agents)}")
    print(f"📦 Modules: {len(mesh.loader.modules)}")
    
    # Test queries
    test_queries = [
        "Why aren't the dashboard buttons working?",
        "How do I fix the broken UI integration?",
        "What files are involved in the Evolution cycle?"
    ]
    
    print(f"\n🧪 Running test queries...")
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        answer = await mesh.query(query)
        
        print(f"\n📝 Answer:")
        print(answer)
        print()

if __name__ == "__main__":
    if LANGGRAPH_AVAILABLE:
        asyncio.run(main())
    else:
        print("❌ LangGraph not installed. Install with:")
        print("   pip install langgraph langchain-ollama")
