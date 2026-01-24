"""
🎮 BYTEBOT GESTURE EXECUTOR
============================
Routes hand gesture control to the ByteBot virtual Ubuntu desktop.
Instead of PyAutoGUI (local), uses xdotool inside the Docker container.

This enables Minority Report-style webcam control of the virtual desktop!
"""

import asyncio
import subprocess
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ByteBotActionType(Enum):
    """Types of actions for ByteBot desktop"""
    NONE = "none"
    MOVE_CURSOR = "move_cursor"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    DRAG_START = "drag_start"
    DRAG_MOVE = "drag_move"
    DRAG_END = "drag_end"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    KEY_PRESS = "key_press"
    TYPE_TEXT = "type_text"


@dataclass
class ByteBotConfig:
    """Configuration for ByteBot gesture control"""
    container_name: str = "bytebot-desktop"
    display: str = ":1"
    screen_width: int = 1280
    screen_height: int = 720
    cursor_speed: float = 2.0
    scroll_speed: int = 5
    click_delay_ms: int = 50


class ByteBotGestureExecutor:
    """
    Executes gesture actions on ByteBot virtual Ubuntu desktop.
    Uses xdotool inside the Docker container for mouse/keyboard control.
    """
    
    def __init__(self, config: Optional[ByteBotConfig] = None):
        self.config = config or ByteBotConfig()
        self.is_dragging = False
        self.is_enabled = True
        self.last_action = ByteBotActionType.NONE
        
        # Current cursor position (tracked locally since we can't query xdotool easily)
        self.cursor_x = self.config.screen_width // 2
        self.cursor_y = self.config.screen_height // 2
        
        # Check if container is available
        self._container_ok = self._check_container()
        
        logger.info(f"🎮 ByteBotGestureExecutor initialized (Container: {'✅' if self._container_ok else '❌'})")
    
    def _check_container(self) -> bool:
        """Check if ByteBot container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.config.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=3
            )
            return self.config.container_name in result.stdout
        except Exception:
            return False
    
    def _exec_xdotool(self, command: str) -> bool:
        """Execute xdotool command inside ByteBot container"""
        if not self._container_ok:
            logger.warning("ByteBot container not available")
            return False
        
        try:
            full_cmd = f"DISPLAY={self.config.display} xdotool {command}"
            result = subprocess.run(
                ["docker", "exec", self.config.container_name, "bash", "-c", full_cmd],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"xdotool execution failed: {e}")
            return False
    
    def execute_gesture(self, gesture: str, position: Tuple[float, float], velocity: Tuple[float, float]) -> ByteBotActionType:
        """
        Execute gesture action on ByteBot desktop.
        
        Args:
            gesture: Gesture type string
            position: Normalized hand position (0-1, 0-1)
            velocity: Hand velocity
            
        Returns:
            Action type executed
        """
        if not self.is_enabled:
            return ByteBotActionType.NONE
        
        action = ByteBotActionType.NONE
        
        try:
            if gesture == "point":
                action = self._handle_point(position)
            elif gesture == "pinch":
                action = self._handle_click()
            elif gesture == "grab":
                action = self._handle_grab(position)
            elif gesture == "open_palm":
                action = self._handle_stop()
            elif gesture == "swipe_up":
                action = self._handle_scroll_up(velocity)
            elif gesture == "swipe_down":
                action = self._handle_scroll_down(velocity)
            elif gesture == "swipe_left":
                action = self._handle_navigate_back()
            elif gesture == "swipe_right":
                action = self._handle_navigate_forward()
            elif gesture == "peace":
                action = self._handle_right_click()
            
            self.last_action = action
            return action
            
        except Exception as e:
            logger.error(f"ByteBot action failed: {e}")
            return ByteBotActionType.NONE
    
    def _handle_point(self, position: Tuple[float, float]) -> ByteBotActionType:
        """Move cursor based on hand position - ABSOLUTE MAPPING"""
        # Convert normalized position to screen coordinates (1:1 mapping)
        # Position is mirrored (0,0 is top-right of webcam view)
        self.cursor_x = int((1 - position[0]) * self.config.screen_width)
        self.cursor_y = int(position[1] * self.config.screen_height)
        
        # Ensure cursor stays within bounds
        self.cursor_x = max(0, min(self.config.screen_width, self.cursor_x))
        self.cursor_y = max(0, min(self.config.screen_height, self.cursor_y))
        
        # Move cursor in ByteBot using absolute move
        self._exec_xdotool(f"mousemove {self.cursor_x} {self.cursor_y}")
        
        return ByteBotActionType.MOVE_CURSOR
    
    def _handle_click(self) -> ByteBotActionType:
        """Click at current cursor position"""
        self._exec_xdotool("click 1")
        logger.debug("🖱️ ByteBot click")
        return ByteBotActionType.CLICK
    
    def _handle_right_click(self) -> ByteBotActionType:
        """Right-click at current cursor position"""
        self._exec_xdotool("click 3")
        logger.debug("🖱️ ByteBot right-click")
        return ByteBotActionType.RIGHT_CLICK
    
    def _handle_grab(self, position: Tuple[float, float]) -> ByteBotActionType:
        """Start or continue drag"""
        if not self.is_dragging:
            self._exec_xdotool("mousedown 1")
            self.is_dragging = True
            logger.debug("🤏 ByteBot drag started")
            return ByteBotActionType.DRAG_START
        else:
            # Move while dragging
            self._handle_point(position)
            return ByteBotActionType.DRAG_MOVE
    
    def _handle_stop(self) -> ByteBotActionType:
        """Stop actions / release drag"""
        if self.is_dragging:
            self._exec_xdotool("mouseup 1")
            self.is_dragging = False
            logger.debug("✋ ByteBot drag ended")
            return ByteBotActionType.DRAG_END
        return ByteBotActionType.NONE
    
    def _handle_scroll_up(self, velocity: Tuple[float, float]) -> ByteBotActionType:
        """Scroll up in ByteBot"""
        clicks = max(1, min(10, int(abs(velocity[1]) * self.config.scroll_speed * 5)))
        self._exec_xdotool(f"click --repeat {clicks} 4")  # Button 4 = scroll up
        logger.debug(f"⬆️ ByteBot scroll up ({clicks})")
        return ByteBotActionType.SCROLL_UP
    
    def _handle_scroll_down(self, velocity: Tuple[float, float]) -> ByteBotActionType:
        """Scroll down in ByteBot"""
        clicks = max(1, min(10, int(abs(velocity[1]) * self.config.scroll_speed * 5)))
        self._exec_xdotool(f"click --repeat {clicks} 5")  # Button 5 = scroll down
        logger.debug(f"⬇️ ByteBot scroll down ({clicks})")
        return ByteBotActionType.SCROLL_DOWN
    
    def _handle_navigate_back(self) -> ByteBotActionType:
        """Browser back in ByteBot"""
        self._exec_xdotool("key alt+Left")
        logger.debug("⬅️ ByteBot navigate back")
        return ByteBotActionType.KEY_PRESS
    
    def _handle_navigate_forward(self) -> ByteBotActionType:
        """Browser forward in ByteBot"""
        self._exec_xdotool("key alt+Right")
        logger.debug("➡️ ByteBot navigate forward")
        return ByteBotActionType.KEY_PRESS
    
    # Additional ByteBot-specific actions
    
    def move_to(self, x: int, y: int) -> bool:
        """Move cursor to absolute position"""
        self.cursor_x = x
        self.cursor_y = y
        return self._exec_xdotool(f"mousemove {x} {y}")
    
    def click_at(self, x: int, y: int) -> bool:
        """Click at specific position"""
        return self._exec_xdotool(f"mousemove {x} {y} click 1")
    
    def type_text(self, text: str) -> bool:
        """Type text in ByteBot"""
        # Escape special characters
        text = text.replace("'", "'\\''")
        return self._exec_xdotool(f"type '{text}'")
    
    def press_key(self, key: str) -> bool:
        """Press a key in ByteBot (e.g., 'Return', 'Escape', 'ctrl+c')"""
        return self._exec_xdotool(f"key {key}")
    
    def get_status(self) -> Dict:
        """Get executor status"""
        return {
            "is_enabled": self.is_enabled,
            "container_ok": self._container_ok,
            "is_dragging": self.is_dragging,
            "last_action": self.last_action.value,
            "cursor_position": {"x": self.cursor_x, "y": self.cursor_y},
            "screen_size": {
                "width": self.config.screen_width,
                "height": self.config.screen_height
            }
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable executor"""
        self.is_enabled = enabled
        if not enabled and self.is_dragging:
            self._exec_xdotool("mouseup 1")
            self.is_dragging = False


