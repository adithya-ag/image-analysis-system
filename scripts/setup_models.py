"""
Model Setup Script - Local-First Image Analysis System v0.1
=============================================================

Downloads and converts OpenAI CLIP ViT-B/32 to ONNX format.

v0.1 Model:
    - OpenAI CLIP ViT-B/32: Text-image embedding model (512-dim embeddings)

Deferred to v0.2 (pending optimum export support):
    - SmolVLM-500M: Idefics3 architecture not supported by optimum
    - MobileCLIP-S2: Requires custom export handling

Prerequisites:
    pip install optimum[onnxruntime] onnx
    pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu

Usage:
    python scripts/setup_models.py
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ModelSetup:
    """Handles downloading and converting CLIP ViT-B/32 to ONNX format."""

    def __init__(self):
        self.models_dir = PROJECT_ROOT / "models"
        self.models_dir.mkdir(exist_ok=True)

        # v0.1: CLIP ViT-B/32 only
        # SmolVLM and MobileCLIP deferred to v0.2
        self.models = {
            "clip_vit_b32": {
                "name": "CLIP ViT-B/32",
                "hf_model_id": "openai/clip-vit-base-patch32",
                "task": "feature-extraction",
                "output_dir": "clip_vit_b32",
                "embedding_dim": 512,
                "description": "OpenAI CLIP model for text-image embeddings",
            }
        }

    def check_prerequisites(self) -> bool:
        """Check if required packages are installed."""
        print("\n[1/4] Checking prerequisites...")

        missing = []

        # Check optimum
        try:
            import optimum
            version = getattr(optimum, '__version__', 'installed')
            print(f"      optimum: OK (v{version})")
        except ImportError:
            print("      optimum: MISSING")
            missing.append("optimum[onnxruntime]")

        # Check onnx
        try:
            import onnx
            print(f"      onnx: OK (v{onnx.__version__})")
        except ImportError:
            print("      onnx: MISSING")
            missing.append("onnx")

        # Check torch
        try:
            import torch
            print(f"      torch: OK (v{torch.__version__})")
        except ImportError:
            print("      torch: MISSING")
            missing.append("torch")

        # Check transformers
        try:
            import transformers
            print(f"      transformers: OK (v{transformers.__version__})")
        except ImportError:
            print("      transformers: MISSING")
            missing.append("transformers")

        if missing:
            print(f"\n      Missing packages: {', '.join(missing)}")
            print("      Install with:")
            print("        pip install optimum[onnxruntime] onnx transformers")
            print("        pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu")
            return False

        return True

    def check_existing_model(self, model_key: str) -> bool:
        """Check if model already exists and is valid."""
        model = self.models[model_key]
        model_dir = self.models_dir / model["output_dir"]
        model_file = model_dir / "model.onnx"

        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            if size_mb > 10:  # Sanity check: model should be > 10MB
                print(f"      {model['name']} already exists ({size_mb:.1f} MB)")
                return True
            else:
                print(f"      {model['name']} exists but seems corrupt ({size_mb:.1f} MB), re-downloading...")
                shutil.rmtree(model_dir, ignore_errors=True)
                return False
        return False

    def convert_model(self, model_key: str) -> bool:
        """Download and convert a model to ONNX using optimum."""
        model = self.models[model_key]
        output_path = self.models_dir / model["output_dir"]

        print(f"\n[3/4] Downloading and converting {model['name']}...")
        print(f"      HuggingFace Model: {model['hf_model_id']}")
        print(f"      Output Directory: {output_path}")
        print(f"      Task: {model['task']}")
        print(f"      This may take 2-5 minutes on first run...\n")

        # Build the optimum export command
        cmd = [
            sys.executable, "-m", "optimum.exporters.onnx",
            "--model", model["hf_model_id"],
            "--task", model["task"],
            str(output_path)
        ]

        try:
            # Run the conversion with real-time output
            result = subprocess.run(
                cmd,
                cwd=str(self.models_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                # Verify the model was created
                model_file = output_path / "model.onnx"
                if model_file.exists():
                    size_mb = model_file.stat().st_size / (1024 * 1024)
                    print(f"\n      {model['name']} converted successfully! ({size_mb:.1f} MB)")
                    return True
                else:
                    print(f"\n      ERROR: Conversion completed but model.onnx not found")
                    return False
            else:
                print(f"\n      ERROR: Conversion failed with return code {result.returncode}")
                self._print_manual_instructions(model_key)
                return False

        except FileNotFoundError:
            print(f"\n      ERROR: Python executable not found")
            self._print_manual_instructions(model_key)
            return False
        except Exception as e:
            print(f"\n      ERROR: {type(e).__name__}: {e}")
            self._print_manual_instructions(model_key)
            return False

    def _print_manual_instructions(self, model_key: str) -> None:
        """Print manual conversion instructions if automatic fails."""
        model = self.models[model_key]

        print("\n      MANUAL CONVERSION INSTRUCTIONS:")
        print("      --------------------------------")
        print(f"      cd {self.models_dir}")
        print(f"      optimum-cli export onnx \\")
        print(f"          --model {model['hf_model_id']} \\")
        print(f"          --task {model['task']} \\")
        print(f"          {model['output_dir']}/")

    def create_config(self) -> None:
        """Create model configuration file."""
        print("\n[4/4] Creating model configuration...")

        config = {
            "_comment": "Local-First Image Analysis System v0.1 - Model Configuration",
            "_note": "v0.1 uses CLIP ViT-B/32 only. MobileCLIP and SmolVLM deferred to v0.2.",
            "version": "0.1.0",
            "default_model": "clip_vit_b32",
            "model_dir": str(self.models_dir),
            "models": {}
        }

        # Add model info
        for key, model in self.models.items():
            model_path = self.models_dir / model["output_dir"] / "model.onnx"
            exists = model_path.exists()
            size_mb = model_path.stat().st_size / (1024 * 1024) if exists else 0

            config["models"][key] = {
                "name": model["name"],
                "hf_model_id": model["hf_model_id"],
                "path": str(model_path),
                "embedding_dim": model["embedding_dim"],
                "description": model["description"],
                "exists": exists,
                "size_mb": round(size_mb, 1) if exists else None
            }

        config_path = self.models_dir / "model_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"      Configuration saved to: {config_path}")

    def run(self) -> bool:
        """Run complete setup process."""
        print("=" * 65)
        print("  MODEL SETUP - Local-First Image Analysis System v0.1")
        print("  Model: OpenAI CLIP ViT-B/32 (512-dim embeddings)")
        print("=" * 65)

        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("\n" + "=" * 65)
            print("  SETUP FAILED: Missing prerequisites")
            print("=" * 65)
            return False

        # Step 2: Check existing models
        print("\n[2/4] Checking for existing models...")
        model_key = "clip_vit_b32"
        model_exists = self.check_existing_model(model_key)

        # Step 3: Convert if needed
        if not model_exists:
            if not self.convert_model(model_key):
                print("\n" + "=" * 65)
                print("  SETUP FAILED: Model conversion failed")
                print("  See manual instructions above.")
                print("=" * 65)
                return False

        # Step 4: Create configuration
        self.create_config()

        # Summary
        print("\n" + "=" * 65)
        print("  SETUP COMPLETE")
        print("=" * 65)
        print("\n  Model ready: CLIP ViT-B/32")
        print("\n  Next steps:")
        print("    1. Run: python scripts/verify_setup.py")
        print("    2. Run: python src/init_databases.py")
        print("=" * 65)

        return True


def main():
    """Entry point."""
    setup = ModelSetup()
    success = setup.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
