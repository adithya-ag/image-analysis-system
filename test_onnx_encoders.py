"""
Test MobileCLIP ONNX Encoders

Verifies that image and text encoders produce reasonable embeddings.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

import numpy as np
from config import Config
from analysis.mobileclip import MobileCLIP

# Initialize MobileCLIP
print("="*70)
print("TESTING MOBILECLIP ONNX ENCODERS")
print("="*70)

config = Config(model_name='mobileclip')
model = MobileCLIP(config)

# Test 1: Generate text embedding
print("\n📝 Test 1: Text Embedding")
print("-"*70)
text = "a photo of a cat"
text_emb = model.generate_text_embedding(text)
print(f"Text: '{text}'")
print(f"Embedding shape: {text_emb.shape}")
print(f"Embedding norm: {np.linalg.norm(text_emb):.4f} (should be ~1.0)")
print(f"Embedding range: [{text_emb.min():.4f}, {text_emb.max():.4f}]")
print(f"First 10 values: {text_emb[:10]}")

# Test 2: Generate image embedding
print("\n🖼️  Test 2: Image Embedding")
print("-"*70)

# Find first test image
test_images_dir = Path("data/test_images")
image_files = list(test_images_dir.glob("*.jpg"))[:3]  # First 3 images

if not image_files:
    print("❌ No test images found")
else:
    for img_path in image_files:
        img_emb = model.generate_embedding(str(img_path))
        print(f"\nImage: {img_path.name}")
        print(f"  Shape: {img_emb.shape}")
        print(f"  Norm: {np.linalg.norm(img_emb):.4f} (should be ~1.0)")
        print(f"  Range: [{img_emb.min():.4f}, {img_emb.max():.4f}]")

# Test 3: Self-similarity check
print("\n🔍 Test 3: Self-Similarity")
print("-"*70)
print("Comparing same embeddings (should be ~0.0 distance):")

# Text self-similarity
text_emb2 = model.generate_text_embedding(text)
text_dist = np.linalg.norm(text_emb - text_emb2)
print(f"  Text vs Text: {text_dist:.6f} (should be ~0.0)")

if image_files:
    # Image self-similarity
    img_emb2 = model.generate_embedding(str(image_files[0]))
    img_dist = np.linalg.norm(img_emb - img_emb2)
    print(f"  Image vs Image: {img_dist:.6f} (should be ~0.0)")

# Test 4: Cross-modal distance
print("\n🔄 Test 4: Cross-Modal Distance")
print("-"*70)
if image_files:
    # Random text vs image
    cross_dist = np.linalg.norm(text_emb - img_emb)
    print(f"Text '{text}' vs Random Image:")
    print(f"  L2 Distance: {cross_dist:.4f}")
    print(f"  Expected: 0.5-1.5 for unrelated, <0.5 for related")

    if cross_dist > 1.7:
        print("  ⚠️  WARNING: Distance too high! Embeddings might be misaligned!")
    elif cross_dist < 0.3:
        print("  ⚠️  WARNING: Distance too low! Something seems off!")
    else:
        print("  ✅ Distance seems reasonable")

print("\n" + "="*70)
print("✅ Test complete")
print("="*70)
