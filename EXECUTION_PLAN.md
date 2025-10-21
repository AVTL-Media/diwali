# Diwali Projection System: Technical Execution Plan

## Overview

This document outlines a structured implementation plan for the recommended improvements to the Diwali Projection System, with technical specifications and timelines. The plan is organized into four phases, each focusing on specific areas of improvement identified in the code review and refactoring documentation.

## Phase 1: Configuration Management System (Estimated: 2 weeks)

### Technical Specifications

#### 1.1 ConfigManager Class (Week 1)

```python
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, cast
import json
import os
from pathlib import Path

T = TypeVar('T')

class ConfigManager:
    """
    Centralized configuration management for Diwali Projection System.
    Handles config loading, access, validation, and type conversion.
    """
    
    def __init__(self, config_path: str = "config/settings.json", default_config: Optional[Dict] = None):
        self.config_path = Path(config_path)
        self.config: Dict = default_config or {}
        self.load()
        
    def load(self) -> None:
        """Load configuration from file if exists."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                    self._validate()
        except (json.JSONDecodeError, IOError) as e:
            # Log error but continue with default config
            print(f"Error loading config: {e}")
            
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")
            
    def _validate(self) -> None:
        """Validate configuration structure and values."""
        # Implement schema validation here
        pass
        
    def get(self, path: str, default: Optional[T] = None) -> T:
        """
        Get a configuration value by dot-notation path.
        Example: config_manager.get("rangoli.rotation_speed", 0.01)
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return cast(T, default)
            value = value[key]
            
        return cast(T, value) if value is not None else cast(T, default)
        
    def get_float(self, path: str, default: float = 0.0) -> float:
        """Get a float value from configuration."""
        value = self.get(path, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
            
    def get_int(self, path: str, default: int = 0) -> int:
        """Get an integer value from configuration."""
        value = self.get(path, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
            
    def get_bool(self, path: str, default: bool = False) -> bool:
        """Get a boolean value from configuration."""
        value = self.get(path, default)
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)
        
    def get_list(self, path: str, default: Optional[List] = None) -> List:
        """Get a list value from configuration."""
        value = self.get(path, default or [])
        if isinstance(value, list):
            return value
        return [value] if value is not None else []
        
    def set(self, path: str, value: Any) -> None:
        """Set a configuration value by dot-notation path."""
        keys = path.split('.')
        config = self.config
        
        # Navigate to the innermost dict
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
```

#### 1.2 Configuration Integration (Week 2)

1. **Visual Generator Integration**:
   - Create an adapter to migrate from dictionary-based config to ConfigManager
   - Update all config access patterns in visual_generator.py

2. **Config Schema Validation**:
   - Define JSON schema for configuration validation
   - Implement validation in ConfigManager._validate()

3. **Default Configuration**:
   - Create comprehensive default configuration with documentation
   - Implement fallback values for all settings

### Deliverables

- ConfigManager class with comprehensive test coverage
- Updated visual_generator.py using the new configuration system
- Configuration schema documentation
- Migration guide for other components

## Phase 2: Error Handling Framework (Estimated: 1 week)

### Technical Specifications

#### 2.1 Logger Implementation

```python
import logging
from typing import Optional, Dict, Any
import os
from datetime import datetime

class DiwaliLogger:
    """Centralized logging for Diwali Projection System."""
    
    LOG_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    
    def __init__(
        self, 
        name: str, 
        log_level: str = "info",
        log_to_file: bool = True,
        log_dir: str = "logs"
    ):
        self.logger = logging.getLogger(name)
        
        # Set log level
        level = self.LOG_LEVELS.get(log_level.lower(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler
        console = logging.StreamHandler()
        console.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.setFormatter(formatter)
        
        # Add console handler to logger
        self.logger.addHandler(console)
        
        # Add file handler if enabled
        if log_to_file:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            log_file = os.path.join(
                log_dir, 
                f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional context data."""
        self._log(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional context data."""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional context data."""
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with optional context data."""
        self._log(logging.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with optional context data."""
        self._log(logging.CRITICAL, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal method to handle logging with context data."""
        if kwargs:
            context_str = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} [{context_str}]"
        self.logger.log(level, message)
```

