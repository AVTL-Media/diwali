# Visual Component Render Methods Refactoring

## Overview

This task focuses on refactoring the rendering pipeline in the `VisualGenerator` class to use a layered approach for better organization and clarity.

## Current State

The current `render()` method contains a mix of concerns, handling different types of visual elements in a monolithic function.

## Target State

A structured rendering pipeline using a layered approach:

```python
def render(self, state, state_data, surface):
    # Create a copy of the input surface for rendering
    result = surface.copy()
    
    # Update screen size for floating objects
    self.screen_size = result.get_size()
    
    # Render layers in order of back-to-front
    self._render_background_layer(result)
    self._render_state_specific_layer(result, state, state_data)
    self._render_ethereal_outlines(result, state_data)
    self._render_floating_objects_layer(result)
    
    return result
```

## Implementation Plan

### 1. Create Layer-Specific Rendering Methods

Extract the following methods from the main render function:

- `_render_background_layer(surface)` - Render background image and base rangoli pattern
- `_render_state_specific_layer(surface, state, state_data)` - Render visuals specific to the current state
- `_render_ethereal_outlines(surface, state_data)` - Render ethereal outlines of detected persons
- `_render_floating_objects_layer(surface)` - Render all floating objects (diyas, rangolis)

### 2. Implement Fireworks Rate Limiting

Create a dedicated method for rendering fireworks with rate limiting:

- `_render_fireworks_with_rate_limiting(surface, state_data)` - Manage firework rendering frequency

### 3. Refactor Fireworks Rendering

Decompose the fireworks rendering into more focused methods:

- `_process_new_firework_origins(state_data)` - Handle the creation of new fireworks
- `_draw_firework_particles(surface)` - Render the actual firework particles

### 4. Refactor Ethereal Effects Rendering

Split the ethereal outline rendering into separate concerns:

- `_create_ethereal_surface(person_outline)` - Create the visual effect surface
- `_render_ethereal_surface(surface, ethereal_surface)` - Apply the effect to the target surface

## Testing Strategy

1. Take screenshots of the original rendering output for different states
2. Implement the refactored render methods
3. Compare screenshots before and after refactoring to ensure visual consistency
4. Check performance metrics to ensure no significant regressions

## Success Criteria

- Clearly separated rendering layers
- Improved code organization and readability
- Preserved visual output and functionality
- Enhanced maintainability for future visual effect additions