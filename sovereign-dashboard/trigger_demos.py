#!/usr/bin/env python3
"""
Quick manual trigger for dashboard demos.
"""

import requests
import time

BASE_URL = "http://localhost:8082"

def trigger_demo(demo_type):
    """Trigger a specific demo via API."""
    print(f"\n🚀 Triggering {demo_type}...")
    
    if demo_type == "speaking":
        print("📋 Demo: aSiReM Speaking with Voice Cloning")
        print("   Watch the dashboard - aSiReM's avatar will show lip-synced video!")
        # User should click "aSiReM Speak" button
        
    elif demo_type == "pipeline":
        response = requests.post(f"{BASE_URL}/api/run-pipeline")
        print("📋 Demo: Evolution Pipeline - Multi-Agent Streaming")
        print(f"   Status: {response.json()}")
        print("   Watch agents light up sequentially!")
        
    elif demo_type == "narrative":
        print("📋 Demo: Cinematic Narrative Production")
        print("   Click the '🎭 Cinematic Narrative' button in the dashboard")
        print("   Watch multi-scene production with 9-expert team!")

def main():
    print("=" * 70)
    print("   SOVEREIGN COMMAND CENTER - DEMO TRIGGER")
    print("=" * 70)
    print(f"\n📺 Dashboard: {BASE_URL}/index.html")
    print("\n📋 Available Demos:")
    print("   1. aSiReM Speaking (Manual - click 'aSiReM Speak' button)")
    print("   2. Evolution Pipeline (Auto-triggered)")
    print("   3. Cinematic Narrative (Manual - click '🎭 Cinematic Narrative' button)")
    
    print("\n" + "=" * 70)
    
    # Auto-trigger pipeline
    trigger_demo("pipeline")
    
    print("\n" + "=" * 70)
    print("\n💡 Manual Actions Required:")
    print("   1. Click 'aSiReM Speak' to see lip-synced speaking")
    print("   2. Click '🎭 Cinematic Narrative' for multi-scene production")
    print("\n✅ Pipeline demo triggered! Check the dashboard for visual streams.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure the server is running at http://localhost:8082")
