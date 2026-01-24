#!/usr/bin/env python3
"""
AZIREM CLI v3
=============
Complete command-line interface for the AZIREM ecosystem.

Commands:
  status       - Show system status
  scan         - Run read-only disk discovery
  classify     - Classify discovered files
  pipeline     - Run full agent pipeline
  registry     - Manage agent registry
  serve        - Start REST API + Matrix UI
  dashboard    - Start Sovereign Command Center (port 8082)
  podcast      - Interactive AZIREM conversation
  visual-scan  - Run Integrated Visual Operator
  security     - Run security audit
  qa           - Run QA checks
  agents       - Test core agents
  validate-antigravity - Enforce production-ready standards
"""

import sys
import argparse
import asyncio
import webbrowser
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def cmd_scan(args):
    """Run discovery scan."""
    print("📂 Running enhanced discovery scan...")
    from azirem_discovery.discovery_cli import EnhancedScanner, main as scan_main
    
    scan_main()


def cmd_pipeline(args):
    """Run full pipeline."""
    print("🔄 Running full agent pipeline...")
    from azirem_orchestration.pipeline_orchestrator import PipelineOrchestrator
    
    orchestrator = PipelineOrchestrator(args.output)
    run = orchestrator.run_full_pipeline(
        args.path,
        max_files=args.max_files
    )
    
    if run.current_stage.value == "complete":
        print(f"\n✅ Pipeline complete! {run.total_files} files processed.")
    else:
        print(f"\n❌ Pipeline failed: {run.errors}")


def cmd_registry(args):
    """Manage agent registry."""
    print("📋 Managing agent registry...")
    from azirem_registry.registry_manager import RegistryManager, print_registry_summary
    
    manager = RegistryManager(args.inventory)
    if manager.load_inventory():
        registry = manager.build_registry()
        print_registry_summary(registry)
        manager.freeze_registry(args.output)


def cmd_serve(args):
    """Start REST API server."""
    print("🌐 Starting API server...")
    
    try:
        from azirem_orchestration.api_server import app
        
        print(f"Starting on http://{args.host}:{args.port}")
        print("Matrix UI: http://localhost:8080/")
        print()
        
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("Installing Flask...")
        import subprocess
        subprocess.run(["pip3", "install", "flask", "flask-cors"])
        print("Please run again.")


def cmd_dashboard(args):
    """Start Sovereign Command Center."""
    print("🌌 Starting Sovereign Command Center...")
    print()
    
    dashboard_path = Path(__file__).parent / "sovereign-dashboard"
    server_script = dashboard_path / "real_agent_system.py"
    
    if not server_script.exists():
        print(f"❌ Server not found: {server_script}")
        return
    
    url = f"http://localhost:{args.port}/index.html"
    print(f"📡 WebSocket Server: ws://localhost:{args.port}/ws")
    print(f"🖥️  Dashboard: {url}")
    print()
    
    # Open browser if requested
    if args.open:
        print("🌐 Opening browser...")
        webbrowser.open(url)
    
    # Start the server
    import subprocess
    venv_python = dashboard_path / "venv-speaking" / "bin" / "python"
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    try:
        subprocess.run([python_cmd, str(server_script)], cwd=str(dashboard_path))
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped.")


def cmd_podcast(args):
    """Interactive AZIREM Podcast session."""
    print("🎙️ Starting AZIREM Podcast...")
    print()
    
    from azirem_brain import AziremBrain
    
    async def run_podcast():
        brain = AziremBrain()
        
        # Check Ollama status
        if await brain.check_ollama_available():
            models = await brain.list_models()
            print(f"✅ Ollama connected. Model: {brain.model}")
        else:
            print("⚠️ Ollama not available. Running in fallback mode.")
            print("   Start Ollama for full capabilities: ollama serve")
        
        print()
        print("=" * 60)
        print("🎙️ AZIREM PODCAST - Live Conversation")
        print("=" * 60)
        print("Type your questions. Enter 'quit' to exit.")
        print("-" * 60)
        
        # Single question mode
        if args.question:
            response = await brain.think(args.question)
            print(f"\n🤖 AZIREM: {response}")
            
            # Voice synthesis if requested
            if args.voice:
                await speak_response(response)
            return
        
        # Interactive REPL mode
        while True:
            try:
                question = input("\n🧑 You: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 AZIREM signing off. Until next time!")
                    break
                if not question:
                    continue
                    
                print("\n🤔 AZIREM is thinking...")
                response = await brain.think(question)
                print(f"\n🤖 AZIREM: {response}")
                
                # Voice synthesis if enabled
                if args.voice:
                    await speak_response(response)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except EOFError:
                break
    
    async def speak_response(text: str):
        """Use TTS to speak the response."""
        try:
            sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))
            from asirem_speaking_engine import ASiREMSpeakingEngine
            
            engine = ASiREMSpeakingEngine()
            print("🔊 Speaking...")
            await engine.speak(text)
        except Exception as e:
            print(f"⚠️ Voice synthesis unavailable: {e}")
    
    asyncio.run(run_podcast())


