#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE SYSTEM TEST
Tests all features of the aSiReM Sovereign System v14.0
"""

import asyncio
import aiohttp
import json
from pathlib import Path

BASE_URL = "http://localhost:8082"

class SystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    async def test(self, name: str, test_func):
        """Run a single test"""
        print(f"\n🧪 Testing: {name}")
        try:
            await test_func()
            print(f"   ✅ PASSED")
            self.passed += 1
            self.results.append((name, "PASSED", None))
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            self.failed += 1
            self.results.append((name, "FAILED", str(e)))
    
    async def test_backend_running(self):
        """Test if backend is accessible"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/status") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert "status" in data
    
    async def test_dashboard_loads(self):
        """Test if dashboard HTML loads"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/dashboard") as resp:
                assert resp.status == 200
                text = await resp.text()
                assert "AZIREM" in text or "Sovereign" in text
    
    async def test_gateway_loads(self):
        """Test if gateway loads"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as resp:
                assert resp.status == 200
                text = await resp.text()
                assert "aSiReM" in text or "SOVEREIGN" in text
    
    async def test_api_patterns(self):
        """Test knowledge graph API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/patterns") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert "knowledge_graph" in data
    
    async def test_api_discoveries(self):
        """Test discoveries API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/discoveries") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert "total" in data
    
    async def test_agents_all(self):
        """Test agents list API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/agents/all") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert isinstance(data, list) or isinstance(data, dict)
    
    async def test_podcast_message(self):
        """Test podcast text message API"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "question": "Hello, this is a test",
                "use_voice": False
            }
            # Updated to match actual backend implementation (from grep results)
            async with session.post(f"{BASE_URL}/api/podcast/ask", json=payload) as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status}"
                data = await resp.json()
                assert "response" in data
    
    async def test_static_files(self):
        """Test if static files are served"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/static/sovereign_core.css") as resp:
                assert resp.status == 200
                text = await resp.text()
                assert "font" in text.lower() or "color" in text.lower()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🧪 aSiReM SYSTEM TEST SUITE")
        print("=" * 60)
        
        await self.test("Backend Running", self.test_backend_running)
        await self.test("Dashboard Loads", self.test_dashboard_loads)
        await self.test("Gateway Loads", self.test_gateway_loads)
        await self.test("API: Patterns", self.test_api_patterns)
        await self.test("API: Discoveries", self.test_api_discoveries)
        await self.test("API: Agents List", self.test_agents_all)
        await self.test("API: Podcast Message", self.test_podcast_message)
        await self.test("Static Files", self.test_static_files)
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        
        if self.failed > 0:
            print("\n❌ Failed Tests:")
            for name, status, error in self.results:
                if status == "FAILED":
                    print(f"   - {name}: {error}")
        
        print("\n" + "=" * 60)
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL!")
        else:
            print("⚠️ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("=" * 60)

async def main():
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
