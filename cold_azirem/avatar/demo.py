"""
aSiReM Avatar Demo
Demonstrates the avatar engine with basic functionality.
"""

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from cold_azirem.avatar import AvatarEngine, AvatarConfig, MotionBackend, LipSyncBackend


async def demo_avatar():
    """
    Demo: Initialize and test the Avatar Engine
    """
    print("\n" + "="*60)
    print("🎭 aSiReM AVATAR ENGINE DEMO")
    print("="*60)
    
    # Create configuration
    config = AvatarConfig(
        motion_backend=MotionBackend.FACSVATAR,
        lipsync_backend=LipSyncBackend.MUSETALK,
        target_fps=30,
        enable_gpu=True,  # Use MPS on M4 Pro
        style_preset="sovereign",
        language="fr"
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Motion: {config.motion_backend.value}")
    print(f"   Lip Sync: {config.lipsync_backend.value}")
    print(f"   Voice: {config.voice_backend.value}")
    print(f"   Render: {config.render_backend.value}")
    print(f"   Target FPS: {config.target_fps}")
    print(f"   Language: {config.language}")
    
    # Initialize engine
    print("\n🚀 Initializing Avatar Engine...")
    engine = AvatarEngine(config)
    await engine.initialize()
    
    # Register callbacks
    engine.on_speech_start(lambda text: print(f"🎤 Speaking: {text[:50]}..."))
    engine.on_speech_end(lambda text: print(f"✓ Speech complete"))
    
    # Test speech synthesis
    print("\n🗣️ Testing speech synthesis...")
    test_phrases = [
        "Bienvenue dans l'univers aSiReM. Je suis votre guide.",
        "Le protocole d'ascension est maintenant actif.",
        "مرحبا بكم في نظام الذكاء الاصطناعي"  # Arabic test
    ]
    
    for phrase in test_phrases:
        print(f"\n   → Generating: {phrase[:40]}...")
        audio = await engine.speak(phrase, emotion="confident")
        print(f"   ✓ Generated {len(audio)} bytes of audio")
    
    # Summary
    print("\n" + "="*60)
    print("✅ AVATAR ENGINE DEMO COMPLETE")
    print("="*60)
    print("\nCapabilities demonstrated:")
    print("  • Motion tracking initialization")
    print("  • Lip synchronization engine")
    print("  • Voice synthesis (XTTS v2)")
    print("  • WebGL rendering pipeline")
    print("\nNext: Connect to Cold Azirem Orchestrator for full integration")


async def demo_with_orchestrator():
    """
    Demo: Avatar integrated with Cold Azirem orchestrator
    """
    from cold_azirem.orchestration.orchestrator import AgentOrchestrator
    from cold_azirem.avatar import create_avatar_engine
    
    print("\n" + "="*60)
    print("🤖 aSiReM AVATAR + AGENT INTEGRATION DEMO")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create avatar with factory function
    avatar = create_avatar_engine(
        motion_tracker="facsvatar",
        lip_sync="musetalk",
        voice_engine="xtts_v2",
        renderer="webgl"
    )
    
    # Connect avatar to orchestrator
    avatar.connect_to_orchestrator(orchestrator)
    
    # Initialize SPECTRA for design direction
    print("\n🎨 Initializing SPECTRA for avatar appearance...")
    spectra = await orchestrator.initialize_master_agent("SPECTRA")
    
    # Initialize avatar
    await avatar.initialize()
    
    # Simulate agent response -> avatar speech
    print("\n💬 Simulating agent conversation...")
    
    # This would be a real agent response in production
    agent_response = """
    Bonjour, je suis aSiReM, votre intelligence artificielle souveraine.
    Je peux vous aider avec le développement, la recherche, et la création.
    Que souhaitez-vous accomplir aujourd'hui?
    """
    
    print(f"   Agent Response: {agent_response[:50]}...")
    audio = await avatar.speak(agent_response.strip(), emotion="welcoming")
    print(f"   ✓ Avatar spoke with {len(audio)} bytes of audio")
    
    print("\n✅ Integration demo complete!")
    
    await orchestrator.cleanup()


if __name__ == "__main__":
    print("Select demo mode:")
    print("  1. Basic Avatar Engine Demo")
    print("  2. Avatar + Agent Integration Demo")
    
    # For now, run basic demo
    asyncio.run(demo_avatar())
