"""
Test Data Preparation Script
Copies a subset of images from Unsplash Lite dataset for testing.

Usage:
    python scripts/prepare_test_data.py --source "C:\path\to\unsplash\photos" --count 100
"""

import argparse
import shutil
import random
from pathlib import Path
from tqdm import tqdm
import json


def get_image_files(source_dir):
    """Get all image files from source directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    image_files = []
    
    source_path = Path(source_dir)
    if not source_path.exists():
        raise ValueError(f"Source directory does not exist: {source_dir}")
    
    print(f"📂 Scanning for images in: {source_path}")
    
    for ext in image_extensions:
        image_files.extend(source_path.glob(f"**/*{ext}"))
        image_files.extend(source_path.glob(f"**/*{ext.upper()}"))
    
    print(f"✅ Found {len(image_files)} images")
    return image_files


def copy_random_images(source_files, dest_dir, count):
    """Copy random subset of images to destination"""
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Select random images
    if len(source_files) <= count:
        selected = source_files
        print(f"⚠️  Source has only {len(source_files)} images, copying all")
    else:
        selected = random.sample(source_files, count)
        print(f"✅ Selected {count} random images")
    
    # Copy files with progress bar
    copied = []
    metadata = []
    
    print(f"\n📋 Copying images to: {dest_path}")
    
    for i, src_file in enumerate(tqdm(selected, desc="Copying"), 1):
        # Create new filename with index
        dest_filename = f"test_{i:04d}{src_file.suffix}"
        dest_file = dest_path / dest_filename
        
        try:
            shutil.copy2(src_file, dest_file)
            copied.append(dest_file)
            
            # Store metadata
            metadata.append({
                "id": i,
                "filename": dest_filename,
                "original_path": str(src_file),
                "size_bytes": dest_file.stat().st_size,
            })
        except Exception as e:
            print(f"❌ Failed to copy {src_file.name}: {e}")
    
    print(f"✅ Copied {len(copied)} images successfully")
    return copied, metadata


def save_metadata(metadata, dest_dir):
    """Save metadata about test images"""
    metadata_file = Path(dest_dir) / "test_images_metadata.json"
    
    with open(metadata_file, 'w') as f:
        json.dump({
            "total_images": len(metadata),
            "images": metadata
        }, f, indent=2)
    
    print(f"✅ Metadata saved: {metadata_file}")


def main():
    parser = argparse.ArgumentParser(description='Prepare test dataset from Unsplash images')
    parser.add_argument('--source', required=True, help='Source directory with Unsplash images')
    parser.add_argument('--count', type=int, default=100, help='Number of images to copy (default: 100)')
    parser.add_argument('--dest', default=None, help='Destination directory (default: data/test_images)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    
    # Determine destination
    if args.dest:
        dest_dir = args.dest
    else:
        project_root = Path(__file__).parent.parent
        dest_dir = project_root / "data" / "test_images"
    
    print("=" * 60)
    print("🖼️  TEST DATA PREPARATION")
    print("=" * 60)
    print(f"Source: {args.source}")
    print(f"Destination: {dest_dir}")
    print(f"Count: {args.count}")
    print(f"Random seed: {args.seed}")
    print("=" * 60)
    
    try:
        # Get all images
        image_files = get_image_files(args.source)
        
        if len(image_files) == 0:
            print("❌ No images found in source directory!")
            return
        
        # Copy random subset
        copied, metadata = copy_random_images(image_files, dest_dir, args.count)
        
        # Save metadata
        save_metadata(metadata, dest_dir)
        
        print("\n" + "=" * 60)
        print("✅ TEST DATA PREPARATION COMPLETE")
        print("=" * 60)
        print(f"📁 Images location: {dest_dir}")
        print(f"📊 Total images: {len(copied)}")
        print(f"📄 Metadata: {dest_dir}/test_images_metadata.json")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
