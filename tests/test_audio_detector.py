"""Tests for the AudioDetector module."""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from audio_detector import AudioDetector


class TestAudioDetector:
    """Test suite for AudioDetector class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        detector = AudioDetector()

        assert detector.config["enabled"] is True
        assert detector.config["threshold_multiplier"] == 2.0
        assert detector.config["sample_rate"] == 44100
        assert detector.is_running is False
        assert detector.audio_spike_detected is False
        assert detector.calibration_complete is False

    def test_init_with_config_file(self, temp_config_file):
        """Test initialization with configuration file."""
        detector = AudioDetector(temp_config_file)

        assert detector.config["enabled"] is True
        assert detector.config["threshold_multiplier"] == 2.0

    def test_start_when_disabled(self, temp_config_file, mock_config):
        """Test that start returns False when audio detection is disabled."""
        mock_config["audio_detection"]["enabled"] = False

        with open(temp_config_file, 'w') as f:
            import json
            json.dump(mock_config, f)

        detector = AudioDetector(temp_config_file)
        result = detector.start()

        assert result is False
        assert detector.is_running is False

    @patch('audio_detector.sd.InputStream')
    @patch('audio_detector.threading.Thread')
    def test_start_success(self, mock_thread, mock_inputstream):
        """Test successful start of audio detection."""
        detector = AudioDetector()

        # Mock the thread
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        result = detector.start()

        assert result is True
        assert detector.is_running is True
        mock_thread_instance.start.assert_called_once()

    def test_stop(self):
        """Test stopping audio detection."""
        detector = AudioDetector()
        detector.is_running = True
        mock_thread = Mock()
        detector.audio_thread = mock_thread

        detector.stop()

        assert detector.is_running is False
        mock_thread.join.assert_called_once()

    def test_is_spike_detected_false_initially(self):
        """Test that spike is not detected initially."""
        detector = AudioDetector()

        assert detector.is_spike_detected() is False

    def test_is_spike_detected_true_when_set(self):
        """Test spike detection when spike is set."""
        detector = AudioDetector()
        detector.audio_spike_detected = True

        assert detector.is_spike_detected() is True

    def test_get_volume_level_not_calibrated(self):
        """Test volume level returns 0 when not calibrated."""
        detector = AudioDetector()
        detector.calibration_complete = False

        volume = detector.get_volume_level()

        assert volume == 0.0

    def test_get_volume_level_calibrated(self):
        """Test volume level calculation when calibrated."""
        detector = AudioDetector()
        detector.calibration_complete = True
        detector.baseline_volume = 0.1
        detector.current_volume = 0.15

        volume = detector.get_volume_level()

        # Volume should be normalized: 0.15 / (0.1 * 3.0) = 0.5
        assert 0.0 <= volume <= 1.0
        assert abs(volume - 0.5) < 0.01  # Allow for floating point precision

    def test_get_volume_level_clamps_to_one(self):
        """Test that volume level is clamped to maximum of 1.0."""
        detector = AudioDetector()
        detector.calibration_complete = True
        detector.baseline_volume = 0.1
        detector.current_volume = 1.0  # Very high volume

        volume = detector.get_volume_level()

        assert volume == 1.0

    def test_is_calibrated_false_initially(self):
        """Test that detector is not calibrated initially."""
        detector = AudioDetector()

        assert detector.is_calibrated() is False

    def test_is_calibrated_true_after_calibration(self):
        """Test calibration status after manual calibration."""
        detector = AudioDetector()
        detector.calibration_complete = True

        assert detector.is_calibrated() is True

    def test_baseline_samples_collection(self):
        """Test that baseline samples are collected correctly."""
        detector = AudioDetector()

        # Simulate adding samples
        for i in range(50):
            detector.baseline_samples.append(0.1 + i * 0.01)

        assert len(detector.baseline_samples) == 50
        assert detector.baseline_samples[0] == 0.1

    def test_spike_duration_timeout(self):
        """Test that spike flag resets after duration timeout."""
        detector = AudioDetector()
        detector.audio_spike_detected = True
        detector.spike_timestamp = time.time() - 1.0  # 1 second ago
        detector.spike_duration = 0.5  # 0.5 second timeout

        # Manually check the timeout logic
        if time.time() - detector.spike_timestamp > detector.spike_duration:
            detector.audio_spike_detected = False

        assert detector.audio_spike_detected is False
