#!/usr/bin/env python3
"""
🎙️ AZIREM PODCAST - Interactive AI Podcast System
==================================================
Your personal podcast with AZIREM, powered by:
- Voice Cloning (YOUR voice via XTTS)
- 13-Agent Fleet (Scanner, Spectra, Researcher, etc.)
- 9-Expert Narrative Factory
- Full Codebase + NAS Knowledge

Commands:
  start      - Start interactive podcast session
  ask        - Ask a single question
  demo       - Run demonstration
  status     - Check system status
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "sovereign-dashboard"))


# =============================================================================
# AZIREM PODCAST ENGINE
# =============================================================================

class AziremPodcast:
    """
    Main podcast engine integrating:
    - AZIREM Brain (intelligence)
    - Speaking Engine (voice synthesis)
    - Visual Engine (optional avatar)
    """
    
    def __init__(self, use_voice: bool = True, use_avatar: bool = False):
        self.use_voice = use_voice
        self.use_avatar = use_avatar
        self.brain = None
        self.speaking_engine = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize all podcast components."""
        print("\n" + "🎙️" * 20)
        print("   AZIREM PODCAST")
        print("🎙️" * 20 + "\n")
        
        # Initialize Brain
        print("🧠 Loading AZIREM Brain...")
        from azirem_brain import AziremBrain
        self.brain = AziremBrain()
        self.brain.set_callback(self._handle_event)
        print("   ✅ Brain ready")
        
        # Initialize Speaking Engine (Voice Cloning)
        if self.use_voice:
            print("🔊 Loading Speaking Engine (Voice Cloning)...")
            try:
                from asirem_speaking_engine import ASiREMSpeakingEngine
                self.speaking_engine = ASiREMSpeakingEngine()
                await self.speaking_engine.initialize()
                print("   ✅ Voice cloning ready")
            except Exception as e:
                print(f"   ⚠️ Voice cloning unavailable: {e}")
                self.speaking_engine = None
        
        self.initialized = True
        print("\n✅ AZIREM Podcast ready!")
        print("-" * 50)
        
    async def _handle_event(self, event_type: str, data: dict):
        """Handle events from brain/agents."""
        # Visual feedback during processing
        if event_type == "thinking_started":
            print("   🧠 Thinking...")
        elif event_type == "question_classified":
            print(f"   📋 Type: {data.get('type')} (confidence: {data.get('confidence', 0):.0%})")
        elif event_type == "gathering_started":
            agents = data.get('agents', [])
            print(f"   🔍 Consulting: {', '.join(agents)}")
        elif event_type == "thinking_complete":
            pass  # Response will be shown
    
    async def ask(self, question: str, speak: bool = True) -> str:
        """
        Ask AZIREM a question.
        
        Args:
            question: The question to ask
            speak: Whether to speak the response aloud
            
        Returns:
            AZIREM's response text
        """
        if not self.initialized:
            await self.initialize()
        
        print(f"\n❓ You: {question}")
        print("-" * 40)
        
        # Get response from brain
        response = await self.brain.think(question)
        
        print(f"\n🤖 AZIREM: {response}")
        
        # Speak response if voice is enabled
        if speak and self.speaking_engine and self.use_voice:
            print("\n🔊 Speaking response...")
            try:
                result = await self.speaking_engine.speak(response)
                audio_path = result.get("audio_path")
                if audio_path and os.path.exists(audio_path):
                    print(f"   ✅ Audio: {audio_path}")
                    # Play audio on macOS
                    os.system(f"afplay '{audio_path}' &")
            except Exception as e:
                print(f"   ⚠️ Speech failed: {e}")
        
        return response
    
    async def start_session(self):
        """Start an interactive podcast session."""
        if not self.initialized:
            await self.initialize()
        
        print("\n" + "=" * 60)
        print("🎙️ AZIREM PODCAST SESSION")
        print("=" * 60)
        print("\nWelcome to the AZIREM Podcast!")
        print("Ask me anything about your codebase, AI, or just chat.")
        print("Type 'quit' or 'exit' to end the session.\n")
        
        # Opening greeting
        opening = await self.ask("Introduce yourself briefly for our podcast audience", speak=self.use_voice)
        
        # Interactive loop
        while True:
            try:
                print("\n" + "-" * 40)
                user_input = input("🎤 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                    # Closing
                    closing = await self.ask("Say goodbye to our listeners", speak=self.use_voice)
                    print("\n👋 Thanks for listening to the AZIREM Podcast!")
                    break
                
                # Process question
                await self.ask(user_input, speak=self.use_voice)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended. Thanks for listening!")
                break
            except EOFError:
                break
    
    async def run_demo(self):
        """Run a demonstration podcast segment."""
        if not self.initialized:
            await self.initialize()
        
        print("\n" + "=" * 60)
        print("🎬 AZIREM PODCAST DEMO")
        print("=" * 60)
        print("\nRunning automated demo segment...\n")
        
        demo_questions = [
            "Who are you, AZIREM?",
            "What can you tell me about the multi-agent patterns in my codebase?",
            "What's the most exciting thing about AI in 2026?"
        ]
        
        for i, q in enumerate(demo_questions, 1):
            print(f"\n{'=' * 40}")
            print(f"Demo Question {i}/{len(demo_questions)}")
            print("=" * 40)
            await self.ask(q, speak=self.use_voice)
            await asyncio.sleep(1)  # Brief pause between questions
        
        print("\n" + "=" * 60)
        print("✅ Demo complete!")
        print("=" * 60)


# =============================================================================
# STATUS CHECKER
# =============================================================================

def check_status():
    """Check the status of all podcast system components."""
    print("\n" + "=" * 60)
    print("🔍 AZIREM PODCAST SYSTEM STATUS")
    print("=" * 60 + "\n")
    
    # Check Brain
    brain_path = PROJECT_ROOT / "azirem_brain.py"
    print(f"🧠 AZIREM Brain: {'✅ Ready' if brain_path.exists() else '❌ Missing'}")
    
    # Check Speaking Engine
    se_path = PROJECT_ROOT / "sovereign-dashboard/asirem_speaking_engine.py"
    print(f"🔊 Speaking Engine: {'✅ Ready' if se_path.exists() else '❌ Missing'}")
    
    # Check Voice Reference
    voice_path = PROJECT_ROOT / "sovereign-dashboard/assets/MyVoice.wav"
    if voice_path.exists():
        size_mb = voice_path.stat().st_size / (1024 * 1024)
        print(f"🎤 Voice Reference: ✅ Ready ({size_mb:.1f}MB)")
    else:
        print("🎤 Voice Reference: ❌ Missing (MyVoice.wav)")
    
    # Check XTTS
    xtts_venv = Path.home() / "venv-xtts/bin/python3"
    print(f"🗣️ XTTS Voice Clone: {'✅ Ready' if xtts_venv.exists() else '⚠️ Not installed'}")
    
    # Check Story Bible
    bible_path = PROJECT_ROOT / "cold_azirem/narrative/ASIREM_STORY_BIBLE.md"
    print(f"📖 Story Bible: {'✅ Ready' if bible_path.exists() else '❌ Missing'}")
    
    # Check Narrative Factory
    factory_path = PROJECT_ROOT / "cold_azirem/narrative/factory.py"
    print(f"🎭 9-Expert Factory: {'✅ Ready' if factory_path.exists() else '❌ Missing'}")
    
    # Check NAS
    nas_path = Path("/Volumes/NasYac")
    print(f"💾 NAS (NasYac): {'✅ Mounted' if nas_path.exists() else '⚠️ Not mounted'}")
    
    # Check Real Agent System
    ras_path = PROJECT_ROOT / "sovereign-dashboard/real_agent_system.py"
    print(f"🤖 13-Agent Fleet: {'✅ Ready' if ras_path.exists() else '❌ Missing'}")
    
    print("\n" + "-" * 60)
    print("Quick Start:")
    print("  python azirem_podcast.py demo    # Run demo")
    print("  python azirem_podcast.py start   # Interactive session")
    print("  python azirem_podcast.py ask \"Your question\"")
    print("=" * 60 + "\n")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AZIREM Podcast - Your AI Co-Host",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python azirem_podcast.py status                # Check system
  python azirem_podcast.py demo                  # Run demo
  python azirem_podcast.py start                 # Interactive session
  python azirem_podcast.py start --no-voice      # Text only
  python azirem_podcast.py ask "Who are you?"    # Single question
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check system status")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demonstration")
    demo_parser.add_argument("--no-voice", action="store_true", help="Disable voice synthesis")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start interactive session")
    start_parser.add_argument("--no-voice", action="store_true", help="Disable voice synthesis")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a single question")
    ask_parser.add_argument("question", nargs="+", help="Question to ask")
    ask_parser.add_argument("--no-voice", action="store_true", help="Disable voice synthesis")
    
    args = parser.parse_args()
    
    # Header
    print()
    print("🎙️" * 15)
    print(" AZIREM PODCAST v1.0")
    print("🎙️" * 15)
    
    if args.command == "status":
        check_status()
        
    elif args.command == "demo":
        podcast = AziremPodcast(use_voice=not getattr(args, 'no_voice', False))
        asyncio.run(podcast.run_demo())
        
    elif args.command == "start":
        podcast = AziremPodcast(use_voice=not getattr(args, 'no_voice', False))
        asyncio.run(podcast.start_session())
        
    elif args.command == "ask":
        question = " ".join(args.question)
        podcast = AziremPodcast(use_voice=not getattr(args, 'no_voice', False))
        asyncio.run(podcast.ask(question))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
