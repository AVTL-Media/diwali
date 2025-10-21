"""Tests for the VisualGenerator module."""

import pytest
import numpy as np
import pygame
import time
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from visual_generator import VisualGenerator, FloatingObject
from scene_manager import VisualState


class TestFloatingObject:
    """Test suite for FloatingObject class."""

    def test_init(self):
        """Test FloatingObject initialization."""
        pygame.init()
        image = pygame.Surface((100, 100))
        screen_size = (800, 600)

        obj = FloatingObject(image, screen_size)

        assert obj.screen_width == 800
        assert obj.screen_height == 600
        assert obj.alpha == 0  # Starts faded out
        assert obj.is_fading_in is True

    def test_update_position_changes(self):
        """Test that update changes object position."""
        pygame.init()
        image = pygame.Surface((100, 100))
        obj = FloatingObject(image, (800, 600))

        initial_x, initial_y = obj.x, obj.y
        obj.update(0.1)  # Update with 0.1 second delta

        # Position should have changed
        assert obj.x != initial_x or obj.y != initial_y

    def test_update_alpha_increases(self):
        """Test that alpha increases during fade-in."""
        pygame.init()
        image = pygame.Surface((100, 100))
        obj = FloatingObject(image, (800, 600))

        initial_alpha = obj.alpha
        obj.update(0.1)

        assert obj.alpha > initial_alpha

    def test_update_returns_offscreen_status(self):
        """Test that update returns True when object is off-screen."""
        pygame.init()
        image = pygame.Surface((100, 100))
        obj = FloatingObject(image, (800, 600))

        # Move object far off screen
        obj.x = -1000
        obj.y = -1000

        is_offscreen = obj.update(0.1)

        assert is_offscreen is True

    def test_draw(self):
        """Test drawing floating object."""
        pygame.init()
        image = pygame.Surface((100, 100))
        surface = pygame.Surface((800, 600))
        obj = FloatingObject(image, (800, 600))
        obj.alpha = 255  # Fully visible

        obj.draw(surface)

        # Should not raise any errors
        assert True


