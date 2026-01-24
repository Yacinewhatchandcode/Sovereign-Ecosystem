
import asyncio
import os
import sys
from pathlib import Path

# Add sovereign-dashboard to path
dashboard_path = Path(__file__).parent / "sovereign-dashboard"
sys.path.append(str(dashboard_path))

from real_agent_system import RealMultiAgentOrchestrator

async def main():
    print("🚀 Starting Sovereign Pipeline (Action B)...")
    
    # Initialize orchestrator
    orchestrator = RealMultiAgentOrchestrator()
    
    # Wait for async init (like asirem speaking engine)
    print("⏳ Initializing agents...")
    await asyncio.sleep(3)
    
    # Run pipeline
    print("🧬 Executing full multi-agent evolution cycle...")
    results = await orchestrator.run_full_pipeline()
    
    print("\n" + "="*50)
    print("🏆 PIPELINE COMPLETE")
    print(f"📂 Files Scanned: {results['discovered_files']}")
    print(f"🏷️ Categories: {results['categories']}")
    print(f"🕸️ Knowledge Nodes: {len(results['knowledge_graph'])}")
    print("="*50)
    
    if os.path.exists("pipeline_report.json"):
        print("✅ Report generated: pipeline_report.json")
    else:
        print("❌ Report generation failed.")

if __name__ == "__main__":
    asyncio.run(main())
