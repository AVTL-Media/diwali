"""
Camera Input Module for Diwali Projection System.
Handles webcam input and preprocessing for detection algorithms.
"""

import cv2
import numpy as np
import json
import os
import time
from pathlib import Path

class CameraInput:
    """Camera input handler with preprocessing capabilities."""
    
    def __init__(self, config_path=None):
        """Initialize camera input with configuration."""
        # Default config
        self.config = {
            "device_id": 0,
            "width": 640,
            "height": 480,
            "fps": 30
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "camera" in all_config:
                    self.config.update(all_config["camera"])
        
        # Camera setup
        self.cap = None
        self.frame = None
        self.prev_frame = None
        self.gray = None
        self.is_running = False
        self.fps_start_time = time.time()
        self.frame_count = 0
        self.fps = 0
    
    def start(self):
        """Start the camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.config["device_id"])
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["width"])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["height"])
            self.cap.set(cv2.CAP_PROP_FPS, self.config["fps"])
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
                
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop(self):
        """Stop and release camera resources."""
        if self.cap:
            self.cap.release()
        self.is_running = False
    
    def read(self):
        """Read a frame from the camera with preprocessing."""
        if not self.is_running or not self.cap:
            return None
        
        # Store previous frame for motion detection
        self.prev_frame = self.gray.copy() if self.gray is not None else None
        
        # Read current frame
        ret, self.frame = self.cap.read()
        
        # Calculate FPS
        self.frame_count += 1
        if (time.time() - self.fps_start_time) > 1:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_start_time = time.time()
        
        if not ret:
            print("Failed to grab frame")
            return None
        
        # Flip frame horizontally for more intuitive interaction
        self.frame = cv2.flip(self.frame, 1)
        
        # Convert to grayscale for processing
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        
        return self.frame
    
    def get_frame(self):
        """Get the current frame."""
        return self.frame
    
    def get_gray(self):
        """Get grayscale version of current frame."""
        return self.gray
    
    def get_blurred(self):
        """Get blurred grayscale version of current frame."""
        return self.blurred
    
    def get_prev_frame(self):
        """Get the previous frame for motion detection."""
        return self.prev_frame
    
    def get_fps(self):
        """Get current frames per second."""
        return self.fps
    
    def get_resolution(self):
        """Get current camera resolution."""
        if self.frame is not None:
            h, w = self.frame.shape[:2]
            return (w, h)
        return (self.config["width"], self.config["height"])


# For testing
if __name__ == "__main__":
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    camera = CameraInput(config_path)
    if camera.start():
        try:
            while True:
                frame = camera.read()
                if frame is not None:
                    # Display FPS
                    cv2.putText(
                        frame, 
                        f"FPS: {camera.get_fps()}", 
                        (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, 
                        (0, 255, 0), 
                        2
                    )
                    cv2.imshow("Camera Test", frame)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            camera.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start camera")