#### 2.2 Error Handling Decorator

```python
import functools
from typing import Any, Callable, TypeVar, cast, Optional
import traceback

T = TypeVar('T')

def error_handler(logger: Optional[Any] = None, default_return: Any = None):
    """
    Decorator for consistent error handling.
    
    Args:
        logger: Logger instance to use for error reporting
        default_return: Default value to return on error
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    # Get caller info
                    tb = traceback.extract_tb(e.__traceback__)
                    caller = tb[-2] if len(tb) > 1 else tb[0]
                    caller_info = f"{caller.filename}:{caller.lineno}"
                    
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exception_type=type(e).__name__,
                        caller=caller_info
                    )
                return cast(T, default_return)
        return wrapper
    return decorator
```

#### 2.3 Implementation Strategy

1. **Logger Integration**:
   - Create a logger instance in main.py
   - Pass logger to all major components at initialization

2. **Error Handling in Critical Functions**:
   - Apply error_handler decorator to image loading functions
   - Add try/except blocks in event loops and data processing

3. **Graceful Degradation**:
   - Implement fallback visuals for missing assets
   - Add recovery mechanisms for failed operations

### Deliverables

- DiwaliLogger class with comprehensive test coverage
- Error handling decorator for consistent error management
- Updated core functions with proper error handling
- Documentation on error handling best practices

## Phase 3: Component Decomposition and Refactoring (Estimated: 2 weeks)

### Technical Specifications

#### 3.1 Visual Components Architecture

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import pygame

class VisualComponent(ABC):
    """Base class for all visual components."""
    
    def __init__(self, config_manager: Any):
        self.config_manager = config_manager
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update component state based on time delta."""
        pass
        
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render component to the given surface."""
        pass

class FireworksManager(VisualComponent):
    """Manages firework particle effects."""
    
    def __init__(self, config_manager: Any):
        super().__init__(config_manager)
        self.particles: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
        self.start_times: Dict[Tuple[int, int], float] = {}
        # Initialize other properties
        
    def update(self, dt: float) -> None:
        """Update firework particles physics."""
        self._update_particles(dt)
        self._cleanup_expired_fireworks()
        self._limit_active_fireworks()
        
    def _update_particles(self, dt: float) -> None:
        """Update individual particles in all fireworks."""
        # Implementation
        
    def _cleanup_expired_fireworks(self) -> None:
        """Remove expired fireworks from tracking."""
        # Implementation
        
    def _limit_active_fireworks(self) -> None:
        """Ensure we don't exceed the maximum number of fireworks."""
        # Implementation
        
    def create_firework(self, origin: Tuple[int, int]) -> None:
        """Create a new firework at the specified origin."""
        # Implementation
        
    def render(self, surface: pygame.Surface) -> None:
        """Render all active firework particles."""
        # Implementation

class RangoliRenderer(VisualComponent):
    """Handles rangoli pattern rendering and effects."""
    
    def __init__(self, config_manager: Any):
        super().__init__(config_manager)
        self.angle = 0
        self.color_cycle_hue = 0
        self.patterns = []
        # Initialize other properties
        
    def update(self, dt: float) -> None:
        """Update rangoli animation."""
        self._update_rotation(dt)
        self._update_color_cycling(dt)
        
    def _update_rotation(self, dt: float) -> None:
        """Update rangoli rotation angle."""
        # Implementation
        
    def _update_color_cycling(self, dt: float) -> None:
        """Update color cycling for psychedelic effect."""
        # Implementation
        
    def render(self, surface: pygame.Surface, center: Tuple[int, int], alpha: int = 200) -> None:
        """Render rangoli pattern centered at specified position."""
        # Implementation

