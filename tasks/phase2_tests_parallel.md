# Phase 2: Parallel Test Writing Tasks

**Phase**: 2 - Testing Foundation
**Week**: 3
**Can Run in Parallel**: ✅ Yes - All 3 tasks are independent
**Dependencies**: Phase 2, Task 1 (Test Infrastructure) must be complete

## Overview

Once the test infrastructure is set up, these test writing tasks can be done independently in parallel by different agents.

---

## Task 2A: ConfigManager Tests

**Agent Assignment**: Agent A
**Estimated Duration**: 1 day
**File**: `tests/test_config_manager.py`

### Test Coverage Goals

- Dot notation access
- Type conversion (int, float, bool, list)
- Default values
- Nested paths
- Missing paths
- Set operations
- Save/load cycle
- Error cases

### Minimal Test Suite

```python
import unittest
from src.config_manager import ConfigManager
from tests.base import DiwaliTestCase

class TestConfigManager(DiwaliTestCase):
    def test_get_nested_value(self):
        """Test dot notation access."""
        manager = ConfigManager(self.config_file)
        self.assertEqual(manager.get("camera.fps"), 30)

    def test_get_with_default(self):
        """Test default values."""
        manager = ConfigManager(self.config_file)
        self.assertEqual(manager.get("nonexistent", 42), 42)

    def test_type_conversions(self):
        """Test type-specific getters."""
        manager = ConfigManager(self.config_file)
        self.assertEqual(manager.get_int("camera.fps"), 30)
        self.assertEqual(manager.get_float("rangoli.rotation_speed"), 0.01)
        self.assertTrue(isinstance(manager.get_list("camera.resolution"), list))

    def test_set_and_save(self):
        """Test setting and persisting values."""
        manager = ConfigManager(self.config_file)
        manager.set("new.value", 100)
        manager.save()

        manager2 = ConfigManager(self.config_file)
        self.assertEqual(manager2.get("new.value"), 100)
```

**Target**: 15-20 tests, 90%+ coverage of ConfigManager

---

## Task 2B: AssetManager Tests

**Agent Assignment**: Agent B
**Estimated Duration**: 1 day
**File**: `tests/test_asset_manager.py`

### Test Coverage Goals

- Image loading
- Image caching
- Missing asset fallbacks
- Image sequences
- Random selection
- Asset validation
- Thread safety
- Cache clearing

### Minimal Test Suite

```python
import unittest
import pygame
import tempfile
import os
from src.asset_manager import AssetManager
from tests.base import DiwaliTestCase

class TestAssetManager(DiwaliTestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()
        self.manager = AssetManager(base_path=self.temp_dir)

        # Create test image
        test_surface = pygame.Surface((100, 100))
        test_surface.fill((255, 0, 0))
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        pygame.image.save(test_surface, self.test_image_path)

    def test_load_existing_image(self):
        """Test loading existing image."""
        image = self.manager.get_image("test.png")
        self.assertIsNotNone(image)
        self.assertEqual(image.get_size(), (100, 100))

    def test_missing_image_fallback(self):
        """Test fallback for missing images."""
        image = self.manager.get_image("nonexistent.png")
        self.assertIsNotNone(image)  # Should return default

    def test_image_caching(self):
        """Test that images are cached."""
        img1 = self.manager.get_image("test.png")
        img2 = self.manager.get_image("test.png")
        self.assertIs(img1, img2)  # Same instance

    def test_cache_clearing(self):
        """Test cache clearing."""
        self.manager.get_image("test.png")
        self.assertEqual(len(self.manager.cache), 1)
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.cache), 0)
```

**Target**: 15-20 tests, 85%+ coverage of AssetManager

---

## Task 2C: Error Handling & Logger Tests

**Agent Assignment**: Agent C
**Estimated Duration**: 1 day
**Files**: `tests/test_logger.py`, `tests/test_error_handler.py`

### Test Coverage Goals

- Log file creation
- Log levels
- Context data logging
- Error handler catching exceptions
- Error handler returning defaults
- Error handler with logger
- Integration patterns

### Minimal Test Suite

```python
# tests/test_logger.py
import unittest
import tempfile
import os
from src.logger import DiwaliLogger

class TestDiwaliLogger(unittest.TestCase):
    def setUp(self):
        self.log_dir = tempfile.mkdtemp()

    def test_logger_creates_file(self):
        """Test log file creation."""
        logger = DiwaliLogger("test", log_dir=self.log_dir)
        logger.info("Test message")

        log_files = os.listdir(self.log_dir)
        self.assertEqual(len(log_files), 1)

    def test_all_log_levels(self):
        """Test different log levels."""
        logger = DiwaliLogger("test", log_dir=self.log_dir, log_level="debug")
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        # Should not raise

    def test_context_logging(self):
        """Test logging with context."""
        logger = DiwaliLogger("test", log_dir=self.log_dir)
        logger.info("Message", key="value", count=42)
        # Should format correctly


# tests/test_error_handler.py
import unittest
from src.error_handler import error_handler
from src.logger import DiwaliLogger

class TestErrorHandler(unittest.TestCase):
    def test_catches_exception(self):
        """Test exception catching."""
        logger = DiwaliLogger("test", log_to_file=False)

        @error_handler(logger=logger, default_return=42)
        def failing():
            raise ValueError("Error")

        result = failing()
        self.assertEqual(result, 42)

    def test_passes_success(self):
        """Test successful calls pass through."""
        @error_handler(logger=None, default_return=None)
        def success(x):
            return x * 2

        self.assertEqual(success(21), 42)
```

**Target**: 15-20 tests, 80%+ coverage

---

## Coordination

### Communication Points

- **Daily Standup**: Share progress and blockers
- **Shared Test Report**: All agents push to same coverage report
- **Conflict Resolution**: If tests conflict, Agent A has priority on shared files

### Success Criteria

✅ All three test suites pass
✅ Combined coverage > 40% of codebase
✅ No test conflicts
✅ CI/CD pipeline green
✅ All tests documented

### Integration

After all three tasks complete:
1. Run full test suite: `pytest tests/`
2. Generate coverage report: `pytest --cov=src --cov-report=html`
3. Verify CI/CD pipeline passes
4. Ready to proceed to Phase 3