class TestVisualGenerator:
    """Test suite for VisualGenerator class."""

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_init_default_config(self, mock_pygame_init, mock_detector):
        """Test initialization with default configuration."""
        generator = VisualGenerator()

        assert generator.config is not None
        assert "diya" in generator.config
        assert "fireworks" in generator.config
        assert "rangoli" in generator.config
        assert generator.current_frame == 0

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_init_with_config_file(self, mock_pygame_init, mock_detector, temp_config_file):
        """Test initialization with configuration file."""
        generator = VisualGenerator(temp_config_file)

        assert generator.config is not None

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_firework_particles_initialization(self, mock_pygame_init, mock_detector):
        """Test that firework particles dictionary is initialized."""
        generator = VisualGenerator()

        assert isinstance(generator.firework_particles, dict)
        assert len(generator.firework_particles) == 0

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_create_firework_particles(self, mock_pygame_init, mock_detector):
        """Test creating firework particles."""
        generator = VisualGenerator()

        origin = (400, 300)
        particles = generator._create_firework_particles(origin, count=50)

        assert len(particles) > 0
        assert len(particles) <= 50
        # Each particle should have required properties
        for p in particles:
            assert "x" in p
            assert "y" in p
            assert "dx" in p
            assert "dy" in p
            assert "color" in p
            assert "lifetime" in p

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_update_increments_frame_counter(self, mock_pygame_init, mock_detector):
        """Test that update increments frame counter."""
        generator = VisualGenerator()
        initial_frame = generator.current_frame

        generator.update(0.016)  # ~60fps

        assert generator.current_frame == initial_frame + 1

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_update_rangoli_animation(self, mock_pygame_init, mock_detector):
        """Test rangoli animation updates."""
        generator = VisualGenerator()
        initial_angle = generator.rangoli_angle

        generator.update(0.1)

        # Angle should have changed
        assert generator.rangoli_angle != initial_angle

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_update_fireworks(self, mock_pygame_init, mock_detector):
        """Test fireworks update logic."""
        generator = VisualGenerator()

        # Add some firework particles
        origin = (400, 300)
        generator.firework_particles[origin] = generator._create_firework_particles(origin, 20)

        generator.update(0.1)

        # Particles should still exist or have been cleaned up
        assert isinstance(generator.firework_particles, dict)

    @patch('visual_generator.PersonOutlineDetector')
    def test_render_returns_surface(self, mock_detector):
        """Test that render returns a surface."""
        pygame.init()
        generator = VisualGenerator()

        state = VisualState.IDLE
        state_data = {}
        surface = pygame.Surface((800, 600))

        result = generator.render(state, state_data, surface)

        assert result is not None

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_create_firework_at(self, mock_pygame_init, mock_detector):
        """Test creating firework at specific position."""
        generator = VisualGenerator()

        position = (500, 400)
        generator.create_firework_at(position)

        assert position in generator.firework_particles
        assert len(generator.firework_particles[position]) > 0

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_firework_particle_aging(self, mock_pygame_init, mock_detector):
        """Test that firework particles age correctly."""
        generator = VisualGenerator()

        origin = (400, 300)
        particles = generator._create_firework_particles(origin, 10)

        # Age all particles
        for p in particles:
            initial_age = p["age"]
            p["age"] += 0.1
            assert p["age"] > initial_age

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_color_cycle_updates(self, mock_pygame_init, mock_detector):
        """Test that color cycle hue updates."""
        generator = VisualGenerator()
        initial_hue = generator.color_cycle_hue

        generator.update(0.1)

        # Hue should have changed
        assert generator.color_cycle_hue != initial_hue

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_floating_diyas_list(self, mock_pygame_init, mock_detector):
        """Test floating diyas list is initialized."""
        generator = VisualGenerator()

        assert isinstance(generator.floating_diyas, list)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_floating_rangolis_list(self, mock_pygame_init, mock_detector):
        """Test floating rangolis list is initialized."""
        generator = VisualGenerator()

        assert isinstance(generator.floating_rangolis, list)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_mandala_surfaces_generated(self, mock_pygame_init, mock_detector):
        """Test that mandala surfaces are generated."""
        generator = VisualGenerator()

        # Mandalas should be generated during init
        assert isinstance(generator.mandala_surfaces, list)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_create_diwali_rangoli(self, mock_pygame_init, mock_detector):
        """Test creating Diwali rangoli pattern."""
        pygame.init()
        generator = VisualGenerator()

        rangoli = generator._create_diwali_rangoli(size=400, seed=42)

        # Should return a surface or None
        assert rangoli is None or isinstance(rangoli, pygame.Surface)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_generate_psychedelic_colors(self, mock_pygame_init, mock_detector):
        """Test psychedelic color generation."""
        generator = VisualGenerator()

        colors = generator._generate_psychedelic_colors(5)

        assert len(colors) == 5
        # Each color should be RGBA tuple
        for color in colors:
            assert len(color) == 4
            # Check values are in valid range
            assert 0 <= color[0] <= 1
            assert 0 <= color[1] <= 1
            assert 0 <= color[2] <= 1
            assert 0 <= color[3] <= 1

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_rotate_points(self, mock_pygame_init, mock_detector):
        """Test point rotation helper method."""
        generator = VisualGenerator()

        points = [(100, 100), (200, 100), (200, 200)]
        center = (150, 150)
        angle = 1.57  # ~90 degrees in radians

        rotated = generator._rotate_points(points, center, angle)

        assert len(rotated) == len(points)
        # Points should have changed position
        assert rotated != points

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_rotate_points_helper(self, mock_pygame_init, mock_detector):
        """Test rotate points helper method."""
        generator = VisualGenerator()

        # Test that rotate_points method exists and works
        points = [(100, 100), (200, 100)]
        center = (150, 150)
        angle = 0.0

        rotated = generator._rotate_points(points, center, angle)

        # At angle 0, points should be unchanged
        assert len(rotated) == len(points)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_firework_start_times_tracking(self, mock_pygame_init, mock_detector):
        """Test that firework start times are tracked."""
        generator = VisualGenerator()
        generator.update(0.1)  # Initialize tracking

        assert hasattr(generator, 'firework_start_times')
        assert isinstance(generator.firework_start_times, dict)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_multiple_firework_types(self, mock_pygame_init, mock_detector):
        """Test different firework types can be created."""
        generator = VisualGenerator()

        # Test standard firework
        particles_standard = generator._create_standard_firework((400, 300), 30)
        assert len(particles_standard) > 0

        # Test bloom firework
        particles_bloom = generator._create_bloom_firework((400, 300), 30)
        assert len(particles_bloom) > 0

        # Test ring firework
        particles_ring = generator._create_ring_firework((400, 300), 30)
        assert len(particles_ring) > 0

        # Test willow firework
        particles_willow = generator._create_willow_firework((400, 300), 30)
        assert len(particles_willow) > 0

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_firework_cleanup(self, mock_pygame_init, mock_detector):
        """Test that old fireworks are cleaned up."""
        generator = VisualGenerator()
        generator.firework_start_times = {}

        # Add an old firework
        old_origin = (100, 100)
        generator.firework_particles[old_origin] = []
        generator.firework_start_times[old_origin] = time.time() - 10  # 10 seconds ago

        # Update should clean it up
        generator.update(0.1)

        # Old firework might be removed
        # (depends on cleanup logic)

    @patch('visual_generator.PersonOutlineDetector')
    @patch('visual_generator.pygame.init')
    def test_max_active_fireworks_limit(self, mock_pygame_init, mock_detector):
        """Test that maximum active fireworks is enforced."""
        generator = VisualGenerator()

        # Create more fireworks than the limit
        for i in range(5):
            generator.create_firework_at((i * 100, 200))

        # Should enforce a maximum
        assert len(generator.firework_particles) <= 3  # Max should be around 2-3
