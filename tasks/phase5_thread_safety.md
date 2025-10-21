# Thread Safety Implementation

## Overview

This task focuses on implementing thread safety measures in the Diwali Projection System to enable parallel processing without race conditions or data corruption, particularly for computationally intensive operations like person detection.

## Current State

The application currently performs heavy computations in the main thread, which can cause frame rate drops. Some operations like camera input and audio processing could benefit from parallel execution, but lack proper thread safety measures.

## Target State

A thread-safe implementation that:

1. Moves intensive operations to separate threads
2. Properly synchronizes access to shared resources
3. Ensures smooth frame rates even during heavy processing
4. Provides a clean threading model for future extensions

## Implementation Plan

### 1. Thread-Safe Camera Processing

Implement a thread-safe camera input handler:

```python
import threading
import queue
import time
from typing import Optional, Tuple, Any
import numpy as np
import cv2

class ThreadedCameraInput:
    """Thread-safe camera input handler."""
    
    def __init__(self, camera_id=0, buffer_size=3):
        self.camera_id = camera_id
        self.frame_queue = queue.Queue(maxsize=buffer_size)
        self.running = False
        self.thread = None
        self.camera = None
        self.last_frame_time = 0
        self.fps = 0
        self.frame_count = 0
        
    def start(self) -> bool:
        """Start camera capture thread."""
        if self.thread and self.thread.is_alive():
            return True  # Already running
            
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True
        
    def stop(self) -> None:
        """Stop camera capture thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
    def _capture_loop(self) -> None:
        """Camera capture thread function."""
        while self.running and self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Calculate FPS
                current_time = time.time()
                if self.last_frame_time > 0:
                    time_diff = current_time - self.last_frame_time
                    if time_diff > 0:
                        instant_fps = 1.0 / time_diff
                        self.fps = 0.9 * self.fps + 0.1 * instant_fps  # Moving average
                
                self.last_frame_time = current_time
                self.frame_count += 1
                
                # Put in queue, dropping oldest frame if full
                try:
                    self.frame_queue.put(frame, block=False)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()  # Discard oldest frame
                        self.frame_queue.put(frame, block=False)
                    except (queue.Empty, queue.Full):
                        pass  # Race condition, just drop this frame
            
            time.sleep(0.001)  # Small sleep to prevent CPU hogging
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get the latest frame (non-blocking)."""
        if not self.running or self.frame_queue.empty():
            return False, None
            
        try:
            frame = self.frame_queue.get_nowait()
            return True, frame
        except queue.Empty:
            return False, None
```

### 2. Thread-Safe Person Detection

Implement person detection in a separate thread:

```python
class ThreadedPersonDetector:
    """Thread-safe person detection handler."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.input_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.detector = None  # Will be initialized in thread
        
    def start(self) -> bool:
        """Start detection thread."""
        if self.thread and self.thread.is_alive():
            return True  # Already running
            
        self.running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        return True
        
    def stop(self) -> None:
        """Stop detection thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
    def _detection_loop(self) -> None:
        """Person detection thread function."""
        # Initialize detector in this thread
        from src.person_outline_detector import PersonOutlineDetector
        self.detector = PersonOutlineDetector(self.config_manager)
        
        while self.running:
            try:
                frame = self.input_queue.get(timeout=0.1)
                outlines = self.detector.detect(frame)
                
                # Store result, dropping oldest if full
                try:
                    self.result_queue.put((frame, outlines), block=False)
                except queue.Full:
                    try:
                        self.result_queue.get_nowait()  # Discard oldest result
                        self.result_queue.put((frame, outlines), block=False)
                    except (queue.Empty, queue.Full):
                        pass
                        
            except queue.Empty:
                continue  # No input frame available
                
    def process_frame(self, frame: np.ndarray) -> None:
        """Submit a frame for processing (non-blocking)."""
        try:
            self.input_queue.put(frame, block=False)
        except queue.Full:
            pass  # Drop frame if we can't keep up
            
    def get_latest_result(self) -> Tuple[Optional[np.ndarray], Any]:
        """Get the latest detection result (non-blocking)."""
        if self.result_queue.empty():
            return None, None
            
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None, None
```

### 3. Thread Synchronization Utilities

Create utilities to ensure safe access to shared resources:

```python
class ThreadSafeDict:
    """Thread-safe dictionary implementation."""
    
    def __init__(self, initial_dict=None):
        self._dict = initial_dict or {}
        self._lock = threading.RLock()
        
    def get(self, key, default=None):
        """Thread-safe get operation."""
        with self._lock:
            return self._dict.get(key, default)
            
    def set(self, key, value):
        """Thread-safe set operation."""
        with self._lock:
            self._dict[key] = value
            
    def delete(self, key):
        """Thread-safe delete operation."""
        with self._lock:
            if key in self._dict:
                del self._dict[key]
                
    def items(self):
        """Return a copy of items for thread-safe iteration."""
        with self._lock:
            return list(self._dict.items())
```

### 4. Thread Pool for Parallelized Processing

Implement a thread pool for handling multiple parallel tasks:

```python
class ThreadPool:
    """Thread pool for parallel processing tasks."""
    
    def __init__(self, num_workers=4):
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = False
        
        for _ in range(num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            self.workers.append(worker)
            
    def start(self):
        """Start worker threads."""
        self.running = True
        for worker in self.workers:
            worker.start()
            
    def stop(self):
        """Stop worker threads."""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=1.0)
            
    def submit_task(self, task_func, *args, **kwargs):
        """Submit a task for execution."""
        self.task_queue.put((task_func, args, kwargs))
        
    def _worker_loop(self):
        """Worker thread function."""
        while self.running:
            try:
                task_func, args, kwargs = self.task_queue.get(timeout=0.1)
                try:
                    task_func(*args, **kwargs)
                except Exception as e:
                    print(f"Task error: {e}")
                self.task_queue.task_done()
            except queue.Empty:
                continue
```

### 5. Integration with Main Application Loop

Update the main application loop to use the threaded components:

```python
def main():
    # Initialize components
    config_manager = ConfigManager("config/settings.json")
    
    # Initialize threaded components
    camera = ThreadedCameraInput()
    camera.start()
    
    person_detector = ThreadedPersonDetector(config_manager)
    person_detector.start()
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Get latest frame
        ret, frame = camera.read()
        if ret:
            # Submit for async processing
            person_detector.process_frame(frame)
            
        # Get latest detection results
        detected_frame, outlines = person_detector.get_latest_result()
        
        # Update and render
        # ...
        
        clock.tick(60)  # Target 60 FPS
        
    # Cleanup
    camera.stop()
    person_detector.stop()
```

## Testing Strategy

1. Create stress tests to verify thread safety under load
2. Verify frame rate stability with parallel processing
3. Test error handling in threaded components
4. Test shutdown and cleanup procedures

## Expected Outcomes

1. **Improved Performance**: Higher frame rates during intensive operations
2. **Consistent UI**: No UI freezing during long-running operations
3. **Better Resource Utilization**: Efficient use of multi-core processors
4. **Enhanced Scalability**: Easy to add more parallel processing features

## Success Criteria

- Frame rate remains stable even during intensive detection operations
- No race conditions or data corruption under normal operation
- Graceful shutdown of all threads when application exits
- Easy to understand threading model for future development