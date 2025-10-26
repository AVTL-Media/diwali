# Phase 2, Task 1: Testing Infrastructure Setup

**Phase**: 2 - Testing Foundation
**Week**: 2-3
**Agent Assignment**: Agent B
**Can Run in Parallel**: ✅ Yes (with Phase 1, Task 3: Error Handling)
**Dependencies**: None (can start immediately)
**Estimated Duration**: 3 days

## Overview

Set up the testing infrastructure including base test classes, mock objects, pytest configuration, and CI/CD pipeline.

## Deliverables

1. `tests/base.py` - Base test case class
2. `tests/mocks.py` - Mock objects for hardware
3. `pytest.ini` or `pyproject.toml` - Pytest configuration
4. `.github/workflows/tests.yml` - CI/CD pipeline
5. Test fixtures and utilities

## Implementation Steps

### Step 1: Create Base Test Classes (Day 1)

```python
# tests/base.py
import unittest
import pygame
import numpy as np
import tempfile
import os
import json

class DiwaliTestCase(unittest.TestCase):
    """Base test case for Diwali Projection System tests."""

    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.test_surface = pygame.Surface((800, 600))
        self.config_file = self._create_test_config()

    def tearDown(self):
        """Clean up after test."""
        pygame.quit()
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)

    def _create_test_config(self):
        """Create temporary config file."""
        config = {
            "camera": {"resolution": [640, 480], "fps": 30},
            "motion_detection": {"threshold": 25},
            "rangoli": {"rotation_speed": 0.01},
            "fireworks": {"particle_count": 50}
        }

        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f)
        return path

    def assert_surface_has_content(self, surface):
        """Assert surface is not blank."""
        arr = pygame.surfarray.array3d(surface)
        all_black = np.all(arr == 0)
        self.assertFalse(all_black, "Surface is blank")

    def assert_colors_in_surface(self, surface, colors):
        """Assert specific colors exist in surface."""
        arr = pygame.surfarray.array3d(surface)
        for color in colors:
            color_arr = np.array(color)
            exists = np.any(np.all(arr == color_arr.reshape(1, 1, 3), axis=2))
            self.assertTrue(exists, f"Color {color} not found")

    def create_test_image(self, size=(100, 100), color=(255, 0, 0)):
        """Create a test image surface."""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface
```

### Step 2: Create Mock Objects (Day 1)

```python
# tests/mocks.py
import numpy as np
import time

class MockCamera:
    """Mock camera for testing."""

    def __init__(self, test_frames=None):
        self.test_frames = test_frames or []
        self.frame_index = 0
        self.is_opened = True

    def read(self):
        """Return a test frame."""
        if not self.test_frames:
            # Return black frame
            return True, np.zeros((480, 640, 3), dtype=np.uint8)

        frame = self.test_frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.test_frames)
        return True, frame

    def release(self):
        """Mock release."""
        self.is_opened = False

    def isOpened(self):
        """Check if camera is open."""
        return self.is_opened


class MockAudioDetector:
    """Mock audio detector for testing."""

    def __init__(self, levels=None):
        self.levels = levels or [0.0]
        self.index = 0

    def get_audio_level(self):
        """Return mock audio level."""
        level = self.levels[self.index]
        self.index = (self.index + 1) % len(self.levels)
        return level

    def start(self):
        """Mock start."""
        pass

    def stop(self):
        """Mock stop."""
        pass


class MockMotionDetector:
    """Mock motion detector for testing."""

    def __init__(self, detections=None):
        self.detections = detections or []
        self.index = 0

    def detect(self, frame):
        """Return mock motion detection."""
        if not self.detections:
            return None

        detection = self.detections[self.index]
        self.index = (self.index + 1) % len(self.detections)
        return detection


class MockGestureTracker:
    """Mock gesture tracker for testing."""

    def __init__(self, gestures=None):
        self.gestures = gestures or []
        self.index = 0

    def process_frame(self, frame):
        """Return mock gesture."""
        if not self.gestures:
            return None

        gesture = self.gestures[self.index]
        self.index = (self.index + 1) % len(self.gestures)
        return gesture
```

### Step 3: Configure Pytest (Day 2)

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = """
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
"""
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "visual: marks tests that compare visual output",
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Step 4: Create CI/CD Pipeline (Day 2)

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, improvements ]
  pull_request:
    branches: [ main, improvements ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y libsdl2-dev libsdl2-mixer-dev libsdl2-ttf-dev

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

### Step 5: Create Test Fixtures (Day 3)

```python
# tests/fixtures.py
import pytest
import pygame
import numpy as np
from tests.mocks import MockCamera, MockAudioDetector
from src.config_manager import ConfigManager
from src.asset_manager import AssetManager

@pytest.fixture
def pygame_init():
    """Initialize pygame for testing."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def test_surface():
    """Create a test surface."""
    return pygame.Surface((800, 600))

@pytest.fixture
def test_config(tmp_path):
    """Create a test config file."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "camera": {"resolution": [640, 480], "fps": 30},
        "motion_detection": {"threshold": 25}
    }
    import json
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def config_manager(test_config):
    """Create a ConfigManager instance."""
    return ConfigManager(test_config)

@pytest.fixture
def asset_manager(tmp_path):
    """Create an AssetManager instance."""
    return AssetManager(base_path=str(tmp_path))

@pytest.fixture
def mock_camera():
    """Create a mock camera."""
    return MockCamera()

@pytest.fixture
def mock_audio():
    """Create a mock audio detector."""
    return MockAudioDetector()
```

### Step 6: Documentation (Day 3)

```markdown
# Testing Guide

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_config_manager.py

# Run specific test
pytest tests/test_config_manager.py::TestConfigManager::test_get_nested_value

# Run tests matching pattern
pytest -k "config"
```

## Writing Tests

### Using Base Test Case

```python
from tests.base import DiwaliTestCase

class TestMyComponent(DiwaliTestCase):
    def test_something(self):
        # pygame already initialized
        # test surface available as self.test_surface
        # test config available as self.config_file
        pass
```

### Using Fixtures

```python
import pytest
from tests.fixtures import config_manager, test_surface

def test_with_fixtures(config_manager, test_surface):
    value = config_manager.get("camera.fps")
    assert value == 30
```

### Using Mocks

```python
from tests.mocks import MockCamera

def test_with_mock_camera():
    camera = MockCamera()
    ret, frame = camera.read()
    assert ret == True
```

## Test Organization

- `tests/test_config_manager.py` - ConfigManager tests
- `tests/test_asset_manager.py` - AssetManager tests
- `tests/test_components/` - Component tests
- `tests/integration/` - Integration tests
```
```

## Testing Checklist

- [ ] Base test case class created
- [ ] Mock objects for hardware created
- [ ] Pytest configuration complete
- [ ] CI/CD pipeline configured
- [ ] Test fixtures available
- [ ] Documentation written
- [ ] Sample tests run successfully
- [ ] Coverage reporting works

## Integration Points

**Can Run in Parallel with:**
- Phase 1, Task 3 (Error Handling)

**Provides for:**
- Phase 2, Tasks 2-4 (Component tests)
- All future test development

## Success Criteria

✅ Pytest runs successfully
✅ CI/CD pipeline triggers on commits
✅ Coverage reporting works
✅ Mock objects work correctly
✅ Base test class utilities work
✅ Documentation complete
✅ Ready for writing component tests
