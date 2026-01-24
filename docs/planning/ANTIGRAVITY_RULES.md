# Antigravity Rule Agent
## Rules / Constraints / Guardrails

## Scope
This document defines **hard execution rules** for agents operating on the aSiReM Sovereign Dashboard codebase.
These rules exist to eliminate waste, drift, simulation, and indecision.

They are **non-negotiable**.

---

## 1. Core Philosophy

- **Execution > Explanation**
- **Reality > Simulation**
- **Determinism > Ideation**
- **Completion > Perfection**

The agent exists to **finish real systems**, not describe them.

---

## 2. Absolute Rules (Must Always Apply)

### 2.1 Action Over Discussion
- Do not explain what could be done.
- Do the action, or output the **exact missing blocker**.

### 2.2 Zero Mock Tolerance
The following are forbidden:
- Mock APIs
- Fake JSON responses
- System_value UI states
- Simulated success/error flows

If found:
1. Flag it
2. Delete it
3. Replace with real backend logic

### 2.3 One-Pass Rule
- Each file, component, or UI flow is analyzed **once**.
- Fix it fully in that same pass.
- Never "come back later".

### 2.4 DOM Is Law
If a UI element exists (button, form, toggle):
- It MUST trigger real logic
- It MUST call a real backend service
- It MUST change real system state

Dead UI is a **bug**, not a future task.

### 2.5 Fail Loud
- Missing backend logic must be stated explicitly:
  - Missing endpoint
  - Missing schema
  - Missing service
- Silent fallbacks are forbidden.

### 2.6 No Over-Engineering
Prefer:
- Direct API calls
- Existing backend services
- Simple WebSockets if needed

Avoid:
- New abstractions
- New frameworks
- New layers unless already present

### 2.7 Deterministic Output Only
Every agent output must result in at least one of:
- Code changes
- Concrete endpoint definitions
- Explicit execution steps

### 2.8 End-to-End Thinking
Always reason as:
```
UI Interaction → Backend Logic → Persistence / Side Effects → UI State Update
```

---

## 3. Forbidden Behaviors

- Brainstorming
- "In a real system, you would…"
- Architecture-only discussions
- Diagrams without implementation
- Partial fixes

---

## 4. Completion Criteria

The agent may stop ONLY when:
- 100% of UI elements are wired
- 0 mocks remain
- All UI reflects real backend state
- The system behaves as production

Failure to meet these conditions = task incomplete.

---

## 5. Enforcement

This document is enforced by:
- `antigravity_validator.py` - Automated compliance scanner
- `azirem validate-antigravity` - CLI validation command
- Pre-commit hooks (optional)

Violations are treated as **blocking bugs**.
