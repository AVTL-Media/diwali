# Phase 5: Parallel Method Refactoring Tasks

**Phase**: 5 - Method Refactoring
**Week**: 9
**Can Run in Parallel**: ✅ Yes - Up to 4 agents
**Dependencies**: Phase 4 (Component Extraction) MUST be complete

## Overview

Now that components are extracted, refine their internal methods. Each component can be refactored independently in parallel.

**Maximum Parallelization**: 4 agents working simultaneously

---

## Task 5.1: Refactor FireworksManager Methods

**Agent Assignment**: Agent A
**Estimated Duration**: 2 days
**Can Run in Parallel**: ✅ Yes (with Tasks 5.2, 5.3, 5.4)
**Dependencies**: Task 4.1 complete
**File**: `src/components/fireworks_manager.py`

### Goal

Break down large methods in FireworksManager into smaller, focused functions.

### Current Issues

- `update()` method does too much
- Particle physics logic is monolithic
- Rendering has mixed concerns

### Refactoring Plan

#### Before

```python
def update(self, dt: float) -> None:
    """Update all firework particles."""
    # 100+ lines of code doing everything
    for origin, particles in list(self.particles.items()):
        for particle in particles:
            # Update position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 9.8 * dt  # Gravity
            # Update color
            # Update lifetime
            # etc...
        # Cleanup logic
        # Rate limiting logic
```

#### After

```python
def update(self, dt: float) -> None:
    """Update all firework particles."""
    self._update_particle_physics(dt)
    self._update_particle_colors(dt)
    self._cleanup_expired_particles()
    self._enforce_rate_limits()

def _update_particle_physics(self, dt: float) -> None:
    """Update positions and velocities."""
    for particles in self.particles.values():
        for particle in particles:
            self._apply_gravity(particle, dt)
            self._apply_air_resistance(particle, dt)
            self._update_position(particle, dt)

def _apply_gravity(self, particle: Dict, dt: float) -> None:
    """Apply gravity to particle."""
    particle['vy'] += self.gravity * dt

def _apply_air_resistance(self, particle: Dict, dt: float) -> None:
    """Apply air resistance to particle."""
    particle['vx'] *= 0.99
    particle['vy'] *= 0.99

def _update_position(self, particle: Dict, dt: float) -> None:
    """Update particle position."""
    particle['x'] += particle['vx'] * dt
    particle['y'] += particle['vy'] * dt
```

### Checklist

- [ ] Extract `_update_particle_physics()`
- [ ] Extract `_apply_gravity()`
- [ ] Extract `_apply_air_resistance()`
- [ ] Extract `_update_position()`
- [ ] Extract `_update_particle_colors()`
- [ ] Extract `_cleanup_expired_particles()`
- [ ] Extract `_enforce_rate_limits()`
- [ ] Update tests
- [ ] Verify no behavioral changes

### Success Criteria

✅ No method longer than 30 lines
✅ Each method has single responsibility
✅ All tests still pass
✅ Visual output unchanged

---

## Task 5.2: Refactor RangoliRenderer Methods

**Agent Assignment**: Agent B
**Estimated Duration**: 2 days
**Can Run in Parallel**: ✅ Yes (with Tasks 5.1, 5.3, 5.4)
**Dependencies**: Task 4.2 complete
**File**: `src/components/rangoli_renderer.py`

### Goal

Simplify rangoli rendering pipeline.

### Refactoring Plan

#### Before

```python
def render(self, surface, center, alpha=200):
    """Render rangoli - 80+ lines."""
    # Create surface
    # Apply rotation
    # Apply colors
    # Apply blend modes
    # Handle psychedelic effects
    # Blit to target
```

#### After

```python
def render(self, surface, center, alpha=200):
    """Render rangoli pattern."""
    rangoli_surface = self._create_rangoli_surface()
    rangoli_surface = self._apply_rotation(rangoli_surface)
    rangoli_surface = self._apply_colors(rangoli_surface)

    if self.psychedelic_mode:
        rangoli_surface = self._apply_psychedelic_effects(rangoli_surface)

    self._blit_with_alpha(surface, rangoli_surface, center, alpha)

def _create_rangoli_surface(self) -> pygame.Surface:
    """Create base rangoli surface."""
    pass

def _apply_rotation(self, surface: pygame.Surface) -> pygame.Surface:
    """Apply rotation transformation."""
    pass

def _apply_colors(self, surface: pygame.Surface) -> pygame.Surface:
    """Apply color transformations."""
    pass

def _apply_psychedelic_effects(self, surface: pygame.Surface) -> pygame.Surface:
    """Apply psychedelic visual effects."""
    pass
```

### Checklist

- [ ] Extract surface creation
- [ ] Extract rotation logic
- [ ] Extract color application
- [ ] Extract psychedelic effects
- [ ] Extract blending logic
- [ ] Update tests
- [ ] Verify visual output

### Success Criteria

✅ Rendering pipeline clear and layered
✅ Each method has single responsibility
✅ Tests pass
✅ Visual output unchanged

---

## Task 5.3: Refactor EtherealEffects Methods

**Agent Assignment**: Agent C
**Estimated Duration**: 1-2 days
**Can Run in Parallel**: ✅ Yes (with Tasks 5.1, 5.2, 5.4)
**Dependencies**: Task 4.3 complete
**File**: `src/components/ethereal_effects.py`

### Goal

Simplify ethereal outline rendering.

### Refactoring Plan

Extract glow effect creation into focused methods:

- `_create_outline_mask()`
- `_apply_glow_effect()`
- `_add_particles()`
- `_blend_with_target()`

### Checklist

- [ ] Extract outline mask creation
- [ ] Extract glow effect
- [ ] Extract particle effects
- [ ] Extract blending
- [ ] Update tests

### Success Criteria

✅ Clear rendering pipeline
✅ Tests pass
✅ Visual output unchanged

---

## Task 5.4: Refactor FloatingObjects Methods

**Agent Assignment**: Agent D
**Estimated Duration**: 1-2 days
**Can Run in Parallel**: ✅ Yes (with Tasks 5.1, 5.2, 5.3)
**Dependencies**: Task 4.4 complete
**File**: `src/components/floating_objects.py`

### Goal

Simplify floating object management.

### Refactoring Plan

Extract object lifecycle management:

- `_spawn_new_objects()`
- `_update_physics()`
- `_apply_wobble_effect()`
- `_remove_offscreen()`
- `_limit_object_count()`

### Checklist

- [ ] Extract spawning logic
- [ ] Extract physics updates
- [ ] Extract wobble effects
- [ ] Extract cleanup logic
- [ ] Update tests

### Success Criteria

✅ Clear object lifecycle
✅ Tests pass
✅ Visual output unchanged

---

## Coordination

### Independence

These tasks are highly independent because:
- Each agent works on different component
- No shared files modified
- No integration needed until all complete

### Code Review

After individual tasks complete:
1. Self-review for method length (<30 lines)
2. Peer review for clarity
3. Run full test suite
4. Visual regression testing

### Communication

- Daily progress updates
- Share patterns that work well
- Coordinate on testing approach

## Success Criteria for Phase 5 Completion

✅ All 4 components refactored
✅ Average method length < 30 lines
✅ No methods > 50 lines
✅ Single responsibility principle applied
✅ All tests pass
✅ Visual output unchanged
✅ Code more readable and maintainable
✅ **Ready for Phase 6: Performance Optimization**
