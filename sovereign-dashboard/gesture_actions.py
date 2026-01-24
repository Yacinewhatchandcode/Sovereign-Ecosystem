"""
aSiReM Gesture Actions - Desktop/Browser Control via Gestures
Maps detected gestures to system actions using PyAutoGUI.
"""

import asyncio
import logging
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional, Tuple

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.01    # Small pause between actions
except ImportError:
    pyautogui = None

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of system actions"""
    NONE = "none"
    MOVE_CURSOR = "move_cursor"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    DRAG_START = "drag_start"
    DRAG_END = "drag_end"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    NAVIGATE_BACK = "navigate_back"
    NAVIGATE_FORWARD = "navigate_forward"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    OPEN_FILE_PICKER = "open_file_picker"
    SWITCH_APP = "switch_app"
    STOP = "stop"


@dataclass
class ActionConfig:
    """Configuration for action execution"""
    screen_width: int = 1920
    screen_height: int = 1080
    cursor_speed: float = 1.5      # Multiplier for cursor movement
    scroll_speed: int = 3          # Lines per scroll action
    click_duration: float = 0.05   # Click hold time
    enable_desktop_control: bool = True
    enable_browser_control: bool = True
    safe_zone_margin: int = 50     # Pixels from edge to trigger failsafe


class GestureActionExecutor:
    """
    Executes system actions based on gesture input.
    Maps gesture types to PyAutoGUI commands.
    """
    
    def __init__(self, config: Optional[ActionConfig] = None):
        self.config = config or ActionConfig()
        self.is_dragging = False
        self.is_enabled = True
        self.last_action = ActionType.NONE
        self._is_mac = platform.system() == "Darwin"
        
        # Get actual screen size
        if pyautogui:
            size = pyautogui.size()
            self.config.screen_width = size.width
            self.config.screen_height = size.height
        
        # Custom action handlers
        self._custom_handlers: Dict[ActionType, Callable] = {}
        
        logger.info(f"🎮 GestureActionExecutor initialized ({self.config.screen_width}x{self.config.screen_height})")
    
    def execute_gesture(self, gesture: str, position: Tuple[float, float], velocity: Tuple[float, float]) -> ActionType:
        """
        Execute action based on gesture type.
        
        Args:
            gesture: Gesture type string (from GestureType enum)
            position: Normalized hand position (0-1, 0-1)
            velocity: Hand velocity (normalized units/sec)
            
        Returns:
            ActionType that was executed
        """
        if not self.is_enabled or not pyautogui:
            return ActionType.NONE
        
        action = ActionType.NONE
        
        try:
            if gesture == "point":
                action = self._handle_point(position)
            elif gesture == "pinch":
                action = self._handle_pinch()
            elif gesture == "grab":
                action = self._handle_grab(position)
            elif gesture == "open_palm":
                action = self._handle_open_palm()
            elif gesture == "swipe_left":
                action = self._handle_swipe_left()
            elif gesture == "swipe_right":
                action = self._handle_swipe_right()
            elif gesture == "swipe_up":
                action = self._handle_swipe_up(velocity)
            elif gesture == "swipe_down":
                action = self._handle_swipe_down(velocity)
            elif gesture == "spread":
                action = self._handle_spread()
            elif gesture == "peace":
                action = self._handle_peace()
            
            # Check for custom handler
            if action in self._custom_handlers:
                self._custom_handlers[action]()
            
            self.last_action = action
            return action
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionType.NONE
    
    def _handle_point(self, position: Tuple[float, float]) -> ActionType:
        """Move cursor based on hand position"""
        if not self.config.enable_desktop_control:
            return ActionType.NONE
        
        # Convert normalized position to screen coordinates
        # Position is mirrored (0,0 is top-right of webcam view)
        x = int((1 - position[0]) * self.config.screen_width)
        y = int(position[1] * self.config.screen_height)
        
        # Apply speed multiplier (relative movement)
        current_x, current_y = pyautogui.position()
        target_x = current_x + int((x - self.config.screen_width/2) * self.config.cursor_speed * 0.02)
        target_y = current_y + int((y - self.config.screen_height/2) * self.config.cursor_speed * 0.02)
        
        # Clamp to screen bounds with safe zone
        margin = self.config.safe_zone_margin
        target_x = max(margin, min(self.config.screen_width - margin, target_x))
        target_y = max(margin, min(self.config.screen_height - margin, target_y))
        
        pyautogui.moveTo(target_x, target_y, duration=0)
        return ActionType.MOVE_CURSOR
    
    def _handle_pinch(self) -> ActionType:
        """Click at current cursor position"""
        if not self.config.enable_desktop_control:
            return ActionType.NONE
        
        pyautogui.click(duration=self.config.click_duration)
        logger.debug("🖱️ Click executed")
        return ActionType.CLICK
    
    def _handle_grab(self, position: Tuple[float, float]) -> ActionType:
        """Start/continue drag operation"""
        if not self.config.enable_desktop_control:
            return ActionType.NONE
        
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True
            logger.debug("🤏 Drag started")
            return ActionType.DRAG_START
        else:
            # Continue drag - move cursor while holding
            self._handle_point(position)
            return ActionType.MOVE_CURSOR
    
    def _handle_open_palm(self) -> ActionType:
        """Stop all actions"""
        if self.is_dragging and pyautogui:
            pyautogui.mouseUp()
            self.is_dragging = False
            logger.debug("✋ Drag ended")
        
        logger.debug("✋ Stop action")
        return ActionType.STOP
    
    def _handle_swipe_left(self) -> ActionType:
        """Browser back navigation"""
        if not self.config.enable_browser_control:
            return ActionType.NONE
        
        if self._is_mac:
            pyautogui.hotkey('command', '[')
        else:
            pyautogui.hotkey('alt', 'left')
        
        logger.debug("⬅️ Navigate back")
        return ActionType.NAVIGATE_BACK
    
    def _handle_swipe_right(self) -> ActionType:
        """Browser forward navigation"""
        if not self.config.enable_browser_control:
            return ActionType.NONE
        
        if self._is_mac:
            pyautogui.hotkey('command', ']')
        else:
            pyautogui.hotkey('alt', 'right')
        
        logger.debug("➡️ Navigate forward")
        return ActionType.NAVIGATE_FORWARD
    
    def _handle_swipe_up(self, velocity: Tuple[float, float]) -> ActionType:
        """Scroll up"""
        if not self.config.enable_browser_control:
            return ActionType.NONE
        
        # Scale scroll by velocity
        scroll_amount = int(abs(velocity[1]) * self.config.scroll_speed * 10)
        scroll_amount = max(1, min(scroll_amount, 20))  # Clamp
        
        pyautogui.scroll(scroll_amount)
        logger.debug(f"⬆️ Scroll up ({scroll_amount})")
        return ActionType.SCROLL_UP
    
    def _handle_swipe_down(self, velocity: Tuple[float, float]) -> ActionType:
        """Scroll down"""
        if not self.config.enable_browser_control:
            return ActionType.NONE
        
        scroll_amount = int(abs(velocity[1]) * self.config.scroll_speed * 10)
        scroll_amount = max(1, min(scroll_amount, 20))
        
        pyautogui.scroll(-scroll_amount)
        logger.debug(f"⬇️ Scroll down ({scroll_amount})")
        return ActionType.SCROLL_DOWN
    
    def _handle_spread(self) -> ActionType:
        """Zoom in"""
        if not self.config.enable_browser_control:
            return ActionType.NONE
        
        if self._is_mac:
            pyautogui.hotkey('command', '=')
        else:
            pyautogui.hotkey('ctrl', '=')
        
        logger.debug("🔍 Zoom in")
        return ActionType.ZOOM_IN
    
    def _handle_peace(self) -> ActionType:
        """Execute right-click at current position"""
        if not self.config.enable_desktop_control:
            return ActionType.NONE
        
        pyautogui.rightClick()
        logger.debug("🖱️ Right-click executed")
        return ActionType.RIGHT_CLICK
    
    def register_custom_action(self, action_type: ActionType, handler: Callable):
        """Register a custom handler for an action type"""
        self._custom_handlers[action_type] = handler
    
    def set_enabled(self, enabled: bool):
        """Enable or disable action execution"""
        self.is_enabled = enabled
        if not enabled and self.is_dragging:
            if pyautogui:
                pyautogui.mouseUp()
            self.is_dragging = False
        logger.info(f"Action executor {'enabled' if enabled else 'disabled'}")
    
    def get_status(self) -> Dict:
        """Get current executor status"""
        return {
            "is_enabled": self.is_enabled,
            "is_dragging": self.is_dragging,
            "last_action": self.last_action.value,
            "screen_size": {
                "width": self.config.screen_width,
                "height": self.config.screen_height
            }
        }


# =============================================================================
# Integration with GestureController
# =============================================================================

class GestureActionBridge:
    """
    Bridges GestureController with GestureActionExecutor.
    Handles the async event loop integration.
    """
    
    def __init__(self, controller, executor: GestureActionExecutor):
        self.controller = controller
        self.executor = executor
        self._action_cooldown = 0.2  # Seconds between repeated actions
        self._last_action_time = 0.0
    
    async def on_gesture_update(self, state):
        """Handle gesture updates from controller"""
        import time
        current_time = time.time()
        
        # Rate limit actions
        if current_time - self._last_action_time < self._action_cooldown:
            # Still allow cursor movement
            if state.gesture.value == "point":
                self.executor.execute_gesture(
                    state.gesture.value,
                    state.position,
                    state.velocity
                )
            return
        
        # Execute action
        action = self.executor.execute_gesture(
            state.gesture.value,
            state.position,
            state.velocity
        )
        
        if action != ActionType.NONE and action != ActionType.MOVE_CURSOR:
            self._last_action_time = current_time
    
    def start(self):
        """Start the bridge"""
        self.controller.on_hand_update(self.on_gesture_update)


# =============================================================================
# Factory Function
# =============================================================================

def create_action_executor(
    enable_desktop: bool = True,
    enable_browser: bool = True,
    cursor_speed: float = 1.5
) -> GestureActionExecutor:
    """Factory function to create an action executor"""
    config = ActionConfig(
        enable_desktop_control=enable_desktop,
        enable_browser_control=enable_browser,
        cursor_speed=cursor_speed
    )
    return GestureActionExecutor(config)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.DEBUG)
    executor = create_action_executor()
    
    print(f"Screen: {executor.config.screen_width}x{executor.config.screen_height}")
    print("Testing scroll...")
    executor.execute_gesture("swipe_down", (0.5, 0.5), (0, 0.5))
