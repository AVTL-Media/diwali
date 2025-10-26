# Phase 1, Task 1: ConfigManager Implementation

**Phase**: 1 - Foundation
**Week**: 1
**Agent Assignment**: Agent A
**Can Run in Parallel**: ✅ Yes (with Task 2: AssetManager)
**Dependencies**: None
**Estimated Duration**: 3-4 days

## Overview

Implement the ConfigManager class to replace nested dictionary access with type-safe dot notation.

## Deliverables

1. `src/config_manager.py` - ConfigManager class implementation
2. Unit tests in `tests/test_config_manager.py`
3. Documentation and examples

## Implementation Steps

### Step 1: Create ConfigManager Class (Day 1)

```python
# src/config_manager.py
from typing import Any, Dict, List, Optional, TypeVar, cast
import json
from pathlib import Path

T = TypeVar('T')

class ConfigManager:
    """Centralized configuration management."""

    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")

    def get(self, path: str, default: Optional[T] = None) -> T:
        """Get value by dot-notation path."""
        keys = path.split('.')
        value = self.config

        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return cast(T, default)
            value = value[key]

        return cast(T, value) if value is not None else cast(T, default)

    def get_float(self, path: str, default: float = 0.0) -> float:
        """Get float value with type conversion."""
        value = self.get(path, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_int(self, path: str, default: int = 0) -> int:
        """Get int value with type conversion."""
        value = self.get(path, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, path: str, default: bool = False) -> bool:
        """Get bool value with type conversion."""
        value = self.get(path, default)
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)

    def get_list(self, path: str, default: Optional[List] = None) -> List:
        """Get list value."""
        value = self.get(path, default or [])
        return value if isinstance(value, list) else [value]

    def set(self, path: str, value: Any) -> None:
        """Set value by dot-notation path."""
        keys = path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")
```

### Step 2: Write Unit Tests (Day 2)

```python
# tests/test_config_manager.py
import unittest
import tempfile
import json
import os
from src.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        """Create temporary config file."""
        self.config_data = {
            "camera": {
                "resolution": [640, 480],
                "fps": 30
            },
            "motion_detection": {
                "threshold": 25,
                "enabled": True
            }
        }

        fd, self.config_path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        """Remove temporary config file."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_get_nested_value(self):
        """Test retrieving nested config value."""
        manager = ConfigManager(self.config_path)
        self.assertEqual(manager.get("camera.fps"), 30)

    def test_get_with_default(self):
        """Test default value for missing path."""
        manager = ConfigManager(self.config_path)
        self.assertEqual(manager.get("nonexistent.path", 42), 42)

    def test_get_float(self):
        """Test float type conversion."""
        manager = ConfigManager(self.config_path)
        self.assertEqual(manager.get_float("motion_detection.threshold"), 25.0)

    def test_get_int(self):
        """Test int type conversion."""
        manager = ConfigManager(self.config_path)
        self.assertEqual(manager.get_int("camera.fps"), 30)

    def test_get_bool(self):
        """Test bool type conversion."""
        manager = ConfigManager(self.config_path)
        self.assertTrue(manager.get_bool("motion_detection.enabled"))

    def test_get_list(self):
        """Test list retrieval."""
        manager = ConfigManager(self.config_path)
        self.assertEqual(manager.get_list("camera.resolution"), [640, 480])

    def test_set_value(self):
        """Test setting config value."""
        manager = ConfigManager(self.config_path)
        manager.set("new.nested.value", 100)
        self.assertEqual(manager.get("new.nested.value"), 100)

    def test_save_and_load(self):
        """Test saving and reloading config."""
        manager = ConfigManager(self.config_path)
        manager.set("test.value", 123)
        manager.save()

        manager2 = ConfigManager(self.config_path)
        self.assertEqual(manager2.get("test.value"), 123)
```

### Step 3: Create ConfigAdapter (Day 3)

For backward compatibility during migration:

```python
# src/config_adapter.py
class ConfigAdapter:
    """Adapter for gradual migration from dict to ConfigManager."""

    def __init__(self, config_manager, legacy_dict, use_new=True):
        self.config_manager = config_manager
        self.legacy_dict = legacy_dict
        self.use_new = use_new

    def get(self, path, default=None):
        """Get config value using new or old system."""
        if self.use_new:
            return self.config_manager.get(path, default)
        else:
            # Legacy nested dict access
            keys = path.split('.')
            value = self.legacy_dict
            for key in keys:
                if not isinstance(value, dict) or key not in value:
                    return default
                value = value[key]
            return value
```

### Step 4: Documentation (Day 4)

Create documentation with examples:

```markdown
# ConfigManager Usage

## Basic Usage

```python
from src.config_manager import ConfigManager

config = ConfigManager("config/settings.json")

# Get values with dot notation
fps = config.get_int("camera.fps", 30)
resolution = config.get_list("camera.resolution", [640, 480])
enabled = config.get_bool("motion_detection.enabled", True)

# Set values
config.set("camera.fps", 60)
config.save()
```

## Migration from Legacy Dict

```python
# Old way
fps = config["camera"]["fps"]

# New way
fps = config_manager.get("camera.fps", 30)
```
```

## Testing Checklist

- [ ] ConfigManager loads JSON files correctly
- [ ] Dot notation access works for nested values
- [ ] Type-specific getters (int, float, bool, list) work correctly
- [ ] Default values returned for missing paths
- [ ] Set operations create nested structure correctly
- [ ] Save operation persists changes
- [ ] Empty config file handled gracefully
- [ ] Malformed JSON handled gracefully

## Integration Points

**Coordinates with:**
- Phase 1, Task 2 (AssetManager) - Will use ConfigManager
- Phase 1, Task 3 (Error Handling) - Will add error handling to ConfigManager

**Blocks:**
- Phase 2 testing tasks need this complete

## Success Criteria

✅ All unit tests pass
✅ ConfigManager can load existing config/settings.json
✅ Type conversions work correctly
✅ Documentation complete with examples
✅ Ready for integration in main.py
