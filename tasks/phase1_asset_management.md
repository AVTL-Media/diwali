# Asset Management System

## Overview

This task focuses on creating a dedicated Asset Management System for the Diwali Projection System to improve asset loading, organization, and management.

## Current State

The application currently loads assets directly in various components without centralization. This leads to potential duplication, lack of error handling for missing assets, and no reuse of common resources.

## Target State

A centralized Asset Management System that:

1. Provides organized access to all visual and audio assets
2. Handles error cases gracefully with fallback assets
3. Optimizes loading through caching and lazy loading
4. Supports different asset types with appropriate loading strategies

## Implementation Plan

### 1. Define Asset Manager Class

```python
import os
import pygame
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import time
import threading

class AssetManager:
    """Centralized asset management for the Diwali Projection System."""
    
    def __init__(self, base_path="assets", config_manager=None):
        self.base_path = base_path
        self.config_manager = config_manager
        self.cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        self.default_assets: Dict[str, Any] = {}
        self._initialize_defaults()
        
    def _initialize_defaults(self) -> None:
        """Create default assets to use as fallbacks."""
        # Create a small default surface
        default_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        default_surface.fill((255, 0, 255))  # Magenta for visibility
        pygame.draw.rect(default_surface, (0, 0, 0), (0, 0, 64, 64), 2)
        pygame.draw.line(default_surface, (0, 0, 0), (0, 0), (64, 64), 2)
        pygame.draw.line(default_surface, (0, 0, 0), (0, 64), (64, 0), 2)
        
        self.default_assets["image"] = default_surface
        
    def get_image(self, relative_path: str, use_alpha: bool = True) -> pygame.Surface:
        """
        Load an image with proper error handling.
        
        Args:
            relative_path: Path relative to assets directory
            use_alpha: Whether to load with alpha channel
            
        Returns:
            Loaded image surface or default image if loading fails
        """
        cache_key = f"image:{relative_path}:{use_alpha}"
        
        with self.cache_lock:
            # Return from cache if available
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        try:
            full_path = os.path.join(self.base_path, relative_path)
            if not os.path.exists(full_path):
                print(f"Warning: Image not found: {full_path}")
                return self.default_assets["image"]
                
            image = pygame.image.load(full_path)
            if use_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
                
            # Store in cache
            with self.cache_lock:
                self.cache[cache_key] = image
                
            return image
            
        except Exception as e:
            print(f"Error loading image {relative_path}: {e}")
            return self.default_assets["image"]
            
    def get_image_sequence(self, directory: str) -> List[pygame.Surface]:
        """
        Load a sequence of images from a directory.
        
        Args:
            directory: Directory relative to assets containing image sequence
            
        Returns:
            List of loaded image surfaces
        """
        try:
            full_path = os.path.join(self.base_path, directory)
            if not os.path.exists(full_path):
                print(f"Warning: Directory not found: {full_path}")
                return [self.default_assets["image"]]
                
            # Find all image files
            image_files = [f for f in os.listdir(full_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            image_files.sort()  # Sort for consistent order
            
            images = []
            for image_file in image_files:
                relative_path = os.path.join(directory, image_file)
                images.append(self.get_image(relative_path))
                
            return images if images else [self.default_assets["image"]]
            
        except Exception as e:
            print(f"Error loading image sequence from {directory}: {e}")
            return [self.default_assets["image"]]
            
    def get_random_image(self, directory: str) -> pygame.Surface:
        """
        Load a random image from a directory.
        
        Args:
            directory: Directory relative to assets containing images
            
        Returns:
            Randomly selected image surface
        """
        import random
        images = self.get_image_sequence(directory)
        return random.choice(images) if images else self.default_assets["image"]
        
    def preload_assets(self, asset_list: List[str]) -> None:
        """
        Preload a list of assets into the cache.
        
        Args:
            asset_list: List of asset paths to preload
        """
        for asset_path in asset_list:
            if asset_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.get_image(asset_path)
                
    def clear_cache(self) -> None:
        """Clear the asset cache to free memory."""
        with self.cache_lock:
            self.cache.clear()
```

### 2. Implement Asset Categories and Type-Specific Methods

Extend the AssetManager with category-specific methods:

