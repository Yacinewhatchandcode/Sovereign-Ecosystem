#!/usr/bin/env python3
"""
🎬 PODCAST VIDEO API TESTER
============================
Test the complete podcast video generation system:
- User avatar with cloned voice
- AZIREM avatar with anime character
- Real-time MP4 generation
- Video streaming

Usage:
    python3 test_podcast_video_api.py
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def test_podcast_video_generation():
    """Test generating a podcast video with both avatars."""
    print("\n" + "="*60)
    print("🎬 PODCAST VIDEO GENERATION TEST")
    print("="*60)
    
    url = "http://localhost:8082/api/podcast/video"
    
    # Sample conversation
    conversation = [
        {
            "speaker": "user",
            "text": "Hello AZIREM! I'm excited to see our podcast come to life with both of our avatars."
        },
        {
            "speaker": "ai",
            "text": "Hello! I'm thrilled too! As AZIREM, I manage a fleet of 13 specialized agents, each with unique capabilities."
        },
        {
            "speaker": "user",
            "text": "That sounds amazing! Can you tell me more about how they work together?"
        },
        {
            "speaker": "ai",
            "text": "Absolutely! When you trigger an evolution, Scanner analyzes your codebase, Classifier organizes findings, and Evolution synthesizes insights. It's a beautiful symphony of AI collaboration!"
        },
        {
            "speaker": "user",
            "text": "I love that! What makes your system different from other AI frameworks?"
        },
        {
            "speaker": "ai",
            "text": "Great question! Unlike traditional frameworks, we combine strategic orchestration with real-time visual streaming. Each agent has its own video stream, and we use voice cloning for authentic communication."
        }
    ]
    
    payload = {
        "conversation": conversation
    }
    
    print(f"\n📤 Sending conversation with {len(conversation)} segments...")
    print(f"\n💬 Preview:")
    for i, msg in enumerate(conversation[:2], 1):
        speaker_emoji = "🧑" if msg["speaker"] == "user" else "🤖"
        print(f"   {speaker_emoji} {msg['speaker'].upper()}: {msg['text'][:60]}...")
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"\n⏳ Generating video (this may take a few minutes)...")
            start = datetime.now()
            
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    elapsed = (datetime.now() - start).total_seconds()
                    
                    print(f"\n✅ Video generated in {elapsed:.1f}s")
                    print(f"\n📹 Video Details:")
                    print(f"   - Path: {data.get('video_path', 'N/A')}")
                    print(f"   - Segments: {data.get('segments', 0)}")
                    print(f"   - Message: {data.get('message', '')}")
                    
                    # Test streaming
                    video_path = data.get('video_path')
                    if video_path:
                        await test_video_streaming(session, video_path)
                    
                    return True
                else:
                    error_text = await resp.text()
                    print(f"\n❌ Error {resp.status}: {error_text}")
                    return False
                    
        except asyncio.TimeoutError:
            print(f"\n⏱️  Request timed out (video generation takes time)")
            return False
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            return False


async def test_video_streaming(session, video_path):
    """Test streaming the generated video."""
    print(f"\n" + "-"*60)
    print("📡 TESTING VIDEO STREAMING")
    print("-"*60)
    
    url = f"http://localhost:8082/api/podcast/stream?path={video_path}"
    
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                content_type = resp.headers.get('Content-Type', '')
                content_length = resp.headers.get('Content-Length', 'unknown')
                
                print(f"\n✅ Video stream accessible")
                print(f"   - Content-Type: {content_type}")
                print(f"   - Size: {content_length} bytes")
                print(f"   - URL: {url}")
                
                # Read first chunk to verify
                chunk = await resp.content.read(1024)
                if chunk:
                    print(f"   - First chunk: {len(chunk)} bytes")
                    
                return True
            else:
                print(f"\n❌ Streaming failed: {resp.status}")
                return False
                
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        return False


async def test_simple_conversation():
    """Test a simple 2-turn conversation."""
    print("\n" + "="*60)
    print("🎬 SIMPLE CONVERSATION TEST")
    print("="*60)
    
    url = "http://localhost:8082/api/podcast/video"
    
    conversation = [
        {
            "speaker": "user",
            "text": "Hi AZIREM!"
        },
        {
            "speaker": "ai",
            "text": "Hello! I'm AZIREM, your AI orchestrator. How can I help you today?"
        }
    ]
    
    payload = {"conversation": conversation}
    
    print(f"\n📤 Generating simple 2-turn conversation...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"\n✅ Simple video generated")
                    print(f"   - Path: {data.get('video_path', 'N/A')}")
                    return True
                else:
                    print(f"\n❌ Error: {resp.status}")
                    return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False


async def test_default_conversation():
    """Test with no conversation (should use default)."""
    print("\n" + "="*60)
    print("🎬 DEFAULT CONVERSATION TEST")
    print("="*60)
    
    url = "http://localhost:8082/api/podcast/video"
    
    print(f"\n📤 Requesting default conversation...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json={}, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"\n✅ Default video generated")
                    print(f"   - Segments: {data.get('segments', 0)}")
                    return True
                else:
                    print(f"\n❌ Error: {resp.status}")
                    return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False


async def main():
    """Run all tests."""
    print("\n" + "🎬"*30)
    print("PODCAST VIDEO API TEST SUITE")
    print("🎬"*30)
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: http://localhost:8082")
    
    tests = [
        ("Default Conversation", test_default_conversation),
        ("Simple Conversation", test_simple_conversation),
        ("Full Conversation", test_podcast_video_generation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
            results.append((name, False))
        
        # Pause between tests
        await asyncio.sleep(2)
    
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
    
    if passed == total:
        print("\n✅ All tests passed! Podcast video system is working.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
