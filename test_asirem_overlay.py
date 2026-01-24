
import asyncio
import os
import sys
from real_agent_system import RealMultiAgentOrchestrator
from bytebot_agent_bridge import ByteBotAgentBridge

async def test_overlay():
    print("🧬 Testing aSiReM ByteBot Overlay...")
    
    # Initialize components
    bridge = ByteBotAgentBridge()
    if not await bridge.check_connection():
        print("❌ ByteBot not connected. Start it first.")
        return

    orchestrator = RealMultiAgentOrchestrator()
    # Wait for async init
    await asyncio.sleep(2)
    
    # Trigger a state change
    print("🎨 Changing state to ANALYZING...")
    await orchestrator.asirem.set_state("analyzing", "I am now analyzing your sovereign environment.")
    
    # Wait for overlay to apply
    await asyncio.sleep(5)
    
    # Capture screenshot to verify
    print("📸 Capturing ByteBot screenshot...")
    screenshot_path = await bridge.capture_screenshot("test_overlay")
    
    if screenshot_path:
        print(f"✅ Screenshot saved to: {screenshot_path}")
        print("Please check the screenshot to verify the aSiReM avatar and speech bubble overlays.")
    else:
        print("❌ Screenshot failed.")

if __name__ == "__main__":
    asyncio.run(test_overlay())
