# Cold Azirem Multi-Agent Ecosystem

A sophisticated multi-agent system with 10 specialized AI agents powered by local Ollama models.

## 🎯 Features

- **10 Specialized Agents**: Architecture, PM, BA, Frontend, Backend, DevOps, Database, QA, Security, Tech Writer
- **Local LLM Execution**: All agents run on your local Ollama models (no external API calls)
- **Tool Integration**: 13+ tools including web search, code generation, GitHub/Supabase MCP
- **Parallel Execution**: Run multiple agents concurrently
- **Inter-Agent Communication**: Event-driven message bus for agent collaboration
- **Self-Reflection**: Agents can critique and improve their own outputs
- **Comprehensive Metrics**: Track performance, success rates, and response times

## 📁 Project Structure

```
cold_azirem/
├── agents/
│   ├── base_agent.py           # Base agent class
│   └── specialized_agents.py   # Specialized agent implementations
├── orchestration/
│   └── orchestrator.py         # Multi-agent orchestration
├── tools/
│   └── agent_tools.py          # Tool implementations
├── config/
│   └── agent_config.py         # Agent configurations
└── demo.py                     # Full demonstration script
```

## 🚀 Quick Start

### Prerequisites

1. **Ollama** installed and running
2. **Python 3.10+**
3. Required models (you already have these):
   - deepseek-r1:7b
   - phi3:14b
   - llama3.1:8b
   - qwen3:8b
   - gemma2:2b

### Installation

```bash
cd /Users/yacinebenhamou/aSiReM/cold_azirem

# Install dependencies
pip install httpx asyncio

# Run the demo
python demo.py
```

## 🎭 Agent Roster

| Agent | Model | Specialty | Tools |
|-------|-------|-----------|-------|
| **ArchitectureDev** | deepseek-r1:7b | System design, patterns | web_search, code_analysis, diagram_gen, github_mcp, supabase_mcp |
| **ProductManager** | llama3.1:8b | Roadmap, prioritization | web_search, analytics, documentation |
| **BusinessAnalyst** | llama3.1:8b | Requirements, stakeholders | web_search, documentation, analytics |
| **FrontendDev** | phi3:14b | React, Next.js, UI/UX | code_gen, github_mcp, web_search, ui_preview |
| **BackendDev** | phi3:14b | APIs, databases | code_gen, github_mcp, supabase_mcp, web_search |
| **DevOpsEngineer** | phi3:14b | CI/CD, infrastructure | github_mcp, deployment, monitoring, web_search |
| **DatabaseEngineer** | qwen3:8b | Schema, migrations | supabase_mcp, code_gen, web_search |
| **QASpecialist** | qwen3:8b | Testing, automation | code_gen, test_runner, github_mcp, web_search |
| **SecuritySpecialist** | llama3.1:8b | Threat modeling, audits | code_analysis, security_scan, web_search |
| **TechnicalWriter** | gemma2:2b | Documentation, guides | documentation, web_search |

## 📊 Demo Scenarios

The demo script (`demo.py`) showcases:

1. **Agent Initialization**: Initialize all 10 agents
2. **Tool Testing**: Test all tools for each agent
3. **Single Agent Task**: Execute a complex task with one agent
4. **Parallel Execution**: Run 4 agents simultaneously
5. **Agent Collaboration**: Sequential pipeline (PM → Architect → Dev → QA)
6. **Inter-Agent Communication**: Event-driven message bus
7. **Performance Metrics**: Track success rates and response times

## 🔧 Usage Examples

### Single Agent Task

```python
from cold_azirem.orchestration.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
await orchestrator.initialize_agent("ArchitectureDev")

result = await orchestrator.execute_task(
    agent_name="ArchitectureDev",
    task="Design a scalable microservices architecture",
    max_iterations=5
)

print(result['response'])
```

### Parallel Execution

```python
tasks = {
    "ArchitectureDev": "Design the system architecture",
    "FrontendDev": "Create the UI mockup",
    "BackendDev": "Design the API",
    "QASpecialist": "Create test strategy"
}

results = await orchestrator.execute_parallel_tasks(tasks)
```

### Agent Collaboration Pipeline

```python
sequence = ["ProductManager", "ArchitectureDev", "BackendDev", "QASpecialist"]

results = await orchestrator.agent_collaboration(
    task="Build a user authentication system",
    agent_sequence=sequence
)
```

## 🛠️ Available Tools

- **web_search**: Search the web for information
- **code_gen**: Generate code based on description
- **code_analysis**: Analyze code quality/security
- **github_mcp**: GitHub operations (PRs, issues, etc.)
- **supabase_mcp**: Database operations (migrations, queries)
- **documentation**: Generate documentation
- **analytics**: Get analytics data
- **diagram_gen**: Generate architecture diagrams
- **test_runner**: Run tests
- **security_scan**: Perform security scans
- **deployment**: Deploy services
- **monitoring**: Monitor service health
- **ui_preview**: Generate UI component previews

## 📈 Performance Metrics

Each agent tracks:
- Total requests
- Successful requests
- Failed requests
- Tool calls
- Average response time

Access metrics:
```python
status = orchestrator.get_agent_status("ArchitectureDev")
print(status['metrics'])
```

## 🔄 Inter-Agent Communication

Agents communicate via an event-driven message bus:

```python
# Get recent events
events = orchestrator.get_message_bus_log(limit=50)

for event in events:
    print(f"{event['source']} - {event['type']} - {event['timestamp']}")
```

## 🎯 Next Steps

1. **Run the demo**: `python demo.py`
2. **Integrate real tools**: Replace mock tools with actual implementations
3. **Add more agents**: Extend the system with domain-specific agents
4. **Implement RAG**: Add ChromaDB/FAISS for knowledge persistence
5. **Build UI**: Create a dashboard to visualize agent activity

## 📝 Notes

- All tools are currently mocked for demonstration
- Integrate with real MCP servers (GitHub, Supabase) for production
- Add web search integration (Perplexity or similar) for research capabilities
- Implement vector database (ChromaDB/FAISS) for agent memory

## 🌟 Features Coming Soon

- LangGraph integration for advanced workflows
- Self-reflection loops (Reflexion pattern)
- Tree-of-Thought reasoning
- Vector database for persistent memory
- Real-time dashboard
- Production-grade error handling

---

**Built with ❤️ for the Cold Azirem Multi-Agent Ecosystem**
