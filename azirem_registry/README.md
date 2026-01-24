# AZIREM Registry Zone

This zone contains the **Master Registry** that indexes all discovered agents, tools, and resources.

## Purpose

- **Index** all agents discovered by the scanner
- **Track** agent capabilities, locations, and states  
- **Freeze** the registry as a source of truth

## Structure

```
registry/
├── agent_registry.json     # Frozen agent manifest
├── tool_registry.json      # Frozen tool manifest  
├── resource_registry.json  # Frozen resource manifest
└── registry_manager.py     # Registry management (read after freeze)
```

## Rule

**Registry is frozen after discovery.** Orchestrator reads from frozen registry only.
