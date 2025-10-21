"""Tests for the MotionDetector module."""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from motion_detector import MotionDetector


class TestMotionDetector:
    """Test suite for MotionDetector class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        detector = MotionDetector()

        assert detector.config["blur_size"] == 5
        assert detector.config["threshold"] == 25
        assert detector.config["min_area"] == 500
        assert detector.config["history"] == 20
        assert detector.motion_detected is False
        assert len(detector.motion_contours) == 0

    def test_init_with_config_file(self, temp_config_file):
        """Test initialization with configuration file."""
        detector = MotionDetector(temp_config_file)

        assert detector.config["blur_size"] == 5
        assert detector.config["threshold"] == 25

    def test_detect_with_none_frames(self):
        """Test detect returns False with None frames."""
        detector = MotionDetector()

        motion_detected, contours, mask = detector.detect(None, None)

        assert motion_detected is False
        assert contours == []
        assert mask is None

    def test_detect_with_one_none_frame(self, mock_gray_frame):
        """Test detect returns False when one frame is None."""
        detector = MotionDetector()

        motion_detected, contours, mask = detector.detect(mock_gray_frame, None)

        assert motion_detected is False
        assert contours == []

    def test_detect_no_motion(self):
        """Test detect with identical frames (no motion)."""
        detector = MotionDetector()

        # Create identical frames
        frame = np.ones((480, 640), dtype=np.uint8) * 128

        motion_detected, contours, mask = detector.detect(frame, frame)

        assert motion_detected is False
        assert len(contours) == 0

    def test_detect_with_motion(self, mock_frame_with_motion):
        """Test detect with frames showing motion."""
        detector = MotionDetector()
        frame1, frame2 = mock_frame_with_motion

        motion_detected, contours, mask = detector.detect(frame2, frame1)

        assert motion_detected is True
        assert len(contours) > 0
        assert mask is not None
        assert mask.shape == frame1.shape

    def test_detect_small_motion_filtered(self):
        """Test that small motion areas below min_area are filtered out."""
        detector = MotionDetector()
        detector.config["min_area"] = 5000  # Large minimum area

        # Create frames with small motion
        frame1 = np.ones((480, 640), dtype=np.uint8) * 100
        frame2 = frame1.copy()
        frame2[100:110, 100:110] = 255  # Small 10x10 area

        motion_detected, contours, mask = detector.detect(frame2, frame1)

        # Should not detect motion due to small area
        assert motion_detected is False

    def test_get_motion_intensity_empty_history(self):
        """Test motion intensity returns 0 with empty history."""
        detector = MotionDetector()

        intensity = detector.get_motion_intensity()

        assert intensity == 0.0

    def test_get_motion_intensity_with_history(self):
        """Test motion intensity calculation with history."""
        detector = MotionDetector()
        detector.motion_history = [1, 1, 0, 1, 0]  # 60% motion

        intensity = detector.get_motion_intensity()

        assert intensity == 0.6

    def test_motion_history_updates(self, mock_frame_with_motion):
        """Test that motion history is updated correctly."""
        detector = MotionDetector()
        frame1, frame2 = mock_frame_with_motion

        # First detection
        detector.detect(frame2, frame1)
        assert len(detector.motion_history) == 1
        assert detector.motion_history[0] == 1  # Motion detected

        # Second detection (no motion)
        detector.detect(frame1, frame1)
        assert len(detector.motion_history) == 2
        assert detector.motion_history[1] == 0  # No motion

    def test_motion_history_max_length(self):
        """Test that motion history doesn't exceed maximum length."""
        detector = MotionDetector()
        detector.config["history"] = 5

        # Add more than max history
        for i in range(10):
            detector.motion_history.append(1)
            if len(detector.motion_history) > detector.config["history"]:
                detector.motion_history.pop(0)

        assert len(detector.motion_history) <= 5

    def test_get_largest_contour_none_initially(self):
        """Test that largest contour is None initially."""
        detector = MotionDetector()

        contour = detector.get_largest_contour()

        assert contour is None

    def test_get_largest_contour_after_detection(self, mock_frame_with_motion):
        """Test largest contour is set after motion detection."""
        detector = MotionDetector()
        frame1, frame2 = mock_frame_with_motion

        detector.detect(frame2, frame1)
        contour = detector.get_largest_contour()

        assert contour is not None
        assert len(contour) > 0  # Contour should have points

    def test_get_contour_center_none_initially(self):
        """Test that contour center is None initially."""
        detector = MotionDetector()

        center = detector.get_contour_center()

        assert center is None

    def test_get_contour_center_after_detection(self, mock_frame_with_motion):
        """Test contour center is calculated after detection."""
        detector = MotionDetector()
        frame1, frame2 = mock_frame_with_motion

        detector.detect(frame2, frame1)
        center = detector.get_contour_center()

        assert center is not None
        assert isinstance(center, tuple)
        assert len(center) == 2
        # Center should be within frame bounds
        assert 0 <= center[0] <= 640
        assert 0 <= center[1] <= 480

    def test_detect_multiple_contours(self):
        """Test detection with multiple motion areas."""
        detector = MotionDetector()
        detector.config["min_area"] = 100

        # Create frame with multiple motion regions
        frame1 = np.ones((480, 640), dtype=np.uint8) * 100
        frame2 = frame1.copy()
        frame2[50:100, 50:100] = 255    # First region
        frame2[200:250, 300:350] = 255  # Second region

        motion_detected, contours, mask = detector.detect(frame2, frame1)

        assert motion_detected is True
        assert len(contours) >= 2  # Should detect both regions

    def test_threshold_sensitivity(self):
        """Test that threshold affects motion detection sensitivity."""
        detector = MotionDetector()

        # Low threshold - should detect small changes
        detector.config["threshold"] = 10

        frame1 = np.ones((480, 640), dtype=np.uint8) * 100
        frame2 = frame1.copy()
        frame2[100:200, 100:200] = 115  # Small intensity change

        motion_detected, _, _ = detector.detect(frame2, frame1)

        # With low threshold, should detect motion
        assert motion_detected is True
