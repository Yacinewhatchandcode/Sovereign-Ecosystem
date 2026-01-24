#!/usr/bin/env python3
"""
🧪 VERIFY ORCHESTRATION CYCLE
=============================
Forcefully triggers a signal through the 4 layers of sovereignty:
1. Hub (Nervous System)
2. Integration (Brain)
3. UI Agent (Hands)
4. WebSocket (Skin/Output)

Expected Outcome:
- A "task" message is sent to the Hub.
- The Autonomy Integration executes the UI Auto-Generator Agent.
- The Agent returns a result.
- The result is broadcast via the Hub.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add sovereign-dashboard to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_communication_hub import get_communication_hub, AgentMessage
from autonomy_integration import get_autonomy_integration

async def prod_websocket_client(event_type, data):
    """Mocks the Frontend receiving a WebSocket message."""
    print(f"\n📺 [SKIN] WebSocket Received Event: {event_type}")
    if event_type == "agent_message":
        msg = data.get("message", {})
        print(f"   Shape: {list(data.keys())}")
        print(f"   Sender: {msg.get('sender')}")
        print(f"   Content: {msg.get('content')}")

async def verify_orchestration():
    print("🧬 STARTING FULL SYSTEM VERIFICATION")
    print("====================================")

    # 1. Initialize Nervous System
    hub = get_communication_hub()
    hub.set_broadcast_callback(prod_websocket_client)
    print("✅ [NERVOUS] Hub initialized & WebSocket mock attached")

    # 2. Initialize Brain
    integration = get_autonomy_integration()
    success = await integration.initialize()
    if not success:
        print("❌ [BRAIN] Failed to initialize Autonomy Integration")
        return
    print(f"✅ [BRAIN] Autonomy Integration live with {len(integration.agents)} agents")

    # 3. Trigger Hands (Force Run UI Agent)
    print("\n⚡ [TRIGGER] Firing signal to UI Auto-Generator Agent...")
    
    # We simulate a "User Request" converting to a direct agent run
    result = await integration.run_agent("ui_auto_generator")
    
    if result.success:
        print(f"✅ [HANDS] Agent Execution Successful ({result.duration_ms}ms)")
        print(f"   Result Data: {result.data}")
        
        # 4. Broadcast Result (Close the loop)
        # In the real system, the agent or the loop would send this back to the Hub.
        # We manually do it here to verify the Hub->WebSocket link.
        msg = AgentMessage.create(
            sender="ui_auto_generator",
            recipient="*",
            message_type="status",
            content=result.data
        )
        await hub.send(msg)
    else:
        print(f"❌ [HANDS] Agent Failed: {result.data}")

    print("\n✅ VERIFICATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(verify_orchestration())