def cmd_voice_podcast(args):
    """Run real-time speech-to-speech podcast."""
    print("🎙️ Starting Voice Podcast (Speech-to-Speech)...")
    print()
    
    from azirem_voice_podcast import VoicePodcast
    
    podcast = VoicePodcast(
        whisper_model=args.model,
        silence_duration=args.silence,
        silence_threshold=args.threshold,
        record_session=args.record if hasattr(args, 'record') else False
    )
    
    asyncio.run(podcast.run())


def cmd_visual_scan(args):
    """Run Integrated Visual Operator."""
    print("👁️ Starting Integrated Visual Scan...")
    print()
    
    sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))
    
    async def run_scan():
        from integrated_visual_operator import IntegratedVisualOperator
        
        operator = IntegratedVisualOperator()
        
        async def print_event(event_type, data):
            icon = data.get("icon", "📡")
            message = data.get("message", event_type)
            print(f"{icon} {message}")
        
        operator.set_callback(print_event)
        
        paths = args.paths if args.paths else ["/Users/yacinebenhamou/aSiReM"]
        use_docker = args.docker
        
        print(f"📂 Scanning: {', '.join(paths)}")
        print(f"🐳 Docker mode: {use_docker}")
        print("-" * 60)
        
        await operator.start_integrated_scan(paths, use_docker)
        
        print("-" * 60)
        print("✅ Visual scan complete!")
    
    asyncio.run(run_scan())


def cmd_security(args):
    """Run security audit."""
    print("🛡️ Running Security Audit...")
    print()
    
    sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))
    
    async def run_audit():
        from real_agent_system import RealSecurityAgent, RealScannerAgent
        
        # First, scan for files
        scanner = RealScannerAgent()
        
        async def print_event(event_type, data):
            if event_type == "security_alert":
                print(f"⚠️ Risk in {data.get('file')}: {', '.join(data.get('issues', []))}")
            elif event_type == "activity":
                print(f"  {data.get('icon', '📡')} {data.get('message', '')}")
        
        scanner.set_callback(print_event)
        
        print("📂 Scanning files...")
        discovered = await scanner.scan_all()
        
        print(f"\n🔍 Found {len(discovered)} files with patterns")
        print("-" * 60)
        
        # Run security audit
        security = RealSecurityAgent()
        security.set_callback(print_event)
        
        await security.scan_security(discovered)
        
        print("-" * 60)
        print("✅ Security audit complete!")
    
    asyncio.run(run_audit())


def cmd_qa(args):
    """Run QA checks."""
    print("🧪 Running QA Checks...")
    print()
    
    sys.path.insert(0, str(Path(__file__).parent / "sovereign-dashboard"))
    
    async def run_qa():
        from real_agent_system import RealQAAgent, RealScannerAgent
        
        scanner = RealScannerAgent()
        
        async def print_event(event_type, data):
            if event_type == "qa_failure":
                print(f"❌ Syntax error in {data.get('file')}: {data.get('error', '')[:50]}")
            elif event_type == "activity":
                print(f"  {data.get('icon', '📡')} {data.get('message', '')}")
        
        scanner.set_callback(print_event)
        
        print("📂 Scanning Python files...")
        discovered = await scanner.scan_all()
        
        python_files = [f for f in discovered if f.extension == '.py']
        print(f"\n🐍 Found {len(python_files)} Python files")
        print("-" * 60)
        
        # Run QA
        qa = RealQAAgent()
        qa.set_callback(print_event)
        
        await qa.run_qa(python_files)
        
        print("-" * 60)
        print("✅ QA checks complete!")
    
    asyncio.run(run_qa())


