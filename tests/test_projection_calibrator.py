"""Tests for the ProjectionCalibrator module."""

import pytest
import numpy as np
import pygame
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from projection_calibrator import ProjectionCalibrator


class TestProjectionCalibrator:
    """Test suite for ProjectionCalibrator class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        calibrator = ProjectionCalibrator()

        assert calibrator.config["fullscreen"] is True
        assert calibrator.config["calibration_enabled"] is True
        assert len(calibrator.corners) == 4
        assert calibrator.active_corner == 0
        assert calibrator.is_calibrated is False

    def test_init_with_config_file(self, temp_config_file):
        """Test initialization with configuration file."""
        calibrator = ProjectionCalibrator(temp_config_file)

        assert len(calibrator.corners) == 4

    def test_initial_corners_normalized(self):
        """Test that initial corners are in normalized coordinates."""
        calibrator = ProjectionCalibrator()

        # Corners should be in 0-1 range initially
        for corner in calibrator.corners:
            assert 0.0 <= corner[0] <= 1.0
            assert 0.0 <= corner[1] <= 1.0

    def test_start_calibration_scales_corners(self):
        """Test that start_calibration scales corners to screen size."""
        calibrator = ProjectionCalibrator()
        screen_size = (1920, 1080)

        calibrator.start_calibration(screen_size)

        # Corners should now be in pixel coordinates
        for corner in calibrator.corners:
            assert 0 <= corner[0] <= 1920
            assert 0 <= corner[1] <= 1080

    def test_move_active_corner(self):
        """Test moving the active corner."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (1920, 1080)
        calibrator.start_calibration((1920, 1080))

        initial_pos = calibrator.corners[0].copy()
        result = calibrator.move_active_corner(10, 5)

        assert result is True
        assert calibrator.corners[0][0] == initial_pos[0] + 10
        assert calibrator.corners[0][1] == initial_pos[1] + 5

    def test_move_active_corner_negative_delta(self):
        """Test moving corner with negative delta."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (1920, 1080)
        calibrator.start_calibration((1920, 1080))

        initial_pos = calibrator.corners[0].copy()
        calibrator.move_active_corner(-10, -5)

        assert calibrator.corners[0][0] == initial_pos[0] - 10
        assert calibrator.corners[0][1] == initial_pos[1] - 5

    def test_set_active_corner_valid(self):
        """Test setting active corner with valid index."""
        calibrator = ProjectionCalibrator()

        result = calibrator.set_active_corner(2)

        assert result is True
        assert calibrator.active_corner == 2

    def test_set_active_corner_invalid(self):
        """Test setting active corner with invalid index."""
        calibrator = ProjectionCalibrator()

        result = calibrator.set_active_corner(5)

        assert result is False
        assert calibrator.active_corner != 5

    def test_set_active_corner_negative(self):
        """Test setting active corner with negative index."""
        calibrator = ProjectionCalibrator()

        result = calibrator.set_active_corner(-1)

        assert result is False

    def test_complete_calibration(self):
        """Test completing the calibration process."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (1920, 1080)
        calibrator.start_calibration((1920, 1080))

        result = calibrator.complete_calibration()

        assert result is True
        assert calibrator.is_calibrated is True
        assert calibrator.transform_matrix is not None

    def test_complete_calibration_saves_normalized_corners(self):
        """Test that complete_calibration normalizes and saves corners."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (1920, 1080)
        calibrator.start_calibration((1920, 1080))

        calibrator.complete_calibration()

        # Check that calibration_points are normalized
        for point in calibrator.config["calibration_points"]:
            assert 0.0 <= point[0] <= 1.0
            assert 0.0 <= point[1] <= 1.0

    @patch('projection_calibrator.pygame.Surface')
    def test_apply_transform_not_calibrated(self, mock_surface):
        """Test apply_transform returns original surface when not calibrated."""
        pygame.init()
        calibrator = ProjectionCalibrator()
        calibrator.is_calibrated = False

        surface = pygame.Surface((100, 100))
        result = calibrator.apply_transform(surface)

        assert result == surface

    @patch('projection_calibrator.cv2.warpPerspective')
    @patch('projection_calibrator.pygame.surfarray.array3d')
    @patch('projection_calibrator.pygame.surfarray.make_surface')
    def test_apply_transform_calibrated(self, mock_make_surface, mock_array3d, mock_warp):
        """Test apply_transform applies perspective transformation."""
        pygame.init()
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (640, 480)
        calibrator.start_calibration((640, 480))
        calibrator.complete_calibration()

        surface = pygame.Surface((640, 480))
        mock_array3d.return_value = np.zeros((640, 480, 3))
        mock_warp.return_value = np.zeros((480, 640, 3))
        mock_make_surface.return_value = surface

        result = calibrator.apply_transform(surface)

        # Verify warpPerspective was called
        mock_warp.assert_called_once()

    def test_draw_calibration_ui(self):
        """Test drawing calibration UI elements."""
        pygame.init()
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (800, 600)
        calibrator.start_calibration((800, 600))

        # Create a real pygame surface
        surface = pygame.Surface((800, 600))

        result = calibrator.draw_calibration_ui(surface)

        assert result is not None

    def test_corners_count(self):
        """Test that exactly 4 corners are maintained."""
        calibrator = ProjectionCalibrator()

        assert len(calibrator.corners) == 4

    def test_transform_matrix_initially_none(self):
        """Test that transform matrix is None before calibration."""
        calibrator = ProjectionCalibrator()

        assert calibrator.transform_matrix is None

    def test_transform_matrix_after_calibration(self):
        """Test that transform matrix is created after calibration."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (1920, 1080)
        calibrator.start_calibration((1920, 1080))
        calibrator.complete_calibration()

        assert calibrator.transform_matrix is not None
        # Transform matrix should be 3x3
        assert calibrator.transform_matrix.shape == (3, 3)

    def test_screen_size_stored(self):
        """Test that screen size is stored during calibration."""
        calibrator = ProjectionCalibrator()
        screen_size = (1280, 720)

        calibrator.start_calibration(screen_size)

        assert calibrator.screen_size == screen_size

    def test_active_corner_starts_at_zero(self):
        """Test that active corner starts at index 0."""
        calibrator = ProjectionCalibrator()
        calibrator.start_calibration((800, 600))

        assert calibrator.active_corner == 0

    def test_move_multiple_corners(self):
        """Test moving different corners sequentially."""
        calibrator = ProjectionCalibrator()
        calibrator.screen_size = (800, 600)
        calibrator.start_calibration((800, 600))

        # Move corner 0
        calibrator.set_active_corner(0)
        pos0_before = calibrator.corners[0].copy()
        calibrator.move_active_corner(5, 5)
        pos0_after = calibrator.corners[0].copy()

        # Move corner 1
        calibrator.set_active_corner(1)
        pos1_before = calibrator.corners[1].copy()
        calibrator.move_active_corner(10, 10)
        pos1_after = calibrator.corners[1].copy()

        # Verify both moved
        assert not np.array_equal(pos0_before, pos0_after)
        assert not np.array_equal(pos1_before, pos1_after)
