# Phase 4: Parallel Component Extraction Tasks

**Phase**: 4 - Component Decomposition
**Weeks**: 6-8
**Can Run in Parallel**: ✅ Yes - Up to 4 agents
**Dependencies**: Phase 3 (Event System & State Machine) MUST be complete

## Overview

Once the architecture (Events + State Machine) is in place, component extraction can happen in parallel. Each component is extracted independently and uses the established patterns.

**Maximum Parallelization**: 4 agents working simultaneously

---

## Task 4.1: Extract FireworksManager

**Agent Assignment**: Agent A
**Estimated Duration**: 3-4 days
**Can Run in Parallel**: ✅ Yes (with Tasks 4.2, 4.3, 4.4)
**Dependencies**: Phase 3 complete
**File**: `src/components/fireworks_manager.py`

### Overview

Extract fireworks particle system logic from VisualGenerator into a dedicated component.

### Implementation

```python
# src/components/fireworks_manager.py
from src.components.base import VisualComponent
from src.event_system import Event, EventType
import pygame
from typing import Dict, List, Tuple

class FireworksManager(VisualComponent):
    """Manages firework particle effects."""

    def __init__(self, config_manager, event_system):
        super().__init__(config_manager, event_system)
        self.particles: Dict[Tuple[int, int], List[Dict]] = {}
        self.start_times: Dict[Tuple[int, int], float] = {}
        self.max_fireworks = config_manager.get_int("fireworks.max_active", 5)

        # Subscribe to firework creation events
        self.event_system.subscribe(
            EventType.FIREWORK_CREATED,
            self._on_firework_created
        )

    def _on_firework_created(self, event: Event) -> None:
        """Handle firework creation event."""
        origin = event.data.get("origin")
        if origin:
            self.create_firework(origin)

    def create_firework(self, origin: Tuple[int, int]) -> None:
        """Create firework at origin."""
        # Implementation from VisualGenerator
        pass

    def update(self, dt: float) -> None:
        """Update firework particles."""
        self._update_particles(dt)
        self._cleanup_expired()
        self._limit_active()

    def render(self, surface: pygame.Surface) -> None:
        """Render fireworks."""
        for origin, particles in self.particles.items():
            for particle in particles:
                self._draw_particle(surface, particle)

    def _update_particles(self, dt: float) -> None:
        """Update particle physics."""
        pass

    def _cleanup_expired(self) -> None:
        """Remove expired fireworks."""
        pass

    def _limit_active(self) -> None:
        """Limit number of active fireworks."""
        pass
```

### Extraction Steps

1. **Day 1**: Create FireworksManager class with base structure
2. **Day 2**: Move fireworks logic from VisualGenerator
3. **Day 3**: Add event integration, write tests
4. **Day 4**: Visual parity testing, documentation

### Feature Flag

```json
{
  "experimental": {
    "components": {
      "use_fireworks_manager": false
    }
  }
}
```

### Testing

```python
# tests/test_fireworks_manager.py
class TestFireworksManager(DiwaliTestCase):
    def test_create_firework(self):
        """Test creating firework."""
        manager = FireworksManager(self.config_manager, self.event_system)
        manager.create_firework((400, 300))
        self.assertIn((400, 300), manager.particles)

    def test_event_integration(self):
        """Test event-based creation."""
        manager = FireworksManager(self.config_manager, self.event_system)
        event = Event(
            EventType.FIREWORK_CREATED,
            {"origin": (400, 300)},
            time.time()
        )
        self.event_system.publish(event)
        self.assertIn((400, 300), manager.particles)
```

### Success Criteria

✅ FireworksManager extracted
✅ Uses EventSystem for communication
✅ Visual output matches original
✅ Tests pass
✅ Feature flag works

---

## Task 4.2: Extract RangoliRenderer

**Agent Assignment**: Agent B
**Estimated Duration**: 3-4 days
**Can Run in Parallel**: ✅ Yes (with Tasks 4.1, 4.3, 4.4)
**Dependencies**: Phase 3 complete
**File**: `src/components/rangoli_renderer.py`

### Overview

Extract rangoli pattern rendering logic from VisualGenerator into a dedicated component.

### Implementation

```python
# src/components/rangoli_renderer.py
from src.components.base import VisualComponent
import pygame
from typing import Tuple

class RangoliRenderer(VisualComponent):
    """Handles rangoli pattern rendering."""

    def __init__(self, config_manager, event_system):
        super().__init__(config_manager, event_system)
        self.angle = 0
        self.color_cycle_hue = 0
        self.rotation_speed = config_manager.get_float(
            "rangoli.rotation_speed", 0.01
        )
        self.patterns = []
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load rangoli patterns."""
        pass

    def update(self, dt: float) -> None:
        """Update rangoli animation."""
        self._update_rotation(dt)
        self._update_color_cycling(dt)

    def render(
        self,
        surface: pygame.Surface,
        center: Tuple[int, int],
        alpha: int = 200
    ) -> None:
        """Render rangoli pattern."""
        pass

    def _update_rotation(self, dt: float) -> None:
        """Update rotation angle."""
        self.angle += self.rotation_speed

    def _update_color_cycling(self, dt: float) -> None:
        """Update color cycle."""
        self.color_cycle_hue += dt * 0.1
```

### Extraction Steps

1. **Day 1**: Create RangoliRenderer class
2. **Day 2**: Move rangoli logic from VisualGenerator
3. **Day 3**: Add pattern loading, write tests
4. **Day 4**: Visual parity testing, documentation

### Feature Flag

