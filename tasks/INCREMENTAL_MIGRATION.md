# Incremental Migration Strategy

## Overview

This document outlines the strategy for incrementally migrating the Diwali Projection System to the new architecture while maintaining a working application at all times.

## Core Principles

1. **Always Ship**: Every commit should result in a working application
2. **Feature Flags**: Use configuration to toggle between old and new implementations
3. **Parallel Systems**: Run old and new systems side-by-side during transition
4. **Gradual Cutover**: Switch components one at a time, not all at once
5. **Easy Rollback**: Always able to revert to previous working state

## Feature Flag System

### Configuration Structure

Add to `config/settings.json`:

```json
{
  "experimental": {
    "use_new_config_manager": true,
    "use_new_asset_manager": true,
    "use_event_system": false,
    "use_state_machine": false,
    "use_component_architecture": false,
    "use_threaded_camera": false,
    "use_threaded_detection": false,
    "components": {
      "use_fireworks_manager": false,
      "use_rangoli_renderer": false,
      "use_ethereal_effects": false,
      "use_floating_objects": false
    }
  },
  "debug": {
    "log_config_access": false,
    "log_events": false,
    "log_state_transitions": false,
    "compare_old_new_output": false
  }
}
```

### Feature Flag Helper

```python
class FeatureFlags:
    """Helper for checking experimental features."""

    def __init__(self, config_manager):
        self.config = config_manager

    def is_enabled(self, feature_path: str) -> bool:
        """Check if a feature is enabled."""
        full_path = f"experimental.{feature_path}"
        return self.config.get_bool(full_path, False)

    def use_new_config(self) -> bool:
        return self.is_enabled("use_new_config_manager")

    def use_event_system(self) -> bool:
        return self.is_enabled("use_event_system")

    def use_component(self, component_name: str) -> bool:
        return self.is_enabled(f"components.use_{component_name}")
```

## Phase-by-Phase Migration

### Phase 1: Foundation (Weeks 1-2)

**Migration Strategy**: Adapter pattern for backward compatibility

#### ConfigManager Migration

**Step 1**: Create ConfigAdapter that supports both old and new:

```python
class ConfigAdapter:
    """Adapter allowing gradual migration from dict to ConfigManager."""

    def __init__(self, config_manager, legacy_dict, feature_flags):
        self.config_manager = config_manager
        self.legacy_dict = legacy_dict
        self.feature_flags = feature_flags

    def get(self, path, default=None):
        """Get config value using new or old system."""
        if self.feature_flags.use_new_config():
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

**Step 2**: Replace all direct config dict access with adapter:

```python
# Old code:
rotation_speed = config["rangoli"]["rotation_speed"]

# New code:
rotation_speed = config_adapter.get("rangoli.rotation_speed", 0.01)
```

**Step 3**: Enable new system via config:

```json
{"experimental": {"use_new_config_manager": true}}
```

**Step 4**: Monitor for issues, rollback if needed

**Step 5**: Remove legacy code once stable

#### AssetManager Migration

Similar adapter pattern:

```python
class AssetAdapter:
    """Adapter for gradual asset management migration."""

    def __init__(self, asset_manager, feature_flags):
        self.asset_manager = asset_manager
        self.feature_flags = feature_flags
        self.legacy_cache = {}

    def get_image(self, path):
        if self.feature_flags.is_enabled("use_new_asset_manager"):
            return self.asset_manager.get_image(path)
        else:
            # Legacy direct loading
            if path not in self.legacy_cache:
                self.legacy_cache[path] = pygame.image.load(path).convert_alpha()
            return self.legacy_cache[path]
```

**Rollback**: Set `use_new_config_manager: false` and `use_new_asset_manager: false`

### Phase 2: Testing Foundation (Weeks 2-3)

**Migration Strategy**: No runtime changes, pure addition

- Tests don't affect production code
- CI/CD runs in parallel with development
- No feature flags needed
- No rollback concerns

**Risk**: Minimal

### Phase 3: Architectural Patterns (Weeks 4-5)

**Migration Strategy**: Parallel execution with comparison

#### Event System Migration (Week 4)

**Step 1**: Implement EventSystem but don't use it yet

**Step 2**: Add event publishing alongside existing direct calls:

```python
# Old code still works:
self.scene_manager.on_motion_detected(position)

