# 🪔 AI-Augmented Diwali Projection Experience

An interactive installation that merges computer vision, projection mapping, and generative visuals to create a festive augmented-reality experience for Diwali celebrations.

## Overview

The **AI-Augmented Diwali Projection System** uses a camera feed to analyze motion, gestures, and sound cues, dynamically generating **Diwali-themed visuals** (e.g., diyas, fireworks, rangolis) projected onto a physical wall or surface.

This system provides an immersive, real-time, culturally inspired interactive display suitable for events, homes, or public installations during Diwali celebrations.

## Features

- **Interactive Visualization:** Project dynamic visuals that respond to human movement and gestures
- **Multiple Interaction Modes:**
  - **Motion Detection:** Detects movement in the camera frame
  - **Gesture Recognition:** Recognizes hand gestures using MediaPipe
  - **Audio Detection:** Responds to claps or loud sounds
- **Diwali-themed Visual Effects:**
  - **Virtual Diyas:** Place glowing lamps with hand gestures that flicker realistically
  - **Elegant Fireworks:** Multiple firework types with realistic physics and visual effects
  - **Traditional Rangoli Patterns:** Beautifully crafted digital rangoli with authentic designs
  - **Floating Elements:** Diyas and rangoli patterns that drift gracefully across the screen
  - **Aura Effects:** Follow people's movements with ethereal glowing outlines
- **Projection Calibration:** Utility for aligning projection with physical surfaces
- **Low-Latency Design:** Optimized for smooth real-time interaction

## Requirements

### Hardware

- Computer (Windows/Mac/Linux) with webcam
- Projector
- Microphone (optional, for audio interaction)

### Software Dependencies

- Python 3.10+
- OpenCV (Computer Vision)
- MediaPipe (Gesture Recognition)
- Pygame (Visualization)
- NumPy
- SoundDevice (Audio Processing)

## Installation

1. Clone or download this repository:

```bash
git clone https://github.com/username/diwali-projection.git
cd diwali-projection
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

3. Ensure your webcam and projector are connected and working

## Usage

### Basic Usage

Run the main application:

```bash
python src/main.py
```

### Command Line Options

```bash
python src/main.py --fullscreen  # Run in fullscreen mode
python src/main.py --debug       # Show debug overlay
python src/main.py --config /path/to/custom-config.json  # Use custom configuration
```

### Calibration

When first starting the application, it will enter calibration mode. This allows you to align the projection with your physical space:

1. Use arrow keys to move each corner point (use SHIFT + arrow for larger movements)
2. Press 1-4 to select different corner points
3. Press ENTER when the alignment looks correct
4. Press C at any time to re-enter calibration mode

### Interactive Controls

During normal operation:

- **ESC:** Exit the application
- **C:** Enter/exit calibration mode
- **D:** Toggle debug overlay

## Project Structure

```text
.
├── assets/
│   ├── diyas/        # Diya images for projection
│   ├── rangoli/      # Rangoli pattern images
│   └── fireworks/    # Firework effect assets
├── config/
│   └── settings.json # Configuration parameters
├── src/
│   ├── main.py                  # Main application entry point
│   ├── camera_input.py          # Camera input handling
│   ├── motion_detector.py       # Motion detection algorithms
│   ├── gesture_tracker.py       # Hand gesture recognition
│   ├── audio_detector.py        # Sound detection
│   ├── scene_manager.py         # Visual state management
│   ├── visual_generator.py      # Visual effects rendering
│   └── projection_calibrator.py # Projection alignment utility
└── README.md
```

## Customization

### Adding Your Own Visuals

To add custom diya or rangoli images:

1. Add PNG images with transparency to `assets/diyas/` or `assets/rangoli/`
2. Restart the application

### Configuration

Edit `config/settings.json` to customize:

- Camera settings (resolution, FPS)
- Motion detection sensitivity
- Gesture tracking parameters
- Audio detection thresholds
- Visual effect properties
  - **Fireworks**: Customize particle count, colors, types, and physics
  - **Rangoli**: Adjust complexity, colors, and animation parameters
  - **Diyas**: Configure size, brightness, and floating behavior
  - **Aura Effects**: Modify colors, opacity, and particle effects

## Development

Each component is designed to be modular, making it easy to extend or replace parts of the system:

- **Camera Input:** Handles webcam capture and preprocessing
- **Motion Detector:** Implements frame differencing for movement detection
- **Gesture Tracker:** Uses MediaPipe to recognize hand poses
- **Audio Detector:** Identifies sound spikes from microphone
- **Scene Manager:** Coordinates inputs and determines visual states
- **Visual Generator:** Renders Diwali-themed graphics
- **Projection Calibrator:** Aligns output with physical surfaces

## Enhanced Visual Effects

### Traditional Rangoli Patterns

- **Bezier-based Design**: Algorithmically generated authentic traditional rangoli patterns
- **Dynamic Animation**: Rotating patterns with color cycling and smooth transitions
- **Floating Display**: Rangoli patterns that drift gracefully across the screen
- **Cultural Authenticity**: Traditional Indian color palettes and motifs

### Advanced Fireworks System

- **Multiple Firework Types**: Bloom, palm, ring, chrysanthemum, willow, and multi-break patterns
- **Realistic Physics**: Gravity, air resistance, and natural particle motion
- **Launch Phase**: Rockets with smoke trails before explosion
- **Visual Effects**: Particle trails, color transitions, glow effects, and realistic fading

### Interactive Diyas

- **Realistic Flickering**: Subtle animation mimicking real flame movement
- **Floating Motion**: Diyas that gently float across the projected space
- **Natural Physics**: Realistic wobble and rotation as diyas move

### Ethereal Aura Effects

- **Person Outline Detection**: Glowing outlines that follow people's movements
- **Color Cycling**: Smooth transitions through traditional Diwali colors
- **Particle Effects**: Optional particle systems around detected people

## Future Enhancements

- Music-reactive light shows synchronized with Diwali music
- AR marker alignment for precise mapping to physical objects
- Web dashboard for remote control and customization
- Multi-projector support for larger installations
- AI-driven narrative experiences based on traditional Diwali stories

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenCV](https://opencv.org/) - Computer vision library
- [MediaPipe](https://developers.google.com/mediapipe) - Gesture recognition
- [Pygame](https://www.pygame.org/) - Visualization framework
- [SoundDevice](https://python-sounddevice.readthedocs.io/) - Audio processing

---

## Credits

Created for Diwali celebrations 2025

## Conclusion

This AI-Augmented Diwali Projection Experience combines traditional cultural elements with cutting-edge technology to create an immersive, interactive celebration of the Festival of Lights. The system's responsive visuals, authentic cultural representations, and smooth performance make it suitable for both personal and public celebrations, bringing the joy and beauty of Diwali to life in new and innovative ways.
