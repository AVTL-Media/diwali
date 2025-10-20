"""
Audio Detection Module for Diwali Projection System.
Detects audio spikes (like claps) to trigger visual effects.
"""

import numpy as np
import sounddevice as sd
import json
import os
import time
import threading
from pathlib import Path


class AudioDetector:
    """Detects audio spikes in real-time from microphone input."""
    
    def __init__(self, config_path=None):
        """Initialize audio detector with configuration."""
        # Default config
        self.config = {
            "enabled": True,
            "threshold_multiplier": 2.0,
            "sample_rate": 44100,
            "chunk_size": 1024,
            "window_size": 0.5
        }
        
        # Load config if provided
        if config_path:
            with open(config_path, 'r') as f:
                all_config = json.load(f)
                if "audio_detection" in all_config:
                    self.config.update(all_config["audio_detection"])
        
        # Audio detection variables
        self.is_running = False
        self.audio_spike_detected = False
        self.spike_timestamp = 0
        self.baseline_volume = 0
        self.current_volume = 0
        self.baseline_samples = []
        self.max_baseline_samples = 100
        self.audio_thread = None
        self.calibration_complete = False
        self.spike_duration = 0.5  # seconds to keep spike flag active
        
    def start(self):
        """Start audio detection in a background thread."""
        if not self.config["enabled"]:
            print("Audio detection is disabled in configuration")
            return False
            
        try:
            self.is_running = True
            self.audio_thread = threading.Thread(target=self._audio_processing_loop)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            return True
        except Exception as e:
            print(f"Error starting audio detection: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop audio detection."""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
            self.audio_thread = None
    
    def _audio_processing_loop(self):
        """Background thread for continuous audio processing."""
        try:
            # Calculate number of frames based on window size
            window_frames = int(self.config["sample_rate"] * self.config["window_size"])
            
            def audio_callback(indata, frames, time, status):
                """Callback for audio stream to process incoming audio chunks."""
                if status:
                    print(f"Audio status: {status}")
                    return
                    
                # Calculate volume (RMS amplitude)
                volume = np.sqrt(np.mean(indata**2))
                self.current_volume = volume
                
                # During calibration, collect baseline samples
                if not self.calibration_complete:
                    self.baseline_samples.append(volume)
                    if len(self.baseline_samples) >= self.max_baseline_samples:
                        # Calculate baseline as the average of collected samples
                        self.baseline_volume = np.mean(self.baseline_samples)
                        self.calibration_complete = True
                        print(f"Audio calibration complete. Baseline: {self.baseline_volume:.6f}")
                else:
                    # Detect spike based on threshold multiplier
                    threshold = self.baseline_volume * self.config["threshold_multiplier"]
                    if volume > threshold:
                        self.audio_spike_detected = True
                        import time as py_time
                        self.spike_timestamp = py_time.time()
                        # print(f"Audio spike detected! Volume: {volume:.6f}, Threshold: {threshold:.6f}")
            
            # Start audio stream
            with sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=self.config["sample_rate"],
                blocksize=self.config["chunk_size"]
            ):
                print("Audio detection started")
                # Keep thread running while is_running flag is True
                while self.is_running:
                    # Reset spike flag after duration expires
                    if (self.audio_spike_detected and 
                        time.time() - self.spike_timestamp > self.spike_duration):
                        self.audio_spike_detected = False
                    
                    time.sleep(0.01)  # Sleep to prevent CPU usage
                    
        except Exception as e:
            print(f"Audio processing error: {e}")
            self.is_running = False
    
    def is_spike_detected(self):
        """Check if an audio spike was recently detected."""
        return self.audio_spike_detected
    
    def get_volume_level(self):
        """Get current audio volume level (0.0 to 1.0)."""
        if not self.calibration_complete or self.baseline_volume == 0:
            return 0.0
        # Normalize volume level relative to baseline
        normalized = self.current_volume / (self.baseline_volume * 3.0)
        return min(max(normalized, 0.0), 1.0)
    
    def is_calibrated(self):
        """Check if the audio detection is calibrated."""
        return self.calibration_complete


# For testing
if __name__ == "__main__":
    import cv2
    import time
    
    # Find config path relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_path = current_dir.parent / "config" / "settings.json"
    
    # Create a simple visualization window
    width, height = 800, 400
    window_name = "Audio Detection Test"
    cv2.namedWindow(window_name)
    
    # Create and start audio detector
    audio_detector = AudioDetector(config_path)
    if audio_detector.start():
        try:
            # Wait for calibration
            print("Calibrating audio detection... Please be quiet.")
            while not audio_detector.is_calibrated() and cv2.waitKey(1) != ord('q'):
                time.sleep(0.1)
            
            print("Calibration complete! Make some noise to see detection.")
            
            # Visualization loop
            while True:
                # Create a black canvas
                canvas = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Get current volume level
                volume = audio_detector.get_volume_level()
                bar_height = int(volume * height)
                
                # Draw volume bar
                cv2.rectangle(
                    canvas, 
                    (50, height - bar_height), 
                    (width - 50, height),
                    (0, 255, 0) if audio_detector.is_spike_detected() else (0, 0, 255), 
                    -1
                )
                
                # Draw spike indicator
                if audio_detector.is_spike_detected():
                    cv2.putText(
                        canvas,
                        "SPIKE DETECTED!", 
                        (width // 4, height // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.5, 
                        (255, 255, 0), 
                        2
                    )
                
                # Show information
                cv2.putText(
                    canvas,
                    f"Volume: {volume:.2f}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (255, 255, 255), 
                    2
                )
                
                # Show the canvas
                cv2.imshow(window_name, canvas)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            audio_detector.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start audio detection")