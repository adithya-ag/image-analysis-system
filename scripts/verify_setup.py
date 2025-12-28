"""
Setup Verification Script
Checks if all components are properly installed and configured.

Usage:
    python scripts/verify_setup.py
"""

import sys
import os
from pathlib import Path
import importlib.util

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SetupVerifier:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
    
    def check(self, name, condition, error_msg=None, warning=False):
        """Check a condition and print result"""
        if condition:
            print(f"[OK] {name}")
            self.checks_passed += 1
            return True
        else:
            if warning:
                print(f"[WARN] {name}")
                if error_msg:
                    print(f"   -> {error_msg}")
                self.warnings.append(name)
            else:
                print(f"[FAIL] {name}")
                if error_msg:
                    print(f"   -> {error_msg}")
                self.checks_failed += 1
            return False
    
    def check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        is_valid = version.major == 3 and 10 <= version.minor <= 12
        
        self.check(
            f"Python version: {version.major}.{version.minor}.{version.micro}",
            is_valid,
            "Python 3.10-3.12 required. You have Python 3.13 which may have compatibility issues."
        )
    
    def check_virtual_env(self):
        """Check if running in virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        self.check(
            "Virtual environment: Active",
            in_venv,
            "Not running in virtual environment. Activate with: venv\\Scripts\\activate",
            warning=True
        )
    
    def check_dependency(self, package_name, import_name=None):
        """Check if a Python package is installed"""
        if import_name is None:
            import_name = package_name.replace('-', '_')
        
        try:
            spec = importlib.util.find_spec(import_name)
            installed = spec is not None
        except (ImportError, ModuleNotFoundError):
            installed = False
        
        self.check(
            f"Package: {package_name}",
            installed,
            f"Install with: pip install {package_name}"
        )
        
        return installed
    
    def check_dependencies(self):
        """Check all required dependencies"""
        dependencies = [
            ('numpy', 'numpy'),
            ('opencv-python', 'cv2'),
            ('pillow', 'PIL'),
            ('onnxruntime', 'onnxruntime'),
            ('openvino', 'openvino'),
            ('lancedb', 'lancedb'),
            ('transformers', 'transformers'),
            ('torch', 'torch'),
            ('requests', 'requests'),
            ('tqdm', 'tqdm'),
        ]
        
        for package, import_name in dependencies:
            self.check_dependency(package, import_name)
    
    def check_directory_structure(self):
        """Check if required directories exist"""
        dirs = ['src', 'scripts', 'models', 'databases', 'data', 'tests', 'docs']
        
        for dir_name in dirs:
            dir_path = PROJECT_ROOT / dir_name
            self.check(
                f"Directory: {dir_name}/",
                dir_path.exists(),
                f"Create with: mkdir {dir_name}"
            )
    
    def check_models(self):
        """Check if models are downloaded"""
        models_dir = PROJECT_ROOT / "models"

        # v0.1: CLIP ViT-B/32 only (SmolVLM and MobileCLIP deferred to v0.2)
        clip_model_path = models_dir / "clip_vit_b32" / "model.onnx"
        exists = clip_model_path.exists() and clip_model_path.stat().st_size > 1024 * 1024  # >1MB

        if exists:
            size_mb = clip_model_path.stat().st_size / (1024 * 1024)
            self.check(
                f"Model: CLIP ViT-B/32 ({size_mb:.1f} MB)",
                True,
                None
            )
        else:
            self.check(
                "Model: CLIP ViT-B/32",
                False,
                "Run: python scripts/setup_models.py",
                warning=True
            )
    
    def check_test_images(self):
        """Check if test images are prepared"""
        test_images_dir = PROJECT_ROOT / "data" / "test_images"
        
        if test_images_dir.exists():
            image_files = list(test_images_dir.glob("*.jpg")) + \
                         list(test_images_dir.glob("*.jpeg")) + \
                         list(test_images_dir.glob("*.png"))
            
            count = len(image_files)
            self.check(
                f"Test images: {count} found",
                count >= 10,
                "Run: python scripts/prepare_test_data.py --source <path>",
                warning=True
            )
        else:
            self.check(
                "Test images directory",
                False,
                "Run: python scripts/prepare_test_data.py --source <path>",
                warning=True
            )
    
    def check_databases(self):
        """Check if databases are initialized"""
        db_dir = PROJECT_ROOT / "databases"
        
        sqlite_db = db_dir / "metadata.db"
        lance_db = db_dir / "embeddings.lance"
        
        self.check(
            "SQLite database",
            sqlite_db.exists(),
            "Run: python src/init_databases.py",
            warning=True
        )
        
        self.check(
            "LanceDB directory",
            lance_db.exists(),
            "Run: python src/init_databases.py",
            warning=True
        )
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"[OK] Checks passed: {self.checks_passed}")
        print(f"[FAIL] Checks failed: {self.checks_failed}")
        print(f"[WARN] Warnings: {len(self.warnings)}")

        if self.checks_failed == 0:
            print("\n*** Setup complete! Ready for Phase 1 implementation. ***")
        else:
            print("\n[!] Some checks failed. Please address the issues above.")

        if self.warnings:
            print("\n[!] Warnings (optional but recommended):")
            for warning in self.warnings:
                print(f"   - {warning}")

        print("=" * 60)
    
    def run(self):
        """Run all verification checks"""
        print("=" * 60)
        print("SETUP VERIFICATION")
        print("=" * 60)
        print()

        print("[1] Python Environment")
        self.check_python_version()
        self.check_virtual_env()
        print()

        print("[2] Dependencies")
        self.check_dependencies()
        print()

        print("[3] Project Structure")
        self.check_directory_structure()
        print()

        print("[4] Models")
        self.check_models()
        print()

        print("[5] Test Data")
        self.check_test_images()
        print()

        print("[6] Databases")
        self.check_databases()

        self.print_summary()

        return 0 if self.checks_failed == 0 else 1


def main():
    verifier = SetupVerifier()
    return verifier.run()


if __name__ == "__main__":
    exit(main())
