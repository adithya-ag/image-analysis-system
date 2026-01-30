"""
Fix CLIP ONNX Export - Export Vision Encoder Using Optimum
===========================================================

Export CLIP vision encoder using optimum with custom configuration.
"""

from pathlib import Path
from transformers import CLIPModel, CLIPProcessor
from optimum.onnxruntime import ORTModelForFeatureExtraction
from optimum.exporters.onnx import main_export
import sys
import shutil

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "clip_vit_b32"


def export_clip_vision():
    """Export CLIP vision encoder using custom approach."""
    print("=" * 70)
    print("  CLIP Vision Encoder Export (Method 2)")
    print("=" * 70)

    # Load the model to extract vision encoder
    print("\n[1/4] Loading full CLIP model...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    # Create a temporary directory for vision-only model
    temp_dir = Path("temp_vision_model")
    temp_dir.mkdir(exist_ok=True)

    try:
        print("[2/4] Saving vision encoder separately...")
        # Save just the vision model
        model.vision_model.save_pretrained(temp_dir)

        # Also save the processor/config
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        processor.save_pretrained(temp_dir)

        print("[3/4] Exporting vision encoder to ONNX...")
        # Now export this vision-only model
        from optimum.exporters.onnx import export_models
        from optimum.exporters.tasks import TasksManager

        # Manual export
        import subprocess
        result = subprocess.run(
            [
                sys.executable, "-m", "optimum.exporters.onnx",
                "--model", str(temp_dir),
                "--task", "feature-extraction",
                str(MODEL_DIR / "vision_temp")
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Export failed: {result.stderr}")
            return False

        print("[4/4] Moving exported model...")
        # Move the exported model to replace the old one
        exported_model = MODEL_DIR / "vision_temp" / "model.onnx"
        target_model = MODEL_DIR / "model.onnx"

        if exported_model.exists():
            shutil.copy(exported_model, target_model)
            shutil.rmtree(MODEL_DIR / "vision_temp", ignore_errors=True)

            size_mb = target_model.stat().st_size / (1024 * 1024)
            print(f"\n{'=' * 70}")
            print(f"  SUCCESS")
            print(f"{'=' * 70}")
            print(f"  Model: {target_model}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"{'=' * 70}")
            return True
        else:
            print("ERROR: Export completed but model not found")
            return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        success = export_clip_vision()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
