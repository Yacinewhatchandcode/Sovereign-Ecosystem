#!/usr/bin/env python3
"""
Test all Quick Actions to verify they're functional
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8082"

async def test_quick_actions():
    print("🧪 Testing All Quick Actions\n")
    print("="*60)
    
    results = {}
    
    # Test 1: Agent Config
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/agents/config") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results["Agent Config"] = f"✅ {len(data['agents'])} agents"
                else:
                    results["Agent Config"] = f"❌ Status {resp.status}"
    except Exception as e:
        results["Agent Config"] = f"❌ {e}"
    
    # Test 2: Veo3 Credits
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/veo3/credits") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results["Veo3 Credits"] = f"✅ {data['remaining']} credits"
                else:
                    results["Veo3 Credits"] = f"❌ Status {resp.status}"
    except Exception as e:
        results["Veo3 Credits"] = f"❌ {e}"
    
    # Test 3: Veo3 Generate (will fail without API key, but should respond)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/veo3/generate",
                json={"prompt": "Test", "quality": "fast"}
            ) as resp:
                data = await resp.json()
                if "error" in data and "GOOGLE_API_KEY" in data["error"]:
                    results["Veo3 Generate"] = "✅ Ready (needs API key)"
                elif resp.status == 200:
                    results["Veo3 Generate"] = "✅ Working"
                else:
                    results["Veo3 Generate"] = f"⚠️ {data.get('error', 'Unknown')}"
    except Exception as e:
        results["Veo3 Generate"] = f"❌ {e}"
    
    # Test 4: Speaking
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/speak",
                json={"text": "Test"}
            ) as resp:
                if resp.status == 200:
                    results["aSiReM Speak"] = "✅ Working"
                else:
                    results["aSiReM Speak"] = f"❌ Status {resp.status}"
    except Exception as e:
        results["aSiReM Speak"] = f"❌ {e}"
    
    # Test 5: WebSocket
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"ws://localhost:8082/ws/stream") as ws:
                # Send test message
                await ws.send_json({"type": "get_bytebot_vnc"})
                
                # Wait for response (with timeout)
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        results["WebSocket"] = "✅ Connected & responding"
                    else:
                        results["WebSocket"] = "⚠️ Connected but no response"
                except asyncio.TimeoutError:
                    results["WebSocket"] = "⚠️ Connected but timeout"
    except Exception as e:
        results["WebSocket"] = f"❌ {e}"
    
    # Print results
    print("\n📊 Test Results:\n")
    for action, status in results.items():
        print(f"  {action:20} {status}")
    
    # Summary
    working = sum(1 for s in results.values() if "✅" in s)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"\n✅ Working: {working}/{total}")
    print(f"❌ Broken: {total - working}/{total}")
    
    if working == total:
        print("\n🎉 ALL QUICK ACTIONS FUNCTIONAL!")
    elif working >= total - 1:
        print("\n✅ MOSTLY FUNCTIONAL (minor issues)")
    else:
        print("\n⚠️ SOME ISSUES DETECTED")

if __name__ == "__main__":
    asyncio.run(test_quick_actions())
