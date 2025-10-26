# Phase 1, Task 2: AssetManager Implementation

**Phase**: 1 - Foundation
**Week**: 1
**Agent Assignment**: Agent B
**Can Run in Parallel**: ✅ Yes (with Task 1: ConfigManager)
**Dependencies**: ConfigManager (for using config, but can start independently)
**Estimated Duration**: 3-4 days

## Overview

Implement the AssetManager class for centralized asset loading with caching, error handling, and fallback assets.

## Deliverables

1. `src/asset_manager.py` - AssetManager class implementation
2. Unit tests in `tests/test_asset_manager.py`
3. Default fallback assets
4. Documentation

## Implementation Steps

### Step 1: Create AssetManager Class (Day 1-2)

```python
# src/asset_manager.py
import os
import pygame
import threading
from typing import Dict, List, Any, Optional

class AssetManager:
    """Centralized asset management with caching and fallbacks."""

    def __init__(self, base_path="assets", config_manager=None):
        self.base_path = base_path
        self.config_manager = config_manager
        self.cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        self.default_assets: Dict[str, Any] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Create default fallback assets."""
        # Default image (magenta with X)
        default_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        default_surface.fill((255, 0, 255))
        pygame.draw.rect(default_surface, (0, 0, 0), (0, 0, 64, 64), 2)
        pygame.draw.line(default_surface, (0, 0, 0), (0, 0), (64, 64), 2)
        pygame.draw.line(default_surface, (0, 0, 0), (0, 64), (64, 0), 2)
        self.default_assets["image"] = default_surface

    def get_image(self, relative_path: str, use_alpha: bool = True) -> pygame.Surface:
        """Load image with caching and error handling."""
        cache_key = f"image:{relative_path}:{use_alpha}"

        with self.cache_lock:
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

            with self.cache_lock:
                self.cache[cache_key] = image

            return image

        except Exception as e:
            print(f"Error loading image {relative_path}: {e}")
            return self.default_assets["image"]

    def get_image_sequence(self, directory: str) -> List[pygame.Surface]:
        """Load all images from a directory."""
        try:
            full_path = os.path.join(self.base_path, directory)
            if not os.path.exists(full_path):
                print(f"Warning: Directory not found: {full_path}")
                return [self.default_assets["image"]]

            image_files = [f for f in os.listdir(full_path)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            image_files.sort()

            images = []
            for image_file in image_files:
                relative_path = os.path.join(directory, image_file)
                images.append(self.get_image(relative_path))

            return images if images else [self.default_assets["image"]]

        except Exception as e:
            print(f"Error loading image sequence from {directory}: {e}")
            return [self.default_assets["image"]]

    def get_random_image(self, directory: str) -> pygame.Surface:
        """Load a random image from directory."""
        import random
        images = self.get_image_sequence(directory)
        return random.choice(images)

    def get_diya_image(self, index: Optional[int] = None) -> pygame.Surface:
        """Get a diya image by index or randomly."""
        if index is not None:
            return self.get_image(f"diyas/{index}.png")
        return self.get_random_image("diyas")

    def get_rangoli_pattern(self, index: Optional[int] = None) -> pygame.Surface:
        """Get a rangoli pattern by index or randomly."""
        if index is not None:
            return self.get_image(f"rangoli/{index}.png")
        return self.get_random_image("rangoli")

    def get_background(self) -> pygame.Surface:
        """Get the background image."""
        return self.get_image("diwali_bg.jpg", use_alpha=False)

    def preload_assets(self, asset_list: List[str]) -> None:
        """Preload assets into cache."""
        for asset_path in asset_list:
            if asset_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.get_image(asset_path)

    def clear_cache(self) -> None:
        """Clear the asset cache."""
        with self.cache_lock:
            self.cache.clear()

    def validate_assets(self) -> Dict[str, List[str]]:
        """Validate that required assets exist."""
        missing = {
            "diyas": [],
            "rangoli": [],
            "background": []
        }

        # Check background
        if not os.path.exists(os.path.join(self.base_path, "diwali_bg.jpg")):
            missing["background"].append("diwali_bg.jpg")

        # Check diyas directory
        diyas_dir = os.path.join(self.base_path, "diyas")
        if not os.path.exists(diyas_dir):
            missing["diyas"].append("diyas directory missing")

        # Check rangoli directory
        rangoli_dir = os.path.join(self.base_path, "rangoli")
        if not os.path.exists(rangoli_dir):
            missing["rangoli"].append("rangoli directory missing")

        return missing
```

