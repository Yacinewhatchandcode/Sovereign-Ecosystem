# Antigravity System - Complete Deployment Guide

## Overview

Complete orchestration system with Discovery Node, Validation Node, and Auto-Remediation.

## Quick Start

### 1. Test Violations (Local)

```bash
# Inject test violations
python3 sovereign-dashboard/inject_test_violations.py

# Run discovery
python3 sovereign-dashboard/discovery_node.py sovereign-dashboard/test_violations

# Validate
python3 sovereign-dashboard/validation_node.py --snapshot sovereign-dashboard/knowledge_store.json

# Generate PR templates
python3 sovereign-dashboard/pr_generator.py sovereign-dashboard/reports/report-*.json
```

### 2. Docker Compose Stack

```bash
# Build and start all services
docker-compose -f docker-compose.antigravity.yml up --build

# Access services
- Discovery Node: http://localhost:4000
- Validation Node: http://localhost:4100
- Mock Agent 1 (UI): http://localhost:3001
- Mock Agent 2 (Backend): http://localhost:3002
- Mock Agent 3 (Security): http://localhost:3003

# View logs
docker-compose -f docker-compose.antigravity.yml logs -f

# Stop
docker-compose -f docker-compose.antigravity.yml down
```

### 3. CI/CD Integration

```yaml
# .github/workflows/antigravity.yml
name: Antigravity Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Discovery
        run: |
          python3 sovereign-dashboard/discovery_node.py .
      
      - name: Run Validation
        run: |
          python3 sovereign-dashboard/validation_node.py \
            --snapshot sovereign-dashboard/knowledge_store.json
      
      - name: Generate PRs (if violations)
        if: failure()
        run: |
          python3 sovereign-dashboard/pr_generator.py \
            sovereign-dashboard/reports/report-*.json \
            --create
```

## Components

### Discovery Node (`discovery_node.py`)
- Queries all registered agents via `AgentCommunicationHub`
- Scans disk using `FeatureScanner`
- Builds canonical knowledge graph
- Pushes snapshots to Validation Node

**Usage:**
```bash
python3 discovery_node.py /path/to/scan \
  --validator http://localhost:4100 \
  --tasks scan index capabilities
```

### Validation Node (`validation_node.py`)
- Receives knowledge snapshots
- Enforces Antigravity Rules (2.2, 2.4, 2.5)
- Detects: dom-mock, api-mock, file-mock, dom-unmapped
- Generates blocker reports with remediation

**Usage:**
```bash
# As server
python3 validation_node.py --port 4100

# CLI mode
python3 validation_node.py --snapshot knowledge_store.json
```

### PR Generator (`pr_generator.py`)
- Reads validation reports  
- Generates PR templates with:
  - Branch names
  - Commit messages
  - Code patches
  - Remediation descriptions

**Usage:**
```bash
python3 pr_generator.py reports/report-xxx.json

# Actually create PRs
python3 pr_generator.py reports/report-xxx.json --create
```

### Mock Agents (`prod_agent.py`)
- Simulates external agents for testing
- Implements agent API contract:
  - `GET /agent/metadata`
  - `POST /agent/scan`
  - `GET /agent/result/:scan_id`

**Usage:**
```bash
AGENT_ID=test-agent AGENT_PORT=3001 python3 prod_agent.py
```

## Antigravity Rules Enforced

| Rule | Description | Detection |
|------|-------------|-----------|
| 2.2 | Zero Mock Tolerance | Scans for `mock`, `fake`, `system_value`, `simulated` keywords |
| 2.4 | DOM Is Law | Checks UI elements have backend connections |
| 2.5 | Fail Loud | Flags missing endpoints, explicit errors required |

## Workflow

```
┌──────────────┐
│ Code Changes │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│ Discovery    │────▶│ AgentComm Hub   │
│ Node         │     │ (13 agents)     │
└──────┬───────┘     └─────────────────┘
       │
       │ Snapshot
       ▼
┌──────────────┐     ┌─────────────────┐
│ Validation   │────▶│ Blocker Report  │
│ Node         │     │ (JSON)          │
└──────┬───────┘     └─────────────────┘
       │
       │ If violations
       ▼
┌──────────────┐     ┌─────────────────┐
│ PR Generator │────▶│ Auto PRs        │
│              │     │ (Git branches)  │
└──────────────┘     └─────────────────┘
```

## Next Steps

1. **Enhance File Scanning**: Add AST parsing for deeper code analysis
2. **Webhook Integration**: Auto-trigger on Git pushes
3. **Dashboard UI**: Visualize violations and trends
4. **AI-Powered Fixes**: Use LLM to generate actual code patches
5. **Multi-Repo Support**: Scan entire organization

## Files Created

- `discovery_node.py` - Agent orchestrator
- `validation_node.py` - Antigravity enforcer
- `pr_generator.py` - Auto-remediation
- `inject_test_violations.py` - Test data
- `prod_agent.py` - Mock agent server
- `docker-compose.antigravity.yml` - Full stack
- `Dockerfile.discovery` - Discovery container
- `Dockerfile.validator` - Validator container
- `Dockerfile.prod_agent` - Mock agent container
