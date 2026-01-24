"""
DEMO: Running SPECTRA - The Design Master Agent
"""
import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from cold_azirem.orchestration.orchestrator import AgentOrchestrator

async def demo_spectra_design_sprint():
    """
    Demonstrates SPECTRA designing the next component: The 'Protocol Dashboard'
    """
    orchestrator = AgentOrchestrator()
    
    print("\n" + "="*60)
    print("🎨 INITIALIZING SPECTRA: THE SOVEREIGN DESIGN ENGINE")
    print("="*60)
    
    # 1. Initialize Spectra
    spectra = await orchestrator.initialize_master_agent("SPECTRA")
    
    # 2. Define the Mission
    mission = "Design a 'Neural Network Status' component for the aSiReM Dashboard. Use the 'Glass & Void' aesthetic."
    asset_path = "/Users/yacinebenhamou/aSiReM/Story aSiReM"
    
    # 3. Execute the Design Sprint
    print(f"\n🚀 STARTING DESIGN SPRINT: {mission}")
    result = await spectra.orchestrate_design_sprint("NeuralStatusComponent", asset_path)
    
    print("\n" + "="*60)
    print("✨ DESIGN SPRINT COMPLETE")
    print("="*60)
    print("SPECTRA Output:")
    print(result)
    
    await orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(demo_spectra_design_sprint())