def cmd_status(args):
    """Show system status."""
    import json
    
    print("=" * 60)
    print("🌌 AZIREM SYSTEM STATUS v3")
    print("=" * 60)
    
    # Check discovery
    discovery_path = Path("/Users/yacinebenhamou/aSiReM/azirem_discovery/inventory_frozen.json")
    if discovery_path.exists():
        with open(discovery_path) as f:
            inv = json.load(f)
        print(f"✅ Discovery: {inv.get('total_files', 0)} files")
        print(f"   Scan time: {inv.get('scan_timestamp', 'unknown')}")
    else:
        print("❌ Discovery: Not run yet")
    
    # Check pipeline
    pipeline_path = Path("/tmp/azirem_pipeline/registry.json")
    if pipeline_path.exists():
        with open(pipeline_path) as f:
            reg = json.load(f)
        summary = reg.get("summary", {})
        print(f"\n✅ Pipeline Registry:")
        print(f"   Files: {summary.get('total_files', 0)}")
        print(f"   Projects: {summary.get('total_projects', 0)}")
        print(f"   Execution: {summary.get('execution_time_ms', 0)}ms")
        
        by_tag = reg.get("by_tag", {})
        if by_tag:
            print(f"   Tags: {', '.join(f'{k}:{v}' for k, v in list(by_tag.items())[:5])}")
    else:
        print("\n❌ Pipeline: Not run yet")
    
    # Check agents
    agents_path = Path("/Users/yacinebenhamou/aSiReM/azirem_registry/agents_frozen.json")
    if agents_path.exists():
        with open(agents_path) as f:
            agents = json.load(f)
        print(f"\n✅ Agents Registry: {agents.get('total_agents', 0)} agents")
        for tier, ids in agents.get("tiers", {}).items():
            tier_names = {1: "Strategic", 2: "Execution", 3: "Specialist"}
            print(f"   Tier {tier} ({tier_names.get(int(tier), 'Unknown')}): {len(ids)} agents")
    else:
        print("\n❌ Agents: Not registered yet")
    
    # Check Ollama for Brain
    print("\n🧠 AZIREM Brain:")
    try:
        import aiohttp
        async def check():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            models = [m["name"] for m in data.get("models", [])]
                            return models
            except:
                return None
        models = asyncio.run(check())
        if models:
            print(f"   ✅ Ollama connected. Models: {', '.join(models[:3])}")
        else:
            print("   ⚠️ Ollama not running (run: ollama serve)")
    except:
        print("   ⚠️ Cannot check Ollama status")
    
    # Check dashboard
    dashboard_path = Path(__file__).parent / "sovereign-dashboard" / "real_agent_system.py"
    print(f"\n🖥️ Dashboard: {'✅ Available' if dashboard_path.exists() else '❌ Not found'}")
    
    # Show quick commands
    print("\n" + "-" * 60)
    print("📋 Quick Commands:")
    print("   python azirem_cli.py dashboard      # Start Command Center")
    print("   python azirem_cli.py podcast        # Chat with AZIREM")
    print("   python azirem_cli.py visual-scan    # Visual exploration")
    print("   python azirem_cli.py security       # Security audit")
    print("   python azirem_cli.py pipeline /path # Full pipeline")
    print("=" * 60)


def cmd_agents(args):
    """Test core agents."""
    print("🤖 Testing core agents...")
    from azirem_agents.core_agents import AgentFactory
    
    print(f"Available agent types: {', '.join(AgentFactory.list_types())}")
    
    # Quick test
    for agent_type in AgentFactory.list_types():
        agent = AgentFactory.create(agent_type, f"test_{agent_type}")
        print(f"  ✅ {agent_type}: {agent.get_status()['version']}")



