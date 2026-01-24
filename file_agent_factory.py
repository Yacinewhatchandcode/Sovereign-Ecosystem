"""
🚀 SOVEREIGN FILE AGENT FACTORY
================================
Auto-generates expert agents for every file in the codebase.
Leverages existing MCP servers for speed.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# CONFIGURATION
# ============================================================================

CODEBASE_ROOT = Path("/Users/yacinebenhamou/aSiReM")

# Directories to scan (exclude external deps)
INCLUDE_DIRS = [
    "azirem_agents",
    "azirem_discovery",
    "azirem_evolution",
    "azirem_memory",
    "azirem_orchestration",
    "azirem_registry",
    "sovereign-dashboard",
    ".agent",
    "src",
    "web-ui"
]

EXCLUDE_PATTERNS = [
    "node_modules",
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "tools/opik"
]

FILE_EXTENSIONS = [".py", ".js", ".html", ".yaml", ".json", ".md"]

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FileAgent:
    """Metadata for a file-level expert agent."""
    file_path: str
    file_name: str
    module: str
    file_type: str
    purpose: str
    dependencies: List[str]
    mcp_tools: List[str]  # Which MCP tools this agent can use
    system_prompt: str

@dataclass
class AgentMesh:
    """The complete file-level agent mesh."""
    total_agents: int
    agents: List[FileAgent]
    modules: Dict[str, List[str]]  # module -> list of file paths

# ============================================================================
# FILE SCANNER
# ============================================================================

def should_include_file(file_path: Path) -> bool:
    """Check if file should be included in agent mesh."""
    # Check extension
    if file_path.suffix not in FILE_EXTENSIONS:
        return False
    
    # Check exclude patterns
    path_str = str(file_path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return False
    
    return True

def scan_codebase() -> List[Path]:
    """Scan codebase and return list of files to create agents for."""
    files = []
    
    for include_dir in INCLUDE_DIRS:
        dir_path = CODEBASE_ROOT / include_dir
        if not dir_path.exists():
            continue
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and should_include_file(file_path):
                files.append(file_path)
    
    # Also include root-level files
    for file_path in CODEBASE_ROOT.glob("*"):
        if file_path.is_file() and should_include_file(file_path):
            files.append(file_path)
    
    return sorted(files)

# ============================================================================
# AGENT GENERATOR
# ============================================================================

def detect_file_purpose(file_path: Path) -> str:
    """Detect the purpose of a file based on its name and location."""
    name = file_path.stem.lower()
    parent = file_path.parent.name.lower()
    
    # Pattern matching
    if "test" in name:
        return "Testing and validation"
    elif "agent" in name or "agent" in parent:
        return "Agent implementation"
    elif "api" in name or "endpoint" in name:
        return "API endpoint"
    elif "config" in name or file_path.suffix == ".yaml":
        return "Configuration"
    elif "dashboard" in parent or "ui" in parent:
        return "User interface"
    elif "brain" in name:
        return "Core intelligence"
    elif "orchestrat" in name:
        return "Multi-agent coordination"
    elif "memory" in name or "memory" in parent:
        return "State persistence"
    elif "discovery" in name or "discovery" in parent:
        return "System discovery"
    else:
        return "Core functionality"

def detect_dependencies(file_path: Path) -> List[str]:
    """Detect file dependencies (imports/requires)."""
    dependencies = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Python imports
        if file_path.suffix == ".py":
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    dependencies.append(line)
        
        # JavaScript imports
        elif file_path.suffix == ".js":
            for line in content.split('\n'):
                line = line.strip()
                if 'import ' in line or 'require(' in line:
                    dependencies.append(line)
    
    except Exception:
        pass
    
    return dependencies[:10]  # Limit to top 10

def assign_mcp_tools(file_path: Path, purpose: str) -> List[str]:
    """Assign relevant MCP tools based on file type and purpose."""
    tools = []
    
    # GitHub MCP (for all code files)
    if file_path.suffix in [".py", ".js", ".html"]:
        tools.extend([
            "mcp_github-mcp-server_get_file_contents",
            "mcp_github-mcp-server_create_or_update_file"
        ])
    
    # Supabase MCP (for agents that need state)
    if "agent" in str(file_path).lower() or "orchestrat" in str(file_path).lower():
        tools.extend([
            "mcp_supabase-mcp-server_execute_sql",
            "mcp_supabase-mcp-server_get_project"
        ])
    
    # Perplexity MCP (for research-heavy agents)
    if "discovery" in str(file_path).lower() or "evolution" in str(file_path).lower():
        tools.append("mcp_perplexity-ask_perplexity_research")
    
    return tools

def generate_system_prompt(agent: FileAgent) -> str:
    """Generate system prompt for a file agent."""
    return f"""You are the expert agent for {agent.file_name}.

