"""
Main Application for Diwali Projection System.
Integrates all components for the interactive projection experience.
"""

import os
import sys
import time
import pygame
import cv2
import numpy as np
import json
import argparse
import threading
from pathlib import Path

# Add the current directory to the path for module imports
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(current_dir))

# Import custom modules
from camera_input import CameraInput
from motion_detector import MotionDetector
from gesture_tracker import GestureTracker
from audio_detector import AudioDetector
from scene_manager import SceneStateManager, VisualState
from visual_generator import VisualGenerator
from projection_calibrator import ProjectionCalibrator


class DiwaliProjectionApp:
    """Main application class for the Diwali Projection System."""
    
    def __init__(self, config_path=None):
        """Initialize the application with configuration."""
        # Default config
        self.config = {
            "title": "AI-Augmented Diwali Projection",
            "debug_mode": False,
            "show_fps": True,
            "exit_key": "q"
        }
        
        # Set config path
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = current_dir.parent / "config" / "settings.json"
        
        # Load config if available
        self._load_config()
        
        # Application state
        self.running = False
        self.calibration_mode = False
        self.debug_mode = self.config.get("debug_mode", False)
        
        # Initialize components
        self.init_components()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    all_config = json.load(f)
                    if "app" in all_config:
                        self.config.update(all_config["app"])
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def init_components(self):
        """Initialize all system components."""
        # Initialize camera input
        self.camera = CameraInput(self.config_path)
        
        # Initialize detectors
        self.motion_detector = MotionDetector(self.config_path)
        self.gesture_tracker = GestureTracker(self.config_path)
        self.audio_detector = AudioDetector(self.config_path)
        
        # Initialize scene manager
        self.scene_manager = SceneStateManager(self.config_path)
        
        # Initialize visual generator
        self.visual_generator = VisualGenerator(self.config_path)
        
        # Initialize projection calibrator
        self.calibrator = ProjectionCalibrator(self.config_path)
        self.calibrator.config_path = self.config_path
    
    def start(self, fullscreen=False):
        """
        Start the Diwali projection application.
        
        Args:
            fullscreen: Boolean indicating whether to run in fullscreen mode
        """
        print("Starting Diwali Projection System...")
        
        # Initialize pygame
        pygame.init()
        
        # Set up display
        flags = pygame.FULLSCREEN if fullscreen else 0
        info = pygame.display.Info()
        
        if fullscreen:
            width, height = info.current_w, info.current_h
        else:
            width, height = 1920, 1080
            
        print(f"Setting up display: {width}x{height}")
        
        # Create pygame screen
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(self.config.get("title", "Diwali Projection"))
        
        # Start camera
        if not self.camera.start():
            print("Error: Failed to start camera. Exiting.")
            pygame.quit()
            return False
        
        # Start audio detector in a separate thread
        self.audio_detector.start()
        
        # Set up calibration
        self.calibrator.start_calibration((width, height))
        
        # If calibration is enabled in config, start in calibration mode
        self.calibration_mode = self.calibrator.config.get("calibration_enabled", True)
        
        # Set up clock for frame timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Main loop
        self.main_loop()
        
        # Cleanup
        self.cleanup()
        return True
    
    def main_loop(self):
        """Main application loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0  # seconds
            
            # Process pygame events
            self.process_events()
            
            if self.calibration_mode:
                # Handle calibration mode
                self.handle_calibration()
            else:
                # Normal operation mode
                self.process_frame(dt)
            
            # Update display
            pygame.display.flip()
    
    def process_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Global key handlers
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_c:
                    # Toggle calibration mode
                    self.calibration_mode = not self.calibration_mode
                elif event.key == pygame.K_d:
                    # Toggle debug mode
                    self.debug_mode = not self.debug_mode
                
                # Calibration mode specific keys
                if self.calibration_mode:
                    self.handle_calibration_keys(event)
    
    def handle_calibration_keys(self, event):
        """Handle key events during calibration mode."""
        step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        
        if event.key == pygame.K_UP:
            self.calibrator.move_active_corner(0, -step)
        elif event.key == pygame.K_DOWN:
            self.calibrator.move_active_corner(0, step)
        elif event.key == pygame.K_LEFT:
            self.calibrator.move_active_corner(-step, 0)
        elif event.key == pygame.K_RIGHT:
            self.calibrator.move_active_corner(step, 0)
        elif event.key == pygame.K_1:
            self.calibrator.set_active_corner(0)
        elif event.key == pygame.K_2:
            self.calibrator.set_active_corner(1)
        elif event.key == pygame.K_3:
            self.calibrator.set_active_corner(2)
        elif event.key == pygame.K_4:
            self.calibrator.set_active_corner(3)
        elif event.key == pygame.K_RETURN:
            self.calibrator.complete_calibration()
            self.calibration_mode = False
    
    def handle_calibration(self):
        """Handle rendering during calibration mode."""
        # Create test pattern for calibration
        width, height = self.screen.get_size()
        
        # Create a grid test pattern
        surface = pygame.Surface((width, height))
        surface.fill((0, 0, 0))
        
        # Draw grid lines
        grid_size = 50
        for x in range(0, width, grid_size):
            pygame.draw.line(surface, (50, 50, 50), (x, 0), (x, height))
        for y in range(0, height, grid_size):
            pygame.draw.line(surface, (50, 50, 50), (0, y), (width, y))
        
        # Draw central crosshair
        center_x, center_y = width // 2, height // 2
        pygame.draw.line(surface, (255, 255, 255), (center_x, 0), (center_x, height), 2)
        pygame.draw.line(surface, (255, 255, 255), (0, center_y), (width, center_y), 2)
        
        # Draw circles
        pygame.draw.circle(surface, (255, 0, 0), (center_x, center_y), 100, 2)
        pygame.draw.circle(surface, (0, 255, 0), (center_x, center_y), 200, 2)
        pygame.draw.circle(surface, (0, 0, 255), (center_x, center_y), 300, 2)
        
        # Display calibration UI
        self.screen.blit(surface, (0, 0))
        self.calibrator.draw_calibration_ui(self.screen)
    
    def process_frame(self, dt):
        """Process a frame and update the projection display."""
        # Read frame from camera
        frame = self.camera.read()
        if frame is None:
            return
            
        # Skip if we don't have a previous frame yet for motion detection
        prev_frame = self.camera.get_prev_frame()
        if prev_frame is None:
            return
        
        # Detect motion
        motion_detected, motion_contours, motion_mask = self.motion_detector.detect(
            self.camera.get_blurred(), 
            prev_frame
        )
        
        # Get motion center and intensity
        motion_center = self.motion_detector.get_contour_center()
        motion_intensity = self.motion_detector.get_motion_intensity()
        
        # Process hand gestures
        hands_present, hand_positions, gestures = self.gesture_tracker.process_frame(frame)
        
        # Check for audio spikes
        audio_spike = self.audio_detector.is_spike_detected()
        audio_level = self.audio_detector.get_volume_level()
        
        # Update scene state
        state, state_changed, state_data = self.scene_manager.update(
            motion_detected=motion_detected,
            motion_intensity=motion_intensity,
            motion_center=motion_center,
            audio_spike=audio_spike,
            audio_level=audio_level,
            hands_present=hands_present,
            hand_positions=hand_positions,
            gestures=gestures
        )
        
        # Update visual animations, passing the current camera frame for person detection
        self.visual_generator.update(dt, frame)
        
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Render visuals based on scene state
        projection = self.visual_generator.render(state, state_data, self.screen)
        
        # Apply projection calibration if needed
        if self.calibrator.is_calibrated:
            projection = self.calibrator.apply_transform(projection)
        
        # Draw to screen
        self.screen.blit(projection, (0, 0))
        
        # Draw debug information if enabled
        if self.debug_mode:
            self.draw_debug_info(frame, state, motion_detected)
    
    def draw_debug_info(self, frame, state, motion_detected):
        """Draw debug information overlay."""
        width, height = self.screen.get_size()
        margin = 10
        line_height = 20
        
        # Convert OpenCV BGR frame to RGB for pygame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = cv2.resize(rgb_frame, (320, 240))
        
        # Convert frame to pygame surface
        pygame_frame = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        
        # Draw camera preview in top-right corner
        self.screen.blit(pygame_frame, (width - 320 - margin, margin))
        
        # Draw state information
        font = pygame.font.SysFont(None, 24)
        
        lines = [
            f"FPS: {int(self.clock.get_fps())}",
            f"State: {state.name}",
            f"Motion: {'YES' if motion_detected else 'NO'}",
            f"Audio: {self.audio_detector.get_volume_level():.2f}",
            f"Hands: {'Detected' if self.gesture_tracker.get_hands_present() else 'None'}",
            "",
            "Controls:",
            "ESC: Exit",
            "C: Toggle calibration",
            "D: Toggle debug overlay"
        ]
        
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (margin, margin + i * line_height))
    
    def cleanup(self):
        """Clean up resources on exit."""
        print("Cleaning up resources...")
        
        # Stop camera
        if hasattr(self, 'camera'):
            self.camera.stop()
        
        # Stop audio detection
        if hasattr(self, 'audio_detector'):
            self.audio_detector.stop()
        
        # Quit pygame
        pygame.quit()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Diwali Projection System")
    parser.add_argument("--config", help="Path to config file", default=None)
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Find config path
    config_path = None
    if args.config:
        config_path = Path(args.config)
    else:
        config_path = current_dir.parent / "config" / "settings.json"
    
    # Create and start application
    app = DiwaliProjectionApp(config_path)
    
    # Override debug mode from arguments if specified
    if args.debug:
        app.debug_mode = True
    
    # Start the application
    app.start(fullscreen=args.fullscreen)