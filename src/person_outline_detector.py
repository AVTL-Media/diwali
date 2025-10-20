"""
Person Outline Detector for Diwali Projection System.
Extracts ethereal outlines of people from camera input.
"""

import cv2
import numpy as np
import json
import os
import time
import mediapipe as mp
from pathlib import Path


class PersonOutlineDetector:
    """Detects and extracts ethereal outlines of people from camera feed."""
    
    def __init__(self, config_path=None):
        """Initialize person outline detector with configuration."""
        # Default config
        self.config = {
            "enabled": True,
            "detection_confidence": 0.7,
            "outline_thickness": 5,
            "background_subtractor": "MOG2",  # Options: "MOG2", "KNN", "EDGE"
            "blur_strength": 15,
            "outline_color": [140, 220, 255],  # Light blue
            "min_contour_area": 1000,
            "max_outline_age": 1.0,  # seconds
            "particle_count": 100,
            "particle_lifetime": 2.0,
            "use_mediapipe": True,  # Whether to use mediapipe for better person detection
            "history_frames": 10
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "ethereal_outlines" in all_config:
                    self.config.update(all_config["ethereal_outlines"])
        
        # Initialize background subtractor based on config
        self.setup_background_subtractor()
        
        # Initialize MediaPipe pose detector if enabled
        self.mp_pose = None
        self.pose = None
        if self.config["use_mediapipe"]:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=self.config["detection_confidence"],
                min_tracking_confidence=0.5,
                model_complexity=1  # 0, 1 or 2, higher is more accurate but slower
            )
            
        # Outline tracking variables
        self.outlines = []  # List of detected outline contours
        self.outline_timestamps = []  # Creation times for each outline
        self.outline_history = []  # Historical frames of outlines for smooth transitions
        self.frame_count = 0
    
    def setup_background_subtractor(self):
        """Setup the background subtractor based on configuration."""
        if self.config["background_subtractor"] == "MOG2":
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=500, 
                varThreshold=16, 
                detectShadows=False
            )
        elif self.config["background_subtractor"] == "KNN":
            self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
                history=500,
                dist2Threshold=400.0,
                detectShadows=False
            )
        else:
            self.bg_subtractor = None  # Will use edge detection instead
    
    def detect(self, frame):
        """
        Detect and extract ethereal outlines of people from the frame.
        
        Args:
            frame: Current BGR frame from the camera
            
        Returns:
            ethereal_mask: Mask with the ethereal outlines
            has_person: Boolean indicating if a person was detected
        """
        if not self.config["enabled"] or frame is None:
            return np.zeros_like(frame), False
            
        # Increment frame counter
        self.frame_count += 1
        current_time = time.time()
        
        # Create a mask for the ethereal effect
        ethereal_mask = np.zeros_like(frame)
        
        # Use MediaPipe for pose detection if enabled
        person_detected = False
        if self.config["use_mediapipe"] and self.pose:
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                person_detected = True
                # Create a blank mask for the person
                h, w = frame.shape[:2]
                mask = np.zeros((h, w), dtype=np.uint8)
                
                # Draw the pose landmarks on the mask
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing_styles = mp.solutions.drawing_styles
                
                # Create a temporary image to draw landmarks
                temp_img = np.zeros((h, w, 3), dtype=np.uint8)
                mp_drawing.draw_landmarks(
                    temp_img,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                # Convert to grayscale and threshold
                temp_gray = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(temp_gray, 1, 255, cv2.THRESH_BINARY)
                
                # Dilate to create a fuller silhouette
                kernel = np.ones((15, 15), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=2)
                
                # Find contours in the mask
                contours, _ = cv2.findContours(
                    mask, 
                    cv2.RETR_EXTERNAL, 
                    cv2.CHAIN_APPROX_SIMPLE
                )
                
                # Filter contours by minimum area
                person_contours = [
                    cnt for cnt in contours 
                    if cv2.contourArea(cnt) > self.config["min_contour_area"]
                ]
                
                if person_contours:
                    # Add to outlines with timestamp
                    for contour in person_contours:
                        self.outlines.append(contour)
                        self.outline_timestamps.append(current_time)
        
        # If MediaPipe didn't detect a person or is disabled, try background subtraction
        if not person_detected or not self.config["use_mediapipe"]:
            # Apply background subtraction
            if self.bg_subtractor:
                # Apply background subtraction
                fg_mask = self.bg_subtractor.apply(frame)
                
                # Apply morphological operations to clean up the mask
                kernel = np.ones((5, 5), np.uint8)
                fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
                fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
                
                # Find contours in the mask
                contours, _ = cv2.findContours(
                    fg_mask, 
                    cv2.RETR_EXTERNAL, 
                    cv2.CHAIN_APPROX_SIMPLE
                )
                
                # Filter contours by minimum area
                person_contours = [
                    cnt for cnt in contours 
                    if cv2.contourArea(cnt) > self.config["min_contour_area"]
                ]
                
                if person_contours:
                    person_detected = True
                    # Add to outlines with timestamp
                    for contour in person_contours:
                        self.outlines.append(contour)
                        self.outline_timestamps.append(current_time)
            
            # Alternative: Use edge detection
            else:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply Gaussian blur
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Apply Canny edge detection
                edges = cv2.Canny(blurred, 50, 150)
                
                # Dilate edges to connect them
                kernel = np.ones((3, 3), np.uint8)
                dilated_edges = cv2.dilate(edges, kernel, iterations=2)
                
                # Find contours in the edges
                contours, _ = cv2.findContours(
                    dilated_edges, 
                    cv2.RETR_EXTERNAL, 
                    cv2.CHAIN_APPROX_SIMPLE
                )
                
                # Filter contours by minimum area
                person_contours = [
                    cnt for cnt in contours 
                    if cv2.contourArea(cnt) > self.config["min_contour_area"]
                ]
                
                if person_contours:
                    person_detected = True
                    # Add to outlines with timestamp
                    for contour in person_contours:
                        self.outlines.append(contour)
                        self.outline_timestamps.append(current_time)
        
        # Remove old outlines
        current_outlines = []
        current_timestamps = []
        
        for i, timestamp in enumerate(self.outline_timestamps):
            if i < len(self.outlines) and current_time - timestamp < self.config["max_outline_age"]:
                current_outlines.append(self.outlines[i])
                current_timestamps.append(timestamp)
        
        self.outlines = current_outlines
        self.outline_timestamps = current_timestamps
        
        # Store in history for smoother transitions
        if self.outlines:
            outline_frame = np.zeros_like(frame)
            for idx, contour in enumerate(self.outlines):
                # Calculate alpha based on age (newer contours are more opaque)
                age = current_time - self.outline_timestamps[idx]
                alpha = 1.0 - (age / self.config["max_outline_age"])
                thickness = int(self.config["outline_thickness"] * alpha)
                
                # Draw the contour on the mask
                color = [int(c * alpha) for c in self.config["outline_color"]]
                cv2.drawContours(outline_frame, [contour], -1, color, thickness)
            
            self.outline_history.append(outline_frame)
        else:
            self.outline_history.append(np.zeros_like(frame))
        
        # Keep only recent history
        if len(self.outline_history) > self.config["history_frames"]:
            self.outline_history.pop(0)
        
        # Blend historical frames for smoother effect
        for i, hist_frame in enumerate(self.outline_history):
            weight = (i + 1) / len(self.outline_history)
            ethereal_mask = cv2.addWeighted(ethereal_mask, 1.0, hist_frame, weight, 0)
        
        # Apply blur for ethereal glow effect
        if np.any(ethereal_mask):
            blur_size = self.config["blur_strength"]
            if blur_size % 2 == 0:  # Must be odd for Gaussian blur
                blur_size += 1
            ethereal_mask = cv2.GaussianBlur(ethereal_mask, (blur_size, blur_size), 0)
        
        return ethereal_mask, person_detected
    
    def add_particle_effects(self, ethereal_mask):
        """
        Add particle effects around the ethereal outlines.
        
        Args:
            ethereal_mask: The mask with ethereal outlines
            
        Returns:
            mask_with_particles: Updated mask with particle effects
        """
        # Skip if no outline is present
        if not np.any(ethereal_mask):
            return ethereal_mask
        
        # Convert to grayscale if needed for finding non-zero pixels
        if ethereal_mask.ndim > 2:
            gray_mask = cv2.cvtColor(ethereal_mask, cv2.COLOR_BGR2GRAY)
        else:
            gray_mask = ethereal_mask.copy()
        
        # Find non-zero pixels (outline pixels)
        non_zero = cv2.findNonZero(gray_mask)
        
        # Skip if no outline pixels found
        if non_zero is None or len(non_zero) == 0:
            return ethereal_mask
            
        # Create particle effects
        particles_mask = np.zeros_like(ethereal_mask)
        
        # Select random points from the outline for particles
        num_particles = min(self.config["particle_count"], len(non_zero))
        random_indices = np.random.choice(len(non_zero), num_particles, replace=False)
        
        for idx in random_indices:
            # Get point from outline
            point = non_zero[idx][0]
            x, y = point
            
            # Add randomness to position
            x += np.random.randint(-10, 11)
            y += np.random.randint(-10, 11)
            
            # Random particle size
            size = np.random.randint(1, 5)
            
            # Random color based on outline color with varying brightness
            color = self.config["outline_color"].copy()
            brightness = np.random.uniform(0.6, 1.4)
            color = [min(255, int(c * brightness)) for c in color]
            
            # Draw the particle
            cv2.circle(particles_mask, (x, y), size, color, -1)
        
        # Combine with the original mask
        result = cv2.addWeighted(ethereal_mask, 1.0, particles_mask, 0.7, 0)
        
        return result
    
    def visualize(self, frame, ethereal_mask):
        """
        Create a visualization of the frame with ethereal outlines.
        
        Args:
            frame: Original BGR frame
            ethereal_mask: Mask with ethereal outlines
            
        Returns:
            visualization: Frame with visualized ethereal outlines
        """
        # Create a copy of the frame
        result = frame.copy()
        
        # Apply the ethereal mask with additive blending
        cv2.add(result, ethereal_mask, result)
        
        return result
    
    def cleanup(self):
        """Clean up resources."""
        if self.pose:
            self.pose.close()


# For testing
if __name__ == "__main__":
    from camera_input import CameraInput
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    camera = CameraInput(config_path)
    detector = PersonOutlineDetector(config_path)
    
    if camera.start():
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    break
                
                # Detect ethereal outlines
                ethereal_mask, has_person = detector.detect(frame)
                
                # Add particle effects to the outlines
                ethereal_mask = detector.add_particle_effects(ethereal_mask)
                
                # Visualize the result
                visualization = detector.visualize(frame, ethereal_mask)
                
                # Display info
                cv2.putText(
                    visualization, 
                    f"Person Detected: {'YES' if has_person else 'NO'}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 255, 0) if has_person else (0, 0, 255), 
                    2
                )
                
                # Display FPS
                cv2.putText(
                    visualization, 
                    f"FPS: {camera.get_fps()}", 
                    (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 255, 255), 
                    2
                )
                
                # Show the visualization
                cv2.imshow("Ethereal Outlines", visualization)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            camera.stop()
            detector.cleanup()
            cv2.destroyAllWindows()
    else:
        print("Failed to start camera")