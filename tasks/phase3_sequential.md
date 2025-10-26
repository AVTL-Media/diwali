# Phase 3: Sequential Architecture Tasks

**Phase**: 3 - Architectural Patterns
**Weeks**: 4-5
**Can Run in Parallel**: ❌ No - Sequential dependency
**Dependencies**: Phase 1 and Phase 2 must be complete

## Overview

Phase 3 tasks MUST be done sequentially because the State Machine (Week 5) depends on the Event System (Week 4) being complete.

**Critical Path Warning**: This is the bottleneck in the schedule. Only 1 agent can work effectively during this phase.

---

## Task 3.1: Event System Implementation

**Week**: 4
**Agent Assignment**: Agent A (experienced with pub-sub patterns)
**Can Run in Parallel**: ❌ No
**Dependencies**: None (from Phase 3)
**Blocks**: Task 3.2 (State Machine) cannot start until this completes
**Estimated Duration**: 5 days

### Deliverables

1. `src/event_system.py` - EventSystem, Event, EventType classes
2. Integration with existing detectors
3. Event logging/debugging tools
4. Unit tests
5. Documentation

### Implementation Overview

```python
# src/event_system.py
from enum import Enum, auto
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import time

class EventType(Enum):
    """Event types."""
    MOTION_DETECTED = auto()
    GESTURE_RECOGNIZED = auto()
    AUDIO_PEAK = auto()
    STATE_CHANGED = auto()
    FIREWORK_CREATED = auto()

@dataclass
class Event:
    """Event data container."""
    type: EventType
    data: Dict[str, Any]
    timestamp: float

class EventSystem:
    """Centralized event system."""

    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe from event type."""
        if event_type in self.subscribers:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """Publish event to subscribers."""
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
```

### Integration Steps

1. **Day 1-2**: Implement EventSystem core
2. **Day 3**: Integrate with MotionDetector, AudioDetector
3. **Day 4**: Add event logging/debugging
4. **Day 5**: Write tests, documentation

### Feature Flag

```json
{
  "experimental": {
    "use_event_system": false
  }
}
```

### Testing Checklist

- [ ] EventSystem created
- [ ] Subscribe/unsubscribe works
- [ ] Events published correctly
- [ ] Error handling for bad handlers
- [ ] Integration with detectors
- [ ] Feature flag toggling works
- [ ] Documentation complete

### Success Criteria

✅ EventSystem fully implemented
✅ Integrated with at least 2 detectors
✅ Tests pass
✅ Can be enabled via feature flag
✅ Ready for State Machine to use

**⚠️ BLOCKS Phase 3, Task 3.2 - Must complete before State Machine starts**

---

## Task 3.2: State Machine Implementation

**Week**: 5
**Agent Assignment**: Agent A (same agent as Task 3.1 for continuity)
**Can Run in Parallel**: ❌ No
**Dependencies**: Task 3.1 (Event System) MUST be complete
**Blocks**: Phase 4 (Component Extraction) cannot start until this completes
**Estimated Duration**: 5 days

### Why This Depends on Event System

The State Machine needs to:
- Publish STATE_CHANGED events
- Subscribe to MOTION_DETECTED, AUDIO_PEAK, etc.
- Use EventSystem for communication

### Deliverables

1. `src/state_machine.py` - State base class and concrete states
2. Refactored SceneManager to use State Machine
3. State transition diagram
4. Unit tests
5. Documentation

### Implementation Overview

```python
# src/state_machine.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.event_system import Event, EventType, EventSystem

class State(ABC):
    """Base class for application states."""

    def __init__(self, scene_manager, event_system: EventSystem):
        self.scene_manager = scene_manager
        self.event_system = event_system

    @abstractmethod
    def enter(self) -> None:
        """Called when entering state."""
        pass

    @abstractmethod
    def exit(self) -> None:
        """Called when exiting state."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state."""
        pass

    def transition_to(self, new_state_name: str) -> None:
        """Transition to new state."""
        self.scene_manager.change_state(new_state_name)


class IdleState(State):
    """Idle state waiting for interaction."""

    def enter(self) -> None:
        print("Entering idle state")
        self.timer = 0.0

    def exit(self) -> None:
        print("Exiting idle state")

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer > 30.0:  # Timeout
            self.transition_to("attract")

    def handle_event(self, event: Event) -> None:
        """Handle events in idle state."""
        if event.type == EventType.MOTION_DETECTED:
            self.transition_to("interactive")

# Additional states: AttractState, InteractiveState, FireworksState, etc.
```

### Integration Steps

1. **Day 1-2**: Implement State base class and concrete states
2. **Day 3**: Refactor SceneManager to use states
3. **Day 4**: Integrate with EventSystem
4. **Day 5**: Write tests, create state diagram, documentation

### Feature Flag

```json
{
  "experimental": {
    "use_state_machine": false
  }
}
```

### Testing Checklist

- [ ] State base class implemented
- [ ] All concrete states implemented
- [ ] State transitions work
- [ ] Event handling works
- [ ] SceneManager refactored
- [ ] State diagram created
- [ ] Feature flag toggling works
- [ ] Documentation complete

### Success Criteria

✅ State Machine fully implemented
✅ All states created (Idle, Attract, Interactive, Fireworks)
✅ Integrated with EventSystem
✅ Tests pass
✅ State diagram documented
✅ Ready for Phase 4 (Component Extraction)

**⚠️ BLOCKS Phase 4 - Component Decomposition cannot start until this completes**

---

## Phase 3 Coordination

### Why Sequential?

1. State Machine publishes/subscribes to events
2. State Machine uses EventSystem infrastructure
3. Testing State Machine requires EventSystem working
4. Both are architectural foundations for Phase 4

### Handoff Process

When Task 3.1 (Event System) completes:

1. Agent A completes Event System
2. Agent A runs all Event System tests
3. Agent A enables `use_event_system: true` in config
4. Agent A verifies integration with detectors
5. Agent A commits and pushes
6. Agent A immediately starts Task 3.2 (State Machine)

### Parallel Work During Phase 3

While Agent A works on Phase 3, other agents can:
- Write additional tests for Phase 1/2 components
- Improve documentation
- Prepare for Phase 4 by reading component extraction docs
- **Cannot** start Phase 4 work (needs architecture complete)

### Timeline

- **Week 4**: Event System (5 days)
- **Week 5**: State Machine (5 days)
- **Total**: 10 days sequential work

This is the **critical path** through the project.

## Success Criteria for Phase 3 Completion

✅ EventSystem working and tested
✅ State Machine working and tested
✅ Both integrated together
✅ SceneManager uses State Machine
✅ Detectors publish events
✅ Feature flags work
✅ Documentation complete
✅ **Ready for Phase 4: Component Decomposition**
