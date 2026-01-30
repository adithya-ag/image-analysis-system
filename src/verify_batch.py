"""
Verify Batch Processing Results

Check that images were correctly processed and stored in databases.

Phase 1 Day 2 - Image Analysis System v0.1

Usage:
    python src/verify_batch.py [--detailed]
"""

import sys
import os
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from storage.sqlite_store import SQLiteStore
from storage.lance_store import LanceStore


def verify_batch(detailed: bool = False):
    """Verify batch processing results
    
    Args:
        detailed: If True, show detailed information about each image
    """
    
    print("\n" + "=" * 70)
    print("🔍 BATCH PROCESSING VERIFICATION")
    print("=" * 70)
    
    config = Config()
    
    # Connect to databases
    print("\n💾 Connecting to databases...")
    sqlite_store = SQLiteStore(config.SQLITE_DB_PATH)
    lance_store = LanceStore(config.LANCEDB_PATH)
    print("✅ Connected")
    
    # Count records
    print("\n📊 Counting records...")
    sqlite_count = sqlite_store.count_images()
    lance_count = lance_store.count_embeddings()
    
    print(f"\n📈 Database Statistics:")
    print(f"   SQLite (metadata): {sqlite_count} images")
    print(f"   LanceDB (vectors): {lance_count} embeddings")
    
    # Check consistency
    if sqlite_count == lance_count:
        print(f"✅ Counts match - {sqlite_count} images processed")
    else:
        print(f"⚠️  Warning: Counts don't match!")
        print(f"   Difference: {abs(sqlite_count - lance_count)}")
    
    # Show sample records
    if sqlite_count > 0:
        print("\n📋 Sample Records (first 5):")
        print("-" * 70)
        
        # Get sample images from SQLite
        samples = sqlite_store.get_all_images(limit=5)
        
        for i, img in enumerate(samples, 1):
            print(f"\n{i}. Image ID: {img['image_id'][:16]}...")
            print(f"   File: {img['filename']}")
            print(f"   Size: {img['file_size_bytes']:,} bytes")
            if img['width'] and img['height']:
                print(f"   Dimensions: {img['width']}x{img['height']}")
            print(f"   Format: {img['format']}")
            print(f"   Model: {img['embedding_model']}")
            print(f"   Indexed: {img['indexed_at']}")
    
    # Detailed verification
    if detailed and sqlite_count > 0:
        print("\n" + "=" * 70)
        print("🔬 DETAILED VERIFICATION")
        print("=" * 70)
        
        print("\nChecking all images have embeddings...")
        all_images = sqlite_store.get_all_images()
        
        missing_embeddings = []
        for img in all_images:
            # Check if embedding exists in LanceDB
            result = lance_store.search_similar(
                query_embedding=None,  # We'll modify search to handle None
                top_k=1,
                filter_image_id=img['image_id']
            )
            if not result:
                missing_embeddings.append(img['image_id'])
        
        if missing_embeddings:
            print(f"⚠️  Found {len(missing_embeddings)} images without embeddings")
            for img_id in missing_embeddings[:5]:
                print(f"   - {img_id}")
        else:
            print("✅ All images have embeddings")
    
    # Storage info
    print("\n" + "=" * 70)
    print("💾 Storage Information:")
    print(f"   SQLite database: {config.SQLITE_DB_PATH}")
    if os.path.exists(config.SQLITE_DB_PATH):
        size_mb = os.path.getsize(config.SQLITE_DB_PATH) / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
    
    print(f"   LanceDB directory: {config.LANCEDB_PATH}")
    if os.path.exists(config.LANCEDB_PATH):
        # Calculate directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(config.LANCEDB_PATH):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        size_mb = total_size / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
    
    # Summary
    print("\n" + "=" * 70)
    if sqlite_count > 0 and sqlite_count == lance_count:
        print("✅ VERIFICATION PASSED")
        print(f"   {sqlite_count} images successfully processed and stored")
    elif sqlite_count == 0:
        print("⚠️  NO IMAGES FOUND")
        print("   Run batch ingestion first: python run_batch_ingestion.py")
    else:
        print("⚠️  VERIFICATION ISSUES DETECTED")
        print("   Database counts don't match - review errors above")
    
    print("=" * 70)
    
    return sqlite_count, lance_count


def main():
    """Main entry point"""
    detailed = '--detailed' in sys.argv
    verify_batch(detailed=detailed)


if __name__ == '__main__':
    main()
