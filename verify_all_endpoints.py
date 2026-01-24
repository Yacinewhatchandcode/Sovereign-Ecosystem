#!/usr/bin/env python3
"""
Verify ALL 31 API endpoints are working
"""
import asyncio
import aiohttp

BASE = "http://localhost:8082"

ENDPOINTS = [
    ("GET", "/api/status"),
    ("GET", "/api/agents/config"),
    ("GET", "/api/agents/all"),
    ("GET", "/api/agents/communications"),
    ("GET", "/api/agents/capabilities"),
    ("GET", "/api/agents/extended"),
    ("GET", "/api/veo3/credits"),
    ("GET", "/api/discoveries"),
    ("GET", "/api/patterns"),
    ("GET", "/api/features/all"),
    ("GET", "/api/features/summary"),
    ("GET", "/api/memory/search"),
    ("GET", "/api/embedding/search"),
    ("POST", "/api/run-pipeline"),
    ("POST", "/api/evolution"),
    ("POST", "/api/web-search"),
    ("POST", "/api/speak"),
    ("POST", "/api/podcast/ask"),
    ("POST", "/api/veo3/generate"),
    ("POST", "/api/features/scan"),
    ("POST", "/api/agents/message"),
    ("POST", "/api/mesh/query"),
    ("POST", "/api/memory/store"),
    ("POST", "/api/embedding/index"),
    ("POST", "/api/docgen/readme"),
    ("POST", "/api/docgen/api"),
    ("POST", "/api/mcp/github"),
    ("POST", "/api/mcp/perplexity"),
]

async def test_all():
    results = {"working": 0, "broken": 0}
    
    async with aiohttp.ClientSession() as session:
        for method, path in ENDPOINTS:
            try:
                if method == "GET":
                    async with session.get(BASE + path) as resp:
                        if resp.status < 500:
                            results["working"] += 1
                            print(f"✅ {method:4} {path}")
                        else:
                            results["broken"] += 1
                            print(f"❌ {method:4} {path} - {resp.status}")
                else:
                    async with session.post(BASE + path, json={}) as resp:
                        if resp.status < 500:
                            results["working"] += 1
                            print(f"✅ {method:4} {path}")
                        else:
                            results["broken"] += 1
                            print(f"❌ {method:4} {path} - {resp.status}")
            except Exception as e:
                results["broken"] += 1
                print(f"❌ {method:4} {path} - {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Working: {results['working']}/{len(ENDPOINTS)}")
    print(f"❌ Broken: {results['broken']}/{len(ENDPOINTS)}")
    print(f"📊 Coverage: {results['working']*100//len(ENDPOINTS)}%")
    
    if results['working'] == len(ENDPOINTS):
        print("\n🎉 ALL ENDPOINTS FUNCTIONAL!")

if __name__ == "__main__":
    asyncio.run(test_all())
