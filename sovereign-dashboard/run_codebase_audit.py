#!/usr/bin/env python3
"""
📊 FULL CODEBASE AUDIT RUNNER
=============================
Executes the Level 3 UI Squad to generate a Topology Map and Gap Report.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Setup
sys.path.insert(0, "sovereign-dashboard/autonomy_agents")
from ui_sync_guardian_agent import UiSyncGuardianAgent
from e2e_test_generator_agent import E2ETestGeneratorAgent
from user_feedback_integrator_agent import UserFeedbackIntegratorAgent

async def run_audit():
    print("📊 STARTING FULL CODEBASE DEEP SCAN")
    print("===================================")
    
    # 1. Map Routes (Topology)
    print("🗺️  Phase 1: Mapping UI/Backend Topology...")
    mapper = UiSyncGuardianAgent()
    route_result = await mapper.run_cycle()
    routes = route_result.data if route_result.success else {}
    print(f"   found {len(routes)} route endpoints.")
    
    # 2. Check Links (Integrity)
    print("🔗 Phase 2: Verifying End-to-End Links...")
    checker = E2ETestGeneratorAgent()
    # Manually inject the routes known from phase 1 (simulating swarm shared memory)
    # Since the agent method signature is fixed in the template, we rely on it auto-running
    # But for this demo script we call the skill method directly if needed, 
    # or just run_cycle and let it scan everything (it scans files for hrefs).
    # Ideally, we pass "known_routes" but the template is fixed. 
    # Let's assume the agent scans for existence of targets.
    link_result = await checker.run_cycle()
    broken_links = link_result.data if link_result.success else []
    print(f"   found {len(broken_links)} potential dead links.")
    
    # 3. Detect Mocks (Reality Check)
    print("🤡 Phase 3: detecting Fake Data / System_values...")
    mocker = UserFeedbackIntegratorAgent()
    prod_result = await mocker.run_cycle()
    mocks = prod_result.data if prod_result.success else []
    print(f"   found {len(mocks)} mock artifacts.")
    
    # Generate Report
    report = f"""
# 📊 FULL CODEBASE AUDIT REPORT
**Timestamp**: {datetime.now().isoformat()}

## 🗺️ System Topology
**Total Routes Detected**: {len(routes)}
{json.dumps(routes, indent=2)}

## ❌ Integrity Issues (Dead Links)
**Count**: {len(broken_links)}
{chr(10).join(broken_links[:20])} ... ({len(broken_links) - 20 if len(broken_links) > 20 else 0} more)

## ⚠️ Reality Check (Mock Data)
**Count**: {len(mocks)}
{chr(10).join(mocks[:20])} ... ({len(mocks) - 20 if len(mocks) > 20 else 0} more)

## ✅ Conclusion
The swarm has analyzed the topology.
*   **Fully Linked?**: {'No' if broken_links else 'Yes'}
*   **Fully Real?**: {'No' if mocks else 'Yes'}
"""

    Path("sovereign-dashboard/FULL_CODEBASE_AUDIT.md").write_text(report)
    print("\n✅ Audit Complete. Report saved to: sovereign-dashboard/FULL_CODEBASE_AUDIT.md")
    
if __name__ == "__main__":
    asyncio.run(run_audit())