### Step 2: Write Unit Tests (Day 2-3)

```python
# tests/test_asset_manager.py
import unittest
import pygame
import tempfile
import os
from pathlib import Path
from src.asset_manager import AssetManager

class TestAssetManager(unittest.TestCase):

    def setUp(self):
        """Create temporary asset directory."""
        pygame.init()
        self.temp_dir = tempfile.mkdtemp()
        self.manager = AssetManager(base_path=self.temp_dir)

        # Create test image
        test_surface = pygame.Surface((100, 100))
        test_surface.fill((255, 0, 0))
        test_image_path = os.path.join(self.temp_dir, "test.png")
        pygame.image.save(test_surface, test_image_path)

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
        pygame.quit()

    def test_get_existing_image(self):
        """Test loading existing image."""
        image = self.manager.get_image("test.png")
        self.assertIsInstance(image, pygame.Surface)
        self.assertEqual(image.get_size(), (100, 100))

    def test_get_missing_image_returns_default(self):
        """Test that missing image returns default."""
        image = self.manager.get_image("nonexistent.png")
        self.assertIsInstance(image, pygame.Surface)
        # Should be default magenta surface
        self.assertEqual(image.get_size(), (64, 64))

    def test_image_caching(self):
        """Test that images are cached."""
        image1 = self.manager.get_image("test.png")
        image2 = self.manager.get_image("test.png")
        # Should be same cached instance
        self.assertIs(image1, image2)

    def test_clear_cache(self):
        """Test cache clearing."""
        self.manager.get_image("test.png")
        self.assertEqual(len(self.manager.cache), 1)
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.cache), 0)

    def test_validate_assets(self):
        """Test asset validation."""
        missing = self.manager.validate_assets()
        # Should report missing directories
        self.assertIn("diyas directory missing", missing["diyas"])
        self.assertIn("rangoli directory missing", missing["rangoli"])
```

### Step 3: Create Asset README (Day 3)

```markdown
# Asset Organization

## Directory Structure

```
assets/
├── diwali_bg.jpg          # Background image
├── diyas/                 # Diya images
│   ├── 1.png
│   ├── 2.png
│   └── 3.png
├── rangoli/              # Rangoli patterns
│   ├── 1.png
│   ├── 2.png
│   └── 3.png
└── sounds/               # Sound effects (future)
```

## Image Requirements

- **Diyas**: PNG with transparency, ~200x200px
- **Rangoli**: PNG with transparency, ~500x500px
- **Background**: JPG, 1920x1080px

## Fallback Behavior

If assets are missing, AssetManager will:
1. Log a warning
2. Return a magenta placeholder with X
3. Continue running without crash
```

### Step 4: Documentation (Day 4)

```markdown
# AssetManager Usage

## Basic Usage

```python
from src.asset_manager import AssetManager

asset_manager = AssetManager("assets")

# Load specific image
diya = asset_manager.get_image("diyas/1.png")

# Load random image from directory
random_diya = asset_manager.get_random_image("diyas")

# Load background
bg = asset_manager.get_background()

# Preload assets
asset_manager.preload_assets(["diyas/1.png", "diyas/2.png"])
```

## Validation

```python
missing = asset_manager.validate_assets()
for category, items in missing.items():
    if items:
        print(f"Missing {category}: {items}")
```
```

## Testing Checklist

- [ ] AssetManager loads images correctly
- [ ] Missing images return default fallback
- [ ] Image caching works correctly
- [ ] Cache clearing works
- [ ] Image sequences load all files
- [ ] Random image selection works
- [ ] Asset validation detects missing files
- [ ] Thread-safe cache access works

## Integration Points

**Coordinates with:**
- Phase 1, Task 1 (ConfigManager) - Will use for configuration
- Phase 1, Task 3 (Error Handling) - Will add error handling

**Blocks:**
- Phase 2 testing tasks need this complete

## Success Criteria

✅ All unit tests pass
✅ Can load existing assets from assets/ directory
✅ Missing assets handled gracefully with fallbacks
✅ Caching improves performance
✅ Documentation complete
✅ Ready for integration in visual_generator.py
