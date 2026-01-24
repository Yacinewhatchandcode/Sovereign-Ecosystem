#!/usr/bin/env python3
"""
🎯 AGENT ACTION DISPATCHER
===========================
Maps agent intents to concrete desktop/ByteBot actions.

Each specialized agent can now perform REAL actions:
- AZIREM team → Opens VS Code, runs terminal commands, creates files
- BumbleBee team → Opens browser, searches web, generates documents
- Scanner agents → Opens Finder, navigates directories
- SPECTRA team → Creates UI mockups, writes CSS

This is the bridge between "agent thinking" and "visible action".
"""

import asyncio
import subprocess
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import platform


class ActionType(Enum):
    """Types of actions agents can perform"""
    # File Operations
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    DELETE_FILE = "delete_file"
    READ_FILE = "read_file"
    
    # Application Control
    OPEN_VSCODE = "open_vscode"
    OPEN_TERMINAL = "open_terminal"
    OPEN_BROWSER = "open_browser"
    OPEN_FINDER = "open_finder"
    OPEN_PREVIEW = "open_preview"
    
    # Command Execution
    RUN_COMMAND = "run_command"
    RUN_PYTHON = "run_python"
    RUN_NPM = "run_npm"
    RUN_GIT = "run_git"
    
    # Browser Actions
    NAVIGATE_URL = "navigate_url"
    SEARCH_WEB = "search_web"
    SCREENSHOT_PAGE = "screenshot_page"
    
    # Document Generation
    CREATE_PDF = "create_pdf"
    CREATE_DOCX = "create_docx"
    CREATE_XLSX = "create_xlsx"
    CREATE_PPTX = "create_pptx"
    
    # UI Actions
    TYPE_TEXT = "type_text"
    CLICK = "click"
    SCROLL = "scroll"
    HIGHLIGHT = "highlight"


@dataclass
class ActionResult:
    """Result from executing an agent action"""
    action_type: str
    agent_id: str
    success: bool
    output: str = ""
    error: str = ""
    screenshot_path: Optional[str] = None
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass 
class AgentAction:
    """Defines an action an agent wants to perform"""
    agent_id: str
    agent_type: str  # azirem, bumblebee, scanner, spectra
    action_type: ActionType
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


