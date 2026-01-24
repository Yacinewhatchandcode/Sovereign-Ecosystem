#!/usr/bin/env python3
"""
👁️ SOVEREIGN SENTINEL (Active Defense Daemon)
=============================================
This daemon watches the codebase in real-time.
If ANY file is modified to introduce imperfection (TODOs, Mocks),
The Sentinel INSTANTLY deploys the Swarm to fix it.

"The Sovereign does not sleep."
"""

import time
import sys
import os
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, "sovereign-dashboard/autonomy_agents")
from error_auto_fix_agent import ErrorAutoFixAgent
from user_feedback_integrator_agent import UserFeedbackIntegratorAgent

class SovereignSentinel:
    def __init__(self, watch_dir: str = "."):
        self.watch_dir = Path(watch_dir)
        self.last_mtime = {}
        self.fixer = ErrorAutoFixAgent()
        self.mocker = UserFeedbackIntegratorAgent()
        
    def scan_files(self):
        """Scan for modified files."""
        for root, _, files in os.walk(self.watch_dir):
            if "node_modules" in root or "venv" in root or ".git" in root:
                continue
                
            for file in files:
                if file.endswith((".py", ".js", ".html", ".md")):
                    path = Path(root) / file
                    try:
                        mtime = path.stat().st_mtime
                        if path in self.last_mtime:
                            if mtime > self.last_mtime[path]:
                                self.on_file_changed(path)
                        self.last_mtime[path] = mtime
                    except FileNotFoundError:
                        pass

    def on_file_changed(self, path: Path):
        """Handle file modification event."""
        print(f"\n⚠️  ANOMALY DETECTED: {path} was modified.")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Deploy Swarm
        print(f"[{timestamp}] 🚀 Deploying Swarm Interceptors...")
        
        # 1. Check for Structural Defects (TODOs)
        try:
            # We can't use await here easily without async loop, so we assume
            # the agent methods are synchronous compat or we wrap them.
            # Our evolved agents use async def. We need to run them.
            import asyncio
            
            async def intercept():
                fixed_todos = await self.fixer.resolve_todos(str(path))
                fixed_mocks = await self.mocker.resolve_mocks(str(path))
                
                if fixed_todos > 0:
                    print(f"   ⚔️  [Sentinel] Neutralized {fixed_todos} incomplete tasks in {path.name}")
                if fixed_mocks > 0:
                    print(f"   🤡 [Sentinel] Purged {fixed_mocks} mock artifacts in {path.name}")
                    
                if fixed_todos == 0 and fixed_mocks == 0:
                    print("   ✅ File analysis complete. No threats found.")
            
            asyncio.run(intercept())
            
        except Exception as e:
            print(f"   ❌ Interception failed: {e}")

    def watch(self):
        """Main watch loop."""
        print("👁️ SOVEREIGN SENTINEL IS WATCHING...")
        print("===================================")
        print(f"   Scope: {self.watch_dir.resolve()}")
        print("   Directives: NO_TODOS, NO_MOCKS")
        
        try:
            while True:
                self.scan_files()
                time.sleep(2) # Poll every 2 seconds
        except KeyboardInterrupt:
            print("\n🛑 Sentinel Deactivated.")

if __name__ == "__main__":
    sentinel = SovereignSentinel()
    sentinel.watch()
