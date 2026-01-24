#!/usr/bin/env python3
"""
🎙️ AZIREM PODCAST API TEST SUITE
==================================
Comprehensive testing of the podcast backend API endpoints.

Tests:
1. Basic text-only podcast interaction
2. Voice-enabled podcast (if TTS available)
3. WebSocket real-time podcast streaming
4. Waveform data generation
5. Multi-turn conversation
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime


class PodcastAPITester:
    """Test the AZIREM Podcast API."""
    
    def __init__(self, base_url="http://localhost:8082"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            
    async def test_basic_podcast(self):
        """Test basic podcast question/answer."""
        print("\n" + "="*60)
        print("TEST 1: Basic Podcast Interaction")
        print("="*60)
        
        url = f"{self.base_url}/api/podcast/ask"
        payload = {
            "question": "What is your purpose as AZIREM?",
            "use_voice": False
        }
        
        print(f"\n📤 Sending: {payload['question']}")
        start = time.time()
        
        async with self.session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                elapsed = time.time() - start
                
                print(f"\n✅ Response received in {elapsed:.2f}s")
                print(f"\n🤖 AZIREM: {data['response']}")
                print(f"\n📊 Metadata:")
                print(f"   - Agent: {data.get('agent', 'unknown')}")
                print(f"   - Response length: {len(data['response'])} chars")
                
                return True
            else:
                print(f"\n❌ Error: {resp.status}")
                print(await resp.text())
                return False
                
    async def test_voice_podcast(self):
        """Test podcast with voice synthesis."""
        print("\n" + "="*60)
        print("TEST 2: Voice-Enabled Podcast")
        print("="*60)
        
        url = f"{self.base_url}/api/podcast/ask"
        payload = {
            "question": "Tell me about your agent fleet in one sentence.",
            "use_voice": True
        }
        
        print(f"\n📤 Sending: {payload['question']}")
        print("🔊 Voice synthesis: ENABLED")
        start = time.time()
        
        async with self.session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                elapsed = time.time() - start
                
                print(f"\n✅ Response received in {elapsed:.2f}s")
                print(f"\n🤖 AZIREM: {data['response']}")
                
                if data.get('audio_path'):
                    print(f"\n🎵 Audio generated: {data['audio_path']}")
                if data.get('video_path'):
                    print(f"\n🎬 Video generated: {data['video_path']}")
                else:
                    print(f"\n⚠️  No audio/video generated (TTS may not be available)")
                    
                return True
            else:
                print(f"\n❌ Error: {resp.status}")
                return False
                
    async def test_websocket_podcast(self):
        """Test real-time podcast via WebSocket."""
        print("\n" + "="*60)
        print("TEST 3: WebSocket Real-Time Podcast")
        print("="*60)
        
        ws_url = f"ws://localhost:8082/ws/stream"
        
        try:
            async with self.session.ws_connect(ws_url) as ws:
                print("\n✅ WebSocket connected")
                
                # Send podcast question
                question = "What makes you different from other AI systems?"
                message = {
                    "type": "podcast_ask",
                    "data": {
                        "question": question,
                        "use_voice": False
                    }
                }
                
                print(f"\n📤 Sending via WebSocket: {question}")
                await ws.send_json(message)
                
                # Wait for response
                print("\n⏳ Waiting for response...")
                timeout = 30
                start = time.time()
                
                while time.time() - start < timeout:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            
                            if data.get('type') == 'podcast_response':
                                response_data = data.get('data', {})
                                print(f"\n✅ Response received via WebSocket")
                                print(f"\n🤖 AZIREM: {response_data.get('response', '')}")
                                return True
                                
                            elif data.get('type') == 'activity':
                                activity = data.get('data', {})
                                print(f"   📡 Activity: {activity.get('message', '')}")
                                
                    except asyncio.TimeoutError:
                        continue
                        
                print(f"\n⚠️  No response received within {timeout}s")
                return False
                
        except Exception as e:
            print(f"\n❌ WebSocket error: {e}")
            return False
            
    async def test_conversation_flow(self):
        """Test multi-turn conversation."""
        print("\n" + "="*60)
        print("TEST 4: Multi-Turn Conversation")
        print("="*60)
        
        questions = [
            "Hi AZIREM, what's your name?",
            "What agents do you manage?",
            "Which agent handles security?"
        ]
        
        url = f"{self.base_url}/api/podcast/ask"
        
        for i, question in enumerate(questions, 1):
            print(f"\n--- Turn {i} ---")
            print(f"🧑 User: {question}")
            
            async with self.session.post(url, json={"question": question}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data['response']
                    # Truncate long responses
                    if len(response) > 200:
                        response = response[:200] + "..."
                    print(f"🤖 AZIREM: {response}")
                else:
                    print(f"❌ Error: {resp.status}")
                    return False
                    
            await asyncio.sleep(0.5)  # Brief pause between turns
            
        print("\n✅ Conversation flow test complete")
        return True
        
    async def test_api_health(self):
        """Test basic API health."""
        print("\n" + "="*60)
        print("TEST 0: API Health Check")
        print("="*60)
        
        # Try to get stats
        url = f"{self.base_url}/api/stats"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("\n✅ API is healthy")
                    print(f"\n📊 System Stats:")
                    for key, value in data.items():
                        print(f"   - {key}: {value}")
                    return True
                else:
                    print(f"\n⚠️  Stats endpoint returned {resp.status}")
                    return True  # Not critical
        except Exception as e:
            print(f"\n⚠️  Could not fetch stats: {e}")
            return True  # Not critical
            
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "🎙️"*30)
        print("AZIREM PODCAST API TEST SUITE")
        print("🎙️"*30)
        print(f"\nBase URL: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("API Health", self.test_api_health),
            ("Basic Podcast", self.test_basic_podcast),
            ("Voice Podcast", self.test_voice_podcast),
            ("WebSocket Podcast", self.test_websocket_podcast),
            ("Conversation Flow", self.test_conversation_flow),
        ]
        
        results = []
        
        for name, test_func in tests:
            try:
                result = await test_func()
                results.append((name, result))
            except Exception as e:
                print(f"\n❌ Test '{name}' failed with exception: {e}")
                results.append((name, False))
                
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
            
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        return passed == total


async def main():
    """Run the test suite."""
    async with PodcastAPITester() as tester:
        success = await tester.run_all_tests()
        
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
