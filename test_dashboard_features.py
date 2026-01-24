#!/usr/bin/env python3
"""
Diagnostic script to test each dashboard feature independently
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))

async def test_veo3():
    """Test Veo3 video generation"""
    try:
        from asirem_speaking_engine import Veo3Generator
        gen = Veo3Generator()
        print(f"✅ Veo3Generator: Available (simulated={gen.is_simulated})")
        
        # Try to check credits
        credits = await gen.get_credits()
        print(f"   Credits: {credits}")
        return True
    except Exception as e:
        print(f"❌ Veo3Generator: {e}")
        return False

async def test_speaking():
    """Test speaking engine"""
    try:
        from asirem_speaking_engine import ASiREMSpeakingEngine
        engine = ASiREMSpeakingEngine()
        print(f"✅ Speaking Engine: Available")
        return True
    except Exception as e:
        print(f"❌ Speaking Engine: {e}")
        return False

async def test_bytebot():
    """Test ByteBot integration"""
    try:
        from integrated_visual_operator import IntegratedVisualOperator
        operator = IntegratedVisualOperator()
        vnc_info = await operator.get_bytebot_vnc_embed()
        print(f"✅ ByteBot: Available")
        print(f"   VNC URL: {vnc_info['vnc_url']}")
        return True
    except Exception as e:
        print(f"❌ ByteBot: {e}")
        return False

async def test_scanner():
    """Test feature scanner"""
    try:
        from feature_scanner import get_feature_scanner
        scanner = get_feature_scanner()
        print(f"✅ Feature Scanner: Available")
        return True
    except Exception as e:
        print(f"❌ Feature Scanner: {e}")
        return False

async def main():
    print("🔍 Testing Dashboard Features\n")
    print("=" * 50)
    
    results = {
        "Veo3": await test_veo3(),
        "Speaking": await test_speaking(),
        "ByteBot": await test_bytebot(),
        "Scanner": await test_scanner()
    }
    
    print("\n" + "=" * 50)
    print(f"\nWorking: {sum(results.values())}/{len(results)}")
    print(f"Broken: {len(results) - sum(results.values())}/{len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
