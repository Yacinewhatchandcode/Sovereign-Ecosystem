
import sys
import asyncio
import os

# Mock paths
sys.path.append(os.getcwd())

async def test_init():
    print("Testing IntegratedVisualOperator init...")
    try:
        from integrated_visual_operator import IntegratedVisualOperator
        op = IntegratedVisualOperator()
        print("✅ SUCCESS: IntegratedVisualOperator initialized")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_init())
