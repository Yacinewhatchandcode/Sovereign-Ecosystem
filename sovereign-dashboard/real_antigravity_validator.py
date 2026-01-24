#!/usr/bin/env python3
"""
REAL Antigravity Validator
Uses live AgentCommunicationHub and actual API testing instead of static analysis.
"""

import asyncio
import sys
from pathlib import Path

# Import real system components
sys.path.insert(0, str(Path(__file__).parent))
from agent_communication_hub import get_communication_hub
from real_agent_system import RealMultiAgentOrchestrator


class RealAntigravityValidator:
    """Validates Antigravity compliance using live system components."""
    
    def __init__(self):
        self.violations = []
        
   async def validate_all(self):
        """Run all validation checks using REAL system."""
        
        print("🔍 REAL Antigravity Validation (Using Live System)")
        print("=" * 60)
        
        # 1. Validate Agent Communication Hub
        await self._validate_agents()
        
        # 2. Validate API Endpoints
        await self._validate_apis()
        
        # 3. Validate No Simulation Modes
        await self._validate_no_simulation()
        
        # 4. Report
        self._print_report()
        
        return len(self.violations) == 0
    
    async def _validate_agents(self):
        """Validate agents using CommunicationHub."""
        print("\n1️⃣  Agent Communication Hub Validation")
        
        try:
            hub = get_communication_hub()
            agents = hub.get_all_agents()
            
            print(f"   ✅ {len(agents)} agents registered")
            
            # Test messaging
            test_msg = await hub.send_message(
                from_agent='validator',
                to_agent='scanner',
                msg_type='ping',
                content={}
            )
            
            print("   ✅ Agent messaging operational")
            
        except Exception as e:
            self.violations.append(f"Agent Hub FAILURE: {e}")
            print(f"   ❌ {e}")
    
    async def _validate_apis(self):
        """Test actual API endpoints."""
        print("\n2️⃣  API Endpoint Validation")
        
        import aiohttp
        
        endpoints = [
            '/api/status',
            '/api/agents/config',
            '/api/veo3/credits',
            '/api/agents/all'
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f'http://localhost:8082{endpoint}') as resp:
                        if resp.status == 200:
                            print(f"   ✅ {endpoint}")
                        else:
                            self.violations.append(f"API {endpoint} returned {resp.status}")
                            print(f"   ❌ {endpoint} ({resp.status})")
                except Exception as e:
                    self.violations.append(f"API {endpoint} FAILED: {e}")
                    print(f"   ❌ {endpoint} (unreachable)")
    
    async def _validate_no_simulation(self):
        """Check for simulation/mock modes in live system."""
        print("\n3️⃣  Zero Simulation Mode Validation")
        
        try:
            orch = RealMultiAgentOrchestrator()
            
            # Check Veo3
            if hasattr(orch, 'veo3_generator'):
                if orch.veo3_generator and orch.veo3_generator.is_simulated:
                    self.violations.append(
                        "Veo3Generator is in SIMULATION mode - "
                        "Missing GOOGLE_API_KEY environment variable"
                    )
                    print("   ❌ Veo3: SIMULATION MODE (Rule 2.2 violation)")
                else:
                    print("   ✅ Veo3: Production mode")
            
            # Check Speaking Engine
            if hasattr(orch, 'speaking_engine'):
                if orch.speaking_engine and getattr(orch.speaking_engine, 'is_simulated', False):
                    self.violations.append("SpeakingEngine is in SIMULATION mode")
                    print("   ❌ Speaking: SIMULATION MODE (Rule 2.2 violation)")
                else:
                    print("   ✅ Speaking: Production mode")
                    
        except Exception as e:
            self.violations.append(f"Orchestrator check failed: {e}")
            print(f"   ❌ {e}")
    
    def _print_report(self):
        """Print final report."""
        print("\n" + "=" * 60)
        
        if len(self.violations) == 0:
            print("✅ ANTIGRAVITY COMPLIANCE: PASS")
        else:
            print(f"❌ ANTIGRAVITY COMPLIANCE: FAIL ({len(self.violations)} violations)")
            print("\nVIOLATIONS:")
            for i, v in enumerate(self.violations, 1):
                print(f"  {i}. {v}")
        
        print("=" * 60)


async def main():
    validator = RealAntigravityValidator()
    passed = await validator.validate_all()
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    asyncio.run(main())
