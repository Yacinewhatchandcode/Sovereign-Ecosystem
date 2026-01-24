#!/usr/bin/env python3
"""
Test Veo3 Video Generation - MP4 Output
Verifies the video generation pipeline works end-to-end
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_veo3_generation():
    """Test video generation with Veo3"""
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not set")
        print("Run: export GOOGLE_API_KEY='your-key-here'")
        return False
    
    print("🎬 Testing Veo3 Video Generation")
    print("=" * 60)
    
    # Import generator
    try:
        from asirem_speaking_engine import Veo3Generator
        print("✅ Veo3Generator imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Create generator
    try:
        gen = Veo3Generator()
        print("✅ Generator initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Check credits
    try:
        credits = gen.get_credits()
        print(f"✅ Credits available:")
        print(f"   Total: {credits['total']}")
        print(f"   Used: {credits['used']}")  
        print(f"   Remaining: {credits['remaining']}")
    except Exception as e:
        print(f"⚠️  Credit check failed: {e}")
    
    # Generate test video
    print("\n🎥 Generating test video...")
    print("   Prompt: 'A blue bird flying through clouds'")
    print("   Duration: 5 seconds")
    print("   Quality: fast (20 credits)")
    
    try:
        video_path = gen.generate_video(
            prompt="A blue bird flying through clouds",
            duration=5,
            quality="fast"
        )
        
        print(f"\n✅ VIDEO GENERATED SUCCESSFULLY!")
        print(f"   Path: {video_path}")
        
        # Verify file exists
        if Path(video_path).exists():
            size = Path(video_path).stat().st_size
            print(f"   Size: {size / 1024 / 1024:.2f} MB")
            print(f"   ✅ MP4 file exists")
        else:
            print(f"   ❌ File not found at: {video_path}")
            return False
        
        # Check credits after
        credits_after = gen.get_credits()
        print(f"\n📊 Credits after generation:")
        print(f"   Used: {credits_after['used']}")
        print(f"   Remaining: {credits_after['remaining']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("VEO3 VIDEO GENERATION TEST")
    print("=" * 60 + "\n")
    
    success = test_veo3_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Video generation works!")
        print("\nGenerated videos are in:")
        print("  /Users/yacinebenhamou/aSiReM/sovereign-dashboard/generated_videos/")
    else:
        print("❌ TEST FAILED - See errors above")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
