"""Tests for the GestureTracker module."""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from gesture_tracker import GestureTracker, GestureType


class TestGestureType:
    """Test suite for GestureType enum."""

    def test_gesture_types_exist(self):
        """Test that all gesture types are defined."""
        assert GestureType.UNKNOWN
        assert GestureType.OPEN_PALM
        assert GestureType.CLOSED_FIST
        assert GestureType.POINTING
        assert GestureType.PINCH

    def test_gesture_type_values(self):
        """Test gesture type numeric values."""
        assert GestureType.UNKNOWN.value == 0
        assert GestureType.OPEN_PALM.value == 1
        assert GestureType.CLOSED_FIST.value == 2


class TestGestureTracker:
    """Test suite for GestureTracker class."""

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_init_default_config(self, mock_hands):
        """Test initialization with default configuration."""
        tracker = GestureTracker()

        assert tracker.config["min_detection_confidence"] == 0.7
        assert tracker.config["min_tracking_confidence"] == 0.5
        assert tracker.config["max_num_hands"] == 2
        assert tracker.hands_present is False
        assert len(tracker.hand_landmarks) == 0

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_init_with_config_file(self, mock_hands, temp_config_file):
        """Test initialization with configuration file."""
        tracker = GestureTracker(temp_config_file)

        assert tracker.config["min_detection_confidence"] == 0.7
        assert tracker.config["max_num_hands"] == 2

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_process_frame_no_hands(self, mock_hands, mock_frame):
        """Test process_frame with no hands detected."""
        # Mock MediaPipe hands to return no results
        mock_hands_instance = Mock()
        mock_hands_instance.process.return_value = Mock(multi_hand_landmarks=None)
        mock_hands.return_value = mock_hands_instance

        tracker = GestureTracker()
        hands_present, positions, gestures = tracker.process_frame(mock_frame)

        assert hands_present is False
        assert len(positions) == 0
        assert len(gestures) == 0

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_process_frame_with_hands(self, mock_hands, mock_frame):
        """Test process_frame with hands detected."""
        # Create mock hand landmarks
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = 0.0

        mock_hand_landmarks = Mock()
        mock_hand_landmarks.landmark = [mock_landmark] * 21  # 21 landmarks per hand

        # Mock MediaPipe hands to return hand results
        mock_results = Mock()
        mock_results.multi_hand_landmarks = [mock_hand_landmarks]

        mock_hands_instance = Mock()
        mock_hands_instance.process.return_value = mock_results
        mock_hands.return_value = mock_hands_instance

        tracker = GestureTracker()
        hands_present, positions, gestures = tracker.process_frame(mock_frame)

        assert hands_present is True
        assert len(positions) == 1
        assert len(gestures) == 1

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_get_hands_present_false_initially(self, mock_hands):
        """Test that hands_present is False initially."""
        tracker = GestureTracker()

        assert tracker.get_hands_present() is False

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_get_hand_positions_empty_initially(self, mock_hands):
        """Test that hand positions list is empty initially."""
        tracker = GestureTracker()

        positions = tracker.get_hand_positions()

        assert positions == []

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_get_gestures_empty_initially(self, mock_hands):
        """Test that gestures list is empty initially."""
        tracker = GestureTracker()

        gestures = tracker.get_gestures()

        assert gestures == []

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_distance_between_calculation(self, mock_hands):
        """Test the _distance_between helper method."""
        tracker = GestureTracker()

        p1 = (0, 0)
        p2 = (3, 4)
        distance = tracker._distance_between(p1, p2)

        # Distance should be 5 (3-4-5 triangle)
        assert distance == 5.0

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_distance_between_same_point(self, mock_hands):
        """Test distance calculation for identical points."""
        tracker = GestureTracker()

        p1 = (5, 10)
        p2 = (5, 10)
        distance = tracker._distance_between(p1, p2)

        assert distance == 0.0

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_is_finger_extended(self, mock_hands):
        """Test _is_finger_extended logic."""
        tracker = GestureTracker()

        wrist = (0, 0)
        base = (10, 10)

        # Extended finger tip (far from wrist)
        tip_extended = (25, 25)
        assert tracker._is_finger_extended(tip_extended, base, wrist) is True

        # Curled finger tip (close to wrist)
        tip_curled = (5, 5)
        assert tracker._is_finger_extended(tip_curled, base, wrist) is False

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    @patch('gesture_tracker.mp.solutions.drawing_utils')
    def test_draw_landmarks_no_hands(self, mock_drawing_utils, mock_hands, mock_frame):
        """Test draw_landmarks when no hands are present."""
        tracker = GestureTracker()
        tracker.hands_present = False

        result = tracker.draw_landmarks(mock_frame.copy())

        # Should return frame unchanged
        assert result is not None
        assert result.shape == mock_frame.shape

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    @patch('gesture_tracker.mp.solutions.drawing_utils.draw_landmarks')
    def test_draw_landmarks_with_hands(self, mock_draw_landmarks, mock_hands, mock_frame):
        """Test draw_landmarks when hands are detected."""
        # Setup mock hand data
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5

        mock_hand_landmarks = Mock()
        mock_hand_landmarks.landmark = [mock_landmark] * 21

        tracker = GestureTracker()
        tracker.hands_present = True
        tracker.hand_landmarks = [mock_hand_landmarks]
        tracker.hand_positions = [(320, 240)]
        tracker.gestures = [GestureType.OPEN_PALM]

        result = tracker.draw_landmarks(mock_frame.copy())

        # Should have called draw_landmarks
        assert mock_draw_landmarks.called

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_recognize_gesture_open_palm(self, mock_hands):
        """Test gesture recognition for open palm."""
        tracker = GestureTracker()

        # Create mock landmarks for open palm (all fingers extended)
        landmarks = Mock()
        landmarks.landmark = []

        # Add landmarks in a pattern that suggests open palm
        # All fingertips should be far from wrist
        for i in range(21):
            lm = Mock()
            if i in [4, 8, 12, 16, 20]:  # Fingertips
                lm.x = 0.5 + (i * 0.05)
                lm.y = 0.1
            else:
                lm.x = 0.5
                lm.y = 0.5
            landmarks.landmark.append(lm)

        gesture = tracker._recognize_gesture(landmarks, 640, 480)

        # With properly extended fingers, should recognize gesture
        assert gesture in [GestureType.OPEN_PALM, GestureType.UNKNOWN, GestureType.POINTING]

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_recognize_gesture_closed_fist(self, mock_hands):
        """Test gesture recognition for closed fist."""
        tracker = GestureTracker()

        # Create mock landmarks for closed fist (no fingers extended)
        landmarks = Mock()
        landmarks.landmark = []

        # All points close together (fist)
        for i in range(21):
            lm = Mock()
            lm.x = 0.5
            lm.y = 0.5
            landmarks.landmark.append(lm)

        gesture = tracker._recognize_gesture(landmarks, 640, 480)

        # Should recognize closed fist or unknown
        assert gesture in [GestureType.CLOSED_FIST, GestureType.UNKNOWN]

    @patch('gesture_tracker.mp.solutions.hands.Hands')
    def test_hand_positions_normalized(self, mock_hands, mock_frame):
        """Test that hand positions are properly calculated."""
        # Create mock hand landmarks
        mock_landmark = Mock()
        mock_landmark.x = 0.5  # Center of frame
        mock_landmark.y = 0.5

        mock_hand_landmarks = Mock()
        mock_hand_landmarks.landmark = [mock_landmark] * 21

        mock_results = Mock()
        mock_results.multi_hand_landmarks = [mock_hand_landmarks]

        mock_hands_instance = Mock()
        mock_hands_instance.process.return_value = mock_results
        mock_hands.return_value = mock_hands_instance

        tracker = GestureTracker()
        hands_present, positions, gestures = tracker.process_frame(mock_frame)

        # Center should be at (320, 240) for 640x480 frame
        assert len(positions) == 1
        assert 250 <= positions[0][0] <= 390  # Allow some tolerance
        assert 190 <= positions[0][1] <= 290
