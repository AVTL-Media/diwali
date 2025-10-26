# Visual Component Update Methods Refactoring

⚠️ **REVISED PLAN UPDATE**: This is now part of **Phase 5** (Week 9), moved from original Phase 3 (Week 4).

**Critical Change**: This refactoring now operates on **already extracted components** from Phase 4, not the monolithic VisualGenerator.

## Overview

This task focuses on refactoring update methods in the **extracted component classes** (FireworksManager, RangoliRenderer, etc.) by applying the Single Responsibility Principle.

## Current State (After Phase 4)

After Phase 4, we have extracted components, but their internal methods may still be large and could benefit from further decomposition.

## Target State

Each extracted component has clean, focused update methods:

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