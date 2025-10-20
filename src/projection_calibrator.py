"""
Projection Calibration Utility for Diwali Projection System.
Aligns the projection with physical surfaces using perspective transformation.
"""

import cv2
import numpy as np
import json
import os
import pygame
from pathlib import Path


class ProjectionCalibrator:
    """Calibrates projection mapping to align with physical surfaces."""
    
    def __init__(self, config_path=None):
        """Initialize the projection calibrator with configuration."""
        # Default config
        self.config = {
            "fullscreen": True,
            "calibration_points": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "calibration_enabled": True
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "projection" in all_config:
                    self.config.update(all_config["projection"])
        
        # Calibration state
        self.corners = []  # Four corner points in [x, y] format
        self.active_corner = 0
        self.is_calibrated = False
        self.transform_matrix = None
        
        # Initialize calibration points from config
        self._init_from_config()
    
    def _init_from_config(self):
        """Initialize corner points from configuration."""
        # Start with normalized corner points
        if not self.corners:
            self.corners = np.array([
                [0.0, 0.0],  # Top-left
                [1.0, 0.0],  # Top-right
                [1.0, 1.0],  # Bottom-right
                [0.0, 1.0]   # Bottom-left
            ], dtype=np.float32)
        
        # Apply saved calibration points if available
        saved_points = self.config.get("calibration_points")
        if saved_points and len(saved_points) == 4:
            for i, point in enumerate(saved_points):
                if len(point) == 2:
                    self.corners[i] = np.array(point, dtype=np.float32)
    
    def start_calibration(self, screen_size):
        """
        Start the calibration process.
        
        Args:
            screen_size: (width, height) of the projection area
        """
        self.is_calibrated = False
        self.screen_size = screen_size
        
        # Convert normalized corners to pixel coordinates
        for i in range(4):
            self.corners[i][0] *= screen_size[0]
            self.corners[i][1] *= screen_size[1]
        
        # Start with the first corner
        self.active_corner = 0
    
    def move_active_corner(self, dx, dy):
        """
        Move the active corner by the specified delta.
        
        Args:
            dx: X-axis movement
            dy: Y-axis movement
        """
        if 0 <= self.active_corner < 4:
            self.corners[self.active_corner][0] += dx
            self.corners[self.active_corner][1] += dy
            self._update_transform()
            return True
        return False
    
    def set_active_corner(self, index):
        """Set the currently active corner (0-3)."""
        if 0 <= index < 4:
            self.active_corner = index
            return True
        return False
    
    def _update_transform(self):
        """Update the perspective transform matrix based on current corners."""
        # Target rectangle (full screen)
        width, height = self.screen_size
        dst_points = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ], dtype=np.float32)
        
        # Calculate perspective transform
        self.transform_matrix = cv2.getPerspectiveTransform(
            dst_points, self.corners
        )
        self.is_calibrated = True
    
    def complete_calibration(self):
        """
        Complete the calibration process and save settings.
        
        Returns:
            success: Boolean indicating if calibration was successful
        """
        if len(self.corners) != 4:
            return False
        
        self._update_transform()
        
        # Normalize and save corner positions to config
        normalized_corners = []
        width, height = self.screen_size
        for corner in self.corners:
            normalized_corners.append([
                corner[0] / width,
                corner[1] / height
            ])
        
        self.config["calibration_points"] = normalized_corners
        
        # Save to config file if path is available
        if hasattr(self, 'config_path') and self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    all_config = json.load(f)
                
                all_config["projection"] = self.config
                
                with open(self.config_path, 'w') as f:
                    json.dump(all_config, f, indent=2)
                    
                print("Calibration saved to config file")
            except Exception as e:
                print(f"Error saving calibration: {e}")
        
        return True
    
    def apply_transform(self, surface):
        """
        Apply perspective transform to a pygame surface.
        
        Args:
            surface: pygame.Surface to transform
            
        Returns:
            Transformed pygame.Surface
        """
        if not self.is_calibrated:
            return surface
        
        # Convert pygame surface to OpenCV image
        pygame_surface_array = pygame.surfarray.array3d(surface)
        cv_image = pygame_surface_array.transpose([1, 0, 2])
        
        # Apply perspective transform
        width, height = surface.get_size()
        warped = cv2.warpPerspective(
            cv_image,
            self.transform_matrix,
            (width, height)
        )
        
        # Convert back to pygame surface
        warped_surface_array = warped.transpose([1, 0, 2])
        result = pygame.surfarray.make_surface(warped_surface_array)
        
        return result
    
    def draw_calibration_ui(self, surface):
        """
        Draw calibration UI elements on the surface.
        
        Args:
            surface: pygame.Surface to draw onto
            
        Returns:
            Modified surface with calibration UI
        """
        # Draw corner points and connect them with lines
        colors = [
            (255, 0, 0),    # Red (top-left)
            (0, 255, 0),    # Green (top-right)
            (0, 0, 255),    # Blue (bottom-right)
            (255, 255, 0)   # Yellow (bottom-left)
        ]
        
        # Draw lines connecting corners
        for i in range(4):
            start = (int(self.corners[i][0]), int(self.corners[i][1]))
            end = (int(self.corners[(i+1)%4][0]), int(self.corners[(i+1)%4][1]))
            pygame.draw.line(surface, (255, 255, 255), start, end, 1)
        
        # Draw corner points
        for i, corner in enumerate(self.corners):
            x, y = int(corner[0]), int(corner[1])
            color = colors[i]
            
            # Make active corner brighter
            if i == self.active_corner:
                radius = 10
                color = (255, 255, 255)  # White for active corner
            else:
                radius = 5
            
            pygame.draw.circle(surface, color, (x, y), radius)
            
            # Draw corner index
            font = pygame.font.SysFont(None, 24)
            label = font.render(str(i+1), True, (255, 255, 255))
            surface.blit(label, (x + 15, y + 15))
        
        # Draw instructions
        font = pygame.font.SysFont(None, 30)
        instructions = [
            "Calibration Mode",
            "Arrow keys: Move corner",
            "1-4: Select corner",
            "Enter: Complete calibration",
            "Esc: Cancel"
        ]
        
        for i, text in enumerate(instructions):
            label = font.render(text, True, (255, 255, 255))
            surface.blit(label, (10, 10 + i * 30))
        
        return surface


