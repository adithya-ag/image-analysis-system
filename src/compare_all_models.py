"""
Compare All Models: CLIP vs MobileCLIP vs SigLIP

Tests all three models on same images and compares performance.

Phase 1 Day 2 - Image Analysis System v0.1

Usage:
    python compare_all_models.py --images 10
"""

import sys
import time
import argparse
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config


def get_test_images(directory: str, count: int = 10):
    """Get test images from directory"""
    image_files = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(os.path.join(directory, filename))
            if len(image_files) >= count:
                break
    return image_files


def test_model(model, model_name: str, images: list):
    """Test model on images and collect metrics"""
    print(f"\n{'=' * 70}")
    print(f"Testing {model_name}")
    print(f"{'=' * 70}")
    
    # Get model info
    info = model.get_model_info()
    print(f"\nModel Info:")
    print(f"   Type: {info['type']}")
    print(f"   Embedding dim: {info['embedding_dim']}")
    print(f"   Provider: {info['provider']}")
    
    # Process images
    results = []
    total_time = 0
    
    print(f"\nProcessing {len(images)} images...")
    
    for i, image_path in enumerate(images, 1):
        try:
            start_time = time.time()
            embedding = model.generate_embedding(image_path)
            elapsed = time.time() - start_time
            
            results.append({
                'image': os.path.basename(image_path),
                'time': elapsed,
                'dims': embedding.shape[0],
                'norm': float((embedding ** 2).sum() ** 0.5),
                'success': True
            })
            
            total_time += elapsed
            
            print(f"   [{i}/{len(images)}] {os.path.basename(image_path)}: "
                  f"{elapsed:.3f}s | {embedding.shape[0]}D")
            
        except Exception as e:
            print(f"   [{i}/{len(images)}] {os.path.basename(image_path)}: FAILED - {e}")
            results.append({
                'image': os.path.basename(image_path),
                'success': False,
                'error': str(e)
            })
    
    return results, total_time


def main():
    parser = argparse.ArgumentParser(description='Compare CLIP vs MobileCLIP vs SigLIP')
    parser.add_argument('--images', type=int, default=10, help='Number of images to test')
    parser.add_argument('--directory', type=str, default=r'C:\Adithya Work\image-analysis-system\image-analysis-system\data\test_images',
                       help='Directory with test images')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔬 3-MODEL COMPARISON - CLIP vs MobileCLIP vs SigLIP")
    print("=" * 70)
    
    # Get test images
    project_root = Path(__file__).parent
    image_dir = project_root / args.directory
    
    if not image_dir.exists():
        print(f"❌ Error: Directory not found: {image_dir}")
        sys.exit(1)
    
    images = get_test_images(str(image_dir), args.images)
    
    if not images:
        print(f"❌ Error: No images found in {image_dir}")
        sys.exit(1)
    
    print(f"\n📂 Testing {len(images)} images from {image_dir}")
    
    # Test all models
    model_results = {}
    
    for model_name in ['clip', 'mobileclip', 'siglip']:
        try:
            print(f"\n📊 Loading {model_name.upper()}...")
            load_start = time.time()
            
            config = Config(model_name=model_name)
            model = config.get_model_instance()
            
            load_time = time.time() - load_start
            print(f"✅ {model_name.upper()} loaded in {load_time:.2f}s")
            
            # Test model
            results, total_time = test_model(model, model_name.upper(), images)
            
            model_results[model_name] = {
                'load_time': load_time,
                'results': results,
                'total_time': total_time,
                'info': model.get_model_info()
            }
            
        except FileNotFoundError as e:
            print(f"⚠️  {model_name.upper()} not available: {e}")
            model_results[model_name] = None
        except Exception as e:
            print(f"❌ {model_name.upper()} failed: {e}")
            model_results[model_name] = None
    
    # Print comparison
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE COMPARISON")
    print("=" * 70)
    
    available_models = [name for name, data in model_results.items() if data is not None]
    
    if not available_models:
        print("❌ No models available for comparison")
        sys.exit(1)
    
    # Success rates
    print(f"\n✅ Success Rate:")
    for model_name in available_models:
        data = model_results[model_name]
        success = sum(1 for r in data['results'] if r['success'])
        print(f"   {model_name.upper():12s}: {success}/{len(images)} images")
    
    # Model load times
    print(f"\n⏱️  Performance (Model Load):")
    for model_name in available_models:
        data = model_results[model_name]
        print(f"   {model_name.upper():12s}: {data['load_time']:.2f}s")
    
    # Per-image performance
    print(f"\n⏱️  Performance (Per Image):")
    for model_name in available_models:
        data = model_results[model_name]
        success = sum(1 for r in data['results'] if r['success'])
        if success > 0:
            avg = data['total_time'] / success
            print(f"   {model_name.upper():12s}: {avg:.3f}s avg ({data['total_time']:.2f}s total)")
    
    # Find fastest
    if len(available_models) > 1:
        speeds = {}
        for model_name in available_models:
            data = model_results[model_name]
            success = sum(1 for r in data['results'] if r['success'])
            if success > 0:
                speeds[model_name] = data['total_time'] / success
        
        if speeds:
            fastest = min(speeds, key=speeds.get)
            slowest = max(speeds, key=speeds.get)
            speedup = speeds[slowest] / speeds[fastest]
            print(f"   → {fastest.upper()} is fastest ({speedup:.2f}x faster than {slowest.upper()})")
    
    # Model sizes
    print(f"\n💾 Model Size:")
    for model_name in available_models:
        info = model_results[model_name]['info']
        if 'model_size_mb' in info:
            print(f"   {model_name.upper():12s}: {info['model_size_mb']:.1f} MB")
        elif 'image_encoder_size_mb' in info:
            total = info['image_encoder_size_mb'] + info['text_encoder_size_mb']
            print(f"   {model_name.upper():12s}: {total:.1f} MB")
    
    # Embedding dimensions
    print(f"\n🔢 Embedding Quality:")
    for model_name in available_models:
        info = model_results[model_name]['info']
        data = model_results[model_name]
        success_results = [r for r in data['results'] if r['success']]
        
        if success_results:
            avg_norm = sum(r['norm'] for r in success_results) / len(success_results)
            print(f"   {model_name.upper():12s}: {info['embedding_dim']}D | norm: {avg_norm:.4f}")
    
    print("\n" + "=" * 70)
    
    all_success = all(
        sum(1 for r in model_results[m]['results'] if r['success']) == len(images)
        for m in available_models
    )
    
    if all_success:
        print("🎉 All models working perfectly!")
    else:
        print("⚠️  Some images failed - check errors above")
    
    print("=" * 70)
    
    print("\n💡 Summary:")
    print(f"   Tested: {', '.join(m.upper() for m in available_models)}")
    print(f"   All have different embedding dimensions - need to normalize for comparison")
    print("\n💡 Next Steps:")
    print("   1. Process full dataset with all models")
    print("   2. Implement search to compare quality")
    print("   3. Choose best model based on speed + quality")


if __name__ == '__main__':
    main()
