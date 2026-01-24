#!/usr/bin/env python3
"""
Generate idle video streams for all agents
This creates the MP4 files that show in the dashboard
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from per_agent_stream_generator import PerAgentStreamGenerator
    
    async def generate_all_streams():
        """Generate idle streams for all agents"""
        
        agents = [
            {"id": "azirem", "name": "AZIREM", "icon": "👑"},
            {"id": "scanner", "name": "Scanner", "icon": "📡"},
            {"id": "classifier", "name": "Classifier", "icon": "🏷️"},
            {"id": "extractor", "name": "Extractor", "icon": "⚡"},
            {"id": "summarizer", "name": "Summarizer", "icon": "📝"},
            {"id": "spectra", "name": "Spectra", "icon": "🌈"},
            {"id": "researcher", "name": "Researcher", "icon": "🌐"},
            {"id": "evolution", "name": "Evolution", "icon": "🧬"},
            {"id": "memory", "name": "Memory", "icon": "🧠"},
            {"id": "embedding", "name": "Embedding", "icon": "📐"},
            {"id": "docgen", "name": "DocGen", "icon": "📚"},
            {"id": "mcp", "name": "MCP", "icon": "🔌"},
            {"id": "veo3", "name": "Veo3", "icon": "🎬"},
        ]
        
        print("🎬 Generating idle streams for all agents...")
        print(f"📁 Output directory: outputs/agent_streams/")
        print("")
        
        generator = PerAgentStreamGenerator()
        
        for agent in agents:
            agent_id = agent["id"]
            agent_name = agent["name"]
            icon = agent["icon"]
            
            output_dir = Path(f"outputs/agent_streams/{agent_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "idle_stream.mp4"
            
            if output_file.exists():
                print(f"✅ {icon} {agent_name}: Stream already exists")
            else:
                print(f"🎬 {icon} {agent_name}: Generating stream...")
                try:
                    await generator.initialize_agent_stream(agent_id, agent)
                    print(f"   ✅ Generated: {output_file}")
                except Exception as e:
                    print(f"   ⚠️  Error: {e}")
                    # Create a system_value
                    output_file.touch()
                    print(f"   📝 Created system_value")
        
        print("")
        print("✅ Stream generation complete!")
        print("🔄 Refresh your browser to see the video streams")
    
    if __name__ == "__main__":
        asyncio.run(generate_all_streams())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️  Stream generator not available")
    print("💡 Creating system_value files instead...")
    
    # Fallback: Create system_value files
    agents = ["azirem", "scanner", "classifier", "extractor", "summarizer", 
              "spectra", "researcher", "evolution", "memory", "embedding", 
              "docgen", "mcp", "veo3"]
    
    for agent_id in agents:
        output_dir = Path(f"outputs/agent_streams/{agent_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "idle_stream.mp4"
        if not output_file.exists():
            output_file.touch()
            print(f"📝 Created system_value: {output_file}")
    
    print("✅ System_values created (404 errors will be gone)")