# Additional component classes would follow the same pattern
```

#### 3.2 Refactoring Strategy

1. **Extract Components**:
   - Create specialized classes for each major visual component
   - Refactor VisualGenerator to compose and delegate to these components

2. **Configuration Injection**:
   - Inject ConfigManager into components
   - Use dependency injection for better testability

3. **Interface Consistency**:
   - Ensure all components follow the same interface pattern
   - Standardize method signatures and naming conventions

### Deliverables

- Component base class and specialized implementations
- Refactored VisualGenerator using composition
- Updated integration with main.py
- Documentation on component architecture

## Phase 4: Testing Infrastructure (Estimated: 1 week)

### Technical Specifications

#### 4.1 Test Framework

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

#### 4.2 Mock Objects

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

#### 4.3 Sample Tests

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
        from src.fireworks_manager import FireworksManager
        
        config = ConfigManager(self.config_file)
        manager = FireworksManager(config)
        
        # Initial state
        self.assertEqual(len(manager.particles), 0)
        
        # Create firework
        manager.create_firework((400, 300))
        
        # Check particles were created
        self.assertEqual(len(manager.particles), 1)
        self.assertIn((400, 300), manager.particles)
        
    def test_update_particles(self):
        """Test updating particle physics."""
        from src.config_manager import ConfigManager
        from src.fireworks_manager import FireworksManager
        
        config = ConfigManager(self.config_file)
        manager = FireworksManager(config)
        
        # Create firework
        manager.create_firework((400, 300))
        
        # Get initial positions
        particles = manager.particles[(400, 300)]
        initial_positions = [(p["x"], p["y"]) for p in particles]
        
        # Update with time delta
        manager.update(0.1)
        
        # Check positions have changed
        new_positions = [(p["x"], p["y"]) for p in manager.particles[(400, 300)]]
        self.assertNotEqual(initial_positions, new_positions)
```

### Deliverables

- Test base classes for consistent testing
- Mock objects for hardware dependencies
- Unit tests for new components
- Documentation on test writing and running

## Implementation Timeline

```
Week 1: ConfigManager Class Development
Week 2: ConfigManager Integration
Week 3: Error Handling Framework
Week 4: Core Component Extraction (FireworksManager, RangoliRenderer)
Week 5: Additional Component Extraction and Integration
Week 6: Testing Infrastructure and Initial Tests
```

## Resource Requirements

1. **Development Environment**:
   - Python 3.9+
   - Pygame 2.1.0+
   - OpenCV 4.5+
   - NumPy 1.20+

2. **Testing Tools**:
   - pytest for unit testing
   - pytest-cov for coverage reporting
   - unittest.mock for mocking

3. **Version Control**:
   - Git repository with feature branches
   - Pull request process for code review

## Success Metrics

1. **Code Quality**:
   - Reduce average method length by 50%
   - Increase test coverage to 70%+
   - Eliminate deep nested configuration access

2. **Robustness**:
   - Zero uncaught exceptions in normal operation
   - Graceful degradation for all error cases

3. **Maintainability**:
   - All new code has proper type hints
   - All public methods have docstrings
   - Component boundaries clearly defined

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking changes | High | Medium | Comprehensive test suite before/after refactoring |
| Performance regression | Medium | Low | Benchmark key operations before/after changes |
| Feature compatibility | High | Medium | Create compatibility layers for transition |

## Conclusion

This execution plan provides a detailed roadmap for implementing the recommended improvements to the Diwali Projection System. By following this structured approach with clear technical specifications, the codebase will become more maintainable, robust, and performant while preserving its core functionality.

The plan prioritizes configuration management and error handling as foundational improvements, followed by component decomposition and testing infrastructure to ensure long-term sustainability. Each phase builds on the previous one, creating a gradual transformation that minimizes risk while maximizing improvement.
