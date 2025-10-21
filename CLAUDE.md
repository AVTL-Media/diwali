# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **AI-Augmented Diwali Projection System** is an interactive Python application that combines computer vision, gesture recognition, and audio detection to create dynamic Diwali-themed visual projections. The system analyzes camera feeds, detects motion and gestures, and projects culturally-inspired visuals (diyas, fireworks, rangoli patterns) onto physical surfaces.

## Common Commands

### Running the Application

```bash
# Basic execution
python src/main.py

# Fullscreen mode
python src/main.py --fullscreen

# Debug mode with overlay
python src/main.py --debug

# Custom configuration
python src/main.py --config /path/to/custom-config.json
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# The project uses a conda environment (environment.yml is present)
# The environment directory is already set up locally
```

### Interactive Controls

During runtime:
- **ESC**: Exit application
- **C**: Enter/exit calibration mode
- **D**: Toggle debug overlay
- **Arrow keys**: Move calibration corner points
- **SHIFT + arrows**: Larger movements in calibration
- **1-4**: Select different corner points during calibration
- **ENTER**: Confirm calibration alignment

## Architecture Overview

### Core Components

The system follows a modular, event-driven architecture with clear separation of concerns:

**Input Processing Layer** (camera_input.py, audio_detector.py):
- `CameraInput`: Captures and preprocesses webcam frames at 30 FPS (configurable)
- `AudioDetector`: Detects claps/sound spikes using sounddevice for audio-reactive effects

**Detection Layer** (motion_detector.py, gesture_tracker.py, person_outline_detector.py):
- `MotionDetector`: Frame differencing algorithm to identify moving regions
- `GestureTracker`: Uses MediaPipe Hands to detect hand poses and locations for interaction triggers
- `PersonOutlineDetector`: Identifies person silhouettes for ethereal outline rendering

**State Management** (scene_manager.py):
- `SceneStateManager`: Coordinates inputs from all detectors and manages visual state transitions
- Uses `VisualState` enum: IDLE, DIYA, FIREWORKS, RANGOLI, AURA
- Handles state persistence, timeouts, and event-driven transitions

**Visual Generation** (visual_generator.py):
- `VisualGenerator`: The largest and most complex module, responsible for all rendering
- Implements layered rendering: background → state-specific visuals → ethereal outlines → floating objects
- Manages particle systems for fireworks, rangoli animation, floating diyas, and aura effects

**Projection Calibration** (projection_calibrator.py):
- `ProjectionCalibrator`: Four-point perspective warp for aligning projection to physical surfaces

**Main Application** (main.py):
- `DiwaliProjectionApp`: Orchestrates all components, manages the main event loop, handles configuration loading

### Data Flow

```
Camera → Motion/Gesture Detection → Scene State Manager → Visual Generator → Pygame Display/Projector
  ↓                                         ↑
Audio Detection ─────────────────────────────┘
```

1. Camera captures frame and passes to detection modules
2. Detection modules analyze frame for motion, gestures, and person outlines
3. Audio detector monitors for sound spikes independently
4. Scene Manager receives all detection events and determines current visual state
5. Visual Generator renders appropriate visuals based on state
6. Pygame displays rendered output to projector

### Configuration Architecture

All settings are centralized in `config/settings.json` with nested structure:
- `camera`: Device settings, resolution, FPS
- `motion_detection`: Blur, threshold, minimum area
- `gesture_tracking`: MediaPipe confidence levels
- `audio_detection`: Threshold multipliers, sampling
- `visual_effects`: Nested configs for each visual type (diya, fireworks, rangoli, aura, ethereal_outlines)
- `projection`: Fullscreen, calibration points
- `app`: Debug mode, FPS display, exit key

Configuration is loaded at initialization and accessed via deep dictionary gets throughout the codebase.

## Visual Effects System

### Rangoli Patterns
- Algorithmically generated using Bezier curves for authentic traditional designs
- **Psychedelic mode**: Dynamic mandalas with rotating patterns, color cycling, blend modes
- Configurable complexity levels, rotation speeds, and floating animations
- Located in `visual_generator.py`: `_generate_rangoli()`, `_generate_psychedelic_rangoli()`

