# Opik Integration & Agent Evolution Plan

> **Sovereign Observability Upgrade**

## 🎯 Vision
Upgrade the aSiReM multi-agent ecosystem with professional-grade observability using **Opik**. This enables "Black Box" recording for all 13 agents, allowing for deep post-mortem analysis of agent reasoning and automatic evaluation of response quality.

---

## 🏗️ Architecture

1.  **Observability Layer**: Opik (Self-hosted via Docker)
2.  **Instrumentation**: direct SDK integration in `AziremBrain`
3.  **Storage**: Local ClickHouse and MySQL (containers)
4.  **UI**: 
    - Sovereign Dashboard (Live Telemetry)
    - Opik UI (Deep Trace Analysis & Debugging)

---

## 🛠️ Implementation Progress

### Phase 1: Infrastructure (Complete)
- [x] Install Opik Python SDK
- [x] Shallow clone Opik repository for local deployment configuration
- [x] Start Opik services via Docker Compose
  - [x] mc, mysql, zookeeper, redis, clickhouse, minio, backend, frontend, python-backend (Running on port 5173/8080)

### Phase 2: Instrumentation ✅ **COMPLETE**
- [x] Install Opik Python SDK in `venv-speaking` environment
- [x] Add `opik.track` to `azirem_brain.py` with `@track(name="azirem_think")` and `@track(name="ollama_call")`
- [x] Configure `OPIK_URL_OVERRIDE` and `OPIK_PROJECT_NAME` environment variables
- [x] Add trace support to `AgentExecutor` in `ollama_executor.py` with `@track(name="agent_execute")`
- [x] Instrument `real_agent_system.py` to auto-configure Opik on startup
- [x] **VERIFIED**: Traces successfully logging to `asirem-sovereign` project at `http://localhost:5173`

### Phase 3: Dashboard Alignment ✅ **COMPLETE**
- [x] Add "🔍 Traces" button to the Sovereign Dashboard header (opens Opik Console at `http://localhost:5173`)
- [x] Button styled with purple neon theme matching Opik branding
- [x] Map high-level "Evolution" events to Opik trace IDs
- [x] Real-time trace URL logging in console output

### Phase 4: Automated Evaluation (Sovereign Architecture) - Complete
- [x] **Judge Model**: Implemented `SovereignMetric` base class using **Ollama (llama3.1:8b)** for local sovereignty.
- [x] **Metrics**:
  - **Reasoning Depth**: Evaluates `<think>` blocks for logical coherence.
  - **Tool Efficiency**: Scores tool selection accuracy vs user intent.
  - **Hallucination Check**: Verifies output against `scanned_files` context.
- [x] **Implementation Files**:
  - `azirem_evaluation.py`: Core evaluation module with custom Opik metrics.
  - `test_sovereign_evaluation.py`: Integration test demonstrating full workflow.
- [x] **Workflow**: 
  - Evaluation triggered via `evaluate()` function with dataset.
  - Scores logged to Opik Experiments for tracking over time.

---

## 🚀 How to Run

1.  **Start Observability Stack**:
    ```bash
    cd tools/opik/deployment/docker-compose
    docker compose --profile opik up -d
    ```

2.  **Start aSiReM Ecosystem**:
    ```bash
    # Starts dashboard + real_agent_system (now fully traced)
    python azirem_cli.py dashboard
    ```

3.  **Trace Analysis**:
    - **Opik Console**: `http://localhost:5173` (Deep technical traces)
    - **Sovereign Dashboard**: `http://localhost:8080` (High-level visual telemetry)
