"""
Model Setup Script
Downloads and prepares ONNX models for image analysis.

Models:
1. SmolVLM-500M (primary) - ~500MB
2. MobileCLIP-S2 (benchmark) - ~100MB

Usage:
    python scripts/setup_models.py
"""

import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ModelSetup:
    def __init__(self):
        self.models_dir = PROJECT_ROOT / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Model configurations
        # Note: These are placeholder URLs - actual ONNX models need to be sourced
        self.models = {
            "smolvlm_500m": {
                "name": "SmolVLM-500M",
                "url": "https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct/resolve/main/model.onnx",
                "filename": "smolvlm_500m.onnx",
                "size_mb": 500,
                "embedding_dim": 512,
            },
            "mobileclip_s2": {
                "name": "MobileCLIP-S2",
                "url": "https://huggingface.co/apple/MobileCLIP-S2/resolve/main/model.onnx",
                "filename": "mobileclip_s2.onnx",
                "size_mb": 100,
                "embedding_dim": 512,
            }
        }
    
    def download_file(self, url, filepath):
        """Download file with progress bar"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f, tqdm(
                desc=filepath.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
            
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def check_existing_model(self, model_key):
        """Check if model already exists"""
        filepath = self.models_dir / self.models[model_key]["filename"]
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"✅ {self.models[model_key]['name']} already exists ({size_mb:.1f} MB)")
            return True
        return False
    
    def setup_model(self, model_key):
        """Download and setup a single model"""
        model = self.models[model_key]
        filepath = self.models_dir / model["filename"]
        
        print(f"\n📥 Downloading {model['name']}...")
        print(f"   URL: {model['url']}")
        print(f"   Size: ~{model['size_mb']} MB")
        
        # Note: These URLs are placeholders
        # In reality, we need to:
        # 1. Download from HuggingFace
        # 2. Convert to ONNX if not already
        # 3. Optimize for OpenVINO
        
        print(f"\n⚠️  MANUAL DOWNLOAD REQUIRED:")
        print(f"   The models need to be manually downloaded and converted to ONNX.")
        print(f"\n   STEPS:")
        print(f"   1. Download {model['name']} from HuggingFace")
        print(f"   2. Convert to ONNX format (if needed)")
        print(f"   3. Save as: {filepath}")
        print(f"\n   For now, creating placeholder file...")
        
        # Create placeholder file for development
        with open(filepath, 'w') as f:
            f.write(f"# Placeholder for {model['name']} ONNX model\n")
            f.write(f"# Download from: {model['url']}\n")
            f.write(f"# Expected size: {model['size_mb']} MB\n")
        
        print(f"✅ Placeholder created: {filepath}")
        return True
    
    def create_config(self):
        """Create model configuration file"""
        config = {
            "models": self.models,
            "default_model": "smolvlm_500m",
            "model_dir": str(self.models_dir),
        }
        
        config_path = self.models_dir / "model_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Model config created: {config_path}")
    
    def run(self):
        """Run complete setup process"""
        print("=" * 60)
        print("🔧 MODEL SETUP - Local-First Image Analysis System")
        print("=" * 60)
        
        # Check and download each model
        for model_key in self.models.keys():
            if not self.check_existing_model(model_key):
                self.setup_model(model_key)
        
        # Create configuration
        self.create_config()
        
        print("\n" + "=" * 60)
        print("📋 NEXT STEPS FOR ACTUAL MODEL SETUP:")
        print("=" * 60)
        print("\nTo get real ONNX models:")
        print("\n1. SmolVLM-500M:")
        print("   - Visit: https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct")
        print("   - Download model files")
        print("   - Convert to ONNX using: optimum-cli export onnx")
        print("   - Place in: models/smolvlm_500m.onnx")
        
        print("\n2. MobileCLIP-S2:")
        print("   - Visit: https://huggingface.co/apple/MobileCLIP-S2")
        print("   - Download model files")
        print("   - Convert to ONNX")
        print("   - Place in: models/mobileclip_s2.onnx")
        
        print("\n3. Alternative (for quick testing):")
        print("   - Use pre-trained CLIP model from OpenAI")
        print("   - Install: pip install clip-onnx")
        print("   - Convert: python -m clip_onnx.convert")
        
        print("\n" + "=" * 60)
        print("✅ Model setup complete (placeholders created)")
        print("   Replace placeholders with actual ONNX models to proceed.")
        print("=" * 60)


def main():
    setup = ModelSetup()
    setup.run()


if __name__ == "__main__":
    main()