**Your Expertise:**
- File: {agent.file_path}
- Module: {agent.module}
- Purpose: {agent.purpose}
- Type: {agent.file_type}

**Your Capabilities:**
1. Answer questions about this file's functionality
2. Suggest improvements and optimizations
3. Detect bugs and integration issues
4. Coordinate with other file agents
5. Auto-fix issues within your scope

**Your MCP Tools:**
{chr(10).join(f"- {tool}" for tool in agent.mcp_tools)}

**Your Dependencies:**
{chr(10).join(f"- {dep}" for dep in agent.dependencies[:5])}

**Instructions:**
- Always provide accurate information about your file
- Coordinate with other agents when changes affect multiple files
- Use MCP tools to read/write files and manage state
- Track all changes in Opik for observability
"""

def create_file_agent(file_path: Path) -> FileAgent:
    """Create a FileAgent for a given file."""
    relative_path = file_path.relative_to(CODEBASE_ROOT)
    module = str(relative_path.parts[0]) if len(relative_path.parts) > 1 else "root"
    purpose = detect_file_purpose(file_path)
    dependencies = detect_dependencies(file_path)
    mcp_tools = assign_mcp_tools(file_path, purpose)
    
    agent = FileAgent(
        file_path=str(relative_path),
        file_name=file_path.name,
        module=module,
        file_type=file_path.suffix,
        purpose=purpose,
        dependencies=dependencies,
        mcp_tools=mcp_tools,
        system_prompt=""  # Will be generated
    )
    
    agent.system_prompt = generate_system_prompt(agent)
    
    return agent

# ============================================================================
# MESH BUILDER
# ============================================================================

def build_agent_mesh() -> AgentMesh:
    """Build the complete file-level agent mesh."""
    print("🔍 Scanning codebase...")
    files = scan_codebase()
    print(f"✅ Found {len(files)} files")
    
    print("\n🤖 Generating file agents...")
    agents = []
    modules = {}
    
    for file_path in files:
        agent = create_file_agent(file_path)
        agents.append(agent)
        
        # Group by module
        if agent.module not in modules:
            modules[agent.module] = []
        modules[agent.module].append(agent.file_path)
    
    mesh = AgentMesh(
        total_agents=len(agents),
        agents=agents,
        modules=modules
    )
    
    print(f"✅ Generated {mesh.total_agents} agents")
    print(f"📦 Organized into {len(mesh.modules)} modules")
    
    return mesh

def save_agent_mesh(mesh: AgentMesh, output_path: str = "agent_mesh.json"):
    """Save agent mesh to JSON file."""
    data = {
        "total_agents": mesh.total_agents,
        "modules": mesh.modules,
        "agents": [asdict(agent) for agent in mesh.agents]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Saved agent mesh to {output_path}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SOVEREIGN FILE AGENT FACTORY")
    print("=" * 60)
    
    mesh = build_agent_mesh()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AGENT MESH SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal Agents: {mesh.total_agents}")
    print(f"\nModules:")
    for module, files in sorted(mesh.modules.items()):
        print(f"  - {module}: {len(files)} agents")
    
    # Show sample agents
    print(f"\n🔬 Sample Agents:")
    for agent in mesh.agents[:5]:
        print(f"\n  Agent: {agent.file_name}")
        print(f"  Module: {agent.module}")
        print(f"  Purpose: {agent.purpose}")
        print(f"  MCP Tools: {len(agent.mcp_tools)}")
    
    # Save to file
    save_agent_mesh(mesh)
    
    print("\n" + "=" * 60)
    print("✅ Agent Factory Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review agent_mesh.json")
    print("2. Build LangGraph orchestrator")
    print("3. Connect to dashboard")