### Fireworks System
- Multiple types: bloom, palm, ring, chrysanthemum, willow, multi-break
- Two-phase system: launch rockets with smoke trails, then particle explosion
- Realistic physics: gravity, air resistance, particle trails, color transitions
- Rate-limited rendering to prevent performance degradation
- Methods: `_render_fireworks()`, `_process_new_firework_origins()`, `_update_firework_particles()`

### Floating Objects
- Diyas and rangolis that drift across the screen with natural physics
- Wobble and rotation effects for realistic movement
- Spawn rate control and maximum instance limits
- Class: `FloatingObject` and subclasses `FloatingDiya`, `FloatingRangoli`

### Ethereal Outlines
- Glowing person silhouettes with color cycling
- Optional particle effects around detected people
- Gaussian blur for glow effect, alpha blending for transparency
- Methods: `_render_ethereal_outlines()`, `_create_ethereal_surface()`

## Development Guidelines

### Code Organization Principles

**Recent Refactoring** (see REFACTORING.md for details):
- The `update()` and `render()` methods in visual_generator.py were decomposed into focused sub-methods
- Naming convention: `_update_*` for state updates, `_render_*` for drawing
- Layered rendering approach for clarity

**Method Size**:
- Aim for methods under 30 lines
- Extract complex logic into helper methods with descriptive names

**Configuration Access**:
- Deep dictionary access with `.get()` and defaults is the current pattern
- Future improvement: Create a `ConfigManager` class for cleaner access

### Known Technical Debt

1. **visual_generator.py** is large (81KB) and handles multiple responsibilities
   - Consider extracting separate classes: `FireworksManager`, `RangoliRenderer`, `FloatingObjectManager`

2. **Configuration handling** uses repetitive nested `.get()` calls
   - Future: Implement a ConfigManager with validation

3. **Error handling** is minimal in many places
   - Asset loading failures are often silent
   - Add try/except blocks for file operations and provide meaningful feedback

4. **Performance concerns**:
   - Large surfaces frequently created/destroyed
   - No surface caching for scaled/rotated images
   - Person outline detection is computationally heavy and runs in main thread

5. **No automated testing** infrastructure exists yet
   - Creating tests would require mocking camera/audio hardware
   - Visual output validation is challenging

### Type Hints
The codebase currently lacks type hints. When adding new code or refactoring, consider adding Python type annotations for better IDE support and code clarity.

### Asset Management
- Assets are loaded from `assets/` directory
- Diyas: PNG images with transparency in `assets/diyas/`
- Rangoli: Traditional patterns in `assets/rangoli/`
- Background: `assets/diwali_bg.jpeg`
- Missing assets should be handled gracefully with fallbacks

## Dependencies

Core libraries (from requirements.txt):
- `opencv-python>=4.7.0`: Computer vision and image processing
- `mediapipe>=0.10.0`: Hand gesture recognition
- `pygame>=2.5.0`: Rendering and display
- `numpy>=1.24.0`: Numerical operations and array manipulation
- `sounddevice>=0.4.6`: Audio input processing

## Performance Considerations

- Target: ≥25 FPS for smooth projection
- Camera input downscaled to 640×480 by default for performance
- Motion detection uses frame differencing (computationally light)
- Gesture tracking via MediaPipe is the most CPU-intensive operation
- Person outline detection can cause frame drops; consider optimization or threading
- Fireworks particle system has rate limiting to prevent slowdown

## Cultural Context

The visual effects are designed to honor traditional Diwali celebrations:
- **Diyas**: Oil lamps symbolizing light over darkness
- **Rangoli**: Traditional floor art patterns with geometric and floral designs
- **Fireworks**: Celebratory light displays
- Color palettes use traditional Indian festival colors (warm oranges, golds, magentas)

When modifying visual effects, maintain cultural authenticity and respect for the traditions being represented.
