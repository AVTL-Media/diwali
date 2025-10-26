# Component Decomposition and Refactoring Implementation

⚠️ **REVISED PLAN UPDATE**: This is now **Phase 4** (Weeks 6-8), moved from original Phase 4 (Weeks 5-6).

**Critical Dependencies**: This phase now requires Phase 3 (Event System & State Machine) to be completed first.

This document outlines the implementation plan for Component Decomposition and Refactoring, which is **Phase 4** of the Diwali Projection System improvements.

## Overview

This phase focuses on breaking down the monolithic `VisualGenerator` class into smaller, more focused components that follow a consistent interface pattern.

**IMPORTANT**: Components should be designed to use the Event System and State Machine patterns established in Phase 3.

## Timeline - REVISED

- **Week 6**: Core Component Extraction (FireworksManager, RangoliRenderer)
- **Week 7**: Additional Component Extraction (EtherealEffects, FloatingObjects)
- **Week 8**: Integration Testing and Stabilization

## Technical Specifications

### Visual Component Architecture

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
```

### FireworksManager Component

```python
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
```

### RangoliRenderer Component

```python
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
```

## Implementation Tasks

### 1. Component Base Classes

- [ ] Create `src/components/visual_component.py` with the VisualComponent base class
- [ ] Define the standard component interface with update/render methods
- [ ] Add helper methods common to all components

### 2. Component Implementations

- [ ] Create `src/components/fireworks_manager.py` with FireworksManager class
- [ ] Create `src/components/rangoli_renderer.py` with RangoliRenderer class
- [ ] Create `src/components/ethereal_effects.py` for person outline effects
- [ ] Create `src/components/floating_objects.py` for floating diyas and rangolis
- [ ] Write unit tests for each component

### 3. Refactoring VisualGenerator

- [ ] Update VisualGenerator to use composition instead of inheritance
- [ ] Initialize and store component instances
- [ ] Delegate functionality to appropriate components
- [ ] Maintain backward compatibility with existing interfaces
- [ ] Update documentation to reflect new architecture

### 4. Integration Plan

- [ ] Update `main.py` to work with the new component architecture
- [ ] Ensure state transitions work correctly with components
- [ ] Create compatibility layers for existing code

## Expected Outcomes

1. **Cleaner Architecture**: Better separation of concerns with focused components
2. **Improved Testability**: Ability to test components in isolation
3. **Enhanced Maintainability**: Smaller, more focused classes and methods
4. **Better Extensibility**: Easier to add new visual effects

## Refactoring Strategy

### Component Extraction Process

1. Identify cohesive functionality sets in VisualGenerator
2. Extract each set into a separate component class
3. Move related methods and state variables to the component
4. Update VisualGenerator to use the component
5. Update tests to reflect the new structure

### Example Refactoring: Fireworks

#### Before Refactoring

```python
# In VisualGenerator
def _update_fireworks(self, dt):
    # Fireworks update logic
    
def _render_fireworks(self, surface, state_data):
    # Fireworks rendering logic
    
def _create_firework_particles(self, origin, count):
    # Create firework particles
```

#### After Refactoring

```python
# In FireworksManager
def update(self, dt):
    # Fireworks update logic
    
def render(self, surface):
    # Fireworks rendering logic
    
def create_firework(self, origin, count):
    # Create firework particles

# In VisualGenerator
def _update_fireworks(self, dt):
    self.fireworks_manager.update(dt)
    
def _render_fireworks(self, surface, state_data):
    if "firework_origins" in state_data:
        for origin in state_data["firework_origins"]:
            self.fireworks_manager.create_firework(origin)
    self.fireworks_manager.render(surface)
```

## Dependencies and Requirements

- Depends on ConfigManager from Phase 1
- Depends on Logger and error handling from Phase 2
- Requires understanding of the existing VisualGenerator implementation
