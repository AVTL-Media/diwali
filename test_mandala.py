from RandomMandala import RandomMandala
import inspect

# Print initialization signature
print("Signature:", inspect.signature(RandomMandala.__init__))

# Create a basic mandala and inspect the object
mandala = RandomMandala()
print("\nMethods available:")
methods = [method for method in dir(mandala) if not method.startswith('_')]
for method in methods:
    print(f"- {method}")

# Try to generate a mandala
print("\nTrying to generate a mandala...")
try:
    img = mandala.to_image(dim=400)
    print("Successfully generated mandala with to_image()")
except Exception as e:
    print(f"Error with to_image(): {e}")

