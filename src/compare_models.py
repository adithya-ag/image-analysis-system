"""
Compare CLIP vs MobileCLIP

Tests both models on same images and compares performance.

Phase 1 Day 2 - Image Analysis System v0.1

Usage:
    python compare_models.py --images 10
"""

import sys
import time
import argparse
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from analysis.clip_openai import CLIPOpenAI
from analysis.mobileclip import MobileCLIP


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
        start_time = time.time()
        
        try:
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
    parser = argparse.ArgumentParser(description='Compare CLIP vs MobileCLIP')
    parser.add_argument('--images', type=int, default=10, help='Number of images to test')
    parser.add_argument('--directory', type=str, default='data/test_images', 
                       help='Directory with test images')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔬 MODEL COMPARISON - CLIP vs MobileCLIP")
    print("=" * 70)
    
    # Get test images
    project_root = Path(__file__).parent.parent
    image_dir = project_root / args.directory
    
    if not image_dir.exists():
        print(f"❌ Error: Directory not found: {image_dir}")
        sys.exit(1)
    
    images = get_test_images(str(image_dir), args.images)
    
    if not images:
        print(f"❌ Error: No images found in {image_dir}")
        sys.exit(1)
    
    print(f"\n📂 Found {len(images)} images in {image_dir}")
    print(f"   Testing first {len(images)} images")
    
    # Load CLIP
    print(f"\n📊 Loading CLIP...")
    clip_start = time.time()
    clip_config = Config(model_name='clip')
    clip_model = CLIPOpenAI(clip_config)
    clip_load_time = time.time() - clip_start
    print(f"✅ CLIP loaded in {clip_load_time:.2f}s")
    
    # Load MobileCLIP
    print(f"\n📊 Loading MobileCLIP...")
    mobile_start = time.time()
    mobile_config = Config(model_name='mobileclip')
    mobile_model = MobileCLIP(mobile_config)
    mobile_load_time = time.time() - mobile_start
    print(f"✅ MobileCLIP loaded in {mobile_load_time:.2f}s")
    
    # Test CLIP
    clip_results, clip_total_time = test_model(clip_model, "CLIP", images)
    
    # Test MobileCLIP
    mobile_results, mobile_total_time = test_model(mobile_model, "MobileCLIP", images)
    
    # Print comparison
    print("\n" + "=" * 70)
    print("📊 COMPARISON SUMMARY")
    print("=" * 70)
    
    # Success rates
    clip_success = sum(1 for r in clip_results if r['success'])
    mobile_success = sum(1 for r in mobile_results if r['success'])
    
    print(f"\n✅ Success Rate:")
    print(f"   CLIP:       {clip_success}/{len(images)} images")
    print(f"   MobileCLIP: {mobile_success}/{len(images)} images")
    
    # Performance comparison
    print(f"\n⏱️  Performance (Model Load):")
    print(f"   CLIP:       {clip_load_time:.2f}s")
    print(f"   MobileCLIP: {mobile_load_time:.2f}s")
    
    if clip_success > 0 and mobile_success > 0:
        clip_avg = clip_total_time / clip_success
        mobile_avg = mobile_total_time / mobile_success
        
        print(f"\n⏱️  Performance (Per Image):")
        print(f"   CLIP:       {clip_avg:.3f}s avg ({clip_total_time:.2f}s total)")
        print(f"   MobileCLIP: {mobile_avg:.3f}s avg ({mobile_total_time:.2f}s total)")
        
        speedup = clip_avg / mobile_avg
        if speedup > 1:
            print(f"   → MobileCLIP is {speedup:.2f}x faster per image")
        else:
            print(f"   → CLIP is {1/speedup:.2f}x faster per image")
    
    # Model sizes
    clip_info = clip_model.get_model_info()
    mobile_info = mobile_model.get_model_info()
    
    print(f"\n💾 Model Size:")
    if 'model_size_mb' in clip_info:
        print(f"   CLIP:       {clip_info['model_size_mb']:.1f} MB")
    if 'image_encoder_size_mb' in mobile_info:
        total_size = mobile_info['image_encoder_size_mb'] + mobile_info['text_encoder_size_mb']
        print(f"   MobileCLIP: {total_size:.1f} MB "
              f"({mobile_info['image_encoder_size_mb']:.1f} + "
              f"{mobile_info['text_encoder_size_mb']:.1f} MB)")
    
    # Embedding quality
    print(f"\n🔢 Embedding Quality:")
    print(f"   Both models: {clip_info['embedding_dim']}D embeddings")
    
    if clip_success > 0:
        clip_norms = [r['norm'] for r in clip_results if r['success']]
        print(f"   CLIP norm: {sum(clip_norms)/len(clip_norms):.4f} avg")
    
    if mobile_success > 0:
        mobile_norms = [r['norm'] for r in mobile_results if r['success']]
        print(f"   MobileCLIP norm: {sum(mobile_norms)/len(mobile_norms):.4f} avg")
    
    print("\n" + "=" * 70)
    
    if clip_success == len(images) and mobile_success == len(images):
        print("🎉 Both models working perfectly!")
    else:
        print("⚠️  Some images failed - check errors above")
    
    print("=" * 70)
    
    print("\n💡 Next Steps:")
    print("   1. Process full dataset with chosen model:")
    print("      python run_batch_ingestion.py --model clip")
    print("      python run_batch_ingestion.py --model mobileclip")
    print("   2. Implement search to compare quality")
    print("   3. Choose best model for v0.1")


if __name__ == '__main__':
    main()
