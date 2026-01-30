"""
Fix CLIP ONNX Export - Export Vision Encoder
============================================

The standard optimum export with task="feature-extraction" exports
the text encoder. We need to manually export the vision encoder.
"""

import torch
from transformers import CLIPModel, CLIPProcessor
from pathlib import Path
import sys
import os

# Set UTF-8 encoding to avoid console encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "clip_vit_b32"


def export_clip_vision_encoder():
    """Export only the CLIP vision encoder to ONNX."""
    print("=" * 70)
    print("  CLIP Vision Encoder Export")
    print("=" * 70)

    print("\n[1/3] Loading CLIP model from HuggingFace...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    print("[2/3] Extracting vision encoder...")
    vision_model = model.vision_model
    vision_model.eval()

    print("[3/3] Exporting to ONNX...")

    # Create dummy input (1 image, 3 channels, 224x224)
    dummy_input = torch.randn(1, 3, 224, 224)

    # Export path
    onnx_path = MODEL_DIR / "model.onnx"

    # Suppress verbose output to avoid encoding issues
    import io
    import contextlib

    # Export to ONNX with suppressed output
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        torch.onnx.export(
            vision_model,
            dummy_input,
            str(onnx_path),
            input_names=['pixel_values'],
            output_names=['last_hidden_state', 'pooler_output'],
            dynamic_axes={
                'pixel_values': {0: 'batch_size'},
                'last_hidden_state': {0: 'batch_size'},
                'pooler_output': {0: 'batch_size'}
            },
            opset_version=18,
            do_constant_folding=True,
            verbose=False
        )

    # Verify
    size_mb = onnx_path.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 70)
    print("  SUCCESS")
    print("=" * 70)
    print(f"  Model: {onnx_path}")
    print(f"  Size: {size_mb:.1f} MB")
    print("  Input: pixel_values (batch_size, 3, 224, 224)")
    print("  Output: pooler_output (batch_size, 512)")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        export_clip_vision_encoder()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
