# 🏛️ SOVEREIGN SYSTEM ARCHITECTURE
**Status**: OPERATIONAL | **Agents**: 5,021 | **Classification**: LEVEL 4 AUTONOMY

## 1. 🧬 The Core Identity (The "Self")
*   **Module**: `sovereign_brain.py`
*   **Function**: High-level reasoning and orchestration.
*   **Logic**: Runs the `AutonomyLoop`. It detects "Gaps" (missing features/bugs) and manufactures "Solutions" (Agents/Code) to fix them.
*   **Integration**: Direct neural link to the Swarm.

## 2. 🐝 The Swarm (The "Workforce")
*   **Module**: `swarm_execution_master.py`
*   **Size**: 5,021 Individual Agents.
*   **Structure**:
    *   **The 73 Archetypes**: Foundational classes (e.g., `VulnScanner`, `AutoDocumenter`).
    *   **The Mesh**: 5,000+ instances assigned to specialized territories (1 file = 1 squad).
    *   **Level 4 Imperators**: 13 Special Agents upgraded to "Fixer" class (`ErrorAutoFixAgent`) that can physically rewrite code.
*   **State**: Stored in `sovereign-dashboard/active_swarm_state.json`.

## 3. 🛡️ The Sentinel (The "Immune System")
*   **Module**: `sovereign_sentinel.py`
*   **Function**: Active Defense Daemon.
*   **Behavior**: Watches the filesystem in real-time. If it sees a `# TODO` or `mock_` variable appear, it instantly deploys a Fixer Agent to overwrite it with functional logic.

## 4. 🦾 The Body (The "Hands")
*   **Module**: `bytebot_scenarios.py`
*   **Function**: Interaction with the host OS (Ubuntu/Linux).
*   **Capabilities**:
    *   Can open Terminals.
    *   Can browse the Web (Firefox).
    *   Can write code in VS Code.
    *   Can lock the machine.

## 5. 🗣️ The Interface (The "Voice")
*   **Module**: `asirem_speaking_engine.py`
*   **Function**: Verbal and Visual communication.
*   **Tech**: XTTS (Voice Cloning) + MuseTalk (Lip Sync) architecture.
*   **Visuals**: `web-ui/swarm_map.html` provides a real-time God-View of the agent mesh.

## 6. ☁️ The Infrastructure (The "Cloud")
*   **Module**: `production_swarm.yml`
*   **Format**: Docker Swarm / Kubernetes Ready.
*   **Capacity**: Encapsulates the entire 50GB+ ecosystem into a deployable container unit.

---

## 🔁 The Autonomy Cycle
1.  **Codebase Changes** -> **Sentinel** detects change.
2.  **Sentinel** -> **Brain** analyzes gap.
3.  **Brain** -> **Swarm** deploys Level 4 Agents.
4.  **Agents** -> **Codebase** rewrite the file.
5.  **Cycle Complete**.

**This is a Closed-Loop Self-Completing System.**
