"""
aSiReM Gesture Controller - Minority Report Style Hand Control
Real-time hand gesture detection using MediaPipe for browser/desktop control.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
# import numpy as np  # LAZY: Moved to function level to prevent startup hang

try:
    import cv2
    import mediapipe as mp
except ImportError:
    cv2 = None
    mp = None

logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Core gesture types for system control"""
    NONE = "none"
    POINT = "point"           # Index finger extended → cursor control
    PINCH = "pinch"           # Thumb + index touch → click
    GRAB = "grab"             # Fist closed → drag
    OPEN_PALM = "open_palm"   # All fingers spread → stop
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SPREAD = "spread"         # Fingers spreading apart → zoom in
    PEACE = "peace"           # Peace sign → right-click


@dataclass
class HandState:
    """Current state of detected hand"""
    landmarks: List[Tuple[float, float, float]] = field(default_factory=list)
    gesture: GestureType = GestureType.NONE
    confidence: float = 0.0
    position: Tuple[float, float] = (0.5, 0.5)  # Normalized 0-1
    velocity: Tuple[float, float] = (0.0, 0.0)
    is_right_hand: bool = True
    timestamp: float = 0.0


@dataclass 
class GestureConfig:
    """Configuration for gesture detection"""
    target_fps: int = 30
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    gesture_hold_time_ms: int = 150  # Time to hold gesture before action
    swipe_threshold: float = 0.15   # Min movement for swipe detection
    pinch_threshold: float = 0.05   # Max distance for pinch detection
    smoothing_factor: float = 0.3   # Kalman-like smoothing (0-1)
    performance_mode: bool = False  # True = 15fps, False = 30fps


