# Phase 6: Parallel Performance & Concurrency Tasks

**Phase**: 6 - Performance & Concurrency
**Weeks**: 10-11
**Can Run in Parallel**: ✅ Yes - 2 agents
**Dependencies**: Phase 5 (Method Refactoring) MUST be complete

## Overview

Optimize the stable, refactored architecture. Two parallel tracks: Performance optimization and Thread safety.

**Maximum Parallelization**: 2 agents working simultaneously

---

## Task 6.1: Performance Optimization

**Week**: 10
**Agent Assignment**: Agent A
**Estimated Duration**: 5 days
**Can Run in Parallel**: ✅ Yes (with Task 6.2)
**Dependencies**: Phase 5 complete
**Files**: `src/surface_cache.py`, component optimizations

### Goal

Implement surface caching and optimize rendering performance.

### Deliverables

1. `src/surface_cache.py` - SurfaceCache class
2. Optimized component rendering
3. Performance benchmarks
4. Documentation

### Implementation

#### Step 1: Create SurfaceCache (Day 1-2)

```python
# src/surface_cache.py
import pygame
from typing import Dict, Tuple, Optional
import hashlib

class SurfaceCache:
    """Cache for frequently used surfaces."""

    def __init__(self, max_size: int = 50):
        self.cache: Dict[str, pygame.Surface] = {}
        self.access_counts: Dict[str, int] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[pygame.Surface]:
        """Get surface from cache."""
        if key in self.cache:
            self.access_counts[key] += 1
            return self.cache[key].copy()
        return None

    def store(self, key: str, surface: pygame.Surface) -> None:
        """Store surface in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = surface.copy()
        self.access_counts[key] = 0

    def _evict_lru(self) -> None:
        """Evict least recently used."""
        if not self.cache:
            return

        min_key = min(self.access_counts.items(), key=lambda x: x[1])[0]
        del self.cache[min_key]
        del self.access_counts[min_key]

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.access_counts.clear()

    @staticmethod
    def generate_key(*args) -> str:
        """Generate cache key from arguments."""
        key_str = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()[:16]
```

#### Step 2: Integrate with RangoliRenderer (Day 2-3)

```python
# src/components/rangoli_renderer.py
class RangoliRenderer(VisualComponent):
    def __init__(self, config_manager, event_system, surface_cache):
        super().__init__(config_manager, event_system)
        self.surface_cache = surface_cache

    def render(self, surface, center, alpha=200):
        """Render with caching."""
        # Generate cache key
        cache_key = self.surface_cache.generate_key(
            "rangoli",
            int(self.angle / 10) * 10,  # Round to 10 degrees
            self.color_cycle_hue // 0.1
        )

        # Try cache first
        cached = self.surface_cache.get(cache_key)
        if cached:
            surface.blit(cached, center)
            return

        # Render and cache
        rangoli_surface = self._render_rangoli()
        self.surface_cache.store(cache_key, rangoli_surface)
        surface.blit(rangoli_surface, center)
```

#### Step 3: Performance Profiling (Day 3-4)

```python
# src/profiler.py
import time
from functools import wraps
from typing import Dict, List

class PerformanceProfiler:
    """Profile performance of methods."""

    def __init__(self):
        self.timings: Dict[str, List[float]] = {}

    def profile(self, func):
        """Decorator to profile method."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            func_name = func.__name__
            if func_name not in self.timings:
                self.timings[func_name] = []
            self.timings[func_name].append(elapsed)

            return result
        return wrapper

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get timing statistics."""
        stats = {}
        for func_name, timings in self.timings.items():
            stats[func_name] = {
                'count': len(timings),
                'total': sum(timings),
                'avg': sum(timings) / len(timings),
                'min': min(timings),
                'max': max(timings)
            }
        return stats
```

#### Step 4: Optimize Components (Day 4-5)

Optimization targets:
- Cache rotated rangoli patterns
- Pre-compute firework trajectories
- Reduce surface creation/destruction
- Optimize blending operations

#### Step 5: Benchmarking (Day 5)

```python
# tests/benchmark.py
import pytest
import time

def test_performance_baseline():
    """Benchmark baseline performance."""
    # Initialize system
    # Run for 30 seconds
    # Measure FPS
    # Assert FPS >= 60
    pass

def test_cache_effectiveness():
    """Measure cache hit rate."""
    # Run with cache enabled
    # Measure hit rate
    # Assert hit rate > 70%
    pass
```

### Success Criteria

✅ SurfaceCache implemented
✅ Cache integrated with components
✅ FPS improved by 20%+
✅ Memory usage stable
✅ Benchmarks pass
✅ Documentation complete

---

## Task 6.2: Thread Safety & Concurrency

**Week**: 11
**Agent Assignment**: Agent B
**Estimated Duration**: 5 days
**Can Run in Parallel**: ✅ Yes (with Task 6.1)
**Dependencies**: Phase 5 complete
**Files**: `src/threaded_camera.py`, `src/threaded_detector.py`

### Goal

Implement thread-safe camera input and person detection to prevent frame drops.

### Deliverables

1. `src/threaded_camera.py` - ThreadedCameraInput
2. `src/threaded_detector.py` - ThreadedPersonDetector
3. Thread-safe utilities
4. Documentation

### Implementation

#### Step 1: ThreadedCameraInput (Day 1-2)

