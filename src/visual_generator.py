"""
Visual Generation Module for Diwali Projection System.
Renders dynamic visual effects including diyas, fireworks, rangoli patterns, and aura effects.
"""

import pygame
import numpy as np
import cv2
import json
import os
import random
import math
import time
import colorsys
from pathlib import Path
from scene_manager import VisualState
from person_outline_detector import PersonOutlineDetector


class FloatingObject:
    """Class to represent objects that float/drift across the screen."""
    
    def __init__(self, image, screen_size, speed_factor=1.0, rotation_speed=None, size_factor=1.0):
        """Initialize a floating object with its image and movement parameters."""
        self.original_image = image
        self.screen_width, self.screen_height = screen_size
        
        # Apply size factor
        orig_width, orig_height = self.original_image.get_size()
        self.width = int(orig_width * size_factor)
        self.height = int(orig_height * size_factor)
        self.image = pygame.transform.smoothscale(self.original_image, (self.width, self.height))
        
        # Initial position - can start from any edge
        edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        if edge == 0:  # Top edge
            self.x = random.randint(-self.width, self.screen_width)
            self.y = -self.height
            self.dx = random.uniform(-0.5, 0.5) * speed_factor
            self.dy = random.uniform(0.2, 1.0) * speed_factor
        elif edge == 1:  # Right edge
            self.x = self.screen_width
            self.y = random.randint(-self.height, self.screen_height)
            self.dx = random.uniform(-1.0, -0.2) * speed_factor
            self.dy = random.uniform(-0.5, 0.5) * speed_factor
        elif edge == 2:  # Bottom edge
            self.x = random.randint(-self.width, self.screen_width)
            self.y = self.screen_height
            self.dx = random.uniform(-0.5, 0.5) * speed_factor
            self.dy = random.uniform(-1.0, -0.2) * speed_factor
        else:  # Left edge
            self.x = -self.width
            self.y = random.randint(-self.height, self.screen_height)
            self.dx = random.uniform(0.2, 1.0) * speed_factor
            self.dy = random.uniform(-0.5, 0.5) * speed_factor
            
        # Add some randomness to the movement
        self.wobble_x = random.uniform(0, math.pi * 2)
        self.wobble_y = random.uniform(0, math.pi * 2)
        self.wobble_speed_x = random.uniform(0.01, 0.05)
        self.wobble_speed_y = random.uniform(0.01, 0.05)
        self.wobble_amount = random.uniform(0.2, 1.0)
        
        # Rotation
        self.angle = random.uniform(0, 360)
        self.rotation_speed = rotation_speed if rotation_speed is not None else random.uniform(-1, 1)
        
        # Alpha for fading in/out
        self.alpha = 0
        self.fade_speed = random.uniform(1, 3)  # Speed of fade in/out
        self.is_fading_in = True
        
    def update(self, dt):
        """Update the position and state of the floating object."""
        # Update position with wobble
        self.wobble_x += self.wobble_speed_x
        self.wobble_y += self.wobble_speed_y
        
        # Add wobble to movement
        wobble_dx = math.sin(self.wobble_x) * self.wobble_amount
        wobble_dy = math.sin(self.wobble_y) * self.wobble_amount
        
        self.x += (self.dx + wobble_dx) * 60 * dt
        self.y += (self.dy + wobble_dy) * 60 * dt
        
        # Update rotation
        self.angle = (self.angle + self.rotation_speed * dt) % 360
        
        # Update alpha for fade effect
        if self.is_fading_in:
            self.alpha = min(255, self.alpha + self.fade_speed * dt * 60)
            if self.alpha >= 255:
                self.alpha = 255
                self.is_fading_in = False
        
        # Check if object is off-screen plus a margin to allow for proper exit
        margin = max(self.width, self.height) * 2
        return (self.x < -margin or 
                self.x > self.screen_width + margin or 
                self.y < -margin or 
                self.y > self.screen_height + margin)
                
    def draw(self, surface):
        """Draw the floating object on the given surface."""
        # Create a copy with correct alpha
        image_copy = self.image.copy()
        image_copy.set_alpha(int(self.alpha))
        
        # Rotate the image
        rotated = pygame.transform.rotate(image_copy, self.angle)
        
        # Get the rect for the rotated image to ensure it's centered correctly
        rect = rotated.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        
        # Draw the rotated image
        surface.blit(rotated, rect.topleft)