class GestureController:
    """
    Real-time hand gesture detection and classification.
    Uses MediaPipe Hands for landmark detection.
    """
    
    def __init__(self, config: Optional[GestureConfig] = None):
        self.config = config or GestureConfig()
        self.is_running = False
        self.cap = None
        self.hands = None
        
        # Hand state tracking
        self.current_state = HandState()
        self.prev_state = HandState()
        self.gesture_start_time = 0.0
        self.confirmed_gesture = GestureType.NONE
        
        # Position smoothing
        self._smooth_pos = (0.5, 0.5)
        
        # Callbacks
        self._on_gesture: Optional[Callable] = None
        self._on_hand_update: Optional[Callable] = None
        
        # MediaPipe setup
        if mp:
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
        
        logger.info("🖐️ GestureController initialized")
    
    def initialize(self) -> bool:
        """Initialize MediaPipe and camera"""
        if not mp or not cv2:
            logger.error("MediaPipe or OpenCV not installed!")
            return False
        
        try:
            # Initialize MediaPipe Hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=self.config.min_detection_confidence,
                min_tracking_confidence=self.config.min_tracking_confidence
            )
            
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Cannot open camera!")
                return False
            
            # Set camera properties
            fps = 15 if self.config.performance_mode else self.config.target_fps
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            logger.info(f"✅ Camera initialized at {fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> Optional[HandState]:
        """Process a single frame and return hand state"""
        if self.hands is None:
            return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return HandState(gesture=GestureType.NONE)
        
        # Get first detected hand
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0] if results.multi_handedness else None
        
        # Extract landmarks as list of tuples
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append((lm.x, lm.y, lm.z))
        
        # Calculate hand center position (wrist)
        wrist = landmarks[0]
        raw_pos = (wrist[0], wrist[1])
        
        # Apply smoothing
        self._smooth_pos = (
            self._smooth_pos[0] * (1 - self.config.smoothing_factor) + raw_pos[0] * self.config.smoothing_factor,
            self._smooth_pos[1] * (1 - self.config.smoothing_factor) + raw_pos[1] * self.config.smoothing_factor
        )
        
        # Calculate velocity from previous frame
        velocity = (0.0, 0.0)
        if self.prev_state.timestamp > 0:
            dt = time.time() - self.prev_state.timestamp
            if dt > 0:
                velocity = (
                    (raw_pos[0] - self.prev_state.position[0]) / dt,
                    (raw_pos[1] - self.prev_state.position[1]) / dt
                )
        
        # Classify gesture
        gesture = self._classify_gesture(landmarks, velocity)
        
        # Create hand state
        state = HandState(
            landmarks=landmarks,
            gesture=gesture,
            confidence=results.multi_handedness[0].classification[0].score if handedness else 0.8,
            position=self._smooth_pos,
            velocity=velocity,
            is_right_hand=handedness.classification[0].label == "Right" if handedness else True,
            timestamp=time.time()
        )
        
        # Update confirmed gesture with hold time
        self._update_confirmed_gesture(state)
        
        # Store previous state
        self.prev_state = self.current_state
        self.current_state = state
        
        return state
    
    def _classify_gesture(self, landmarks: List[Tuple[float, float, float]], velocity: Tuple[float, float]) -> GestureType:
        """Classify hand gesture from landmarks"""
        if len(landmarks) < 21:
            return GestureType.NONE
        
        # Key landmark indices (MediaPipe hand model)
        WRIST = 0
        THUMB_TIP = 4
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        RING_TIP = 16
        PINKY_TIP = 20
        INDEX_MCP = 5
        MIDDLE_MCP = 9
        
        # Calculate finger states (extended or not)
        fingers_extended = self._get_fingers_extended(landmarks)
        
        # Check for swipe gestures first (based on velocity)
        speed = (velocity[0]**2 + velocity[1]**2)**0.5
        if speed > self.config.swipe_threshold:
            if abs(velocity[0]) > abs(velocity[1]):
                return GestureType.SWIPE_LEFT if velocity[0] < 0 else GestureType.SWIPE_RIGHT
            else:
                return GestureType.SWIPE_UP if velocity[1] < 0 else GestureType.SWIPE_DOWN
        
        # Check pinch (thumb and index close together)
        import numpy as np  # lazy import
        thumb_tip = np.array(landmarks[THUMB_TIP][:2])
        index_tip = np.array(landmarks[INDEX_TIP][:2])
        pinch_distance = np.linalg.norm(thumb_tip - index_tip)
        if pinch_distance < self.config.pinch_threshold:
            return GestureType.PINCH
        
        # Check peace sign (index + middle extended, others closed)
        if fingers_extended == [False, True, True, False, False]:
            return GestureType.PEACE
        
        # Check point (only index extended)
        if fingers_extended == [False, True, False, False, False]:
            return GestureType.POINT
        
        # Check open palm (all fingers extended)
        if all(fingers_extended):
            return GestureType.OPEN_PALM
        
        # Check grab/fist (all fingers closed)
        if not any(fingers_extended):
            return GestureType.GRAB
        
        # Check spread (all fingers extended and spread apart)
        if all(fingers_extended):
            # Check if fingers are spread
            index_middle_dist = np.linalg.norm(np.array(landmarks[INDEX_TIP][:2]) - np.array(landmarks[MIDDLE_TIP][:2]))
            if index_middle_dist > 0.1:
                return GestureType.SPREAD
        
        return GestureType.NONE
    
    def _get_fingers_extended(self, landmarks: List[Tuple[float, float, float]]) -> List[bool]:
        """Check which fingers are extended [thumb, index, middle, ring, pinky]"""
        # Finger tip and pip (proximal interphalangeal) indices
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        
        extended = []
        for i, (tip_idx, pip_idx) in enumerate(zip(tips, pips)):
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            
            if i == 0:  # Thumb (compare x for left/right)
                wrist = landmarks[0]
                extended.append(abs(tip[0] - wrist[0]) > abs(pip[0] - wrist[0]))
            else:  # Other fingers (compare y - lower y means extended)
                extended.append(tip[1] < pip[1])
        
        return extended
    
    def _update_confirmed_gesture(self, state: HandState):
        """Update confirmed gesture with hold time requirement"""
        current_time = time.time() * 1000  # milliseconds
        
        if state.gesture == self.current_state.gesture:
            # Same gesture, check if held long enough
            if current_time - self.gesture_start_time >= self.config.gesture_hold_time_ms:
                if self.confirmed_gesture != state.gesture:
                    self.confirmed_gesture = state.gesture
                    if self._on_gesture:
                        self._on_gesture(state)
        else:
            # New gesture, reset timer
            self.gesture_start_time = current_time
    
    async def start_detection(self):
        """Start async gesture detection loop"""
        if not self.initialize():
            return
        
        self.is_running = True
        fps_delay = 1 / (15 if self.config.performance_mode else self.config.target_fps)
        
        logger.info("▶️ Starting gesture detection...")
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue
            
            # Mirror the frame for intuitive control
            frame = cv2.flip(frame, 1)
            
            # Process frame
            state = self.process_frame(frame)
            
            # Notify listeners
            if state and self._on_hand_update:
                await self._on_hand_update(state)
            
            await asyncio.sleep(fps_delay)
        
        self.cleanup()
    
    def stop_detection(self):
        """Stop gesture detection"""
        self.is_running = False
        logger.info("⏹️ Gesture detection stopped")
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        logger.info("🧹 GestureController cleaned up")
    
    def on_gesture(self, callback: Callable):
        """Register callback for confirmed gestures"""
        self._on_gesture = callback
    
    def on_hand_update(self, callback: Callable):
        """Register callback for every hand update"""
        self._on_hand_update = callback
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary for WebSocket"""
        return {
            "gesture": self.confirmed_gesture.value,
            "raw_gesture": self.current_state.gesture.value,
            "position": {
                "x": self.current_state.position[0],
                "y": self.current_state.position[1]
            },
            "velocity": {
                "x": self.current_state.velocity[0],
                "y": self.current_state.velocity[1]
            },
            "confidence": self.current_state.confidence,
            "is_right_hand": self.current_state.is_right_hand,
            "landmarks": [{"x": l[0], "y": l[1], "z": l[2]} for l in self.current_state.landmarks],
            "timestamp": self.current_state.timestamp
        }


# =============================================================================
# WebSocket Handler for Real-Time Streaming
# =============================================================================

class GestureWebSocketHandler:
    """Handles WebSocket connections for gesture streaming"""
    
    def __init__(self, controller: GestureController):
        self.controller = controller
        self.clients: List[Any] = []
    
    async def register(self, websocket):
        """Register a new WebSocket client"""
        self.clients.append(websocket)
        logger.info(f"👋 Gesture client connected ({len(self.clients)} total)")
    
    async def unregister(self, websocket):
        """Unregister a WebSocket client"""
        if websocket in self.clients:
            self.clients.remove(websocket)
        logger.info(f"👋 Gesture client disconnected ({len(self.clients)} total)")
    
    async def broadcast(self, state: HandState):
        """Broadcast hand state to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps(self.controller.get_state_dict())
        
        # Send to all clients
        for client in self.clients[:]:  # Copy list to allow removal
            try:
                await client.send(message)
            except Exception:
                await self.unregister(client)


# =============================================================================
# Factory Function
# =============================================================================

def create_gesture_controller(
    fps: int = 30,
    performance_mode: bool = False,
    **kwargs
) -> GestureController:
    """Factory function to create a gesture controller"""
    config = GestureConfig(
        target_fps=fps,
        performance_mode=performance_mode,
        **kwargs
    )
    return GestureController(config)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    controller = create_gesture_controller()
    
    def on_gesture(state):
        print(f"🎯 Gesture: {state.gesture.value} at {state.position}")
    
    controller.on_gesture(on_gesture)
    asyncio.run(controller.start_detection())
