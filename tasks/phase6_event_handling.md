# Event Handling System Refactoring

⚠️ **REVISED PLAN UPDATE**: This is now **Phase 3, Week 4** (moved from original Phase 6, Weeks 9-10).

**Critical Change**: Event System now comes **BEFORE** component extraction (Phase 4) so components can be designed to use events from the start.

## Overview

This task focuses on implementing a centralized event handling system that will be used by all components extracted in Phase 4.

**IMPORTANT**: This must be completed before Phase 4 (Component Decomposition) begins.

## Current State

The current event handling code is scattered throughout different components, making it difficult to track and maintain. Event handling logic is tightly coupled with state management, making it harder to add new event types or modify existing behaviors.

## Target State

A centralized, consistent event system that:

1. Provides a unified interface for raising and handling events
2. Decouples event generation from event handling
3. Supports custom event types with rich data
4. Allows components to subscribe to relevant events

## Implementation Plan

### 1. Define Event System

Create a centralized event system with publisher-subscriber pattern:

```python
from enum import Enum, auto
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass

class EventType(Enum):
    """Enumeration of supported event types."""
    
    # System events
    STARTUP = auto()
    SHUTDOWN = auto()
    ERROR = auto()
    
    # Input events
    MOTION_DETECTED = auto()
    GESTURE_RECOGNIZED = auto()
    AUDIO_PEAK = auto()
    
    # State events
    STATE_CHANGED = auto()
    
    # Visual events
    FIREWORK_CREATED = auto()
    RANGOLI_ANIMATED = auto()

@dataclass
class Event:
    """Event data container."""
    
    type: EventType
    data: Dict[str, Any]
    timestamp: float

class EventSystem:
    """Centralized event system for the application."""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        self.subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type."""
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
```

### 2. Integrate with Motion Detection

Update the motion detector to use the event system:

```python
import time
from src.event_system import EventSystem, EventType, Event

class MotionDetector:
    """Detects motion in camera frames."""
    
    def __init__(self, config_manager, event_system: EventSystem):
        self.config_manager = config_manager
        self.event_system = event_system
        # Other initialization
        
    def process_frame(self, frame):
        """Process a camera frame to detect motion."""
        # Detect motion in frame
        motion_detected = self._detect_motion(frame)
        
        if motion_detected:
            # Publish motion event with data
            event = Event(
                type=EventType.MOTION_DETECTED,
                data={
                    "position": motion_detected["position"],
                    "magnitude": motion_detected["magnitude"]
                },
                timestamp=time.time()
            )
            self.event_system.publish(event)
```

### 3. Update Scene Manager to Use Event System

Modify the scene manager to use the event system for state transitions:

```python
class SceneManager:
    """Manages application states and transitions."""
    
    def __init__(self, config_manager, event_system: EventSystem):
        self.config_manager = config_manager
        self.event_system = event_system
        self.current_state = None
        self.states = {}
        
        # Subscribe to relevant events
        self.event_system.subscribe(EventType.MOTION_DETECTED, self._handle_motion)
        self.event_system.subscribe(EventType.AUDIO_PEAK, self._handle_audio_peak)
        
        # Initialize states
        # ...
        
    def _handle_motion(self, event: Event) -> None:
        """Handle motion detection events."""
        if self.current_state:
            # Check state rules for motion events
            if self.current_state.name == "idle":
                self.change_state("interactive")
                
    def _handle_audio_peak(self, event: Event) -> None:
        """Handle audio peak events."""
        if self.current_state:
            # Check state rules for audio events
            if self.current_state.name == "interactive":
                self.change_state("fireworks")
                
    def change_state(self, new_state_name: str) -> None:
        """Change to a new state with event notification."""
        old_state_name = self.current_state.name if self.current_state else "None"
        
        # Change state
        if self.current_state:
            self.current_state.exit()
            
        self.current_state = self.states[new_state_name]
        self.current_state.enter()
        
        # Publish state changed event
        event = Event(
            type=EventType.STATE_CHANGED,
            data={
                "old_state": old_state_name,
                "new_state": new_state_name
            },
            timestamp=time.time()
        )
        self.event_system.publish(event)
```

### 4. Create Event Visualization Component

Implement a debugging component to visualize recent events:

```python
class EventVisualizer:
    """Visualizes recent events for debugging."""
    
    def __init__(self, event_system: EventSystem, max_events=10):
        self.event_system = event_system
        self.max_events = max_events
        self.recent_events = []
        
        # Subscribe to all event types
        for event_type in EventType:
            self.event_system.subscribe(event_type, self._record_event)
            
    def _record_event(self, event: Event) -> None:
        """Record an event for visualization."""
        self.recent_events.append(event)
        while len(self.recent_events) > self.max_events:
            self.recent_events.pop(0)
            
    def render(self, surface):
        """Render recent events to the surface."""
        font = pygame.font.SysFont("monospace", 16)
        y = 10
        
        for event in reversed(self.recent_events):
            event_time = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
            text = f"{event_time} - {event.type.name}"
            
            text_surface = font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (10, y))
            y += 20
```

### 5. Add Event Logging

Integrate events with the logging system:

```python
class EventLogger:
    """Logs events to the application log."""
    
    def __init__(self, event_system: EventSystem, logger):
        self.event_system = event_system
        self.logger = logger
        
        # Subscribe to all event types
        for event_type in EventType:
            self.event_system.subscribe(event_type, self._log_event)
            
    def _log_event(self, event: Event) -> None:
        """Log an event to the application log."""
        self.logger.info(
            f"Event: {event.type.name}",
            event_data=str(event.data),
            timestamp=event.timestamp
        )
```

## Implementation Tasks

### 1. Event System Development

- [ ] Create `src/event_system.py` with the EventSystem class
- [ ] Define core event types in an EventType enum
- [ ] Implement the Event data container class
- [ ] Add unit tests for event system functionality

### 2. Component Integration

- [ ] Update existing components to use the event system:
  - [ ] Motion detector
  - [ ] Audio detector
  - [ ] Scene manager
  - [ ] Visual generator
- [ ] Create an EventLogger component for debugging

### 3. Documentation and Examples

- [ ] Create documentation for the event system
- [ ] Add examples of common event handling patterns
- [ ] Create an event flow diagram showing how events propagate

## Expected Outcomes

1. **Centralized Event Handling**: All events are managed through a single system
2. **Reduced Coupling**: Components communicate via events rather than direct method calls
3. **Enhanced Debugging**: Events can be logged and visualized for debugging
4. **Better Extensibility**: New event types can be added with minimal changes

## Testing Strategy

1. Create unit tests for the event system
2. Verify event propagation through components
3. Test error handling in event subscribers
4. Create an event simulation tool for testing complex scenarios

## Success Criteria

- All application interactions are properly captured as events
- Components can subscribe to and handle relevant events
- Event history provides useful debugging information
- The system is resilient to errors in event handlers