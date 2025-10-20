from RandomMandala import RandomMandala
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image
import random

def create_mandala(size=800, n_arms=8, seed=None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
        
    # Create a mandala with specific parameters
    mandala = RandomMandala()
    
    # Set up the figure first (required)
    fig, ax = plt.subplots(figsize=(size/100, size/100), dpi=100)
    mandala.set_figure(fig)
    mandala.set_axes(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')  # Hide axes
    
    # Generate random seed points
    n_points = random.randint(3, 7)
    points = np.random.rand(n_points, 2) * 0.4 + 0.3  # Keep points in the middle area
    
    # Set up the mandala parameters
    mandala.set_seed_points(points)
    mandala.set_symmetric(True)
    mandala.set_angle(2 * np.pi / n_arms)  # Evenly divide the circle
    
    # Choose random colors
    colors = []
    for _ in range(n_points):
        r, g, b = np.random.random(3)
        colors.append((r, g, b, 0.7))  # Add some transparency
    
    # Create the mandala image - we need to pass the points
    # Since we already set the seed points, we can use those
    mandala_points = mandala.take_seed_points()
    mandala.to_bezier_curve(points=mandala_points)
    
    # Generate multiple rotated copies for a full mandala
    for i in range(n_arms):
        angle = i * 2 * np.pi / n_arms
        rotated_points = rotate_points(mandala_points, angle)
        mandala.to_bezier_curve(points=rotated_points, color=colors[i % len(colors)])
    
    # Get the image data
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf)
    
    # Display some information
    print(f"Created mandala with shape: {img.size}")
    
    plt.close(fig)  # Close the figure to free memory
    return img

def rotate_points(points, angle):
    """Rotate points around the center (0.5, 0.5)"""
    # Translate to origin
    points = points.copy() - 0.5
    
    # Rotation matrix
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    
    # Apply rotation and translate back
    rotated = np.dot(points, R.T) + 0.5
    return rotated

# Create and save a mandala
img = create_mandala(size=800, n_arms=12, seed=42)
img.save('test_mandala.png')
print(f"Saved mandala image to test_mandala.png")

