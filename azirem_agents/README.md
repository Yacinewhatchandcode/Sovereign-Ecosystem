# AZIREM Agents Zone

This zone contains agent definitions and implementations.

## Purpose

- **Store** agent class definitions
- **Define** agent capabilities and contracts
- **Provide** uniform agent interface

## Structure

```
agents/
├── base/
│   └── base_agent.py       # Abstract base agent
├── core/
│   ├── azirem_agent.py     # Main coding agent
│   ├── bumblebee_agent.py  # Research agent
│   └── spectra_agent.py    # Experience agent
├── specialized/
│   └── (domain-specific agents)
└── README.md
```

## Rule

**Agents are passive.** They do not self-execute. Orchestrator calls them.