class VisualGenerator:
    """Generates and renders visual effects for the projection system."""
    
    def __init__(self, config_path=None):
        """Initialize the visual generator with configuration."""
        # Default config
        self.config = {
            "diya": {
                "fade_duration": 0.5,
                "scale_factor": 0.5,
                "max_instances": 10,
                "floating": {
                    "enabled": True,
                    "max_count": 5,
                    "speed_factor": 0.5,
                    "spawn_rate": 5.0  # seconds between spawns
                }
            },
            "fireworks": {
                "particle_count": 100,
                "lifetime": 2.0,
                "colors": ["#FF5733", "#FFC300", "#DAF7A6", "#C70039", "#900C3F"]
            },
            "rangoli": {
                "pattern_complexity": 3,
                "color_scheme": "traditional",
                "rotation_speed": 0.01,
                "floating": {
                    "enabled": True,
                    "max_count": 3,
                    "speed_factor": 0.3,
                    "spawn_rate": 8.0  # seconds between spawns
                }
            },
            "aura": {
                "blur_radius": 15,
                "opacity": 0.7,
                "color": [255, 223, 0]
            },
            "background": {
                "enabled": True,
                "image_path": "diwali_bg.jpeg",
                "opacity": 0.8
            }
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "visual_effects" in all_config:
                    self.config.update(all_config["visual_effects"])
        
        # Initialize pygame for rendering
        pygame.init()
        
        # Visual resources
        self.assets_dir = None
        self.diya_images = []
        self.rangoli_patterns = []
        self.firework_particles = {}  # Key: origin tuple, Value: list of particle dictionaries
        self.background_image = None  # Will hold the Diwali background image
        
        # Initialize person outline detector for ethereal effects
        self.person_outline_detector = PersonOutlineDetector(config_path)
        self.ethereal_mask = None
        self.has_person = False
        self.ethereal_color_index = 0
        self.ethereal_last_color_change = time.time()
        
        # Animation state
        self.rangoli_angle = 0.0
        self.current_frame = 0
        
        # Psychedelic rangoli state
        self.mandala_surfaces = []
        self.color_cycle_hue = 0.0
        self.last_mandala_generation = time.time()
        
        # Floating objects
        self.floating_diyas = []
        self.floating_rangolis = []
        self.last_diya_spawn_time = time.time()
        self.last_rangoli_spawn_time = time.time()
        self.screen_size = (1280, 720)  # Default - will be updated in render
        
        # Get settings from config
        rangoli_config = self.config.get("rangoli", {})
        self.mandala_refresh_rate = rangoli_config.get("psychedelic", {}).get("mandala_refresh_rate", 5.0)
        
        # Initialize assets
        self._initialize_assets()
        
        # Generate initial psychedelic mandalas immediately
        self._generate_bezier_mandalas()
        
        # Print status message for mandala creation
        print(f"Generated {len(self.mandala_surfaces)} psychedelic mandala patterns")
    
    def _initialize_assets(self):
        """Load and prepare visual assets."""
        # Find assets directory relative to this file
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = current_dir.parent / "assets"
        
        # Load background image
        bg_path = self.assets_dir / "diwali_bg.jpeg"
        if bg_path.exists():
            try:
                self.background_image = pygame.image.load(str(bg_path))
                print(f"Loaded background image: {bg_path}")
            except Exception as e:
                print(f"Error loading background image {bg_path}: {e}")
                self.background_image = None
        else:
            print(f"Background image not found: {bg_path}")
            self.background_image = None
        
        # Load diya images
        diya_dir = self.assets_dir / "diyas"
        if diya_dir.exists():
            for file in diya_dir.glob("*.png"):
                try:
                    img = pygame.image.load(str(file)).convert_alpha()
                    self.diya_images.append(img)
                except Exception as e:
                    print(f"Error loading diya image {file}: {e}")
        
        # If no diya images found, create a default one
        if not self.diya_images:
            print("No diya images found, creating default")
            self._create_default_diya()
        
        # Load rangoli patterns
        rangoli_dir = self.assets_dir / "rangoli"
        if rangoli_dir.exists():
            for file in rangoli_dir.glob("*.png"):
                try:
                    img = pygame.image.load(str(file)).convert_alpha()
                    self.rangoli_patterns.append(img)
                except Exception as e:
                    print(f"Error loading rangoli pattern {file}: {e}")
        
        # If no rangoli patterns found, create default ones
        if not self.rangoli_patterns:
            print("No rangoli patterns found, creating defaults")
            self._create_default_rangoli_patterns()
    
    def _create_default_diya(self):
        """Create a default diya image if no assets are available."""
        size = (100, 100)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Draw a simple diya shape
        pygame.draw.ellipse(surface, (200, 100, 0), (0, 50, 100, 50))  # Base
        pygame.draw.ellipse(surface, (255, 150, 0), (25, 25, 50, 50))  # Bowl
        pygame.draw.ellipse(surface, (255, 255, 0), (40, 20, 20, 20))  # Flame
        
        self.diya_images.append(surface)
    
    def _create_default_rangoli_patterns(self):
        """Create default rangoli patterns if no assets are available."""
        sizes = [(300, 300), (400, 400), (500, 500)]
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (128, 0, 128)   # Purple
        ]
        
        for size in sizes:
            surface = pygame.Surface(size, pygame.SRCALPHA)
            
            # Draw a colorful rangoli pattern
            center = (size[0] // 2, size[1] // 2)
            radius = min(size) // 2 - 10
            
            # Draw concentric circles
            for i in range(5):
                r = radius * (5-i) // 5
                color = colors[i % len(colors)]
                pygame.draw.circle(surface, color, center, r, 3)
            
            # Draw radial lines
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x = center[0] + radius * math.cos(rad)
                y = center[1] + radius * math.sin(rad)
                pygame.draw.line(surface, colors[angle // 60], center, (x, y), 2)
            
            # Draw decorative dots
            for i in range(8):
                angle = math.radians(i * 45)
                for j in range(3):
                    r = radius * (j + 1) // 4
                    x = int(center[0] + r * math.cos(angle))
                    y = int(center[1] + r * math.sin(angle))
                    dot_radius = 5
                    pygame.draw.circle(surface, colors[(i+j) % len(colors)], (x, y), dot_radius)
            
            self.rangoli_patterns.append(surface)
            
    def _generate_bezier_mandalas(self):
        """Generate Diwali rangoli patterns using the specified algorithm."""
        try:
            # Clear existing mandala surfaces
            self.mandala_surfaces = []
            
            # Get screen dimensions for sizing mandalas
            # Use a reasonable default if we don't have it yet
            size = 600
            
            # Get configuration settings
            rangoli_config = self.config.get("rangoli", {})
            psychedelic_config = rangoli_config.get("psychedelic", {})
            
            # Generate a few different mandalas with varying seeds
            num_mandalas = 5  # Generate 5 different rangoli patterns
            sizes = [size * factor for factor in [0.8, 1.0, 1.2]]
            
            for mandala_size in sizes:
                for seed in range(num_mandalas):
                    # Create a Diwali rangoli surface
                    surface = self._create_diwali_rangoli(
                        size=int(mandala_size),
                        seed=seed + int(time.time() * 10) % 1000  # Use time as part of the seed for variety
                    )
                    
                    if surface is not None:
                        self.mandala_surfaces.append(surface)
                        
            print(f"Generated {len(self.mandala_surfaces)} Diwali rangoli patterns")
                        
        except Exception as e:
            print(f"Error generating rangoli patterns: {e}")
            # If rangoli generation fails, ensure we have at least one surface
            if not self.mandala_surfaces and self.rangoli_patterns:
                self.mandala_surfaces = self.rangoli_patterns.copy()
                
    def _create_diwali_rangoli(self, size=600, seed=0):
        """Create a Diwali rangoli pattern using traditional design elements."""
        try:
            # Set random seed for reproducible designs
            random.seed(seed)
            np.random.seed(seed)
            
            # Create a surface with alpha channel
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            # Fill with completely transparent black (RGBA all zeros)
            surface.fill((0, 0, 0, 0))
            center = (size // 2, size // 2)
            
            # 1) Global Styling & Palettes
            # Traditional Diwali/Indian color palette
            base_palette = [
                (255, 153, 51),    # saffron (#FF9933)
                (255, 163, 0),     # marigold (#FFA300)
                (227, 66, 52),     # vermilion (#E34234)
                (255, 93, 162),    # gulal_pink (#FF5DA2)
                (0, 106, 113),     # peacock_blue (#006A71)
                (43, 182, 115),    # emerald (#2BB673)
                (255, 211, 78),    # turmeric_yellow (#FFD34E)
                (255, 204, 102),   # diya_glow (#FFCC66)
                (247, 244, 239)    # white_rice (#F7F4EF)
            ]
            outline_color = (60, 31, 11)  # dark_brown (#3C1F0B)
            dot_color = (247, 244, 239)   # white_rice
            
            # 2) Mandala Symmetry & Layout
            # Choose number of segments with weighted probability
            segments_options = [8, 10, 12, 16]
            segments_weights = [0.25, 0.25, 0.35, 0.15]
            segments_cumulative = np.cumsum(segments_weights)
            r = random.random()
            segments = segments_options[np.searchsorted(segments_cumulative, r)]
            
            # Concentric guide radii (normalized 0..1 of min(width, height)/2)
            max_radius = size // 2
            radii = [r * max_radius for r in [0.10, 0.18, 0.26, 0.36, 0.48, 0.62, 0.78, 0.92]]
            
            # 3) Background (deep navy or floor maroon)
            # Choose between navy and maroon
            bg_colors = [(16, 25, 58, 200), (115, 25, 25, 200)]  # with alpha
            bg_color = random.choice(bg_colors)
            
            # Fill with radial gradient
            # Create a larger surface for the gradient
            gradient_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Create a radial gradient
            for radius in range(size // 2, 0, -1):
                # Calculate color alpha based on radius
                alpha = int(255 * (radius / (size / 2)))
                # Darken color slightly for inner part
                darken_factor = 0.7 + 0.3 * (radius / (size / 2))
                color = tuple(min(255, int(c * darken_factor)) for c in bg_color[:3]) + (min(255, alpha),)
                # Draw circle
                pygame.draw.circle(gradient_surf, color, center, radius)
            
            # Apply to main surface
            surface.blit(gradient_surf, (0, 0))
            
            # 4) Lotus Base Layer (Bézier petals)
            # Since we don't have actual Bezier curves, we'll approximate with polygons
            petal_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            base_radius = radii[4]
            petal_len = random.uniform(0.22, 0.30) * max_radius
            
            for i in range(segments):
                # Pick color from palette with slight variation
                color = random.choice(base_palette)
                # Add some variance to the color
                color = tuple(min(255, max(0, c + random.randint(-20, 20))) for c in color)
                
                # Draw petal approximation
                angle = i * (2 * math.pi / segments)
                # Bezier points for a petal shape
                petal_width = random.uniform(0.16, 0.22) * max_radius
                cp_spread = random.uniform(0.18, 0.26) * max_radius
                
                # Create polygon points approximating a Bezier petal
                points = []
                # Start point at base radius
                start_x = center[0] + base_radius * math.cos(angle)
                start_y = center[1] + base_radius * math.sin(angle)
                points.append((start_x, start_y))
                
                # Control points for the shape
                right_angle = angle + math.pi/6
                left_angle = angle - math.pi/6
                
                # Right side control point
                right_cp_x = start_x + cp_spread * math.cos(right_angle)
                right_cp_y = start_y + cp_spread * math.sin(right_angle)
                points.append((right_cp_x, right_cp_y))
                
                # Tip point
                tip_x = center[0] + (base_radius + petal_len) * math.cos(angle)
                tip_y = center[1] + (base_radius + petal_len) * math.sin(angle)
                points.append((tip_x, tip_y))
                
                # Left side control point
                left_cp_x = start_x + cp_spread * math.cos(left_angle)
                left_cp_y = start_y + cp_spread * math.sin(left_angle)
                points.append((left_cp_x, left_cp_y))
                
                # Complete the shape
                points.append((start_x, start_y))
                
                # Draw the petal
                pygame.draw.polygon(petal_layer, color, points)
                # Add outline
                thickness = random.uniform(1.5, 3.0)
                pygame.draw.lines(petal_layer, outline_color, True, points, int(thickness))
            
            # Blit petal layer
            surface.blit(petal_layer, (0, 0))
            
            # 5) Inner Rosette (fine filigree)
            rosette_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            r_small = radii[2]
            
            for k in range(segments * 2):
                # Shift hue slightly from palette
                hue = random.choice(base_palette)
                hue = tuple(min(255, max(0, c + random.randint(-25, 25))) for c in hue)
                stroke = random.uniform(1.0, 1.6)
                
                # Create spiral approximation
                angle = k * (math.pi / segments)
                radius_start = r_small * 0.7
                radius_end = r_small
                turns = random.uniform(0.75, 1.25)
                
                # Draw spiral as a series of connected lines
                points = []
                num_points = 20
                for t in range(num_points + 1):
                    t_normalized = t / num_points
                    radius = radius_start + (radius_end - radius_start) * t_normalized
                    spiral_angle = angle + turns * 2 * math.pi * t_normalized
                    x = center[0] + radius * math.cos(spiral_angle)
                    y = center[1] + radius * math.sin(spiral_angle)
                    points.append((x, y))
                
                # Draw the spiral
                if len(points) > 1:
                    pygame.draw.lines(rosette_layer, hue, False, points, int(stroke))
            
            # Blit rosette layer with multiply blend (approximate with alpha)
            rosette_layer.set_alpha(217)  # 0.85 * 255
            surface.blit(rosette_layer, (0, 0))
            
            # 6) Diya Motifs at ring
            diya_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            diya_count = segments
            r_diya = radii[6]
            vermilion = (227, 66, 52)
            diya_glow = (255, 204, 102)
            
            for d in range(diya_count):
                angle = d * (2 * math.pi / diya_count)
                pos_x = center[0] + r_diya * math.cos(angle)
                pos_y = center[1] + r_diya * math.sin(angle)
                
                # Draw diya (simplified)
                bowl_width = random.uniform(0.10, 0.14) * max_radius
                bowl_depth = random.uniform(0.05, 0.07) * max_radius
                flame_height = random.uniform(0.06, 0.09) * max_radius
                
                # Bowl points
                bowl_left_x = pos_x - bowl_width/2
                bowl_right_x = pos_x + bowl_width/2
                bowl_bottom_y = pos_y + bowl_depth
                
                # Draw bowl as a half-ellipse approximation
                bowl_points = []
                for t in range(11):
                    t_angle = math.pi * t / 10
                    x = pos_x + (bowl_width/2) * math.cos(t_angle)
                    y = pos_y + bowl_depth * math.sin(t_angle)
                    if y > pos_y:  # Only bottom half
                        bowl_points.append((x, y))
                
                # Draw bowl
                pygame.draw.polygon(diya_layer, vermilion, bowl_points)
                pygame.draw.lines(diya_layer, outline_color, False, bowl_points, 2)
                
                # Draw flame
                flame_points = [
                    (pos_x, pos_y),
                    (pos_x - bowl_width/4, pos_y - flame_height/2),
                    (pos_x, pos_y - flame_height),
                    (pos_x + bowl_width/4, pos_y - flame_height/2)
                ]
                pygame.draw.polygon(diya_layer, diya_glow, flame_points)
                
                # Add glow around flame
                glow_radius = random.uniform(0.04, 0.06) * max_radius
                glow_surf = pygame.Surface((int(glow_radius*2), int(glow_radius*2)), pygame.SRCALPHA)
                
                for r in range(int(glow_radius), 0, -1):
                    alpha = int(153 * (r / glow_radius))  # Max alpha 0.6 * 255
                    pygame.draw.circle(glow_surf, diya_glow + (alpha,), (int(glow_radius), int(glow_radius)), r)
                
                # Position the glow
                glow_pos = (pos_x - glow_radius, pos_y - flame_height - glow_radius)
                diya_layer.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ADD)
            
            # Blit diya layer
            diya_layer.set_alpha(242)  # 0.95 * 255
            surface.blit(diya_layer, (0, 0))
            
            # 7) Paisley / Peacock Feather Ring
            paisley_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            r_p = radii[5]
            
            for p in range(segments):
                # Interpolate between colors
                t = random.random()
                peacock_blue = (0, 106, 113)
                emerald = (43, 182, 115)
                fill = tuple(int(peacock_blue[i] * (1-t) + emerald[i] * t) for i in range(3))
                
                angle = p * (2 * math.pi / segments)
                # Flip every other paisley
                flip_factor = -1 if p % 2 == 0 else 1
                
                # Paisley parameters
                length = random.uniform(0.12, 0.18) * max_radius
                thickness = random.uniform(0.06, 0.10) * max_radius
                curl = random.uniform(0.45, 0.70)
                
                # Draw paisley approximation using polygon
                # Base position on the circle
                base_x = center[0] + r_p * math.cos(angle)
                base_y = center[1] + r_p * math.sin(angle)
                
                # Direction vectors
                dir_x = math.cos(angle + math.pi/2 * flip_factor)
                dir_y = math.sin(angle + math.pi/2 * flip_factor)
                
                # Calculate paisley points
                paisley_points = []
                
                # Base point
                paisley_points.append((base_x, base_y))
                
                # Curve outward
                curve_x = base_x + length * 0.6 * math.cos(angle)
                curve_y = base_y + length * 0.6 * math.sin(angle)
                paisley_points.append((curve_x + thickness * dir_x, curve_y + thickness * dir_y))
                
                # Tip
                tip_x = base_x + length * math.cos(angle)
                tip_y = base_y + length * math.sin(angle)
                paisley_points.append((tip_x, tip_y))
                
                # Curve back
                paisley_points.append((curve_x - thickness * dir_x, curve_y - thickness * dir_y))
                
                # Close shape
                paisley_points.append((base_x, base_y))
                
                # Draw the paisley
                pygame.draw.polygon(paisley_layer, fill, paisley_points)
                pygame.draw.lines(paisley_layer, outline_color, True, paisley_points, 2)
                
                # Add eye-dot
                turmeric_yellow = (255, 211, 78)
                dot_radius = random.uniform(0.008, 0.012) * max_radius
                pygame.draw.circle(paisley_layer, turmeric_yellow, (tip_x, tip_y), int(dot_radius))
                pygame.draw.circle(paisley_layer, outline_color, (tip_x, tip_y), int(dot_radius), 1)
            
            # Blit paisley layer
            paisley_layer.set_alpha(204)  # 0.8 * 255
            surface.blit(paisley_layer, (0, 0))
            
            # 8) Kolam Dot Grid & Connectors
            kolam_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            grid_r = radii[3]
            dots_per_seg = random.randint(3, 4)
            
            for s in range(segments):
                angle_start = s * (2 * math.pi / segments)
                angle_end = (s + 1) * (2 * math.pi / segments)
                
                # Place dots along the segment
                points = []
                for d in range(dots_per_seg):
                    rad_spacing = random.uniform(0.035, 0.05) * max_radius
                    r = grid_r + d * rad_spacing
                    # Add a tiny bit of jitter
                    jitter_angle = angle_start + random.uniform(-0.05, 0.05)
                    x = center[0] + r * math.cos(jitter_angle)
                    y = center[1] + r * math.sin(jitter_angle)
                    points.append((x, y))
                
                # Connect dots with bezier-like curves
                for i in range(len(points) - 1):
                    a, b = points[i], points[i+1]
                    # Create a slightly curved line between points
                    # Find midpoint and push it out slightly
                    mid_x = (a[0] + b[0]) / 2
                    mid_y = (a[1] + b[1]) / 2
                    
                    # Direction perpendicular to line
                    dx = b[0] - a[0]
                    dy = b[1] - a[1]
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        perpx = -dy / length
                        perpy = dx / length
                    else:
                        perpx, perpy = 0, 0
                    
                    # Bow amount
                    bow = random.uniform(0.15, 0.25) * length
                    mid_x += perpx * bow
                    mid_y += perpy * bow
                    
                    # Draw using a series of small line segments to approximate curve
                    curve_points = []
                    steps = 10
                    for t in range(steps + 1):
                        t_normalized = t / steps
                        # Quadratic Bezier formula
                        qx = (1-t_normalized)**2 * a[0] + 2*(1-t_normalized)*t_normalized*mid_x + t_normalized**2 * b[0]
                        qy = (1-t_normalized)**2 * a[1] + 2*(1-t_normalized)*t_normalized*mid_y + t_normalized**2 * b[1]
                        curve_points.append((qx, qy))
                    
                    # Draw the curve
                    pygame.draw.lines(kolam_layer, dot_color, False, curve_points, max(1, int(random.uniform(1.0, 1.4))))
                
                # Draw dots
                for p in points:
                    dot_radius = random.uniform(0.006, 0.010) * max_radius
                    pygame.draw.circle(kolam_layer, dot_color, p, int(dot_radius))
            
            # Blit kolam layer
            kolam_layer.set_alpha(230)  # 0.9 * 255
            surface.blit(kolam_layer, (0, 0))
            
            # 9) Outer Garland & Border
            border_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            border_r = radii[7]
            
            # Draw wave ring (simplified with segments)
            saffron = (255, 153, 51)
            wave_points = []
            num_wave_points = segments * 4
            amplitude = random.uniform(0.015, 0.025) * max_radius
            
            for i in range(num_wave_points + 1):
                angle = i * (2 * math.pi / num_wave_points)
                r = border_r + amplitude * math.sin(segments * angle)
                x = center[0] + r * math.cos(angle)
                y = center[1] + r * math.sin(angle)
                wave_points.append((x, y))
            
            # Draw the garland
            pygame.draw.lines(border_layer, saffron, True, wave_points, int(random.uniform(2.0, 3.0)))
            
            # Draw outer circle
            pygame.draw.circle(border_layer, outline_color, center, int(border_r + 0.015 * max_radius), int(1.2))
            
            # Blit border layer
            surface.blit(border_layer, (0, 0))
            
            # 10) Accent Sprinkles (rangoli powder)
            sprinkle_layer = pygame.Surface((size, size), pygame.SRCALPHA)
            n_specks = random.randint(800, 1400)
            
            for n in range(n_specks):
                r = random.uniform(radii[0], radii[7] + 0.02 * max_radius)
                theta = random.uniform(0, 2 * math.pi)
                speck_size = random.uniform(0.002, 0.006) * max_radius
                color = random.choice(base_palette)
                
                # Calculate position
                x = center[0] + r * math.cos(theta)
                y = center[1] + r * math.sin(theta)
                
                # Draw speck with soft edge (using multiple circles with decreasing opacity)
                for i in range(3):
                    radius = speck_size * (3-i) / 3
                    alpha = 120 - i * 30  # Decreasing alpha for softer edge
                    rgba_color = color + (alpha,)
                    pygame.draw.circle(sprinkle_layer, rgba_color, (int(x), int(y)), max(1, int(radius)))
            
            # Blit sprinkle layer
            sprinkle_layer.set_alpha(217)  # 0.85 * 255
            surface.blit(sprinkle_layer, (0, 0), special_flags=pygame.BLEND_ADD)
            
            # 11) Optional Om/Aum Glyph
            if random.random() < 0.35:
                glyph_layer = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # We'll create a simplified Om symbol
                glyph_scale = random.uniform(0.25, 0.32)
                glyph_size = int(size * glyph_scale)
                
                # Get the position for the glyph
                glyph_x = center[0] - glyph_size // 2
                glyph_y = center[1] - glyph_size // 2
                
                # Create a simple approximation of Om symbol
                # (In a real implementation, you might load an image or use a more complex path)
                gulal_pink = (255, 93, 162)
                
                # Draw a circular base
                pygame.draw.circle(glyph_layer, gulal_pink, center, int(glyph_size // 3))
                pygame.draw.circle(glyph_layer, outline_color, center, int(glyph_size // 3), 2)
                
                # Add a curve on top
                curve_points = []
                curve_center_x = center[0]
                curve_center_y = center[1] - glyph_size // 4
                
                for angle in range(0, 181, 10):
                    rad = math.radians(angle)
                    x = curve_center_x + (glyph_size // 4) * math.cos(rad)
                    y = curve_center_y + (glyph_size // 4) * math.sin(rad)
                    curve_points.append((x, y))
                
                pygame.draw.lines(glyph_layer, outline_color, False, curve_points, 2)
                
                # Blit glyph layer
                glyph_layer.set_alpha(204)  # 0.8 * 255
                surface.blit(glyph_layer, (0, 0))
            
            # Reset random seed
            random.seed()
            np.random.seed()
            
            return surface
            
        except Exception as e:
            print(f"Error creating Diwali rangoli: {e}")
            import traceback
            traceback.print_exc()
            # Reset random seed
            random.seed()
            np.random.seed()
            return None
    
    def _create_psychedelic_mandala(self, size=600, n_segments=5, n_rotations=12):
        """Create a single psychedelic mandala using pygame drawing primitives."""
        try:
            # Create a surface with alpha channel - this is transparent by default
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            # Fill with completely transparent black (RGBA all zeros)
            surface.fill((0, 0, 0, 0))
            center = (size // 2, size // 2)
            
            # Generate multiple layers for a more complex pattern
            for layer in range(3):
                # Generate a different set of colors for each layer
                colors = self._generate_psychedelic_colors(n_rotations)
                
                # Scale factor for this layer
                scale = 0.7 - 0.15 * layer  # First layer is largest
                max_radius = size // 2 * scale
                
                # Generate points for each segment
                segment_points = []
                for i in range(n_segments):
                    # Random angle and distance from center
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(0.3, 0.9) * max_radius
                    x = center[0] + dist * math.cos(angle)
                    y = center[1] + dist * math.sin(angle)
                    segment_points.append((x, y))
                
                # Draw each rotation of the segment
                for i in range(n_rotations):
                    # Rotate around center by i * (360/n_rotations) degrees
                    angle = i * (2 * math.pi / n_rotations)
                    rotated_points = self._rotate_points(segment_points, center, angle)
                    
                    # Draw lines connecting the rotated points
                    if len(rotated_points) >= 2:
                        # Draw closed polygon with psychedelic color
                        color_idx = i % len(colors)
                        color = colors[color_idx]
                        
                        # Convert from [0-1] float to [0-255] int for pygame
                        # Ensure alpha channel is present and properly set
                        pygame_color = (
                            int(color[0] * 255),
                            int(color[1] * 255),
                            int(color[2] * 255),
                            int(color[3] * 180) if len(color) > 3 else 180  # Slightly reduced opacity
                        )
                        
                        # Draw polygon or lines
                        if random.random() > 0.5:
                            # Draw filled polygon with semi-transparent color
                            pygame.draw.polygon(surface, pygame_color, rotated_points, 0)
                        else:
                            # Draw outline only
                            pygame.draw.polygon(surface, pygame_color, rotated_points, 
                                             max(1, int(size / 200)))  # Scale line width with image size
                        
                        # Sometimes add circles at the points
                        if random.random() > 0.7:
                            for point in rotated_points:
                                pygame.draw.circle(
                                    surface, 
                                    pygame_color, 
                                    (int(point[0]), int(point[1])), 
                                    max(2, int(size / 150))
                                )
            
            # Add some final decorative elements
            self._add_decorative_elements(surface, center, size)
            
            return surface
            
        except Exception as e:
            print(f"Error creating mandala: {e}")
            return None
            
    def _rotate_points(self, points, center, angle):
        """Rotate points around the given center by the specified angle."""
        rotated = []
        for x, y in points:
            # Translate to origin
            x -= center[0]
            y -= center[1]
            
            # Rotate
            x_rot = x * math.cos(angle) - y * math.sin(angle)
            y_rot = x * math.sin(angle) + y * math.cos(angle)
            
            # Translate back
            rotated.append((x_rot + center[0], y_rot + center[1]))
        
        return rotated
        
    def _add_decorative_elements(self, surface, center, size):
        """Add decorative elements to the mandala."""
        # Draw concentric circles
        for i in range(3, 8):
            radius = size * (i / 20)
            color = self._generate_psychedelic_colors(1)[0]
            # Lower alpha value for better transparency
            pygame_color = (
                int(color[0] * 255),
                int(color[1] * 255),
                int(color[2] * 255),
                int(color[3] * 120) if len(color) > 3 else 120  # More transparent
            )
            pygame.draw.circle(
                surface, 
                pygame_color, 
                center, 
                int(radius),
                max(1, int(size / 200))  # Scale line width with image size
            )
            
        # Draw radiating lines
        for i in range(18):
            angle = i * (2 * math.pi / 18)
            x = center[0] + (size // 2 - 10) * math.cos(angle)
            y = center[1] + (size // 2 - 10) * math.sin(angle)
            color = self._generate_psychedelic_colors(1)[0]
            # Lower alpha value for better transparency
            pygame_color = (
                int(color[0] * 255),
                int(color[1] * 255),
                int(color[2] * 255),
                int(color[3] * 150) if len(color) > 3 else 150  # Semi-transparent
            )
            pygame.draw.line(
                surface, 
                pygame_color, 
                center, 
                (x, y), 
                max(1, int(size / 300))  # Scale line width with image size
            )
            
    def _generate_psychedelic_colors(self, num_colors):
        """Generate a list of psychedelic colors with proper transparency."""
        colors = []
        # Start with a random hue for variety
        hue_start = random.random()
        
        # Define some classic psychedelic color combinations
        psychedelic_palettes = [
            # Classic psychedelic
            [(0.95, 1.0, 1.0), (0.6, 1.0, 1.0), (0.15, 1.0, 1.0), (0.3, 1.0, 1.0)],
            # Neon trip
            [(0.8, 1.0, 1.0), (0.5, 1.0, 1.0), (0.3, 1.0, 1.0), (0.0, 1.0, 1.0)],
            # Electric dream
            [(0.7, 1.0, 1.0), (0.9, 1.0, 1.0), (0.55, 1.0, 1.0), (0.2, 1.0, 1.0)]
        ]
        
        # Randomly select a palette to base our colors on
        base_palette = random.choice(psychedelic_palettes)
        
        for i in range(num_colors):
            # Use golden ratio for even distribution of hues
            golden_ratio = 0.618033988749895
            hue = (hue_start + i * golden_ratio) % 1.0
            
            # Sometimes use base palette colors for consistency
            if random.random() < 0.4 and base_palette:
                base_hsv = random.choice(base_palette)
                # Add some variation to the base color
                hue = (base_hsv[0] + random.uniform(-0.05, 0.05)) % 1.0
                saturation = min(1.0, base_hsv[1] * random.uniform(0.9, 1.1))
                value = min(1.0, base_hsv[2] * random.uniform(0.9, 1.1))
            else:
                # High saturation and value for psychedelic look
                saturation = 0.9 + random.random() * 0.1  # Very saturated
                value = 0.85 + random.random() * 0.15  # Bright
            
            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            
            # Use lower alpha values to ensure proper transparency
            # This helps prevent the "weird background" issue
            # For filled areas, use lower alpha
            if random.random() > 0.7:
                # Some colors will be more transparent for contrast
                alpha = 0.3 + random.random() * 0.3  # Between 0.3 and 0.6
            else:
                # Most colors will have medium transparency
                alpha = 0.5 + random.random() * 0.3  # Between 0.5 and 0.8
            
            # Return as RGBA tuple
            colors.append((r, g, b, alpha))
            
        return colors
    
    def _create_firework_particles(self, origin, count=100):
        """Create a new firework explosion at the given origin."""
        # Reduce particle count to make fireworks less noisy
        count = min(count, 50)  # Limit to a maximum of 50 particles
        
        particles = []
        for _ in range(count):
            # Random angle and velocity (reduced speed)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)  # Slower particles
            
            # Random color from config
            color_hex = random.choice(self.config["fireworks"]["colors"])
            color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Random lifetime (shortened)
            lifetime = random.uniform(0.5, min(1.5, self.config["fireworks"]["lifetime"]))
            
            particles.append({
                "x": origin[0],
                "y": origin[1],
                "dx": speed * math.cos(angle),
                "dy": speed * math.sin(angle),
                "color": color_rgb,
                "size": random.randint(1, 3),  # Smaller particles
                "lifetime": lifetime,
                "age": 0
            })
        return particles
    
    def update(self, dt, current_frame=None):
        """
        Update visual elements animations.
        
        Args:
            dt: Time delta in seconds since last update
            current_frame: Optional current camera frame for person detection
        """
        # Update rangoli rotation
        rotation_speed = self.config.get("rangoli", {}).get("rotation_speed", 0.01)
        self.rangoli_angle += rotation_speed * dt * 360  # degrees per second
        self.rangoli_angle %= 360
        
        # Get psychedelic configuration
        rangoli_config = self.config.get("rangoli", {})
        psychedelic_config = rangoli_config.get("psychedelic", {})
        
        # Update color cycling for psychedelic effect
        cycle_speed = psychedelic_config.get("color_cycle_speed", 0.03)
        self.color_cycle_hue += cycle_speed * dt
        if self.color_cycle_hue >= 1.0:
            self.color_cycle_hue -= 1.0
            
        # Check if it's time to generate new mandalas
        now = time.time()
        if now - self.last_mandala_generation > self.mandala_refresh_rate:
            self._generate_bezier_mandalas()
            self.last_mandala_generation = now
        
        # Update ethereal outline effects if we have a camera frame
        if current_frame is not None and "ethereal_outlines" in self.config:
            ethereal_config = self.config.get("ethereal_outlines", {})
            
            if ethereal_config.get("enabled", True):
                # Detect person outlines
                self.ethereal_mask, self.has_person = self.person_outline_detector.detect(current_frame)
                
                # Add particle effects to the outlines if enabled
                if ethereal_config.get("particle_effects", True):
                    self.ethereal_mask = self.person_outline_detector.add_particle_effects(self.ethereal_mask)
                
                # Handle color cycling if enabled
                if ethereal_config.get("color_cycling", True):
                    now = time.time()
                    cycle_speed = ethereal_config.get("color_cycle_speed", 0.05)
                    
                    if now - self.ethereal_last_color_change > cycle_speed:
                        outline_colors = ethereal_config.get("outline_colors", [[140, 220, 255]])
                        self.ethereal_color_index = (self.ethereal_color_index + 1) % len(outline_colors)
                        self.person_outline_detector.config["outline_color"] = outline_colors[self.ethereal_color_index]
                        self.ethereal_last_color_change = now
        
        # Update firework particles
        expired_origins = []
        
        # Enforce a maximum lifetime for fireworks displays (in seconds)
        max_firework_lifetime = 3.0
        current_time = time.time()
        
        # Track firework start times if not already being tracked
        if not hasattr(self, 'firework_start_times'):
            self.firework_start_times = {}
            
        for origin, particles in self.firework_particles.items():
            # Track when this firework started
            if origin not in self.firework_start_times:
                self.firework_start_times[origin] = current_time
                
            # Check if this firework has been active too long
            if current_time - self.firework_start_times.get(origin, 0) > max_firework_lifetime:
                expired_origins.append(origin)
                continue
                
            active_particles = []
            
            for p in particles:
                # Update particle position
                p["x"] += p["dx"]
                p["y"] += p["dy"]
                
                # Add gravity (slightly increased)
                p["dy"] += 0.15
                
                # Age the particle (faster aging)
                p["age"] += dt * 1.2
                
                # Keep particle if still alive
                if p["age"] < p["lifetime"]:
                    active_particles.append(p)
            
            # Update or remove particle list
            if active_particles:
                self.firework_particles[origin] = active_particles
            else:
                expired_origins.append(origin)
        
        # Remove expired fireworks
        for origin in expired_origins:
            self.firework_particles.pop(origin, None)
            if origin in self.firework_start_times:
                self.firework_start_times.pop(origin)
                
        # Limit total number of active fireworks
        max_active_fireworks = 2
        if len(self.firework_particles) > max_active_fireworks:
            # Remove oldest fireworks until we're within limit
            fireworks_to_remove = sorted(
                self.firework_start_times.items(), 
                key=lambda x: x[1]
            )[:len(self.firework_particles) - max_active_fireworks]
            
            for origin, _ in fireworks_to_remove:
                if origin in self.firework_particles:
                    self.firework_particles.pop(origin)
                if origin in self.firework_start_times:
                    self.firework_start_times.pop(origin)
            
        # Update floating diyas
        if self.config.get("diya", {}).get("floating", {}).get("enabled", True):
            # Spawn new floating diyas if needed
            now = time.time()
            spawn_rate = self.config.get("diya", {}).get("floating", {}).get("spawn_rate", 5.0)
            max_count = self.config.get("diya", {}).get("floating", {}).get("max_count", 5)
            
            if now - self.last_diya_spawn_time > spawn_rate and len(self.floating_diyas) < max_count and self.diya_images:
                # Choose a random diya image
                diya_img = random.choice(self.diya_images)
                speed_factor = self.config.get("diya", {}).get("floating", {}).get("speed_factor", 0.5)
                size_factor = self.config.get("diya", {}).get("scale_factor", 0.5)
                
                # Create a new floating diya
                self.floating_diyas.append(FloatingObject(
                    diya_img, 
                    self.screen_size, 
                    speed_factor=speed_factor,
                    rotation_speed=random.uniform(-0.5, 0.5),
                    size_factor=size_factor
                ))
                self.last_diya_spawn_time = now
                
            # Update existing floating diyas
            new_diyas = []
            for diya in self.floating_diyas:
                if not diya.update(dt):  # Returns True if off-screen
                    new_diyas.append(diya)
            self.floating_diyas = new_diyas
            
        # Update floating rangolis
        if self.config.get("rangoli", {}).get("floating", {}).get("enabled", True):
            # Spawn new floating rangolis if needed
            now = time.time()
            spawn_rate = self.config.get("rangoli", {}).get("floating", {}).get("spawn_rate", 8.0)
            max_count = self.config.get("rangoli", {}).get("floating", {}).get("max_count", 3)
            
            patterns = self.mandala_surfaces if self.mandala_surfaces else self.rangoli_patterns
            if now - self.last_rangoli_spawn_time > spawn_rate and len(self.floating_rangolis) < max_count and patterns:
                # Choose a random rangoli pattern
                rangoli_img = random.choice(patterns)
                speed_factor = self.config.get("rangoli", {}).get("floating", {}).get("speed_factor", 0.3)
                
                # Create a new floating rangoli
                self.floating_rangolis.append(FloatingObject(
                    rangoli_img, 
                    self.screen_size, 
                    speed_factor=speed_factor,
                    rotation_speed=random.uniform(-0.3, 0.3),
                    size_factor=random.uniform(0.15, 0.25)  # Smaller size for rangolis as they can be large
                ))
                self.last_rangoli_spawn_time = now
                
            # Update existing floating rangolis
            new_rangolis = []
            for rangoli in self.floating_rangolis:
                if not rangoli.update(dt):  # Returns True if off-screen
                    new_rangolis.append(rangoli)
            self.floating_rangolis = new_rangolis
        
        # Increment frame counter
        self.current_frame += 1
    
    def render(self, state, state_data, surface):
        """
        Render visual effects based on current state.
        
        Args:
            state: Current VisualState enum
            state_data: Dictionary of state-specific data
            surface: pygame.Surface to render onto
            
        Returns:
            Modified surface with rendered visuals
        """
        # Create a copy of the input surface for rendering
        result = surface.copy()
        
        # Update screen size for floating objects
        self.screen_size = result.get_size()
        
        # Render background image if available
        self._render_background(result)
        
        # Always render the psychedelic rangoli pattern in the background
        # Use semi-transparent effect so it doesn't overpower other elements
        width, height = result.get_size()
        self._render_rangoli(result, {"rangoli_center": (width // 2, height // 2)}, alpha=180)
        
        # Process different visual states
        if state == VisualState.IDLE:
            # In idle state, we might want to make the rangoli more prominent
            self._render_rangoli(result, state_data, alpha=220)
        elif state == VisualState.DIYA:
            self._render_diyas(result, state_data)
        elif state == VisualState.FIREWORKS:
            # Track the last time fireworks were created
            if not hasattr(self, 'last_firework_time'):
                self.last_firework_time = 0
                
            # Don't create fireworks too frequently (at most once every 2 seconds)
            current_time = time.time()
            if current_time - self.last_firework_time > 2.0:
                # Limit the number of firework origins to process at once
                if 'firework_origins' in state_data and state_data['firework_origins']:
                    # Only keep the latest origin point
                    state_data['firework_origins'] = [state_data['firework_origins'][-1]]
                    self.last_firework_time = current_time
                    
            self._render_fireworks(result, state_data)
        elif state == VisualState.RANGOLI:
            # For rangoli state, render at full opacity on top
            self._render_rangoli(result, state_data, alpha=255)
        elif state == VisualState.AURA:
            self._render_aura(result, state_data)
        
        # Render ethereal outlines (people detection) if enabled and available
        self._render_ethereal_outlines(result, state_data)
        
        # Render floating diyas
        for diya in self.floating_diyas:
            diya.draw(result)
            
        # Render floating rangolis
        for rangoli in self.floating_rangolis:
            rangoli.draw(result)
        
        return result
        
    def _render_background(self, surface):
        """Render the background image behind all other content."""
        if self.background_image and self.config.get("background", {}).get("enabled", True):
            # Scale the background image to fit the surface
            surface_width, surface_height = surface.get_size()
            scaled_bg = pygame.transform.scale(self.background_image, (surface_width, surface_height))
            
            # Apply opacity if configured
            opacity = self.config.get("background", {}).get("opacity", 1.0)
            if opacity < 1.0:
                # Create a copy with per-surface alpha
                scaled_bg = scaled_bg.convert_alpha()
                scaled_bg.set_alpha(int(255 * opacity))
            
            # Draw the background
            surface.blit(scaled_bg, (0, 0))
    

    def _render_diyas(self, surface, state_data):
        """Render diya effect at specified positions."""
        if not self.diya_images:
            return
        
        diya_positions = state_data.get("diya_positions", [])
        if not diya_positions:
            return
            
        # Get a random diya image
        diya_img = random.choice(self.diya_images)
        
        # Calculate size based on config
        scale = self.config["diya"]["scale_factor"]
        width = int(diya_img.get_width() * scale)
        height = int(diya_img.get_height() * scale)
        scaled_diya = pygame.transform.scale(diya_img, (width, height))
        
        # Draw diyas at each position
        for pos in diya_positions:
            # Center the diya at the position
            x = pos[0] - width // 2
            y = pos[1] - height // 2
            
            # Apply flickering effect
            flicker = random.uniform(0.8, 1.0)
            if flicker > 0.95:  # Occasional brighter flicker
                flicker = 1.2
                
            # Apply the flickering as a brightness adjustment
            flickered_diya = self._adjust_brightness(scaled_diya, flicker)
            
            # Draw the diya
            surface.blit(flickered_diya, (x, y))
    
    def _render_fireworks(self, surface, state_data):
        """Render firework particle effects."""
        # Check for new firework origins
        firework_origins = state_data.get("firework_origins", [])
        
        # Limit the number of simultaneous fireworks
        max_fireworks = 2  # Keep only 2 simultaneous fireworks
        if len(self.firework_particles) >= max_fireworks and firework_origins:
            # Keep only the newest firework origins
            firework_origins = firework_origins[-1:]
        
        # Create new fireworks for any new origins
        for origin in firework_origins:
            if origin and origin not in self.firework_particles:
                # Reduce particle count
                count = min(50, self.config["fireworks"].get("particle_count", 100))
                self.firework_particles[origin] = self._create_firework_particles(origin, count)
        
        # Draw all active firework particles - use softer rendering
        for particles in self.firework_particles.values():
            for p in particles:
                # Calculate fade based on age
                fade = 1.0 - (p["age"] / p["lifetime"])
                
                # Calculate color with fade - reduce brightness
                color = tuple(int(c * fade * 0.7) for c in p["color"])
                
                # Draw particle
                pygame.draw.circle(
                    surface, 
                    color, 
                    (int(p["x"]), int(p["y"])), 
                    p["size"]
                )
    
    def _render_rangoli(self, surface, state_data, alpha=200):
        """Render psychedelic rotating rangoli pattern."""
        # Ensure we have patterns to render
        patterns = self.mandala_surfaces if self.mandala_surfaces else self.rangoli_patterns
        
        # If no patterns are available yet, try to generate them
        if not patterns:
            self._generate_bezier_mandalas()
            patterns = self.mandala_surfaces if self.mandala_surfaces else self.rangoli_patterns
        
        if not patterns:
            return
            
        # Get the center position for the rangoli
        center = state_data.get("rangoli_center")
        
        # If no center specified, use the center of the surface
        if not center:
            width, height = surface.get_size()
            center = (width // 2, height // 2)
        
        # Use frame count to cycle through patterns
        pattern_index = (self.current_frame // 180) % len(patterns)
        rangoli = patterns[pattern_index]
        
        # Create a copy for color modifications - ensure we maintain the alpha channel
        rangoli_copy = rangoli.copy().convert_alpha()
        
        # Apply psychedelic color cycling effect if using Bezier mandalas
        if self.mandala_surfaces:
            # Create a color overlay for psychedelic effect - with alpha channel
            overlay = pygame.Surface(rangoli.get_size(), pygame.SRCALPHA)
            
            # Get a psychedelic color based on the current cycle
            r, g, b = colorsys.hsv_to_rgb(self.color_cycle_hue, 1.0, 1.0)
            # Use a lower alpha for the overlay to avoid washing out the pattern
            overlay_color = (int(r*255), int(g*255), int(b*255), 80)
            
            # Only fill non-transparent pixels with the overlay color
            # This preserves the transparency of the original pattern
            temp_surf = rangoli.copy().convert_alpha()
            temp_surf.fill(overlay_color, special_flags=pygame.BLEND_RGBA_MULT)
            
            # Apply the overlay to our copy, preserving transparency
            rangoli_copy.blit(temp_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        # Get psychedelic configuration
        rangoli_config = self.config.get("rangoli", {})
        psychedelic_config = rangoli_config.get("psychedelic", {})
        
        # Check if zoom effect is enabled
        zoom_effect = psychedelic_config.get("zoom_effect", True)
        
        # Apply a pulsating zoom effect if enabled
        if zoom_effect:
            zoom_factor = 1.0 + 0.1 * math.sin(time.time() * 2)
            scaled_size = (int(rangoli_copy.get_width() * zoom_factor), 
                          int(rangoli_copy.get_height() * zoom_factor))
            scaled_rangoli = pygame.transform.smoothscale(rangoli_copy, scaled_size)
        else:
            scaled_rangoli = rangoli_copy
        
        # Rotate the pattern - ensure we maintain alpha channel
        rotated = pygame.transform.rotate(scaled_rangoli, self.rangoli_angle)
        
        # Add a second rotated copy with different rotation for more complexity
        rotated2 = pygame.transform.rotate(scaled_rangoli, -self.rangoli_angle * 0.7)
        
        # Position the patterns centered on the specified point
        x1 = center[0] - rotated.get_width() // 2
        y1 = center[1] - rotated.get_height() // 2
        
        x2 = center[0] - rotated2.get_width() // 2
        y2 = center[1] - rotated2.get_height() // 2
        
        # Apply custom alpha for blending
        if alpha < 255:
            # Create temporary surfaces with the desired alpha
            temp1 = rotated.copy()
            temp2 = rotated2.copy()
            
            # Adjust alpha for each surface
            temp1.set_alpha(alpha)
            temp2.set_alpha(alpha // 2)  # Second layer more transparent
            
            rotated = temp1
            rotated2 = temp2
        
        # Get blend mode
        blend_mode = psychedelic_config.get("blend_mode", "add").lower()
        blend_flag = pygame.BLEND_RGBA_ADD  # default - using RGBA version for better transparency
        
        if blend_mode == "add":
            blend_flag = pygame.BLEND_RGBA_ADD
        elif blend_mode == "multiply":
            blend_flag = pygame.BLEND_RGBA_MULT
        elif blend_mode == "rgba_add":
            blend_flag = pygame.BLEND_RGBA_ADD
        
        # Draw the rangoli layers with proper alpha blending
        surface.blit(rotated2, (x2, y2), special_flags=blend_flag)
        surface.blit(rotated, (x1, y1), special_flags=blend_flag)
    
    def _render_aura(self, surface, state_data):
        """Render glowing aura effect around a position."""
        aura_position = state_data.get("aura_position")
        if not aura_position:
            return
            
        aura_radius = state_data.get("aura_radius", 100)
        color = self.config["aura"]["color"]
        opacity = self.config["aura"]["opacity"]
        blur_radius = self.config["aura"]["blur_radius"]
        
        # Create a temporary surface for the aura
        width, height = surface.get_size()
        aura_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw a radial gradient for the aura
        for r in range(aura_radius, 0, -1):
            alpha = int(255 * opacity * (r / aura_radius))
            pygame.draw.circle(
                aura_surface,
                (*color, alpha),
                aura_position,
                r
            )
        
        # Apply a simple blur effect by scaling down and up
        scale_factor = 0.5
        small_surface = pygame.transform.scale(
            aura_surface, 
            (int(width * scale_factor), int(height * scale_factor))
        )
        blurred_surface = pygame.transform.scale(
            small_surface,
            (width, height)
        )
        
        # Blend the aura with the main surface
        surface.blit(blurred_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    def _render_ethereal_outlines(self, surface, state_data):
        """Render ethereal outlines of people detected in the scene."""
        # Skip if not enabled or no mask available
        ethereal_config = self.config.get("ethereal_outlines", {})
        if not ethereal_config.get("enabled", True) or self.ethereal_mask is None:
            return
            
        # Convert the ethereal mask from OpenCV format (numpy) to pygame surface
        if self.has_person:
            # Create pygame surface from numpy array
            h, w = self.ethereal_mask.shape[:2]
            
            # Convert from BGR (OpenCV) to RGB (Pygame)
            ethereal_rgb = cv2.cvtColor(self.ethereal_mask, cv2.COLOR_BGR2RGB)
            
            # Set opacity if configured
            opacity = ethereal_config.get("opacity", 0.8)
            
            # Convert to pygame surface
            ethereal_surface = pygame.surfarray.make_surface(ethereal_rgb.swapaxes(0, 1))
            
            # Apply opacity
            ethereal_surface.set_alpha(int(opacity * 255))
            
            # Scale the ethereal surface to match the display surface if needed
            surface_width, surface_height = surface.get_size()
            if w != surface_width or h != surface_height:
                ethereal_surface = pygame.transform.scale(ethereal_surface, (surface_width, surface_height))
                
            # Blend the ethereal outlines with the scene using additive blending for glow effect
            surface.blit(ethereal_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def _adjust_brightness(self, surface, factor):
        """Adjust the brightness of a surface by a factor."""
        # Create a copy of the surface to work with
        temp = surface.copy()
        # Convert to float first to prevent type issues
        temp_array = pygame.surfarray.pixels3d(temp).astype(float)
        # Apply brightness factor
        temp_array = np.clip(temp_array * factor, 0, 255).astype(np.uint8)
        # Update the surface with new values
        pygame.surfarray.blit_array(temp, temp_array)
        return temp
    
    def create_firework_at(self, position):
        """Create a firework explosion at the specified position."""
        # Prevent creating too many fireworks
        if len(self.firework_particles) >= 2:
            # Remove the oldest firework if we have too many
            if hasattr(self, 'firework_start_times') and self.firework_start_times:
                oldest_origin = min(self.firework_start_times.items(), key=lambda x: x[1])[0]
                if oldest_origin in self.firework_particles:
                    self.firework_particles.pop(oldest_origin)
                if oldest_origin in self.firework_start_times:
                    self.firework_start_times.pop(oldest_origin)
        
        # Create a reduced firework
        count = min(50, self.config["fireworks"].get("particle_count", 100))
        self.firework_particles[position] = self._create_firework_particles(position, count)
        
        # Track the start time
        if not hasattr(self, 'firework_start_times'):
            self.firework_start_times = {}
        self.firework_start_times[position] = time.time()
    
    def add_diya_at(self, position):
        """Add a diya at the specified position for future rendering."""
        if position not in self.firework_particles:
            self.diya_positions.append(position)


# For testing
if __name__ == "__main__":
    import time
    from scene_manager import SceneStateManager
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    # Initialize pygame
    width, height = 800, 600
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Visual Generator Test")
    
    # Create components
    visual_generator = VisualGenerator(config_path)
    scene_manager = SceneStateManager(config_path)
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    # Initial state data
    state_data = {
        "diya_positions": [(200, 300), (600, 300)],
        "rangoli_center": (width // 2, height // 2)
    }
    
    current_state = VisualState.IDLE
    last_state_change = time.time()
    
    while running:
        # Calculate delta time
        dt = clock.tick(60) / 1000.0  # seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    current_state = VisualState.IDLE
                    last_state_change = time.time()
                elif event.key == pygame.K_2:
                    current_state = VisualState.DIYA
                    last_state_change = time.time()
                elif event.key == pygame.K_3:
                    current_state = VisualState.FIREWORKS
                    state_data["firework_origins"] = [(width//2, height//2)]
                    last_state_change = time.time()
                elif event.key == pygame.K_4:
                    current_state = VisualState.RANGOLI
                    last_state_change = time.time()
                elif event.key == pygame.K_5:
                    current_state = VisualState.AURA
                    last_state_change = time.time()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Add firework or diya at mouse position
                pos = pygame.mouse.get_pos()
                if current_state == VisualState.FIREWORKS:
                    state_data["firework_origins"] = [pos]
                elif current_state == VisualState.DIYA:
                    state_data["diya_positions"].append(pos)
                elif current_state == VisualState.AURA:
                    state_data["aura_position"] = pos
        
        # Update mouse position for aura
        if current_state == VisualState.AURA:
            state_data["aura_position"] = pygame.mouse.get_pos()
            state_data["aura_radius"] = 100 + 50 * math.sin(time.time() * 2)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Update visual animations
        visual_generator.update(dt)
        
        # Render visuals
        screen = visual_generator.render(current_state, state_data, screen)
        
        # Display state information
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"State: {current_state.name} (Press 1-5 to change)", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        help_text = font.render("Click to add effects at cursor position", True, (255, 255, 255))
        screen.blit(help_text, (10, 40))
        
        # Update display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()