# New code runs in parallel:
if self.feature_flags.use_event_system():
    event = Event(EventType.MOTION_DETECTED, {"position": position})
    self.event_system.publish(event)
```

**Step 3**: SceneManager responds to both old calls and events:

```python
def on_motion_detected(self, position):
    """Legacy direct call handler."""
    self._handle_motion(position)

def _on_motion_event(self, event):
    """Event system handler."""
    self._handle_motion(event.data["position"])

def _handle_motion(self, position):
    """Actual logic (shared by both paths)."""
    # ... implementation
```

**Step 4**: Enable event system, disable old calls:

```json
{"experimental": {"use_event_system": true}}
```

**Step 5**: Compare behavior with debug logging:

```python
if self.config.get_bool("debug.compare_old_new_output"):
    self.logger.info("Old path result: ..., New path result: ...")
```

**Step 6**: Remove old code paths once validated

**Rollback**: Set `use_event_system: false`

#### State Machine Migration (Week 5)

**Step 1**: Implement State classes

**Step 2**: SceneManager runs both old and new state management:

```python
class SceneManager:
    def update(self, dt):
        # Old state management
        if not self.feature_flags.is_enabled("use_state_machine"):
            self._update_old_way(dt)
        else:
            # New state machine
            self.current_state.update(dt)
```

**Step 3**: Enable state machine, validate transitions:

```json
{"experimental": {"use_state_machine": true}}
{"debug": {"log_state_transitions": true}}
```

**Step 4**: Compare state transitions between old and new

**Rollback**: Set `use_state_machine: false`

### Phase 4: Component Decomposition (Weeks 6-8)

**Migration Strategy**: One component at a time with visual parity testing

#### Component Extraction Pattern

For each component (FireworksManager, RangoliRenderer, etc.):

**Step 1**: Extract component but don't use it yet

**Step 2**: Add component alongside old code:

```python
class VisualGenerator:
    def __init__(self, config, feature_flags):
        # Old code
        self.firework_particles = {}

        # New component
        self.fireworks_manager = FireworksManager(config)
        self.feature_flags = feature_flags
```

**Step 3**: Call both old and new, compare output:

```python
def _render_fireworks(self, surface):
    if self.feature_flags.use_component("fireworks_manager"):
        # New component
        self.fireworks_manager.render(surface)
    else:
        # Old inline code
        self._render_fireworks_old_way(surface)

    # Optional: Compare outputs
    if self.config.get_bool("debug.compare_old_new_output"):
        self._compare_fireworks_output()
```

**Step 4**: Take screenshots for visual comparison:

```python
# Test script
def test_visual_parity():
    # Render with old system
    old_output = render_with_flags({"use_fireworks_manager": False})

    # Render with new system
    new_output = render_with_flags({"use_fireworks_manager": True})

    # Compare pixel-by-pixel
    diff = compute_image_diff(old_output, new_output)
    assert diff < threshold, f"Visual difference: {diff}"
```

**Step 5**: Enable component:

```json
{
  "experimental": {
    "components": {
      "use_fireworks_manager": true
    }
  }
}
```

**Step 6**: Monitor in production-like testing

**Step 7**: Remove old code once stable

**Rollback**: Set `use_fireworks_manager: false`

#### Component Migration Order

1. **FireworksManager** (Week 6) - Complex but isolated
2. **RangoliRenderer** (Week 6) - Medium complexity
3. **EtherealEffects** (Week 7) - Simple extraction
4. **FloatingObjects** (Week 7) - Simple extraction

Extract one at a time, validate, then move to next.

### Phase 5: Method Refactoring (Week 9)

**Migration Strategy**: Internal changes only

- Refactoring within already-extracted components
- No external interface changes
- Tests verify behavior unchanged
- No feature flags needed

**Risk**: Low (covered by tests)

### Phase 6: Performance & Concurrency (Weeks 10-11)

**Migration Strategy**: Opt-in threading with fallback

#### Threaded Camera (Week 10-11)

**Step 1**: Implement ThreadedCameraInput

**Step 2**: Use adapter to switch between implementations:

```python
class CameraAdapter:
    def __init__(self, config, feature_flags):
        if feature_flags.is_enabled("use_threaded_camera"):
            self.camera = ThreadedCameraInput(config)
        else:
            self.camera = CameraInput(config)

    def read(self):
        return self.camera.read()
