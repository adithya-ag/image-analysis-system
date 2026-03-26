"""
Inspect MobileCLIP ONNX Text Encoder

Checks what inputs/outputs the ONNX model expects.
"""

import onnxruntime as ort
from pathlib import Path

# Load the ONNX model
model_path = Path("models/mobileclip_s2/mobileclip_text_encoder.onnx")

if not model_path.exists():
    print(f"❌ Model not found: {model_path}")
    exit(1)

print(f"📦 Loading ONNX model: {model_path}")
session = ort.InferenceSession(str(model_path))

print("\n" + "="*70)
print("INPUTS:")
print("="*70)
for inp in session.get_inputs():
    print(f"  Name: {inp.name}")
    print(f"  Shape: {inp.shape}")
    print(f"  Type: {inp.type}")
    print()

print("="*70)
print("OUTPUTS:")
print("="*70)
for out in session.get_outputs():
    print(f"  Name: {out.name}")
    print(f"  Shape: {out.shape}")
    print(f"  Type: {out.type}")
    print()

print("="*70)
print("\n✅ Inspection complete")
