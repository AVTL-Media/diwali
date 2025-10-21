"""Pytest configuration and shared fixtures."""

import pytest
import numpy as np
import cv2
import json
import tempfile
from pathlib import Path


@pytest.fixture
def mock_config():
    """Provide a mock configuration dictionary."""
    return {
        "camera": {
            "device_id": 0,
            "width": 640,
            "height": 480,
            "fps": 30
        },
        "audio_detection": {
            "enabled": True,
            "threshold_multiplier": 2.0,
            "sample_rate": 44100,
            "chunk_size": 1024,
            "window_size": 0.5
        },
        "motion_detection": {
            "blur_size": 5,
            "threshold": 25,
            "min_area": 500,
            "history": 20
        },
        "gesture_tracking": {
            "min_detection_confidence": 0.7,
            "min_tracking_confidence": 0.5,
            "max_num_hands": 2
        },
        "projection": {
            "fullscreen": True,
            "calibration_points": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "calibration_enabled": True
        },
        "visual_effects": {
            "diya": {
                "fade_duration": 0.5,
                "scale_factor": 0.5,
                "max_instances": 10
            },
            "fireworks": {
                "particle_count": 100,
                "lifetime": 2.0,
                "colors": ["#FF5733", "#FFC300", "#DAF7A6"]
            },
            "rangoli": {
                "pattern_complexity": 3,
                "rotation_speed": 0.01
            }
        },
        "ethereal_outlines": {
            "enabled": True,
            "detection_confidence": 0.7,
            "outline_thickness": 5
        }
    }


@pytest.fixture
def temp_config_file(mock_config):
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        config_path = f.name

    yield config_path

    # Cleanup
    Path(config_path).unlink(missing_ok=True)


@pytest.fixture
def mock_frame():
    """Generate a mock camera frame (640x480 BGR image)."""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def mock_gray_frame():
    """Generate a mock grayscale frame (640x480)."""
    return np.random.randint(0, 255, (480, 640), dtype=np.uint8)


@pytest.fixture
def mock_frame_pair():
    """Generate a pair of consecutive frames for motion detection."""
    frame1 = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
    # Second frame with slight differences
    frame2 = frame1.copy()
    frame2[100:200, 100:200] = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    return frame1, frame2


@pytest.fixture
def mock_frame_with_motion():
    """Generate frames with significant motion between them."""
    # First frame - mostly uniform
    frame1 = np.ones((480, 640), dtype=np.uint8) * 100

    # Second frame - with a bright square (simulating motion)
    frame2 = frame1.copy()
    frame2[200:300, 250:350] = 255

    return frame1, frame2
