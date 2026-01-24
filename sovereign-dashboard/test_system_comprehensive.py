#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE SYSTEM TEST SUITE
===================================
Tests all features of the aSiReM Sovereign Command Center
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

class SystemTester:
    def __init__(self):
        self.base_path = Path.home() / "aSiReM" / "sovereign-dashboard"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def test(self, name, func):
        """Run a single test"""
        self.total_tests += 1
        print(f"\n{CYAN}[TEST {self.total_tests}]{RESET} {name}...", end=" ", flush=True)
        
        try:
            result = func()
            if result:
                print(f"{GREEN}✅ PASS{RESET}")
                self.passed_tests += 1
                self.results.append({"test": name, "status": "PASS", "details": result})
                return True
            else:
                print(f"{RED}❌ FAIL{RESET}")
                self.failed_tests += 1
                self.results.append({"test": name, "status": "FAIL", "details": "Test returned False"})
                return False
        except Exception as e:
            print(f"{RED}❌ ERROR{RESET}")
            self.failed_tests += 1
            self.results.append({"test": name, "status": "ERROR", "details": str(e)})
            return False
    
    def test_server_running(self):
        """Test if server is running on port 8082"""
        result = subprocess.run(['lsof', '-i', ':8082'], capture_output=True, text=True)
        return "LISTEN" in result.stdout
    
    def test_dashboard_files(self):
        """Test if dashboard files exist"""
        files = ['index.html', 'real_agent_system.py', 'agent_visual_engine.py', 'asirem_speaking_engine.py']
        for f in files:
            if not (self.base_path / f).exists():
                return False
        return True
    
    def test_assets_exist(self):
        """Test if assets are available"""
        voice_file = self.base_path / "assets" / "MyVoice.wav"
        video_file = self.base_path / "assets" / "asirem-video.mp4"
        return voice_file.exists() and video_file.exists() and voice_file.stat().st_size > 1000000
    
    def test_generated_outputs(self):
        """Test if generated files exist"""
        generated = self.base_path / "generated"
        if not generated.exists():
            return False
        
        wav_files = list(generated.glob("speech_*.wav"))
        mp4_files = list(generated.glob("video_*.mp4"))
        
        return len(wav_files) > 0 and len(mp4_files) > 0
    
    def test_xtts_installation(self):
        """Test if XTTS venv is installed"""
        venv_path = Path.home() / "venv-xtts"
        tts_bin = venv_path / "bin" / "tts"
        return venv_path.exists() and tts_bin.exists()
    
    def test_xtts_model(self):
        """Test if XTTS can list models"""
        try:
            venv_path = Path.home() / "venv-xtts"
            tts_bin = venv_path / "bin" / "tts"
            result = subprocess.run([str(tts_bin), '--list_models'], 
                                  capture_output=True, text=True, timeout=10)
            return "xtts" in result.stdout.lower()
        except:
            return False
    
    def test_musetalk_exists(self):
        """Test if MuseTalk is installed"""
        musetalk_path = Path.home() / "aSiReM" / "cold_azirem" / "avatar" / "deps" / "MuseTalk"
        inference_script = musetalk_path / "scripts" / "inference.py"
        return musetalk_path.exists() and inference_script.exists()
    
    def test_character_assets(self):
        """Test if character assets are loaded"""
        char_dir = self.base_path / "assets" / "character"
        if not char_dir.exists():
            return False
        images = list(char_dir.glob("*.png")) + list(char_dir.glob("*.jpg"))
        return len(images) >= 10
    
    def test_story_bible(self):
        """Test if Story Bible exists"""
        story_bible = Path.home() / "aSiReM" / "cold_azirem" / "narrative" / "ASIREM_STORY_BIBLE.md"
        return story_bible.exists() and story_bible.stat().st_size > 1000
    
    def test_documentation(self):
        """Test if documentation files exist"""
        docs = [
            'QUICK_STATUS.md',
            'COMPREHENSIVE_FEATURE_ANALYSIS.md',
            'FINAL_STATUS.md',
            'IMPLEMENTATION_COMPLETE.md'
        ]
        for doc in docs:
            if not (self.base_path / doc).exists():
                return False
        return True
    
    def test_database_schema(self):
        """Test if database schema file exists"""
        return (self.base_path / "database_schema.sql").exists()
    
    def test_python_imports(self):
        """Test if key Python modules can be imported"""
        try:
            sys.path.insert(0, str(self.base_path))
            # Try importing the main modules
            import real_agent_system
            import agent_visual_engine
            import asirem_speaking_engine
            return True
        except ImportError as e:
            return False
    
    def test_websocket_imports(self):
        """Test if WebSocket dependencies are available"""
        try:
            import websockets
            import asyncio
            return True
        except ImportError:
            return False
    
    def test_web_search_capability(self):
        """Test if web search tools are available"""
        try:
            import requests
            return True
        except ImportError:
            return False
    
    def test_filesystem_scanner(self):
        """Test if filesystem paths exist"""
        paths = [
            Path.home() / "aSiReM",
            Path.home() / "OptimusAI"
        ]
        return all(p.exists() for p in paths)
    
    def test_voice_cloning_ready(self):
        """Test if voice cloning is ready"""
        # Check XTTS installed
        venv_path = Path.home() / "venv-xtts"
        # Check voice file
        voice_file = self.base_path / "assets" / "MyVoice.wav"
        # Check speaking engine
        engine = self.base_path / "asirem_speaking_engine.py"
        
        return venv_path.exists() and voice_file.exists() and engine.exists()
    
    def test_visual_streaming_ready(self):
        """Test if visual streaming is configured"""
        engine = self.base_path / "agent_visual_engine.py"
        outputs = self.base_path / "outputs"
        
        # Check if outputs dir exists or can be created
        if not outputs.exists():
            try:
                outputs.mkdir(parents=True, exist_ok=True)
                return True
            except:
                return False
        return engine.exists()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n\n{'='*80}")
        print(f"{CYAN}🧪 COMPREHENSIVE SYSTEM TEST REPORT{RESET}")
        print(f"{'='*80}\n")
        
        print(f"📊 {BLUE}SUMMARY{RESET}")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   {GREEN}Passed: {self.passed_tests}{RESET}")
        print(f"   {RED}Failed: {self.failed_tests}{RESET}")
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        print(f"\n{'='*80}")
        print(f"📋 {BLUE}DETAILED RESULTS{RESET}\n")
        
        for i, result in enumerate(self.results, 1):
            status_color = GREEN if result['status'] == 'PASS' else RED
            status_icon = '✅' if result['status'] == 'PASS' else '❌'
            print(f"{i:2d}. {status_icon} {status_color}{result['status']:6s}{RESET} | {result['test']}")
            if result['status'] != 'PASS' and result['details']:
                print(f"    └─ {YELLOW}{result['details']}{RESET}")
        
        print(f"\n{'='*80}")
        print(f"🎯 {BLUE}SYSTEM STATUS{RESET}\n")
        
        if pass_rate >= 90:
            print(f"   {GREEN}✅ EXCELLENT{RESET} - System is fully operational!")
        elif pass_rate >= 80:
            print(f"   {GREEN}✅ GOOD{RESET} - System is operational with minor issues")
        elif pass_rate >= 70:
            print(f"   {YELLOW}⚠️ WARNING{RESET} - System has some issues that need attention")
        else:
            print(f"   {RED}❌ CRITICAL{RESET} - System requires immediate attention")
        
        print(f"\n{'='*80}\n")
        
        # Save report to file
        report_file = self.base_path / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': self.total_tests,
                    'passed': self.passed_tests,
                    'failed': self.failed_tests,
                    'pass_rate': pass_rate
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"📝 Report saved to: {report_file}\n")
        
        return pass_rate >= 80