# For testing
if __name__ == "__main__":
    import sys
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    # Initialize pygame
    pygame.init()
    
    # Set up display
    flags = pygame.FULLSCREEN if len(sys.argv) > 1 and sys.argv[1] == "fullscreen" else 0
    info = pygame.display.Info()
    width, height = (1280, 720) if not flags else (info.current_w, info.current_h)
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Projection Calibration Tool")
    
    # Create calibrator
    calibrator = ProjectionCalibrator(config_path)
    calibrator.config_path = config_path
    calibrator.start_calibration((width, height))
    
    # Create a test pattern
    def create_test_pattern(size):
        """Create a grid test pattern to visualize calibration."""
        surface = pygame.Surface(size)
        surface.fill((0, 0, 0))
        
        # Draw grid lines
        grid_size = 50
        for x in range(0, size[0], grid_size):
            pygame.draw.line(surface, (50, 50, 50), (x, 0), (x, size[1]))
        for y in range(0, size[1], grid_size):
            pygame.draw.line(surface, (50, 50, 50), (0, y), (size[0], y))
        
        # Draw central crosshair
        center_x, center_y = size[0] // 2, size[1] // 2
        pygame.draw.line(surface, (255, 255, 255), (center_x, 0), (center_x, size[1]), 2)
        pygame.draw.line(surface, (255, 255, 255), (0, center_y), (size[0], center_y), 2)
        
        # Draw circles
        pygame.draw.circle(surface, (255, 0, 0), (center_x, center_y), 100, 2)
        pygame.draw.circle(surface, (0, 255, 0), (center_x, center_y), 200, 2)
        pygame.draw.circle(surface, (0, 0, 255), (center_x, center_y), 300, 2)
        
        return surface
    
    test_pattern = create_test_pattern((width, height))
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    calibration_mode = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Calibration controls
                if calibration_mode:
                    step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                    
                    if event.key == pygame.K_UP:
                        calibrator.move_active_corner(0, -step)
                    elif event.key == pygame.K_DOWN:
                        calibrator.move_active_corner(0, step)
                    elif event.key == pygame.K_LEFT:
                        calibrator.move_active_corner(-step, 0)
                    elif event.key == pygame.K_RIGHT:
                        calibrator.move_active_corner(step, 0)
                    elif event.key == pygame.K_1:
                        calibrator.set_active_corner(0)
                    elif event.key == pygame.K_2:
                        calibrator.set_active_corner(1)
                    elif event.key == pygame.K_3:
                        calibrator.set_active_corner(2)
                    elif event.key == pygame.K_4:
                        calibrator.set_active_corner(3)
                    elif event.key == pygame.K_RETURN:
                        calibrator.complete_calibration()
                        calibration_mode = False
                else:
                    # Switch back to calibration mode with 'c'
                    if event.key == pygame.K_c:
                        calibration_mode = True
        
        # Draw test pattern
        screen.blit(test_pattern, (0, 0))
        
        if calibration_mode:
            # Draw calibration UI
            calibrator.draw_calibration_ui(screen)
        else:
            # Apply perspective transform
            transformed = calibrator.apply_transform(test_pattern)
            screen.blit(transformed, (0, 0))
            
            # Draw instructions for returning to calibration
            font = pygame.font.SysFont(None, 30)
            text = font.render("Press 'C' to return to calibration", True, (255, 255, 255))
            screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()