class AgentActionDispatcher:
    """
    Central dispatcher for all agent actions.
    Routes actions to appropriate executors (local desktop or ByteBot).
    """
    
    # Action capabilities per agent type
    AGENT_CAPABILITIES = {
        "azirem": {
            "description": "Master Coding Orchestrator",
            "actions": [
                ActionType.OPEN_VSCODE, ActionType.OPEN_TERMINAL,
                ActionType.CREATE_FILE, ActionType.EDIT_FILE, ActionType.READ_FILE,
                ActionType.RUN_COMMAND, ActionType.RUN_PYTHON, ActionType.RUN_NPM, ActionType.RUN_GIT,
            ],
            "sub_agents": {
                "architecture_dev": ["CREATE_FILE", "OPEN_VSCODE"],
                "product_manager": ["CREATE_FILE", "OPEN_BROWSER"],
                "qa_specialist": ["RUN_COMMAND", "RUN_PYTHON"],
                "backend_dev": ["CREATE_FILE", "RUN_PYTHON", "OPEN_TERMINAL"],
                "frontend_dev": ["CREATE_FILE", "RUN_NPM", "OPEN_BROWSER"],
                "devops_engineer": ["RUN_COMMAND", "OPEN_TERMINAL"],
                "security_specialist": ["RUN_COMMAND", "READ_FILE"],
            }
        },
        "bumblebee": {
            "description": "Master Research & Document Orchestrator",
            "actions": [
                ActionType.OPEN_BROWSER, ActionType.NAVIGATE_URL, ActionType.SEARCH_WEB,
                ActionType.CREATE_PDF, ActionType.CREATE_DOCX, ActionType.CREATE_XLSX, ActionType.CREATE_PPTX,
                ActionType.SCREENSHOT_PAGE,
            ],
            "sub_agents": {
                "web_search_specialist": ["OPEN_BROWSER", "SEARCH_WEB", "NAVIGATE_URL"],
                "research_analyst": ["READ_FILE", "SEARCH_WEB"],
                "pdf_processor": ["CREATE_PDF", "OPEN_PREVIEW"],
                "word_processor": ["CREATE_DOCX"],
                "excel_processor": ["CREATE_XLSX"],
                "powerpoint_processor": ["CREATE_PPTX"],
                "document_synthesizer": ["CREATE_FILE", "CREATE_PDF"],
            }
        },
        "scanner": {
            "description": "File System Discovery & Analysis",
            "actions": [
                ActionType.OPEN_FINDER, ActionType.READ_FILE,
                ActionType.RUN_COMMAND,
            ],
            "sub_agents": {
                "scanner_agent": ["OPEN_FINDER", "READ_FILE"],
                "classifier_agent": ["READ_FILE"],
                "extractor_agent": ["READ_FILE", "OPEN_VSCODE"],
                "dependency_resolver": ["RUN_COMMAND"],
                "merger_agent": ["CREATE_FILE"],
                "writer_agent": ["CREATE_FILE"],
            }
        },
        "spectra": {
            "description": "UI/UX Design & Visual",
            "actions": [
                ActionType.OPEN_VSCODE, ActionType.OPEN_BROWSER,
                ActionType.CREATE_FILE, ActionType.SCREENSHOT_PAGE,
            ],
            "sub_agents": {
                "creative_director": ["OPEN_BROWSER", "SCREENSHOT_PAGE"],
                "interface_architect": ["CREATE_FILE", "OPEN_VSCODE"],
                "motion_choreographer": ["CREATE_FILE", "OPEN_BROWSER"],
            }
        }
    }
    
    def __init__(self, 
                 use_bytebot: bool = False,
                 bytebot_url: str = "http://localhost:8080",
                 output_dir: str = "outputs/agent_actions"):
        self.use_bytebot = use_bytebot
        self.bytebot_url = bytebot_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_mac = platform.system() == "Darwin"
        self.action_log: List[ActionResult] = []
        self.callback: Optional[Callable] = None
        
        # Try to import pyautogui for UI automation
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.has_pyautogui = True
        except ImportError:
            self.has_pyautogui = False
            print("⚠️ pyautogui not available - UI automation disabled")
    
    def set_callback(self, callback: Callable):
        """Set callback for action events (for WebSocket updates)"""
        self.callback = callback
    
    async def emit(self, event_type: str, data: dict):
        """Emit event to dashboard"""
        if self.callback:
            await self.callback(event_type, data)
    
    async def dispatch(self, action: AgentAction) -> ActionResult:
        """
        Main dispatch method - routes action to appropriate executor.
        """
        start_time = time.time()
        
        # Emit reasoning/thought if provided
        reasoning = action.params.get("reasoning") or action.description
        if reasoning:
            await self.emit("agent_thought", {
                "agent_id": action.agent_id,
                "agent_name": action.agent_id.capitalize(),
                "thought": reasoning,
                "action": action.action_type.value,
                "speed": "fast"
            })

        await self.emit("action_start", {
            "agent_id": action.agent_id,
            "agent_type": action.agent_type,
            "action": action.action_type.value,
            "description": action.description
        })
        
        try:
            # Validate action is allowed for this agent type
            if not self._validate_action(action):
                raise ValueError(f"Action {action.action_type} not allowed for {action.agent_type}")
            
            # Route to appropriate executor
            if self.use_bytebot:
                result = await self._execute_bytebot(action)
            else:
                result = await self._execute_local(action)
            
            result.duration_ms = int((time.time() - start_time) * 1000)
            self.action_log.append(result)
            
            await self.emit("action_complete", {
                "agent_id": action.agent_id,
                "action": action.action_type.value,
                "success": result.success,
                "output": result.output[:500] if result.output else "",
                "duration_ms": result.duration_ms
            })
            
            return result
            
        except Exception as e:
            result = ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
            self.action_log.append(result)
            
            await self.emit("action_error", {
                "agent_id": action.agent_id,
                "action": action.action_type.value,
                "error": str(e)
            })
            
            return result
    
    def _validate_action(self, action: AgentAction) -> bool:
        """Check if action is allowed for this agent type"""
        if action.agent_type not in self.AGENT_CAPABILITIES:
            return False
        
        allowed_actions = self.AGENT_CAPABILITIES[action.agent_type]["actions"]
        return action.action_type in allowed_actions
    
    async def _execute_local(self, action: AgentAction) -> ActionResult:
        """Execute action on local desktop (macOS)"""
        
        handlers = {
            ActionType.OPEN_VSCODE: self._open_vscode,
            ActionType.OPEN_TERMINAL: self._open_terminal,
            ActionType.OPEN_BROWSER: self._open_browser,
            ActionType.OPEN_FINDER: self._open_finder,
            ActionType.OPEN_PREVIEW: self._open_preview,
            ActionType.CREATE_FILE: self._create_file,
            ActionType.EDIT_FILE: self._edit_file,
            ActionType.READ_FILE: self._read_file,
            ActionType.RUN_COMMAND: self._run_command,
            ActionType.RUN_PYTHON: self._run_python,
            ActionType.RUN_NPM: self._run_npm,
            ActionType.RUN_GIT: self._run_git,
            ActionType.NAVIGATE_URL: self._navigate_url,
            ActionType.SEARCH_WEB: self._search_web,
            ActionType.TYPE_TEXT: self._type_text,
            ActionType.CREATE_PDF: self._create_pdf,
        }
        
        handler = handlers.get(action.action_type)
        if not handler:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=f"No handler for action: {action.action_type}"
            )
        
        return await handler(action)
    
    async def _execute_bytebot(self, action: AgentAction) -> ActionResult:
        """Execute action in ByteBot Docker container"""
        # Import ByteBot bridge if available
        try:
            from bytebot_agent_bridge import ByteBotAgentBridge
            bridge = ByteBotAgentBridge()
            
            # Map action to ByteBot command
            if action.action_type == ActionType.OPEN_VSCODE:
                path = action.params.get("path", "/workspace")
                result = await bridge.open_vscode(path, action.agent_id)
            elif action.action_type == ActionType.OPEN_BROWSER:
                url = action.params.get("url", "https://google.com")
                result = await bridge.open_browser(url, action.agent_id)
            elif action.action_type == ActionType.OPEN_TERMINAL:
                result = await bridge.open_terminal(action.agent_id)
            elif action.action_type == ActionType.OPEN_FINDER:
                path = action.params.get("path", "/workspace")
                result = await bridge.open_finder(path, action.agent_id)
            elif action.action_type == ActionType.CREATE_FILE:
                filepath = action.params.get("filepath", "/tmp/agent_file.txt")
                content = action.params.get("content", "")
                result = await bridge.create_file(filepath, content, action.agent_id)
            elif action.action_type == ActionType.SEARCH_WEB:
                query = action.params.get("query", "")
                url = f"https://www.google.com/search?q={query}"
                result = await bridge.open_browser(url, action.agent_id)
            elif action.action_type == ActionType.RUN_COMMAND:
                cmd = action.params.get("command", "echo 'No command'")
                result = await bridge.execute_command(cmd, action.agent_id)
            elif action.action_type == ActionType.SCREENSHOT_PAGE:
                screenshot_path = await bridge.capture_screenshot(action.agent_id)
                result = {"output": f"Screenshot saved to {screenshot_path}"} if screenshot_path else {"error": "Failed to capture screenshot"}
            else:
                result = {"error": f"ByteBot doesn't support: {action.action_type}"}
            
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success="error" not in result,
                output=str(result.get("output", result)),
                error=result.get("error", "")
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=f"ByteBot execution failed: {e}"
            )
    
    # =========================================================================
    # LOCAL ACTION HANDLERS
    # =========================================================================
    
    async def _open_vscode(self, action: AgentAction) -> ActionResult:
        """Open VS Code at specified path"""
        path = action.params.get("path", ".")
        try:
            subprocess.Popen(["code", path])
            await asyncio.sleep(1)  # Wait for VS Code to open
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Opened VS Code at: {path}"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _open_terminal(self, action: AgentAction) -> ActionResult:
        """Open Terminal app"""
        try:
            if self.is_mac:
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                subprocess.Popen(["gnome-terminal"])
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output="Opened Terminal"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _open_browser(self, action: AgentAction) -> ActionResult:
        """Open browser (Firefox/Chrome)"""
        url = action.params.get("url", "https://google.com")
        try:
            if self.is_mac:
                subprocess.Popen(["open", "-a", "Firefox", url])
            else:
                subprocess.Popen(["firefox", url])
            await asyncio.sleep(2)
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Opened browser at: {url}"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _open_finder(self, action: AgentAction) -> ActionResult:
        """Open Finder at specified path"""
        path = action.params.get("path", "~")
        path = os.path.expanduser(path)
        try:
            if self.is_mac:
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["nautilus", path])
            await asyncio.sleep(1)
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Opened Finder at: {path}"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _open_preview(self, action: AgentAction) -> ActionResult:
        """Open file in Preview (macOS)"""
        filepath = action.params.get("filepath", "")
        try:
            if self.is_mac:
                subprocess.Popen(["open", "-a", "Preview", filepath])
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Opened in Preview: {filepath}"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _create_file(self, action: AgentAction) -> ActionResult:
        """Create a new file with content"""
        filepath = action.params.get("filepath", "")
        content = action.params.get("content", "")
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Created file: {filepath} ({len(content)} bytes)"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _edit_file(self, action: AgentAction) -> ActionResult:
        """Edit an existing file"""
        filepath = action.params.get("filepath", "")
        content = action.params.get("content", "")
        append = action.params.get("append", False)
        try:
            path = Path(filepath)
            if append and path.exists():
                existing = path.read_text()
                content = existing + "\n" + content
            path.write_text(content)
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Edited file: {filepath}"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _read_file(self, action: AgentAction) -> ActionResult:
        """Read file content"""
        filepath = action.params.get("filepath", "")
        try:
            path = Path(filepath)
            content = path.read_text()
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=content[:5000]  # Limit output size
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _run_command(self, action: AgentAction) -> ActionResult:
        """Run a shell command"""
        command = action.params.get("command", "")
        cwd = action.params.get("cwd", None)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd
            )
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=result.returncode == 0,
                output=result.stdout[:5000] if result.stdout else "",
                error=result.stderr[:1000] if result.stderr else ""
            )
        except subprocess.TimeoutExpired:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error="Command timed out after 60 seconds"
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _run_python(self, action: AgentAction) -> ActionResult:
        """Run Python script or code"""
        script = action.params.get("script", "")
        code = action.params.get("code", "")
        
        if script:
            command = f"python3 {script}"
        elif code:
            command = f'python3 -c "{code}"'
        else:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error="No script or code provided"
            )
        
        action.params["command"] = command
        return await self._run_command(action)
    
    async def _run_npm(self, action: AgentAction) -> ActionResult:
        """Run npm command"""
        npm_cmd = action.params.get("npm_command", "run dev")
        cwd = action.params.get("cwd", ".")
        action.params["command"] = f"npm {npm_cmd}"
        action.params["cwd"] = cwd
        return await self._run_command(action)
    
    async def _run_git(self, action: AgentAction) -> ActionResult:
        """Run git command"""
        git_cmd = action.params.get("git_command", "status")
        cwd = action.params.get("cwd", ".")
        action.params["command"] = f"git {git_cmd}"
        action.params["cwd"] = cwd
        return await self._run_command(action)
    
    async def _navigate_url(self, action: AgentAction) -> ActionResult:
        """Navigate to URL (reuses open_browser)"""
        return await self._open_browser(action)
    
    async def _search_web(self, action: AgentAction) -> ActionResult:
        """Search the web"""
        query = action.params.get("query", "")
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        action.params["url"] = search_url
        return await self._open_browser(action)
    
    async def _type_text(self, action: AgentAction) -> ActionResult:
        """Type text using pyautogui"""
        text = action.params.get("text", "")
        if not self.has_pyautogui:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error="pyautogui not available"
            )
        try:
            self.pyautogui.typewrite(text, interval=0.02)
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=True,
                output=f"Typed: {text[:50]}..."
            )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    async def _create_pdf(self, action: AgentAction) -> ActionResult:
        """Create a PDF document"""
        output_path = action.params.get("output_path", "output.pdf")
        content = action.params.get("content", "No content provided")
        title = action.params.get("title", "Document")
        
        try:
            # Use reportlab if available, otherwise use a simple text-to-pdf approach
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                c = canvas.Canvas(output_path, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(72, 750, title)
                c.setFont("Helvetica", 12)
                
                # Split content into lines
                y = 720
                for line in content.split('\n')[:50]:  # Limit to 50 lines
                    c.drawString(72, y, line[:80])  # Limit line length
                    y -= 15
                    if y < 72:
                        c.showPage()
                        y = 750
                
                c.save()
                return ActionResult(
                    action_type=action.action_type.value,
                    agent_id=action.agent_id,
                    success=True,
                    output=f"Created PDF: {output_path}"
                )
            except ImportError:
                # Fallback: create a text file with .pdf extension note
                Path(output_path.replace('.pdf', '.txt')).write_text(f"# {title}\n\n{content}")
                return ActionResult(
                    action_type=action.action_type.value,
                    agent_id=action.agent_id,
                    success=True,
                    output=f"Created text file (reportlab not installed): {output_path}"
                )
        except Exception as e:
            return ActionResult(
                action_type=action.action_type.value,
                agent_id=action.agent_id,
                success=False,
                error=str(e)
            )
    
    # =========================================================================
    # Convenience Methods for Agent Teams
    # =========================================================================
    
    async def azirem_code(self, filepath: str, content: str, open_editor: bool = True) -> ActionResult:
        """AZIREM: Create a code file and optionally open in VS Code"""
        action = AgentAction(
            agent_id="azirem",
            agent_type="azirem",
            action_type=ActionType.CREATE_FILE,
            params={"filepath": filepath, "content": content},
            description=f"Creating code file: {filepath}"
        )
        result = await self.dispatch(action)
        
        if result.success and open_editor:
            editor_action = AgentAction(
                agent_id="azirem",
                agent_type="azirem",
                action_type=ActionType.OPEN_VSCODE,
                params={"path": filepath},
                description=f"Opening in VS Code: {filepath}"
            )
            await self.dispatch(editor_action)
        
        return result
    
    async def bumblebee_research(self, query: str) -> ActionResult:
        """BumbleBee: Search the web for research"""
        action = AgentAction(
            agent_id="bumblebee",
            agent_type="bumblebee",
            action_type=ActionType.SEARCH_WEB,
            params={"query": query},
            description=f"Researching: {query}"
        )
        return await self.dispatch(action)
    
    async def scanner_explore(self, path: str) -> ActionResult:
        """Scanner: Open Finder to explore directory"""
        action = AgentAction(
            agent_id="scanner",
            agent_type="scanner",
            action_type=ActionType.OPEN_FINDER,
            params={"path": path},
            description=f"Exploring directory: {path}"
        )
        return await self.dispatch(action)
    
    async def spectra_preview(self, url: str) -> ActionResult:
        """SPECTRA: Preview UI in browser"""
        action = AgentAction(
            agent_id="spectra",
            agent_type="spectra",
            action_type=ActionType.OPEN_BROWSER,
            params={"url": url},
            description=f"Previewing UI: {url}"
        )
        return await self.dispatch(action)
    
    def get_action_log(self) -> List[Dict]:
        """Get log of all executed actions"""
        return [
            {
                "action": r.action_type,
                "agent_id": r.agent_id,
                "success": r.success,
                "output": r.output[:200] if r.output else "",
                "error": r.error,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp
            }
            for r in self.action_log
        ]
    
    def get_agent_stats(self) -> Dict:
        """Get statistics per agent type"""
        stats = {}
        for result in self.action_log:
            agent_type = result.agent_id.split("_")[0] if "_" in result.agent_id else result.agent_id
            if agent_type not in stats:
                stats[agent_type] = {"total": 0, "success": 0, "failed": 0}
            stats[agent_type]["total"] += 1
            if result.success:
                stats[agent_type]["success"] += 1
            else:
                stats[agent_type]["failed"] += 1
        return stats


# Singleton instance
_dispatcher: Optional[AgentActionDispatcher] = None

def get_dispatcher(use_bytebot: bool = False) -> AgentActionDispatcher:
    """Get or create the singleton dispatcher"""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = AgentActionDispatcher(use_bytebot=use_bytebot)
    return _dispatcher


# CLI Testing
if __name__ == "__main__":
    async def test_dispatcher():
        dispatcher = get_dispatcher()
        
        print("🎯 Agent Action Dispatcher Test")
        print("=" * 50)
        
        # Test AZIREM - Create a file
        print("\n1. Testing AZIREM: Create file...")
        result = await dispatcher.azirem_code(
            filepath="/tmp/test_agent_output/hello.py",
            content="#!/usr/bin/env python3\nprint('Hello from AZIREM!')",
            open_editor=False
        )
        print(f"   Result: {'✅' if result.success else '❌'} {result.output or result.error}")
        
        # Test Scanner - Open Finder
        print("\n2. Testing Scanner: Explore directory...")
        result = await dispatcher.scanner_explore("/tmp")
        print(f"   Result: {'✅' if result.success else '❌'} {result.output or result.error}")
        
        # Test BumbleBee - Search web
        print("\n3. Testing BumbleBee: Web search...")
        result = await dispatcher.bumblebee_research("AI agents 2026")
        print(f"   Result: {'✅' if result.success else '❌'} {result.output or result.error}")
        
        # Print stats
        print("\n📊 Action Statistics:")
        print(json.dumps(dispatcher.get_agent_stats(), indent=2))
    
    asyncio.run(test_dispatcher())
