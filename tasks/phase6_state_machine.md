# State Machine Pattern Implementation

## Overview

This task focuses on implementing a formal State Machine pattern for the scene transitions in the Diwali Projection System, replacing the current ad hoc state management in `SceneManager`.

## Current State

The `SceneManager` currently handles application state transitions using basic conditionals and event handling, but state transitions are not formalized and state-specific behaviors are scattered.

## Target State

A well-defined State Machine pattern implementation that:

1. Makes state transitions explicit and well-documented
2. Encapsulates state-specific behaviors within state classes
3. Allows for easier addition of new states
4. Provides clearer visualization of the application flow

## Implementation Plan

### 1. Define State Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class State(ABC):
    """Base class for application states."""
    
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass
        
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this state."""
        pass
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state based on time delta."""
        pass
        
    @abstractmethod
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle events in the context of this state."""
        pass
        
    def transition_to(self, new_state_name: str) -> None:
        """Transition to a new state."""
        self.scene_manager.change_state(new_state_name)
```

### 2. Implement Concrete States

Create specific state implementations for each application state:

```python
class IdleState(State):
    """Idle state waiting for interaction."""
    
    def enter(self) -> None:
        """Enter idle state."""
        self.scene_manager.visual_generator.clear_all_effects()
        self.scene_manager.timer = 0.0
        
    def exit(self) -> None:
        """Exit idle state."""
        pass
        
    def update(self, dt: float) -> None:
        """Update idle state."""
        self.scene_manager.timer += dt
        
        # Check for automatic transition to attract mode
        if self.scene_manager.timer > self.scene_manager.config_manager.get_float("idle.timeout", 30.0):
            self.transition_to("attract")
            
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle events in idle state."""
        if event_type == "motion_detected":
            self.transition_to("interactive")
        elif event_type == "audio_peak":
            self.transition_to("fireworks")
```

### 3. Refactor SceneManager

Update the `SceneManager` to use the State pattern:

```python
class SceneManager:
    """Manages application states and transitions."""
    
    def __init__(self, config_manager, visual_generator):
        self.config_manager = config_manager
        self.visual_generator = visual_generator
        self.timer = 0.0
        self.current_state = None
        
        # Register available states
        self.states = {
            "idle": IdleState(self),
            "attract": AttractState(self),
            "interactive": InteractiveState(self),
            "fireworks": FireworksState(self),
            # Add other states
        }
        
        # Set initial state
        self.change_state("idle")
        
    def change_state(self, new_state_name: str) -> None:
        """Change to a new state."""
        if self.current_state:
            self.current_state.exit()
            
        self.current_state = self.states[new_state_name]
        self.current_state.enter()
        
    def update(self, dt: float) -> None:
        """Update current state."""
        if self.current_state:
            self.current_state.update(dt)
            
    def handle_event(self, event_type: str, event_data: Dict[str, Any] = None) -> None:
        """Handle events in current state."""
        if self.current_state:
            self.current_state.handle_event(event_type, event_data or {})
```

### 4. Implement State Transition Diagram

Create a visual state transition diagram to document the application flow:

```
[Idle] <----timeout----- [Attract]
  |                         |
  |                         |
motion                    motion
  |                         |
  v                         v
[Interactive] <---timeout--- 
  |
  |
audio_peak
  |
  v
[Fireworks] ---timeout---> [Idle]
```

### 5. Implement State History and Debugging

Add state history tracking and debugging tools:

```python
def change_state(self, new_state_name: str) -> None:
    """Change to a new state with history tracking."""
    if new_state_name not in self.states:
        self.logger.error(f"Unknown state: {new_state_name}")
        return
        
    old_state_name = self.current_state.__class__.__name__ if self.current_state else "None"
    self.logger.info(f"State transition: {old_state_name} -> {new_state_name}")
    
    if self.current_state:
        self.current_state.exit()
        
    self.current_state = self.states[new_state_name]
    self.state_history.append((new_state_name, time.time()))
    self.current_state.enter()
```

## Testing Strategy

1. Create unit tests for each state class
2. Test all valid state transitions
3. Test invalid state transition handling
4. Verify event handling in different states
5. Verify automatic transitions based on timers

## Expected Outcomes

1. **Clearer Code Structure**: State behaviors clearly encapsulated in dedicated classes
2. **Simplified Debugging**: Easier to track and debug state transitions
3. **Better Documentation**: Explicit state machine diagram explains application flow
4. **Improved Extensibility**: New states can be added with minimal changes to existing code

## Success Criteria

- All state transitions work as documented
- State-specific behaviors are properly encapsulated
- Adding a new state requires minimal changes to existing code
- State history provides useful debugging information