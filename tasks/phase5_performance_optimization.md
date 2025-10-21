# Performance Optimization

## Overview

This task focuses on improving the performance of the Diwali Projection System by implementing optimization strategies, particularly around surface caching and resource management.

## Current State

The application currently creates and destroys large surfaces frequently, which is inefficient and can impact frame rates. Some visual elements are recomputed each frame even when unchanged.

## Target State

An optimized application with:
- Cached surfaces for frequently used visual elements
- Optimized camera processing to maintain consistent frame rates
- Strategic memory management to reduce garbage collection pauses

## Implementation Plan

### 1. Surface Caching System

Create a caching system for frequently rendered surfaces:

```python
class SurfaceCache:
    """Cache for frequently used surfaces."""
    
    def __init__(self, max_size=20):
        self.cache = {}
        self.max_size = max_size
        self.access_counts = {}
        
    def get(self, key):
        """Get a surface from cache."""
        if key in self.cache:
            self.access_counts[key] += 1
            return self.cache[key].copy()
        return None
        
    def store(self, key, surface):
        """Store a surface in cache."""
        # Evict least recently used item if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
            
        self.cache[key] = surface.copy()
        self.access_counts[key] = 0
        
    def invalidate(self, key):
        """Remove a surface from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_counts[key]
            
    def _evict_lru(self):
        """Evict least recently used surface."""
        if not self.cache:
            return
            
        min_key = min(self.access_counts.items(), key=lambda x: x[1])[0]
        del self.cache[min_key]
        del self.access_counts[min_key]
```

### 2. Rangoli Pattern Optimization

Create pre-rendered rangoli patterns at different scales and rotations:

- Pre-render common rangoli pattern sizes
- Cache rotated versions at regular intervals (e.g. every 10 degrees)
- Interpolate between cached versions for smooth animation

### 3. Camera Processing Optimization

- Implement frame skipping when processing is falling behind
- Resize input frames to lower resolution for processing when needed
- Use threading to handle camera processing in parallel with rendering

### 4. Asset Management

- Load assets on demand rather than all at startup
- Implement progressive loading of assets
- Unload unused assets when memory pressure is high

### 5. Performance Profiling

- Add performance monitoring instrumentation
- Track frame rates and rendering times
- Identify and address bottlenecks

## Testing Strategy

1. Establish performance baseline before optimization
2. Create performance tests for key scenarios
3. Measure improvements for each optimization
4. Ensure visual quality is not compromised

## Expected Outcomes

1. **Higher Frame Rates**: Target consistent 60 FPS on reference hardware
2. **Reduced Memory Usage**: Optimize memory footprint by at least 30%
3. **Smoother Transitions**: Eliminate stutters during state transitions
4. **Faster Startup**: Reduce initial loading time by implementing progressive loading

## Success Criteria

- All animations run at target frame rate (60 FPS) on reference hardware
- Memory usage remains stable over extended periods
- CPU utilization stays below 50% during normal operation
- No visual artifacts from optimization techniques