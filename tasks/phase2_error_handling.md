# Error Handling Framework Implementation

This document outlines the implementation plan for the Error Handling Framework, which is Phase 2 of the Diwali Projection System improvements.

## Overview

The Error Handling Framework will provide consistent error handling and logging across the codebase, improving robustness and debuggability of the application.

## Timeline

- **Week 3**: Development and integration of error handling components

## Technical Specifications

### DiwaliLogger Class

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

### Error Handler Decorator

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

## Implementation Tasks

### 1. Logger Development

- [ ] Create `src/logger.py` with the DiwaliLogger class
- [ ] Write unit tests for all logger methods
- [ ] Create configuration options for log levels in settings.json
- [ ] Implement log rotation for long-running sessions

### 2. Error Handling Implementation

- [ ] Create `src/error_handler.py` with the error_handler decorator
- [ ] Write unit tests for the decorator with various scenarios
- [ ] Create examples of usage patterns in documentation

### 3. Integration Plan

- [ ] Initialize logger in main.py and pass to all major components
- [ ] Apply error handling to critical functions:
  - [ ] Asset loading functions
  - [ ] Configuration access
  - [ ] Camera and audio processing
  - [ ] Event handling loops
- [ ] Implement graceful degradation for common failure scenarios:
  - [ ] Missing assets
  - [ ] Camera unavailable
  - [ ] Audio system failure

## Expected Outcomes

1. **Consistent Error Handling**: All errors handled in a consistent manner
2. **Improved Debugging**: Detailed logs with contextual information
3. **Graceful Degradation**: Application continues to function even when components fail
4. **Centralized Logging**: Single source of truth for application status

## Testing Strategy

1. Create unit tests for logger and error handler
2. Test various error scenarios to ensure proper handling
3. Verify log file creation and format
4. Test graceful degradation paths

## Example Usage Patterns

### Asset Loading with Error Handling

```python
@error_handler(logger=self.logger, default_return=default_image)
def load_image(self, path):
    """Load an image with error handling."""
    return pygame.image.load(path).convert_alpha()
```

### Graceful Degradation Example

```python
def detect_person(self, frame):
    """Detect person in frame with fallback."""
    try:
        # Attempt advanced detection
        return self.detector.detect(frame)
    except Exception as e:
        self.logger.error(f"Person detection failed: {str(e)}")
        # Fall back to simple detection
        return self.fallback_detector.detect(frame)
```