def cmd_validate_antigravity(args):
    """Validate Antigravity compliance."""
    print("🚀 Running Antigravity Validation...")
    print()
    
    validator_path = Path(__file__).parent / "sovereign-dashboard" / "antigravity_validator.py"
    
    if not validator_path.exists():
        print(f"❌ Validator not found: {validator_path}")
        return
    
    import subprocess
    result = subprocess.run([sys.executable, str(validator_path)], 
                          cwd=str(validator_path.parent))
    
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="AZIREM CLI v3 - Sovereign Discovery & Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python azirem_cli.py status                    # Check system status
  python azirem_cli.py dashboard --open          # Start Command Center
  python azirem_cli.py podcast                   # Interactive text chat
  python azirem_cli.py podcast -q "Who are you?" # Single question
  python azirem_cli.py voice-podcast             # 🎤 Speech-to-speech (real-time)
  python azirem_cli.py voice-podcast -m small    # With larger Whisper model
  python azirem_cli.py visual-scan /path         # Visual exploration
  python azirem_cli.py security                  # Security audit
  python azirem_cli.py qa                        # QA checks
  python azirem_cli.py pipeline /path            # Full agent pipeline
        """
    )

    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=cmd_status)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start Sovereign Command Center")
    dashboard_parser.add_argument("--port", "-p", type=int, default=8082)
    dashboard_parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    # Podcast command
    podcast_parser = subparsers.add_parser("podcast", help="Interactive AZIREM conversation")
    podcast_parser.add_argument("--question", "-q", help="Single question mode")
    podcast_parser.add_argument("--voice", "-v", action="store_true", help="Enable voice synthesis")
    podcast_parser.set_defaults(func=cmd_podcast)
    
    # Voice Podcast command (speech-to-speech)
    voice_parser = subparsers.add_parser("voice-podcast", help="Real-time speech-to-speech conversation")
    voice_parser.add_argument("--model", "-m", default="base",
                             choices=["tiny", "base", "small", "medium", "large"],
                             help="Whisper model size (default: base)")
    voice_parser.add_argument("--silence", "-s", type=float, default=1.5,
                             help="Silence duration to trigger processing (seconds)")
    voice_parser.add_argument("--threshold", "-t", type=float, default=0.01,
                             help="Audio threshold for silence detection")
    voice_parser.add_argument("--record", "-r", action="store_true",
                             help="Record session and export as MP4/MP3")
    voice_parser.set_defaults(func=cmd_voice_podcast)
    
    # Visual scan command
    visual_parser = subparsers.add_parser("visual-scan", help="Run Integrated Visual Operator")
    visual_parser.add_argument("paths", nargs="*", help="Paths to scan")
    visual_parser.add_argument("--docker", "-d", action="store_true", help="Use ByteBot Docker container")
    visual_parser.set_defaults(func=cmd_visual_scan)
    
    # Security command
    security_parser = subparsers.add_parser("security", help="Run security audit")
    security_parser.set_defaults(func=cmd_security)
    
    # QA command
    qa_parser = subparsers.add_parser("qa", help="Run QA checks")
    qa_parser.set_defaults(func=cmd_qa)
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run discovery scan")
    scan_parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    scan_parser.add_argument("--output", "-o", default="/tmp/azirem_manifest")
    scan_parser.add_argument("--max-files", "-m", type=int, default=10000)
    scan_parser.set_defaults(func=cmd_scan)
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full agent pipeline")
    pipeline_parser.add_argument("path", help="Path to process")
    pipeline_parser.add_argument("--output", "-o", default="/tmp/azirem_pipeline")
    pipeline_parser.add_argument("--max-files", "-m", type=int, default=10000)
    pipeline_parser.set_defaults(func=cmd_pipeline)
    
    # Registry command
    registry_parser = subparsers.add_parser("registry", help="Build agent registry")
    registry_parser.add_argument("--inventory", "-i", 
                                 default="/Users/yacinebenhamou/aSiReM/azirem_discovery/inventory_frozen.json")
    registry_parser.add_argument("--output", "-o",
                                 default="/Users/yacinebenhamou/aSiReM/azirem_registry/agents_frozen.json")
    registry_parser.set_defaults(func=cmd_registry)
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start REST API server")
    serve_parser.add_argument("--port", "-p", type=int, default=8080)
    serve_parser.add_argument("--host", "-H", default="0.0.0.0")
    serve_parser.add_argument("--debug", "-d", action="store_true")
    serve_parser.set_defaults(func=cmd_serve)
    
    # Agents command
    agents_parser = subparsers.add_parser("agents", help="Test core agents")
    agents_parser.set_defaults(func=cmd_agents)
    
    # Validate Antigravity command
    validate_parser = subparsers.add_parser("validate-antigravity", 
                                           help="Validate production-ready standards")
    validate_parser.set_defaults(func=cmd_validate_antigravity)
    
    args = parser.parse_args()
    
    print()
    print("=" * 60)
    print("🌌 AZIREM CLI v3.0")
    print("=" * 60)
    print()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