```python
# src/threaded_camera.py
import threading
import queue
import time
import cv2
import numpy as np

class ThreadedCameraInput:
    """Thread-safe camera input."""

    def __init__(self, camera_id: int = 0, buffer_size: int = 3):
        self.camera_id = camera_id
        self.frame_queue = queue.Queue(maxsize=buffer_size)
        self.running = False
        self.thread = None
        self.camera = None
        self.fps = 0.0

    def start(self) -> bool:
        """Start capture thread."""
        if self.thread and self.thread.is_alive():
            return True

        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            return False

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self) -> None:
        """Stop capture thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.camera:
            self.camera.release()

    def _capture_loop(self) -> None:
        """Camera capture thread."""
        last_time = time.time()

        while self.running and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Calculate FPS
                current_time = time.time()
                fps = 1.0 / (current_time - last_time) if last_time > 0 else 0
                self.fps = 0.9 * self.fps + 0.1 * fps
                last_time = current_time

                # Put in queue, drop oldest if full
                try:
                    self.frame_queue.put(frame, block=False)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put(frame, block=False)
                    except (queue.Empty, queue.Full):
                        pass

            time.sleep(0.001)

    def read(self) -> tuple:
        """Get latest frame (non-blocking)."""
        if not self.running or self.frame_queue.empty():
            return False, None

        try:
            frame = self.frame_queue.get_nowait()
            return True, frame
        except queue.Empty:
            return False, None
```

#### Step 2: ThreadedPersonDetector (Day 2-3)

```python
# src/threaded_detector.py
import threading
import queue
from typing import Optional, Tuple, Any
import numpy as np

class ThreadedPersonDetector:
    """Thread-safe person detection."""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.input_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=1)
        self.running = False
        self.thread = None
        self.detector = None

    def start(self) -> bool:
        """Start detection thread."""
        if self.thread and self.thread.is_alive():
            return True

        self.running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self) -> None:
        """Stop detection thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _detection_loop(self) -> None:
        """Detection thread."""
        from src.person_outline_detector import PersonOutlineDetector
        self.detector = PersonOutlineDetector(self.config_manager)

        while self.running:
            try:
                frame = self.input_queue.get(timeout=0.1)
                outlines = self.detector.detect(frame)

                # Store result
                try:
                    self.result_queue.put((frame, outlines), block=False)
                except queue.Full:
                    try:
                        self.result_queue.get_nowait()
                        self.result_queue.put((frame, outlines), block=False)
                    except (queue.Empty, queue.Full):
                        pass

            except queue.Empty:
                continue

    def process_frame(self, frame: np.ndarray) -> None:
        """Submit frame for processing (non-blocking)."""
        try:
            self.input_queue.put(frame, block=False)
        except queue.Full:
            pass  # Drop frame if can't keep up

    def get_latest_result(self) -> Tuple[Optional[np.ndarray], Any]:
        """Get latest detection result (non-blocking)."""
        if self.result_queue.empty():
            return None, None

        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None, None
```

#### Step 3: Thread-Safe Data Structures (Day 3-4)

```python
# src/thread_safe_dict.py
import threading
from typing import Dict, Any, List, Tuple

class ThreadSafeDict:
    """Thread-safe dictionary."""

    def __init__(self, initial_dict: Dict = None):
        self._dict = initial_dict or {}
        self._lock = threading.RLock()

    def get(self, key: str, default: Any = None) -> Any:
        """Thread-safe get."""
        with self._lock:
            return self._dict.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Thread-safe set."""
        with self._lock:
            self._dict[key] = value

    def delete(self, key: str) -> None:
        """Thread-safe delete."""
        with self._lock:
            if key in self._dict:
                del self._dict[key]

    def items(self) -> List[Tuple]:
        """Thread-safe items (returns copy)."""
        with self._lock:
            return list(self._dict.items())
```

#### Step 4: Integration (Day 4-5)

Update main.py to use threaded components:

```python
# src/main.py
def main():
    # Initialize
    config_manager = ConfigManager()

    # Threaded camera
    if config_manager.get_bool("experimental.use_threaded_camera"):
        camera = ThreadedCameraInput()
    else:
        camera = CameraInput()

    camera.start()

    # Threaded detection
    if config_manager.get_bool("experimental.use_threaded_detection"):
        person_detector = ThreadedPersonDetector(config_manager)
        person_detector.start()

    # Main loop
    running = True
    while running:
        ret, frame = camera.read()
        if ret and person_detector:
            person_detector.process_frame(frame)

        # Get results
        detected_frame, outlines = person_detector.get_latest_result()

        # Render...

    # Cleanup
    camera.stop()
    if person_detector:
        person_detector.stop()
```

#### Step 5: Testing (Day 5)

```python
# tests/test_threading.py
def test_threaded_camera():
    """Test threaded camera input."""
    camera = ThreadedCameraInput()
    camera.start()

    # Read frames
    for _ in range(30):
        ret, frame = camera.read()
        assert ret or frame is None  # Might be empty initially

    camera.stop()

def test_thread_safety():
    """Test thread-safe data structures."""
    tsd = ThreadSafeDict()

    def writer():
        for i in range(100):
            tsd.set(f"key_{i}", i)

    threads = [threading.Thread(target=writer) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should not crash or corrupt data
```

### Success Criteria

✅ ThreadedCameraInput implemented
✅ ThreadedPersonDetector implemented
✅ No race conditions
✅ Frame rate stable
✅ UI remains responsive
✅ Tests pass
✅ Documentation complete

---

## Coordination

### Independence

Tasks 6.1 and 6.2 are largely independent:
- Different files modified
- Different optimization targets
- Can be tested separately

### Integration

After both complete:
1. Enable both optimizations together
2. Test combined performance
3. Verify no conflicts
4. Benchmark full system

### Communication

- Daily progress updates
- Share performance measurements
- Coordinate on testing

## Success Criteria for Phase 6 Completion

✅ Surface caching implemented
✅ Threading implemented
✅ FPS: 60+ on target hardware
✅ CPU usage < 50%
✅ No memory leaks
✅ UI responsive during heavy processing
✅ All tests pass
✅ Documentation complete
✅ **PROJECT COMPLETE!**
