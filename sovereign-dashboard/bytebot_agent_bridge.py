#!/usr/bin/env python3
"""
🔌 BYTEBOT AGENT INTEGRATION
============================
Connects ByteBot VNC container to the aSiReM agent system.

Agents can now:
- Execute commands in ByteBot desktop
- Capture screenshots
- Control browser/IDE
- Monitor visual output
"""

import asyncio
import aiohttp
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class ByteBotAgentBridge:
    """
    Bridge between aSiReM agents and ByteBot Docker container.
    Allows agents to control and monitor the ByteBot desktop.
    """
    
    def __init__(self):
        self.container_name = "bytebot-desktop"
        self.vnc_url = "http://localhost:9990"
        self.output_dir = Path("outputs/bytebot_captures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_connected = False
        
    async def check_connection(self) -> bool:
        """Check if ByteBot container is accessible."""
        try:
            # Check if container is running
            def run_check():
                return subprocess.run(
                    ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            result = await asyncio.to_thread(run_check)
            
            if self.container_name in result.stdout:
                # Check if VNC is accessible
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.vnc_url}/novnc/vnc.html",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        self.is_connected = resp.status == 200
                        return self.is_connected
        except Exception as e:
            print(f"⚠️ ByteBot connection check failed: {e}")
            
        self.is_connected = False
        return False
        
    async def execute_command(self, command: str, agent_id: str = "system") -> Dict:
        """
        Execute a command in the ByteBot container.
        
        Args:
            command: Shell command to execute
            agent_id: ID of the agent executing the command
            
        Returns:
            Dict with stdout, stderr, and exit_code
        """
        try:
            # Use asyncio.to_thread to make subprocess.run non-blocking
            def run_docker():
                return subprocess.run(
                    ["docker", "exec", self.container_name, "bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            result = await asyncio.to_thread(run_docker)
            
            response = {
                "agent_id": agent_id,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0
            }
            
            # Save command log
            log_file = self.output_dir / f"command_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(response) + '\n')
                
            return response
            
        except Exception as e:
            return {
                "agent_id": agent_id,
                "command": command,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
    async def capture_screenshot(self, agent_id: str = "system") -> Optional[str]:
        """
        Capture a screenshot from ByteBot desktop.
        
        Args:
            agent_id: ID of the agent requesting the screenshot
            
        Returns:
            Path to saved screenshot or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.output_dir / f"{agent_id}_screenshot_{timestamp}.png"
            
            # Use scrot to capture screenshot in container
            await self.execute_command(
                f"DISPLAY=:0 scrot /tmp/screenshot.png",
                agent_id
            )
            
            # Copy screenshot from container to host
            def run_cp():
                return subprocess.run(
                    ["docker", "cp", f"{self.container_name}:/tmp/screenshot.png", str(screenshot_path)],
                    capture_output=True,
                    timeout=10
                )
            await asyncio.to_thread(run_cp)
            
            if screenshot_path.exists():
                print(f"📸 Screenshot captured: {screenshot_path}")
                return str(screenshot_path)
                
        except Exception as e:
            print(f"⚠️ Screenshot capture failed: {e}")
            
        return None
        
    async def open_browser(self, url: str, agent_id: str = "system") -> Dict:
        """Open a URL in the browser inside ByteBot."""
        # Use x-www-browser as a generic pointer or firefox-esr if available
        command = f"DISPLAY=:0 x-www-browser '{url}' &"
        return await self.execute_command(command, agent_id)
        
    async def open_terminal(self, agent_id: str = "system") -> Dict:
        """Open a terminal in ByteBot."""
        command = "DISPLAY=:0 xfce4-terminal &"
        return await self.execute_command(command, agent_id)
        
    async def open_vscode(self, path: str = "/workspace", agent_id: str = "system") -> Dict:
        """Open VS Code in ByteBot."""
        # Must use --no-sandbox and --user-data-dir when running as root
        command = f"DISPLAY=:0 code '{path}' --no-sandbox --user-data-dir=/tmp/vs-root &"
        return await self.execute_command(command, agent_id)
        
    async def open_finder(self, path: str = "/workspace", agent_id: str = "system") -> Dict:
        """Open file manager (Thunar) in ByteBot."""
        command = f"DISPLAY=:0 thunar '{path}' &"
        return await self.execute_command(command, agent_id)

    async def create_file(self, filepath: str, content: str, agent_id: str = "system") -> Dict:
        """Create a file with content inside ByteBot."""
        # Create parent directory first
        dir_path = Path(filepath).parent
        await self.execute_command(f"mkdir -p '{dir_path}'", agent_id)
        
        # Write content using base64 to avoid escaping issues with shell
        import base64
        b64_content = base64.b64encode(content.encode()).decode()
        command = f"echo '{b64_content}' | base64 -d > '{filepath}'"
        return await self.execute_command(command, agent_id)
        
    async def list_running_apps(self, agent_id: str = "system") -> Dict:
        """List running applications in ByteBot."""
        command = "ps aux | grep -E '(firefox|code|terminal)' | grep -v grep"
        return await self.execute_command(command, agent_id)
        
    async def scan_directory(self, path: str, agent_id: str = "scanner") -> Dict:
        """Scan a directory and return file structure."""
        command = f"find '{path}' -maxdepth 3 -type f -name '*.py' -o -name '*.js' -o -name '*.ts' | head -50"
        result = await self.execute_command(command, agent_id)
        
        if result["success"]:
            files = [f.strip() for f in result["stdout"].split('\n') if f.strip()]
            result["files"] = files
            result["file_count"] = len(files)
            
        return result
        
    async def read_container_file(self, filepath: str, agent_id: str = "system") -> str:
        """Read full content of a file inside ByteBot."""
        command = f"cat '{filepath}'"
        result = await self.execute_command(command, agent_id)
        return result.get("stdout", "")
        
    async def analyze_code_file(self, filepath: str, agent_id: str = "classifier") -> Dict:
        """Analyze a code file in ByteBot."""
        # Get file info
        info_cmd = f"wc -l '{filepath}' && file '{filepath}'"
        info_result = await self.execute_command(info_cmd, agent_id)
        
        # Get file content preview
        content_cmd = f"head -100 '{filepath}'"
        content_result = await self.execute_command(content_cmd, agent_id)
        
        return {
            "filepath": filepath,
            "info": info_result["stdout"],
            "preview": content_result["stdout"][:500],
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
        
    async def start_visual_scan(self, paths: List[str], agent_id: str = "scanner") -> Dict:
        """
        Start a visual scan session in ByteBot.
        Opens file browser, terminal, and VS Code for visual monitoring.
        """
        results = []
        
        # Open terminal
        terminal_result = await self.open_terminal(agent_id)
        results.append({"action": "open_terminal", "result": terminal_result})
        
        # Open VS Code with first path
        if paths:
            vscode_result = await self.open_vscode(paths[0], agent_id)
            results.append({"action": "open_vscode", "result": vscode_result})
            
        # Scan directories
        for path in paths:
            scan_result = await self.scan_directory(path, agent_id)
            results.append({"action": "scan_directory", "path": path, "result": scan_result})
            
        # Capture screenshot of the setup
        await asyncio.sleep(2)  # Wait for apps to open
        screenshot = await self.capture_screenshot(agent_id)
        
        return {
            "agent_id": agent_id,
            "action": "visual_scan_started",
            "paths": paths,
            "results": results,
            "screenshot": screenshot,
            "timestamp": datetime.now().isoformat()
        }


# Integration with existing agent system
async def integrate_with_agents():
    """
    Integrate ByteBot with the agent orchestrator.
    This should be called from real_agent_system.py
    """
    bridge = ByteBotAgentBridge()
    
    # Check connection
    connected = await bridge.check_connection()
    if not connected:
        print("⚠️ ByteBot not connected. Make sure container is running.")
        return None
        
    print("✅ ByteBot Agent Bridge connected!")
    return bridge


# CLI testing
if __name__ == "__main__":
    async def main():
        print("🔌 ByteBot Agent Integration Test")
        print("=" * 50)
        
        bridge = ByteBotAgentBridge()
        
        # Test connection
        print("\n1. Testing connection...")
        connected = await bridge.check_connection()
        print(f"   Connected: {connected}")
        
        if not connected:
            print("   ⚠️ ByteBot container not accessible")
            return
            
        # Test command execution
        print("\n2. Testing command execution...")
        result = await bridge.execute_command("echo 'Hello from ByteBot!'", "test_agent")
        print(f"   Output: {result['stdout']}")
        
        # Test screenshot
        print("\n3. Testing screenshot capture...")
        screenshot = await bridge.capture_screenshot("test_agent")
        print(f"   Screenshot: {screenshot}")
        
        # Test browser
        print("\n4. Opening browser...")
        browser_result = await bridge.open_browser("https://github.com", "test_agent")
        print(f"   Browser opened: {browser_result['success']}")
        
        # Test directory scan
        print("\n5. Scanning directory...")
        scan_result = await bridge.scan_directory("/workspace", "scanner")
        print(f"   Files found: {scan_result.get('file_count', 0)}")
        
        # Test visual scan
        print("\n6. Starting visual scan...")
        visual_result = await bridge.start_visual_scan(["/workspace"], "scanner")
        print(f"   Visual scan complete: {visual_result['screenshot']}")
        
        print("\n✅ All tests completed!")
        
    asyncio.run(main())
