# AZIREM Orchestration Zone

This zone contains the **Master Orchestrator** that coordinates all agents.

## Purpose

- **Read** frozen inventory and registry
- **Route** tasks to appropriate agents
- **Coordinate** multi-agent workflows
- **Report** execution results

## Structure

```
orchestration/
├── master_orchestrator.py  # Main orchestration engine
├── workflow_engine.py      # LangGraph workflow definitions
├── task_router.py          # Task-to-agent routing logic
└── execution_log/          # Execution audit trail
```

## Rule

**Orchestrate only after inventory is frozen.** Never call agents before discovery is complete.
