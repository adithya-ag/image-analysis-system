"""
Batch Image Processor

Handles ingestion of multiple images with progress tracking,
error handling, and performance metrics.

Phase 1 Day 2 - Image Analysis System v0.1
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import hashlib

from config import Config
from analysis.clip_openai import CLIPOpenAI
from storage.sqlite_store import SQLiteStore
from storage.lance_store import LanceStore


class BatchProcessor:
    """Process multiple images and store their embeddings"""
    
    def __init__(self, config: Config):
        """Initialize batch processor with configuration"""
        self.config = config
        self.model = None
        self.sqlite_store = None
        self.lance_store = None
        
        # Performance tracking
        self.metrics = {
            'total_images': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'total_time': 0,
            'model_load_time': 0,
            'avg_embedding_time': 0,
        }
        
        # Error tracking
        self.errors = []
        
    def _generate_image_id(self, file_path: str) -> str:
        """Generate unique ID for image based on file path and content hash
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Unique image ID (first 16 chars of SHA-256 hash)
        """
        # Use file path + file size for quick hash
        stat = os.stat(file_path)
        content = f"{file_path}_{stat.st_size}_{stat.st_mtime}".encode()
        return hashlib.sha256(content).hexdigest()[:16]
    
    def _get_image_metadata(self, file_path: str) -> Dict:
        """Extract basic metadata from image file
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary with metadata fields
        """
        from PIL import Image
        
        stat = os.stat(file_path)
        
        # Try to get image dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                img_format = img.format
        except Exception as e:
            print(f"⚠️  Warning: Could not read image dimensions: {e}")
            width, height, img_format = None, None, None
        
        return {
            'filename': os.path.basename(file_path),
            'file_size_bytes': stat.st_size,
            'width': width,
            'height': height,
            'format': img_format,
            'created_at': datetime.fromtimestamp(stat.st_ctime),
        }
    
    def initialize(self):
        """Initialize model and storage systems"""
        print("\n" + "=" * 70)
        print("🚀 INITIALIZING BATCH PROCESSOR")
        print("=" * 70)
        
        # Load model
        print(f"\n📊 Step 1: Loading {self.config.model_name.upper()} model...")
        start_time = time.time()
        self.model = self.config.get_model_instance()
        self.metrics['model_load_time'] = time.time() - start_time
        print(f"✅ Model loaded in {self.metrics['model_load_time']:.2f}s")

        # Initialize storage
        print("\n💾 Step 2: Connecting to databases...")
        self.sqlite_store = SQLiteStore(self.config.sqlite_path)
        self.lance_store = LanceStore(self.config.lance_path)
        print(f"✅ Databases connected")
        print(f"   SQLite: {self.config.sqlite_path}")
        print(f"   LanceDB: {self.config.lance_path}")
        
        print("\n" + "=" * 70)
    
    def process_images(self, image_paths: List[str], skip_existing: bool = True) -> Dict:
        """Process a batch of images
        
        Args:
            image_paths: List of paths to image files
            skip_existing: If True, skip images already in database
            
        Returns:
            Dictionary with processing results and metrics
        """
        self.metrics['total_images'] = len(image_paths)
        start_time = time.time()
        
        print(f"\n📷 Processing {len(image_paths)} images...")
        print(f"Skip existing: {skip_existing}")
        print("-" * 70)
        
        embedding_times = []
        
        for idx, image_path in enumerate(image_paths, 1):
            try:
                # Generate unique ID
                image_id = self._generate_image_id(image_path)
                
                # Check if already processed
                if skip_existing and self.sqlite_store.image_exists(image_id):
                    self.metrics['skipped'] += 1
                    print(f"⏭️  [{idx}/{len(image_paths)}] Skipped (already exists): {os.path.basename(image_path)}")
                    continue
                
                # Process image
                embed_start = time.time()
                
                # Generate embedding
                embedding = self.model.generate_embedding(image_path)
                embed_time = time.time() - embed_start
                embedding_times.append(embed_time)
                
                # Get metadata
                metadata = self._get_image_metadata(image_path)
                
                # Store in SQLite
                self.sqlite_store.store_image(
                    image_id=image_id,
                    file_path=image_path,
                    metadata={
                        **metadata,
                        'embedding_model': self.config.model_name,
                        'embedding_version': '1.0',
                    }
                )
                
                # Store in LanceDB
                self.lance_store.store_embedding(
                    image_id=image_id,
                    embedding=embedding,
                    metadata={'file_path': image_path}
                )
                
                self.metrics['processed'] += 1
                
                # Progress update (every 10 images or last image)
                if idx % 10 == 0 or idx == len(image_paths):
                    avg_time = sum(embedding_times) / len(embedding_times)
                    remaining = len(image_paths) - idx
                    eta_seconds = remaining * avg_time
                    
                    print(f"✅ [{idx}/{len(image_paths)}] Processed: {os.path.basename(image_path)}")
                    print(f"   Progress: {(idx/len(image_paths)*100):.1f}% | "
                          f"Avg time: {avg_time:.2f}s | "
                          f"ETA: {eta_seconds:.0f}s")
                
            except Exception as e:
                self.metrics['failed'] += 1
                error_msg = f"Image {idx}: {image_path} - {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ [{idx}/{len(image_paths)}] Failed: {os.path.basename(image_path)}")
                print(f"   Error: {str(e)}")
        
        # Calculate final metrics
        self.metrics['total_time'] = time.time() - start_time
        if embedding_times:
            self.metrics['avg_embedding_time'] = sum(embedding_times) / len(embedding_times)
        
        return self.metrics
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "=" * 70)
        print("📊 BATCH PROCESSING SUMMARY")
        print("=" * 70)
        
        print(f"\n📈 Results:")
        print(f"   Total images: {self.metrics['total_images']}")
        print(f"   ✅ Processed: {self.metrics['processed']}")
        print(f"   ⏭️  Skipped: {self.metrics['skipped']}")
        print(f"   ❌ Failed: {self.metrics['failed']}")
        
        print(f"\n⏱️  Performance:")
        print(f"   Model load time: {self.metrics['model_load_time']:.2f}s")
        print(f"   Total processing time: {self.metrics['total_time']:.2f}s")
        print(f"   Average per image: {self.metrics['avg_embedding_time']:.3f}s")
        
        if self.metrics['processed'] > 0:
            throughput = self.metrics['processed'] / self.metrics['total_time']
            print(f"   Throughput: {throughput:.2f} images/second")
        
        if self.errors:
            print(f"\n⚠️  Errors ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more")
        
        print("\n" + "=" * 70)
    
    def verify_results(self) -> Tuple[bool, Dict]:
        """Verify that processing completed successfully
        
        Returns:
            Tuple of (success, stats_dict)
        """
        print("\n🔍 Verifying results...")
        
        # Count images in databases
        sqlite_count = self.sqlite_store.count_images()
        lance_count = self.lance_store.count_embeddings()
        
        stats = {
            'sqlite_count': sqlite_count,
            'lance_count': lance_count,
            'match': sqlite_count == lance_count,
            'expected': self.metrics['processed'],
        }
        
        print(f"   SQLite records: {sqlite_count}")
        print(f"   LanceDB vectors: {lance_count}")
        print(f"   Expected: {self.metrics['processed']}")
        
        success = (sqlite_count == lance_count == self.metrics['processed'])
        
        if success:
            print("✅ Verification passed - all counts match!")
        else:
            print("⚠️  Verification warning - counts don't match")
        
        return success, stats
    
    def cleanup(self):
        """Clean up resources"""
        # Currently no explicit cleanup needed
        # Model and stores will be garbage collected
        pass


def get_image_files(directory: str, extensions: tuple = ('.jpg', '.jpeg', '.png')) -> List[str]:
    """Get all image files from a directory
    
    Args:
        directory: Path to directory
        extensions: Tuple of file extensions to include
        
    Returns:
        List of full paths to image files
    """
    image_files = []
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(extensions):
            full_path = os.path.join(directory, filename)
            image_files.append(full_path)
    
    return sorted(image_files)  # Sort for consistent ordering
