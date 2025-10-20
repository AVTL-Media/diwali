# 🪔 Technical Design Document (TDD)

**Project Title:** *AI-Augmented Diwali Projection Experience*
**Version:** 1.0
**Author:** S. K. Ali Ahmed
**Date:** 20 October 2025

---

## 1. Overview

The **AI-Augmented Diwali Projection System** is an interactive installation that merges **computer vision**, **projection mapping**, and **generative visuals** to create a festive augmented-reality experience.
It uses a **camera feed** to analyze motion, gestures, and sound cues, dynamically generating **Diwali-themed visuals** (e.g., diyas, fireworks, rangolis) projected onto a physical wall or surface.

The system provides an immersive, real-time, culturally inspired interactive display suitable for events, homes, or public installations.

---

## 2. Objectives

* To project **real-time, AI-generated or pre-animated visuals** responsive to human interaction.
* To enhance **user engagement** using **gesture detection**, **motion recognition**, and **sound response**.
* To ensure **low-latency projection** for smooth interactivity.
* To support **plug-and-play deployment** on commodity hardware (laptop + projector + webcam).

---

## 3. System Architecture

### 3.1 High-Level Architecture Diagram

```
             ┌─────────────────────┐
             │     User/Viewer     │
             └───────┬─────────────┘
                     │
                     ▼
             ┌─────────────────────┐
             │  Camera Input Layer │
             │  (Webcam/OpenCV)    │
             └───────┬─────────────┘
                     │
                     ▼
      ┌────────────────────────────────────┐
      │   AI Processing & Interaction Core │
      │────────────────────────────────────│
      │ - Motion Detection (OpenCV)        │
      │ - Gesture Tracking (Mediapipe)     │
      │ - Audio Detection (sounddevice)    │
      │ - Scene State Manager              │
      └───────────────┬────────────────────┘
                      │
                      ▼
             ┌─────────────────────┐
             │ Visual Generation   │
             │ (Pygame / OpenGL /  │
             │  Generative AI)     │
             └───────┬─────────────┘
                     │
                     ▼
             ┌─────────────────────┐
             │ Projection Display  │
             │ (Projector Output)  │
             └─────────────────────┘
```

---

## 4. System Components

### 4.1 Input Layer

* **Camera:** Captures real-time frames (30 FPS).
* **Audio Sensor (Optional):** Detects claps or beats using `sounddevice` or `pyaudio`.
* **User Input:** Gesture or movement acts as the interaction trigger.

### 4.2 AI Processing Layer

| Module                   | Description                                                   | Technology               |
| ------------------------ | ------------------------------------------------------------- | ------------------------ |
| **Motion Detector**      | Uses frame differencing to identify moving regions.           | `OpenCV`                 |
| **Gesture Tracker**      | Detects hand, palm, or body pose for location-based triggers. | `MediaPipe Hands / Pose` |
| **Audio Event Detector** | Triggers effects on clapping or sound spikes.                 | `sounddevice`, `numpy`   |
| **Scene State Manager**  | Maintains visual states and transitions.                      | Custom Python class      |

### 4.3 Visual Generation Layer

| Visual Type     | Trigger                           | Render Method                      |
| --------------- | --------------------------------- | ---------------------------------- |
| Diya            | Hand proximity or detected motion | PNG overlay with alpha blending    |
| Fireworks       | Audio spike or fast movement      | Particle system (OpenGL / Pygame)  |
| Rangoli Pattern | Idle state or surface alignment   | Static or generative texture       |
| Aura Light      | Around detected person            | Gaussian glow with dynamic opacity |

---

## 5. Data Flow

1. **Camera Input:**
   Captures frame → Preprocess (resize, grayscale, blur)
2. **Motion/Gesture Detection:**
   Computes frame difference → Identifies contours or keypoints
3. **State Management:**
   Updates `scene_state` (e.g., `motion_detected=True`, `gesture="wave"`)
4. **Visual Mapping:**
   Depending on the state, selects corresponding visual assets or generates patterns.
5. **Projection Output:**
   Rendered via Pygame/OpenGL and projected in real time.

---

## 6. Technical Stack

