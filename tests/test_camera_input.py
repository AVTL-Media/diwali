"""Tests for the CameraInput module."""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from camera_input import CameraInput


class TestCameraInput:
    """Test suite for CameraInput class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        camera = CameraInput()

        assert camera.config["device_id"] == 0
        assert camera.config["width"] == 640
        assert camera.config["height"] == 480
        assert camera.config["fps"] == 30
        assert camera.is_running is False
        assert camera.frame is None

    def test_init_with_config_file(self, temp_config_file):
        """Test initialization with configuration file."""
        camera = CameraInput(temp_config_file)

        assert camera.config["device_id"] == 0
        assert camera.config["width"] == 640
        assert camera.config["height"] == 480

    @patch('camera_input.cv2.VideoCapture')
    def test_start_success(self, mock_video_capture):
        """Test successful camera start."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        camera = CameraInput()
        result = camera.start()

        assert result is True
        assert camera.is_running is True
        mock_cap.set.assert_called()
        mock_video_capture.assert_called_once_with(0)

    @patch('camera_input.cv2.VideoCapture')
    def test_start_failure(self, mock_video_capture):
        """Test camera start failure when camera cannot be opened."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        camera = CameraInput()
        result = camera.start()

        assert result is False

    def test_stop_releases_camera(self):
        """Test that stop releases camera resources."""
        camera = CameraInput()
        camera.cap = Mock()
        camera.is_running = True

        camera.stop()

        camera.cap.release.assert_called_once()
        assert camera.is_running is False

    @patch('camera_input.cv2.VideoCapture')
    def test_read_when_not_running(self, mock_video_capture):
        """Test read returns None when camera is not running."""
        camera = CameraInput()
        camera.is_running = False

        frame = camera.read()

        assert frame is None

    @patch('camera_input.cv2.VideoCapture')
    def test_read_success(self, mock_video_capture, mock_frame):
        """Test successful frame reading."""
        mock_cap = Mock()
        mock_cap.read.return_value = (True, mock_frame.copy())
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        camera = CameraInput()
        camera.start()
        result_frame = camera.read()

        assert result_frame is not None
        assert result_frame.shape == (480, 640, 3)
        mock_cap.read.assert_called()

    @patch('camera_input.cv2.VideoCapture')
    def test_read_failure(self, mock_video_capture):
        """Test read when frame grab fails."""
        mock_cap = Mock()
        mock_cap.read.return_value = (False, None)
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        camera = CameraInput()
        camera.start()
        result_frame = camera.read()

        assert result_frame is None

    def test_get_frame_returns_current_frame(self, mock_frame):
        """Test get_frame returns the current frame."""
        camera = CameraInput()
        camera.frame = mock_frame

        result = camera.get_frame()

        assert np.array_equal(result, mock_frame)

    def test_get_gray_returns_grayscale(self, mock_gray_frame):
        """Test get_gray returns grayscale frame."""
        camera = CameraInput()
        camera.gray = mock_gray_frame

        result = camera.get_gray()

        assert np.array_equal(result, mock_gray_frame)
        assert len(result.shape) == 2  # Grayscale has 2 dimensions

    def test_get_prev_frame(self, mock_gray_frame):
        """Test get_prev_frame returns previous frame."""
        camera = CameraInput()
        camera.prev_frame = mock_gray_frame

        result = camera.get_prev_frame()

        assert np.array_equal(result, mock_gray_frame)

    def test_get_fps_initial(self):
        """Test FPS is 0 initially."""
        camera = CameraInput()

        fps = camera.get_fps()

        assert fps == 0

    @patch('camera_input.cv2.VideoCapture')
    @patch('camera_input.time.time')
    def test_fps_calculation(self, mock_time, mock_video_capture, mock_frame):
        """Test FPS calculation over multiple frames."""
        mock_cap = Mock()
        mock_cap.read.return_value = (True, mock_frame.copy())
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        # Simulate time progression
        time_values = [0.0, 0.5, 1.0, 1.5, 2.0]
        mock_time.side_effect = time_values * 10  # Repeat for multiple calls

        camera = CameraInput()
        camera.start()

        # Read multiple frames to trigger FPS calculation
        for _ in range(35):
            camera.read()

        # FPS should be calculated after 1 second
        assert camera.get_fps() > 0

    def test_get_resolution_with_frame(self, mock_frame):
        """Test get_resolution returns correct size when frame exists."""
        camera = CameraInput()
        camera.frame = mock_frame

        width, height = camera.get_resolution()

        assert width == 640
        assert height == 480

    def test_get_resolution_without_frame(self):
        """Test get_resolution returns config values when no frame exists."""
        camera = CameraInput()
        camera.frame = None

        width, height = camera.get_resolution()

        assert width == 640
        assert height == 480

    @patch('camera_input.cv2.VideoCapture')
    def test_frame_preprocessing(self, mock_video_capture, mock_frame):
        """Test that frames are properly preprocessed."""
        mock_cap = Mock()
        mock_cap.read.return_value = (True, mock_frame.copy())
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        camera = CameraInput()
        camera.start()
        camera.read()

        # Check that gray and blurred frames are created
        assert camera.gray is not None
        assert hasattr(camera, 'blurred')
        assert camera.blurred is not None
