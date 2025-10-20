from RandomMandala import RandomMandala
import inspect

print("Signature of to_image:", inspect.signature(RandomMandala.to_image))

# Test with different parameters
mandala = RandomMandala()

# Try some common parameters that might work
print("\nTrying different parameter combinations...")
try:
    img = mandala.to_image()
    print("Successfully generated with no parameters")
except Exception as e:
    print(f"Error with no parameters: {e}")

try:
    img = mandala.to_image(size=400)
    print("Successfully generated with size=400")
except Exception as e:
    print(f"Error with size=400: {e}")

try:
    img = mandala.to_image(width=400, height=400)
    print("Successfully generated with width=400, height=400")
except Exception as e:
    print(f"Error with width/height: {e}")

