"""
Scene State Manager for Diwali Projection System.
Coordinates inputs from various detectors and manages visual state transitions.
"""

import json
import os
import time
from pathlib import Path
from enum import Enum


class VisualState(Enum):
    """Enumeration of visual scene states."""
    IDLE = 0
    DIYA = 1
    FIREWORKS = 2
    RANGOLI = 3
    AURA = 4


class SceneStateManager:
    """Manages the state of the scene based on various inputs."""
    
    def __init__(self, config_path=None):
        """Initialize the scene state manager with configuration."""
        # Default config
        self.config = {
            "idle_timeout": 5.0,  # seconds without interaction to return to idle
            "gesture_persistence": 1.0,  # seconds to maintain gesture-triggered state
            "diya_duration": 3.0,  # seconds to show diya after trigger
            "firework_duration": 2.0,  # seconds to show firework animation
            "aura_fade_duration": 0.5,  # seconds to fade aura in/out
            "rangoli_rotation_speed": 0.01  # degrees per frame for idle animation
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                # Extract relevant config from different sections
                if "visual_effects" in all_config:
                    effects_config = all_config["visual_effects"]
                    if "diya" in effects_config:
                        self.config["diya_duration"] = effects_config["diya"].get("fade_duration", 3.0)
                    if "fireworks" in effects_config:
                        self.config["firework_duration"] = effects_config["fireworks"].get("lifetime", 2.0)
                    if "aura" in effects_config:
                        self.config["aura_fade_duration"] = 0.5
                    if "rangoli" in effects_config:
                        self.config["rangoli_rotation_speed"] = effects_config["rangoli"].get("rotation_speed", 0.01)
        
        # Initialize state variables
        self.current_state = VisualState.IDLE
        self.previous_state = VisualState.IDLE
        self.last_interaction_time = time.time()
        self.state_change_time = time.time()
        
        # State data for visual effects
        self.state_data = {
            "diya_positions": [],     # [(x, y)] positions for diya placement
            "firework_origins": [],   # [(x, y)] positions for firework origins
            "rangoli_center": None,   # (x, y) for rangoli center
            "aura_position": None,    # (x, y) for aura center
            "aura_radius": 0.0,       # Radius of the aura effect
            "motion_intensity": 0.0,  # Current motion intensity (0.0-1.0)
            "audio_level": 0.0,       # Current audio level (0.0-1.0)
            "gesture_positions": [],  # [(x, y)] positions from gesture tracking
            "gesture_types": []       # List of current gesture types
        }
    
    def update(self, motion_detected=False, motion_intensity=0.0, motion_center=None, 
              audio_spike=False, audio_level=0.0, 
              hands_present=False, hand_positions=None, gestures=None):
        """
        Update scene state based on sensor inputs.
        
        Args:
            motion_detected: Boolean indicating if motion is detected
            motion_intensity: Float (0.0-1.0) indicating motion intensity
            motion_center: (x, y) center of the most significant motion
            audio_spike: Boolean indicating if an audio spike was detected
            audio_level: Float (0.0-1.0) indicating current audio volume level
            hands_present: Boolean indicating if hands are detected
            hand_positions: List of (x, y) hand center positions
            gestures: List of gesture types corresponding to hand_positions
            
        Returns:
            current_state: Current VisualState
            state_changed: Boolean indicating if state just changed
            state_data: Dictionary of state-related data for rendering
        """
        # Update state data
        self.state_data["motion_intensity"] = motion_intensity
        self.state_data["audio_level"] = audio_level
        
        if hand_positions:
            self.state_data["gesture_positions"] = hand_positions
        if gestures:
            self.state_data["gesture_types"] = gestures
        
        # Track if motion center changed
        if motion_center:
            self.state_data["motion_center"] = motion_center
            
        # Flag to indicate whether a state change occurred during this update
        state_changed = False
        now = time.time()
        
        # Update the last interaction time whenever there's user activity
        if motion_detected or audio_spike or hands_present:
            self.last_interaction_time = now
        
        # Store previous state for state change detection
        prev_state = self.current_state
        
        # State transition logic based on inputs
        if audio_spike:
            # Audio spike (like clap) triggers fireworks
            self.current_state = VisualState.FIREWORKS
            self.state_data["firework_origins"] = [motion_center] if motion_center else []
            self.state_change_time = now
            
        elif hands_present and gestures:
            from gesture_tracker import GestureType
            
            # Use hand gestures to determine visual state
            for i, gesture in enumerate(gestures):
                if i < len(hand_positions):
                    position = hand_positions[i]
                    
                    if gesture == GestureType.OPEN_PALM:
                        # Open palm shows aura around hand
                        self.current_state = VisualState.AURA
                        self.state_data["aura_position"] = position
                        self.state_data["aura_radius"] = 100  # Base radius
                        self.state_change_time = now
                        
                    elif gesture == GestureType.PINCH:
                        # Pinch gesture lights a diya at that position
                        self.current_state = VisualState.DIYA
                        if position not in self.state_data["diya_positions"]:
                            self.state_data["diya_positions"].append(position)
                        self.state_change_time = now
                        
        elif motion_detected and motion_intensity > 0.5:
            # Fast motion can trigger fireworks
            self.current_state = VisualState.FIREWORKS
            self.state_data["firework_origins"] = [motion_center] if motion_center else []
            self.state_change_time = now
            
        elif motion_detected:
            # Gentle motion shows rangoli patterns
            self.current_state = VisualState.RANGOLI
            if motion_center:
                self.state_data["rangoli_center"] = motion_center
            self.state_change_time = now
            
        else:
            # If no interaction for idle_timeout seconds, return to idle state
            idle_duration = now - self.last_interaction_time
            if idle_duration > self.config["idle_timeout"]:
                self.current_state = VisualState.IDLE
        
        # Handle timeout-based state transitions
        if self.current_state == VisualState.FIREWORKS:
            # Return to previous state after firework duration
            if now - self.state_change_time > self.config["firework_duration"]:
                self.current_state = VisualState.IDLE
                
        # Detect state changes
        if prev_state != self.current_state:
            state_changed = True
            self.previous_state = prev_state
            self.state_change_time = now
        
        # Return current state info
        return self.current_state, state_changed, self.state_data
    
    def get_current_state(self):
        """Get the current visual state."""
        return self.current_state
    
    def get_state_duration(self):
        """Get seconds elapsed in current state."""
        return time.time() - self.state_change_time
    
    def get_state_data(self):
        """Get the current state data dictionary."""
        return self.state_data


# For testing
if __name__ == "__main__":
    import cv2
    import numpy as np
    from camera_input import CameraInput
    from motion_detector import MotionDetector
    from gesture_tracker import GestureTracker, GestureType
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    # Create components
    camera = CameraInput(config_path)
    motion_detector = MotionDetector(config_path)
    gesture_tracker = GestureTracker(config_path)
    scene_manager = SceneStateManager(config_path)
    
    # Color mapping for visual states
    state_colors = {
        VisualState.IDLE: (50, 50, 50),      # Dark gray
        VisualState.DIYA: (0, 165, 255),     # Orange
        VisualState.FIREWORKS: (255, 0, 255),  # Magenta
        VisualState.RANGOLI: (0, 255, 255),    # Yellow
        VisualState.AURA: (255, 255, 0)        # Cyan
    }
    
    if camera.start():
        try:
            # First frame to initialize
            camera.read()
            
            while True:
                frame = camera.read()
                if frame is None:
                    break
                    
                # Skip if we don't have a previous frame yet
                prev_frame = camera.get_prev_frame()
                if prev_frame is None:
                    continue
                
                # Detect motion
                motion_detected, contours, motion_mask = motion_detector.detect(
                    camera.get_blurred(), 
                    prev_frame
                )
                
                # Get motion center and intensity
                motion_center = motion_detector.get_contour_center()
                motion_intensity = motion_detector.get_motion_intensity()
                
                # Process hand gestures
                hands_present, hand_positions, gestures = gesture_tracker.process_frame(frame)
                
                # Simulate audio spike with spacebar for testing
                key = cv2.waitKey(1) & 0xFF
                audio_spike = (key == ord(' '))
                audio_level = 1.0 if audio_spike else 0.0
                
                # Update scene state
                state, state_changed, state_data = scene_manager.update(
                    motion_detected=motion_detected,
                    motion_intensity=motion_intensity,
                    motion_center=motion_center,
                    audio_spike=audio_spike,
                    audio_level=audio_level,
                    hands_present=hands_present,
                    hand_positions=hand_positions,
                    gestures=gestures
                )
                
                # Create a visualization frame
                display = frame.copy()
                
                # Add color overlay based on state
                color = state_colors.get(state, (0, 0, 0))
                overlay = np.ones_like(frame) * color
                cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)
                
                # Draw hand landmarks
                display = gesture_tracker.draw_landmarks(display)
                
                # Draw motion contours
                cv2.drawContours(display, contours, -1, (0, 255, 0), 2)
                
                # Display state information
                cv2.putText(
                    display,
                    f"State: {state.name}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (255, 255, 255), 
                    2
                )
                
                cv2.putText(
                    display,
                    f"Motion: {motion_intensity:.2f}", 
                    (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (255, 255, 255), 
                    2
                )
                
                # Show diya positions if any
                for pos in state_data.get("diya_positions", []):
                    cv2.circle(display, pos, 20, (0, 165, 255), -1)
                    cv2.putText(
                        display,
                        "DIYA", 
                        (pos[0] - 20, pos[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )
                
                # Show the visualization
                cv2.imshow("Scene State Manager", display)
                
                # Press 'q' to exit
                if key == ord('q'):
                    break
                    
        finally:
            camera.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start camera")