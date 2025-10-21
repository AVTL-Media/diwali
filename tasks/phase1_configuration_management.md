# Configuration Management Implementation

This document outlines the implementation plan for the Configuration Management System, which is Phase 1 of the Diwali Projection System improvements.

## Overview

The Configuration Management System will replace the current nested dictionary access pattern with a more robust, type-safe approach using dot notation for configuration paths.

## Timeline

- **Week 1**: ConfigManager class development and testing
- **Week 2**: Integration with existing codebase

## Technical Specifications

### ConfigManager Class

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

## Implementation Tasks

### 1. ConfigManager Development

- [ ] Create `src/config_manager.py` with the ConfigManager class
- [ ] Add schema validation using JSON Schema
- [ ] Write unit tests for all ConfigManager methods
- [ ] Document all methods with proper docstrings
- [ ] Add examples in docstrings for common usage patterns

### 2. Integration Plan

- [ ] Create adapter method to convert existing config dict to ConfigManager
- [ ] Update `visual_generator.py` to use ConfigManager
- [ ] Create default configuration file with all settings documented
- [ ] Update all configuration access patterns throughout the codebase
- [ ] Document migration path for future components

## Expected Outcomes

1. **Code Simplification**: Replace complex nested dictionary access with simple dot notation
2. **Type Safety**: Strong typing for configuration values with proper conversion
3. **Documentation**: Self-documenting configuration with schema validation
4. **Default Values**: Centralized management of default values

## Testing Strategy

1. Create unit tests for all ConfigManager methods
2. Test boundary conditions (empty config, missing paths, etc.)
3. Test type conversion edge cases (string to number, etc.)
4. Integration tests with real configuration files

## Compatibility Considerations

To ensure a smooth transition, consider implementing a compatibility layer that allows both old-style dict access and new ConfigManager access during the migration period.