```json
{
  "experimental": {
    "components": {
      "use_rangoli_renderer": false
    }
  }
}
```

### Success Criteria

✅ RangoliRenderer extracted
✅ Animation works correctly
✅ Visual output matches original
✅ Tests pass

---

## Task 4.3: Extract EtherealEffects

**Agent Assignment**: Agent C
**Estimated Duration**: 2-3 days
**Can Run in Parallel**: ✅ Yes (with Tasks 4.1, 4.2, 4.4)
**Dependencies**: Phase 3 complete
**File**: `src/components/ethereal_effects.py`

### Overview

Extract person outline ethereal effects from VisualGenerator.

### Implementation

```python
# src/components/ethereal_effects.py
from src.components.base import VisualComponent
import pygame
import cv2

class EtherealEffects(VisualComponent):
    """Handles ethereal person outline effects."""

    def __init__(self, config_manager, event_system):
        super().__init__(config_manager, event_system)
        self.glow_color = (0, 255, 255)
        self.particles_enabled = config_manager.get_bool(
            "ethereal.particles_enabled", True
        )

    def update(self, dt: float) -> None:
        """Update ethereal effects."""
        pass

    def render(self, surface: pygame.Surface, person_outlines: List) -> None:
        """Render ethereal outlines."""
        for outline in person_outlines:
            ethereal_surface = self._create_ethereal_surface(outline)
            self._render_ethereal_surface(surface, ethereal_surface)

    def _create_ethereal_surface(self, outline) -> pygame.Surface:
        """Create glowing effect surface."""
        pass

    def _render_ethereal_surface(
        self,
        surface: pygame.Surface,
        ethereal: pygame.Surface
    ) -> None:
        """Apply ethereal effect to surface."""
        pass
```

### Extraction Steps

1. **Day 1**: Create EtherealEffects class
2. **Day 2**: Move person outline logic
3. **Day 3**: Write tests, documentation

### Success Criteria

✅ EtherealEffects extracted
✅ Visual output matches original
✅ Tests pass

---

## Task 4.4: Extract FloatingObjects

**Agent Assignment**: Agent D
**Estimated Duration**: 2-3 days
**Can Run in Parallel**: ✅ Yes (with Tasks 4.1, 4.2, 4.3)
**Dependencies**: Phase 3 complete
**File**: `src/components/floating_objects.py`

### Overview

Extract floating diyas and rangolis from VisualGenerator.

### Implementation

```python
# src/components/floating_objects.py
from src.components.base import VisualComponent
import pygame
from typing import List

class FloatingObject:
    """Base class for floating objects."""
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self, dt: float) -> None:
        """Update position."""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt


class FloatingObjects(VisualComponent):
    """Manages floating diyas and rangolis."""

    def __init__(self, config_manager, event_system, asset_manager):
        super().__init__(config_manager, event_system)
        self.asset_manager = asset_manager
        self.objects: List[FloatingObject] = []
        self.max_objects = config_manager.get_int("floating.max_objects", 10)

    def update(self, dt: float) -> None:
        """Update all floating objects."""
        for obj in self.objects:
            obj.update(dt)
        self._remove_offscreen()

    def render(self, surface: pygame.Surface) -> None:
        """Render floating objects."""
        for obj in self.objects:
            surface.blit(obj.image, (obj.x, obj.y))

    def _remove_offscreen(self) -> None:
        """Remove objects that are offscreen."""
        pass
```

### Extraction Steps

1. **Day 1**: Create FloatingObjects class
2. **Day 2**: Move floating object logic
3. **Day 3**: Write tests, documentation

### Success Criteria

✅ FloatingObjects extracted
✅ Animation works correctly
✅ Tests pass

---

## Task 4.5: Integration Testing

**Week**: 8
**Agent Assignment**: All agents collaborate
**Estimated Duration**: 3-5 days
**Can Run in Parallel**: ❌ No (requires all components extracted)
**Dependencies**: Tasks 4.1-4.4 complete

### Overview

Integrate all extracted components and verify system works as a whole.

### Integration Steps

1. **Day 1**: Enable all component feature flags
2. **Day 2**: Run visual regression tests
3. **Day 3**: Performance testing
4. **Day 4**: Bug fixes
5. **Day 5**: Documentation and cleanup

### Testing Checklist

- [ ] All components work together
- [ ] EventSystem routes events correctly
- [ ] State Machine transitions work
- [ ] Visual output matches original
- [ ] Performance is acceptable
- [ ] No memory leaks
- [ ] Feature flags can enable/disable components

### Success Criteria

✅ All components integrated
✅ Full system tests pass
✅ Visual output matches original
✅ Performance acceptable
✅ Ready for Phase 5 (Method Refactoring)

---

## Coordination Strategy

### Daily Standups

- Each agent reports progress
- Share blockers
- Coordinate on VisualGenerator modifications

### Conflict Resolution

If multiple agents need to modify VisualGenerator:
1. Create adapter methods first
2. Each agent works in separate branch
3. Merge in order: 4.1 → 4.2 → 4.3 → 4.4
4. Agent A coordinates merges

### Shared Resources

**VisualGenerator**: All agents will modify this
**EventSystem**: All components subscribe to events
**Config**: Each component has its own config section

### Communication

Use shared document to track:
- Which methods have been extracted
- Which methods are in progress
- Dependencies between components

## Success Criteria for Phase 4 Completion

✅ All 4 components extracted
✅ All components tested independently
✅ Integration testing complete
✅ Visual output unchanged
✅ Performance acceptable
✅ Documentation complete
✅ **Ready for Phase 5: Method Refactoring**
