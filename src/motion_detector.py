"""
Motion Detection Module for Diwali Projection System.
Detects movement in the camera frame using frame differencing technique.
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path


class MotionDetector:
    """Detects motion in video frames using frame differencing."""
    
    def __init__(self, config_path=None):
        """Initialize motion detector with configuration."""
        # Default config
        self.config = {
            "blur_size": 5,
            "threshold": 25,
            "min_area": 500,
            "history": 20
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "motion_detection" in all_config:
                    self.config.update(all_config["motion_detection"])
        
        # Motion detection variables
        self.motion_detected = False
        self.motion_contours = []
        self.motion_history = []
        self.largest_contour = None
        self.contour_center = None
        
    def detect(self, current_frame, prev_frame):
        """
        Detect motion between two consecutive frames.
        
        Args:
            current_frame: Current grayscale blurred frame
            prev_frame: Previous grayscale blurred frame
            
        Returns:
            motion_detected: Boolean indicating if motion was detected
            motion_contours: List of contours where motion was detected
            motion_mask: Binary mask showing motion areas
        """
        if current_frame is None or prev_frame is None:
            return False, [], None
            
        # Calculate absolute difference between current and previous frame
        frame_diff = cv2.absdiff(current_frame, prev_frame)
        
        # Apply threshold to difference image
        _, thresh = cv2.threshold(
            frame_diff, 
            self.config["threshold"], 
            255, 
            cv2.THRESH_BINARY
        )
        
        # Dilate the thresholded image to fill in holes
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Find contours in thresholded image
        contours, _ = cv2.findContours(
            dilated, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by minimum area
        significant_contours = [
            cnt for cnt in contours 
            if cv2.contourArea(cnt) > self.config["min_area"]
        ]
        
        # Track the largest contour if any found
        self.largest_contour = None
        self.contour_center = None
        
        if significant_contours:
            # Get the largest contour by area
            self.largest_contour = max(significant_contours, key=cv2.contourArea)
            
            # Calculate center of the largest contour
            M = cv2.moments(self.largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                self.contour_center = (cx, cy)
        
        # Update motion history
        self.motion_detected = len(significant_contours) > 0
        self.motion_contours = significant_contours
        
        # Keep track of motion history
        self.motion_history.append(1 if self.motion_detected else 0)
        if len(self.motion_history) > self.config["history"]:
            self.motion_history.pop(0)
        
        # Create a mask for visualization
        motion_mask = np.zeros_like(current_frame)
        cv2.drawContours(motion_mask, significant_contours, -1, 255, -1)
        
        return self.motion_detected, significant_contours, motion_mask
    
    def get_motion_intensity(self):
        """Calculate motion intensity based on recent history."""
        if not self.motion_history:
            return 0.0
            
        return sum(self.motion_history) / len(self.motion_history)
    
    def get_largest_contour(self):
        """Get the largest detected motion contour."""
        return self.largest_contour
    
    def get_contour_center(self):
        """Get center point of the largest contour."""
        return self.contour_center


# For testing
if __name__ == "__main__":
    from camera_input import CameraInput
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    camera = CameraInput(config_path)
    motion_detector = MotionDetector(config_path)
    
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
                
                # Create a copy for visualization
                display = frame.copy()
                
                # Draw contours on the display image
                cv2.drawContours(display, contours, -1, (0, 255, 0), 2)
                
                # Display motion intensity and status
                intensity = motion_detector.get_motion_intensity()
                cv2.putText(
                    display,
                    f"Motion: {'YES' if motion_detected else 'NO'}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 0, 255) if motion_detected else (0, 255, 0), 
                    2
                )
                
                cv2.putText(
                    display,
                    f"Intensity: {intensity:.2f}", 
                    (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 255, 255), 
                    2
                )
                
                # Draw center of the largest contour
                center = motion_detector.get_contour_center()
                if center:
                    cv2.circle(display, center, 10, (255, 0, 0), -1)
                
                # Show the original frame and motion mask
                cv2.imshow("Original", display)
                
                if motion_mask is not None:
                    cv2.imshow("Motion Mask", motion_mask)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            camera.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start camera")