class ByteBotGestureBridge:
    """
    Bridge between GestureController and ByteBotGestureExecutor.
    Handles gesture events and routes them to ByteBot.
    """
    
    def __init__(self, executor: ByteBotGestureExecutor):
        self.executor = executor
        self._action_cooldown = 0.15  # Faster response for ByteBot
        self._last_action_time = 0.0
    
    async def on_gesture_update(self, state):
        """Handle gesture updates"""
        import time
        current_time = time.time()
        
        # Always allow cursor movement
        if state.gesture.value == "point":
            self.executor.execute_gesture(
                state.gesture.value,
                state.position,
                state.velocity
            )
            return
        
        # Rate limit other actions
        if current_time - self._last_action_time < self._action_cooldown:
            return
        
        # Execute action
        action = self.executor.execute_gesture(
            state.gesture.value,
            state.position,
            state.velocity
        )
        
        if action != ByteBotActionType.NONE and action != ByteBotActionType.MOVE_CURSOR:
            self._last_action_time = current_time


# Factory function
def create_bytebot_executor(
    container_name: str = "bytebot-desktop",
    screen_width: int = 1280,
    screen_height: int = 720
) -> ByteBotGestureExecutor:
    """Create a ByteBot gesture executor"""
    config = ByteBotConfig(
        container_name=container_name,
        screen_width=screen_width,
        screen_height=screen_height
    )
    return ByteBotGestureExecutor(config)


# Singleton instance
_bytebot_executor: Optional[ByteBotGestureExecutor] = None

def get_bytebot_executor() -> ByteBotGestureExecutor:
    """Get or create singleton ByteBot executor"""
    global _bytebot_executor
    if _bytebot_executor is None:
        _bytebot_executor = create_bytebot_executor()
    return _bytebot_executor


if __name__ == "__main__":
    # Test ByteBot gestures
    logging.basicConfig(level=logging.DEBUG)
    
    executor = create_bytebot_executor()
    print(f"Status: {executor.get_status()}")
    
    if executor._container_ok:
        print("\n🎮 Testing ByteBot gesture control...")
        
        # Move cursor to center
        executor.move_to(640, 360)
        print("✅ Moved to center")
        
        # Click
        executor.execute_gesture("pinch", (0.5, 0.5), (0, 0))
        print("✅ Click executed")
        
        # Scroll
        executor.execute_gesture("swipe_down", (0.5, 0.5), (0, 0.5))
        print("✅ Scroll executed")
    else:
        print("❌ ByteBot container not running")
