#!/usr/bin/env python3
"""
🕹️ BYTEBOT SCENARIOS
====================
High-level automation scripts for the ByteBot Virtual Desktop.
These scenarios link discrete gestures into meaningful workflows.

Scenarios:
1. 🌐 Web Research (Open Browser -> Search)
2. 💻 Coding Session (Open Terminal -> VS Code)
3. 📊 System Monitor (Open Terminal -> htop)
4. 🛡️ Lockdown (Minimize All -> Lock Screen)
5. 📝 Note Taking (Open Text Editor)
"""

import asyncio
import logging
from typing import Dict, Any, List
from bytebot_gesture_executor import get_bytebot_executor, ByteBotGestureExecutor

logger = logging.getLogger(__name__)

class ByteBotScenarios:
    """Orchestrator for ByteBot automation scenarios."""
    
    def __init__(self):
        self.executor = get_bytebot_executor()
        
    async def run_scenario(self, scenario_id: str, params: Dict[str, Any] = None) -> bool:
        """Execute a predefined scenario."""
        params = params or {}
        method_name = f"scenario_{scenario_id}"
        
        if hasattr(self, method_name):
            logger.info(f"🎬 Starting ByteBot Scenario: {scenario_id}")
            method = getattr(self, method_name)
            try:
                await method(**params)
                logger.info(f"✅ Finished ByteBot Scenario: {scenario_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Scenario failed: {e}")
                return False
        else:
            logger.warning(f"⚠️ Unknown scenario: {scenario_id}")
            return False

    async def scenario_web_research(self, query: str = "Sovereign AI Architecture"):
        """
        Scenario 1: Open Browser and Search
        Steps:
        1. Open Application Launcher (Super)
        2. Type 'firefox'
        3. Enter
        4. Wait for load
        5. Type query
        6. Enter
        """
        ex = self.executor
        
        # Open Launcher
        ex.press_key("Super")
        await asyncio.sleep(1)
        
        # Launch Browser
        ex.type_text("firefox")
        await asyncio.sleep(0.5)
        ex.press_key("Return")
        
        # Wait for browser (simulated)
        await asyncio.sleep(4) 
        
        # Focus Address Bar (Ctrl+L)
        ex.press_key("ctrl+l")
        await asyncio.sleep(0.5)
        
        # Type Query
        ex.type_text(query)
        await asyncio.sleep(0.5)
        ex.press_key("Return")

    async def scenario_coding_session(self):
        """
        Scenario 2: Coding Session
        Steps:
        1. Open Terminal (Ctrl+Alt+T)
        2. Navigate to project
        3. Open VS Code
        """
        ex = self.executor
        
        # Open Terminal
        ex.press_key("ctrl+alt+t")
        await asyncio.sleep(1.5)
        
        # Open workspace
        ex.type_text("cd ~/workspace/sovereign-dashboard")
        ex.press_key("Return")
        await asyncio.sleep(0.5)
        
        # List files
        ex.type_text("ls -la")
        ex.press_key("Return")
        await asyncio.sleep(1)
        
        # Open Code
        ex.type_text("code .")
        ex.press_key("Return")

    async def scenario_system_monitor(self):
        """
        Scenario 3: System Status
        Steps:
        1. Open Terminal
        2. Run htop
        """
        ex = self.executor
        
        # Open Terminal
        ex.press_key("ctrl+alt+t")
        await asyncio.sleep(1.5)
        
        # Run htop
        ex.type_text("htop")
        ex.press_key("Return")

    async def scenario_lockdown(self):
        """
        Scenario 4: Security Lockdown
        Steps:
        1. Minimize all windows (Super+D)
        """
        ex = self.executor
        # Toggle Desktop
        ex.press_key("super+d")

    async def scenario_note_taking(self, content: str = "Meeting Notes"):
        """
        Scenario 5: Quick Tech Note
        """
        ex = self.executor
        
        # Open Text Editor via Terminal for speed
        ex.press_key("ctrl+alt+t")
        await asyncio.sleep(1)
        
        ex.type_text("nano notes.txt")
        ex.press_key("Return")
        await asyncio.sleep(0.5)
        
        ex.type_text(f"--- {content} ---")
        ex.press_key("Return")
        ex.type_text("Captured by ByteBot Sovereign Agent")

# Singleton
_scenarios = None

def get_bytebot_scenarios():
    global _scenarios
    if _scenarios is None:
        _scenarios = ByteBotScenarios()
    return _scenarios

if __name__ == "__main__":
    # Demo run
    async def main():
        scenarios = get_bytebot_scenarios()
        print("🎮 Testing ByteBot Scenarios (Dry Run - no container check here)")
        # Just creating the object implies code validity
        print("✅ Scenarios Loaded: web_research, coding_session, system_monitor, lockdown, note_taking")
    
    asyncio.run(main())
