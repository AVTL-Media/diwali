# Testing Infrastructure Implementation

⚠️ **REVISED PLAN UPDATE**: This is now **Phase 2** (Weeks 2-3), moved from original Phase 7 (Week 11).

**Critical Change**: Testing infrastructure now comes **8 WEEKS EARLIER** to provide a safety net for all subsequent refactoring work.

This document outlines the implementation plan for the Testing Infrastructure, which is **Phase 2** of the Diwali Projection System improvements.

## Overview

This phase focuses on creating a comprehensive testing framework **EARLY** to provide confidence during the risky refactoring phases ahead.

**IMPORTANT**: Testing must be in place before Phase 3 (Events/State) and Phase 4 (Component Extraction) begin.

## Timeline - REVISED

- **Week 2-3** (parallel with Phase 1 completion): Testing Infrastructure setup
- **Week 3**: Initial test coverage (40%+ target)

## Technical Specifications

### Test Base Classes

```python
import unittest
import pygame
import numpy as np
from unittest import mock
import tempfile
import os
import json

class DiwaliTestCase(unittest.TestCase):
    """Base test case for Diwali Projection System tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Initialize pygame
        pygame.init()
        
        # Create a test surface
        self.test_surface = pygame.Surface((800, 600))
        
        # Create a temporary config file
        self.config_file = self._create_test_config()
        
    def tearDown(self):
        """Clean up after test."""
        pygame.quit()
        # Remove temporary config file
        if hasattr(self, 'config_file') and os.path.exists(self.config_file):
            os.remove(self.config_file)
            
    def _create_test_config(self):
        """Create a temporary config file with test settings."""
        config = {
            "rangoli": {
                "rotation_speed": 0.01,
                "psychedelic": {
                    "color_cycle_speed": 0.03
                }
            },
            "fireworks": {
                "particle_count": 50
            }
        }
        
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f)
            
        return path
        
    def assert_surface_has_content(self, surface):
        """Assert that a surface has non-blank content."""
        # Convert surface to array
        arr = pygame.surfarray.array3d(surface)
        # Check if all pixels are black (0,0,0)
        all_black = np.all(arr == 0)
        self.assertFalse(all_black, "Surface is blank")
        
    def assert_colors_in_surface(self, surface, colors):
        """Assert that specific colors exist in the surface."""
        arr = pygame.surfarray.array3d(surface)
        
        for color in colors:
            # Convert color to numpy array for comparison
            color_arr = np.array(color)
            # Check if color exists in surface
            exists = np.any(np.all(arr == color_arr.reshape(1, 1, 3), axis=2))
            self.assertTrue(exists, f"Color {color} not found in surface")
```

### Mock Objects

```python
class MockCamera:
    """Mock camera for testing."""
    
    def __init__(self, test_frames=None):
        self.test_frames = test_frames or []
        self.frame_index = 0
        
    def read(self):
        """Return a test frame."""
        if not self.test_frames:
            # Return black frame if no test frames
            return True, np.zeros((480, 640, 3), dtype=np.uint8)
            
        frame = self.test_frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.test_frames)
        return True, frame
        
    def release(self):
        """Mock release method."""
        pass

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
```

### Sample Tests

```python
class TestConfigManager(DiwaliTestCase):
    """Tests for ConfigManager class."""
    
    def test_get_with_dot_notation(self):
        """Test retrieving nested config with dot notation."""
        from src.config_manager import ConfigManager
        
        manager = ConfigManager(self.config_file)
        
        # Test getting nested value
        self.assertEqual(manager.get("rangoli.rotation_speed"), 0.01)
        
        # Test default value for non-existent path
        self.assertEqual(manager.get("nonexistent.path", "default"), "default")
        
    def test_type_specific_getters(self):
        """Test type-specific getter methods."""
        from src.config_manager import ConfigManager
        
        manager = ConfigManager(self.config_file)
        
        # Test float getter
        self.assertEqual(manager.get_float("rangoli.rotation_speed"), 0.01)
        
        # Test float conversion
        manager.set("test.string_number", "123.45")
        self.assertEqual(manager.get_float("test.string_number"), 123.45)
        
        # Test int getter with default
        self.assertEqual(manager.get_int("nonexistent.path", 42), 42)

class TestFireworksManager(DiwaliTestCase):
    """Tests for FireworksManager class."""
    
    def test_create_firework(self):
        """Test creating a firework."""
        from src.config_manager import ConfigManager
        from src.components.fireworks_manager import FireworksManager
        
        config = ConfigManager(self.config_file)
        manager = FireworksManager(config)
        
        # Initial state
        self.assertEqual(len(manager.particles), 0)
        
        # Create firework
        manager.create_firework((400, 300))
        
        # Check particles were created
        self.assertEqual(len(manager.particles), 1)
        self.assertIn((400, 300), manager.particles)
```

## Implementation Tasks

### 1. Test Framework

- [ ] Create `tests/base.py` with DiwaliTestCase class
- [ ] Create `tests/mocks.py` with mock objects for hardware dependencies
- [ ] Set up pytest configuration in pyproject.toml or setup.cfg
- [ ] Create test fixtures for common test scenarios

### 2. Unit Tests

- [ ] Create tests for ConfigManager (Phase 1)
- [ ] Create tests for error handling (Phase 2)
- [ ] Create tests for visual components (Phase 3)
- [ ] Create integration tests for the full system

### 3. Test Data

- [ ] Create test images for asset loading
- [ ] Create test configurations for various scenarios
- [ ] Create test camera frames for person detection
- [ ] Create reference outputs for visual comparison

### 4. Test Automation

- [ ] Set up GitHub Actions for continuous integration
- [ ] Configure test coverage reporting
- [ ] Create test documentation and examples

## Expected Outcomes

1. **Comprehensive Test Coverage**: Ensure all components are tested
2. **Regression Prevention**: Catch bugs before they make it to production
3. **Documentation**: Tests serve as additional documentation for expected behavior
4. **Confidence**: Enable confident refactoring and feature addition

## Testing Strategy

### Unit Testing

- Test individual components in isolation
- Mock dependencies to control test environment
- Focus on boundary conditions and edge cases

### Integration Testing

- Test components working together
- Verify correct interaction between components
- Test full system behavior

### Visual Testing

- Verify visual output matches expectations
- Compare rendered surfaces to reference images
- Test animations and dynamic effects

## Test Examples

### Testing Visual Output

```python
def test_rangoli_rendering(self):
    """Test that rangoli rendering produces expected visual output."""
    # Create rangoli renderer with test config
    config = ConfigManager(self.config_file)
    renderer = RangoliRenderer(config)
    
    # Create a surface to render onto
    surface = pygame.Surface((800, 600))
    
    # Render rangoli
    renderer.render(surface, (400, 300), alpha=200)
    
    # Verify surface has content
    self.assert_surface_has_content(surface)
    
    # Verify expected colors are present
    expected_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Example colors
    self.assert_colors_in_surface(surface, expected_colors)
```

### Testing Component Lifecycle

```python
def test_fireworks_lifecycle(self):
    """Test full lifecycle of firework particles."""
    # Create fireworks manager with test config
    config = ConfigManager(self.config_file)
    manager = FireworksManager(config)
    
    # Create firework
    manager.create_firework((400, 300))
    
    # Get initial particle count
    initial_count = len(manager.particles[(400, 300)])
    
    # Update multiple times to simulate time passing
    for _ in range(100):
        manager.update(0.1)
        
    # Verify particles have expired
    self.assertNotIn((400, 300), manager.particles)
```
