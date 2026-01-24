"""
aSiReM Narrative Factory Demo
Demonstrates the 9-expert deliberation system.
"""

import asyncio
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cold_azirem.narrative.factory import (
    NarrativeFactory,
    STORY_EXPERTS,
    create_story_episode
)


async def demo_expert_deliberation():
    """
    Demo: Watch the 9 experts deliberate on creating an aSiReM episode.
    """
    print("\n" + "="*70)
    print("🎬 aSiReM NARRATIVE FACTORY - 9-EXPERT DELIBERATION DEMO")
    print("="*70)
    
    print("\n📋 THE EXPERT TEAM:")
    print("-" * 50)
    for key, expert in STORY_EXPERTS.items():
        print(f"   • {expert.name} - {expert.title}")
    print()
    
    # Run the deliberation
    print("🎭 Starting 5-minute deliberation session (Simulated)...")
    print("   Topic: 'Episode 1: What is AI?'\n")
    print("-" * 70)
    
    # We use a short deliberation time for the demo, but in production this would be 5.0
    result = await create_story_episode(
        episode_title="Episode 1: What is AI?",
        target_duration_minutes=1.0, # 1 minute for the demo
        deliberation_minutes=0.1
    )
    
    print("-" * 70)
    
    # Show production estimate
    est = result["production_estimate"]
    print("\n📊 PRODUCTION ESTIMATE:")
    print(f"   • Target Duration: {est['duration_formatted']}")
    print(f"   • Video Chunks Needed: {est['num_chunks']}")
    print(f"   • Estimated Cost: ${est['estimated_cost_usd']:.2f} (Simulated)")
    print(f"   • Generation Time: ~{est['generation_time_minutes']} minutes")
    
    # Save transcript
    transcript_path = Path("/Users/yacinebenhamou/aSiReM/cold_azirem/narrative/output")
    transcript_path.mkdir(parents=True, exist_ok=True)
    
    transcript_file = transcript_path / "deliberation_transcript.md"
    with open(transcript_file, "w") as f:
        f.write(result["deliberation_transcript"])
    
    print(f"\n📝 Full transcript saved to: {transcript_file}")
    
    print("\n" + "="*70)
    print("✅ DELIBERATION SIMULATION COMPLETE")
    print("="*70)
    print("\nThe 9 experts have provided their input on:")
    print("   • Asset analysis (character, environment)")
    print("   • Story conceptualization (emotional beats)")
    print("   • Technical planning (Veo3 chunks)")
    print("   • Script drafting (opening lines)")
    print("   • Prompt engineering (consistency)")
    print("\n🚀 READY FOR PRODUCTION:")
    print("   To generate actual video, ensure GOOGLE_API_KEY is set in your environment.")
    print("   Then set `deliberation_minutes=5.0` and run the full factory.")


if __name__ == "__main__":
    asyncio.run(demo_expert_deliberation())
