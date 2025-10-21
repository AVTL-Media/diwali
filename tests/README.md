# Tests for Diwali Projection System

This directory contains comprehensive test suites for all modules in the Diwali Projection System.

## Test Structure

```
tests/
├── __init__.py                        # Test package initialization
├── conftest.py                        # Shared fixtures and configuration
├── test_audio_detector.py             # Tests for audio detection module
├── test_camera_input.py               # Tests for camera input module
├── test_gesture_tracker.py            # Tests for gesture tracking module
├── test_motion_detector.py            # Tests for motion detection module
├── test_person_outline_detector.py    # Tests for person outline detection
├── test_projection_calibrator.py      # Tests for projection calibration
├── test_scene_manager.py              # Tests for scene state management
└── test_visual_generator.py           # Tests for visual effects generation
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

This will install pytest, pytest-cov, and pytest-mock.

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Run tests for a specific module
pytest tests/test_audio_detector.py

# Run a specific test class
pytest tests/test_motion_detector.py::TestMotionDetector

# Run a specific test function
pytest tests/test_camera_input.py::TestCameraInput::test_init_default_config
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Show Print Statements

```bash
pytest -s
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "motion" in the name
pytest -k motion

# Run all initialization tests
pytest -k init
```

## Test Coverage

Each test file provides comprehensive coverage for its corresponding module:

### test_audio_detector.py
- Initialization with default and custom configs
- Audio spike detection
- Volume level calculation
- Calibration status
- Start/stop functionality

### test_camera_input.py
- Camera initialization and configuration
- Frame capture and preprocessing
- FPS calculation
- Frame transformations (grayscale, blur)
- Resource management

### test_gesture_tracker.py
- Hand detection using MediaPipe
- Gesture recognition (open palm, fist, pointing, pinch)
- Hand position tracking
- Drawing landmarks
- Distance calculations

### test_motion_detector.py
- Frame differencing
- Motion contour detection
- Motion intensity calculation
- History tracking
- Largest contour identification

### test_person_outline_detector.py
- Person detection via MediaPipe Pose
- Background subtraction
- Outline extraction
- Particle effects
- Visualization

### test_projection_calibrator.py
- Calibration point management
- Corner manipulation
- Perspective transformation
- UI rendering
- Configuration persistence

### test_scene_manager.py
- State transitions
- Input processing (motion, audio, gestures)
- State data management
- Timeout handling
- Visual state tracking

### test_visual_generator.py
- Firework particle systems
- Rangoli pattern generation
- Floating object animations
- Visual effect rendering
- Color cycling

## Shared Fixtures (conftest.py)

The following fixtures are available across all test files:

- `mock_config`: Dictionary with default configuration
- `temp_config_file`: Temporary JSON config file
- `mock_frame`: 640x480 BGR camera frame
- `mock_gray_frame`: 640x480 grayscale frame
- `mock_frame_pair`: Two consecutive frames for motion detection
- `mock_frame_with_motion`: Frames with visible motion between them

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.slow
def test_long_running_operation():
    pass

@pytest.mark.hardware
def test_requires_camera():
    pass
```

Run tests excluding certain markers:

```bash
# Skip slow tests
pytest -m "not slow"

# Skip hardware tests
pytest -m "not hardware"
```

## Mocking

Tests use `unittest.mock` to mock external dependencies:

- Camera devices (cv2.VideoCapture)
- Audio input (sounddevice)
- MediaPipe models
- Pygame surfaces
- File I/O operations

This allows tests to run without requiring actual hardware or external resources.

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:

- Don't require physical hardware (camera, microphone)
- Have deterministic outcomes
- Run quickly (most tests < 1 second)
- Provide clear failure messages

## Writing New Tests

When adding new functionality:

1. Create tests in the corresponding test file
2. Use existing fixtures from `conftest.py`
3. Mock external dependencies
4. Test both success and failure paths
5. Verify edge cases
6. Add docstrings to explain test purpose

Example:

```python
def test_new_feature(self, mock_config):
    """Test that new feature works correctly."""
    # Arrange
    detector = MyDetector(mock_config)

    # Act
    result = detector.new_feature()

    # Assert
    assert result is not None
    assert result.some_property == expected_value
```

## Troubleshooting

### Import Errors

If you see import errors, ensure the `src` directory is in your Python path:

```python
import sys
sys.path.insert(0, '/path/to/claude/src')
```

### Mock Not Working

Ensure you're patching the correct import path:

```python
# Patch where it's used, not where it's defined
@patch('motion_detector.cv2.findContours')
def test_something(self, mock_find_contours):
    pass
```

### Pygame Issues

Some tests require pygame initialization:

```python
pygame.init()
# ... test code ...
```

## Coverage Goals

Target coverage metrics:
- Overall: > 80%
- Critical modules (motion_detector, gesture_tracker): > 90%
- Utility modules: > 70%

View coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```
