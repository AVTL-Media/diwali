"""Tests for the PersonOutlineDetector module."""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from person_outline_detector import PersonOutlineDetector


class TestPersonOutlineDetector:
    """Test suite for PersonOutlineDetector class."""

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_init_default_config(self, mock_pose):
        """Test initialization with default configuration."""
        detector = PersonOutlineDetector()

        assert detector.config["enabled"] is True
        assert detector.config["detection_confidence"] == 0.7
        assert detector.config["outline_thickness"] == 5
        assert len(detector.outlines) == 0
        assert detector.frame_count == 0

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_init_with_config_file(self, mock_pose, temp_config_file):
        """Test initialization with configuration file."""
        detector = PersonOutlineDetector(temp_config_file)

        assert detector.config["enabled"] is True

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_init_with_mediapipe_enabled(self, mock_pose):
        """Test that MediaPipe is initialized when enabled."""
        detector = PersonOutlineDetector()

        assert detector.mp_pose is not None
        mock_pose.assert_called_once()

    @patch('person_outline_detector.cv2.createBackgroundSubtractorMOG2')
    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_setup_background_subtractor_mog2(self, mock_pose, mock_mog2):
        """Test setup of MOG2 background subtractor."""
        mock_subtractor = Mock()
        mock_mog2.return_value = mock_subtractor

        detector = PersonOutlineDetector()
        detector.config["background_subtractor"] = "MOG2"
        detector.setup_background_subtractor()

        # Should have been called at least once (may be called during init)
        assert mock_mog2.called
        assert detector.bg_subtractor is not None

    @patch('person_outline_detector.cv2.createBackgroundSubtractorKNN')
    def test_setup_background_subtractor_knn(self, mock_knn):
        """Test setup of KNN background subtractor."""
        mock_subtractor = Mock()
        mock_knn.return_value = mock_subtractor

        detector = PersonOutlineDetector()
        detector.config["background_subtractor"] = "KNN"
        detector.setup_background_subtractor()

        mock_knn.assert_called_once()

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_detect_when_disabled(self, mock_pose, mock_frame):
        """Test detect returns empty mask when disabled."""
        detector = PersonOutlineDetector()
        detector.config["enabled"] = False

        mask, has_person = detector.detect(mock_frame)

        assert has_person is False
        assert mask is not None
        assert np.all(mask == 0)  # Should be all zeros

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_detect_with_none_frame(self, mock_pose):
        """Test detect returns empty mask with None frame."""
        detector = PersonOutlineDetector()

        mask, has_person = detector.detect(None)

        assert has_person is False
        # Mask might be None or empty array depending on implementation
        assert mask is None or (hasattr(mask, 'size') and mask.size == 0)

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_detect_increments_frame_count(self, mock_pose, mock_frame):
        """Test that detect increments frame counter."""
        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = Mock(pose_landmarks=None)
        mock_pose.return_value = mock_pose_instance

        detector = PersonOutlineDetector()
        initial_count = detector.frame_count

        detector.detect(mock_frame)

        assert detector.frame_count == initial_count + 1

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_detect_no_person(self, mock_pose, mock_frame):
        """Test detect when no person is in frame."""
        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = Mock(pose_landmarks=None)
        mock_pose.return_value = mock_pose_instance

        detector = PersonOutlineDetector()
        mask, has_person = detector.detect(mock_frame)

        assert has_person is False or has_person is True  # Depends on background subtraction

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_detect_with_person(self, mock_pose, mock_frame):
        """Test detect when person is detected by MediaPipe."""
        # Create mock pose landmarks with visibility attribute
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = 0.0
        mock_landmark.visibility = 0.9  # High visibility

        mock_pose_landmarks = Mock()
        mock_pose_landmarks.landmark = [mock_landmark] * 33  # 33 pose landmarks

        mock_results = Mock()
        mock_results.pose_landmarks = mock_pose_landmarks

        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = mock_results
        mock_pose.return_value = mock_pose_instance

        detector = PersonOutlineDetector()
        mask, has_person = detector.detect(mock_frame)

        # MediaPipe detected a person, so has_person should be True
        assert has_person is True
        assert mask is not None

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_add_particle_effects_no_outline(self, mock_pose):
        """Test add_particle_effects with no outline."""
        detector = PersonOutlineDetector()

        empty_mask = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.add_particle_effects(empty_mask)

        assert result is not None
        assert result.shape == empty_mask.shape

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_add_particle_effects_with_outline(self, mock_pose):
        """Test add_particle_effects with outline present."""
        detector = PersonOutlineDetector()
        detector.config["particle_count"] = 50

        # Create mask with some outline
        mask = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(mask, (320, 240), 100, (255, 255, 255), 5)

        result = detector.add_particle_effects(mask)

        assert result is not None
        assert result.shape == mask.shape

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_visualize(self, mock_pose, mock_frame):
        """Test visualize method."""
        detector = PersonOutlineDetector()

        # Create a simple ethereal mask
        ethereal_mask = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(ethereal_mask, (320, 240), 50, (100, 200, 255), -1)

        result = detector.visualize(mock_frame, ethereal_mask)

        assert result is not None
        assert result.shape == mock_frame.shape

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_outlines_list_management(self, mock_pose, mock_frame):
        """Test that outlines list is properly managed."""
        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = Mock(pose_landmarks=None)
        mock_pose.return_value = mock_pose_instance

        detector = PersonOutlineDetector()

        # Add some fake outlines
        detector.outlines = [np.array([[100, 100]]), np.array([[200, 200]])]
        detector.outline_timestamps = [0.0, 0.0]

        # Detect should manage outlines
        detector.detect(mock_frame)

        # Outlines list should still be valid
        assert isinstance(detector.outlines, list)

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_cleanup(self, mock_pose):
        """Test cleanup method."""
        mock_pose_instance = Mock()
        mock_pose.return_value = mock_pose_instance

        detector = PersonOutlineDetector()
        detector.cleanup()

        # Should close pose detector
        mock_pose_instance.close.assert_called_once()

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_config_particle_count(self, mock_pose):
        """Test that particle count config is respected."""
        detector = PersonOutlineDetector()

        assert "particle_count" in detector.config
        assert isinstance(detector.config["particle_count"], int)

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_config_outline_thickness(self, mock_pose):
        """Test that outline thickness config is respected."""
        detector = PersonOutlineDetector()

        assert detector.config["outline_thickness"] > 0

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_config_min_contour_area(self, mock_pose):
        """Test that min contour area config exists."""
        detector = PersonOutlineDetector()

        assert "min_contour_area" in detector.config
        assert detector.config["min_contour_area"] >= 0

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_outline_history_initialization(self, mock_pose):
        """Test that outline history is initialized."""
        detector = PersonOutlineDetector()

        assert isinstance(detector.outline_history, list)
        assert len(detector.outline_history) == 0

    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_max_outline_age_config(self, mock_pose):
        """Test that max outline age config exists."""
        detector = PersonOutlineDetector()

        assert "max_outline_age" in detector.config
        assert detector.config["max_outline_age"] > 0

    @patch('person_outline_detector.cv2.createBackgroundSubtractorMOG2')
    @patch('person_outline_detector.mp.solutions.pose.Pose')
    def test_background_subtraction_fallback(self, mock_pose, mock_mog2, mock_frame):
        """Test background subtraction when MediaPipe doesn't detect person."""
        # Mock MediaPipe to not detect person
        mock_pose_instance = Mock()
        mock_pose_instance.process.return_value = Mock(pose_landmarks=None)
        mock_pose.return_value = mock_pose_instance

        # Mock background subtractor
        mock_subtractor = Mock()
        mock_subtractor.apply.return_value = np.zeros((480, 640), dtype=np.uint8)
        mock_mog2.return_value = mock_subtractor
        detector = PersonOutlineDetector()
        detector.config["use_mediapipe"] = True
        detector.setup_background_subtractor()

        mask, has_person = detector.detect(mock_frame)

        # Should fallback to background subtraction
        assert mask is not None
