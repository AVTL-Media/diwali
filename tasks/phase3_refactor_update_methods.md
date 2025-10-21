# Visual Component Update Methods Refactoring

## Overview

This task focuses on refactoring the monolithic `update()` method in the `VisualGenerator` class by decomposing it into smaller, focused methods following the Single Responsibility Principle.

## Current State

The current `update()` method handles multiple responsibilities in a single large function, making it difficult to maintain and test.

## Target State

A hierarchical structure of update methods, each responsible for a specific visual component:

```python
def update(self, dt, current_frame=None):
    # Update each visual component separately
    self._update_rangoli_animation(dt)
    self._update_ethereal_effects(current_frame)
    self._update_fireworks(dt)
    self._update_floating_objects(dt)
    self._increment_frame_counter()
```

## Implementation Plan

### 1. Decompose Update Method

Create the following methods:

- `_update_rangoli_animation(dt)` - Extract code related to rangoli rotation and color cycling
- `_update_ethereal_effects(current_frame)` - Extract code related to person outline effects
- `_update_fireworks(dt)` - Extract code related to firework particle physics

### 2. Further Decompose Fireworks Update

Break down the fireworks update into more manageable components:

- `_update_firework_particles(dt)` - Update particle positions and properties
- `_cleanup_expired_fireworks()` - Remove expired firework displays
- `_limit_active_fireworks()` - Ensure only a reasonable number of fireworks are active

### 3. Decompose Floating Objects Update

Create specialized methods for different floating object types:

- `_update_floating_objects(dt)` - Main method that delegates to specific object types
  - `_update_floating_diyas(dt)` - Update diya animations
  - `_update_floating_rangolis(dt)` - Update rangoli animations

### 4. Add Frame Counter Management

Create a dedicated method for frame counter management:

- `_increment_frame_counter()` - Encapsulate frame counting logic

## Testing Strategy

1. Record the state before and after the original update() method
2. Implement the refactored methods
3. Verify that the refactored code produces identical state changes
4. Verify that visual output remains unchanged

## Success Criteria

- Each method has a single responsibility
- Method names clearly indicate their purpose
- All original functionality is preserved
- Code is more maintainable and easier to understand