```python
def get_diya_image(self, index: Optional[int] = None) -> pygame.Surface:
    """
    Get a diya image, either by index or randomly.
    
    Args:
        index: Optional index of the specific diya to load
        
    Returns:
        Diya image surface
    """
    if index is not None:
        return self.get_image(f"diyas/{index}.png")
    else:
        return self.get_random_image("diyas")
        
def get_rangoli_pattern(self, index: Optional[int] = None) -> pygame.Surface:
    """
    Get a rangoli pattern, either by index or randomly.
    
    Args:
        index: Optional index of the specific rangoli to load
        
    Returns:
        Rangoli pattern surface
    """
    if index is not None:
        return self.get_image(f"rangoli/{index}.png")
    else:
        return self.get_random_image("rangoli")
        
def get_background(self) -> pygame.Surface:
    """
    Get the background image.
    
    Returns:
        Background surface
    """
    return self.get_image("diwali_bg.jpg", use_alpha=False)
```

### 3. Add Sound Asset Management

```python
def get_sound(self, relative_path: str) -> Optional[pygame.mixer.Sound]:
    """
    Load a sound effect with proper error handling.
    
    Args:
        relative_path: Path relative to assets directory
        
    Returns:
        Loaded sound or None if loading fails
    """
    cache_key = f"sound:{relative_path}"
    
    with self.cache_lock:
        # Return from cache if available
        if cache_key in self.cache:
            return self.cache[cache_key]
    
    try:
        full_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(full_path):
            print(f"Warning: Sound not found: {full_path}")
            return None
            
        sound = pygame.mixer.Sound(full_path)
        
        # Store in cache
        with self.cache_lock:
            self.cache[cache_key] = sound
            
        return sound
        
    except Exception as e:
        print(f"Error loading sound {relative_path}: {e}")
        return None
```

### 4. Add Asset Validation

```python
def validate_assets(self) -> Dict[str, List[str]]:
    """
    Validate that all required assets exist.
    
    Returns:
        Dictionary with lists of missing assets by category
    """
    missing_assets = {
        "diyas": [],
        "rangoli": [],
        "background": [],
        "sounds": []
    }
    
    # Check background
    bg_path = "diwali_bg.jpg"
    if not os.path.exists(os.path.join(self.base_path, bg_path)):
        missing_assets["background"].append(bg_path)
    
    # Check diyas directory
    diyas_dir = os.path.join(self.base_path, "diyas")
    if not os.path.exists(diyas_dir):
        missing_assets["diyas"].append("diyas directory")
    else:
        diya_files = [f for f in os.listdir(diyas_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not diya_files:
            missing_assets["diyas"].append("No diya images found")
    
    # Check rangoli directory
    rangoli_dir = os.path.join(self.base_path, "rangoli")
    if not os.path.exists(rangoli_dir):
        missing_assets["rangoli"].append("rangoli directory")
    else:
        rangoli_files = [f for f in os.listdir(rangoli_dir) 
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not rangoli_files:
            missing_assets["rangoli"].append("No rangoli images found")
    
    return missing_assets
```

### 5. Implement Asset Configuration

Update the settings.json schema to include asset configuration:

```json
{
  "assets": {
    "preload": ["diwali_bg.jpg", "diyas/1.png", "rangoli/1.png"],
    "diya_count": 3,
    "rangoli_count": 3
  }
}
```

## Implementation Tasks

### 1. Asset Manager Development

- [ ] Create `src/asset_manager.py` with the AssetManager class
- [ ] Implement image loading with error handling
- [ ] Add sound asset loading support
- [ ] Create default fallback assets
- [ ] Add asset validation functionality

### 2. Asset Organization

- [ ] Organize assets into clear categories:
  - [ ] Background images
  - [ ] Diya images
  - [ ] Rangoli patterns
  - [ ] Sound effects
- [ ] Create README files for each asset directory explaining usage

### 3. Integration Plan

- [ ] Update `visual_generator.py` to use AssetManager
- [ ] Replace direct asset loading with AssetManager calls
- [ ] Add asset preloading during application startup
- [ ] Implement graceful fallbacks for missing assets

## Expected Outcomes

1. **Centralized Asset Access**: Single source for all asset loading
2. **Error Resilience**: Graceful handling of missing assets
3. **Performance Improvements**: Cached assets and optimized loading
4. **Better Organization**: Clear structure for managing different asset types

## Testing Strategy

1. Create unit tests for the AssetManager class
2. Test behavior with missing assets
3. Verify performance with asset caching
4. Test random asset selection

## Success Criteria

- All asset loading in the application uses the AssetManager
- Missing assets are handled gracefully with visible fallbacks
- Asset loading performance is improved through caching
- Clear asset organization improves maintainability