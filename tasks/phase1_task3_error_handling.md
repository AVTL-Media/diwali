# Phase 1, Task 3: Error Handling & Logging

**Phase**: 1 - Foundation
**Week**: 2
**Agent Assignment**: Agent A
**Can Run in Parallel**: ✅ Yes (with Phase 2, Task 1: Testing Infrastructure)
**Dependencies**: ConfigManager (Task 1) and AssetManager (Task 2) should be complete
**Estimated Duration**: 2-3 days

## Overview

Implement centralized logging and error handling framework to provide consistent error management across the codebase.

## Deliverables

1. `src/logger.py` - DiwaliLogger class
2. `src/error_handler.py` - Error handling decorator
3. Unit tests
4. Integration with ConfigManager and AssetManager

## Implementation Steps

### Step 1: Create DiwaliLogger (Day 1)

```python
# src/logger.py
import logging
import os
from datetime import datetime
from typing import Any

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
        level = self.LOG_LEVELS.get(log_level.lower(), logging.INFO)
        self.logger.setLevel(level)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # File handler
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
        """Log debug message with context."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context."""
        self._log(logging.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal method with context data."""
        if kwargs:
            context_str = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} [{context_str}]"
        self.logger.log(level, message)
```

### Step 2: Create Error Handler Decorator (Day 1)

```python
# src/error_handler.py
import functools
import traceback
from typing import Any, Callable, TypeVar, cast, Optional

T = TypeVar('T')

def error_handler(logger: Optional[Any] = None, default_return: Any = None):
    """Decorator for consistent error handling."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
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

### Step 3: Integrate with ConfigManager and AssetManager (Day 2)

Update ConfigManager:

```python
# src/config_manager.py (additions)
from src.logger import DiwaliLogger
from src.error_handler import error_handler

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.json"):
        self.logger = DiwaliLogger("ConfigManager")
        # ... rest of init

    @error_handler(logger=None, default_return={})
    def load(self) -> None:
        """Load configuration with error handling."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"Loaded config from {self.config_path}")
        else:
            self.logger.warning(f"Config file not found: {self.config_path}")
```

Update AssetManager:

```python
# src/asset_manager.py (additions)
from src.logger import DiwaliLogger
from src.error_handler import error_handler

class AssetManager:
    def __init__(self, base_path="assets", config_manager=None):
        self.logger = DiwaliLogger("AssetManager")
        # ... rest of init

    @error_handler(logger=None, default_return=None)
    def get_image(self, relative_path: str, use_alpha: bool = True) -> pygame.Surface:
        """Load image with error handling."""
        # ... existing code
        self.logger.debug(f"Loading image: {relative_path}")
        # ...
```

### Step 4: Write Unit Tests (Day 2-3)

```python
# tests/test_logger.py
import unittest
import os
import tempfile
from src.logger import DiwaliLogger

class TestDiwaliLogger(unittest.TestCase):

    def setUp(self):
        """Create temp log directory."""
        self.log_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.log_dir)

    def test_logger_creates_log_file(self):
        """Test that logger creates log file."""
        logger = DiwaliLogger("test", log_dir=self.log_dir)
        logger.info("Test message")

        # Check log file was created
        log_files = os.listdir(self.log_dir)
        self.assertEqual(len(log_files), 1)
        self.assertTrue(log_files[0].startswith("test_"))

    def test_logger_levels(self):
        """Test different log levels."""
        logger = DiwaliLogger("test", log_dir=self.log_dir, log_level="debug")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        # Should not raise exceptions

    def test_logger_with_context(self):
        """Test logging with context data."""
        logger = DiwaliLogger("test", log_dir=self.log_dir)
        logger.info("Test message", key1="value1", key2="value2")
        # Should not raise exceptions


# tests/test_error_handler.py
import unittest
from src.error_handler import error_handler
from src.logger import DiwaliLogger

class TestErrorHandler(unittest.TestCase):

    def test_error_handler_catches_exception(self):
        """Test that decorator catches exceptions."""
        logger = DiwaliLogger("test", log_to_file=False)

        @error_handler(logger=logger, default_return=42)
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        self.assertEqual(result, 42)

    def test_error_handler_passes_through_success(self):
        """Test that decorator doesn't affect successful calls."""
        @error_handler(logger=None, default_return=None)
        def successful_function(x):
            return x * 2

        result = successful_function(21)
        self.assertEqual(result, 42)
```

### Step 5: Documentation (Day 3)

```markdown
# Logging and Error Handling

## DiwaliLogger Usage

```python
from src.logger import DiwaliLogger

logger = DiwaliLogger("MyComponent", log_level="debug")

logger.debug("Detailed info for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")

# With context
logger.info("Config loaded", path="/path/to/config", size=1024)
```

## Error Handler Decorator

```python
from src.error_handler import error_handler
from src.logger import DiwaliLogger

logger = DiwaliLogger("MyComponent")

@error_handler(logger=logger, default_return=None)
def load_asset(path):
    # If this raises an exception, it will be logged and None returned
    return pygame.image.load(path)
```

## Graceful Degradation Pattern

```python
@error_handler(logger=logger, default_return=default_surface)
def load_image_with_fallback(path):
    return pygame.image.load(path)
```
```

## Testing Checklist

- [ ] DiwaliLogger creates log files
- [ ] All log levels work correctly
- [ ] Context data is logged properly
- [ ] Error handler catches exceptions
- [ ] Error handler logs with context
- [ ] Error handler returns default values
- [ ] Successful calls pass through unmodified
- [ ] Integration with ConfigManager works
- [ ] Integration with AssetManager works

## Integration Points

**Requires:**
- Phase 1, Task 1 (ConfigManager) - Complete
- Phase 1, Task 2 (AssetManager) - Complete

**Coordinates with:**
- Phase 2, Task 1 (Testing Infrastructure) - Can run in parallel

**Provides:**
- Logging infrastructure for all future phases
- Error handling patterns for all components

## Success Criteria

✅ All unit tests pass
✅ ConfigManager and AssetManager use logging
✅ Error handling integrated into asset loading
✅ Log files created and formatted correctly
✅ Documentation complete with examples
✅ Ready for use in all subsequent phases
