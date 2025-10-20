"""
Gesture Tracking Module for Diwali Projection System.
Uses MediaPipe to track hand gestures for interactive effects.
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
import math
from enum import Enum
from pathlib import Path


class GestureType(Enum):
    """Enumeration of recognized gesture types."""
    UNKNOWN = 0
    OPEN_PALM = 1
    CLOSED_FIST = 2
    POINTING = 3
    PINCH = 4
    WAVE = 5


class GestureTracker:
    """Track and recognize hand gestures using MediaPipe Hands."""
    
    def __init__(self, config_path=None):
        """Initialize the gesture tracker with configuration."""
        # Default config
        self.config = {
            "min_detection_confidence": 0.7,
            "min_tracking_confidence": 0.5,
            "max_num_hands": 2
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "gesture_tracking" in all_config:
                    self.config.update(all_config["gesture_tracking"])
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config["max_num_hands"],
            min_detection_confidence=self.config["min_detection_confidence"],
            min_tracking_confidence=self.config["min_tracking_confidence"]
        )
        
        # Gesture tracking state
        self.hand_landmarks = []
        self.hand_positions = []  # [(x, y) center positions]
        self.gestures = []        # [GestureType]
        self.hands_present = False
        
    def process_frame(self, frame):
        """
        Process a frame to detect and track hands.
        
        Args:
            frame: RGB image frame from camera
            
        Returns:
            hands_present: Boolean indicating if hands are detected
            hand_positions: List of (x, y) coordinates of hand centers
            gestures: List of detected gesture types
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Hands
        results = self.hands.process(rgb_frame)
        
        # Reset tracking data
        self.hand_landmarks = []
        self.hand_positions = []
        self.gestures = []
        self.hands_present = False
        
        # Check if hands were detected
        if results.multi_hand_landmarks:
            self.hands_present = True
            height, width, _ = frame.shape
            
            # Process each detected hand
            for hand_landmarks in results.multi_hand_landmarks:
                self.hand_landmarks.append(hand_landmarks)
                
                # Calculate hand center position
                cx = int(sum(lm.x for lm in hand_landmarks.landmark) / len(hand_landmarks.landmark) * width)
                cy = int(sum(lm.y for lm in hand_landmarks.landmark) / len(hand_landmarks.landmark) * height)
                self.hand_positions.append((cx, cy))
                
                # Recognize gesture
                gesture = self._recognize_gesture(hand_landmarks, width, height)
                self.gestures.append(gesture)
        
        return self.hands_present, self.hand_positions, self.gestures
    
    def _recognize_gesture(self, landmarks, width, height):
        """
        Recognize the gesture type based on hand landmark positions.
        
        Args:
            landmarks: MediaPipe hand landmarks
            width: Frame width
            height: Frame height
            
        Returns:
            GestureType: The recognized gesture
        """
        # Extract normalized landmark positions
        points = []
        for lm in landmarks.landmark:
            points.append((int(lm.x * width), int(lm.y * height)))
        
        # Calculate finger states (extended or not)
        thumb_tip = points[4]
        index_tip = points[8]
        middle_tip = points[12]
        ring_tip = points[16]
        pinky_tip = points[20]
        
        wrist = points[0]
        thumb_base = points[2]
        index_base = points[5]
        middle_base = points[9]
        ring_base = points[13]
        pinky_base = points[17]
        
        # Check if fingers are extended by comparing with palm
        fingers_extended = [
            self._is_finger_extended(thumb_tip, thumb_base, wrist),
            self._is_finger_extended(index_tip, index_base, wrist),
            self._is_finger_extended(middle_tip, middle_base, wrist),
            self._is_finger_extended(ring_tip, ring_base, wrist),
            self._is_finger_extended(pinky_tip, pinky_base, wrist)
        ]
        
        # Distance between thumb and index fingertips
        pinch_distance = self._distance_between(thumb_tip, index_tip)
        pinch_threshold = 0.05 * max(width, height)  # 5% of frame dimension
        
        # Recognize gestures
        if sum(fingers_extended[1:]) >= 4:  # At least 4 fingers extended
            return GestureType.OPEN_PALM
        elif sum(fingers_extended) <= 1:  # No fingers extended
            return GestureType.CLOSED_FIST
        elif fingers_extended[1] and not any(fingers_extended[2:]):  # Only index finger extended
            return GestureType.POINTING
        elif pinch_distance < pinch_threshold:  # Thumb and index close together
            return GestureType.PINCH
        else:
            return GestureType.UNKNOWN
    
    def _is_finger_extended(self, tip, base, wrist):
        """Check if a finger is extended by comparing distances."""
        tip_to_wrist = self._distance_between(tip, wrist)
        base_to_wrist = self._distance_between(base, wrist)
        return tip_to_wrist > base_to_wrist * 1.2  # 20% longer than base
    
    def _distance_between(self, p1, p2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def draw_landmarks(self, frame):
        """
        Draw hand landmarks and labels on the frame.
        
        Args:
            frame: BGR image frame to draw on
            
        Returns:
            frame: Modified frame with landmarks and labels
        """
        if not self.hands_present:
            return frame
            
        # Draw landmarks on each detected hand
        for i, (landmarks, position, gesture) in enumerate(zip(self.hand_landmarks, self.hand_positions, self.gestures)):
            # Draw hand landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # Draw center point
            cv2.circle(frame, position, 10, (255, 0, 255), -1)
            
            # Draw gesture label
            label = gesture.name
            cv2.putText(
                frame, 
                label, 
                (position[0] - 20, position[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 255),
                2
            )
        
        return frame
    
    def get_hands_present(self):
        """Check if any hands are present in the frame."""
        return self.hands_present
    
    def get_hand_positions(self):
        """Get the center positions of detected hands."""
        return self.hand_positions
    
    def get_gestures(self):
        """Get the recognized gestures for detected hands."""
        return self.gestures


# For testing
if __name__ == "__main__":
    from camera_input import CameraInput
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    camera = CameraInput(config_path)
    gesture_tracker = GestureTracker(config_path)
    
    if camera.start():
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    break
                
                # Process frame for hand detection
                hands_present, hand_positions, gestures = gesture_tracker.process_frame(frame)
                
                # Draw hand landmarks and information
                display = gesture_tracker.draw_landmarks(frame.copy())
                
                # Show status
                cv2.putText(
                    display,
                    f"Hands: {'Detected' if hands_present else 'None'}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 255, 0) if hands_present else (0, 0, 255), 
                    2
                )
                
                # Display gesture information
                if hands_present:
                    for i, (pos, gesture) in enumerate(zip(hand_positions, gestures)):
                        info = f"Hand {i+1}: {gesture.name}"
                        cv2.putText(
                            display,
                            info, 
                            (10, 70 + i*40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1, 
                            (255, 255, 0), 
                            2
                        )
                
                cv2.imshow("Gesture Tracking", display)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            camera.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start camera")