| Layer                    | Technology              | Purpose                       |
| ------------------------ | ----------------------- | ----------------------------- |
| **Language**             | Python 3.10+            | Core logic and integration    |
| **Computer Vision**      | OpenCV                  | Motion detection and tracking |
| **Gesture AI**           | Mediapipe               | Hand/body pose recognition    |
| **Audio Processing**     | sounddevice, numpy      | Clap/sound detection          |
| **Rendering Engine**     | Pygame / PyOpenGL       | Dynamic visual rendering      |
| **Projection Alignment** | Manual calibration tool | Wall mapping adjustment       |
| **Optional Web Layer**   | Flask + Socket.IO       | Remote control / dashboard    |

---

## 7. Algorithms

### 7.1 Motion Detection Algorithm

1. Capture two consecutive frames.
2. Convert to grayscale and apply Gaussian blur.
3. Compute absolute difference.
4. Apply binary thresholding and contour detection.
5. If contour area > threshold → trigger “motion event.”

### 7.2 Gesture Recognition

Uses **Mediapipe Hand Tracking**:

* Extracts 21 landmark coordinates.
* Calculates relative distances.
* Recognizes gestures (open palm, wave, pinch).
* Maps gesture → action (e.g., “light diya”, “burst firework”).

### 7.3 Sound Detection

* Record 0.5-second audio window.
* Compute amplitude envelope.
* If amplitude exceeds `mean + 2σ`, trigger “firework event.”

---

## 8. Output Rendering

| Visual        | Rendering Method            | Example Behavior                  |
| ------------- | --------------------------- | --------------------------------- |
| **Diya**      | Alpha PNG overlay           | Fades in/out on palm motion       |
| **Firework**  | Particle burst system       | Random direction + gravity effect |
| **Rangoli**   | Generative symmetry pattern | Color changes on slow motion      |
| **Glow/Aura** | Gaussian blur overlay       | Follows user silhouette           |

---

## 9. Projection Calibration

A **calibration utility** aligns projected visuals with the wall:

* Displays four adjustable corner markers.
* Uses arrow keys or mouse to align the projection.
* Saves projection transform matrix (4-point perspective warp).

---

## 10. Performance Considerations

| Factor                   | Solution                                    |
| ------------------------ | ------------------------------------------- |
| **Frame Lag**            | Downscale camera input to 640×480           |
| **Lighting Variability** | Adaptive thresholding in motion detection   |
| **Projection Delay**     | Use double-buffered rendering               |
| **CPU Usage**            | Multiprocessing for camera + render threads |

---

## 11. Future Enhancements

* 🎭 **Generative AI visuals** (Stable Diffusion or RunwayML integration for new Rangoli textures).
* 🪩 **AR marker alignment** for precise surface mapping.
* 🔊 **Music-driven light show** synced with beat detection.
* ☁️ **Web dashboard** for remote theme customization.

---

## 12. Risks and Mitigation

| Risk                                        | Mitigation                                           |
| ------------------------------------------- | ---------------------------------------------------- |
| Low-light conditions affect camera accuracy | Use IR-based motion sensors or high-contrast filters |
| Latency due to heavy computation            | Use GPU acceleration or reduce frame size            |
| Calibration drift                           | Implement automatic recalibration via AR markers     |

---

## 13. Success Metrics

| Metric              | Description                             | Target      |
| ------------------- | --------------------------------------- | ----------- |
| Interaction Latency | Time between motion and visual response | ≤ 150 ms    |
| Frame Rate          | Smoothness of projection                | ≥ 25 FPS    |
| User Engagement     | Average interaction duration            | ≥ 2 minutes |
| Accuracy            | Correct gesture/motion recognition      | ≥ 85%       |

---

## 14. References

* OpenCV Documentation. *[https://docs.opencv.org/](https://docs.opencv.org/)*
* Google Mediapipe Framework. *[https://developers.google.com/mediapipe](https://developers.google.com/mediapipe)*
* Pygame Community Docs. *[https://www.pygame.org/docs/](https://www.pygame.org/docs/)*
* RunwayML SDK. *[https://runwayml.com/developers/](https://runwayml.com/developers/)*
* Szeliski, R. (2022). *Computer Vision: Algorithms and Applications (2nd ed.)*.

---

Would you like me to now generate a **ready-to-run prototype folder** (with Python files and assets) that implements the *motion + diya projection system* described in this design doc?
It would include:

* `/src/main.py`
* `/assets/diyas/`
* `/config/settings.json`
* `/readme.md`

That would make this technical design directly executable.