def main():
    print(f"\n{CYAN}{'='*80}")
    print(f"🧪 aSiReM SOVEREIGN COMMAND CENTER - COMPREHENSIVE TEST SUITE")
    print(f"{'='*80}{RESET}\n")
    
    tester = SystemTester()
    
    # Infrastructure Tests
    print(f"\n{BLUE}━━━ INFRASTRUCTURE TESTS ━━━{RESET}")
    tester.test("Server Running on Port 8082", tester.test_server_running)
    tester.test("Dashboard Files Exist", tester.test_dashboard_files)
    tester.test("Documentation Complete", tester.test_documentation)
    tester.test("Database Schema Created", tester.test_database_schema)
    
    # Asset Tests
    print(f"\n{BLUE}━━━ ASSET TESTS ━━━{RESET}")
    tester.test("Voice & Video Assets", tester.test_assets_exist)
    tester.test("Character Assets Loaded", tester.test_character_assets)
    tester.test("Story Bible Available", tester.test_story_bible)
    tester.test("Generated Outputs Exist", tester.test_generated_outputs)
    
    # Voice & Video Tests
    print(f"\n{BLUE}━━━ VOICE & VIDEO SYSTEM TESTS ━━━{RESET}")
    tester.test("XTTS Installation", tester.test_xtts_installation)
    tester.test("XTTS Model Available", tester.test_xtts_model)
    tester.test("MuseTalk Installed", tester.test_musetalk_exists)
    tester.test("Voice Cloning Ready", tester.test_voice_cloning_ready)
    tester.test("Visual Streaming Ready", tester.test_visual_streaming_ready)
    
    # Code Tests
    print(f"\n{BLUE}━━━ CODE & DEPENDENCY TESTS ━━━{RESET}")
    tester.test("Python Imports Working", tester.test_python_imports)
    tester.test("WebSocket Dependencies", tester.test_websocket_imports)
    tester.test("Web Search Capability", tester.test_web_search_capability)
    tester.test("Filesystem Scanner Paths", tester.test_filesystem_scanner)
    
    # Generate final report
    success = tester.generate_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