```

**Step 3**: Enable threading:

```json
{"experimental": {"use_threaded_camera": true}}
```

**Step 4**: Monitor frame rates and stability

**Rollback**: Set `use_threaded_camera: false`

## Rollback Procedures

### Immediate Rollback (Production Issue)

1. Edit `config/settings.json`
2. Set problematic feature flag to `false`
3. Restart application
4. Verify issue resolved

### Code Rollback (Git)

1. Identify last working commit
2. `git revert <commit-hash>` or `git reset --hard <commit-hash>`
3. Push to branch
4. Deploy

### Partial Rollback

Disable specific components while keeping others:

```json
{
  "experimental": {
    "use_event_system": true,        // Keep working
    "use_state_machine": true,       // Keep working
    "components": {
      "use_fireworks_manager": false, // Rollback this one
      "use_rangoli_renderer": true    // Keep this one
    }
  }
}
```

## Testing Strategy During Migration

### Parallel Testing

For each phase with feature flags:

1. Run test suite with old system (`flag: false`)
2. Run test suite with new system (`flag: true`)
3. Both must pass before proceeding

### Visual Regression Testing

```python
def test_visual_regression():
    """Ensure new code produces same visual output."""
    test_scenarios = [
        "idle_state",
        "fireworks_burst",
        "rangoli_animation",
        "person_detection"
    ]

    for scenario in test_scenarios:
        old_output = render_scenario(scenario, use_new=False)
        new_output = render_scenario(scenario, use_new=True)

        # Allow small differences due to timing
        assert visual_similarity(old_output, new_output) > 0.95
```

### Performance Regression Testing

```python
def test_performance_regression():
    """Ensure new code doesn't hurt performance."""
    old_fps = measure_fps(duration=30, use_new=False)
    new_fps = measure_fps(duration=30, use_new=True)

    # New system should be at least 90% as fast
    assert new_fps >= old_fps * 0.9
```

## Monitoring During Migration

### Metrics to Track

1. **Frame Rate**: Should not degrade
2. **Memory Usage**: Should stay stable or improve
3. **Error Rate**: Should not increase
4. **Visual Output**: Should match previous version

### Logging Strategy

```python
# Log all feature flag usage
if self.feature_flags.is_enabled("use_new_feature"):
    self.logger.info("Using new feature: use_new_feature")

# Log comparison results
if self.config.get_bool("debug.compare_old_new_output"):
    self.logger.info(f"Old: {old_result}, New: {new_result}, Match: {match}")
```

## Communication Plan

### Commit Messages

Use clear commit messages indicating migration phase:

```
[Phase 1] Add ConfigManager with adapter for backward compatibility
[Phase 3] Implement EventSystem (disabled by default)
[Phase 4] Extract FireworksManager (feature flag: use_fireworks_manager)
[Rollback] Disable use_fireworks_manager due to rendering issue
```

### Documentation Updates

After each component migration:
1. Update CLAUDE.md with new architecture
2. Document feature flags in README
3. Add migration notes to CHANGELOG

## Success Criteria

A migration phase is successful when:

✅ All tests pass with feature flag enabled
✅ Visual output matches previous version (>95% similarity)
✅ Performance is maintained or improved
✅ No new errors or crashes
✅ Can run for 1 hour without issues
✅ Easy rollback via feature flag

## Conclusion

This incremental migration strategy ensures:

1. **No Big Bang**: Changes deployed gradually
2. **Always Working**: Application functional throughout
3. **Easy Rollback**: Single config change reverts to old system
4. **Validated Changes**: Each step tested before proceeding
5. **Low Risk**: Parallel systems allow comparison and validation

By following this strategy, the 11-week refactoring becomes manageable and safe rather than risky and chaotic.
